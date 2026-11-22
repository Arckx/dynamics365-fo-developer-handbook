---
name: d365-flashcards
description: Anki/Quizlet flashcard export for D365 F&O glossary terms and key concepts
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Flashcards

> **Import into Anki** (File → Import → CSV) or **Quizlet** (Create → Import from file)
> Format: `Front,Back,Tags`

---

## Core Concepts (Chapter 1-3)

| Front | Back | Tags |
|-------|------|------|
| What does ERP stand for? | Enterprise Resource Planning | chapter1,erp |
| What problem does ERP solve? | Data silos — integrates all departments into one system with a single database | chapter1,erp |
| What is D365 F&O? | Microsoft's cloud ERP (SaaS) for finance, supply chain, HR, projects | chapter1,d365 |
| What language does D365 F&O use? | X++ (runs on .NET CLR) | chapter1,xpp |
| What is the AOT? | Application Object Tree — metadata repository for all objects (tables, forms, classes) | chapter1,aot |
| What is a Model? | Container for your customizations (like a VS project) | chapter2,model |
| What is a Package? | Compiled model (.axmodel file) ready for deployment | chapter2,package |
| What are the layers in order? | SYS → ISV → VAR → CUS → USR (higher wins) | chapter2,layers |
| What is CoC? | Chain of Command — extension pattern using `next` keyword | chapter3,coc |
| What is a Data Entity? | Business document view for import/export/OData | chapter3,entity |

---

## X++ Syntax (Chapter 5-7)

| Front | Back | Tags |
|-------|------|------|
| X++ primitive types | int, int64, real, str, date, utcdatetime, enum, guid, boolean, anytype | chapter5,types |
| What is `real` used for? | Decimal precision (safe for money) — never use float/double for currency | chapter5,types |
| Variable scope in X++ | Class fields, static fields, method locals, block scope (inside {}) | chapter5,scope |
| `while select` vs `select` | `while select` iterates multiple rows; `select` gets single row (or firstOnly) | chapter6,select |
| How to do bulk insert? | `insert_recordset` — single SQL statement | chapter6,bulk |
| How to do bulk update? | `update_recordset` — single SQL statement | chapter6,bulk |
| How to do bulk delete? | `delete_from` — single SQL statement | chapter6,bulk |
| Transaction pattern | `ttsBegin; try { ... ttsCommit; } catch { ttsAbort; throw; }` | chapter6,transaction |
| `super()` vs `next` | `super()` in base override; `next` in CoC extension | chapter7,coc |
| Exception handling | `try { } catch (Exception::Deadlock) { } catch (Exception::Error) { }` | chapter7,exception |
| `checkFailed()` vs `error()` | `checkFailed()` in validation (returns false); `error()` throws exception | chapter7,validation |

---

## Tables & EDTs (Chapter 9)

| Front | Back | Tags |
|-------|------|------|
| EDT Golden Rule | Never use base types directly in tables/forms — always use an EDT | chapter9,edt |
| Table types | Regular, TempDB (persists, indexes), InMemory (fast, <1000 rows) | chapter9,tabletype |
| Field groups | Named field collections for auto-form generation | chapter9,fieldgroup |
| Relations | Links between fields on different tables (FK) | chapter9,relation |
| Indexes | Primary, Alternate (unique), Non-unique, Hash | chapter9,index |
| `validateWrite()` | Called before insert/update — use `checkFailed()` for errors | chapter9,validation |
| `CacheLookup` values | None, NotInTTS, Found, FoundAndEmpty, EntireTable | chapter9,cache |

---

## Forms & CoC (Chapter 10)

| Front | Back | Tags |
|-------|------|------|
| Form extension pattern | `[ExtensionOf(formStr(Name))] final class Name_Ext` | chapter10,formext |
| CoC on form methods | `public void init() { next init(); // custom code }` | chapter10,coc |
| Data source link types | Inner, Outer, Exists, NotExists, Delayed | chapter10,datasource |
| MultiSelectionHelper | For grid multi-select actions | chapter10,multiselect |
| Form patterns | ListPage, Grid, FactBox, Tree, Dialog, Details Master | chapter10,patterns |

