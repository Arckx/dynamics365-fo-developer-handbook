# Dynamics 365 Finance & Operations (D365 F&O) Developer Handbook

> The definitive technical handbook, 35-chapter desktop guide, and 12-month learning journey designed for Microsoft D365 F&O developers, technical interns, and enterprise engineers.

---

## The Language Mindset

This handbook is built around a fundamental engineering shift. D365 F&O comes with its own language mindset that impacts how developers think about software:

* **Relational-First, Not Object-First:** The database is the primary focus; data access and movement drive the application architecture. D365 F&O is built around SQL tables with business entities represented as rows. Developers think in terms of relations between data sets, not just objects.
* **Metadata over Code:** Business logic and configurations are defined in the Application Object Tree (AOT) rather than hardcoded. The AOT contains all definitions (tables, classes, forms, enums) and stores them as metadata that the AOS loads and executes.
* **Extensibility as a Constraint:** Customizations must be non-invasive, relying on Chain of Command (CoC) and Event Handlers to protect the evergreen Microsoft core. Since Microsoft updates D365 F&O frequently, your code must not directly modify standard Microsoft tables or classes, or your customizations will be overwritten during future updates.

---

## 30-Minute Quick Start (New Developers)

If you're new to D365 F&O, start here:

1. **Environment Setup** — [Prerequisites](#prerequisites-and-environment-setup) → Get a Tier-1 VM or Dev VM with VS + Dynamics 365 Add-in
2. **First X++ Job** — [Exercise 1](d365-xpp-exercises.md#exercise-1---variable-declaration-and-type-casting) → `conPeek`, `typeid()`, `info()`
3. **First Query** — [Exercise 2](d365-xpp-exercises.md#exercise-2---while-select-with-filtering) → `while select` with `where`
4. **First Table Extension** — [Learning Guide Ch 9](d365-learning-guide.md#9-table-design--edts) → `[ExtensionOf(tableStr(VendTable))]`
5. **First Data Entity** — [Learning Guide Ch 16](d365-learning-guide.md#16-data-entities) → `IsPublic = Yes`, OData endpoint

> **Tip:** Keep [d365-xpp-quick-reference.md](d365-xpp-quick-reference.md) open while coding — it's your syntax cheat sheet.

---

## Repository Structure

| File | Description | Recommended Use |
|---|---|---|
| `d365-learning-guide.md` | 35-chapter technical desktop guide with full code examples, tables, and exercises. Covers X++, architecture, tables, forms, workflows, services, VSI patterns, Data Entities, SysTest, Performance, and more. | In-depth technical study and daily code reference. |
| `d365-fao-learning-journey.md` | 12-month structured study plan with quarterly milestones and deliverables. | Structuring internship programs and training paths. |
| `d365-guide-cross-reference.md` | Master index mapping curriculum phases to desktop guide chapters. | Navigating between study phases and reference chapters. |
| `d365-xpp-quick-reference.md` | X++ syntax cheat sheet covering CRUD operations, CoC, LINQ-style queries, and exception handling. | Quick syntax checks while writing code. |
| `d365-xpp-exercises.md` | 17 hands-on coding exercises aligned with each learning phase (beginner → advanced). | Practical application of core concepts. |
| `d365-glossary.md` | Glossary of 100+ core D365 terms (AOT, EDTs, CoC, XDS, etc.) with one-sentence definitions. | Terminology lookups. |
| `d365-handbook-appendices.md` | Reference appendices: EDT table, X++→SQL cheat sheet, Debugging cookbook, Microsoft Learn URLs. | Quick lookups and troubleshooting. |
| `d365-anti-patterns.md` | Anti-pattern library documenting "What NOT to do" with code examples and fixes. | Avoiding common mistakes and upgrade issues. |
| `d365-certification-mapping.md` | Mapping of 35 chapters to MB-310, MB-330, MB-500 exam domains. | Study planning and exam preparation. |
| `vsi_gap_analysis.md` | Analysis of real-world VSI codebase patterns and architectural enhancement roadmap. | Advanced architectural review. |
| `d365-batch-processing-runbase-vs-sysoperation.md` | Technical comparison of `RunBaseBatch` versus `SysOperationServiceController`. | Designing asynchronous background jobs. |
| `d365-fao-interest.md` | Interest tracking and learning objectives. | Personal progress tracking. |
| `d365-performance-sql-tuning.md` | Performance & SQL tuning deep dive chapter. | Query optimization reference. |
| `data-entities-chapter.md` | Data Entities chapter (OData, staging, DMF, Power Platform). | Integration reference. |
| `language-mindset-development.md` | Language Mindset development notes. | Philosophy and approach reference. |
| `d365_combined_guide.md` | Combined guide from previous iterations. | Legacy reference. |
| `systest-framework-chapter.md` | SysTest Framework chapter. | Testing reference. |
| `batchprocessingind365forunbasebatchvssysoperation.md` | Batch processing comparison (legacy format). | Legacy reference. |

---

## Curriculum Overview (35 Chapters)

The curriculum spans **35 chapters** organized into **four foundational quarters**:

### Quarter 1 (Months 1–3): Foundations & Data Layer
| Ch | Topic | Key Skills |
|---|---|---|
| 1 | Platform Architecture & AOT | AOS, AOT, model store, layers |
| 2 | Models, Layers, Packages | Model manifest, dependencies, SYS/ISV/VAR/CUS |
| 3 | VS Setup & Language Mindset | Relational-first, metadata, extensibility, primitives, EDTs |
| 4 | LCS & Development Lifecycle | Environments, build pipeline, release pipeline, hotfixes |
| 5 | X++ Data Types & Variables | Primitives, composites, `real` precision, block scope |
| 6 | Control Flow & CRUD | `while select`, `update_recordset`, `delete_from`, transactions |
| 7 | Methods, Exceptions, Classes | `super()`/`next`, `try/catch`, inheritance, abstract, interfaces |
| 8 | VS Development & Activity | Debugging, build/deploy, customer validation service |

### Quarter 2 (Months 4–6): Extensibility & Backend Architecture
| Ch | Topic | Key Skills |
|---|---|---|
| 9 | Table Design & EDTs | Field groups, relations, indexes, TempDB/InMemory, validation |
| 10 | Form Architecture & CoC | Data sources, controls, CoC patterns, form extensions |
| 11 | Views & Lookups | View definitions, `SysTableLookup`, multi-select lookups |
| 12 | Class Fundamentals & RunBase | `RunBase`/`RunBaseBatch`, dialog, `SysOperation` pattern |
| 13 | Event Handlers & Command Pattern | Pre/Post handlers, `SubscribesTo`, menu item → class chain |
| 14 | Extensibility Deep Dive | CoC vs override vs event handler, `ExtensionOf`, attributes |
| 15 | Security Model | Hierarchy, XDS, record-level, privilege assertions, audit |

### Quarter 3 (Months 7–9): Quality, DevOps & Advanced Performance
| Ch | Topic | Key Skills |
|---|---|---|
| 16 | Data Entities | OData, staging, composite entities, DMF, Power Platform |
| 17 | SSRS & Electronic Reporting | `SrsReportDataProvider`, RDL, ER, pre-processing |
| 18 | Batch Processing | `RunBaseBatch`, `SysOperation`, progress, retry, cancellation |
| 19 | SysTest Framework | `SysTestCase`, assertions, data fixtures, CI/CD integration |
| 20 | LCS Deep Dive & CI/CD | Model management, `AxModelStore`, pipeline design |
| 21 | Performance & SQL Tuning | Query plans, `CacheLookup`, deadlock resolution, indexing |

### Quarter 4 (Months 10–12): Enterprise Solutions & Specialization
| Ch | Topic | Key Skills |
|---|---|---|
| 22 | Capstone Projects | End-to-end architecture, manufacturing P2P compliance |
| 23 | Advanced X++ Patterns | `SysDa`, `RecordInsertList`, `var`, `orig()`, CoC order |
| 24 | Production Debugging | Timeouts, memory, slow forms, deadlocks |
| 25 | Power Platform & Copilot | Logic Apps, Power Automate, mobile, process automation |
| 26 | Module Specialization | Finance, SCM, HR deep dives, certification prep |
| 27 | Advanced DevOps | CD pipelines, DB movement, build automation |
| 28 | Compliance & ISV | GDPR, financial tags, date effectivity, hardening |
| 29 | Workflow Architecture | Document, events, submit/action managers, enabled forms |
| 30 | Number Sequences | Module registration, reference API, form handler, targets |
| 31 | Form Patterns | ListPage, Grid, FactBox, Tree, Dialog, MultiSelectionHelper |
| 32 | VSI Patterns | Status change context, notifications, multi-company |
| 33 | Advanced Batch | Cross-company, `VSIWorker`, constants, retry patterns |
| 34 | Localization & Best Practices | Labels, AppChecker, configuration keys |
| 35 | Service Patterns | `SysOperation`, shared executor, JSON/CLR interop, exposure |

---

## Core Learning Outcomes

Upon completing this handbook, developers will be able to:
* Write production-grade, maintainable X++ following Microsoft best practices.
* Implement non-invasive customizations using Chain of Command.
* Design secure tables, EDTs, forms, and custom data entities.
* Build asynchronous background batch jobs and custom SSRS reports.
* Configure automated Azure DevOps CI/CD pipelines and unit tests (`SysTest`).
* Troubleshoot and optimize complex SQL queries, memory caching, and deadlocks.
* Specialize in core D365 F&O enterprise modules and prepare for Microsoft certifications MB-310 and MB-330.
* Integrate with Power Platform (Logic Apps, Power Automate, Dataverse).
* Build and consume custom service endpoints (OData, REST, JSON).

---

## Prerequisites and Environment Setup

* **Development Environment:** Access to a D365 F&O Development VM or Tier-1 Cloud Hosted Environment with Visual Studio.
* **Prerequisites:** Basic object-oriented programming experience and relational database fundamentals (SQL).
* **Tooling:** Visual Studio with Dynamics 365 Add-in, Azure DevOps, Lifecycle Services (LCS).

---

**Target Audience:** Technical Interns, Junior-to-Senior X++ Developers, Enterprise Solution Architects.
