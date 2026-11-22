# Changelog

All notable changes to the D365 F&O Developer Handbook.

## [Unreleased] - 2026-11-22

### Added
- **d365-migration-guide.md** — AX 2012 → D365 F&O migration guide with code upgrade patterns, metadata mapping, DMF data migration
- **d365-copilot-guide.md** — Copilot extensibility: plugins, actions, skills, prompt engineering, Custom APIs
- **d365-testing-patterns.md** — Property-based testing, test data factories, SysTest + TestFramework integration
- **d365-observability.md** — Application Insights integration, custom telemetry, performance counters, alerting rules
- **d365-security-patterns.md** — Role/privilege design, XDS policies, audit logging, compliance patterns
- **d365-pipeline-templates/** — Azure DevOps pipelines: build, release, database sync
- **d365-code-review-checklist.md** — PR review checklist: naming, CoC, transactions, SQL, security, tests
- **d365-perf-benchmark.md** — Performance benchmarking scripts, SQL queries, load testing, CI/CD gates
- **d365-security-audit.md** — Security audit checklist: SoD, XDS coverage, privilege creep, compliance
- **d365-cookbook.md** — Copy-paste patterns for tables, queries, forms, services, entities, testing
- **d365-foundations.md** — **Chapter 0** — ERP concepts, D365 F&O modules, business processes, Azure basics
- **d365-oop-primer.md** — OOP concepts mapped to X++: classes, inheritance, interfaces, polymorphism, SOLID
- **d365-sql-primer.md** — SQL basics mapped to X++: SELECT, JOIN, INDEX, transactions, query plans
- **d365-environment-setup.md** — Step-by-step Tier-1 VM, VS + D365 extension, first project, Git setup
- **d365-architecture-diagrams.md** — Mermaid.js diagrams for all key architectures
- **d365-flashcards.md** — Anki/Quizlet flashcard export for glossary + key concepts
- **d365-study-guide-quizzes.md** — 5-10 MCQs per chapter with explanations (245 total)
- **d365-capstone-rubric.md** — Grading rubric for Chapter 22 capstone projects
- **d365-pair-programming-prompts.md** — Driver/navigator exercises for complex topics
- **d365-video-links.md** — Curated Microsoft Learn + YouTube links with timestamps per chapter
- **d365-learning-path-tracker.md** — Printable progress tracker with checkboxes, time estimates, milestones for 12-month journey
- **d365-oop-exercises.md** — 10 hands-on OOP exercises with solutions mapped to X++ patterns
- **d365-sql-exercises.md** — 10 hands-on SQL exercises with practice schema, X++ mappings, solutions
- **d365-business-glossary.md** — Business terms (P2P, O2C, MRP, BOM, financial, supply chain)
- **d365-role-day-in-life.md** — Day-in-life of AP Clerk, Warehouse Worker, Controller, Buyer, Developer
- **d365-erp-comparison.md** — SAP vs Oracle vs NetSuite vs D365 F&O — architecture, licensing, why choose F&O
- **d365-beginner-faq.md** — 50 common beginner questions — D365 basics, X++, SQL, OOP, workflow
- **d365-career-paths.md** — Junior → Architect progression — roles, skills, certs, salaries, 12-month plans
- **d365-production-grade-development.md** — Production-grade development — decision frameworks, trade-off analysis, code structuring principles, mental models for building requirements that survive production

### Changed
- **README.md** — Added Foundational Guides (9), Learning Tools & Visual Aids (11) sections; updated curriculum to 35 chapters; linked all new guides
- **memory.md** — Updated index with all 35 new reference files

---

## [1.0.0] - 2026-08-29

### Added
- **d365-learning-guide.md** — 30-chapter desktop guide (Chapters 1-15 complete, 16-30 outline)
- **d365-fao-learning-journey.md** — 12-month structured study plan
- **d365-guide-cross-reference.md** — Master index mapping phases to chapters
- **d365-xpp-quick-reference.md** — X++ syntax cheat sheet
- **d365-xpp-exercises.md** — 17 hands-on exercises
- **d365-glossary.md** — 100+ term glossary
- **d365-handbook-appendices.md** — Reference appendices
- **d365-anti-patterns.md** — Anti-pattern library
- **d365-certification-mapping.md** — MB-310, MB-330, MB-500 mapping
- **d365-cheatsheet.md** — One-page printable reference
- **d365-troubleshooting.md** — 50+ common errors with fixes

### Fixed
- AX 2012 legacy references corrected in Chapters 1-15
- `validateWrite()` patterns updated to use `checkFailed()` not `error()`
- Cross-references between learning guide and exercises validated

---

## Versioning Scheme

- **Major** — Structural reorganization, chapter count changes
- **Minor** — New chapters, major new guides, pipeline templates
- **Patch** — Fixes, clarifications, link updates, typo corrections

## Microsoft Docs Alignment

Each chapter includes `<!-- last-verified: YYYY-MM-DD -->` comment. Run verification quarterly against:
- https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/

---

*Generated: 2026-11-22*