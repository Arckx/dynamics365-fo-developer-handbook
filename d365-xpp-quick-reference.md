---
name: d365-xpp-quick-reference
description: X++ syntax cheat sheet covering data types, CRUD patterns, control flow, classes, exceptions, common mistakes, and naming conventions
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-10T17:26:07.024Z
---

# X++ Quick Reference Card

> **D365 Finance & Operations — X++ Syntax at a Glance**
> Keep this open while coding. For full details, refer to the Desktop Guide (Chapters 1–2).

---

## Data Types

### True Primitive Types

Per Microsoft's official X++ primitive type list — these are the built-in scalar types:

| Type | Example | Notes |
|---|---|---|
| `int` | `int i = 5;` | 32-bit signed integer |
| `int64` | `int64 recId = 5637144576;` | 64-bit — used for `RecId` |
| `real` | `real price = 19.99;` | 128-bit fixed-point decimal internally — safe for monetary values via EDTs like `AmountMST`; does NOT have the rounding problems that IEEE-754 doubles have in languages like C#/Java |
| `str` | `str name = "Customer";` | Unicode string |
| `boolean` | `boolean flag = true;` | `true` / `false` |
| `date` | `date d = today();` | No time component |
| `utcdatetime` | `utcdatetime udt = DateTimeUtil::utcNow();` | UTC datetime |
| `timeOfDay` | `timeOfDay t = 120000;` | Seconds since midnight (int) |
| `enum` | `Status::New` | Named constant set |
| `AnyType` | `AnyType val = 42;` | Universal type — use with care |
| `guid` | `guid g = Guid::newGuid();` | Globally unique identifier |

### Composite Types

| Type | Example | Notes |
|---|---|---|
| `container` | `container c = [1, "two", 3.0];` | Typed ordered list — the only composite primitive in X++ |

### Non-Primitive "Types" (clarification)

These are **not** primitive or composite data types — they are language constructs that serve different purposes:

| Type | Example | What It Actually Is |
|---|---|---|
| `record` | `CustTable custTable;` | A **table buffer declaration** — a variable that holds a row from a data entity (table), not a standalone data type |
| `class` | `MyService service;` | A **class instance reference** — declares a variable that will hold an object, not a scalar value |
| `void` | `public void doSomething()` | The **absence of a return type** — indicates a method returns nothing; it is not a value type |

---

## Variable Declaration

```xpp
// Standard declaration
int     i = 0;
str     s = "Hello";
real    r = 123.45;
date    d = today();
boolean flag = true;

// Static constant — class level
static const Str AppName = "MyApp";

// Static variable — shared across instances
static int instanceCount = 0;

// Instance variable — each object has its own copy
CustTable _custTable;
boolean   _isValid;
```

---

## Control Flow

### If / Else If / Else
```xpp
if (score >= 90)
{
    info("Grade: A");
}
else if (score >= 80)
{
    info("Grade: B");
}
else
{
    info("Grade: C");
}
```

### Switch (int, str, enum only)
```xpp
switch (status)
{
    case Status::New:
        info("New record");
        break;

    case Status::Approved:
        info("Already approved");
        break;

    default:
        info("Unknown status");
        break;
}
```

### For Loop
```xpp
for (int i = 1; i <= 10; i++)
{
    info(strFmt("Iteration %1", i));
}

// Iterate a container
container numbers = [10, 20, 30];
for (int i = 1; i <= conLen(numbers); i++)
{
    info(strFmt("Element %1 = %2", i, conPeek(numbers, i)));
}
```

### While Select — The Idiomatic X++ Iteration
```xpp
// Basic
CustTable custTable;
while select custTable
{
    info(custTable.AccountNum);
}

// With where clause
while select custTable
    where custTable.Currency == "USD"
{
    info(custTable.AccountNum);
}

// With ordering
while select custTable
    order by custTable.AccountNum
{
    info(custTable.AccountNum);
}

// Firstonly — stops after first match
while select firstonly custTable
    where custTable.AccountNum == "CUST-001"
{
    info(custTable.Name);
}
```

### Do While
```xpp
int i = 1;
do
{
    info(strFmt("Value: %1", i));
    i++;
}
while (i <= 5);
```

---

## CRUD Operations

### Select
```xpp
CustTable custTable;

// Simple select
select custTable
    where custTable.AccountNum == "CUST-001";

// Firstonly — optimized
select firstonly custTable
    where custTable.AccountNum == "CUST-001";

// Specific fields only
select custTable.Name, custTable.Phone();

// Exists join — check for related records without retrieving them
boolean hasVendor = exists join vendTable
    where vendTable.AccountNum == custTable.AccountNum;
```

