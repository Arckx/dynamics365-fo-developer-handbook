---
name: d365-guide-cross-reference
description: Maps main guide phases to Desktop guide chapters, topic lookup table, and recommended reading order
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-10T17:48:59.571Z
---

# D365 F&O Guides — Cross-Reference Map

> **How to navigate both guides.** The main guide (`d365_fao_technical_concepts_guide.md`) is organized into 12 phases. The Desktop guide (`d365-learning-guide.md`) is organized into 15 chapters. This map shows where each concept lives in both documents.

---

## Phase → Chapter Mapping

| Main Guide Phase | Title | Desktop Guide Chapters | Key Topics Covered |
|---|---|---|---|
| **Phase 1** | Foundations (Months 1–2) | **Ch 1** + **Ch 2** | Platform architecture, AOT, model layers, X++ data types, variables, control flow, CRUD, VS environment |
| **Phase 2** | Development Deep Dive (Months 2–4) | **Ch 2** + **Ch 3** + **Ch 4** + **Ch 5** + **Ch 6** | Table design, EDTs, classes, AOT navigation, views/queries, form controls, business logic classes |
| **Phase 3** | Architecture & Infrastructure (Months 3–5) | **Ch 1** | Server architecture, cloud, metadata subsystem, identity/authentication |
| **Phase 4** | Extensibility Patterns (Months 4–6) | **Ch 7** | Chain of Command, method wrapping, event handlers, table/form extensions (delegates deprecated by Microsoft — use CoC instead) |
| **Phase 5** | Business Logic & Backend (Months 5–7) | **Ch 6** + **Ch 11** | RunBase, SysOperation, batch processing, job framework |
| **Phase 6** | Integration (Months 6–8) | **Ch 9** | Data entities, integration patterns, REST APIs, OData |
| **Phase 7** | Reporting & Analytics (Months 7–9) | **Ch 10** | SSRS reports, legacy AX reports, analytical reporting, BI |
| **Phase 8** | Testing & Debugging (Months 7–10) | **Ch 12** | Unit testing (SysTest), ATL, RSAT, debugging |
| **Phase 9** | DevOps & CI/CD (Months 8–10) | **Ch 13** | Build automation, LCS, Azure DevOps, ALM |
| **Phase 10** | Security & Compliance (Months 9–11) | **Ch 8** | Security model, roles/duties/privileges, XDS, SoD |
| **Phase 11** | Performance & Problem Solving (Months 10–12) | **Ch 14** | SQL optimization, caching, indexing, bottleneck identification |
| **Phase 12** | Solution Crafting & Capstone (Months 11–12) | **Ch 15** | End-to-end production scenario, design patterns, solution crafting |
| **Phase 13** | Advanced Data Access (Months 5–6) | **Ch 16** | SysDa classes, RecordInsertList, RecordSortedList, doInsert/doUpdate/doDelete |
| **Phase 14** | Advanced Extensibility (Months 5–6) | **Ch 17** | Extension methods, local functions, var keyword, orig(), prmIsDefault(), CoC execution order |
| **Phase 15** | Production Hardening (Months 7–8) | **Ch 18** | SQL timeouts, CacheLookup, deadlock handling, indexing strategy |
| **Phase 16** | Platform Integration (Months 9–10) | **Ch 19** | Power Platform, OData, Logic Apps, Copilot, mobile, Process Automation |
| **Phase 17** | Module Deep Dives (Months 11–12) | **Ch 20** | Finance, SCM, HR, Retail/Commerce, Project Operations module tables, EDTs, patterns |
| **Phase 18** | Advanced DevOps (Ongoing) | **Ch 21** | Continuous delivery, validate package, database movement |
| **Phase 19** | Compliance & Governance (Ongoing) | **Ch 22** | GDPR, ISV considerations, financial tags, date effectivity, security hardening |
| **Phase 20** | Workflow Framework (Months 5-6) | **Ch 23** | WorkflowDocument, WorkflowType, Approvals, Tasks, event handlers, submit/resubmit |
| **Phase 21** | Number Sequences (Months 5-6) | **Ch 24** | NumberSeqApplicationModule, loadModule, NumberSeqFormHandler, scope types |
| **Phase 22** | Data Management Framework (Months 7-8) | **Ch 25** | Data entities, staging tables, mapEntityToDataSource, import/export |
| **Phase 23** | Advanced Forms (Months 9-10) | **Ch 26** | ListPage, SimpleListDetails-Grid, FactBox, Tree forms, dialog overrides |
| **Phase 24** | Notifications & IDisposable (Months 9-10) | **Ch 27** | Action Center, SystemNotificationsManager, status change context |
| **Phase 25** | Batch & Concurrency (Months 7-8) | **Ch 28** | Runtime tasks, deadlock retry, cross-company queries, batch constants |
| **Phase 26** | Labels & AppChecker (Ongoing) | **Ch 29** | Label files, AppChecker config, configuration keys |
| **Phase 27** | Services & JSON/CLR (Months 9-10) | **Ch 30** | Custom services, contracts, FormJsonSerializer, Newtonsoft.Json, service security |

