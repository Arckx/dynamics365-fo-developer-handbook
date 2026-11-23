---
name: d365-pair-programming-prompts
description: Driver/navigator exercises for complex D365 F&O topics — CoC, SysOperation, batch, security, performance
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Pair Programming Prompts

> **Driver/Navigator format** — Switch roles every 15-20 minutes. Navigator guides, Driver codes. Both discuss.

---

## How to Use

| Role | Responsibility |
|------|----------------|
| **Driver** | Types code, focuses on syntax, runs build/tests |
| **Navigator** | Reviews design, catches issues, suggests alternatives, thinks ahead |
| **Switch** | Every 15-20 min or at natural breakpoints |

> **Golden Rule:** Navigator does NOT touch keyboard. Ask questions instead of giving answers.

---

## Session 1: Chain of Command (CoC) Mastery

### Prompt 1.1: Basic CoC Extension
**Time:** 20 min  
**Goal:** Extend `CustTable.validateWrite()` to require `Email` field when `CustGroup == 'VIP'`

**Navigator Checklist:**
- [ ] Extension class named correctly (`CustTable_Ext`)
- [ ] `[ExtensionOf(tableStr(CustTable))]` attribute
- [ ] Method signature matches base exactly
- [ ] `next validateWrite()` called first
- [ ] Uses `checkFailed()` not `error()`
- [ ] Returns boolean

**Stretch:** Add unit test with SysTest

---

### Prompt 1.2: CoC with Multiple Extensions
**Time:** 25 min  
**Goal:** Simulate ISV + VAR + CUS extensions on same method

**Setup:** Create base class `OrderValidator` with `validate()` method

**Tasks:**
1. **Driver 1 (ISV):** Add logging extension
2. **Switch** — **Driver 2 (VAR):** Add country-specific validation
3. **Switch** — **Driver 3 (CUS):** Add custom field validation
4. **Together:** Trace execution order — verify Base → ISV → VAR → CUS

**Discussion:** What happens if ISV throws exception? Does VAR run?

---

### Prompt 1.3: CoC vs Override vs Event Handler
**Time:** 20 min  
**Goal:** Implement same requirement three ways

**Requirement:** When `SalesTable` is created, set `DeliveryMode = 'AIR'` if `CustGroup == 'EXPRESS'`

**Three Implementations:**
1. **Override** (on a COPY of SalesTable — discuss why bad)
2. **CoC Extension** on `SalesTable.create()`
3. **Post-Event Handler** on `SalesTable.inserted()`

**Comparison Table to Fill:**
| Aspect | Override | CoC | Event Handler |
|--------|----------|-----|---------------|
| Upgrade safety | | | |
| Access to `this` | | | |
| Can modify params | | | |
| Execution order control | | | |
| Return value access | | | |

---

## Session 2: SysOperation Framework

### Prompt 2.1: Build from Scratch
**Time:** 30 min  
**Goal:** Create a batch job to update credit limits for all customers in a group

**Classes to Create:**
1. `CustCreditLimitContract` (DataContract)
2. `CustCreditLimitService` (Service)
3. `CustCreditLimitController` (Controller)
4. Menu Item Action

**Navigator Guides:**
- DataMember attributes on contract
- Service extends `SysOperationServiceBase`
- Controller execution mode (Async vs Sync)
- Dialog customization (optional)

**Test:** Run from menu, verify batch history, check Infolog

---

### Prompt 2.2: Progress Reporting & Cancellation
**Time:** 20 min  
**Goal:** Add progress bar and cancellation support to Prompt 2.1

**Driver adds:**
- `this.setProgress(percent)` in loop
- Check `this.isCancelled()` 
- Handle cancellation gracefully

**Navigator verifies:**
- Progress updates don't kill performance
- `ttsAbort` on cancellation
- Clean rollback

---

### Prompt 2.3: Data Contract Validation
**Time:** 15 min  
**Goal:** Validate contract before service runs

**Add to Contract:**
```xpp
[DataMemberAttribute('CustGroup')]
public CustGroupId parmCustGroup(CustGroupId _v = custGroup) { ... }

[SysOperationValidated]
public boolean validate()
{
    // Check CustGroup exists
}
```

**Discussion:** Where does validation run? Client vs Server?