### Insert
```xpp
CustTable custTable;
custTable.clear();
custTable.AccountNum = "CUST-NEW-001";
custTable.Name = "New Customer";
custTable.insert();
```

### Update — `update_recordset` (preferred)
```xpp
CustTable custTable;
update_recordset custTable
    setting custTable.Phone = "+1-555-0200"
    where custTable.AccountNum == "CUST-NEW-001";
```

### Delete — `delete_from`
```xpp
CustTable custTable;
delete_from custTable
    where custTable.AccountNum == "CUST-NEW-001";
```

### Transactions
```xpp
ttsBegin;
try
{
    CustTable custTable;
    custTable.clear();
    custTable.AccountNum = "CUST-TRANS-001";
    custTable.Name = "Transactional Customer";
    custTable.insert();

    CustGroup custGroup;
    custGroup.clear();
    custGroup.GroupName = "TRANSACTIONAL";
    custGroup.insert();

    ttsCommit;
}
catch (Exception::Error)
{
    ttsAbort;
    error("Transaction failed — rolled back.");
}
```

---

## Method Overriding & `super()`

```xpp
// In a table — overriding validateWrite
public boolean validateWrite()
{
    boolean ret;

    ret = super();  // Always call super() first in table methods

    // Custom validation
    if (this.AccountNum == "")
    {
        ret = false;
        error("Account number cannot be empty.");
    }

    return ret;
}
```

### Chain of Command (`next` keyword)
```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Extension
{
    public boolean validateWrite()
    {
        boolean ret;

        ret = next validateWrite();  // Call next handler in the chain

        // Custom validation
        if (this.AccountNum == "")
        {
            ret = false;
            error("Account number cannot be empty.");
        }

        return ret;
    }
}
```

---

## Exception Handling

### Exception Types
| Type | When |
|---|---|
| `Exception::Error` | General runtime error |
| `Exception::Warning` | Non-fatal warning |
| `Exception::Info` | Informational message |
| `Exception::Broken` | Object in an invalid state (e.g., deleted record) |
| `Exception::Deadlock` | SQL deadlock — retry |
| `Exception::DuplicateKey` | Unique index violation |

### Try / Catch Pattern
```xpp
try
{
    CustTable custTable;
    select firstonly custTable
        where custTable.AccountNum == "NON-EXISTENT";

    if (!custTable)
    {
        throw error("Customer not found.");
    }
}
catch (Exception::Error)
{
    error("An error occurred.");
}
catch (Exception::Warning)
{
    warning("A warning occurred.");
}
catch (Exception::Info)
{
    info("Informational message.");
}
```

### Deadlock Retry Pattern
```xpp
int retryCount = 0;
boolean success = false;

while (!success && retryCount < 3)
{
    ttsBegin;
    try
    {
        // ... your database operations ...
        ttsCommit;
        success = true;
    }
    catch (Exception::Deadlock)
    {
        ttsAbort;
        retryCount++;
        info(strFmt("Deadlock — retry %1 of 3", retryCount));
    }
    catch (Exception::Error)
    {
        ttsAbort;
        error("A non-deadlock error occurred.");
        break;
    }
}
```

---

## Classes & Objects

### Class Declaration
```xpp
/// <summary>Summary of what this class does.</summary>
class MyService
{
    // Static constant
    static const Str DefaultPrefix = "SRV";

    // Instance variables
    CustTable _custTable;
    boolean   _isValid;

    // Constructor
    public MyService(CustTable _custTable)
    {
        this._custTable = _custTable;
        this._isValid = false;
    }

    // Public method
    public boolean validate()
    {
        // ... validation logic ...
        return this._isValid;
    }

    // Public static method
    public static boolean isAccountValid(str _accountNum)
    {
        return (_accountNum != '' && strLen(_accountNum) >= 3);
    }
}
```

### Inheritance
```xpp
// Base class
class BasePaymentService
{
    public void pay(CustTable _custTable, Amount _amount)
    {
        info(strFmt("Processing payment of %1 for %2", _amount, _custTable.AccountNum));
    }
}

// Derived class
class CreditCardPaymentService extends BasePaymentService
{
    public void pay(CustTable _custTable, Amount _amount)
    {
        this.validateCard();
        super::pay(_custTable, _amount);
        this.logTransaction();
    }
}
```