---

## Topic → Location Lookup

Use this table to find where a specific topic is covered across both guides.

| Topic | Main Guide | Desktop Guide |
|---|---|---|
| Platform architecture & four pillars | Phase 1, §1.1 | Ch 1, §1.1 |
| AOT (Application Object Tree) | Phase 2, §2.4 | Ch 1, §1.2 |
| Model layers (SYS → ISV → VAR → CUS → USR) | Phase 1, §1.1 | Ch 1, §1.3 |
| X++ data types & variables | Phase 1, §1.3 | Ch 2, §2.1–2.2 |
| Control flow (if, switch, for, while) | Phase 1, §1.3.1 | Ch 2, §2.3 |
| CRUD operations (select, insert, update, delete) | Phase 1, §1.3.2 | Ch 2, §2.4 |
| `super()` and method overriding | Phase 1, §1.3.3 | Ch 2, §2.5 |
| Exception handling | Phase 1, §1.3.4 | Ch 2, §2.6 |
| Class structure & constructors | Phase 2, §2.3.1 | Ch 2, §2.7.1 |
| Inheritance & polymorphism | Phase 2, §2.3.2 | Ch 2, §2.7.2 |
| Abstract classes & interfaces | Phase 2, §2.3.3 | Ch 2, §2.7.3 |
| Table design & properties | Phase 2, §2.1 | Ch 3, §3.1 |
| Extended Data Types (EDTs) | Phase 2, §2.2 | Ch 3, §3.2 |
| Field groups & indexes | Phase 2, §2.1 | Ch 3, §3.3–3.4 |
| Form architecture & controls | Phase 2, §2.6 | Ch 4, §4.1 |
| Views & queries | Phase 2, §2.5 | Ch 5 |
| Business logic classes | Phase 2, §2.3 | Ch 6, §6.1 |
| Chain of Command (CoC) | Phase 4, §4.2 | Ch 7, §7.1 |
| Event Handlers | Phase 4, §4.4 | Ch 7, §7.2 |
| Delegates | *(deprecated)* | Do not create new delegates — use Chain of Command (CoC) instead |
| Table extensions | Phase 4, §4.6 | Ch 3, §3.4 |
| Form extensions | Phase 4, §4.7 | Ch 4 |
| Security model (roles, duties, privileges) | Phase 10, §10.1 | Ch 8, §8.1 |
| Extensible Data Security (XDS) | Phase 10, §10.4 | Ch 8, §8.4 |
| Data entities | Phase 6 (not in main guide detail) | Ch 9, §9.1 |
| REST APIs / OData | Phase 6 (not in main guide detail) | Ch 9, §9.3 |
| SSRS reports | Phase 7, §7.1 | Ch 10, §10.1 |
| Analytical reporting | Phase 7, §7.4 | Ch 10, §10.4 |
| Unit testing (SysTest) | Phase 8, §8.1 | Ch 12, §12.1 |
| Acceptance Test Library (ATL) | Phase 8, §8.2 | Ch 12, §12.2 |
| RSAT | Phase 8, §8.3 | Ch 12, §12.3 |
| Debugging | Phase 8, §8.4 | Ch 12, §12.4 |
| Azure DevOps build pipeline | Phase 9, §9.1 | Ch 13, §13.1 |
| LCS environments & release pipeline | Phase 9, §9.2 | Ch 13, §13.2 |
| SQL optimization | Phase 11, §11.1 | Ch 14, §14.1 |
| Caching strategies | Phase 11, §11.2 | Ch 14, §14.2 |
| Table indexing | Phase 11, §11.3 | Ch 14, §14.3 |
| SysDa classes | Phase 13, Ch 16 | Microsoft Learn: SysDa data access API |
| Extension methods | Phase 14, Ch 17 | Microsoft Learn: Extension methods in X++ |
| `orig()` method | Phase 14, Ch 17 | Microsoft Learn: Table buffer orig() |
| `prmIsDefault()` function | Phase 14, Ch 17 | Microsoft Learn: X++ parameter defaults |
| SQL statement timeouts | Phase 15, Ch 18 | Microsoft Learn: SQL statement timeout |
| `var` keyword (type inference) | Phase 14, Ch 17 | Microsoft Learn: X++ var keyword |
| Local functions | Phase 14, Ch 17 | Microsoft Learn: Local functions in X++ |
| Power Platform integration | Phase 16, Ch 19 | Microsoft Learn: Power Platform + D365 F&O |
| Copilot capabilities | Phase 16, Ch 19 | Microsoft Learn: Copilot in D365 F&O |
| Finance module deep dive | Phase 17, Ch 20 | Microsoft Learn: Dynamics 365 Finance |
| SCM module deep dive | Phase 17, Ch 20 | Microsoft Learn: Dynamics 365 Supply Chain Management |
| HR module deep dive | Phase 17, Ch 20 | Microsoft Learn: Dynamics 365 Human Resources |
| Continuous delivery / validate package | Phase 18, Ch 21 | Microsoft Learn: D365 F&O build automation |
| GDPR compliance | Phase 19, Ch 22 | Microsoft Learn: GDPR in D365 F&O |
| Date effectivity | Phase 19, Ch 22 | Microsoft Learn: Date effectivity in D365 F&O |
| Financial tags | Phase 19, Ch 22 | Microsoft Learn: Financial tags in D365 F&O |
| ISV development | Phase 19, Ch 22 | Microsoft Learn: ISV development for D365 F&O |
| Workflow Document / Type / Approval / Task | Phase 20, Ch 23 | Ch 23 |
| NumberSeqApplicationModule / loadModule | Phase 21, Ch 24 | Ch 24 |
| NumberSeqFormHandler | Phase 21, Ch 24 | Ch 24 |
| Data entities & staging tables | Phase 22, Ch 25 | Ch 25 |
| mapEntityToDataSource | Phase 22, Ch 25 | Ch 25 |
| ListPage pattern | Phase 23, Ch 26 | Ch 26 |
| FactBox forms | Phase 23, Ch 26 | Ch 26 |
| Tree forms | Phase 23, Ch 26 | Ch 26 |
| Action Center notifications | Phase 24, Ch 27 | Ch 27 |
| IDisposable status change context | Phase 24, Ch 27 | Ch 27 |
| Batch runtime tasks | Phase 25, Ch 28 | Ch 28 |
| Deadlock retry logic | Phase 25, Ch 28 | Ch 28 |
| Cross-company queries | Phase 25, Ch 28 | Ch 28 |
| Label files | Phase 26, Ch 29 | Ch 29 |
| AppChecker configuration | Phase 26, Ch 29 | Ch 29 |
| Custom services & contracts | Phase 27, Ch 30 | Ch 30 |
| FormJsonSerializer / Newtonsoft.Json | Phase 27, Ch 30 | Ch 30 |
| End-to-end capstone (Procurement-to-Pay) | Phase 12, §12.3 | Ch 15 |
| Capstone A — Finance: AP Tax Compliance | Phase 17 | Ch 15.5 |
| Capstone B — SCM: PO Automation | Phase 17 | Ch 15.5 |
| Capstone C — HR: Leave Management | Phase 17 | Ch 15.5 |
| Capstone D — Retail: Omnichannel Fulfillment | Phase 17 | Ch 15.5 |
| Capstone E — Project Operations: Project Billing Compliance | Phase 17 | Ch 15.5 |

