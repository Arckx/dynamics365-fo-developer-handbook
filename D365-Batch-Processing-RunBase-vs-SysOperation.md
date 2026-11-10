# Batch Processing in D365 F&O: RunBase/RunBaseBatch vs. SysOperation Framework

---

## Part A — The Plain-English Picture

Imagine you're at a restaurant.

- **Interactive/synchronous work** is you ordering at the counter and waiting right there while the cook makes your sandwich. You can't do anything else until it's in your hand.
- **Batch processing** is you filling out a to-go order form, dropping it in a box, and walking away. The kitchen picks it up whenever a cook is free, makes it, and you're notified (or you check back later) when it's ready. You didn't have to stand there, and the kitchen can queue up dozens of these orders, prioritize the urgent ones, and retry if something goes wrong with your specific order — without stopping the whole kitchen.

In D365 F&O, the "kitchen" is the **AOS (Application Object Server)**, and the "order form in a box" is a row written to the **`BatchJob`** table, with one or more **`BatchJobTask`** rows underneath it — think of these as the individual line items on the order. A background process on the server, the **batch server**, continuously works through that queue.

So when someone says "make this class batch-able," they mean: *let this piece of code be dropped into that order queue instead of forcing a user to sit and wait for it.*

There are two different **recipes** (frameworks) for writing the code that goes into that order box:

1. **RunBase / RunBaseBatch** — the older recipe, from the AX 2009/2012 era. Still fully supported and still used across a lot of existing D365 F&O standard code.
2. **SysOperation Framework** — the newer, cleaner recipe, and the one used for all new development.

Both recipes end up producing the exact same kind of order, sitting in the exact same queue, worked by the exact same kitchen staff. The difference is entirely in how the recipe is written — not in how the kitchen processes it.

That's the single most useful idea to carry into both real development work and interviews: **the framework choice is a development-time decision; the production execution engine underneath is shared and identical.**

---

## Part B — The Technical Layer

### 1. What "batch" means at the platform level

A class becomes batch-eligible when its execution is represented as a persisted `BatchJob` (parent) and one or more `BatchJobTask` (child) records, picked up and executed by a **batch server** — an AOS instance flagged as "Is batch server" in **System administration > Setup > System > Server configuration**.

Batch processing is the right tool whenever a piece of logic:
- Shouldn't block a user's session (long-running reports, mass updates, postings)
- Needs to run unattended on a schedule (nightly jobs, recurring imports)
- Needs the reliability of being queued, retried, prioritized, and monitored independently of any one user's client session

Both frameworks below are simply two different ways to get a class into that queue.

---

### 2. RunBase / RunBaseBatch — the legacy pattern

`RunBase` is the base framework class providing the skeleton: *dialog → validate → run → pack/unpack*. `RunBaseBatch` extends `RunBase` and implements the `Batchable` interface — this is what actually allows a class to be submitted as a `BatchJob`. Any job that must be able to run in batch inherits from this class.

**Core lifecycle methods:**

| Method | Purpose |
|---|---|
| `dialog()` | Builds the interactive parameter dialog |
| `getFromDialog()` | Reads dialog values back into member variables |
| `pack()` | Serializes the object's state into a `container` for storage on the `BatchJob` record |
| `unpack()` | Deserializes that container back into a fresh object instance when the job actually runs |
| `run()` | The actual business logic |
| `canGoBatch()` | Defaults to `false` — must be overridden to return `true` to allow batch submission |
| `batchInfo()` | Returns the `BatchInfo` object — the API into the batch table for that job |

**The `pack()`/`unpack()` trap — a genuine interview favorite:**
Submitting a RunBase class to batch doesn't keep the object alive in memory. It's serialized via `pack()` into a `container` and stored on the `BatchJob` record. When the batch server later picks it up — possibly after an AOS restart, possibly hours later — it builds a **brand-new object** and calls `unpack()` to restore state, then calls `run()`. The safe pattern uses a version macro so future schema changes don't silently break already-queued jobs:

