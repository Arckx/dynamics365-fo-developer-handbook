---
name: d365-guide-cross-reference
description: Master cross-reference index mapping curriculum phases, chapters, exercises, and certification domains
metadata:
  type: reference
---

# D365 F&O Developer Handbook — Cross-Reference Index

> **Navigation hub** — Use this to jump between the Learning Journey, Desktop Guide chapters, Exercises, and Certification domains.

---

## 1. Learning Journey Phase → Desktop Guide Chapters

| Phase | Months | Theme | Desktop Guide Chapters | Key Deliverable |
|-------|--------|-------|----------------------|-----------------|
| **Phase 1: Foundations** | 1–3 | Platform, Architecture, X++ Basics | Ch 1–8 | Working X++ job, custom table design |
| **Phase 2: Data & UI** | 4–6 | Tables, Forms, Views, Classes | Ch 9–14 | Multi-form solution with business logic |
| **Phase 3: Extensibility** | 7–9 | CoC, Event Handlers, Security | Ch 15–21 | Extensions + batch job + data entity |
| **Phase 4: Quality & DevOps** | 10–12 | Testing, CI/CD, Performance | Ch 22–27 | Unit tests + build pipeline + perf audit |
| **Phase 5: Specialization** | 13+ | Module Deep Dives, Advanced Patterns | Ch 28–35 | Capstone project in chosen module |

---

## 2. Desktop Guide Chapter → Learning Phase & Exercises

| Ch | Title | Phase | Exercises | Est. Hours |
|---|-------|-------|-----------|------------|
| 1 | Platform Architecture & AOT | 1 | — | 3–4 |
| 2 | Models, Layers, Packages | 1 | — | 2–3 |
| 3 | VS Setup & Language Mindset | 1 | Ex 1–2 | 3–4 |
| 4 | LCS & Development Lifecycle | 1 | — | 2–3 |
| 5 | X++ Data Types & Variables | 2 | Ex 1 | 2–3 |
| 6 | Control Flow & CRUD | 2 | Ex 2–4 | 3–4 |
| 7 | Methods, Exceptions, Classes | 2 | Ex 5–8 | 4–5 |
| 8 | VS Development & Activity | 2 | Ex 8 | 3–4 |
| 9 | Table Design & EDTs | 3 | — | 4–5 |
| 10 | Form Architecture & CoC | 3 | Ex 10 | 4–5 |
| 11 | Views & Lookups | 3 | — | 2–3 |
| 12 | Class Fundamentals & RunBase | 3 | — | 3–4 |
| 13 | Event Handlers & Command Pattern | 3 | Ex 9 | 3–4 |
| 14 | Extensibility Deep Dive | 3 | Ex 10–11 | 4–5 |
| 15 | Security Model | 3 | — | 3–4 |
| 16 | Data Entities | 4 | Ex 12 | 4–5 |
| 17 | SSRS & Electronic Reporting | 4 | Ex 13 | 3–4 |
| 18 | Batch Processing | 4 | Ex 17 | 4–5 |
| 19 | SysTest Framework | 4 | — | 4–5 |
| 20 | LCS Deep Dive & CI/CD | 4 | — | 3–4 |
| 21 | Performance & SQL Tuning | 4 | — | 4–5 |
| 22 | Capstone Projects | 5 | Ex 15 | 8–12 |
| 23 | Advanced X++ Patterns | 5 | — | 3–4 |
| 24 | Production Debugging | 5 | — | 2–3 |
| 25 | Power Platform & Copilot | 5 | — | 3–4 |
| 26 | Module Specialization | 5 | — | 4–6 |
| 27 | Advanced DevOps | 5 | — | 3–4 |
| 28 | Compliance & ISV | 5 | — | 2–3 |
| 29 | Workflow Architecture | 5 | — | 3–4 |
| 30 | Number Sequences | 5 | Ex 16 | 2–3 |
| 31 | Form Patterns | 5 | — | 3–4 |
| 32 | VSI Patterns | 5 | — | 3–4 |
| 33 | Advanced Batch | 5 | — | 3–4 |
| 34 | Localization & Best Practices | 5 | — | 2–3 |
| 35 | Service Patterns | 5 | — | 3–4 |

