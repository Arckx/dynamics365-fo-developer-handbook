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

### Changed
- **README.md** — Added quick reference files section, updated curriculum to 35 chapters, linked all new guides
- **memory.md** — Updated index with new reference files

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