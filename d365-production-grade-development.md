---
name: d365-production-grade-development
description: Production-grade D365 F&O development — decision frameworks, trade-off analysis, code structuring principles, and mental models for building requirements that survive production
metadata:
  type: reference
  last-verified: 2026-11-22
---

# Production-Grade D365 F&O Development

> **The missing chapter** — How to think like a senior developer when structuring code for new requirements. This chapter synthesizes the mental models, decision frameworks, and trade-off analysis that separate code that "works in dev" from code that survives production.

---

## 1. What "Production-Grade" Means in D365 F&O

### 1.1 The Definition

> **Production-grade code** is code that:
> - **Survives upgrades** without rewrite (extensibility-first)
> - **Performs under load** (set-based SQL, caching, batch patterns)
> - **Fails safely** (transactions, idempotency, deadlock handling)
> - **Is observable** (telemetry, audit logging, structured errors)
> - **Is secure by default** (declarative security, XDS, least privilege)
> - **Is testable** (unit tests, integration tests, property-based tests)
> - **Is operable** (feature flags, feature management, graceful degradation)
> - **Is maintainable** (clear ownership, documentation, low cognitive load)

### 1.2 The Production Reality Check

| Dev Environment | Production Reality |
|-----------------|-------------------|
| 100 test records | 10M+ transaction records |
| Single user | 500+ concurrent users |
| No concurrent edits | Optimistic locking conflicts |
| Clean data | Dirty data, nulls, duplicates |
| No batch jobs | 50+ concurrent batch jobs |
| No integrations | 20+ external systems |
| No compliance | SOX, GDPR, SOX auditors |

**Production-grade thinking** = designing for the right column while developing in the left.

---

## 2. The Mental Model: How Senior Developers Structure Code

### 2.1 The Decision Hierarchy

When a new requirement arrives, senior developers don't start coding. They run through this hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REQUIREMENT ARRIVES                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 1: CAN WE AVOID CODE?                                                 │
│  ──────────────────────────────────────────────────────────────────────────  │
│  • Configuration keys / Feature management?                                 │
│  • Existing standard feature with configuration?                            │
│  • Power Automate / Logic Apps instead of X++?                              │
│  • Data Entity + DMF instead of custom import?                              │
│  • Standard workflow instead of custom state machine?                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ (If code is unavoidable)
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 2: EXTENSIBILITY FIRST                                                │
│  ──────────────────────────────────────────────────────────────────────────  │
│  • Extension (CoC) > Event Handler > Override (never)                       │
│  • ExtensionOf on Table > Form > Class > View                               │
│  • Chain of Command preserves upgrade path                                  │
│  • Event handlers for cross-cutting concerns (logging, audit)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 3: ARCHITECTURAL PATTERN SELECTION                                    │
│  ──────────────────────────────────────────────────────────────────────────  │
│  • SysOperation (batch/service) vs RunBaseBatch (legacy)                    │
│  • Data Entity (OData/DMF) vs Custom Service vs Direct Table Access         │
│  • Event-driven (Action Center, Notifications) vs Polling                   │
│  • Feature Management for gradual rollout                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LEVEL 4: PRODUCTION HARDENING (The "Before Commit" Checklist)              │
│  ──────────────────────────────────────────────────────────────────────────  │
│  • Transactions: ttsBegin/Commit/Abort on EVERY multi-table operation       │
│  • Deadlock handling: catch(Exception::Deadlock), retry 3x with backoff    │
│  • Set-based SQL: insert_recordset, update_recordset, delete_from          │
│  • CacheLookup strategy on every table                                      │
│  • Idempotency keys for integrations                                        │
│  • Feature flags for gradual rollout                                        │
│  • Telemetry: trackMetric, trackEvent, trackDependency                      │
│  • Audit logging for critical operations                                    │
│  • Feature Management gate for rollback                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Requirement-to-Code Framework

### 3.1 The Requirement Decomposition Template

Before writing a single line, fill this out:

