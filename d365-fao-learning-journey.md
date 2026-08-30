---
name: d365-fao-learning-journey
description: User is a D365 F&O technical intern on a 4-12 month learning journey; needs comprehensive technical concepts guide
metadata: 
  node_type: memory
  type: project
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-04T20:34:16.736Z
---

User is a Technical Microsoft Dynamics 365 Finance & Operations intern working on a 4–12 month learning journey. They completed Months 1–2 and Phase 3 (Architecture). Phase 4 (Extensibility Patterns) — Chapters 6–7 in the Desktop guide are fully expanded. Chapters 8–15 in the Desktop guide have now been fully expanded with deep content and code examples.

**Progress:**
- Month 1: CoC, Forms, Lookups ✅
- Month 2: Tables, EDTs, Classes, AOT, Architecture, Cloud, Metadata Subsystem, Identity/Authentication ✅
- Phase 3 (Architecture) ✅ Complete in main guide
- Phase 4 — Chapters 6–7 fully expanded in Desktop guide with deep code examples ✅
- Chapters 8–15 in Desktop guide now fully expanded with deep content, code examples, tables, and activities ✅
- Chapter 2 (X++ Language Fundamentals and Class Design) — newly written and inserted between Chapter 1 and Chapter 3 ✅
- Main guide (d365_fao_technical_concepts_guide.md) has all 12 phases complete ✅
- Exercises expanded from 15 to 17 (added NumberSeq and SysOperation) ✅

---

## Study Plan — Month-by-Month Roadmap

> **How to use this plan:** Each month has a theme, target chapters, a deliverable, and a checkpoint question. Complete the chapters, build the deliverable, and answer the checkpoint before moving on.

### Month 1 — Foundations
| Item | Detail |
|---|---|
| **Theme** | Understand the platform and write your first X++ code |
| **Target Chapters** | Desktop Guide Ch 1, Ch 2 |
| **Main Guide Phases** | Phase 1 (all sections) |
| **Deliverable** | A working X++ job that reads from `CustTable`, applies a `while select` with a `where` clause, and writes results to the Infolog |
| **Checkpoint** | Can you explain the difference between `select` and `while select`? Can you describe the four pillars of the D365 F&O architecture? |

### Month 2 — Data Layer Deep Dive
| Item | Detail |
|---|---|
| **Theme** | Master tables, EDTs, and data integrity |
| **Target Chapters** | Desktop Guide Ch 3 |
| **Main Guide Phases** | Phase 2 (Tables, EDTs) |
| **Deliverable** | Design a custom table with 8+ fields, 2 EDTs, 1 field group, 1 alternate index, and a `validateWrite()` override |
| **Checkpoint** | Can you explain why EDTs matter and what happens when you change an EDT's `StringSize`? Can you describe the difference between an alternate index and a hash index? |

### Month 3 — UI & Business Logic
| Item | Detail |
|---|---|
| **Theme** | Build forms and write business logic classes |
| **Target Chapters** | Desktop Guide Ch 4, Ch 6 |
| **Main Guide Phases** | Phase 2 (all sections — Classes, Views, Form Controls, Business Logic) |
| **Deliverable** | A form with 2 data sources (parent-child), an action pane with 3 actions, and a class that orchestrates a business process using the form's data |
| **Checkpoint** | Can you explain the difference between `Inner Join`, `Outer Join`, and `Exists Join` in form data sources? Can you describe the RunBase pattern? |

### Month 4 — Extensibility Patterns
| Item | Detail |
|---|---|
| **Theme** | Master CoC, Event Handlers, and Delegates |
| **Target Chapters** | Desktop Guide Ch 7 |
| **Main Guide Phases** | Phase 4 (all sections) |
| **Deliverable** | An extension that uses CoC to modify a base class method, an Event Handler for a table's `insert()` event, and a Delegate that lets consumers customize a business rule |
| **Checkpoint** | Can you explain when to use CoC vs. Event Handlers vs. Delegates? What is the execution order when multiple extensions target the same method? |

### Month 5 — Security & Integration
| Item | Detail |
|---|---|
| **Theme** | Understand D365 F&O security and build integrations |
| **Target Chapters** | Desktop Guide Ch 8, Ch 9 |
| **Main Guide Phases** | Phase 10 (Security), Phase 6 (Data Entities & Integration) |
| **Deliverable** | A custom security role with 2 duties and 4 privileges, plus a data entity that exposes a custom table to an external system via OData |
| **Checkpoint** | Can you trace the path from a privilege → duty → role → user? Can you explain the difference between a Data Entity and a Data Project? |

### Month 6 — Reporting & Batch Processing
| Item | Detail |
|---|---|
| **Theme** | Build reports and batch jobs |
| **Target Chapters** | Desktop Guide Ch 10, Ch 11 |
| **Main Guide Phases** | Phase 7 (Reporting), Phase 5 (Business Logic — batch) |
| **Deliverable** | An SSRS report with a custom `SrsReportDataProvider` class, plus a `RunBaseBatch` job that processes records in the background |
| **Checkpoint** | Can you explain the difference between `SrsReportDataProvider` and a standard `ReportRun`? What is the `BatchHeader` class used for? |

