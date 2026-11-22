---
name: d365-capstone-rubric
description: Capstone project grading rubric for Chapter 22 — architecture, code quality, tests, docs, security
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Capstone Project Rubric

> **Used for Chapter 22 Capstone Projects** — Evaluates end-to-end architecture, implementation quality, and delivery.

---

## Scoring Overview

| Category | Weight | Max Points |
|----------|--------|------------|
| **Architecture & Design** | 25% | 25 |
| **Code Quality & Patterns** | 25% | 25 |
| **Functionality & Requirements** | 20% | 20 |
| **Testing & Quality Gates** | 15% | 15 |
| **Security & Compliance** | 10% | 10 |
| **Documentation & Delivery** | 5% | 5 |
| **Total** | 100% | **100** |

---

## 1. Architecture & Design (25 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Overall Architecture** | Clean layered architecture; clear separation of concerns; documented with diagrams | Good separation; minor coupling issues | Some mixing of layers; unclear boundaries | Monolithic; no clear architecture |
| **Data Model** | Normalized (3NF); proper PK/FK; EDTs used throughout; indexes on FKs | Mostly normalized; minor denormalization | Some base types used; missing indexes | Flat tables; no relationships |
| **Extensibility Design** | All customizations use CoC/Events; zero over-layering; extension points documented | Mostly CoC; 1-2 over-layered | Mix of patterns; several over-layered | Direct modifications to SYS |
| **Integration Design** | Async patterns; Data Entities/OData; error handling; idempotency | Sync/Async mix; basic error handling | Basic integration; no retry logic | Direct SQL; no error handling |
| **Scalability Considerations** | Batch for volume; caching strategy; partitioning considered | Basic batch usage | No batch; single-threaded | No consideration |

**Subtotal: ___ / 25**

---

## 2. Code Quality & Patterns (25 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Naming Conventions** | Perfect adherence to all conventions (tables, EDTs, classes, extensions) | 1-2 minor deviations | Several deviations | Inconsistent/non-standard |
| **X++ Best Practices** | No BP warnings; proper `checkFailed()`, `ttsBegin`, specific selects | 1-2 BP warnings | Several BP warnings | Many BP warnings |
| **CoC Usage** | Correct `next` usage; proper pre/post logic; no `super()` in extensions | Minor CoC issues | `super()` in extensions; wrong order | No CoC; overrides used |
| **Error Handling** | Structured exceptions; `Deadlock` retry; meaningful messages; `checkFailed` in validation | Basic try/catch; some retry | Generic catch; no retry | No error handling |
| **Performance Patterns** | `insert_recordset`/`update_recordset`/`delete_from`; `exists join`; proper caching | Mostly bulk operations | Some loop operations | Select/update in loops |

**Subtotal: ___ / 25**

---

## 3. Functionality & Requirements (20 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Requirements Coverage** | 100% of functional requirements met; edge cases handled | 90%+ met; minor gaps | 70-89% met | <70% met |
| **Business Logic Correctness** | All calculations, validations, workflows correct | Minor logic bugs | Several logic issues | Major logic flaws |
| **UI/Forms Usability** | Intuitive; proper patterns (ListPage, FactBox); validation feedback | Good UX; minor issues | Usable but confusing | Poor UX; missing patterns |
| **Batch/Async Processing** | Long-running ops in batch; progress reporting; cancellation | Basic batch usage | Sync only for heavy ops | No batch; timeouts |

**Subtotal: ___ / 20**

---

## 4. Testing & Quality Gates (15 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Unit Test Coverage** | >80% coverage; property-based tests for invariants | >60% coverage; basic SysTest | Some tests; <50% coverage | No tests |
| **Integration Tests** | Key flows tested (O2C, P2P); test data factories used | Basic integration tests | Manual testing only | No integration tests |
| **Code Review** | All code reviewed; checklist passed; findings addressed | Self-reviewed; minor findings | No review | No review |

**Subtotal: ___ / 15**

---

