---
name: d365-beginner-faq
description: 50 common beginner questions about D365 F&O, X++, SQL, OOP, and development with clear answers
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Beginner FAQ

> **50 questions every beginner asks** — organized by topic. Search (Ctrl+F) for your question.

---

## D365 F&O Basics (Q1-Q10)

### Q1: What does "F&O" stand for?
**Finance & Operations** — the ERP module of Dynamics 365. Formerly "Dynamics AX."

### Q2: Is D365 F&O the same as Dynamics AX?
**Evolution, not replacement.** AX 2012 was on-prem; F&O is cloud SaaS. Code upgrade path exists (see migration guide).

### Q3: Do I manage servers?
**No.** Microsoft manages Azure infrastructure (AOS, SQL, updates). You get a Tier-1 dev VM — that's it.

### Q4: What's a "Tier-1" environment?
Your personal **development sandbox** with full admin rights. Free with LCS project. One per developer.

### Q5: What's LCS?
**Lifecycle Services** — Microsoft's portal for environment management, deployments, monitoring, support tickets.

### Q6: How often does Microsoft update F&O?
**Monthly quality updates** (auto-applied), **biannual feature updates** (April/Oct, scheduled via LCS).

### Q7: Can I customize standard Microsoft code?
**No over-layering.** Use **Extensions** (Chain of Command, Event Handlers) only. Direct edits break on update.

### Q8: What language is X++?
**C#-like, runs on .NET CLR.** Compiles to IL. Similar syntax to C# but with SQL-like data access.

### Q9: Do I need to know C#?
**Helpful but not required.** X++ is similar. .NET interop lets you call C# libraries when needed.

### Q10: What's the AOT?
**Application Object Tree** — metadata repository (tables, forms, classes, etc.) stored as files in `PackagesLocalDirectory`.

---

## X++ Language (Q11-Q20)

### Q11: What's the difference between `select` and `while select`?
- `select` → single row (or `firstOnly`)
- `while select` → iterates multiple rows

### Q12: When do I use `insert_recordset` vs `insert()`?
- `insert()` → single record
- `insert_recordset` → bulk (single SQL statement, **much faster**)

### Q13: What's `ttsBegin` / `ttsCommit` / `ttsAbort`?
**Transaction control.** `ttsBegin` starts, `ttsCommit` saves, `ttsAbort` rolls back. **Always wrap multi-table ops.**

### Q14: Why `checkFailed()` not `error()` in validation?
`checkFailed()` returns `false` (lets framework handle), `error()` throws exception (breaks flow).

### Q15: What's the difference between `super()` and `next`?
- `super()` → call parent method in **override** (base class)
- `next` → call next in **Chain of Command** (extension)

### Q16: What are EDTs and why use them?
**Extended Data Types** — typed aliases with metadata (labels, help text, relations). **Never use base types in tables/forms.**

### Q17: What's `real` vs `float`?
**`real` = decimal precision** (safe for money). `float`/`double` = binary floating point (rounding errors).

### Q18: How do I debug X++?
**VS Debugger** attached to AOS process. Breakpoints, Watch, Call Stack. Enable "Just My Code" = **Off**.

### Q19: What's `forUpdate` in select?
**Pessimistic locking** — locks row for update. Prevents lost updates in transactions.

### Q20: What's the difference between `TempDB` and `InMemory` tables?
| | TempDB | InMemory |
|---|--------|----------|
| **Persists** | Yes (tempdb) | No (memory only) |
| **Indexes** | Yes | No |
| **Size** | Large (10k+ rows) | Small (<1k rows) |
| **Scope** | Session/Global | Session only |

---

## SQL & Database (Q21-Q30)

### Q21: Does X++ run SQL directly?
**X++ compiles to IL** → AOS generates parameterized SQL. You write `while select`, AOS runs `SELECT`.

### Q22: What's the N+1 problem?
```xpp
while select custTable  // 1 query
{
    select salesTable where salesTable.CustAccount == custTable.AccountNum;  // N queries!
}
```
**Fix:** Use `join` or `exists join` (1 query total).

### Q23: When do I use `exists join` vs `join`?
- `exists join` → only need **boolean** (exists?)
- `join` → need **fields** from joined table

### Q24: What's `CacheLookup` and which should I use?
| Table Type | CacheLookup |
|------------|-------------|
| Setup/Reference (small, static) | `EntireTable` |
| Master data (PK lookups) | `Found` |
| Transactional | `NotInTTS` (default) |
| High churn | `None` |

### Q25: How do I find slow queries?
**Trace Parser** (capture + analyze) or **SQL Query Store** (`sys.query_store_*` DMVs).

