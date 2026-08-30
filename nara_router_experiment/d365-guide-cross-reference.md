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
| **Phase 4** | Extensibility Patterns (Months 4–6) | **Ch 7** | Chain of Command, method wrapping, event handlers, delegates, table/form extensions |
| **Phase 5** | Business Logic & Backend (Months 5–7) | **Ch 6** + **Ch 11** | RunBase, SysOperation, batch processing, job framework |
| **Phase 6** | Integration (Months 6–8) | **Ch 9** | Data entities, integration patterns, REST APIs, OData |
| **Phase 7** | Reporting & Analytics (Months 7–9) | **Ch 10** | SSRS reports, legacy AX reports, analytical reporting, BI |
| **Phase 8** | Testing & Debugging (Months 7–10) | **Ch 12** | Unit testing (SysTest), ATL, RSAT, debugging |
| **Phase 9** | DevOps & CI/CD (Months 8–10) | **Ch 13** | Build automation, LCS, Azure DevOps, ALM |
| **Phase 10** | Security & Compliance (Months 9–11) | **Ch 8** | Security model, roles/duties/privileges, XDS, SoD |
| **Phase 11** | Performance & Problem Solving (Months 10–12) | **Ch 14** | SQL optimization, caching, indexing, bottleneck identification |
| **Phase 12** | Solution Crafting & Capstone (Months 11–12) | **Ch 15** | End-to-end production scenario, design patterns, solution crafting |

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
| Delegates | Phase 4, §4.5 | Ch 7, §7.3 |
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
| End-to-end capstone | Phase 12, §12.3 | Ch 15 |

---

## Guide Comparison

| Aspect | Main Guide (`d365_fao_technical_concepts_guide.md`) | Desktop Guide (`d365-learning-guide.md`) |
|---|---|---|
| **Structure** | 12 phases organized by learning month | 15 chapters organized by topic area |
| **Depth** | Conceptual overviews with key code snippets | Deep dives with full code examples, tables, and activities |
| **Best for** | Quick reference, understanding what to learn next | In-depth study, hands-on practice, exam prep |
| **Length** | ~1,784 lines (~197 KB) | ~10,000+ lines (~400 KB) |
| **Activities** | No — reference only | Yes — each chapter has an activity with hints and ideal solution |
| **Approach** | Linear progression (Phase 1 → 12) | Topic-focused (Ch 1 covers landscape, Ch 2 covers X++, etc.) |

---

## Recommended Reading Order

For a new intern starting the journey:

1. **Ch 1** → Understand the platform landscape
2. **Ch 2** → Learn X++ fundamentals and class design
3. **Main Guide Phase 1** → Reinforce foundations with the conceptual overview
4. **Ch 3** → Master tables and EDTs
5. **Main Guide Phase 2** → Deepen development knowledge
6. **Ch 4** → Build forms
7. **Ch 5** → Learn views and cross-table queries
8. **Ch 6** → Write business logic classes
9. **Ch 7** → Master extensibility patterns (CoC, Event Handlers, Delegates)
10. **Ch 8** → Understand security
11. **Ch 9** → Build integrations with data entities
12. **Ch 10** → Create reports
13. **Ch 11** → Write batch jobs
14. **Ch 12** → Write tests
15. **Ch 13** → Set up DevOps pipelines
16. **Ch 14** → Optimize performance
17. **Ch 15** → Capstone project