---

## Session 3: Batch Processing Patterns

### Prompt 3.1: Parallel Batch with LEMLabPersonnel
**Time:** 25 min  
**Goal:** Process 10,000 customers in parallel batches of 1,000

**Architecture:**
- Controller splits work into ranges
- Each range = separate batch task
- LEMLabPersonnel coordinates (or custom)

**Navigator focuses on:**
- Range calculation (avoid gaps/overlaps)
- Error isolation (one range fails ≠ all fail)
- Progress aggregation

---

### Prompt 3.2: Retry with Exponential Backoff
**Time:** 20 min  
**Goal:** Wrap external API call in retry logic

**Pattern:**
```xpp
int retry = 0;
while (retry < 3)
{
    try
    {
        callApi();
        break;
    }
    catch (Exception::Error)
    {
        retry++;
        sleep(1000 * retry * retry); // 1s, 4s, 9s
    }
}
```

**Discussion:** When to retry vs when to fail fast? Deadlock vs timeout vs business error.

---

### Prompt 3.3: Batch Job Monitoring Dashboard
**Time:** 20 min  
**Goal:** Create a form showing batch job status, duration, success rate

**Data Sources:**
- `BatchJob`
- `BatchJobHistory`
- `Batch` (for running tasks)

**UI Requirements:**
- Filter by date, status, job name
- Color coding: Green=Success, Red=Failed, Yellow=Running
- Drill-down to history details

---

## Session 4: Security & XDS

### Prompt 4.1: Design Custom Role from Scratch
**Time:** 25 min  
**Goal:** Create "Warehouse Supervisor" role

**Steps:**
1. List required duties (Inquire Inventory, Manage Transfers, Adjust On-Hand)
2. Create privileges for each duty
3. Assign table/menu item permissions
4. Create role → add duties
5. **Test:** Login as user with only this role — verify access/deny

**Navigator creates checklist:**
- [ ] No `*` permissions
- [ ] Least privilege (Read vs Write vs Create vs Delete)
- [ ] Menu items have `NeededAccessLevel`
- [ ] No direct table permissions where menu item covers it

---

### Prompt 4.2: XDS Policy Implementation
**Time:** 30 min  
**Goal:** Restrict `InventTable` visibility by `InventSiteId` for warehouse users

**Steps:**
1. Create `InventSiteXDSPolicy` class with `xdsFilter()` method
2. Build query filtering `InventSum.InventLocationId` → user's assigned site
3. Register policy in AOT
4. Assign to "Warehouse Worker" role
5. **Test:** Login as warehouse user — verify only their site's items visible

**Navigator thinks about:**
- How to get user's site? (Custom table `UserInventSiteMapping`)
- What if user has NO site assigned? (Deny all vs allow all)
- Performance: `EntireTable` cache on small mapping table

---

### Prompt 4.3: Segregation of Duties Analysis
**Time:** 20 min  
**Goal:** Detect SoD conflicts in current role assignments

**Write a job that:**
1. Gets all users with roles
2. Checks against conflict matrix (AP Clerk + AP Approver, etc.)
3. Outputs report: User | Role A | Role B | Risk Level
4. **Bonus:** Auto-create compensating control task in workflow

---

## Session 5: Performance Tuning

### Prompt 5.1: Query Plan Analysis
**Time:** 25 min  
**Goal:** Find and fix slow query in existing code

**Given Code:**
```xpp
// SLOW: Find customers with orders > $10k in last 30 days
while select custTable
    join salesTable
        where salesTable.CustAccount == custTable.AccountNum
           && salesTable.SalesAmount > 10000
           && salesTable.CreatedDateTime >= dateAdd(today(), -30)
{
    // Process
}
```

**Driver tasks:**
1. Run in Tier-1 with Trace Parser
2. Identify scan vs seek
3. Add missing index
4. Rewrite with `exists join` if appropriate
5. Verify improvement

**Navigator guides:** What columns in index? Order matters!

---

### Prompt 5.2: CacheLookup Optimization
**Time:** 15 min  
**Goal:** Set correct `CacheLookup` on 5 tables

