# Chapter 36: D365 F&O Anti-Pattern Library

In Dynamics 365 Finance & Operations, writing clean, high-performance X++ code is not just a stylistic preference—it is a critical requirement for maintaining an evergreen, scalable system. Anti-patterns are common solutions to recurring problems that ultimately prove to be counterproductive, leading to performance bottlenecks, security vulnerabilities, or upgrade nightmares.

This chapter details the major anti-patterns in D365 F&O development, structured into four main domains: SQL, X++, Architecture, and Performance.

---

## 1. SQL & Data Access Anti-Patterns

### 1.1 Select-in-Loop (The N+1 Query Problem)

#### Bad Pattern
Executing a database query inside a loop for each iteration, causing $N+1$ database roundtrips.

```xpp
// BAD: Executing a separate query for each line
SalesTable salesTable;
SalesLine salesLine;

while select salesTable
    where salesTable.CustAccount == 'US-001'
{
    // High network overhead: 1 query for SalesTable, N queries for SalesLine
    while select salesLine
        where salesLine.SalesId == salesTable.SalesId
    {
        info(strFmt("Item: %1, Qty: %2", salesLine.ItemId, salesLine.SalesQty));
    }
}
```

#### Correct Pattern
Use a single `join` query to bring data back in a unified result set, or use set-based operations (`update_recordset`, `insert_recordset`, `delete_from`).

```xpp
// CORRECT: Single database roundtrip with a join
SalesTable salesTable;
SalesLine salesLine;

while select ItemId, SalesQty from salesLine
    join AccountNum from salesTable
    where salesLine.SalesId == salesTable.SalesId
       && salesTable.CustAccount == 'US-001'
{
    info(strFmt("Item: %1, Qty: %2", salesLine.ItemId, salesLine.SalesQty));
}
```

* **Why it's an Anti-Pattern:** Every database query incurs a roundtrip network cost between the AOS and Azure SQL. Iterating through thousands of records multiplies this latency exponentially.
* **Impact:**
  * **Performance:** Extreme latency, high AOS CPU consumption, network saturation.
  * **Maintainability:** Harder to trace and debug via SQL Server Profiler/LCS.
  * **Upgradability:** Low direct impact, but scales terribly as database size grows.

---

### 1.2 The "Select *" Trap (Unnecessary Field Fetching)

#### Bad Pattern
Selecting all columns from a table when only a few fields are needed.

```xpp
// BAD: Fetches all fields, including large BLOBs/Container/Memo fields
CustTable custTable;
while select custTable
    where custTable.CustGroup == '10'
{
    info(custTable.AccountNum);
}
```

#### Correct Pattern
Explicitly specify field projection to retrieve only the required fields.

```xpp
// CORRECT: Select only the required fields
CustTable custTable;
while select AccountNum from custTable
    where custTable.CustGroup == '10'
{
    info(custTable.AccountNum);
}
```

* **Why it's an Anti-Pattern:** It bypasses SQL covering indexes and forces the engine to read the full clustered index row from memory/disk, transferring unnecessary payload across the network.
* **Impact:**
  * **Performance:** High memory allocations, high IOPS, network saturation, inability to leverage index-only scans.
  * **Maintainability:** Unintended dependencies on uninitialized fields if developers assume fields exist.
  * **Upgradability:** Safe from updates, but inefficient.

---

### 1.3 Suboptimal Join Order & Missing Indexes

#### Bad Pattern
Joining high-cardinality tables without filtering on indexed fields or placing the most restrictive filter secondary in the join sequence.

```xpp
// BAD: Joining without index coverage or improper relation sequencing
InventItemGroup itemGroup;
InventTable inventTable;

while select inventTable
    join itemGroup
    where itemGroup.ItemGroupId == inventTable.ItemGroupId
       && itemGroup.ItemGroupId == 'RawMat'
{
    // ...
}
```

#### Correct Pattern
Filter the primary driving table first using indexed fields, or utilize `SysDa` framework for complex joins where explicit indexing is enforced.