### Q26: What's a deadlock and how to handle?
Two sessions lock resources in opposite order. **Catch `Exception::Deadlock`, retry max 3x with backoff.**

### Q27: What's `update_recordset`?
**Bulk UPDATE** — single SQL statement. Replaces loop with `update()`.

### Q28: How do I add an index?
**AOT:** Table → Indexes → New Index → add fields. Set `IncludedColumns` for covering index.

### Q29: What's a "clustered index"?
**Data stored in index order.** Every table has one (PK or RecId). Only one per table.

### Q30: Can I write raw SQL in X++?
**No.** Use `select` / `QueryRun` / Data Entities. Direct SQL (`Statement`, `ResultSet`) is deprecated.

---

## OOP & Patterns (Q31-Q40)

### Q31: What's the difference between a class and an object?
- **Class** = blueprint (definition)
- **Object/Instance** = created from class (`new MyClass()`)

### Q32: What's inheritance in X++?
`class Child extends Parent` — child gets parent's fields/methods. Use `super()` to call parent.

### Q33: What's an interface?
**Contract only** — method signatures, no implementation. Class `implements` interface. Multiple allowed.

### Q34: What's polymorphism?
Same method call, different behavior based on actual object type. Base variable, derived instance.

### Q35: What's encapsulation?
**Hide internals** — `private` fields, public getters/setters. Validate in setters.

### Q36: What's the Chain of Command (CoC)?
**Extension pattern** — `[ExtensionOf]` class, `next methodName()` calls base/next extension.

### Q37: What's the difference between CoC and Event Handlers?
| | CoC | Event Handler |
|---|-----|---------------|
| **Flow control** | Yes (`next`) | No |
| **Access `this`** | Yes | No (args only) |
| **Return value** | Can modify | Read only (post) |
| **Use for** | Modify behavior | React to events |

### Q38: What's the Factory Pattern?
`static MyClass create(Type _type)` — returns different subclass based on input.

### Q39: What's Dependency Injection?
Service depends on **interface**, not concrete class. Pass implementation via constructor.

### Q40: Composition over Inheritance?
**Prefer composition** for cross-cutting concerns (logging, caching). Avoid deep inheritance trees.

---

## Development Workflow (Q41-Q50)

### Q41: How do I create a deployable package?
**Build pipeline** → compiles → `.axmodel` + `ModuleDescriptor.xml` → LCS Asset Library → Deploy.

### Q42: What's the build pipeline?
Azure DevOps YAML: Restore → Compile → BP Check → Unit Tests → Package → Artifact.

### Q43: What's "Synchronize Database"?
Creates/updates SQL tables from AOT metadata. Run after model changes.

### Q44: How do I debug a batch job?
**Set breakpoint** in service class → Debug → Attach to **Batch** process (not AOS).

### Q45: What's a Data Entity?
**Business document view** (header + lines) for import/export/OData. `IsPublic = Yes` enables OData.

### Q46: What's DMF?
**Data Management Framework** — import/export, recurring jobs, staging tables, change tracking.

### Q47: What's SysOperation?
**Modern batch framework** — 3 classes: Contract (data), Service (logic), Controller (entry point).

### Q48: How do I test my code?
**SysTest** — `[SysTestCase]`, `[SysTestMethod]`, transactional (auto-rollback). Aim >80% coverage.

### Q49: What's the security hierarchy?
**Role → Duties → Privileges → Permissions** (Table/MenuItem access). XDS for record-level.

### Q50: Where do I get help?
- **Microsoft Learn** — official docs
- **Dynamics 365 Community** — forums
- **Stack Overflow** — tag `dynamics-365-finance-operations`
- **GitHub** — samples, issues

---

## Quick Reference Card

| I Need To... | Go To |
|--------------|-------|
| Set up environment | `d365-environment-setup.md` |
| Learn ERP basics | `d365-foundations.md` |
| Learn OOP for X++ | `d365-oop-primer.md` + `d365-oop-exercises.md` |
| Learn SQL for X++ | `d365-sql-primer.md` + `d365-sql-exercises.md` |
| Understand business terms | `d365-business-glossary.md` |
| See role workflows | `d365-role-day-in-life.md` |
| Compare ERPs | `d365-erp-comparison.md` |
| Practice OOP | `d365-oop-exercises.md` |
| Practice SQL | `d365-sql-exercises.md` |
| Track progress | `d365-learning-path-tracker.md` |
| Test knowledge | `d365-study-guide-quizzes.md` |
| Flashcards | `d365-flashcards.md` |
| Pair program | `d365-pair-programming-prompts.md` |
| Watch videos | `d365-video-links.md` |

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*