**Tables to Analyze:**
| Table | Row Count | Access Pattern | CacheLookup |
|-------|-----------|----------------|-------------|
| `CustGroup` | 50 | Frequent lookups by PK | ? |
| `CustTable` | 100,000 | By AccountNum, CustGroup | ? |
| `SalesTable` | 1,000,000 | By SalesId, CustAccount | ? |
| `InventTrans` | 10,000,000 | High churn, by ItemId/Date | ? |
| `NumberSequenceTable` | 500 | Frequent, by ID | ? |

**Decision Process:**
- Small, rarely changing → `EntireTable`
- Large, PK lookups → `Found`
- Transactional → `NotInTTS`
- High churn → `None`

---

### Prompt 5.3: Bulk Operations Refactoring
**Time:** 20 min  
**Goal:** Convert loop-based operations to set-based

**Before (Driver identifies):**
```xpp
// 1. Insert in loop
while select tmpTable
{
    realTable.insert();
}

// 2. Update in loop
while select custTable where custTable.CustGroup == 'OLD'
{
    custTable.CustGroup = 'NEW';
    custTable.update();
}

// 3. Delete in loop
while select invTable where invTable.ItemId == 'DISC'
{
    invTable.delete();
}
```

**After (Navigator guides):**
1. `insert_recordset` / `RecordInsertList`
2. `update_recordset`
3. `delete_from`

**Measure:** Time before vs after with 10k records

---

## Session 6: Data Entities & Integration

### Prompt 6.1: Composite Entity Design
**Time:** 30 min  
**Goal:** Create composite entity for Sales Order (Header + Lines)

**Components:**
1. `SalesOrderHeaderEntity` (SalesTable fields)
2. `SalesOrderLineEntity` (SalesLine fields)
3. `SalesOrderCompositeEntity` (links both)
4. Staging tables for both

**Navigator checks:**
- Header `IsHeader = Yes`, Lines `IsHeader = No`
- Relations on `SalesId`
- Staging `processReport` methods
- DMF project with both entities

---

### Prompt 6.2: OData Filtering & Pagination
**Time:** 20 min  
**Goal:** Build Power Automate flow that gets customers with paging

**OData Queries to Test:**
```http
GET /data/CustCustomerV3Entities?$filter=CustGroup eq '10'&$top=100&$skip=0
GET /data/CustCustomerV3Entities?$filter=contains(Name,'Contoso')&$orderby=AccountNum
GET /data/CustCustomerV3Entities?$select=AccountNum,Name,Email&$expand=PrimaryContact
```

**Discussion:** Server-side vs client-side filtering; `$count` for pagination UI

---

### Prompt 6.3: DMF Recurring Import
**Time:** 20 min  
**Goal:** Set up recurring import of vendor catalog from SharePoint

**Architecture:**
1. SharePoint → Logic Apps → Azure Blob
2. Blob → DMF Import (recurring batch)
3. Error handling → Notification

**Navigator designs:**
- Data project with source mapping
- Recurring integration schedule
- Change tracking (only new/modified)
- Failure alert to Teams/Email

---

## Session 7: Advanced Debugging

### Prompt 7.1: Trace Parser Workshop
**Time:** 30 min  
**Goal:** Analyze a slow form load trace

**Steps:**
1. Enable trace on form open (Tools → Trace)
2. Reproduce slow load
3. Open trace in Trace Parser
4. Identify:
   - Top 5 CPU consumers
   - SQL queries > 100ms
   - Call stack depth
   - Lock contention

**Navigator interprets:** What does "Clustered Index Scan" on `CustTrans` mean here?

---

### Prompt 7.2: Deadlock Reproduction
**Time:** 25 min  
**Goal:** Create and resolve a deadlock

**Scenario:**
- Session 1: Update `CustTable` then `VendTable`
- Session 2: Update `VendTable` then `CustTable`
- Both in transaction

**Driver writes two jobs; Navigator runs simultaneously**

**Resolution:** Consistent lock ordering (always Cust then Vend)

---

### Prompt 7.3: Memory Leak Hunt
**Time:** 20 min  
**Goal:** Find object leak in long-running batch

**Given:** Batch processes 100k records, memory grows 500MB

**Code Pattern (leak):**
```xpp
while select record
{
    MyClass obj = new MyClass(); // Never cleaned up
    obj.process(record);
    // obj goes out of scope but...
}
```