```markdown
# Requirement: [Brief Title]

## 1. Business Context
- **What**: [One sentence: what does the user need to accomplish?]
- **Why**: [Business value, compliance driver, efficiency gain]
- **Who**: [User roles, external systems, batch vs interactive]
- **When**: [Real-time, scheduled, on-demand, event-triggered]

## 2. Data Impact Analysis
- **Tables touched**: [List every table: read/write/create/delete]
- **Volume**: [Records per transaction, per day, peak hour]
- **Data quality**: [Nulls, duplicates, dirty data handling]
- **Retention**: [Archive policy, GDPR/SOX implications]

## 3. Integration Surface
- **Inbound**: [OData, DMF, Custom Service, File, Queue]
- **Outbound**: [Events, OData, Service Bus, Logic Apps, File]
- **Idempotency**: [How to handle duplicate calls?]
- **Contracts**: [Schema versioning, backward compatibility]

## 4. Security & Compliance
- **Roles**: [Who can execute? Read vs Write vs Approve]
- **XDS policies**: [Record-level filtering needed?]
- **Audit trail**: [What must be logged? Immutable?]
- **Segregation of Duties**: [Conflicts with existing roles?]
- **PII/GDPR/SOX**: [Fields requiring special handling?]

## 5. Performance Contract
- **SLA**: [Response time: interactive <2s, batch <30min]
- **Volume**: [Peak TPS, daily volume, growth rate]
- **Concurrency**: [Expected concurrent users/jobs]
- **Data growth**: [Year 1, Year 3, Year 5 projections]

## 6. Failure Modes & Recovery
- **Retry strategy**: [Transient vs permanent failures]
- **Idempotency keys**: [How to safely retry?]
- **Rollback**: [Manual? Automatic? Point-in-time?]
- **Alerting**: [What triggers on-call?]
- **Degradation**: [Circuit breaker? Feature flag off?]

## 7. Observability Requirements
- **Metrics**: [Latency, throughput, error rate, queue depth]
- **Traces**: [Distributed tracing correlation IDs]
- **Logs**: [Structured, searchable, PII-free]
- **Alerts**: [Thresholds, runbooks, escalation]

## 8. Rollout Strategy
- **Feature flag**: [Name, default off, target audience]
- **Environments**: [Dev → UAT → Staging → Prod]
- **Rollback plan**: [One-click disable, data migration back]
- **Validation**: [Smoke tests, synthetic transactions]
```

---

## 4. Architectural Pattern Selection Guide