## 5. Security & Compliance (10 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Role-Based Security** | Custom roles; duties/privileges; least privilege; menu items secured | Basic roles; some over-privileged | Default roles only | No security |
| **XDS / Record-Level** | XDS policies on sensitive tables; tested | Basic XDS | No XDS | No XDS |
| **Audit Logging** | Critical operations logged; immutable; queryable | Basic logging | No logging | No logging |

**Subtotal: ___ / 10**

---

## 6. Documentation & Delivery (5 pts)

| Criterion | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (1-2) |
|-----------|---------------|----------------|----------------|-----------------|
| **Architecture Doc** | Data model, sequence diagrams, deployment, security | Good docs; missing 1 area | Basic docs; missing several | Minimal/no docs |
| **Deployment Guide** | Step-by-step; prerequisites; rollback plan | Good guide | Basic steps | No guide |
| **Delivery** | On time; deployable package; Git tags; release notes | On time; package | Late; package | Missing artifacts |

**Subtotal: ___ / 5**

---

## Total Score: ___ / 100

### Grade Bands

| Score | Grade | Description |
|-------|-------|-------------|
| 90-100 | A | **Distinction** — Production-ready; exceeds expectations |
| 80-89 | B | **Proficient** — Solid work; minor improvements needed |
| 70-79 | C | **Developing** — Functional but needs significant refinement |
| 60-69 | D | **Beginning** — Major gaps; requires rework |
| <60 | F | **Insufficient** — Does not meet minimum standards |

---

## Detailed Feedback Template

```
CAPSTONE EVALUATION — [Student Name] — [Date]

PROJECT: [Project Title]
MENTOR: [Mentor Name]

SCORES:
├── Architecture & Design:        ___ / 25
├── Code Quality & Patterns:      ___ / 25
├── Functionality & Requirements: ___ / 20
├── Testing & Quality Gates:      ___ / 15
├── Security & Compliance:        ___ / 10
├── Documentation & Delivery:     ___ / 5
└── TOTAL:                        ___ / 100

GRADE: [A/B/C/D/F]

STRENGTHS:
• 
• 
• 

AREAS FOR IMPROVEMENT:
• 
• 
• 

SPECIFIC CODE REVIEW NOTES:
• File:Line — Issue
• 

RECOMMENDED NEXT STEPS:
1. 
2. 
3. 

MENTOR SIGNATURE: _______________  DATE: ___________
STUDENT ACKNOWLEDGMENT: _______________  DATE: ___________
```

---

## Capstone Project Ideas (for reference)

| Domain | Project Scope | Key Technical Challenges |
|--------|---------------|--------------------------|
| **Manufacturing P2P** | Vendor → PO → Receipt → Quality → Invoice → Payment | Multi-table transactions, quality workflow, batch costing |
| **Intercompany Trade** | Company A sells to Company B; auto-generate STO | Cross-company, cross-currency, tax, transfer pricing |
| **Project-Based Services** | Quote → Project → Timesheet → Invoice → Revenue Rec | WBS, resource allocation, milestone billing, rev rec |
| **Retail Omnichannel** | POS → HQ → Replenishment → Store → Customer | Real-time sync, offline POS, inventory visibility |
| **Field Service** | Work Order → Dispatch → Mobile → Completion → Invoice | Scheduling, geo, mobile offline, warranty/contracts |

---

## Submission Checklist

Before submitting, verify:

- [ ] **Code compiles** with zero errors, zero BP warnings
- [ ] **All tests pass** (unit + integration)
- [ ] **Deployable package** builds successfully (.axmodel + ModuleDescriptor.xml)
- [ ] **Database sync** runs clean on fresh Tier-1
- [ ] **Security roles** tested with non-admin user
- [ ] **Documentation** complete (arch, deployment, user guide)
- [ ] **Git repo** tagged with version (e.g., `v1.0.0-capstone`)
- [ ] **Release notes** written
- [ ] **Code review** completed and findings addressed
- [ ] **Mentor demo** scheduled

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*