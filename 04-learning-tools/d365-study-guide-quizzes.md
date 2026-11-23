---
name: d365-study-guide-quizzes
description: Multiple-choice quizzes for each chapter with explanations — 5-10 questions per chapter
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Study Guide Quizzes

> **5-10 MCQs per chapter** with explanations. Use for self-check after reading each chapter.

---

## Chapter 1: Platform Architecture & AOT

### Q1: Which tier executes your X++ business logic?
**A.** Presentation Tier  
**B.** Application Tier (AOS) ✅  
**C.** Database Tier  
**D.** Integration Tier  

> **Explanation:** X++ IL code runs in the AOS (Application Object Server) on the Application Tier. The Presentation Tier only renders UI; the Database Tier stores data; the Integration Tier handles external connections.

### Q2: The AOT is stored as:
**A.** SQL tables in the model database  
**B.** XML files in a file share (PackagesLocalDirectory) ✅  
**C.** JSON in Azure Blob Storage  
**D.** Binary format in the AOS memory  

> **Explanation:** The AOT is a file-system-based metadata repository, not a SQL database. It lives in `C:\AOSService\PackagesLocalDirectory` (or `K:\` in cloud).

### Q3: What happens when you build your project in Visual Studio?
**A.** X++ compiles to C#  
**B.** X++ compiles to .NET IL (Intermediate Language) ✅  
**C.** X++ transpiles to JavaScript  
**D.** X++ is interpreted at runtime  

> **Explanation:** X++ compiles to .NET IL which runs on the CLR (Common Language Runtime) in the AOS.

### Q4: Which Azure component hosts the AOS workers?
**A.** Azure SQL Database  
**B.** Azure App Service ✅  
**C.** Azure Storage  
**D.** Azure Key Vault  

> **Explanation:** AOS workers run in Azure App Service (or on Windows Server in Tier-1).

### Q5: The model store is:
**A.** A SQL database containing model metadata  
**B.** A file share containing compiled models ✅  
**C.** An Azure DevOps artifact feed  
**D.** A Visual Studio project file  

---

## Chapter 2: Models, Layers, Packages

### Q1: What is the correct layer hierarchy (lowest to highest priority)?
**A.** SYS → ISV → VAR → CUS → USR ✅  
**B.** USR → CUS → VAR → ISV → SYS  
**C.** CUS → VAR → ISV → SYS → USR  
**D.** VAR → SYS → ISV → CUS → USR  

> **Explanation:** Higher layers override lower. SYS = Microsoft core, USR = user personalizations.

### Q2: You should NEVER modify objects in which layer directly?
**A.** CUS  
**B.** VAR  
**C.** SYS ✅  
**D.** ISV  

> **Explanation:** SYS is Microsoft's core. Modifications will be lost on updates. Use extensions instead.

### Q3: A deployable package contains:
**A.** Only .xpp source files  
**B.** .axmodel file + ModuleDescriptor.xml ✅  
**C.** Compiled .dll files only  
**D.** SQL scripts for database  

### Q4: What does ModuleDescriptor.xml define?
**A.** Model name, version, publisher, dependencies ✅  
**B.** Table schemas  
**C.** Form layouts  
**D.** Security roles  

### Q5: Two models in the same layer — which wins?
**A.** The one installed first  
**B.** The one with higher version number  
**C.** Undefined — avoid this ✅  
**D.** Alphabetically first  

> **Explanation:** Only one model per layer per object. Conflicts must be resolved manually.

---

## Chapter 3: VS Setup & Language Mindset

### Q1: D365 F&O follows which mindset?
**A.** Object-First  
**B.** Relational-First ✅  
**C.** Functional-First  
**D.** API-First  

> **Explanation:** The database is the primary focus; data access and movement drive the architecture.

### Q2: What does "Extensibility as a Constraint" mean?
**A.** You can't extend anything  
**B.** Customizations must be non-invasive (CoC, Event Handlers) ✅  
**C.** Only Microsoft can extend  
**D.** Extensions are optional  

### Q3: Which is an EDT, not a base type?
**A.** `string`  
**B.** `int`  
**C.** `CustAccount` ✅  
**D.** `real`  

> **Explanation:** Always use EDTs (Extended Data Types) in tables/forms, never base types directly.

### Q4: What does `real` provide that `float` doesn't?
**A.** Better performance  
**B.** Decimal precision (safe for money) ✅  
**C.** Larger range  
**D.** Integer storage  

### Q5: Block scope in X++ means:
**A.** Variables declared in `{}` are only visible inside that block ✅  
**B.** Variables are scoped to the class  
**C.** Variables persist across method calls  
**D.** Variables are thread-local  

---

## Chapter 4: LCS & Development Lifecycle

### Q1: What is LCS (Lifecycle Services)?
**A.** Local Code Storage  
**B.** Lifecycle management portal for D365 F&O ✅  
**C.** Language Compilation System  
**D.** Layer Configuration Service  

### Q2: Tier-1 environment is:
**A.** Production  
**B.** Microsoft-managed UAT  
**C.** Developer sandbox with full admin ✅  
**D.** Build agent only  

### Q3: Deployable packages are uploaded to:
**A.** Azure DevOps  
**B.** LCS Asset Library ✅  
**C.** GitHub  
**D.** Azure Blob Storage  

### Q4: Hotfixes are applied via:
**A.** Manual SQL scripts  
**B.** LCS Environment updates ✅  
**C.** Visual Studio publish  
**D.** PowerShell scripts  

### Q5: The build pipeline produces:
**A.** Source code zip  
**B.** .axmodel file (deployable package) ✅  
**C.** Docker image  
**D.** Executable .exe  

---

## Chapter 5: X++ Data Types & Variables

### Q1: Which type should you use for monetary values?
**A.** `float`  
**B.** `real` ✅  
**C.** `int64`  
**D.** `anytype`  

### Q2: `int64` is used for:
**A.** Large integers  
**B.** RecId (64-bit record identifiers) ✅  
**C.** Precision decimals  
**D. `anytype` values  

### Q3: What is `anytype`?
**A.** A generic type that can hold any value ✅  
**B.** An array type  
**C. A nullable type  
**D. A variant type  

### Q4: Variable naming convention for class fields:
**A.** `camelCase`  
**B.** `_camelCase` (underscore prefix) ✅  
**C.** `PascalCase`  
**D.** `UPPER_SNAKE_CASE`  

### Q5: Constants are named:
**A.** `camelCase`  
**B.** `PascalCase`  
**C.** `UPPER_SNAKE_CASE` ✅  
**D.** `_camelCase`  

---

## Chapter 6: Control Flow & CRUD

### Q1: Which is the idiomatic way to iterate records?
**A.** `for` loop with `select` inside  
**B.** `while select` ✅  
**C.** `do while` with `next`  
**D.** `foreach`  

### Q2: `exists join` returns:
**A.** All matching rows from both tables  
**B.** Boolean — true if any match exists ✅  
**C.** Only rows from the second table  
**D.** Cartesian product  

### Q3: Bulk insert uses:
**A.** `insert()` in a loop  
**B.** `RecordInsertList` or `insert_recordset` ✅  
**C.** `createRecord()`  
**D.** `bulkInsert()`  

### Q4: Transaction pattern:
```xpp
ttsBegin;
try
{
    // ...
    ttsCommit;
}
catch
{
    ttsAbort;
    throw;
}
```
**What happens if `ttsAbort` is missing?**
**A.** Transaction commits anyway  
**B.** Transaction rolls back but error swallowed  
**C.** Uncommitted transaction stays open ✅  
**D.** Compile error  

### Q5: `forUpdate` keyword:
**A.** Updates the record immediately  
**B.** Locks the row for update (pessimistic locking) ✅  
**C.** Marks record for later update  
**D.** Forces optimistic locking  

---

## Chapter 7: Methods, Exceptions, Classes

### Q1: In a base class override, call parent with:
**A.** `next methodName()`  
**B.** `super()` ✅  
**C.** `base.methodName()`  
**D.** `parent::methodName()`  

### Q2: In a CoC extension, call next in chain with:
**A.** `super()`  
**B.** `next methodName()` ✅  
**C.** `base.methodName()`  
**D.** `this.methodName()`  

### Q3: Which exception type should you catch for retry logic?
**A.** `Exception::Error`  
**B.** `Exception::Deadlock` ✅  
**C.** `Exception::Warning`  
**D.** `Exception::Info`  

### Q4: `checkFailed()` vs `error()` in validation:
**A.** Same behavior  
**B.** `checkFailed()` returns false; `error()` throws ✅  
**C.** `checkFailed()` throws; `error()` returns false  
**D.** `checkFailed()` logs only  

### Q5: Abstract class in X++:
**A.** Cannot be instantiated, can have abstract methods ✅  
**B.** Can be instantiated  
**C.** Must have only abstract methods  
**D.** Same as interface  

---

## Chapter 8: VS Development & Activity

### Q1: To debug X++, you need:
**A.** Browser dev tools  
**B.** Visual Studio debugger attached to AOS ✅  
**C.** SQL Profiler  
**D.** Print statements only  

### Q2: "Refresh Models" in VS does:
**A.** Compiles all models  
**B.** Syncs AOT metadata from server to local ✅  
**C.** Updates NuGet packages  
**D.** Restarts AOS  

### Q3: "Synchronize Database" creates:
**A.** Model files  
**B.** SQL tables from AOT metadata ✅  
**C.** Deployable packages  
**D.** Unit tests  

### Q4: Breakpoints in standard Microsoft code work when:
**A.** "Enable Just My Code" = ON  
**B.** "Enable Just My Code" = OFF ✅  
**C.** Debugging Tier-1 only  
**D.** Never  

### Q5: Infolog is accessed via:
**A.** View → Infolog or Ctrl+Alt+I ✅  
**B.** Debug → Windows → Output  
**C.** Dynamics 365 → Infolog  
**D. Right-click project → Infolog  

---

## Chapter 9: Table Design & EDTs

### Q1: EDT Golden Rule:
**A.** Use base types for performance  
**B.** Always use an EDT in tables/forms ✅  
**C.** Create new EDT for every field  
**D.** EDTs are optional  

### Q2: TempDB vs InMemory:
**A.** TempDB = persisted, supports indexes; InMemory = fast, <1000 rows ✅  
**B.** InMemory = persisted; TempDB = memory only  
**C.** Same thing  
**D.** TempDB = SQL temp tables only  

### Q3: `validateWrite()` is called:
**A.** Only on insert  
**B.** On insert AND update ✅  
**C.** Only on update  
**D.** On delete  

### Q4: Field groups are used for:
**A.** Indexing  
**B.** Auto-form generation and list layouts ✅  
**C.** Security  
**D.** Relations  

### Q5: Alternate key vs Primary key:
**A.** Same thing  
**B.** Primary = clustered; Alternate = unique non-clustered ✅  
**C.** Alternate can have nulls; Primary cannot  
**D.** Alternate is for FK only  

---

## Chapter 10: Form Architecture & CoC

### Q1: Form extension naming:
**A.** `FormName_Extension`  
**B.** `FormName_Ext` ✅  
**C.** `Extension_FormName`  
**D.** `Ext_FormName`  

### Q2: CoC on form `init()`:
```xpp
public void init()
{
    next init(); // Call base first
    // Custom code
}
```
**Why call `next` first?**
**A.** Base initializes data sources ✅  
**B.** Required by compiler  
**C.** Performance  
**D.** Security  

### Q3: Data source join types:
**A.** Inner, Outer, Exists, NotExists, Delayed ✅  
**B.** Left, Right, Full, Cross  
**C.** Join, Merge, Hash  
**D.** One-to-One, One-to-Many  

### Q4: MultiSelectionHelper is for:
**A.** Multiple data sources  
**B.** Grid multi-select actions ✅  
**C.** Multiple forms  
**D.** Multiple users  

### Q5: Form patterns include:
**A.** ListPage, Grid, FactBox, Tree, Dialog, Details Master ✅  
**B.** Master, Detail, Wizard, Tab  
**C.** MVC, MVVM, MVP  
**D.** Reactive, Declarative  

---

## Chapter 11: Views & Lookups

### Q1: View vs Table:
**A.** View stores data; Table doesn't  
**B.** View is virtual (SQL query); Table stores data ✅  
**C.** View is faster  
**D.** View supports inserts  

### Q2: SysTableLookup is used for:
**A.** Table relations  
**B.** Building form lookups programmatically ✅  
**C.** Data entity lookups  
**C.** View definitions  

### Q3: Derived view:
**A.** View based on another view ✅  
**B.** View with computed columns  
**C.** View with parameters  
**D.** Temporary view  

### Q4: Multi-select lookup:
**A.** Standard lookup property  
**B.** Requires `MultiSelect = Yes` on form control + custom code ✅  
**C.** Not supported  
**D.** Only for enum fields  

### Q5: View extension:
**A.** `[ExtensionOf(viewStr(Name))]` ✅  
**B.** Modify base view directly  
**C.** Not supported  
**D. Only for composite entities  

---

## Chapter 12: Class Fundamentals & RunBase

### Q1: RunBase pattern classes:
**A.** 1 class (the job)  
**B.** 2 classes (batch + dialog)  
**C.** 3 classes (Contract, Service, Controller) ✅  
**D.** 4 classes  

> **Note:** RunBase is single class; SysOperation is 3 classes.

### Q2: SysOperation DataContract:
**A.** Defines UI dialog fields ✅  
**B.** Contains business logic  
**C.** Runs the batch  
**D.** Handles retries  

### Q3: SysOperation Controller:
**A.** Business logic  
**B.** Entry point, execution mode, dialog customization ✅  
**C.** Data validation  
**D.** Database access  

### Q4: `dialog()` method in RunBase:
**A.** Returns Dialog object with fields ✅  
**B.** Shows message box  
**C. Creates form  
**D.** Validates input  

### Q5: Batch execution modes:
**A.** Sync, Async, Scheduled ✅  
**B.** Immediate, Delayed, Recurring  
**C.** Foreground, Background, Server  
**D.** Manual, Auto, Timer  

---

## Chapter 13: Event Handlers & Command Pattern

### Q1: Pre-event handler:
**A.** Runs after base method  
**B.** Runs before base method, can cancel ✅  
**C.** Runs in separate thread  
**D.** Cannot access parameters  

### Q2: Post-event handler:
**A.** Runs before base method  
**B.** Runs after base method, can read result ✅  
**C.** Can modify base method parameters  
**D.** Cannot access return value  

### Q3: Event handler attribute:
```xpp
[SubscribesTo(classStr(Class), methodStr(Method), true/false)]
```
**Third parameter:**
**A.** Priority  
**B.** Pre (false) / Post (true) ✅  
**C.** Company scope  
**D.** User scope  

### Q4: Command pattern in D365:
**A.** Menu Item → Class → Method chain ✅  
**B.** SQL command execution  
**C.** Batch command queue  
**D.** Form command buttons  

### Q5: Event handler method must be:
**A.** Instance  
**B.** Static ✅  
**C.** Abstract  
**D.** Virtual  

---

## Chapter 14: Extensibility Deep Dive

### Q1: CoC vs Override vs Event Handler:
**A.** Override = preferred  
**B.** CoC = preferred for method augmentation ✅  
**C.** Event Handler = preferred for all  
**D.** All equal  

### Q2: Extension class naming:
**A.** `ClassName_Extension`  
**B.** `ClassName_Ext` ✅  
**C.** `Extension_ClassName`  
**D.** `Ext_ClassName`  

### Q3: `[ExtensionOf]` attribute applies to:
**A.** Classes, Tables, Forms, Views ✅  
**B.** Classes only  
**C.** Tables only  
**D.** Forms only  

### Q4: Multiple extensions on same method — execution order:
**A.** Alphabetical  
**B.** Layer order: SYS → ISV → VAR → CUS → USR ✅  
**C.** Random  
**D.** By model name  

### Q5: `prmIsDefault()` in CoC:
**A.** Checks if parameter is default value ✅  
**B.** Sets default parameter  
**C.** Gets default parameter  
**D.** Validates parameter  

---

## Chapter 15: Security Model

### Q1: Security hierarchy (top to bottom):
**A.** Role → Duty → Privilege → Permission ✅  
**B.** Permission → Privilege → Duty → Role  
**C.** Role → Privilege → Duty → Permission  
**D.** Duty → Role → Privilege → Permission  

### Q2: XDS (Extensible Data Security) provides:
**A.** Field-level encryption  
**B. Record-level filtering ✅  
**C. Column-level permissions  
**D. Row-level encryption  

### Q3: XDS policy types:
**A.** Constrained, Contextual, Role-based, Hierarchical, Time-based ✅  
**B.** Simple, Complex, Advanced  
**C.** Read, Write, Admin  
**D.** Global, Company, User  

### Q4: Privilege access levels:
**A.** Read, Write, Create, Delete, Correct ✅  
**B.** View, Edit, Full, None  
**C.** Select, Insert, Update, Delete  
**D.** User, Power User, Admin  

### Q5: Security Key purpose:
**A.** Encryption  
**B.** Scope access by business context ✅  
**C.** Authentication  
**D.** Audit  

---

## Chapter 16: Data Entities

### Q1: Data Entity types:
**A.** Primary, Composite, Derived ✅  
**B.** Simple, Complex, Nested  
**C.** Read, Write, ReadWrite  
**D.** Table, View, Query  

### Q2: Composite entity = 
**A.** Header entity + Line entity + Staging tables ✅  
**B.** Multiple tables joined  
**C.** Entity with computed columns  
**D.** Entity extending another  

### Q3: OData endpoint format:
**A.** `/api/EntityName`  
**B.** `/data/EntityName` ✅  
**C.** `/odata/EntityName`  
**D.** `/entity/EntityName`  

### Q4: DMF staging pattern:
**A.** Source → Staging → Validation → Target ✅  
**B.** Source → Target directly  
**C.** Source → Transform → Target  
**D.** Source → Queue → Target  

### Q5: `IsPublic = Yes` on entity enables:
**A.** Public constructor  
**B.** OData endpoint exposure ✅  
**C.** Public inheritance  
**D.** Public fields only  

---

## Chapter 17: SSRS & Electronic Reporting

### Q1: SSRS report data provider:
**A.** `SrsReportDataProvider` (RDP) ✅  
**B.** `ReportDataProvider`  
**C.** `SrsDataProvider`  
**D.** `SSRSProvider`  

### Q2: RDL = 
**A.** Report Definition Language (layout) ✅  
**B.** Report Data Layer  
**C.** Runtime Data Link  
**D.** Render Definition Logic  

### Q3: Electronic Reporting (ER) is:
**A.** Code-based reporting  
**B.** Configurable, no-code reporting ✅  
**C.** SSRS replacement  
**D.** Only for finance  

### Q4: ER components:
**A.** Model, Format, Mapping ✅  
**B.** Query, Layout, Parameter  
**C.** Source, Transform, Target  
**D.** Input, Process, Output  

### Q5: Pre-processing in SSRS:
**A.** Data transformation before rendering ✅  
**B.** Parameter validation  
**C.** Layout compilation  
**D.** Print setup  

---

## Chapter 18: Batch Processing

### Q1: Modern batch framework:
**A.** RunBaseBatch  
**B.** SysOperation ✅  
**C.** BatchFramework  
**D.** AsyncOperation  

### Q2: Batch progress reporting:
**A.** `this.setProgress(percent)` ✅  
**B.** `progressBar.update()`  
**C.** `info()` with percent  
**D.** Automatic  

### Q3: Batch retry:
**A.** Manual only  
**B.** Automatic on transient errors ✅  
**C.** Not supported  
**D.** Only for deadlocks  

### Q4: Batch cancellation:
**A.** Not possible  
**B.** User can cancel via Batch Job form ✅  
**C.** Only admin can cancel  
**D.** Auto-cancel on error  

### Q5: `RunBaseBatch.clientType()`:
**A.** Returns `ClientType::Client`  
**B.** Returns `ClientType::Server` ✅  
**C.** Returns `ClientType::Both`  
**D.** Not required  

---

## Chapter 19: SysTest Framework

### Q1: Test class attribute:
**A.** `[TestClass]`  
**B.** `[SysTestCase]` ✅  
**C.** `[TestFixture]`  
**D.** `[UnitTest]`  

### Q2: Test method attribute:
**A.** `[TestMethod]`  
**B.** `[SysTestMethod]` ✅  
**C.** `[Test]`  
**D.** `[Fact]`  

### Q3: Test isolation:
**A.** Manual cleanup required  
**B.** Each test runs in transaction → auto-rollback ✅  
**C.** Separate database per test  
**D.** Shared test data  

### Q4: Property-based testing:
**A.** Test specific examples  
**B.** Test invariants across thousands of generated inputs ✅  
**C.** Test UI properties  
**D.** Test database properties  

### Q5: Assert methods:
**A.** `assertEquals()`, `assertTrue()`, `assertFalse()`, `assertNull()`, `assertNotNull()` ✅  
**B.** `Assert.AreEqual()`, `Assert.IsTrue()`  
**C.** `expect().toBe()`  
**D.** `check()`  

---

## Chapter 20: LCS Deep Dive & CI/CD

### Q1: Build pipeline produces:
**A.** Source zip  
**B.** .axmodel + ModuleDescriptor.xml ✅  
**C.** Docker image  
**D.** Executable  

### Q2: Release pipeline deploys to:
**A.** Tier-1 → UAT → Prod via LCS API ✅  
**B.** Direct to Prod  
**C.** Azure DevOps only  
**D.** GitHub only  

### Q3: Model management in LCS:
**A.** Install/Upgrade models ✅  
**B.** Compile models  
**C.** Debug models  
**D.** Test models  

### Q4: Database movement operations:
**A.** Backup, Restore, Refresh, Sync ✅  
**B.** Import, Export, Sync  
**C.** Attach, Detach, Sync  
**D.** Copy, Move, Sync  

### Q5: Pipeline stages:
**A.** Build → Test → Deploy ✅  
**B.** Compile → Package → Release  
**C.** Code → Build → Run  
**D.** Dev → Test → Prod  

---

## Chapter 21: Performance & SQL Tuning

### Q1: Query plan — best operator:
**A.** Clustered Index Scan  
**B.** Clustered Index Seek ✅  
**C.** Table Scan  
**D.** Key Lookup  

### Q2: `CacheLookup = EntireTable` for:
**A.** Transactional tables  
**B.** Setup/reference tables (small) ✅  
**C.** Large master data  
**D. Temp tables  

### Q3: Anti-pattern — select in loop:
```xpp
while select custTable
{
    select salesTable where salesTable.CustAccount == custTable.AccountNum;
}
```
**Fix:**
**A.** `exists join` or `join` ✅  
**B.** `for` loop  
**C.** `RecordInsertList`  
**D.** `crossCompany`  

### Q4: Deadlock handling:
**A.** Ignore  
**B.** Catch `Exception::Deadlock`, retry max 3 with backoff ✅  
**C.** Increase timeout  
**D.** Restart AOS  

### Q5: `update_recordset` vs `update()` in loop:
**A.** Same performance  
**B.** `update_recordset` = single SQL statement ✅  
**C.** `update()` is faster  
**D. Only for small tables  

---

## Chapter 22: Capstone Projects

### Q1: Capstone project should demonstrate:
**A.** Only X++ syntax  
**B.** End-to-end architecture (data, UI, logic, security, tests) ✅  
**C. Only forms  
**D. Only batch jobs  

### Q2: Manufacturing P2P compliance includes:
**A.** Purchase → Produce → Sell ✅  
**B.** Buy → Store → Sell  
**C.** Order → Ship → Invoice  
**D.** Plan → Execute → Report  

### Q3: Architecture documentation should include:
**A.** Data model, security, integrations, deployment ✅  
**B.** Only code comments  
**C.** Only UI mockups  
**D. Only database schema  

### Q4: Deliverable for capstone:
**A.** Working solution + documentation + tests ✅  
**B.** Code only  
**C.** Presentation only  
**D.** Database dump  

### Q5: Code review for capstone checks:
**A.** Naming, CoC, transactions, SQL, security, tests ✅  
**B.** Only compilation  
**C.** Only functionality  
**D. Only performance  

---

## Chapter 23: Advanced X++ Patterns

### Q1: `SysDa` is:
**A.** Legacy data access  
**B.** Modern fluent data access API ✅  
**C.** Security data access  
**D.** Batch data access  

### Q2: `RecordInsertList`:
**A.** Slowest insert  
**B.** Fastest bulk insert (batches to SQL) ✅  
**C.** Only for temp tables  
**D.** Requires transaction  

### Q3: `var` keyword:
**A.** Dynamic typing  
**B.** Type inference (compile-time) ✅  
**C.** Variant type  
**D.** `anytype` alias  

### Q4: `orig()` in CoC/override:
**A.** Gets original values before update ✅  
**B.** Calls original method  
**C.** Gets original object  
**D.** Resets to default  

### Q5: CoC execution order:
**A.** Ext → Base  
**B.** Base → Ext1 (ISV) → Ext2 (VAR) → Ext3 (CUS) ✅  
**C.** Alphabetical  
**D.** Random  

---

## Chapter 24: Production Debugging

### Q1: Common production issues:
**A.** Timeouts, memory leaks, slow forms, deadlocks ✅  
**B.** Compile errors, syntax errors  
**C.** Deployment failures  
**D.** License issues  

### Q2: Trace Parser analyzes:
**A.** X++ execution traces (CPU, SQL, calls) ✅  
**B.** SQL query plans only  
**C.** Memory dumps only  
**D.** Network traffic  

### Q3: SQL Query Store:
**A.** Stores query plans and performance over time ✅  
**B.** Stores SQL queries only  
**C.** Stores execution logs  
**D.** Stores deadlock graphs  

### Q4: Slow form diagnosis:
**A.** Check data source count, query complexity, control count ✅  
**B.** Recompile form  
**C.** Clear cache  
**D.** Restart AOS  

### Q5: Memory leak detection:
**A.** Task Manager  
**B.** PerfMon / dotMemory / Trace Parser ✅  
**C.** SQL Profiler  
**D.** Event Viewer  

---

## Chapter 25: Power Platform & Copilot

### Q1: Integration options:
**A.** OData, REST, Logic Apps, Power Automate, Dataverse, Dual-write ✅  
**B.** Only OData  
**C.** Only REST  
**D. Only SQL  

### Q2: Dual-write:
**A.** Two-way sync between F&O and Dataverse ✅  
**B.** Backup strategy  
**C.** Batch processing  
**D.** Reporting  

### Q3: Power Automate:
**A.** Flow designer for business processes ✅  
**B.** RPA tool only  
**C.** BI tool  
**D. Database sync  

### Q4: Copilot extensibility:
**A.** Plugins (read), Actions (write), Skills (multi-step) ✅  
**B.** Only plugins  
**C.** Only actions  
**D. Only skills  

### Q5: Custom API for Copilot:
**A.** Required for all integrations  
**B.** Preferred over raw OData for plugins/actions ✅  
**C.** Not supported  
**D. Only for skills  

---

## Chapter 26: Module Specialization

### Q1: Finance key tables:
**A.** `LedgerJournalTable`, `LedgerJournalTrans`, `CustTrans`, `VendTrans`, `AssetTable` ✅  
**B.** `InventTable`, `InventSum`, `PurchTable`  
**C.** `HcmWorker`, `HcmEmployment`  
**D.** `SalesTable`, `SalesLine`, `CustTable`  

### Q2: SCM key tables:
**A.** `InventTable`, `InventSum`, `PurchTable`, `SalesTable`, `ProdTable`, `WMSLocation` ✅  
**B.** `LedgerJournalTable`, `CustTrans`  
**C.** `HcmWorker`, `HcmPosition`  
**D.** `ProjTable`, `ProjTrans`  

### Q3: HR key tables:
**A.** `HcmWorker`, `HcmEmployment`, `HcmPosition`, `HcmCompensation` ✅  
**B.** `CustTable`, `VendTable`  
**C.** `InventTable`, `InventSum`  
**D.** `LedgerJournalTable`, `AssetTable`  

---

## Chapter 27: Advanced DevOps

### Q1: CD pipeline includes:
**A.** DB movement, build automation ✅  
**B.** Only build  
**C.** Only deploy  
**D.** Only test  

### Q2: Database movement:
**A.** Backup/Restore, Refresh, Sync ✅  
**B.** Import/Export only  
**C.** Sync only  
**D.** Manual scripts only  

### Q3: Build automation:
**A.** Compile, BP check, Unit test, Package ✅  
**B.** Compile only  
**C.** Package only  
**D.** Test only  

---

## Chapter 28: Compliance & ISV

### Q1: GDPR rights:
**A.** Access, Rectification, Erasure, Restriction, Portability, Object ✅  
**B.** Read, Write, Delete  
**C.** View, Edit, Admin  
**D.** Select, Insert, Update  

### Q2: Financial tags:
**A.** Dimensions for reporting (no GL impact) ✅  
**B.** GL account tags  
**C.** Tax tags  
**D.** Currency tags  

### Q3: Date effectivity:
**A.** ValidFrom/ValidTo on records (historical tracking) ✅  
**B.** Created/Modified dates  
**C.** Fiscal calendar  
**D.** Expiration dates  

---

## Chapter 29: Workflow Architecture

### Q1: Workflow types:
**A.** Document (business doc), Event (system event) ✅  
**B.** Sequential, Parallel  
**C.** Approval, Task  
**D.** Sync, Async  

### Q2: Key components:
**A.** Workflow, Elements, Approvals, Tasks, Automated Tasks ✅  
**B.** States, Transitions, Actions  
**C.** Nodes, Edges, Conditions  
**D.** Steps, Gates, Events  

---

## Chapter 30: Number Sequences

### Q1: NumberSeq API:
**A.** `NumberSeq::newGetNum(ref).num()` ✅  
**B.** `NumberSeq.getNext()`  
**C.** `NumberSeq.generate()`  
**D.** `NumberSeq.next()`  

### Q2: Scopes:
**A.** Company, Shared, Legal Entity ✅  
**B.** Global, Local, User  
**C.** System, Company, User  
**D.** Public, Private, Protected  

### Q3: Preallocation:
**A.** Caches numbers in memory for performance ✅  
**B.** Reserves numbers in DB  
**C.** Generates sequentially  
**D.** Validates uniqueness  

---

## Chapter 31: Form Patterns

### Q1: ListPage pattern:
**A.** Master list with filters, actions, FactBoxes ✅  
**B.** Detail form with tabs  
**C.** Dialog with buttons  
**D.** Grid only  

### Q2: FactBox:
**A.** Related info pane (related records, counts) ✅  
**B.** Main grid area  
**C.** Filter pane  
**D.** Action pane  

### Q3: Dialog pattern:
**A.** Modal form for input/confirmation ✅  
**B.** List page with dialog  
**C.** FactBox with dialog  
**D.** Wizard form  

---

## Chapter 32: LEM Patterns

### Q1: Status change context:
**A.** Track state transitions with context (who, when, why) ✅  
**B.** Current status only  
**C.** Status history without context  
**D.** Next status prediction  

### Q2: Notifications:
**A.** Event-driven alerts via Notification Framework ✅  
**B.** Email only  
**C.** Infolog only  
**D.** Batch only  

### Q3: Multi-company:
**A.** `crossCompany` keyword, `DataAreaId` filtering ✅  
**B.** Separate databases  
**C. Shared tables only  
**D. Partition only  

---

## Chapter 33: Advanced Batch

### Q1: Cross-company batch:
**A.** `crossCompany` in query, batch runs per company ✅  
**B.** Single company only  
**C.** Manual per company  
**D. Shared batch  

### Q2: LEMLabPersonnel:
**A.** Framework for parallel batch processing ✅  
**B.** Single-threaded batch  
**C.** Batch monitoring  
**D. Batch scheduling  

### Q3: Retry patterns:
**A.** Exponential backoff, circuit breaker, dead letter queue ✅  
**B.** Fixed interval only  
**C. No retry  
**D. Manual retry  

---

## Chapter 34: Localization & Best Practices

### Q1: Label files:
**A.** `.xml` files per language (`@SYS12345`) ✅  
**B.** `.resx` files  
**C.** `.json` files  
**D.** `.txt` files  

### Q2: AppChecker:
**A.** Static analysis for best practices, naming, performance ✅  
**B.** Runtime checker  
**C.** Security scanner  
**D. Performance profiler  

### Q3: Configuration keys:
**A.** Enable/disable features (`#ISO`, custom keys) ✅  
**B.** Encryption keys  
**C.** API keys  
**D. License keys  

---

## Chapter 35: Service Patterns

### Q1: Service patterns:
**A.** SysOperation, Shared Executor, JSON/CLR Interop, OData exposure ✅  
**B.** REST, SOAP, GraphQL  
**C.** gRPC, WebSocket  
**D. MQTT, AMQP  

### Q2: Custom service = 
**A.** Contract + Service + Controller + MenuItemAction ✅  
**B.** Class + Method + MenuItem  
**C.** Table + Form + Report  
**D. Entity + Staging + DMF  

### Q3: JSON interop:
**A.** Newtonsoft.Json or System.Text.Json via .NET interop ✅  
**B.** X++ native JSON  
**C.** XML only  
**D. Not supported  

---

## Answer Key Summary

| Chapter | Correct Answers |
|---------|-----------------|
| 1 | B, B, B, B, B |
| 2 | A, C, B, A, C |
| 3 | B, B, C, B, A |
| 4 | B, C, B, B, B |
| 5 | B, B, A, B, C |
| 6 | B, B, B, C, B |
| 7 | B, B, B, B, A |
| 8 | B, B, B, B, A |
| 9 | B, A, B, B, B |
| 10 | B, A, A, B, A |
| 11 | B, B, A, B, A |
| 12 | C, A, B, A, A |
| 13 | B, B, B, A, B |
| 14 | B, B, A, B, A |
| 15 | A, B, A, A, B |
| 16 | A, A, B, A, B |
| 17 | A, A, B, A, A |
| 18 | B, A, B, B, B |
| 19 | B, B, B, B, A |
| 20 | B, A, A, A, A |
| 21 | B, B, A, B, B |
| 22 | B, A, A, A, A |
| 23 | B, B, B, A, B |
| 24 | A, A, A, A, B |
| 25 | A, A, A, A, B |
| 26 | A, A, A |
| 27 | A, A, A |
| 28 | A, A, A |
| 29 | A, A |
| 30 | A, A, A |
| 31 | A, A, A |
| 32 | A, A, A |
| 33 | A, A, A |
| 34 | A, A, A |
| 35 | A, A, A |

---

## How to Use

1. **After reading each chapter**, take the quiz
2. **Score < 80%?** Re-read the chapter, focus on wrong answers
3. **Track progress** in a spreadsheet: Chapter | Date | Score | Retake?
4. **Before certification**, do all quizzes in random order

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*