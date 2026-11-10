# VSI Asset Management Codebase vs. D365 Learning Guide — Gap Analysis

**Generated:** November 11, 2026  
**VSI Version:** 5.0 (319 files, 2MB)  
**Learning Guide Version:** 30 chapters (d365-learning-guide.md)

---

## Executive Summary

The D365 Learning Guide (30 chapters) provides **excellent coverage** of the VSI Asset Management patterns. Chapters 23–30 were specifically designed to cover the advanced VSI patterns. However, there are **specific VSI implementation details** and **emerging patterns** that could be deepened or added as new advanced chapters.

**Coverage Assessment:** ~90% of VSI patterns are covered; ~10% need enhancement or new chapters.

---

## Detailed Gap Analysis

### ✅ FULLY COVERED (Chapters 23–30)

| VSI Pattern | Chapter | Coverage Quality |
|-------------|---------|------------------|
| Workflow Framework (7 event handler interfaces) | Ch 23 | Excellent — full VSI code examples |
| NumberSeqModule registration + scope types | Ch 24 | Excellent — exact VSI code |
| Data entities + staging + mapEntityToDataSource | Ch 25 | Excellent — VSI vendor/worker examples |
| Form patterns (ListPage, SimpleListDetails, FactBox, Tree) | Ch 26 | Excellent — exact VSI form code |
| Action Center notifications + SystemNotificationsManager | Ch 27 | Excellent — VSI truncation + admin lookup |
| IDisposable status change context (guard pattern) | Ch 27 | Excellent — VSIAssetStatusChangeContext |
| SysOperation runtime tasks + bundle sizing | Ch 28 | Excellent — VSI task controller pattern |
| Deadlock retry with #RetryNum + exponential backoff | Ch 28 | Excellent — VSI execute wrapper |
| Cross-company queries with changecompany | Ch 28 | Excellent — VSI companies() pattern |
| VSIBatchConstants centralized configuration | Ch 28 | Excellent — exact constants table |
| Label files + AppChecker config | Ch 29 | Good — VSI label file format shown |
| Custom services + DataContract/ServiceProcessor | Ch 30 | Excellent — exact VSI service pattern |
| FormJsonSerializer + Newtonsoft.Json | Ch 30 | Excellent — VSI catalog test harness |
| AxServiceGroup / AxService / Security entry points | Ch 30 | Excellent — XML metadata shown |

---

### ⚠️ PARTIALLY COVERED — NEEDS VSI-SPECIFIC DEEPENING

| Gap Area | Current Coverage | Missing VSI Detail |
|----------|------------------|-------------------|
| **VSIAssetStatusHelper.changeStatus** | Ch 27 mentions pattern | Exact implementation with status history logging, multi-company |
| **VSIAssetNotificationHelper** | Ch 27 shows notifyUsers | Specific truncation logic, admin user PlatformUserId join pattern |
| **VSIAssetServiceHelper.execute** | Ch 30 shows execute | infologLine capture, resolveCompany, cross-company tts handling |
| **VSIAssetServiceCatalog test harness** | Ch 30 shows runTest | prettyPrint, isWriteOperation, requestCompany extraction |
| **VSIWorker query pattern** | Not explicitly shown | PlatformUserId + UserInfo join for enabled users |
| **SysQueryRangeUtil patterns** | Not covered | dayRange, monthRange, yearRange, dateRange usage in VSI |
| **Recursive tree building** | Ch 26 shows buildTree | VSI-specific parent-child map + selection sync pattern |
| **MultiSelectionHelper range building** | Ch 26 shows basic usage | queryValue concatenation for report ranges |

---

### 🆕 MISSING TOPICS — CANDIDATES FOR NEW CHAPTERS (31+)

| Missing Topic | VSI Evidence | Priority | Suggested Chapter |
|---------------|--------------|----------|-------------------|
| **SysQueryRangeUtil & Advanced Query Ranges** | VSI uses date ranges extensively | High | Ch 31 |
| **Event-Driven Architecture (Service Bus, Event Grid)** | Not in VSI but standard D365 pattern | Medium | Ch 32 |
| **Power Automate / Logic Apps Integration Patterns** | Ch 19 mentions but no code | Medium | Ch 33 |
| **OData Actions & Functions (beyond Data Entities)** | Ch 19 mentions SysOperationServiceController | Medium | Ch 34 |
| **Unit Testing Batch Jobs (SysTest + BatchHeader)** | Ch 12 covers SysTest, not batch testing | High | Ch 35 |
| **Unit Testing Workflows** | Not covered | Medium | Ch 36 |
| **Unit Testing Custom Services** | Not covered | Medium | Ch 37 |
| **Performance Testing & Load Testing Patterns** | Not covered | Medium | Ch 38 |
| **Database Logging / Change Data Capture** | Not in VSI but critical for audit | Low | Ch 39 |
| **Advanced Security: Record-Level Security (XDS) Deep Dive** | Ch 8 covers XDS, not VSI-specific | Medium | Ch 40 |
| **Mobile Workspace Development** | Ch 19 mentions, no code | Low | Ch 41 |
| **CDS/Dataverse Virtual Tables** | Not covered | Low | Ch 42 |
| **AI/Copilot Extensibility Patterns** | Ch 19 mentions, no code | Low | Ch 43 |
| **Telemetry & Application Insights Integration** | Not covered | Medium | Ch 44 |
| **Feature Management / Flighting** | Not covered | Low | Ch 45 |