### 4.1 Pattern Selection Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    START: WHAT DOES THE REQUIREMENT DO?          │
└─────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│ READ DATA     │           │ WRITE DATA    │           │ PROCESS       │
│ (Query/Report)│           │ (CRUD)        │           │ (Batch/Logic) │
└───────┬───────┘           └───────┬───────┘           └───────┬───────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│ Simple query? │           │ Single record?│           │ Long-running? │
│ → while select│           │ → insert()/   │           │ → SysOperation│
│ Complex query?│           │ update()/     │           │ (Batch/Async) │
│ → QueryBuild  │           │ delete()      │           │ Short?        │
│ → View/SysDa  │           │ Bulk?         │           │ → SysOperation│
│ Report?       │           │ → insert_     │           │ (Sync)        │
│ → SSRS/ER     │           │   recordset   │           │ Event-driven? │
│ External API? │           │ → update_     │           │ → Event Grid/ │
│ → Data Entity │           │   recordset   │           │   Action Ctr  │
└───────────────┘           └───────────────┘           └───────────────┘
```

### 4.2 Pattern Selection Checklist

| Requirement Characteristic | Recommended Pattern | Avoid |
|---------------------------|---------------------|-------|
| **Interactive CRUD, single record** | Table `insert/update/delete` + `validateWrite` | Direct SQL |
| **Bulk data import** | `insert_recordset` / `RecordInsertList` / DMF | Loop with `insert()` |
| **Mass update/delete** | `update_recordset` / `delete_from` with joins | Loop with `update()`/`delete()` |
| **Complex query, reusable** | `QueryBuild` classes / `SysDa` | String concatenation |
| **Report/Analytics** | SSRS (pixel-perfect) / ER (configurable) | Custom X++ to Excel |
| **External API (read)** | Data Entity (OData) | Custom service for simple reads |
| **External API (write)** | Custom Service (SysOperation) + Data Entity | Direct table inserts |
| **Long-running process** | SysOperation (Async/Batch) | Interactive form code |
| **Scheduled/Recurring** | SysOperation + Batch Schedule | Windows Task Scheduler |
| **Event-driven reaction** | Event Handler (post) / Action Center | Polling loops |
| **State machine** | Workflow / Custom state field + events | Hardcoded if/else chains |
| **Configuration-driven** | Feature Management / Parameters table | Hardcoded constants |
| **Cross-system sync** | Dual-write / Logic Apps / Custom Service | Direct DB links |

---

## 5. The Production Hardening Checklist (Mental Model)

### 5.1 Before Every Commit, Ask:

> **"If this runs at 3 AM on Black Friday with 10,000 concurrent users and dirty data, what breaks?"**

| Category | The Question | The Standard |
|----------|--------------|--------------|
| **Transactions** | Does every multi-table write have `ttsBegin/Commit/Abort`? | 100% yes |
| **Deadlocks** | Is `catch(Exception::Deadlock)` with retry 3x + backoff on every DB call? | Yes |
| **SQL Patterns** | Zero `select *`, zero `select` in loops, zero `update()` in loops? | 100% set-based |
| **Caching** | Every reference table has `CacheLookup` (`Found`/`EntireTable`)? | Yes |
| **Idempotency** | Can this run twice safely? (Idempotency keys, upsert logic) | Yes |
| **Feature Flags** | Is new functionality behind a Feature Management flag? | Yes |
| **Telemetry** | `trackMetric`, `trackEvent`, `trackDependency` on critical paths? | Yes |
| **Audit Logging** | Critical ops (post, approve, delete) logged immutably? | Yes |
| **Security** | Declarative (menu items), not imperative (`hasPrivilege`)? | Yes |
| **XDS** | Sensitive data has record-level policies? | Yes |
| **Tests** | Unit test for logic, integration for flows, property-based for invariants? | Yes |
| **Feature Flag** | Can we turn this OFF in 30 seconds without deploy? | Yes |
| **Rollback** | Can we disable and clean up data in <30 min? | Yes |
| **Documentation** | XML comments on public APIs, trade-off rationale in PR? | Yes |

---

## 6. Trade-Off Analysis Framework

### 6.1 The Trade-Off Matrix

For every significant decision, document:

| Decision | Option A | Option B | Chosen | Rationale |
|----------|----------|----------|--------|-----------|
| **Example: Currency validation** | `select CurrencyTable` (accurate, slower) | Static list (fast, stale risk) | Option A | Financial accuracy > 2ms latency; cache CurrencyTable |
| **Example: Batch chunking** | Single large batch (simpler) | Chunked parallel (complex, faster) | Option B | 50k records → 45 min vs 8 min; retry granularity |
| **Example: Validation location** | Table `validateWrite` (always runs) | Service layer (controlled) | Option A | Data integrity > flexibility; prevent bad data at source |

### 6.2 Common Trade-Off Categories

| Category | Typical Tension | Resolution Principle |
|----------|-----------------|----------------------|
| **Accuracy vs Performance** | DB lookup vs cached list | Accuracy wins for financial/compliance; cache with TTL for reference data |
| **Flexibility vs Simplicity** | Config-driven vs hardcoded | Config-driven for business rules; hardcode for technical constants |
| **Consistency vs Availability** | Strong consistency (transactions) vs eventual (events) | Strong for financial; eventual for notifications/analytics |
| **Coupling vs Reuse** | Shared library vs duplication | Shared for stable domain logic; duplicate for unstable/experimental |
| **Build vs Buy** | Custom code vs standard feature | Buy (standard) unless competitive differentiator |
| **Sync vs Async** | Immediate consistency vs user experience | Async for >2s operations; sync for user-facing confirmations |
| **Normalization vs Performance** | 3NF vs denormalized | Normalize first; denormalize only with measured proof |

---

## 6.3 The "Production Hardening" Pattern Library

### 6.3.1 The Resilient Service Template

```xpp
class ResilientService extends SysOperationServiceBase
{
    public void run(ResilientContract _contract)
    {
        // 1. Input validation (fail fast)
        this.validateContract(_contract);
        
        // 2. Idempotency check
        if (this.isDuplicateRequest(_contract.idempotencyKey()))
        {
            info("Duplicate request ignored");
            return;
        }
        
        // 3. Execute with resilience
        this.executeWithResilience(_contract);
        
        // 4. Record successful processing
        this.recordIdempotencyKey(_contract.idempotencyKey());
    }
    