---

## Classes & Patterns (Chapter 12-14)

| Front | Back | Tags |
|-------|------|------|
| RunBase vs SysOperation | RunBase = legacy; SysOperation = modern (3 classes: Contract, Service, Controller) | chapter12,runbase |
| SysOperation classes | 1) DataContract 2) Service extends SysOperationServiceBase 3) Controller extends SysOperationServiceController | chapter12,sysop |
| Event handler attribute | `[SubscribesTo(classStr(Class), methodStr(Method), true/false)]` | chapter13,events |
| Pre vs Post event | Pre = before (can cancel); Post = after (read result) | chapter13,events |
| CoC vs Event Handler | CoC = modify flow (use `next`); Event Handler = react (no flow control) | chapter14,extensibility |
| Extension naming | `TableName_Ext`, `FormName_Ext`, `ClassName_Ext` | chapter14,naming |

---

## Security (Chapter 15)

| Front | Back | Tags |
|-------|------|------|
| Security hierarchy | Role → Duties → Privileges → Permissions (Table/MenuItem access) | chapter15,security |
| XDS (Extensible Data Security) | Record-level filtering via policies assigned to roles | chapter15,xds |
| XDS policy types | Constrained, Contextual, Role-based, Hierarchical, Time-based | chapter15,xds |
| Privilege access levels | Read, Write, Create, Delete, Correct | chapter15,access |

---

## Data Entities (Chapter 16)

| Front | Back | Tags |
|-------|------|------|
| Data Entity types | Primary (main), Composite (header+lines), Derived (from view) | chapter16,entity |
| DMF (Data Management Framework) | Import/export, recurring jobs, staging tables | chapter16,dmf |
| OData endpoint | `/data/EntityName` — RESTful access to entities | chapter16,odata |
| Composite entity | Header entity + Line entity + Staging tables for both | chapter16,composite |

---

## SSRS & Reporting (Chapter 17)

| Front | Back | Tags |
|-------|------|------|
| SSRS report classes | SrsReportDataProvider (RDP) — business logic; RDL — layout | chapter17,ssrs |
| Electronic Reporting (ER) | Configurable, no-code reporting for regulatory/outbound | chapter17,er |
| Report lifecycle | Data Provider → Query → Dataset → RDL Render → Output | chapter17,ssrs |

---

## Batch Processing (Chapter 18)

| Front | Back | Tags |
|-------|------|------|
| Batch frameworks | RunBaseBatch (legacy) vs SysOperation (modern) | chapter18,batch |
| Batch execution modes | Synchronous, Asynchronous, Scheduled | chapter18,batch |
| Batch retry | Automatic retry on transient errors (configurable) | chapter18,batch |
| Batch cancellation | User can cancel via Batch Job form | chapter18,batch |

---

## SysTest (Chapter 19)

| Front | Back | Tags |
|-------|------|------|
| SysTest attributes | `[SysTestCase]`, `[SysTestMethod]`, `[SysTestSetup]`, `[SysTestCleanup]` | chapter19,systest |
| Assert methods | `assertEquals()`, `assertTrue()`, `assertFalse()`, `assertNull()`, `assertNotNull()` | chapter19,systest |
| Test isolation | Each test runs in transaction → auto-rollback | chapter19,systest |
| Property-based testing | Test invariants across thousands of generated inputs | chapter19,property |

---

## Performance (Chapter 21)

| Front | Back | Tags |
|-------|------|------|
| Query plan operators | Seek (good), Scan (bad), Key Lookup (add covering index), Hash Match (large joins) | chapter21,plan |
| CacheLookup guidelines | EntireTable (setup), Found (master), NotInTTS (transactional), None (high churn) | chapter21,cache |
| Common anti-patterns | Select in loop, update in loop, select *, unbounded crossCompany | chapter21,antipattern |
| Deadlock handling | Catch `Exception::Deadlock`, retry max 3 times with backoff | chapter21,deadlock |