```x++
class MyBatchClass extends RunBaseBatch
{
    str myParameter = "Default value";

    #define.CurrentVersion(1)
    #localmacro.CurrentList
        myParameter
    #endmacro

    public container pack()
    {
        return [#CurrentVersion, #CurrentList];
    }

    public boolean unpack(container _packedClass)
    {
        Integer version = RunBase::getVersion(_packedClass);
        switch (version)
        {
            case #CurrentVersion:
                [version, #CurrentList] = _packedClass;
                break;
            default:
                return false; // unrecognized version — refuse to run with stale/unknown state
        }
        return true;
    }

    public boolean canGoBatch()
    {
        return true; // must explicitly opt in
    }
}
```

If a new member variable is added to the class but not to both `pack()` and `unpack()` (with the version bumped), that value silently disappears the moment the job actually executes in batch — a bug that won't show up in interactive testing, only in production, hours after the developer has moved on.

**Pros**
- Fast to stand up for a simple, self-contained job — one class, one file
- Battle-tested and still fully supported in current D365 F&O
- Straightforward mental model once internalized: pack → queue → unpack → run

**Cons**
- UI (dialog), state (pack/unpack), and logic (run) are all fused into one class — poor separation of concerns
- `container`-based serialization is untyped and version-fragile; easy to introduce silent data-loss bugs on schema changes
- Hard to unit test in isolation — dialog and business logic aren't cleanly separable
- No natural way to reuse the same parameter definition across a UI dialog, an external service call, and a batch job — each has to be solved separately

---

### 3. SysOperation Framework — the modern pattern

SysOperation replaces the RunBase framework as the standard way to build interaction dialogs and integrate with the batch server. It follows an **MVC-style pattern** — Model, View (auto-generated), Controller — which cleanly separates the three concerns that RunBase fuses together.

| Piece | Class shape | Responsibility |
|---|---|---|
| **Data Contract** | Plain class, `[DataContractAttribute]` on the class, `[DataMemberAttribute]` on each parm-method | Defines *what* parameters exist — strongly typed, no manual serialization code |
| **Service** | Plain class with one public method taking the contract as its parameter | Defines *what happens* — pure business logic, unaware of whether it's called interactively, asynchronously, or from batch |
| **Controller** | Extends `SysOperationServiceController` | Defines *how* it runs — wires the contract to the service, sets the execution mode, and is the entry point from a menu item |

```x++
// 1. Data Contract
[DataContractAttribute]
class VSICustBlockContract
{
    CustAccount custAccount;

    [DataMemberAttribute('CustAccount')]
    public CustAccount parmCustAccount(CustAccount _custAccount = custAccount)
    {
        custAccount = _custAccount;
        return custAccount;
    }
}

// 2. Service — pure logic, framework-agnostic, unit-testable
class VSICustBlockService extends SysOperationServiceBase
{
    public void blockCustomer(VSICustBlockContract _contract)
    {
        CustTable custTable = CustTable::find(_contract.parmCustAccount(), true);
        ttsBegin;
        custTable.Blocked = CustVendorBlocked::All;
        custTable.update();
        ttsCommit;
    }
}

// 3. Controller — the entry point a menu item points to
class VSICustBlockController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VSICustBlockController controller = new VSICustBlockController();
        controller.parmClassName(classStr(VSICustBlockService));
        controller.parmMethodName(methodStr(VSICustBlockService, blockCustomer));
        controller.startOperation();
    }
}
```

Because the service method (`blockCustomer`) never touches dialog code or batch plumbing, the exact same logic can be invoked interactively, from batch, or directly from another X++ class in a unit test — with zero duplication.

**The four execution modes (`SysOperationExecutionMode`):**