    private void executeWithResilience(ResilientContract _contract)
    {
        int retryCount = 0;
        const int MaxRetries = 3;
        
        while (true)
        {
            ttsBegin;
            try
            {
                // Core business logic here
                this.executeCore(_contract);
                ttsCommit;
                return; // Success
            }
            catch (Exception::Deadlock)
            {
                ttsAbort;
                retryCount++;
                if (retryCount >= 3)
                {
                    throw Exception::Deadlock; // Give up after 3
                }
                sleep(1000 * retryCount * retryCount); // Exponential backoff
            }
            catch (Exception::Error)
            {
                ttsAbort;
                this.logFailure(_contract, getExceptionText());
                throw; // Non-retryable, bubble up
            }
            catch (Exception::CLRError)
            {
                ttsAbort;
                this.logCLRFailure(_contract);
                throw;
            }
        }
    }
    
    // Hook methods for customization
    protected void validateContract(ResilientContract _contract) { }
    protected void executeCore(ResilientContract _contract) { }
    protected void logFailure(ResilientContract _contract, str _error) { }
    protected void logCLRFailure(ResilientContract _contract) { }
    private boolean isDuplicateRequest(str _key) { return false; }
    private void recordIdempotencyKey(str _key) { }
}
```

### 6.3.2 The Safe Batch Chunking Pattern

```xpp
class ChunkedBatchService extends SysOperationServiceBase
{
    public void run(ChunkedBatchContract _contract)
    {
        // 1. Validate
        if (_contract.chunkSize() <= 0) _contract.parmChunkSize(1000);
        
        // 2. Get total count for progress
        int totalCount = this.getTotalCount(_contract);
        _contract.parmTotalCount(totalCount);
        
        // 3. Process in chunks
        int processed = 0;
        int chunkNumber = 0;
        
        while (processed < totalCount)
        {
            chunkNumber++;
            
            // Process chunk in own transaction
            ttsBegin;
            try
            {
                int chunkProcessed = this.processChunk(_contract, chunkNumber);
                ttsCommit;
                
                processed += chunkProcessed;
                this.updateProgress(_contract, processed, totalCount);
                
                // Check cancellation
                if (Batch::checkForCancel())
                {
                    throw error("Batch cancelled by user");
                }
            }
            catch (Exception::Deadlock)
            {
                ttsAbort;
                // Retry logic here
            }
            catch (Exception::Error)
            {
                ttsAbort;
                throw;
            }
        }
    }
}
```

---

## 7. The Code Structuring Principles

### 7.1 The Layered Code Organization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION-GRADE CODE STRUCTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CONTRACT LAYER (Data, Validation)                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • DataContract classes (parmX pattern, DataMember, SysOperationValidated) │
│  • Pure data holders — NO business logic                                    │
│  • Validation attributes (SysOperationValidator, custom validators)         │
│                                                                              │
│  SERVICE LAYER (Business Logic)                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • SysOperationServiceBase / Service classes                                │
│  • Single responsibility: one business process per service                  │
│  • Stateless, dependency-injected dependencies                              │
│  • Transaction boundaries (ttsBegin/Commit/Abort)                           │
│  • Calls repository/manager classes, not tables directly                    │
│                                                                              │
│  REPOSITORY/MANAGER LAYER (Data Access)                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Table-specific: CustTableManager, InventTableManager                     │
│  • Encapsulates query logic, caching, SysDa                                 │
│  • Returns DTOs/Contracts, not table buffers                                │
│  • Handles caching, query optimization                                      │
│                                                                              │
│  DOMAIN LAYER (Pure Business Logic)                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Pure functions: calculateTax, validateCredit, calculateDiscount          │
│  • No database, no framework dependencies                                   │
│  • 100% unit testable, property-based testable                              │
│  • Reusable across services, batch, forms, integrations                     │
│                                                                              │
│  CONTROLLER/ENTRY POINT LAYER                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • SysOperationServiceController (batch, sync, async)                       │
│  • Form event handlers (UI only)                                            │
│  • Custom Services (OData/JSON endpoints)                                   │
│  • Batch job classes (RunBaseBatch legacy only)                             │
│                                                                              │
│  CROSS-CUTTING CONCERNS (Composition)                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Logging/Audit (composition, not inheritance)                             │
│  • Telemetry (Application Insights wrapper)                                 │
│  • Security (declarative, XDS)                                              │
│  • Feature Flags (FeatureManagement)                                        │
│  • Retry/Circuit Breaker (policies, not inline code)                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 The "No Direct Table Access in Services" Rule

```xpp
// ❌ WRONG: Service accesses tables directly
class BadService extends SysOperationServiceBase
{
    public void run(BadContract _contract)
    {
        CustTable cust;
        select forUpdate cust where cust.AccountNum == _contract.accountNum();
        cust.CreditLimit += _contract.amount();
        cust.update(); // Direct table access in service
    }
}