---

## Advanced X++ (Chapter 23)

| Front | Back | Tags |
|-------|------|------|
| `SysDa` | Modern data access API (fluent, type-safe) | chapter23,sysda |
| `RecordInsertList` | Fastest bulk insert (batches to SQL) | chapter23,bulk |
| `var` keyword | Type inference (compile-time, not dynamic) | chapter23,var |
| `orig()` | Get original values before update in CoC/override | chapter23,orig |
| CoC execution order | Base → Ext1 (ISV) → Ext2 (VAR) → Ext3 (CUS) | chapter23,coc |

---

## Debugging (Chapter 24)

| Front | Back | Tags |
|-------|------|------|
| Common production issues | Timeouts, memory leaks, slow forms, deadlocks | chapter24,debug |
| Trace Parser | Analyze X++ execution traces (CPU, SQL, calls) | chapter24,trace |
| SQL Query Store | Track query performance over time | chapter24,querystore |

---

## Power Platform (Chapter 25)

| Front | Back | Tags |
|-------|------|------|
| Integration options | OData, REST, Logic Apps, Power Automate, Dataverse, Dual-write | chapter25,integration |
| Dual-write | Near real-time sync between F&O and Dataverse | chapter25,dualwrite |
| Power Automate | Flow designer for business processes | chapter25,powerautomate |

---

## Module Deep Dives (Chapter 26)

| Front | Back | Tags |
|-------|------|------|
| Finance key tables | LedgerJournalTable, LedgerJournalTrans, CustTrans, VendTrans, AssetTable | chapter26,finance |
| SCM key tables | InventTable, InventSum, PurchTable, SalesTable, ProdTable, WMSLocation | chapter26,scm |
| HR key tables | HcmWorker, HcmEmployment, HcmPosition, HcmCompensation | chapter26,hr |

---

## DevOps (Chapter 27)

| Front | Back | Tags |
|-------|------|------|
| Build pipeline | Compile → BP check → Unit test → Package (.axmodel) | chapter27,devops |
| Release pipeline | Tier-1 → UAT → Prod via LCS API | chapter27,devops |
| DB movement | Backup/Restore, Refresh, Sync | chapter27,dbmovement |

---

## Compliance (Chapter 28)

| Front | Back | Tags |
|-------|------|------|
| GDPR rights | Access, Rectification, Erasure, Restriction, Portability, Object | chapter28,gdpr |
| Financial tags | Dimensions for reporting (no GL impact) | chapter28,financetags |
| Date effectivity | ValidFrom/ValidTo on records (historical tracking) | chapter28,dateeffect |

---

## Workflow (Chapter 29)

| Front | Back | Tags |
|-------|------|------|
| Workflow types | Document (business doc), Event (system event) | chapter29,workflow |
| Key components | Workflow, Elements, Approvals, Tasks, Automated Tasks | chapter29,workflow |
| Workflow runtime | Batch job processes queue, calls handlers | chapter29,workflow |

---

## Number Sequences (Chapter 30)

| Front | Back | Tags |
|-------|------|------|
| NumberSeq API | `NumberSeq::newGetNum(ref).num()` | chapter30,numseq |
| Scopes | Company, Shared, Legal Entity | chapter30,numseq |
| Preallocation | Caches numbers in memory for performance | chapter30,numseq |

---

## Form Patterns (Chapter 31)

| Front | Back | Tags |
|-------|------|------|
| ListPage | Master list with filters, actions, FactBoxes | chapter31,patterns |
| FactBox | Related info pane (related records, counts) | chapter31,patterns |
| Dialog | Modal form for input/confirmation | chapter31,patterns |

---

## VSI Patterns (Chapter 32)