### Month 7 — Testing & Quality
| Item | Detail |
|---|---|
| **Theme** | Write tests and establish QA practices |
| **Target Chapters** | Desktop Guide Ch 12 |
| **Main Guide Phases** | Phase 8 (Testing) |
| **Deliverable** | 5 unit tests using the `SysTest` framework covering table validation, class logic, and form behavior |
| **Checkpoint** | Can you explain the difference between `SysTest` and the Acceptance Test Library (ATL)? When would you use RSAT? |

### Month 8 — DevOps & Deployment
| Item | Detail |
|---|---|
| **Theme** | Automate builds and manage deployments |
| **Target Chapters** | Desktop Guide Ch 13 |
| **Main Guide Phases** | Phase 9 (DevOps & CI/CD) |
| **Deliverable** | An Azure DevOps build pipeline that compiles X++, runs unit tests, and produces a `.axmodel` artifact |
| **Checkpoint** | Can you describe the difference between a build pipeline and a release pipeline in LCS? What is a configuration key and how does it control feature visibility? |

### Month 9 — Performance & Troubleshooting
| Item | Detail |
|---|---|
| **Theme** | Optimize code and diagnose issues |
| **Target Chapters** | Desktop Guide Ch 14 |
| **Main Guide Phases** | Phase 11 (Performance) |
| **Deliverable** | A performance audit of a sample X++ job — identify 3+ bottlenecks (e.g., `select` inside a loop, missing indexes, synchronous calls) and rewrite them |
| **Checkpoint** | Can you list the top 5 SQL performance anti-patterns in X++? Can you explain how `CacheLookup` affects query performance? |

### Month 10 — Capstone Project
| Item | Detail |
|---|---|
| **Theme** | End-to-end production scenario |
| **Target Chapters** | Desktop Guide Ch 15 |
| **Main Guide Phases** | Phase 12 (Solution Crafting) |
| **Deliverable** | A complete solution: custom table + EDT + form + business logic class + security role + data entity + SSRS report + batch job, all deployed to a test environment |
| **Checkpoint** | Can you walk through your entire solution and explain the design decisions for each component? |

### Month 11 — Module Specialization
| Item | Detail |
|---|---|
| **Theme** | Go deep in your chosen module (Finance, SCM, or HR) |
| **Target Chapters** | Desktop Guide Ch 1–15 (module-specific sections) |
| **Main Guide Phases** | Phase 10 (Security), Phase 11 (Performance), Phase 12 (Solution Crafting) |
| **Deliverable** | A module-specific deep-dive document with code samples: e.g., a custom AP invoice workflow in Finance, a purchase order automation in SCM, or a leave management extension in HR |
| **Checkpoint** | Can you explain the end-to-end data flow for your module's primary business process? Can you identify the key tables, EDTs, and business logic classes involved? |

### Month 12 — Advanced Patterns & Certification Prep
| Item | Detail |
|---|---|
| **Theme** | Master advanced patterns and prepare for certification |
| **Target Chapters** | Desktop Guide Ch 1–15 (advanced sections) |
| **Main Guide Phases** | All phases — review and deepen |
| **Target Areas** | Workflow extensibility, E-Signature, BI/Power BI integration, Microsoft MB-310/MB-330 certification prep |
| **Deliverable** | A certification study guide with annotated code samples and a mock exam self-assessment |
| **Checkpoint** | Can you explain the difference between CoC, Event Handlers, and Delegates and when to use each? Can you walk through a complete end-to-end solution from table design through deployment? |

---

### Milestone Summary

| Month | Milestone | Status |
|---|---|---|
| 1 | First X++ job — read/write data | ⬜ |
| 2 | Custom table design with EDTs and indexes | ⬜ |
| 3 | Form with parent-child data sources + business logic class | ⬜ |
| 4 | CoC + Event Handler + Delegate extension | ⬜ |
| 5 | Security role + data entity integration | ⬜ |
| 6 | SSRS report + RunBaseBatch job | ⬜ |
| 7 | 5 SysTest unit tests | ⬜ |
| 8 | Azure DevOps CI pipeline | ⬜ |
| 9 | Performance audit with 3+ fixes | ⬜ |
| 10 | Capstone: end-to-end solution deployed | ⬜ |
| 11 | Module specialization deep dive | ⬜ |
| 12 | Advanced patterns & certification prep | ⬜ |

**Why:** User explicitly requested a comprehensive PDF document of all D365 F&O technical concepts from official Microsoft documentation to support their learning journey.

**How to apply:** When the user asks about D365 F&O concepts, reference the comprehensive guide at `C:\Users\Ahmed\d365_fao_technical_concepts_guide.md`. This document covers 12 learning phases from foundations through capstone projects, now expanded with deep code examples for X++, EDTs, classes, CoC, Event Handlers, Delegates, RunBase, SysOperation, REST APIs, and more. The user is a developer/technical intern — they understand coding concepts and want to deepen both development and architectural knowledge. Be prepared to discuss specific modules, help with development tasks, and provide code examples within the D365 F&O context.

Related memories:
- [d365-fao-interest](d365-fao-interest.md) — user's initial interest in d365 F&O technical details