// ✅ CORRECT: Service delegates to manager
class GoodService extends SysOperationServiceBase
{
    private CustTableManager custManager;
    
    public void new()
    {
        custManager = new CustTableManager(); // Dependency injection
    }
    
    public void run(GoodContract _contract)
    {
        this.custManager.adjustCreditLimit(_contract.accountNum(), _contract.amount());
    }
}

// Manager encapsulates data access
class CustTableManager
{
    public void adjustCreditLimit(CustAccount _account, real _amount)
    {
        CustTable cust;
        ttsBegin;
        select forUpdate cust where cust.AccountNum == _account;
        if (!cust) throw error("Customer not found");
        
        cust.CreditLimit += _amount;
        cust.update();
        ttsCommit;
    }
}
```

---

## 8. The Feature Flag Discipline

### 8.1 Every New Feature Behind a Flag

```xpp
// Feature Management integration
class FeatureGatedService extends SysOperationServiceBase
{
    public void run(FeatureContract _contract)
    {
        // Gate check at entry
        if (!FeatureManagement::isEnabled(FeatureNames::NewCreditProcessing))
        {
            throw error("Feature not enabled. Contact admin to enable 'NewCreditProcessing'.");
        }
        
        // ... rest of logic
    }
}

// Feature registration (run once via job)
static void RegisterFeatures(Args _args)
{
    FeatureManagement::registerFeature(
        FeatureNames::NewCreditProcessing,
        "New Credit Processing Engine",
        "Enables the new async credit limit processing with batch chunking.",
        false // Default OFF
    );
}
```

### 8.2 Feature Flag Lifecycle

| Phase | Flag State | Purpose |
|-------|------------|---------|
| **Development** | `DevOnly` / Off | Developers test in Tier-1 |
| **UAT** | On for UAT environment | Business validation |
| **Staging** | On for Staging | Performance/load testing |
| **Production Rollout** | Gradual (10% → 50% → 100%) | Canary deployment |
| **Stabilized** | On (remove flag after 2 releases) | Technical debt cleanup |

---

## 9. The Observability-First Mindset

### 9.1 What to Instrument (The Minimum)

```xpp
class ObservableService extends SysOperationServiceBase
{
    public void run(ObservableContract _contract)
    {
        var telemetry = TelemetryClient::getInstance();
        var stopwatch = System.Diagnostics.Stopwatch::StartNew();
        
        // 1. Request start
        telemetry.trackEvent("Service.Started", 
            Map.of("operation", "ProcessPayment", "correlationId", _contract.correlationId()));
        
        try
        {
            // ... business logic
            
            // 2. Success metrics
            stopwatch.Stop();
            telemetry.trackMetric("Service.Duration", stopwatch.ElapsedMilliseconds,
                Map.of("operation", "ProcessPayment", "status", "Success"));
            telemetry.trackEvent("Service.Completed", 
                Map.of("operation", "ProcessPayment", "durationMs", stopwatch.ElapsedMilliseconds));
        }
        catch (Exception::Error)
        {
            // 3. Failure metrics (critical!)
            stopwatch.Stop();
            telemetry.trackMetric("Service.Duration", stopwatch.ElapsedMilliseconds,
                Map.of("operation", "ProcessPayment", "status", "Failure"));
            telemetry.trackException(getException());
            throw;
        }
    }
}
```

### 9.2 The Four Golden Signals (Always Track)

| Signal | Metric Name | Alert Threshold |
|--------|-------------|-----------------|
| **Latency** | `Service.Duration` (p50, p95, p99) | p99 > 5s |
| **Traffic** | `Service.RequestsPerSecond` | Drop > 50% |
| **Errors** | `Service.ErrorRate` | > 1% |
| **Saturation** | `Batch.QueueDepth`, `SQL.DTU` | > 80% |

---

## 10. The Testing Pyramid for Production Confidence

### 10.1 Test Strategy by Layer

| Layer | Test Type | Coverage Target | Tools |
|-------|-----------|-----------------|-------|
| **Domain Logic** | Property-based + Unit | 95%+ | SysTest, custom generators |
| **Repository/Manager** | Integration (real DB) | 80% | SysTest + Test Data Factories |
| **Service Layer** | Integration (SysTest) | 70% | SysTest + Test Data Factories |
| **Controller/Entry** | Smoke/Contract | Critical paths | Postman/REST Client |
| **E2E Flows** | RSAT / Playwright | Critical business flows | RSAT |

### 10.2 Property-Based Testing for Invariants

```xpp
[SysTestMethod]
public void testCreditLimitInvariants()
{
    PropertyTest::check(
        "CreditLimit_NeverNegativeAfterAdjustment",
        1000,
        this,
        delegate boolean(List _input)
        {
            real startingLimit = _input.item(1);
            real adjustment = _input.item(2);
            
            // Simulate: start with limit, apply adjustment
            real result = startingLimit + adjustment;
            
            // Invariant: business rule says limit can't go below -10000 (overdraft)
            return result >= -10000;
        },
        delegate List()
        {
            List pair = new List(Types::Real);
            pair.addEnd(Generators::genReal(0, 1000000)); // Starting limit
            pair.addEnd(Generators::genReal(-50000, 50000)); // Adjustment
            return pair;
        }
    );
}
```

---

## 11. The Rollback & Recovery Discipline

### 11.1 Every Deploy Needs a Rollback Plan

```markdown
# Rollback Plan Template (include in PR)