---

## Recommended Action Plan

### Phase 1: Enhance Existing Chapters with VSI Deep Dives (Immediate)
1. **Ch 27** — Add `VSIAssetStatusHelper.changeStatus` full implementation
2. **Ch 27** — Add `VSIAssetNotificationHelper` complete pattern with admin lookup
3. **Ch 30** — Add `VSIAssetServiceHelper.execute` full pattern with infolog capture
4. **Ch 30** — Add `VSIAssetServiceCatalog` test harness complete implementation
5. **Ch 26** — Add SysQueryRangeUtil patterns used in VSI reports
6. **Ch 28** — Add VSIWorker PlatformUserId query pattern

### Phase 2: Add New Advanced Chapters (Priority Order)
1. **Ch 31** — SysQueryRangeUtil & Advanced Query Ranges (High — used everywhere in VSI)
2. **Ch 35** — Unit Testing Batch Jobs (High — critical for CI/CD)
3. **Ch 34** — OData Actions & Functions (Medium — extends Ch 19/30)
4. **Ch 33** — Power Automate Integration Patterns (Medium — real-world integration)
5. **Ch 36** — Unit Testing Workflows (Medium — workflows are complex)
6. **Ch 37** — Unit Testing Custom Services (Medium — services need contract testing)
7. **Ch 38** — Performance Testing Patterns (Medium — production hardening)
8. **Ch 44** — Telemetry & Application Insights (Medium — observability)

### Phase 3: Specialized Topics (Lower Priority)
9. **Ch 32** — Event-Driven Architecture
10. **Ch 39** — Database Logging / CDC
11. **Ch 40** — Advanced XDS with VSI Patterns
12. **Ch 41** — Mobile Workspace Development
13. **Ch 42** — Dataverse Virtual Tables
14. **Ch 43** — AI/Copilot Extensibility
15. **Ch 45** — Feature Management

---

## VSI Code References for Enhancement

### Key VSI Files to Reference (from codebase dump)
| Pattern | VSI File/Class | Lines/Content |
|---------|----------------|---------------|
| Status change context | `VSIAssetStatusChangeContext` | IDisposable singleton guard |
| Document status context | `VSIDocumentStatusChangeContext` | Workflow status transitions |
| Status helper | `VSIAssetStatusHelper::changeStatus` | Multi-field update + history log |
| Notification helper | `VSIAssetNotificationHelper` | truncate, assetAdministratorUserIds |
| Service helper | `VSIAssetServiceHelper::execute` | infologLine, resolveCompany, changecompany |
| Service catalog | `VSIAssetServiceCatalog` | runTest, prettyPrint, isWriteOperation |
| Batch constants | `VSIBatchConstants` | All shared limits |
| Number sequences | `VSIAssetNumberSeqModule` | loadModule + buildModulesMapSubscriber |
| Data entity mapping | `VSIVendorEntity::mapEntityToDataSource` | Insert/Update with orig() |
| Workflow handlers | `VSIAssetRequestApprovalEventHandler` | 7 interfaces implemented |
| Runtime tasks | `VSIAssetIntegrityAuditBatchTaskController` | parmShowDialog(false) |
| Tree form | `VSIFunctionalLocation::buildTree` | Recursive parent-child map |
| Form overrides | `VSIAssetIntegrityAuditBatchUIBuilder` | registerOverrideMethod |
| Query ranges | Various reports | SysQueryRangeUtil::dateRange, monthRange |

---

## Cross-Reference Updates Needed

After enhancements, update:
- `d365-guide-cross-reference.md` — Add new chapters 31–45 to phase mapping
- `README.md` — Update key files list, add new chapter summaries
- `d365-fao-learning-journey.md` — Add months 13+ for advanced topics
- `d365-xpp-exercises.md` — Add exercises for new chapters