```xpp
// CORRECT: Drive the query using the most restricted indexed table first
InventItemGroup itemGroup;
InventTable inventTable;

while select ItemId from inventTable
    where inventTable.ItemGroupId == 'RawMat'
{
    // Process indexed item table directly
}
```

* **Why it's an Anti-Pattern:** Disregards how the SQL Query Optimizer constructs execution plans, leading to full table/index scans instead of index seeks.
* **Impact:**
  * **Performance:** Deadlocks, query timeouts, severe performance degradation as database tables grow.
  * **Maintainability:** Difficult to spot without query plan execution analysis.
  * **Upgradability:** High maintenance overhead when new Microsoft updates add non-indexed fields.

---

## 2. X++ & Extensibility Anti-Patterns

### 2.1 Hardcoded RecIds, Enums, and Literal Values

#### Bad Pattern
Hardcoding RecIds, Enum integer values, or infrastructure string values directly in code.

```xpp
// BAD: Hardcoding internal database RecId or enum integer
if (custTable.RecId == 5637144521)
{
    // ...
}

if (salesLine.SalesStatus == 1) // Using numeric value instead of Enum
{
    // ...
}
```

#### Correct Pattern
Use strong metadata references (`tableNum()`, `enumStr()`, `enumNum()`, `RecId` parameters, or parameters tables).

```xpp
// CORRECT: Use metadata function and strong types
if (custTable.SalesStatus == SalesStatus::Backorder)
{
    // ...
}
```

* **Why it's an Anti-Pattern:** RecIds change across environments (Dev, Test, Prod), and Enum integer values can shift or become unreadable.
* **Impact:**
  * **Performance:** Minor.
  * **Maintainability:** Silent failures, broken business rules after environment refreshes or data movement.
  * **Upgradability:** High failure rate during major upgrades when schema or enum orders change.

---

### 2.2 Modifying Core Objects & Overlayering (Bypassing CoC)

#### Bad Pattern
Overlayering standard code (deprecated) or using direct method suppression/bypassing validation without leveraging Chain of Command (CoC).

```xpp
// BAD: Bypassing core validation logic via direct update/doUpdate
custTable.AccountNum = '1001';
custTable.doUpdate(); // Bypasses update() method, event handlers, and CoC!
```

#### Correct Pattern
Use Chain of Command (`[ExtensionOf]`) and invoke standard `next` calls while keeping validations intact.

```xpp
// CORRECT: Standard write/update invocation with Extension
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Extension
{
    public void update()
    {
        // Custom logic before
        next update();
        // Custom logic after
    }
}

// In business logic:
custTable.update(); // Triggers standard validations and CoC chain
```

* **Why it's an Anti-Pattern:** `doUpdate()` or `doInsert()` bypasses all business logic, auditing, and events attached to `update()` or `insert()`. Direct modification of SYS layer objects (overlayering) breaks evergreen updates.
* **Impact:**
  * **Performance:** Minimal directly, but can cause data corruption.
  * **Maintainability:** Catastrophic—breaks event models, audit logs, and workflow triggers.
  * **Upgradability:** Prevents Microsoft One Version updates from applying seamlessly.

---

### 2.3 Missing Transaction Management (`ttsBegin` / `ttsCommit`)

#### Bad Pattern
Performing multiple interdependent record modifications without a transactional boundary or holding transactions open during UI/User interaction.

```xpp
// BAD: Missing transaction boundary & UI call inside transaction
ttsBegin;
salesTable.insert();

// User input requested INSIDE transaction block!
if (Box::yesNo("Do you want to proceed?", DialogButton::Yes) == DialogButton::Yes)
{
    salesLine.insert();
}
ttsCommit;
```

#### Correct Pattern
Keep transactions as short as possible, keep user interaction completely outside transaction blocks, and wrap multiple operational units in `ttsBegin` / `ttsCommit`.

```xpp
// CORRECT: Collect user confirmation FIRST, then run atomic transaction
if (Box::yesNo("Do you want to proceed?", DialogButton::Yes) == DialogButton::Yes)
{
    ttsBegin;
    salesTable.insert();
    salesLine.insert();
    ttsCommit;
}
```

