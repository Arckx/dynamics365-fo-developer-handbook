# Dynamics 365 Finance & Operations (D365 F&O) Developer Handbook

![Chapters](https://img.shields.io/badge/Chapters-35-blue)
![Exercises](https://img.shields.io/badge/Exercises-17-green)
![Last Updated](https://img.shields.io/badge/Updated-Nov%202026-orange)

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

## How to Read This Handbook

| Learning Style | Start Here | Path |
|---|---|---|
| **New to D365** | 30-Minute Quick Start → Ch 1–3 | Sequential |
| **X++ Refresher** | [d365-xpp-quick-reference.md](d365-xpp-quick-reference.md) → Exercises 1–4 | Reference-driven |
| **Certification Prep** | [d365-certification-mapping.md](d365-certification-mapping.md) → Target chapters | Goal-driven |
| **Architecture Review** | [vsi_gap_analysis.md](vsi_gap_analysis.md) → Chapters 23–35 | Deep-dive |

---

## Repository Structure

### Core Handbook Files

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

### Quick Reference Files

| File | Description | Recommended Use |
|---|---|---|
| `d365-cheatsheet.md` | One-page printable reference card with X++ types, CRUD patterns, layer hierarchy, naming conventions, and key URLs. | Print and keep at desk for instant lookup. |
| `d365-troubleshooting.md` | 50+ common errors with root causes and fixes (runtime, build, deployment, performance, debugging). | Quick diagnosis when things break. |
| `d365-code-review-checklist.md` | PR review checklist: naming, CoC usage, transactions, SQL patterns, security, tests. | Code review standard for all PRs. |
| `d365-cookbook.md` | Copy-paste patterns for tables, queries, forms, services, entities, testing. | Daily coding reference. |

### Foundational Guides (Chapter 0 — Start Here if New)

| File | Description | Recommended Use |
|---|---|---|
| `d365-foundations.md` | **Chapter 0** — ERP concepts, D365 F&O modules, business processes, Azure basics for absolute beginners. | **Read FIRST** before Chapter 1 if new to ERP/cloud. |
| `d365-oop-primer.md` | OOP concepts mapped to X++ — classes, inheritance, interfaces, polymorphism, SOLID. | Read alongside Chapter 3 & 7 if new to OOP. |
| `d365-sql-primer.md` | SQL basics mapped to X++ — SELECT, JOIN, INDEX, transactions, query plans. | Read alongside Chapter 5 & 6 if new to SQL. |
| `d365-environment-setup.md` | Step-by-step Tier-1 VM, VS + D365 extension, first project, Git setup. | **Do THIS** before any coding. |

### Advanced Guides

| File | Description | Recommended Use |
|---|---|---|
| `d365-migration-guide.md` | AX 2012 → D365 F&O migration: code upgrade patterns, metadata mapping, DMF data migration. | Migration projects and upgrades. |
| `d365-copilot-guide.md` | Copilot extensibility: plugins, actions, skills, prompt engineering, Custom APIs. | AI integration and Copilot Studio. |
| `d365-testing-patterns.md` | Property-based testing, test data factories, SysTest + TestFramework integration. | Test strategy and quality gates. |
| `d365-observability.md` | Application Insights, custom telemetry, performance counters, alerting rules. | Production monitoring and alerting. |
| `d365-security-patterns.md` | Role/privilege design, XDS policies, audit logging, compliance patterns. | Security architecture and review. |
| `d365-perf-benchmark.md` | Performance benchmarking scripts, SQL queries, load testing, CI/CD gates. | Performance validation and tuning. |
| `d365-security-audit.md` | Security audit checklist: SoD, XDS coverage, privilege creep, compliance. | Quarterly security audits. |

### Learning Tools & Visual Aids

| File | Description | Recommended Use |
|---|---|---|
| `d365-architecture-diagrams.md` | Mermaid.js diagrams for all key architectures (pillars, request flow, layers, CoC, security, batch, entities). | Visual learners; embed in docs. |
| `d365-flashcards.md` | Anki/Quizlet flashcard export for glossary + key concepts (CSV format). | Spaced repetition study. |
| `d365-study-guide-quizzes.md` | 5-10 MCQs per chapter with explanations (35 chapters × ~7 questions = 245 total). | Self-check after each chapter. |
| `d365-capstone-rubric.md` | Grading rubric for Chapter 22 projects (architecture, code, tests, security, docs). | Mentor evaluation standard. |
| `d365-pair-programming-prompts.md` | Driver/navigator exercises for CoC, SysOperation, batch, security, performance, debugging. | Collaborative learning sessions. |
| `d365-video-links.md` | Curated Microsoft Learn + YouTube links with timestamps per chapter. | Video supplement for each topic. |

### CI/CD Pipeline Templates

| File | Description | Recommended Use |
|---|---|---|
| `d365-pipeline-templates/azure-pipelines-build.yml` | Build pipeline: compile, BP checks, unit tests, model packaging. | Every PR and main branch build. |
| `d365-pipeline-templates/azure-pipelines-release.yml` | Release pipeline: Tier-1 → UAT → Prod via LCS API. | Multi-environment deployments. |
| `d365-pipeline-templates/azure-pipelines-db-sync.yml` | Database sync and data upgrade scripts pipeline. | Post-deployment schema sync. |

### Reference & Legacy Files

| File | Description | Recommended Use |
|---|---|---|
| `vsi_gap_analysis.md` | Analysis of real-world VSI codebase patterns and architectural enhancement roadmap. | Advanced architectural review. |
| `d365-fao-interest.md` | Interest tracking and learning objectives. | Personal progress tracking. |
| `language-mindset-development.md` | Language Mindset development notes. | Philosophy and approach reference. |
| `d365_combined_guide.md` | Combined guide from previous iterations. | Legacy reference. |

---

## Curriculum Overview (35 Chapters)

The curriculum spans **35 chapters** organized into **four foundational quarters**. Each chapter in the learning guide has detailed code examples, tables, and activities.

### Quarter 1 (Months 1–3): Foundations & Data Layer
| Ch | Topic | Key Skills | Learning Guide |
|---|---|---|---|
| 1 | Platform Architecture & AOT | AOS, AOT, model store, layers | [Ch 1](d365-learning-guide.md#chapter-1-platform-architecture--aot) |
| 2 | Models, Layers, Packages | Model manifest, dependencies, SYS/ISV/VAR/CUS | [Ch 2](d365-learning-guide.md#chapter-2-models-layers-packages) |
| 3 | VS Setup & Language Mindset | Relational-first, metadata, extensibility, primitives, EDTs | [Ch 3](d365-learning-guide.md#chapter-3-visual-studio-setup--language-mindset) |
| 4 | LCS & Development Lifecycle | Environments, build pipeline, release pipeline, hotfixes | [Ch 4](d365-learning-guide.md#chapter-4-lcs--dev-lifecycle) |
| 5 | X++ Data Types & Variables | Primitives, composites, `real` precision, block scope | [Ch 5](d365-learning-guide.md#chapter-5-x-data-types--variables) |
| 6 | Control Flow & CRUD | `while select`, `update_recordset`, `delete_from`, transactions | [Ch 6](d365-learning-guide.md#chapter-6-control-flow--crud) |
| 7 | Methods, Exceptions, Classes | `super()`/`next`, `try/catch`, inheritance, abstract, interfaces | [Ch 7](d365-learning-guide.md#chapter-7-methods-exceptions-classes) |
| 8 | VS Development & Activity | Debugging, build/deploy, customer validation service | [Ch 8](d365-learning-guide.md#chapter-8-vs-development--activity) |

### Quarter 2 (Months 4–6): Extensibility & Backend Architecture
| Ch | Topic | Key Skills | Learning Guide |
|---|---|---|---|
| 9 | Table Design & EDTs | Field groups, relations, indexes, TempDB/InMemory, validation | [Ch 9](d365-learning-guide.md#chapter-9-table-design--edts) |
| 10 | Form Architecture & CoC | Data sources, controls, CoC patterns, form extensions | [Ch 10](d365-learning-guide.md#chapter-10-form-architecture--coc) |
| 11 | Views & Lookups | View definitions, `SysTableLookup`, multi-select lookups | [Ch 11](d365-learning-guide.md#chapter-11-views--lookups) |
| 12 | Class Fundamentals & RunBase | `RunBase`/`RunBaseBatch`, dialog, `SysOperation` pattern | [Ch 12](d365-learning-guide.md#chapter-12-class-fundamentals--runbase) |
| 13 | Event Handlers & Command Pattern | Pre/Post handlers, `SubscribesTo`, menu item → class chain | [Ch 13](d365-learning-guide.md#chapter-13-event-handlers--command-pattern) |
| 14 | Extensibility Deep Dive | CoC vs override vs event handler, `ExtensionOf`, attributes | [Ch 14](d365-learning-guide.md#chapter-14-extensibility-deep-dive) |
| 15 | Security Model | Hierarchy, XDS, record-level, privilege assertions, audit | [Ch 15](d365-learning-guide.md#chapter-15-security-model) |

### Quarter 3 (Months 7–9): Quality, DevOps & Advanced Performance
| Ch | Topic | Key Skills | Learning Guide |
|---|---|---|---|
| 16 | **Data Entities** | OData, staging, composite entities, DMF, Power Platform | [Ch 16](d365-learning-guide.md#1-entity-types-dataentity-vs-composite-entity-vs-derived-view) |
| 17 | **SSRS & Electronic Reporting** | `SrsReportDataProvider`, RDL, ER, pre-processing | [Ch 17](d365-learning-guide.md#1-ssrs-report-architecture) |
| 18 | **Batch Processing** | `RunBaseBatch`, `SysOperation`, progress, retry, cancellation | [Ch 18](d365-learning-guide.md#1-batch-processing-fundamentals--the-restaurant-analogy) |
| 19 | **SysTest Framework** | `SysTestCase`, assertions, data fixtures, CI/CD integration | [Ch 19](d365-learning-guide.md#1-the-systest-framework--core-components) |
| 20 | LCS Deep Dive & CI/CD | Model management, `AxModelStore`, pipeline design | [Ch 20](d365-learning-guide.md#chapter-20-lcs-deep-dive--cicd) |
| 21 | **Performance & SQL Tuning** | Query plans, `CacheLookup`, deadlock resolution, indexing | [Ch 21](d365-learning-guide.md#211-sql-query-optimization) |

### Quarter 4 (Months 10–12): Enterprise Solutions & Specialization
| Ch | Topic | Key Skills | Learning Guide |
|---|---|---|---|
| 22 | Capstone Projects | End-to-end architecture, manufacturing P2P compliance | [Ch 22](d365-learning-guide.md#chapter-22-capstone-projects) |
| 23 | Advanced X++ Patterns | `SysDa`, `RecordInsertList`, `var`, `orig()`, CoC order | [Ch 23](d365-learning-guide.md#chapter-23-advanced-x-patterns) |
| 24 | Production Debugging | Timeouts, memory, slow forms, deadlocks | [Ch 24](d365-learning-guide.md#chapter-24-production-debugging) |
| 25 | Power Platform & Copilot | Logic Apps, Power Automate, mobile, process automation | [Ch 25](d365-learning-guide.md#251-power-platform-integration) |
| 26 | Module Specialization | Finance, SCM, HR deep dives, certification prep | [Ch 26](d365-learning-guide.md#261-finance-module-deep-dive) |
| 27 | Advanced DevOps | CD pipelines, DB movement, build automation | [Ch 27](d365-learning-guide.md#chapter-27-advanced-devops) |
| 28 | Compliance & ISV | GDPR, financial tags, date effectivity, hardening | [Ch 28](d365-learning-guide.md#chapter-28-compliance--isv) |
| 29 | Workflow Architecture | Document, events, submit/action managers, enabled forms | [Ch 29](d365-learning-guide.md#chapter-29-workflow-architecture) |
| 30 | Number Sequences | Module registration, reference API, form handler, targets | [Ch 30](d365-learning-guide.md#chapter-30-number-sequences) |
| 31 | Form Patterns | ListPage, Grid, FactBox, Tree, Dialog, MultiSelectionHelper | [Ch 31](d365-learning-guide.md#311-list-page-pattern-listpage) |
| 32 | VSI Patterns | Status change context, notifications, multi-company | [Ch 32](d365-learning-guide.md#chapter-32-vsi-patterns) |
| 33 | Advanced Batch | Cross-company, `VSIWorker`, constants, retry patterns | [Ch 33](d365-learning-guide.md#chapter-33-advanced-batch) |
| 34 | Localization & Best Practices | Labels, AppChecker, configuration keys | [Ch 34](d365-learning-guide.md#341-label-files) |
| 35 | Service Patterns | `SysOperation`, shared executor, JSON/CLR interop, exposure | [Ch 35](d365-learning-guide.md#351-service-pattern-overview) |

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
| 16 | **Data Entities** | OData, staging, composite entities, DMF, Power Platform |
| 17 | **SSRS & Electronic Reporting** | `SrsReportDataProvider`, RDL, ER, pre-processing |
| 18 | **Batch Processing** | `RunBaseBatch`, `SysOperation`, progress, retry, cancellation |
| 19 | **SysTest Framework** | `SysTestCase`, assertions, data fixtures, CI/CD integration |
| 20 | LCS Deep Dive & CI/CD | Model management, `AxModelStore`, pipeline design |
| 21 | **Performance & SQL Tuning** | Query plans, `CacheLookup`, deadlock resolution, indexing |

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