| Aspect | Main Guide (`d365_fao_technical_concepts_guide.md`) | Desktop Guide (`d365-learning-guide.md`) |
|---|---|---|
| **Structure** | 12 phases organized by learning month | 30 chapters organized by topic area |
| **Depth** | Conceptual overviews with key code snippets | Deep dives with full code examples, tables, and activities |
| **Best for** | Quick reference, understanding what to learn next | In-depth study, hands-on practice, exam prep |
| **Length** | ~1,784 lines (~197 KB) | ~14,000+ lines (~700 KB+) |
| **Activities** | No — reference only | Yes — each chapter has an activity with hints and ideal solution |
| **Approach** | Linear progression (Phase 1 → 12) | Topic-focused (Ch 1 covers landscape, Ch 2 covers X++, etc.) |
| **Audience Level** | Beginner to intermediate | Intermediate to advanced (5-month+ intern focus) |

---

## Recommended Reading Order

For a 5-month-experienced intern starting the advanced journey:

1. **Ch 1** → Understand the platform landscape (review)
2. **Ch 2** → Learn X++ fundamentals (review — focus on areas you haven't mastered)
3. **Ch 16** → Advanced data access: SysDa, RecordInsertList
4. **Ch 17** → Advanced extensibility: Extension methods, local functions, var, orig(), prmIsDefault()
5. **Ch 18** → Production hardening: SQL timeouts, CacheLookup, deadlock handling, indexing
6. **Ch 3** → Master tables and EDTs (deepen)
7. **Ch 4** → Build forms (review)
8. **Ch 5** → Learn views and cross-table queries
9. **Ch 6** → Write business logic classes
10. **Ch 7** → Master extensibility patterns (CoC, Event Handlers)
11. **Ch 8** → Understand security
12. **Ch 9** → Build integrations with data entities
13. **Ch 10** → Create reports
14. **Ch 11** → Write batch jobs
15. **Ch 12** → Write tests
16. **Ch 13** → Set up DevOps pipelines
17. **Ch 14** → Optimize performance
18. **Ch 19** → Platform integration: Power Platform, Copilot, mobile, Process Automation
19. **Ch 20** → Module specialization: Finance, SCM, HR, Retail/Commerce, or Project Operations deep dive
20. **Ch 21** → Advanced DevOps: Continuous delivery, validate package, database movement
21. **Ch 22** → Compliance & Governance: GDPR, ISV, financial tags, date effectivity
22. **Ch 23** → Workflow Framework: WorkflowDocument, Approvals, Tasks, event handlers
23. **Ch 24** → Number Sequences: NumberSeqApplicationModule, loadModule, NumberSeqFormHandler
24. **Ch 25** → Data Management Framework: Data entities, staging tables, mapEntityToDataSource
25. **Ch 26** → Advanced Forms: ListPage, FactBox, Tree forms, dialog overrides
26. **Ch 27** → Notifications: Action Center, SystemNotificationsManager, IDisposable context
27. **Ch 28** → Batch & Concurrency: Runtime tasks, deadlock retry, cross-company queries
28. **Ch 29** → Labels & AppChecker: Label files, AppChecker config, configuration keys
29. **Ch 30** → Services & JSON/CLR: Custom services, contracts, FormJsonSerializer, Newtonsoft.Json
30. **Ch 15** → Capstone project