| Mode | What actually happens |
|---|---|
| `Synchronous` | Runs on the server but **freezes the client** for the duration — the user waits |
| `Asynchronous` | Runs on the server without blocking the client, but requires the service class to have a Service node in the AOT and be deployed as part of a service group — otherwise it silently falls back to `Synchronous` |
| `ReliableAsynchronous` | The default mode when none is set. Spins up two threads — one on the batch server doing the work, one on the client polling for the result. Once complete, it remains visible in **Batch Job History** for traceability |
| `ScheduledBatch` | Submits as a proper, schedulable `BatchJob` — equivalent to checking the batch tab in a RunBase dialog. This is the mode for true unattended, recurring, retryable batch execution |

Worth committing to memory precisely: "SysOperation always runs in batch" is a common misconception. Batch is one of four modes it can run in, selected via `controller.parmExecutionMode(...)`.

**Pros**
- Clean separation of Contract / Service / Controller — the service class is genuinely unit-testable with no framework dependency
- Strongly typed `[DataMember]` contracts instead of untyped containers — far safer across upgrades
- One data contract is reusable across the UI dialog, external service exposure (via `SysEntryPointAttribute`), and batch submission
- Dialog is auto-generated from the contract's attributes — less boilerplate than a hand-built `dialog()` override
- Clean fit with F&O's patterns for scaling out to multiple parallel batch tasks

**Cons**
- More ceremony (three classes instead of one) for genuinely trivial one-off tasks
- Attribute-driven metadata can feel opaque until you understand what it's generating
- Slightly steeper initial learning curve than RunBase's single-class model

---

### 4. Side-by-side comparison

| Aspect | RunBase / RunBaseBatch | SysOperation Framework |
|---|---|---|
| Era | AX 2009/2012 | AX 2012 R2+ → current standard in D365 F&O |
| Structure | One monolithic class | Three classes: Contract, Service, Controller |
| Parameter storage | `pack()`/`unpack()` into an untyped `container` | Strongly typed `[DataMember]` attributes on the contract |
| Testability | Poor — logic entangled with dialog code | Strong — service logic is pure and isolatable |
| Reuse across UI / batch / external service | Manual, duplicated per use case | Native — one contract, many entry points |
| Getting into the batch queue | Override `canGoBatch()` to `true`; user checks the Batch tab, or code calls `batchInfo()` directly | Controller sets `parmExecutionMode(SysOperationExecutionMode::ScheduledBatch)` |
| Parallel/multi-threaded execution | Manual — task-splitting logic built directly against `BatchHeader`/`BatchJobTask` | Fits cleanly with F&O's standard parallel-task-splitting patterns |
| Current guidance | Legacy, still supported | Recommended for all new development |
| Where it still shows up | Older standard modules (parts of AR/AP, older Trade code) | Most standard batch/service code added since AX 2012 R2 onward |

---

### 5. Production environment behavior

Once a job becomes a `BatchJob` row, both frameworks are executed by the identical batch engine. Everything below applies equally regardless of which framework produced the job.

- **Batch groups** — Batch servers are configured to service specific batch groups, so heavy jobs (e.g. a large costing or MRP run) can be routed to a dedicated server and kept from starving lighter, time-sensitive batch work on a shared one.
- **Threads/concurrency** — Each batch server has a configured maximum number of concurrent threads it can process.
- **Priority** — Jobs carry a priority (Low/Medium/High); the engine picks the highest-priority *ready* task first, not simple FIFO.
- **Recurrence** — `BatchRecurrence` automatically creates the next occurrence once a recurring job finishes, identically for both frameworks.
- **Retry/failure** — An unhandled exception marks the task **Error**; retry behavior is configurable. Neither framework auto-manages transaction boundaries — `ttsBegin`/`ttsCommit` discipline is entirely on the developer, same as any other X++ code. A RunBase class with incomplete `pack()` state is a uniquely legacy-framework risk here; a typed SysOperation contract makes that specific failure mode much harder to introduce.
- **Security** — Server-bound batch jobs (via `runsImpersonated()` returning `true`) run under the submitting user's permissions and have restricted interaction with the client, making them more secure than non-server-bound execution.
- **Monitoring** — Both surface identically at **System administration > Inquiries > Batch jobs**, showing status (Waiting/Executing/Ended/Error/Canceled), full history, and the ability to requeue. From the Batch Jobs form alone, there's no way to tell whether the underlying class is RunBase or SysOperation — that distinction is invisible at runtime.

