---
name: d365-code-review-checklist
description: D365 F&O PR review checklist — naming, CoC usage, transactions, SQL patterns, security, tests
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Code Review Checklist

> **Usage:** Copy this checklist into PR description or use as reviewer guide. Check each item; comment with findings.

---

## 📋 Pre-Review Setup

- [ ] **Branch named correctly:** `feature/`, `bugfix/`, `hotfix/`, `release/` prefix
- [ ] **PR title follows convention:** `[Module] Short description (Ticket-123)`
- [ ] **Description includes:** What, Why, How to test, Screenshots (if UI)
- [ ] **Linked work item:** Azure DevOps / Jira ticket referenced
- [ ] **Build passes:** CI pipeline green (compile, BP checks, unit tests)
- [ ] **No merge conflicts:** Rebased on target branch

---

## 🏗️ Architecture & Design

### Extensibility
- [ ] **No over-layering:** Zero modifications to SYS/ISV layer objects
- [ ] **Extensions used:** `[ExtensionOf]` on tables, forms, classes, views
- [ ] **CoC over Event Handlers:** Chain of Command preferred for method augmentation
- [ ] **Event handlers static:** `[SubscribesTo]` methods are `static`
- [ ] **No `super()` in extensions:** Use `next` keyword in CoC
- [ ] **Extension naming:** `ClassName_Ext`, `TableName_Ext`, `FormName_Ext`

### Layer Compliance
- [ ] **Model in correct layer:** CUS for customer, VAR for localization, ISV for partner
- [ ] **No cross-layer dependencies:** CUS doesn't reference VAR/ISV internals
- [ ] **Dependencies declared:** `Descriptor/ModuleDescriptor.xml` lists all dependencies

---

## 💻 X++ Code Quality

### Naming Conventions
| Element | Convention | ✅ Check |
|---------|------------|----------|
| Tables | PascalCase + Table | `CustTable` |
| EDTs | PascalCase | `CustAccount` |
| Classes | PascalCase + Suffix | `CustValidationService` |
| Table Extensions | `TableName_Ext` | `CustTable_Ext` |
| Form Extensions | `FormName_Ext` | `CustTable_Ext` |
| Event Handlers | `Table_Event` | `CustTable_inserted` |
| Variables | camelCase with `_` prefix for fields | `_custTable`, `custAccount` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Macros | `#PascalCase` | `#CustValidation` |

### Data Types & EDTs
- [ ] **No base types in tables/forms:** Always use EDTs (`CustAccount` not `string 20`)
- [ ] **Real for money:** `AmountMST`, `AmountCur` — never `real` directly
- [ ] **Int64 for RecId:** `RecId`, `RefRecId` — never `int`
- [ ] **Enums over magic numbers:** `CustVendorBlocked::All` not `1`
- [ ] **Date/UtcDateTime:** `date` for dates, `utcDateTime` for timestamps