| Front | Back | Tags |
|-------|------|------|
| Status change context | Track state transitions with context (who, when, why) | chapter32,vsi |
| Notifications | Event-driven alerts via Notification Framework | chapter32,vsi |
| Multi-company | crossCompany keyword, DataAreaId filtering | chapter32,vsi |

---

## Advanced Batch (Chapter 33)

| Front | Back | Tags |
|-------|------|------|
| Cross-company batch | `crossCompany` in query, batch runs per company | chapter33,batch |
| VSIWorker | Framework for parallel batch processing | chapter33,batch |
| Retry patterns | Exponential backoff, circuit breaker, dead letter queue | chapter33,batch |

---

## Localization (Chapter 34)

| Front | Back | Tags |
|-------|------|------|
| Label files | `.xml` files per language (`@SYS12345`) | chapter34,labels |
| AppChecker | Static analysis for best practices, naming, performance | chapter34,appchecker |
| Configuration keys | Enable/disable features (`#ISO`, custom keys) | chapter34,configkeys |

---

## Services (Chapter 35)

| Front | Back | Tags |
|-------|------|------|
| Service patterns | SysOperation, Shared Executor, JSON/CLR Interop, OData exposure | chapter35,services |
| Custom service | Contract + Service + Controller + MenuItemAction | chapter35,customservice |
| JSON interop | Newtonsoft.Json or System.Text.Json via .NET interop | chapter35,json |

---

## CSV Export for Anki/Quizlet