* **Why it's an Anti-Pattern:** Leaving transactions open during long processes or user prompts locks database rows/tables, leading to system-wide blocking and deadlocks. Failing to use transactions leads to partial updates (corrupted state).
* **Impact:**
  * **Performance:** Massive database lock escalation, deadlocks, performance bottlenecks.
  * **Maintainability:** Extremely difficult to troubleshoot intermittent database deadlocks.
  * **Upgradability:** Unsound transactional integrity.

---

## 3. Architecture Anti-Patterns

### 3.1 Monster Forms & God Classes

#### Bad Pattern
Placing thousands of lines of complex business logic inside Form methods (e.g., `init()`, `clicked()`, `modified()`) or creating massive helper classes that handle everything.

```xpp
// BAD: Writing heavy business logic inside form controls
[Control("Button")]
class ProcessingButton
{
    public void clicked()
    {
        super();
        // 500 lines of complex posted inventory calculation logic here...
    }
}
```

#### Correct Pattern
Enforce Separation of Concerns. Keep Forms as thin UI controllers and delegate business logic to service/operation classes (`SysOperation`).

```xpp
// CORRECT: Delegate logic to a dedicated service class
[Control("Button")]
class ProcessingButton
{
    public void clicked()
    {
        super();

        CustomPostingService service = CustomPostingService::construct();
        service.runProcessing();
    }
}
```

* **Why it's an Anti-Pattern:** Form code cannot be easily unit-tested (`SysTest`), re-used in background batch processes, or exposed via OData/APIs.
* **Impact:**
  * **Performance:** Slow form load times and UI freezing.
  * **Maintainability:** High code duplication, impossible to write automated tests.
  * **Upgradability:** Form structural changes by Microsoft can break heavily customized form code.

---

### 3.2 Tightly Coupled Custom Services

#### Bad Pattern
Creating monolithic service classes that directly instantiate concrete classes and execute synchronous, long-running processes over external API integrations.

```xpp
// BAD: Direct hardcoded dependency and synchronous execution of external calls
public void processOrder(SalesId _salesId)
{
    // Hardcoded direct instantiation without interfaces or abstraction
    ThirdPartyPaymentProcessor processor = new ThirdPartyPaymentProcessor();
    processor.pay(_salesId); // Blocks thread synchronously
}
```

#### Correct Pattern
Use the `SysOperation` framework, dependency injection/interfaces, and asynchronous event-driven integrations (e.g., Azure Service Bus or Business Events).

```xpp
// CORRECT: Decoupled design using interfaces and contract pattern
public void processOrder(SalesId _salesId)
{
    IPaymentProcessor processor = PaymentProcessorFactory::getProcessor();
    // Execute or enqueue job asynchronously
}
```

* **Why it's an Anti-Pattern:** Tight coupling prevents component swapping, mocks for testing, and fault tolerance during external service outages.
* **Impact:**
  * **Performance:** Monolithic API delays causing AOS thread starvation.
  * **Maintainability:** Changes in external systems break the entire internal business engine.
  * **Upgradability:** Low modularity hinders system evolution.

---

## 4. Performance Anti-Patterns

### 4.1 Excessive Use of InMemory Tables for High Volumes

#### Bad Pattern
Using `InMemory` temp tables for handling large datasets (e.g., tens or hundreds of thousands of records).

```xpp
// BAD: InMemory table holding vast datasets
MyInMemoryTable tempTable; // TableType = InMemory

// Inserting 500,000 records into memory...
```

#### Correct Pattern
Use `TempDB` tables for medium-to-large temporary datasets.

```xpp
// CORRECT: TempDB table instantiation
MyTempDbTable tempTable; // TableType = TempDB
tempTable.linkPhysicalTableInstance(otherInstance);
```

* **Why it's an Anti-Pattern:** `InMemory` tables are stored in the AOS service memory. If dataset size exceeds 128 KB, it falls back to RPC file caching on the AOS host, causing severe memory pressure and disk thrashing. `TempDB` tables are backed by SQL Server's high-performance TempDB database.
* **Impact:**
  * **Performance:** AOS memory leaks, `OutOfMemoryException`, extreme slowdowns.
  * **Maintainability:** High infrastructure instability.
  * **Upgradability:** No direct impact, but severe runtime instability.