### Control Flow
- [ ] **No `select` in loops:** Use `join`, `exists join`, `notexists join`
- [ ] **`while select` for iteration:** Not `for` with `select`
- [ ] **`firstOnly` for single record:** Not `while select` with `break`
- [ ] **Specific field selection:** `select AccountNum, Name from custTable` not `select *`
- [ ] **Switch on int/str/enum only:** No fall-through (X++ doesn't support it)

---

## 🗄️ Database & SQL Patterns

### CRUD Operations
- [ ] **Bulk insert:** `insert_recordset` for multiple records
- [ ] **Bulk update:** `update_recordset` for mass updates
- [ ] **Bulk delete:** `delete_from` for mass deletes
- [ ] **Single record:** `insert()`, `update()`, `delete()` with `ttsBegin/commit`
- [ ] **Transactions wrapped:** All multi-table operations in `ttsBegin`/`ttsCommit`
- [ ] **`ttsAbort` in catch:** Every `catch` has `ttsAbort` before `error()`/`throw`

### Query Performance
- [ ] **Indexes exist:** Foreign keys and filter fields indexed
- [ ] **`CacheLookup` set:** `EntireTable`/`Found` on lookup/reference tables
- [ ] **No `crossCompany` unbounded:** Always `crossCompany:['USMF','DEMF']`
- [ ] **Temp tables typed:** `TempDB` for large data, `InMemory` for small (<1000 rows)
- [ ] **`exists join` for existence checks:** Not `select count()`
- [ ] **`join` vs `exists join`:** `join` when need fields, `exists join` for boolean

### Common Anti-Patterns ❌
| Don't Do | Do Instead |
|----------|------------|
| `while select` → `select` inside loop | `join` or `exists join` |
| `update()` in loop | `update_recordset` |
| `InMemory` for 10k+ rows | `TempDB` table type |
| `select *` | `select FieldA, FieldB` |
| `curExt()` in query range | `queryValue(currentCompany())` |
| `strFmt` in `where` clause | Parameterized query / `queryValue()` |

---

## 🔒 Security

### Access Control
- [ ] **Privileges declared:** New menu items have `NeededAccessLevel` and `NeededPermission`
- [ ] **No `SecurityUtil::hasPrivilege` in business logic:** Use declarative security on menu items
- [ ] **XDS policies:** Sensitive data has record-level security policies
- [ ] **No `skipSecurityCheck()`:** Never bypass security (except sysadmin tools with audit)
- [ ] **Role assignment tested:** Verify with non-admin user

### Data Protection
- [ ] **PII fields identified:** Personal data marked in documentation
- [ ] **No hardcoded secrets:** Connection strings, keys in Key Vault
- [ ] **Encryption at rest:** SQL TDE enabled (infra, not code)
- [ ] **Audit logging:** Critical operations logged (post, approve, delete master data)

---

## 🧪 Testing

### Unit Tests (SysTest)
- [ ] **Tests exist:** New functionality has test coverage
- [ ] **Test naming:** `test<MethodName>_<Scenario>` (e.g., `testPostInvoice_ValidVendor`)
- [ ] **AAA pattern:** Arrange, Act, Assert clearly separated
- [ ] **No hardcoded data:** Use test data factories
- [ ] **Transactional tests:** Each test rolls back (no manual cleanup)
- [ ] **Property-based tests:** For mathematical/logical invariants
- [ ] **Assert messages:** Clear failure descriptions

### Integration Tests
- [ ] **Cross-table scenarios tested:** Order-to-cash, procure-to-pay
- [ ] **Batch jobs tested:** Run in test environment, verify results
- [ ] **Data entities tested:** Import/export round-trip
- [ ] **Security tested:** Verify role access (positive & negative)

---

## 📦 Deployment & Operations

### Build & Package
- [ ] **Model version bumped:** `ModuleDescriptor.xml` version incremented
- [ ] **No build warnings:** Zero BP errors, zero compiler warnings
- [ ] **Deployable package builds:** `.axmodel` + `ModuleDescriptor.xml` valid
- [ ] **Database sync safe:** No destructive schema changes (column drops, type changes)

### Database Changes
- [ ] **New fields nullable or defaulted:** No NOT NULL without default
- [ ] **New indexes non-unique first:** Unique after data validated
- [ ] **Data migration script:** If transforming existing data
- [ ] **Rollback plan:** Documented for schema changes

### Configuration
- [ ] **Number sequences:** New sequences registered, formats documented
- [ ] **Parameters:** New module parameters have defaults
- [ ] **License codes:** Features gated by configuration keys
- [ ] **Feature management:** New features behind feature flags

---

## 📚 Documentation

### Code Documentation
- [ ] **XML comments:** Public classes/methods have `/// <summary>`
- [ ] **Complex logic commented:** Why, not what
- [ ] **TODO/FIXME tracked:** Linked to work items
- [ ] **Breaking changes noted:** In PR description and CHANGELOG

### User Documentation
- [ ] **Feature documented:** Wiki/ReadMe updated
- [ ] **Setup steps:** Configuration guide for admins
- [ ] **Troubleshooting:** Known issues and workarounds

---

## ✅ Reviewer Sign-Off

| Review Area | Reviewer | Status | Comments |
|-------------|----------|--------|----------|
| Architecture | | ☐ Pass / ☐ Needs Work | |
| X++ Quality | | ☐ Pass / ☐ Needs Work | |
| Database/SQL | | ☐ Pass / ☐ Needs Work | |
| Security | | ☐ Pass / ☐ Needs Work | |
| Testing | | ☐ Pass / ☐ Needs Work | |
| Deployment | | ☐ Pass / ☐ Needs Work | |
| Documentation | | ☐ Pass / ☐ Needs Work | |

**Overall:** ☐ **Approved** | ☐ **Approved with Comments** | ☐ **Request Changes**

---

## 🛠️ Quick Commands for Reviewers

```bash
# Check for over-layering (should return empty)
grep -r "super(" --include="*.xpp" | grep -v "ExtensionOf" | grep -v "next"

# Find select in loops
grep -B2 -A2 "while select" --include="*.xpp" | grep -A2 "select "

# Find missing ttsBegin
grep -r "\.insert()\|\.update()\|\.delete()" --include="*.xpp" | grep -v "ttsBegin" -B5

# Check for hardcoded strings in where clauses
grep -r "where.*==.*\"" --include="*.xpp"

# Find direct SQL usage
grep -r "Statement\|ResultSet\|Connection" --include="*.xpp"

# Check extension naming
ls -1 *.xpp | grep -v "_Ext\.xpp$" | grep -v "^[A-Z]" # Non-PascalCase files
```

---

## 📖 References

- [Microsoft X++ Best Practices](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-best-practices)
- [Extensibility Patterns](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensibility-home-page)
- [Performance Guidelines](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/performance-testing)
- [Security Development](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/security-development)

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*