```csv
Front,Back,Tags
What does ERP stand for?,Enterprise Resource Planning,chapter1 erp
What problem does ERP solve?,Data silos — integrates all departments into one system with a single database,chapter1 erp
What is D365 F&O?,Microsoft's cloud ERP (SaaS) for finance supply chain HR projects,chapter1 d365
What language does D365 F&O use?,X++ (runs on .NET CLR),chapter1 xpp
What is the AOT?,Application Object Tree — metadata repository for all objects (tables forms classes),chapter1 aot
What is a Model?,Container for your customizations (like a VS project),chapter2 model
What is a Package?,Compiled model (.axmodel file) ready for deployment,chapter2 package
What are the layers in order?,SYS → ISV → VAR → CUS → USR (higher wins),chapter2 layers
What is CoC?,Chain of Command — extension pattern using `next` keyword,chapter3 coc
What is a Data Entity?,Business document view for import/export/OData,chapter3 entity
X++ primitive types,int int64 real str date utcdatetime enum guid boolean anytype,chapter5 types
What is `real` used for?,Decimal precision (safe for money) — never use float/double for currency,chapter5 types
Variable scope in X++,Class fields static fields method locals block scope (inside {}),chapter5 scope
`while select` vs `select`,`while select` iterates multiple rows; `select` gets single row (or firstOnly),chapter6 select
How to do bulk insert?,insert_recordset — single SQL statement,chapter6 bulk
How to do bulk update?,update_recordset — single SQL statement,chapter6 bulk
How to do bulk delete?,delete_from — single SQL statement,chapter6 bulk
Transaction pattern,ttsBegin; try { ... ttsCommit; } catch { ttsAbort; throw; },chapter6 transaction
`super()` vs `next`,`super()` in base override; `next` in CoC extension,chapter7 coc
Exception handling,try { } catch (Exception::Deadlock) { } catch (Exception::Error) { },chapter7 exception
`checkFailed()` vs `error()`,`checkFailed()` in validation (returns false); `error()` throws exception,chapter7 validation
EDT Golden Rule,Never use base types directly in tables/forms — always use an EDT,chapter9 edt
Table types,Regular TempDB (persists indexes) InMemory (fast <1000 rows),chapter9 tabletype
Field groups,Named field collections for auto-form generation,chapter9 fieldgroup
Relations,Links between fields on different tables (FK),chapter9 relation
Indexes,Primary Alternate (unique) Non-unique Hash,chapter9 index
`validateWrite()`,Called before insert/update — use `checkFailed()` for errors,chapter9 validation
`CacheLookup` values,None NotInTTS Found FoundAndEmpty EntireTable,chapter9 cache
Form extension pattern,[ExtensionOf(formStr(Name))] final class Name_Ext,chapter10 formext
CoC on form methods,public void init() { next init(); // custom code },chapter10 coc
Data source link types,Inner Outer Exists NotExists Delayed,chapter10 datasource
MultiSelectionHelper,For grid multi-select actions,chapter10 multiselect
Form patterns,ListPage Grid FactBox Tree Dialog Details Master,chapter10 patterns
RunBase vs SysOperation,RunBase = legacy; SysOperation = modern (3 classes: Contract Service Controller),chapter12 runbase
SysOperation classes,1) DataContract 2) Service extends SysOperationServiceBase 3) Controller extends SysOperationServiceController,chapter12 sysop
Event handler attribute,[SubscribesTo(classStr(Class) methodStr(Method) true/false)],chapter13 events
Pre vs Post event,Pre = before (can cancel); Post = after (read result),chapter13 events
CoC vs Event Handler,CoC = modify flow (use `next`); Event Handler = react (no flow control),chapter14 extensibility
Extension naming,TableName_Ext FormName_Ext ClassName_Ext,chapter14 naming
Security hierarchy,Role → Duties → Privileges → Permissions (Table/MenuItem access),chapter15 security
XDS (Extensible Data Security),Record-level filtering via policies assigned to roles,chapter15 xds
XDS policy types,Constrained Contextual Role-based Hierarchical Time-based,chapter15 xds
Privilege access levels,Read Write Create Delete Correct,chapter15 access
Data Entity types,Primary (main) Composite (header+lines) Derived (from view),chapter16 entity
DMF (Data Management Framework),Import/export recurring jobs staging tables,chapter16 dmf
OData endpoint,`/data/EntityName` — RESTful access to entities,chapter16 odata
Composite entity,Header entity + Line entity + Staging tables for both,chapter16 composite
SSRS report classes,SrsReportDataProvider (RDP) — business logic; RDL — layout,chapter17 ssrs
Electronic Reporting (ER),Configurable no-code reporting for regulatory/outbound,chapter17 er
Report lifecycle,Data Provider → Query → Dataset → RDL Render → Output,chapter17 ssrs
Batch frameworks,RunBaseBatch (legacy) vs SysOperation (modern),chapter18 batch
Batch execution modes,Synchronous Asynchronous Scheduled,chapter18 batch
Batch retry,Automatic retry on transient errors (configurable),chapter18 batch
Batch cancellation,User can cancel via Batch Job form,chapter18 batch
SysTest attributes,[SysTestCase] [SysTestMethod] [SysTestSetup] [SysTestCleanup],chapter19 systest
Assert methods,assertEquals() assertTrue() assertFalse() assertNull() assertNotNull(),chapter19 systest
Test isolation,Each test runs in transaction → auto-rollback,chapter19 systest
Property-based testing,Test invariants across thousands of generated inputs,chapter19 property
Query plan operators,Seek (good) Scan (bad) Key Lookup (add covering index) Hash Match (large joins),chapter21 plan
CacheLookup guidelines,EntireTable (setup) Found (master) NotInTTS (transactional) None (high churn),chapter21 cache
Common anti-patterns,Select in loop update in loop select * unbounded crossCompany,chapter21 antipattern
Deadlock handling,Catch `Exception::Deadlock` retry max 3 times with backoff,chapter21 deadlock
`SysDa`,Modern data access API (fluent type-safe),chapter23 sysda
`RecordInsertList`,Fastest bulk insert (batches to SQL),chapter23 bulk
`var` keyword,Type inference (compile-time not dynamic),chapter23 var
`orig()`,Get original values before update in CoC/override,chapter23 orig
CoC execution order,Base → Ext1 (ISV) → Ext2 (VAR) → Ext3 (CUS),chapter23 coc
Common production issues,Timeouts memory leaks slow forms deadlocks,chapter24 debug
Trace Parser,Analyze X++ execution traces (CPU SQL calls),chapter24 trace
SQL Query Store,Track query performance over time,chapter24 querystore
Integration options,OData REST Logic Apps Power Automate Dataverse Dual-write,chapter25 integration
Dual-write,Near real-time sync between F&O and Dataverse,chapter25 dualwrite
Power Automate,Flow designer for business processes,chapter25 powerautomate
Finance key tables,LedgerJournalTable LedgerJournalTrans CustTrans VendTrans AssetTable,chapter26 finance
SCM key tables,InventTable InventSum PurchTable SalesTable ProdTable WMSLocation,chapter26 scm
HR key tables,HcmWorker HcmEmployment HcmPosition HcmCompensation,chapter26 hr
Build pipeline,Compile → BP check → Unit test → Package (.axmodel),chapter27 devops
Release pipeline,Tier-1 → UAT → Prod via LCS API,chapter27 devops
DB movement,Backup/Restore Refresh Sync,chapter27 dbmovement
GDPR rights,Access Rectification Erasure Restriction Portability Object,chapter28 gdpr
Financial tags,Dimensions for reporting (no GL impact),chapter28 financetags
Date effectivity,ValidFrom/ValidTo on records (historical tracking),chapter28 dateeffect
Workflow types,Document (business doc) Event (system event),chapter29 workflow
Key components,Workflow Elements Approvals Tasks Automated Tasks,chapter29 workflow
Workflow runtime,Batch job processes queue calls handlers,chapter29 workflow
NumberSeq API,NumberSeq::newGetNum(ref).num(),chapter30 numseq
Scopes,Company Shared Legal Entity,chapter30 numseq
Preallocation,Caches numbers in memory for performance,chapter30 numseq
ListPage,Master list with filters actions FactBoxes,chapter31 patterns
FactBox,Related info pane (related records counts),chapter31 patterns
Dialog,Modal form for input/confirmation,chapter31 patterns
Status change context,Track state transitions with context (who when why),chapter32 vsi
Notifications,Event-driven alerts via Notification Framework,chapter32 vsi
Multi-company,crossCompany keyword DataAreaId filtering,chapter32 vsi
Cross-company batch,crossCompany in query batch runs per company,chapter33 batch
VSIWorker,Framework for parallel batch processing,chapter33 batch
Retry patterns,Exponential backoff circuit breaker dead letter queue,chapter33 batch
Label files,`.xml` files per language (`@SYS12345`),chapter34 labels
AppChecker,Static analysis for best practices naming performance,chapter34 appchecker
Configuration keys,Enable/disable features (`#ISO` custom keys),chapter34 configkeys
Service patterns,SysOperation Shared Executor JSON/CLR Interop OData exposure,chapter35 services
Custom service,Contract + Service + Controller + MenuItemAction,chapter35 customs
JSON interop,Newtonsoft.Json or System.Text.Json via .NET interop,chapter35 json
```

---

## How to Import

### Anki
1. **File** → **Import**
2. **Format:** CSV
3. **Delimiter:** Comma
4. **Allow HTML:** ✅
5. **Deck:** "D365 F&O Handbook"
6. **Import**

### Quizlet
1. **Create** → **Import**
2. **Paste CSV** or upload file
3. **Set language:** English / English
4. **Create set**

---

## Study Tips

| Technique | How to Apply |
|-----------|--------------|
| **Spaced Repetition** | Anki default algorithm — review daily |
| **Active Recall** | Don't flip immediately — try to answer first |
| **Tag Filtering** | Study by chapter: `tag:chapter1` |
| **Reverse Cards** | Add "Back→Front" for terms you know well |
| **Cloze Deletion** | For code patterns: `{{c1::insert_recordset}}` |

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*