---

### 6. The mental model to walk away with

> RunBase is "one class does everything," serializing state into an untyped container. SysOperation is "three classes, each with one job," using a strongly typed data contract. Both ultimately produce the same artifact at runtime — a `BatchJob`/`BatchJobTask` row processed by the same batch engine, under the same batch groups, priorities, and recurrence rules. SysOperation is the choice for new work because it's testable, reusable, and safer to evolve — not because production treats it any differently once the job hits the queue.

---

### 7. Practice activity

**Scenario:** Build a job that blocks a *list* of overdue customers (not just one) for invoicing. It must be schedulable nightly, safely retryable, and — since the list can run into the thousands — ideally process customers in parallel chunks in production.

**Work through before checking the answer:**
1. RunBase or SysOperation here, and specifically why — not just "it's newer"?
2. What belongs in the Data Contract vs. the Service class?
3. Where would parallelism go, and which F&O mechanism enables it cleanly?
4. Is the transaction boundary one `ttsBegin`/`ttsCommit` for the whole list, or one per customer — and why does that choice matter for retry safety?

---

### 8. Ideal solution & reasoning

**Question 1 — RunBase or SysOperation, and specifically why?**

SysOperation. Not because it's newer in the abstract, but for two concrete reasons that map directly onto this scenario:

1. **The contract needs to be reused.** The same "which customers are overdue" selection logic will likely be wanted elsewhere — a manual on-demand run from a form button, a scheduled nightly run, maybe eventually an OData action for an external collections system to trigger it. A typed `[DataContract]` gives that for free; a RunBase class's dialog fields don't transfer to a service call without rewriting.
2. **The worker logic needs to be unit-testable in isolation.** Calling "block this one customer" directly in a test with a hand-built contract, and asserting the result, with zero batch or dialog machinery involved, is the whole point of separating the Service class out.

**Question 2 — What goes in the Data Contract vs. the Service class?**

This is the part people get wrong on the first attempt: **the contract holds selection criteria, not the customer list itself.**

- **Contract (`VSICustBlockSelectionContract`)** — holds the filter: `overdueSinceDate`, optionally a specific `CustGroup` to limit scope. This is what a user, or a recurrence schedule, configures once.
- **Service, split into two roles** — matching how standard F&O handles this exact shape of problem in journal batch posting:
  - A **producer/selector service** that runs the query against the contract's criteria and populates a staging/queue table — one row per customer to block, with a status field (`Ready` / `InProgress` / `Done` / `Error`) and a task-owner reference.
  - A **worker service** that doesn't know or care how many customers exist in total — it just repeatedly claims the next `Ready` row from the queue table and processes it, until the queue is empty.

The customer list never lives in the contract or in memory as one big collection — it lives in the staging table. That single design decision is what makes both parallelism and safe retries possible.

**Question 3 — Where does parallelism go, and what mechanism enables it?**

There are three named approaches for splitting a large batch job into fragments:

| Approach | Best for | Fit for this scenario |
|---|---|---|
| **Individual task modeling** | A handful of items, or items with real dependencies between them | Works fine for a dozen customers; at "thousands," the batch engine's own task-tracking overhead becomes the bottleneck and starts dragging down other batch jobs on the server too |
| **Batch bundling** | An evenly distributed, uniform workload with no need for a staging table | Reasonable, since blocking a customer is roughly constant-time work — but it lacks the built-in progress tracking and per-item resilience that top picking gives |
| **Top picking pattern** | An uneven workload at real volume, with a bounded, small number of parallel tasks each grinding through a shared queue | **The right fit** — the same mechanism standard F&O uses for high-volume journal batch posting, for the identical shape of problem: thousands of independent small units of work, processed by a small fixed number of parallel workers, with progress tracked precisely |