---

### 4.2 Unbounded Cross-Company Queries (`crossCompany`)

#### Bad Pattern
Using `crossCompany` without specifying a constrained company container or executing cross-company updates without explicit scope.

```xpp
// BAD: Unbounded cross-company scan across hundreds of legal entities
CustTable custTable;

while select crossCompany custTable
    where custTable.Blocked == CustVendorBlocked::All
{
    // Iterates across ALL companies without restrictions
}
```

#### Correct Pattern
Restrict the `crossCompany` domain using a container of specific DataAreaIds.

```xpp
// CORRECT: Restrict crossCompany to designated legal entities
CustTable custTable;
container targetCompanies = ['USMF', 'DEMF'];

while select crossCompany:targetCompanies custTable
    where custTable.Blocked == CustVendorBlocked::All
{
    // Scoped execution
}
```

* **Why it's an Anti-Pattern:** Cross-company queries disable single-company table caching and force SQL to perform expensive scans across the entire table's partition/company space.
* **Impact:**
  * **Performance:** Extreme query execution delay, index invalidation.
  * **Maintainability:** Risk of unintentional data modifications in foreign legal entities.
  * **Upgradability:** Unsafe multi-tenancy state.

---

### 4.3 Missing Caching Mechanisms for Frequent Lookups

#### Bad Pattern
Repeatedly reading static parameter or setup tables from SQL inside loops or frequently executed methods without table caching.

```xpp
// BAD: Querying setup table repeatedly inside loop
for (int i = 0; i < 10000; i++)
{
    MyParameters params = MyParameters::find(); // Executes SQL query every time if CacheLookup is None
    // Process using params...
}
```

#### Correct Pattern
Configure `CacheLookup` on the table properties (`Found`, `NotInById`, `EntireTable`) or use static in-memory caching patterns.

```xpp
// CORRECT: Static method caching or proper CacheLookup on Table
public static MyParameters find(boolean _update = false)
{
    MyParameters parameter;

    parameter.selectForUpdate(_update);
    // If CacheLookup is set to EntireTable/Found, AOS handles caching automatically
    select firstOnly parameter
        where parameter.Key == 0;

    return parameter;
}
```

* **Why it's an Anti-Pattern:** Database roundtrips for data that rarely changes waste database resources and CPU cycles.
* **Impact:**
  * **Performance:** Unnecessary SQL throughput consumption and increased response times.
  * **Maintainability:** High operational costs.
  * **Upgradability:** Safe, but poor architectural design.

---

## Anti-Pattern Summary Matrix

| Domain | Anti-Pattern | Primary Risk | Recommended Remedy |
|---|---|---|---|
| **SQL** | Select-in-loop (N+1) | Network Latency & SQL Saturation | `join` queries or set-based operations (`update_recordset`) |
| **SQL** | Select * | Memory Pressure & Missing Index Scans | Explicit field projection in `select` statements |
| **SQL** | Missing Indexes | Full Table Scans | Index creation & query plan tuning |
| **X++** | Hardcoded IDs/Enums | Data Instability & Unportable Code | Use metadata functions (`enumNum`, `tableNum`) |
| **X++** | Overlayering / Bypassing CoC | Upgrade Failures & Data Corruption | Chain of Command (`ExtensionOf`) & standard methods |
| **X++** | Open Transactions in UI | Database Deadlocks & Lock Escalation | Short transactions; collect UI input before `ttsBegin` |
| **Architecture** | Monster Forms / God Classes | High Technical Debt & Non-testable code | Separation of Concerns & `SysOperation` framework |
| **Architecture** | Tightly Coupled Services | Brittle System & Cascade Failures | Interface abstraction & Async integration |
| **Performance** | InMemory for Large Datasets | AOS OutOfMemory Crashes | Use `TempDB` table type for large temp data |
| **Performance** | Unbounded Cross-Company | Unscoped SQL Scans | Limit `crossCompany` with container of DataAreaIds |
| **Performance** | Missing Caching | Excessive SQL Load | Enable `CacheLookup` or static code caching |