**Fix:** Reuse object, or ensure GC, or use `using` pattern (if .NET interop)

---

## Session 8: Testing Deep Dive

### Prompt 8.1: Property-Based Test Design
**Time:** 25 min  
**Goal:** Write property tests for `InventQty` operations

**Properties to Verify:**
1. `add(a, 0) == a` (identity)
2. `add(a, b) == add(b, a)` (commutative)
3. `sub(a, a) == 0` (self-inverse)
4. `mul(a, 1) == a` (identity)
5. Round-trip: `qty → str → qty` equals original

**Navigator writes generators; Driver writes properties**

---

### Prompt 8.2: Test Data Factory Pattern
**Time:** 20 min  
**Goal:** Build factory for `SalesTable` with lines

**Factory Interface:**
```xpp
interface ISalesOrderFactory
{
    SalesTable create(Map _overrides);
    List createMultiple(int _count, Map _overrides);
}
```

**Implementation:**
- Creates customer, items, warehouse
- Builds header + 1-5 lines
- Supports overrides for specific test scenarios

---

### Prompt 8.3: Integration Test with Database
**Time:** 25 min  
**Goal:** Test Order-to-Cash flow end-to-end

**Test Steps:**
1. Create customer (factory)
2. Create sales order (factory)
3. Reserve inventory
4. Pick/pack (warehouse)
5. Post packing slip
6. Post invoice
7. Verify: CustTrans, InventTrans, LedgerTrans created

**Cleanup:** Transaction rollback or test company

---

## Session 9: DevOps Pipeline

### Prompt 9.1: Pipeline as Code Review
**Time:** 20 min  
**Goal:** Review and improve `azure-pipelines-build.yml`

**Checklist:**
- [ ] NuGet restore before build
- [ ] BP checks fail build on error
- [ ] Unit tests run and publish results
- [ ] Model version auto-incremented
- [ ] Deployable package artifact published
- [ ] Code coverage threshold enforced

**Navigator suggests:** Parallel jobs for compile + test?

---

### Prompt 9.2: Release Gate Design
**Time:** 15 min  
**Goal:** Define approval gates for UAT → Prod

**Gates:**
1. **Automated:** All tests pass, performance baseline met
2. **Manual:** Business stakeholder approval
3. **Scheduled:** Deploy window (e.g., weekend 2-4 AM)
4. **Rollback:** Auto-rollback on health check failure

---

## Session 10: Capstone Integration

### Prompt 10.1: End-to-End Architecture Review
**Time:** 45 min  
**Goal:** Review capstone project architecture

**Review Checklist:**
```
□ Data model normalized? PK/FK? EDTs?
□ Extensibility: CoC/Events only?
□ Security: Roles, XDS, audit logging?
□ Batch: Long ops async? Progress? Retry?
□ Integration: Data Entities? OData? Error handling?
□ Tests: Unit >80%? Integration for key flows?
□ Docs: Arch diagrams? Deployment guide?
□ Pipeline: Build → Test → Deploy?
```

**Output:** Annotated architecture diagram with risk ratings

---

### Prompt 10.2: Code Review Simulation
**Time:** 30 min  
**Goal:** Practice code review on sample PR

**Sample PR includes:**
- 1 CoC extension with `super()` instead of `next`
- 1 `select *` in loop
- 1 missing `ttsAbort` in catch
- 1 hardcoded string in where clause
- 1 event handler that's not static
- 1 missing `[ExtensionOf]` attribute

**Driver reviews; Navigator facilitates discussion**

---

## Facilitator Notes

### For Mentors Running Sessions

| Tip | Description |
|-----|-------------|
| **Prep environment** | Pre-create Tier-1, VS, Git before session |
| **Timebox strictly** | Use timer; switch roles even if incomplete |
| **Debrief 5 min** | What worked? What was confusing? One action item |
| **Rotate pairs** | Different partners expose different thinking |
| **Document patterns** | Create team wiki from session outputs |

### Difficulty Scaling

| Level | Adjustments |
|-------|-------------|
| **Beginner** | Provide starter code; more navigator guidance |
| **Intermediate** | Skeleton only; navigator asks leading questions |
| **Advanced** | Blank file; navigator only intervenes on blockers |

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*