## Feature: [Name]
## Flag: [FeatureManagement name]

## Rollback Trigger Conditions
- Error rate > 5% in first 30 min
- Latency p99 > 10s
- Data corruption detected
- Business reports incorrect results

## Rollback Steps
1. Disable Feature Flag: `FeatureManagement::disable(FeatureNames::X)`
2. Verify flag propagation (max 5 min)
3. Run cleanup job if data written: `[JobName]`
4. Verify system health (error rate, latency)
5. Notify stakeholders

## Data Cleanup (if applicable)
- Tables affected: [List]
- Cleanup job: [JobName/Script]
- Verification query: [SQL to verify clean]

## Rollback Validation
- [ ] Error rate < 0.1%
- [ ] Latency p99 < 2s
- [ ] Business smoke tests pass
- [ ] No data loss
```

---

## 12. The Senior Developer's Daily Practice

### 11.1 Code Review as Teaching

When reviewing, ask these questions (not just "looks good"):

1. **"What happens at 10x volume?"** → Forces set-based thinking
2. **"What happens if this runs twice?"** → Forces idempotency
3. **"What happens at 3 AM with no one watching?"** → Forces observability
4. **"What happens when Microsoft upgrades next month?"** → Forces extensibility
5. **"How do we turn this off in 30 seconds?"** → Forces feature flags
6. **"What does the auditor see?"** → Forces audit logging
6. **"Can a junior debug this at 3 AM?"** → Forces clarity/logging

### 11.2 The PR Description Template

```markdown
## What
[One sentence: what does this change?]