**The mechanism, concretely:** a bounded number of `BatchJobTask`s (say, 5 or 10 — not one per customer) are scheduled by a controller. Each task runs the same worker loop: inside a short transaction, claim the next `Ready` row from the staging table (mark it `InProgress`, tag it with the task's own identity), commit quickly, then do the actual `CustTable` block outside that claiming transaction, and finally mark the row `Done` (or `Error`). Because each task only ever holds one row's claim at a time and commits that claim fast, tasks don't block each other waiting on locks, and the total number of `BatchJobTask` rows stays small regardless of whether 500 or 50,000 customers are being processed.

```x++
// Staging/queue table: VSICustBlockQueue
// Fields: RecId, CustAccount, Status (Ready/InProgress/Done/Error), BatchTaskId, ErrorText

// --- Producer: populates the queue from the contract's criteria ---
class VSICustBlockSelectorService extends SysOperationServiceBase
{
    public void selectOverdueCustomers(VSICustBlockSelectionContract _contract)
    {
        CustTable custTable;
        VSICustBlockQueue queueRecord;

        while select custTable
            where custTable.overdueDate() <= _contract.parmOverdueSinceDate() // conceptual filter
        {
            queueRecord.clear();
            queueRecord.CustAccount = custTable.AccountNum;
            queueRecord.Status      = VSICustBlockQueueStatus::Ready;
            queueRecord.insert();
        }
    }
}

// --- Worker: top-picking loop, run by each parallel batch task ---
class VSICustBlockWorkerService extends SysOperationServiceBase
{
    public void processQueue()
    {
        VSICustBlockQueue queueRecord;
        boolean            hasWork = true;

        while (hasWork)
        {
            hasWork = false;
            ttsBegin;
            // Claim the next ready row — short, fast transaction
            select firstOnly forUpdate queueRecord
                where queueRecord.Status == VSICustBlockQueueStatus::Ready;

            if (queueRecord.RecId)
            {
                queueRecord.Status      = VSICustBlockQueueStatus::InProgress;
                queueRecord.BatchTaskId = this.getCurrentBatchTaskRecId(); // conceptual
                queueRecord.update();
                hasWork = true;
            }
            ttsCommit;

            if (hasWork)
            {
                this.blockOneCustomer(queueRecord.CustAccount, queueRecord);
            }
        }
    }

    private void blockOneCustomer(CustAccount _custAccount, VSICustBlockQueue _queueRecord)
    {
        CustTable custTable;
        try
        {
            ttsBegin;
            custTable = CustTable::find(_custAccount, true);
            custTable.Blocked = CustVendorBlocked::All;
            custTable.update();

            _queueRecord.selectForUpdate(true);
            _queueRecord.Status = VSICustBlockQueueStatus::Done;
            _queueRecord.update();
            ttsCommit;
        }
        catch (Exception::Error)
        {
            ttsBegin;
            _queueRecord.selectForUpdate(true);
            _queueRecord.Status    = VSICustBlockQueueStatus::Error;
            _queueRecord.ErrorText = "Block failed"; // capture real infolog text in practice
            _queueRecord.update();
            ttsCommit;
        }
    }
}
```

**Question 4 — One transaction for the whole list, or one per customer?**

Per customer — never one transaction for the whole run. Two reasons, both load-bearing:

1. **Blast radius of failure.** If customer #4,000 of 10,000 throws (locked record, validation failure, whatever), a single outer transaction rolls back the entire run, including the 3,999 customers already processed successfully. There'd be zero visibility into which ones actually succeeded, and re-running would mean redoing all 4,000 from scratch.
2. **Retry safety requires idempotency, and idempotency requires per-item commit.** With the queue-table design above, a retried or requeued batch task simply resumes: it queries for `Ready` (and optionally `Error`, for auto-retry) rows and picks up exactly where the last run left off. `Done` rows are never touched again. This only works because each customer's block, and its queue-status update, are committed together, atomically, the moment that customer finishes — not deferred until the whole batch completes. The queue table's per-row status *is* the retry-safety mechanism, and it only functions correctly because commits happen at the per-item boundary, not the per-job boundary.
