---
name: d365-cheatsheet
description: One-page D365 F&O quick reference card for printing (A4/Letter)
metadata:
  type: reference
---

# D365 F&O — Quick Reference Card

> **Glossary:** See the [Business Glossary](../00-foundations/d365-business-glossary.md) for term definitions.

> **Print this page** — Keep at your desk for instant syntax lookup. Covers 90% of daily X++ patterns.

---

## X++ Primitive Types

| Type | Example | Notes |
|------|---------|-------|
| `int` | `int i = 42;` | 32-bit |
| `int64` | `int64 r = 5637144576;` | RecId |
| `real` | `real p = 19.99;` | **Decimal precision** (safe for money) |
| `str` | `str s = "Hello";` | Unicode |
| `date` | `date d = today();` | No time |
| `utcdatetime` | `utcdatetime u = DateTimeUtil::utcNow();` | UTC |
| `enum` | `Status::Open` | Named constants |
| `guid` | `guid g = Guid::newGuid();` | GUID |
| `boolean` | `boolean b = true;` | true/false |
| `anytype` | `anytype a = 42;` | Universal |

---

## Variable Scope

```xpp
class MyClass
{
    static const Str APP_NAME = "MyApp";  // Class constant
    static int instanceCount = 0;         // Shared static
    
    CustTable _custTable;                 // Instance field
    boolean   _isValid;
    
    public void myMethod()
    {
        int localVar = 10;                // Method scope
        if (localVar > 0)
        {
            str blockVar = "block";       // Block scope (X++ supports this)
        }
    }
}
```

---

## Control Flow

```xpp
// If / else if / else
if (score >= 90) { info("A"); }
else if (score >= 80) { info("B"); }
else { info("C"); }

// Switch (int, str, enum only — no fall-through)
switch (status)
{
    case Status::Open:  info("Open");  break;
    case Status::Closed: info("Closed"); break;
    default: info("Unknown"); break;
}

// For loop
for (int i = 1; i <= 10; i++) { info(strFmt("%1", i)); }

// While select (idiomatic iteration)
while select custTable
    where custTable.Currency == "USD"
    order by custTable.AccountNum
{
    info(custTable.AccountNum);
}
```

---

## CRUD Patterns

```xpp
// Select (single record)
select firstonly custTable where custTable.AccountNum == "CUST-001";

// Select (specific fields — performance!)
select AccountNum, Name from custTable where custTable.Currency == "EUR";

// Exists join (check related without fetching)
boolean hasOrders = exists join salesTable
    where salesTable.CustAccount == custTable.AccountNum;

// Insert
custTable.clear();
custTable.AccountNum = "NEW-001";
custTable.Name = "New Customer";
custTable.insert();

// Update recordset (bulk — single SQL statement)
update_recordset custTable
    setting custTable.Currency = "USD"
    where custTable.Currency == "EUR";

// Delete from (bulk)
delete_from custTable where custTable.Blocked == CustVendorBlocked::All;

// Transaction (always wrap multi-table ops)
ttsBegin;
try
{
    custTable.insert();
    custGroup.insert();
    ttsCommit;
}
catch (Exception::Error)
{
    ttsAbort;
    error("Rolled back");
}
```

---

## Method Overriding

```xpp
// Table method — super() FIRST
public boolean validateWrite()
{
    boolean ret = super();
    if (ret && this.AccountNum == "") { ret = checkFailed("Account required"); }
    return ret;
}

// Extension (CoC) — next keyword
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Ext
{
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();
        if (ret && this.CustomField == "") { ret = checkFailed("Custom required"); }
        return ret;
    }
}
```

> **Rule:** `super()` first in base override; `next` in CoC. Use `checkFailed()` not `error()` in validation.

---

## Exception Handling

```xpp
try
{
    // ... code ...
}
catch (Exception::Deadlock)
{
    ttsAbort;
    // Retry logic here (max 3)
}
catch (Exception::Error)
{
    ttsAbort;
    error("Failed");
}
catch (Exception::Warning) { warning("Warn"); }
catch (Exception::Info) { info("Info"); }
```

---

## Common Classes

| Class | Purpose |
|-------|---------|
| `Global` | `info()`, `error()`, `warning()` |
| `SysTableLookup` | Build form lookups |
| `QueryRun` | Dynamic queries at runtime |
| `SrsReportDataProvider` | SSRS report data |
| `RunBaseBatch` | Legacy batch framework |
| `SysOperationServiceController` | Modern service framework |
| `NumberSeq` | Number sequences (concurrency-safe) |
| `DictTable`/`DictField` | Metadata reflection |

---

## Layer Hierarchy (Lowest → Highest)

```
SYS (Microsoft) → ISV (Partner) → VAR (Localization) → CUS (Customer) → USR (User)
```
> Higher layer wins. Never modify SYS directly — use Extensions.

---

## EDT Golden Rule

> **Never use base types directly in tables/forms.** Always use an EDT.

| Instead of | Use |
|------------|-----|
| `string 20` | `CustAccount` |
| `int` | `ItemId` (or custom EDT) |
| `real` | `AmountMST` |

---

## Performance Anti-Patterns

| ❌ Don't | ✅ Do |
|---------|-------|
| `select` inside `while` loop | `join` or `exists join` |
| `select *` (all fields) | `select FieldA, FieldB` |
| `update()` in loop | `update_recordset` |
| `InMemory` for large data | `TempDB` table type |
| Unbounded `crossCompany` | `crossCompany:['USMF','DEMF']` |
| Missing `CacheLookup` | Set `Found`/`EntireTable` on lookup tables |

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Table | PascalCase + Table | `CustTable` |
| EDT | PascalCase | `CustAccount` |
| Class | PascalCase + Suffix | `CustValidationService` |
| Table Extension | `TableName_Ext` | `CustTable_Ext` |
| Event Handler | `Table_Event` | `CustTable_inserted` |

---

## Key URLs (Verified 2026-11-22)

- **X++ Reference**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language
- **Tables**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/tables/tables
- **EDTs**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/edts/extended-data-types
- **CoC**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/chain-of-command
- **Event Handlers**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/event-handlers
- **Data Entities**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro
- **Batch**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-processing-overview
- **SysTest**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework

---

*Handbook: 35 Chapters • 17 Exercises • Updated Nov 2026*