---

## 3. Exercise → Chapter & Concept Mapping

| Ex # | Title | Chapter | Core Concept | Difficulty |
|------|-------|---------|--------------|------------|
| 1 | Variable Declaration & Type Casting | 3 | `conPeek`, `typeid()` | ⭐ Beginner |
| 2 | While Select with Filtering | 6 | `while select` + `where` | ⭐ Beginner |
| 3 | Bulk Update (`update_recordset`) | 6 | Set-based operations | ⭐ Beginner |
| 4 | Transaction with Error Handling | 6 | `ttsBegin`/`ttsCommit`/`ttsAbort` | ⭐⭐ Intermediate |
| 5 | Method Overriding with `super()` | 7 | Table extension `validateWrite` | ⭐⭐ Intermediate |
| 6 | Deadlock Retry Logic | 7 | `catch (Exception::Deadlock)` | ⭐⭐ Intermediate |
| 7 | Class with Constructor & Validation | 7 | Class design, private helpers | ⭐⭐ Intermediate |
| 8 | Inheritance & Polymorphism | 7 | `extends`, method override | ⭐⭐ Intermediate |
| 9 | Event Handler (`SubscribesTo`) | 13 | Table events (`inserted`) | ⭐⭐ Intermediate |
| 10 | Chain of Command (CoC) | 14 | `next` keyword, `ExtensionOf` | ⭐⭐⭐ Advanced |
| 11 | Multiple CoC Extensions | 14 | Execution order, layer priority | ⭐⭐⭐ Advanced |
| 12 | Data Entity Creation | 16 | `DataEntity`, OData, staging | ⭐⭐⭐ Advanced |
| 13 | SSRS Report Data Provider | 17 | `SrsReportDataProvider` | ⭐⭐⭐ Advanced |
| 14 | Error Handling Best Practices | 7, 6 | `super()`, `exists join`, transactions | ⭐⭐⭐ Advanced |
| 15 | Complete End-to-End Job | 22 | Integration of all prior concepts | ⭐⭐⭐⭐ Capstone |
| 16 | Number Sequence | 30 | `NumberSeq`, `NumberSeqReference` | ⭐⭐ Intermediate |
| 17 | SysOperation Service | 18 | `SysOperationServiceBase`, Controller | ⭐⭐⭐ Advanced |

---

## 4. Certification Exam → Chapters & Exercises

### MB-500: Dynamics 365: Finance and Operations Apps Developer
**Primary study resource** — this handbook covers all exam domains.

| Domain | Weight | Chapters | Exercises |
|--------|--------|----------|-----------|
| Architecture & AOT | 15–20% | 1–4 | — |
| X++ Development | 25–30% | 5–8, 12, 14, 23, 35 | 1–8, 10–11, 14–15 |
| Extensibility (CoC, Events) | 20–25% | 10, 13–14 | 5, 9–11 |
| Data Entities & Integration | 10–15% | 16, 18, 25, 35 | 12, 17 |
| Testing (SysTest) | 10–15% | 19 | — |
| DevOps & Lifecycle | 5–10% | 4, 20, 27 | — |
| Performance | 5–10% | 21, 24 | — |

### MB-310: Microsoft Dynamics 365 Finance Functional Consultant
| Domain | Chapters | Exercises |
|--------|----------|-----------|
| Core Setup (GL, AP, AR) | 9–11, 15 | 2, 4 |
| Business Processes (Workflows) | 13, 29 | 13 |
| Reporting (SSRS) | 17 | 13 |

### MB-330: Microsoft Dynamics 365 Supply Chain Management
| Domain | Chapters | Exercises |
|--------|----------|-----------|
| Data Integrity (Tables, Relations) | 9, 11 | 2, 5 |
| Integration (Data Entities, Power Platform) | 16, 25 | 12, 17 |
| Security & Compliance | 15, 28 | — |