## Why
[Business context, ticket link]

## How
[Technical approach, pattern used, key files]

## Trade-offs
| Decision | Alternative | Chosen | Reason |
|----------|-------------|--------|--------|

## Production Hardening
- [ ] Transactions wrapped
- [ ] Deadlock handling
- [ ] Set-based SQL
- [ ] CacheLookup set
- [ ] Idempotency key
- [ ] Feature flag
- [ ] Telemetry
- [ ] Audit logging
- [ ] Feature flag default OFF

## Testing
- [ ] Unit tests (domain logic)
- [ ] Integration tests (flows)
- [ ] Property-based (invariants)
- [ ] Manual verification steps

## Rollback Plan
[Link to rollback doc or inline steps]

## Screenshots/Demo
[If UI change]
```

---

## 13. The Continuous Improvement Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE PRODUCTION-GRADE FEEDBACK LOOP                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DEPLOY → OBSERVE → LEARN → IMPROVE → DEPLOY                               │
│      │         │         │          │          │                             │
│      ▼         ▼         ▼          ▼          ▼                             │
│   Feature   Metrics   Post-mortem  Refactor   Feature Flag                   │
│   Flag ON   (Latency,  (What broke,  (Patterns,  Graduation                 │
│   Gradual   Errors,    why, how to  anti-patterns,  (Remove flag            │
│   Rollout   Saturation prevent)     tech debt)    after 2 releases)         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Quick Reference: The Production-Grade Cheat Sheet

### Before Writing Code
- [ ] Requirement decomposed (template filled)
- [ ] Pattern selected (decision tree)
- [ ] Feature flag registered (default OFF)
- [ ] Trade-offs documented

### While Coding
- [ ] Layered architecture (Contract → Service → Repository → Domain)
- [ ] No direct table access in services
- [ ] Transactions on every multi-table write
- [ ] Deadlock retry on every DB call
- [ ] Set-based SQL only
- [ ] Feature flag gate at entry
- [ ] Telemetry at boundaries
- [ ] Audit logging on critical ops

### Before Commit
- [ ] Code review checklist passed
- [ ] Unit tests > 90% domain coverage
- [ ] Integration tests for flows
- [ ] Property-based for invariants
- [ ] Rollback plan documented
- [ ] Feature flag default OFF
- [ ] XML comments on public APIs
- [ ] Trade-off rationale in PR

### After Deploy
- [ ] Feature flag gradual rollout
- [ ] Golden signals monitored
- [ ] Error budget tracked
- [ ] Post-mortem scheduled if incident
- [ ] Flag removal scheduled (2 releases)

---

## 15. Summary: The Production-Grade Mindset

> **Production-grade is not a checklist. It's a mindset.**
>
> It means every line of code is written with the 3 AM production incident in mind.
> It means choosing the boring, proven pattern over the clever new one.
> It means documenting *why* not just *what*.
> It means building in the ability to turn things off before turning them on.
> It means treating the database as a shared, contested resource.
> It means treating the user's time and data as sacred.
> It means the code you write today is the legacy someone maintains tomorrow.

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*