### Abstract Classes & Interfaces
```xpp
// Abstract class
abstract class AbstractReportGenerator
{
    public abstract void generate();

    public void logGeneration()
    {
        info("Report generation started.");
    }
}

// Interface
interface IExportable
{
    void exportToFile(str _filePath);
    str getExportFormat();
}

// Implementing both
class CsvReportGenerator extends AbstractReportGenerator implements IExportable
{
    public void generate()
    {
        this.logGeneration();
        // CSV logic
    }

    public void exportToFile(str _filePath)
    {
        // Write CSV
    }

    public str getExportFormat()
    {
        return "CSV";
    }
}
```

---

## Common Patterns

### Container Operations
```xpp
container c = [1, "two", 3.0];
int       len = conLen(c);          // 3
int       first = conPeek(c, 1);    // 1
container c2 = conIns(c, 2, "inserted");  // [1, "inserted", "two", 3.0]
```

### String Formatting
```xpp
info(strFmt("Hello, %1. Your balance is %2.", name, balance));
info(strFmt("Date: %1", date2str(today(), 123, 2, 2, 2, 4, DateFlags::None)));
```

### Date/Time Utilities
```xpp
date     d = today();
date     d2 = str2date("2026-01-15", 123);
int      year = year(d);
int      month = monthOfYear(d);
utcdatetime udt = DateTimeUtil::utcNow();
str      formatted = DateTimeUtil::toStr(udt);
```

### File I/O
```xpp
TextIO io = new TextIO(@"C:\temp\output.txt", "w");
io.write("Hello, file!");
io.close();
```

### Infolog Messages
```xpp
info("Informational message");      // Blue
warning("Warning message");         // Yellow
error("Error message");             // Red
```

---

## Key System Classes

| Class | Purpose |
|---|---|
| `Global` | Static utility methods (`Global::info()`, `Global::warning()`, `Global::error()`) |
| `SysTableLookup` | Build lookups for form controls |
| `QueryRun` | Execute a `Query` at runtime — the preferred D365 F&O approach for dynamic queries |
| `SrsReportDataProvider` | Data provider for SSRS reports |
| `RunBase` | Framework for batchable processes |
| `RunBaseBatch` | Batch execution framework |
| `SysOperationServiceController` | Modern service operation framework — replaces RunBase for service-based integrations |
| `NumberSeq` | Number sequence generation (safe under concurrency) |
| `DictTable` / `DictField` / `DictEnum` | Runtime table/field/enum metadata reflection |
| `Exception` | Exception type enum (`Exception::Error`, `Exception::Broken`, `Exception::Deadlock`, etc.) |

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| `select` inside a `while` loop (N+1 queries) | Use `exists join` or `while select` |
| Forgetting `super()` in overridden methods | Always call `super()` first in table methods |
| Using `update` instead of `update_recordset` in loops | Use `update_recordset` for bulk updates |
| Declaring variables inside `if` blocks and expecting them outside | Declare at method scope |
| Not using `ttsBegin`/`ttsCommit` for multi-table inserts | Wrap related inserts in a transaction |
| Ignoring deadlocks | Implement retry logic with `catch (Exception::Deadlock)` |
| Using primitive types instead of EDTs | Always use EDTs for consistency and validation |
| Manual `RecId` assignment | Let the system auto-generate `RecId` |
| Using `real` without an EDT for monetary values | `real` is X++'s built-in real-type and is 128-bit fixed-point (NOT IEEE-754 binary float), so it's precision-safe — but you should still always use a monetary EDT (e.g. `AmountMST`, `AmountCur`) to carry display length, validation, and currency context rather than a bare `real` field |

---

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Table | `CustTable`, `VendTable` | PascalCase + `Table` suffix |
| EDT | `CustAccount`, `VendAccount` | PascalCase, no suffix |
| Class | `CustValidationService` | PascalCase + `Service`/`Handler`/`Extension` |
| Table extension | `[ExtensionOf(tableStr(CustTable))]` | `final` class, `ExtensionOf` attribute |
| EDT extension | `[ExtendsWithEDT('AddressCountryRegionId')]` | Static method with `_Ext` suffix |
| Event handler | `CustTable_inserted` | `TableName_EventName` |
| Delegate | `modifyPrice` | Method name on the delegate publisher |

---

## Key Microsoft Learn URLs

- [D365 F&O Developer Documentation](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/)
- [X++ Language Reference](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/xpp-language-reference)
- [Tables and Fields](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/tables/tables)
- [Extended Data Types](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/edts/extended-data-types)
- [Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/chain-of-command)
- [Event Handlers](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/event-handlers)
- [Data Entities](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro)
- [SSRS Reporting](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-reporting/)
- [Security Model](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/security-operations/)
- [LCS & DevOps](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-devenv/lifecycle-services-lcs)