---

## 5. File → Purpose Quick Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `README.md` | Overview, curriculum table, quick start | First visit, orientation |
| `d365-learning-guide.md` | 35-chapter desktop guide with code | Deep study, daily reference |
| `d365-fao-learning-journey.md` | 12-month structured plan | Planning, progress tracking |
| `d365-xpp-quick-reference.md` | Syntax cheat sheet | While coding |
| `d365-xpp-exercises.md` | 17 hands-on exercises | Practice, skill verification |
| `d365-glossary.md` | 100+ term definitions | Terminology lookup |
| `d365-handbook-appendices.md` | EDT table, X++→SQL, debugging, URLs | Quick lookups |
| `d365-anti-patterns.md` | What NOT to do with fixes | Code review, avoiding mistakes |
| `d365-certification-mapping.md` | Chapter → exam domain mapping | Certification prep |
| `data-entities-chapter.md` | Data Entity deep dive | Integration work |
| `systest-framework-chapter.md` | SysTest complete guide | Writing unit tests |
| `d365-performance-sql-tuning.md` | SQL tuning & query plans | Performance optimization |
| `d365-batch-processing-runbase-vs-sysoperation.md` | Batch framework comparison | Designing batch jobs |
| `vsi_gap_analysis.md` | VSI codebase vs guide gaps | Advanced architectural review |
| `d365-fao-interest.md` | User context & goals | — |
| `language-mindset-development.md` | Chapter 1.5 development notes | — |

---

## 6. Key Concept → Primary Chapter(s)

| Concept | Primary Chapter(s) | Reference Files |
|---------|-------------------|-----------------|
| **AOT & Metadata** | Ch 1, 2 | Appendix: Microsoft Learn URLs |
| **Models/Layers/Packages** | Ch 2 | — |
| **X++ Syntax** | Ch 5–7 | Quick Reference, Exercises 1–8 |
| **Table Design & EDTs** | Ch 9 | Appendix: EDT Table |
| **Form Architecture** | Ch 10 | — |
| **Chain of Command** | Ch 10, 14 | Exercises 10–11 |
| **Event Handlers** | Ch 13 | Exercise 9 |
| **Data Entities** | Ch 16 | `data-entities-chapter.md`, Exercise 12 |
| **SSRS Reports** | Ch 17 | Exercise 13 |
| **Batch Processing** | Ch 18, 33 | `batch-processing...md`, Exercise 17 |
| **SysTest** | Ch 19 | `systest-framework-chapter.md` |
| **LCS & CI/CD** | Ch 4, 20, 27 | — |
| **Performance Tuning** | Ch 21, 24 | `performance-sql-tuning.md` |
| **Security (XDS, Roles)** | Ch 15, 28 | Glossary: Security Hierarchy |
| **Workflows** | Ch 29 | — |
| **Number Sequences** | Ch 30 | Exercise 16 |
| **Power Platform** | Ch 25 | — |
| **Service Patterns** | Ch 35 | Exercise 17 |

---

## 7. Microsoft Learn URL Quick Links (Verified 2026-11-22)

| Topic | URL |
|-------|-----|
| **X++ Language Reference** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language |
| **Tables & Fields** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/tables/tables |
| **Extended Data Types** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/edts/extended-data-types |
| **Chain of Command** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/chain-of-command |
| **Event Handlers** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/event-handlers |
| **Data Entities** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro |
| **SSRS Reporting** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-reporting/ |
| **Security Model** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/security-operations/ |
| **LCS & DevOps** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-devenv/lifecycle-services-lcs |
| **SysTest Framework** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework |
| **Batch Processing** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-processing-overview |
| **Performance & Trace Parser** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/performance-trace-parser |
| **Number Sequences** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/number-sequence-framework |
| **Workflow System** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/workflow/workflow-system-architecture |

---

*Last Updated: 2026-11-22 | Handbook Version: 35 Chapters, 17 Exercises*