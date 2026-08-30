---
name: d365-xpp-exercises
description: 17 hands-on X++ exercises with worked solutions covering CRUD, CoC, delegates, event handlers, transactions, error handling, and more
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-04T20:33:24.598Z
---

# X++ Practice Exercises with Solutions

> **Hands-on coding practice for D365 F&O developers.**
> Each exercise has a problem statement, hints, and a worked solution.
> Try to solve each one yourself before reading the solution.

---

## Exercise 1 — Variable Declaration and Type Casting

### Problem

Write a method that takes a `container` with three elements (an `int`, a `str`, and a `real`) and prints each element to the Infolog with its type name.

### Hints
- Use `conLen()` to get the container length
- Use `conPeek()` to retrieve elements by position (1-based)
- Use `typeid()` to get the type name of a variable
- Use `info()` to write to the Infolog

### Solution

```xpp
static void exercise1_containerTypes(Args _args)
{
    container c = [42, "Hello", 3.14];
    int     i;
    str     s;
    real    r;

    // Element 1: int
    i = conPeek(c, 1);
    info(strFmt("Element 1: value=%1, type=%2", i, typeid(i)));

    // Element 2: str
    s = conPeek(c, 2);
    info(strFmt("Element 2: value=%1, type=%2", s, typeid(s)));

    // Element 3: real
    r = conPeek(c, 3);
    info(strFmt("Element 3: value=%1, type=%2", r, typeid(r)));
}
```

**Expected Infolog output:**
```
Element 1: value=42, type=int
Element 2: value=Hello, type=str
Element 3: value=3.14, type=real
```

---

## Exercise 2 — While Select with Filtering

### Problem

Write a job that selects all customers whose `Currency` is "USD" and whose `GroupName` is "CORP", and prints their `AccountNum` and `Name` to the Infolog.

### Hints
- Use `while select` with a `where` clause combining two conditions with `&&`
- Remember that `CustTable` has fields `AccountNum`, `Name`, `Currency`, and `GroupName`

### Solution

```xpp
static void exercise2_usdCorpCustomers(Args _args)
{
    CustTable custTable;
    int count = 0;

    while select custTable
        where custTable.Currency == "USD"
           && custTable.GroupName == "CORP"
    {
        info(strFmt("Account: %1 — Name: %2", custTable.AccountNum, custTable.Name));
        count++;
    }

    info(strFmt("Total customers found: %1", count));
}
```

---

## Exercise 3 — Update Recordset (Bulk Update)

### Problem

Write a job that updates the `Currency` field to "EUR" for all customers whose `GroupName` is "TEMP". Use `update_recordset` — do not use a `while select` loop with `.update()`.

### Hints
- `update_recordset` generates a single SQL UPDATE statement
- The `setting` clause specifies which field to update and to what value
- The `where` clause filters which records to update

### Solution

```xpp
static void exercise3_bulkCurrencyUpdate(Args _args)
{
    CustTable custTable;
    int updatedCount;

    // Count how many records will be affected
    select countRecId from custTable
        where custTable.GroupName == "TEMP";
    updatedCount = custTable.countRecId;

    // Perform the bulk update
    update_recordset custTable
        setting custTable.Currency = "EUR"
        where custTable.GroupName == "TEMP";

    info(strFmt("Updated %1 customer(s) to EUR", updatedCount));
}
```

---

## Exercise 4 — Transaction with Error Handling

### Problem

Write a job that inserts a new customer and a corresponding customer group record in a single transaction. If either insert fails, roll back the entire transaction and display an error message.

### Hints
- Use `ttsBegin` / `ttsCommit` / `ttsAbort`
- Wrap the inserts in a `try`/`catch` block
- Call `ttsAbort` in the catch block

### Solution

```xpp
static void exercise4_transactionalInsert(Args _args)
{
    CustTable    custTable;
    CustGroup    custGroup;
    str          newAccountNum = "CUST-TRANS-001";

    ttsBegin;
    try
    {
        // Insert the customer group first (parent)
        custGroup.clear();
        custGroup.GroupName = "TRANSACTIONAL";
        custGroup.insert();

        // Insert the customer (child)
        custTable.clear();
        custTable.AccountNum = newAccountNum;
        custTable.Name = "Transactional Customer";
        custTable.GroupName = "TRANSACTIONAL";
        custTable.Currency = "USD";
        custTable.insert();

        ttsCommit;
        info("Transaction committed — both records inserted successfully.");
    }
    catch (Exception::Error)
    {
        ttsAbort;
        error("Transaction failed — both records rolled back.");
    }
}
```

---

## Exercise 5 — Method Overriding with `super()`

### Problem

Create a table extension on `CustTable` that overrides `validateWrite()`. The extension should:
1. Call `super()` first
2. Add a validation that the `AccountNum` field must start with "CUST-"
3. Return `false` and display an error if the validation fails

### Hints
- Use `[ExtensionOf(tableStr(CustTable))]` attribute
- Use `next validateWrite()` to call the base method
- Use `strStartsWith()` to check the prefix

### Solution

```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Extension
{
    public boolean validateWrite()
    {
        boolean ret;

        // Call the base class validation first
        ret = next validateWrite();

        // Custom validation: AccountNum must start with "CUST-"
        if (ret && !strStartsWith(this.AccountNum, "CUST-"))
        {
            ret = false;
            error(strFmt("Account number '%1' must start with 'CUST-'.", this.AccountNum));
        }

        return ret;
    }
}
```

---

## Exercise 6 — Exception Handling with Deadlock Retry

### Problem

Write a method that attempts to update a customer record, with deadlock retry logic. The method should retry up to 3 times on deadlock, and display a message for each retry attempt.

### Hints
- Use a `while` loop with a `retryCount` counter
- Catch `Exception::Deadlock` specifically
- Call `ttsAbort` before retrying
- Use `info()` to log retry attempts

### Solution

```xpp
static void exercise6_deadlockRetry(str _accountNum)
{
    CustTable custTable;
    int       retryCount = 0;
    boolean   success = false;

    while (!success && retryCount < 3)
    {
        ttsBegin;
        try
        {
            select firstonly custTable
                where custTable.AccountNum == _accountNum;

            if (custTable)
            {
                custTable.Name = strFmt("Updated Name %1", retryCount + 1);
                custTable.update();

                ttsCommit;
                success = true;
                info(strFmt("Customer updated successfully on attempt %1.", retryCount + 1));
            }
            else
            {
                ttsCommit;
                info("Customer not found.");
                success = true;  // Not an error, just not found
            }
        }
        catch (Exception::Deadlock)
        {
            ttsAbort;
            retryCount++;
            info(strFmt("Deadlock detected — retry %1 of 3", retryCount));
        }
        catch (Exception::Error)
        {
            ttsAbort;
            error("A non-deadlock error occurred.");
            break;
        }
    }

    if (!success)
    {
        error("Failed to update customer after 3 attempts.");
    }
}
```

---

## Exercise 7 — Class with Constructor and Validation Methods

### Problem

Create a class called `VendPaymentValidator` that:
1. Has a constructor accepting a `VendTable` record
2. Has a `validate()` method that checks:
   - `AccountNum` is not empty
   - `Name` is not empty
   - The vendor's `Currency` exists in `CurrencyTable`
3. Has a static method `isCurrencyValid(str _currencyCode)` that returns a boolean
4. Returns `true` from `validate()` only if all checks pass

### Hints
- Use private helper methods for each validation rule
- Use `select firstonly` against `CurrencyTable` for the currency check
- Use `this.` to access instance variables from instance methods

### Solution

```xpp
class VendPaymentValidator
{
    VendTable _vendTable;
    boolean   _isValid;

    public VendPaymentValidator(VendTable _vendTable)
    {
        this._vendTable = _vendTable;
        this._isValid = false;
    }

    public boolean validate()
    {
        if (this.validateAccountNum()
         && this.validateName()
         && this.validateCurrency())
        {
            this._isValid = true;
        }
        return this._isValid;
    }

    private boolean validateAccountNum()
    {
        if (this._vendTable.AccountNum == '')
        {
            error("Vendor account number cannot be empty.");
            return false;
        }
        return true;
    }

    private boolean validateName()
    {
        if (this._vendTable.Name == '')
        {
            error("Vendor name cannot be empty.");
            return false;
        }
        return true;
    }

    private boolean validateCurrency()
    {
        CurrencyTable currencyTable;
        boolean       found;

        select firstonly currencyTable
            where currencyTable.CurrencyCode == this._vendTable.Currency;

        found = currencyTable.RecId != 0;

        if (!found)
        {
            error(strFmt("Currency '%1' is not valid.", this._vendTable.Currency));
        }

        return found;
    }

    public static boolean isCurrencyValid(str _currencyCode)
    {
        CurrencyTable currencyTable;
        boolean       found;

        select firstonly currencyTable
            where currencyTable.CurrencyCode == _currencyCode;

        found = currencyTable.RecId != 0;
        return found;
    }
}
```

**Usage:**
```xpp
VendTable vendTable = VendTable::find("VEND-001");
VendPaymentValidator validator = new VendPaymentValidator(vendTable);

if (validator.validate())
{
    info("Vendor is valid for payment processing.");
}
else
{
    warning("Vendor validation failed — check the Infolog.");
}
```

---

## Exercise 8 — Inheritance and Polymorphism

### Problem

Create a base class `BaseDiscountCalculator` with a method `calculateDiscount(Amount _amount)` that returns a 0% discount. Then create two derived classes:
- `GoldDiscountCalculator` — returns 10% discount
- `PlatinumDiscountCalculator` — returns 20% discount

Write a job that creates each calculator, calls `calculateDiscount()` with an amount of 1000, and prints the result.

### Hints
- Use `extends` for inheritance
- Override the `calculateDiscount` method in each derived class
- Use `super::` if you want to call the base implementation

### Solution

```xpp
// Base class
class BaseDiscountCalculator
{
    public Amount calculateDiscount(Amount _amount)
    {
        return 0;  // No discount by default
    }
}

// Gold tier — 10% discount
class GoldDiscountCalculator extends BaseDiscountCalculator
{
    public Amount calculateDiscount(Amount _amount)
    {
        return _amount * 0.10;
    }
}

// Platinum tier — 20% discount
class PlatinumDiscountCalculator extends BaseDiscountCalculator
{
    public Amount calculateDiscount(Amount _amount)
    {
        return _amount * 0.20;
    }
}

// Job to test the calculators
static void exercise8_discountCalculators(Args _args)
{
    Amount testAmount = 1000;
    BaseDiscountCalculator calculator;

    // Gold calculator
    calculator = new GoldDiscountCalculator();
    info(strFmt("Gold discount on %1: %2", testAmount, calculator.calculateDiscount(testAmount)));

    // Platinum calculator
    calculator = new PlatinumDiscountCalculator();
    info(strFmt("Platinum discount on %1: %2", testAmount, calculator.calculateDiscount(testAmount)));
}
```

**Expected Infolog output:**
```
Gold discount on 1000: 100
Platinum discount on 1000: 200
```

---

## Exercise 9 — Event Handler

### Problem

Create an event handler that runs after a `CustTable` record is inserted. The handler should log the new customer's `AccountNum` and `Name` to a custom log table called `CustCreationLog`.

### Hints
- Use the `[SubscribesTo(tableStr(CustTable), inserted)]` attribute to register the handler
- Create a custom table `CustCreationLog` with fields: `AccountNum` (string 20), `CustomerName` (string 60), `CreatedDateTime` (utcDateTime)

### Solution

First, create the custom table `CustCreationLog`:

| Field | Type |
|---|---|
| `AccountNum` | `string 20` |
| `CustomerName` | `string 60` |
| `CreatedDateTime` | `utcdatetime` |

Then, the event handler class:

```xpp
class CustCreationEventHandler
{
    /// <summary>Event handler — runs after a CustTable record is inserted.</summary>
    [SubscribesTo(tableStr(CustTable), inserted)]
    public static void onCustTableInserted(CustTable _custTable)
    {
        CustCreationLog log;

        log.clear();
        log.AccountNum     = _custTable.AccountNum;
        log.CustomerName   = _custTable.Name;
        log.CreatedDateTime = DateTimeUtil::utcNow();
        log.insert();
    }
}
```

**Note:** The event handler must be in a class that is part of a model that references the `ApplicationSuite` model. The `[SubscribesTo]` attribute registers the handler automatically at compile time.

---

## Exercise 10 — Delegate

### Problem

Create a delegate on a class called `PriceCalculator` that allows consumers to customize the discount percentage. The delegate should be called during discount calculation, and consumers should be able to subscribe their own logic.

### Hints
- Declare a delegate using the `delegate` keyword
- Use `delegate` on a static method that accepts a `PriceCalculator` instance and the original price
- Consumers subscribe using the `+=` operator
- The publisher calls the delegate with `this.priceDelegate(this, originalPrice)`

### Solution

```xpp
// Publisher class
class PriceCalculator
{
    // Delegate declaration — accepts a PriceCalculator and an Amount, returns a modified Amount
    public delegate Amount discountDelegate(PriceCalculator _calculator, Amount _originalPrice);

    // The delegate instance — consumers subscribe to this
    public discountDelegate priceDelegate;

    // Base discount percentage
    private Amount _baseDiscountPct = 0;

    public Amount calculateDiscountedPrice(Amount _originalPrice)
    {
        Amount discountedPrice;
        Amount discountAmount;

        // Calculate base discount
        discountAmount = _originalPrice * (_baseDiscountPct / 100);

        // Allow consumers to modify the discount via the delegate
        if (this.priceDelegate)
        {
            discountAmount = this.priceDelegate(this, _originalPrice);
        }

        discountedPrice = _originalPrice - discountAmount;
        return discountedPrice;
    }
}

// Consumer — subscribes to the delegate
class CustomDiscountSubscriber
{
    public static Amount customDiscount(PriceCalculator _calculator, Amount _originalPrice)
    {
        // Apply a 15% discount for VIP customers
        return _originalPrice * 0.15;
    }
}

// Job to test the delegate
static void exercise10_delegate(Args _args)
{
    PriceCalculator calculator = new PriceCalculator();
    Amount originalPrice = 1000;
    Amount discountedPrice;

    // Subscribe the custom discount logic
    calculator.priceDelegate += delegate(Amount _price)
    {
        return _price * 0.15;  // 15% discount
    };

    discountedPrice = calculator.calculateDiscountedPrice(originalPrice);
    info(strFmt("Original: %1 — Discounted: %2", originalPrice, discountedPrice));
}
```

**Expected Infolog output:**
```
Original: 1000 — Discounted: 850
```

---

## Exercise 11 — Chain of Command (CoC)

### Problem

Create two extension classes on `CustTable` that both modify the `validateWrite()` method using Chain of Command. The first extension should check that the `AccountNum` starts with "CUST-". The second extension should check that the `Name` is not empty. Both should call `next` so they work together.

### Hints
- Each extension uses `[ExtensionOf(tableStr(CustTable))]`
- Each calls `next validateWrite()` to pass control to the next handler
- The execution order depends on the model layer order (CUS runs after SYS)

### Solution

**Extension 1 — AccountNum validation:**
```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_AccountNumValidation
{
    public boolean validateWrite()
    {
        boolean ret;

        ret = next validateWrite();

        if (ret && !strStartsWith(this.AccountNum, "CUST-"))
        {
            ret = false;
            error("Account number must start with 'CUST-'.");
        }

        return ret;
    }
}
```

**Extension 2 — Name validation:**
```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_NameValidation
{
    public boolean validateWrite()
    {
        boolean ret;

        ret = next validateWrite();

        if (ret && this.Name == '')
        {
            ret = false;
            error("Customer name cannot be empty.");
        }

        return ret;
    }
}
```

**How CoC works here:** When `validateWrite()` is called on `CustTable`, the AOS executes both extensions in layer order. Each extension calls `next validateWrite()` to pass control to the next handler. If any handler returns `false`, the chain stops and the record is not saved.

---

## Exercise 12 — Data Entity Creation

### Problem

Describe the steps to create a simple data entity that exposes a custom table `VendAPCustomsDecl` (with fields `DeclId`, `DeclDate`, `CustomsRef`) to an external system via OData. List the AOT nodes you need to create and configure.

### Hints
- A data entity consists of a `DataEntity` node, a `Query` node, and optionally a staging table
- The entity needs a `PublicCollection` (fields exposed externally) and optionally a `PrivateCollection` (staging fields)
- The entity must be registered in the `Data Entity` node

### Solution

1. **Create the base table** `VendAPCustomsDecl` with fields:
   - `DeclId` (string 35, EDT)
   - `DeclDate` (date)
   - `CustomsRef` (string 50)

2. **Create a Query** `VendAPCustomsDeclQuery`:
   - Add `VendAPCustomsDecl` as the data source
   - Add all fields to the query

3. **Create the Data Entity** `VendAPCustomsDeclEntity`:
   - **AOT Node**: `Data Entities\VendAPCustomsDeclEntity`
   - Set the `Name` property to `VendAPCustomsDeclEntity`
   - Set the `PublicCollection` to include `DeclId`, `DeclDate`, `CustomsRef`
   - Set the `Query` property to point to `VendAPCustomsDeclQuery`
   - Set the `StagingTable` property if you need intermediate storage

4. **Add a Data Entity Field** for each field you want to expose:
   - `VendAPCustomsDeclEntity\Fields\DeclId`
   - `VendAPCustomsDeclEntity\Fields\DeclDate`
   - `VendAPCustomsDeclEntity\Fields\CustomsRef`

5. **Synchronize the database** — right-click the project → **Deploy** to generate the SQL table.

6. **Register the entity** — the entity is automatically available via OData at:
   ```
   https://<your-environment>/data/VendAPCustomsDeclEntity
   ```

---

## Exercise 13 — SSRS Report Data Provider

### Problem

Write the data provider class for an SSRS report that lists all customers in a specific group along with their total outstanding balance. The report should accept a `CustGroup` parameter.

### Hints
- The data provider class extends `SrsReportDataProvider`
- Use `SrsReportDataContract` to pass parameters
- The `processReport()` method contains the query logic
- Use a `QueryRun` with a `Sum` aggregate to calculate the outstanding balance per customer
- The `QueryBuildDataSource::addAggregate()` method adds a sum field to the query

### Solution

```xpp
// Data contract for the report parameter
[DataContractAttribute]
class VendCustomerBalanceDPContract extends SrsReportDataContract
{
    CustGroup _custGroup;

    [DataMemberAttribute('CustGroup')]
    public CustGroup parmCustGroup(CustGroup _custGroup = _custGroup)
    {
        return _custGroup;
    }
}

// Data provider class
class VendCustomerBalanceDP extends SrsReportDataProvider
{
    CustGroup _custGroup;

    public void processReport()
    {
        VendCustomerBalanceTmp tmpTable;
        CustTable              custTable;
        Amount                 totalBalance;

        // Clear any existing data
        tmpTable.deleteFrom();

        // Build a query that sums outstanding balances per customer
        Query query = new Query();
        QueryBuildDataSource qbdsCustTable = query.addDataSource(tableNum(CustTable));
        QueryBuildDataSource qbdsCustTrans = qbdsCustTable.addDataSource(tableNum(CustTrans));

        // Join CustTrans to CustTable on AccountNum
        qbdsCustTrans.addLink(fieldNum(CustTable, AccountNum), fieldNum(CustTrans, AccountNum));

        // Filter: unsettled transactions with invoice date on or before today
        qbdsCustTrans.addRange(fieldNum(CustTrans, InvoiceAccountingDate)).value(queryValue(today()));
        qbdsCustTrans.addRange(fieldNum(CustTrans, HasNotBeenSettled)).value(queryValue(true));

        // Add sum aggregate on AmountMST
        qbdsCustTrans.addAggregate(fieldNum(CustTrans, AmountMST));

        // Filter by customer group
        qbdsCustTable.addRange(fieldNum(CustTable, GroupName)).value(queryValue(_custGroup));

        // Add the fields we need to the query
        qbdsCustTable.addField(fieldNum(CustTable, AccountNum));
        qbdsCustTable.addField(fieldNum(CustTable, Name));
        qbdsCustTable.addField(fieldNum(CustTable, GroupName));

        QueryRun queryRun = new QueryRun(query);

        while (queryRun.next())
        {
            custTable = queryRun.get(tableNum(CustTable));
            totalBalance = queryRun.getSum(fieldNum(CustTrans, AmountMST));

            tmpTable.clear();
            tmpTable.AccountNum = custTable.AccountNum;
            tmpTable.CustomerName = custTable.Name;
            tmpTable.GroupName = custTable.GroupName;
            tmpTable.TotalBalance = totalBalance;
            tmpTable.insert();
        }
    }
}
```

---

## Exercise 14 — Error Handling Best Practices

### Problem

Identify the error in each of the following code snippets and rewrite it correctly:

### Snippet A — Missing `super()` call
```xpp
public boolean validateWrite()
{
    if (this.AccountNum == '')
    {
        error("Account number cannot be empty.");
        return false;
    }
    return true;
}
```

### Snippet B — `select` inside a `while` loop (N+1 problem)
```xpp
CustTable custTable;
while select custTable
{
    VendTable vendTable;
    select firstonly vendTable
        where vendTable.AccountNum == custTable.AccountNum;

    if (vendTable)
    {
        info(strFmt("%1 — %2", custTable.AccountNum, vendTable.Name));
    }
}
```

### Snippet C — Missing transaction
```xpp
CustTable custTable;
custTable.clear();
custTable.AccountNum = "CUST-NEW-001";
custTable.Name = "New Customer";
custTable.insert();

CustGroup custGroup;
custGroup.clear();
custGroup.GroupName = "NEWGROUP";
custGroup.insert();
```

### Solution

**Snippet A — Fixed:**
```xpp
public boolean validateWrite()
{
    boolean ret;

    ret = super();  // Always call super() first

    if (ret && this.AccountNum == '')
    {
        ret = false;
        error("Account number cannot be empty.");
    }

    return ret;
}
```

**Snippet B — Fixed:**
```xpp
// Use exists join instead of a select inside a while loop
CustTable custTable;
VendTable vendTable;
boolean hasVendor;

while select custTable
{
    hasVendor = exists join vendTable
        where vendTable.AccountNum == custTable.AccountNum;

    if (hasVendor)
    {
        info(strFmt("%1 — has vendor", custTable.AccountNum));
    }
}
```

**Snippet C — Fixed:**
```xpp
ttsBegin;
try
{
    CustTable custTable;
    custTable.clear();
    custTable.AccountNum = "CUST-NEW-001";
    custTable.Name = "New Customer";
    custTable.insert();

    CustGroup custGroup;
    custGroup.clear();
    custGroup.GroupName = "NEWGROUP";
    custGroup.insert();

    ttsCommit;
}
catch (Exception::Error)
{
    ttsAbort;
    error("Failed to insert customer and group — rolled back.");
}
```

---

## Exercise 15 — Putting It All Together

### Problem

Write a complete X++ job that:
1. Creates a new customer with `AccountNum = "CUST-EX-001"`, `Name = "Example Corp"`, `Currency = "USD"`, `GroupName = "CORP"`
2. Validates the customer using a `CustValidationService` class (from Chapter 2's activity)
3. If valid, inserts the customer and logs the success to the Infolog
4. If invalid, logs the validation errors and does not insert
5. Wraps everything in a transaction with deadlock retry logic

### Solution

```xpp
static void exercise15_completeJob(Args _args)
{
    CustTable                custTable;
    CustValidationService    validator;
    boolean                  isValid;
    int                      retryCount = 0;
    boolean                  success = false;

    // Step 1: Create the customer record (in memory, not yet inserted)
    custTable.clear();
    custTable.AccountNum = "CUST-EX-001";
    custTable.Name = "Example Corp";
    custTable.Currency = "USD";
    custTable.GroupName = "CORP";

    // Step 2: Validate using the CustValidationService
    validator = new CustValidationService(custTable);
    isValid = validator.validate();

    if (!isValid)
    {
        warning("Customer validation failed — check the Infolog for details.");
    }
    else
    {
        // Step 3: Insert the customer within a transaction with deadlock retry
        while (!success && retryCount < 3)
        {
            ttsBegin;
            try
            {
                custTable.insert();

                ttsCommit;
                info(strFmt("Customer %1 created successfully.", custTable.AccountNum));
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
                error("An unexpected error occurred.");
                break;
            }
        }

    }

    if (!success)
    {
        error("Failed to create customer after 3 attempts.");
    }
}
```

---

## Exercise 16 — Number Sequence

### Problem

Create a custom table `ComplianceLog` with a `ComplianceId` field that uses a number sequence for its value. Write a job that inserts a new `ComplianceLog` record and verifies the number sequence was consumed correctly.

### Hints
- Create a `NumberSeq` reference on the table's `ComplianceId` field
- Use `NumberSeq::newGetNumFromId()` to get the next number in the sequence
- The number sequence must be configured in the `NumberSeq` AOT node under the appropriate module

### Solution

1. **Create the table** `ComplianceLog` with fields:
   - `ComplianceId` (string 20, EDT `ComplianceId`)
   - `Description` (string 60)
   - `CreatedDateTime` (utcDateTime)

2. **Create a NumberSeq reference** on `ComplianceId`:
   - In the AOT, right-click the `ComplianceId` field → **New NumberSeq Reference**
   - Set the `ReferenceField` property to `ComplianceId`

3. **Create the number sequence** in the AOT:
   - `NumberSeq > NumberSeqReference > ComplianceLog`
   - Set `Scope` to `Table`
   - Set the `NumberSequence` property to point to a new `NumberSeq` object

4. **The job**:

```xpp
static void exercise16_numberSequence(Args _args)
{
    ComplianceLog log;
    NumberSeq numberSeq;

    ttsBegin;
    try
    {
        log.clear();

        // Get the next number from the number sequence
        numberSeq = NumberSeq::newGetNumFromId(
            NumberSeqReference::findReference(fieldNum(ComplianceLog, ComplianceId)).NumberSequenceId());
        log.ComplianceId = numberSeq.num();

        log.Description = "Compliance check entry";
        log.CreatedDateTime = DateTimeUtil::utcNow();
        log.insert();

        ttsCommit;
        info(strFmt("Compliance log created with ID: %1", log.ComplianceId));
    }
    catch (Exception::Error)
    {
        ttsAbort;
        error("Failed to create compliance log entry.");
    }
}
```

---

## Exercise 17 — SysOperation Service

### Problem

Create a `SysOperation` service class that accepts a `CustGroup` parameter and returns the count of customers and their total outstanding balance for that group. Use a `SysOperationServiceController` to run the service.

### Hints
- The service class extends `SysOperationServiceBase`
- Use a `DataContract` class to pass parameters to the service
- Override the `process()` method to contain the business logic
- Use `SysOperationServiceController::runService()` to execute the service

### Solution

```xpp
// Data contract for service parameters
[DataContractAttribute]
class CustBalanceServiceContract extends SrsReportDataContract
{
    CustGroup _custGroup;

    [DataMemberAttribute('CustGroup')]
    public CustGroup parmCustGroup(CustGroup _custGroup = _custGroup)
    {
        return _custGroup;
    }
}

// Service class
class CustBalanceService extends SysOperationServiceBase
{
    [DataMemberAttribute('CustGroup')]
    public CustGroup parmCustGroup(CustGroup _custGroup = _custGroup)
    {
        return _custGroup;
    }

    public void process()
    {
        CustTable custTable;
        CustTrans custTrans;
        Amount totalBalance;
        int customerCount;

        while select custTable
            where custTable.GroupName == this.parmCustGroup()
        {
            customerCount++;

            // Use exists join pattern to check for unsettled transactions
            // and accumulate the total balance
            while select custTrans
                where custTrans.AccountNum == custTable.AccountNum
                   && custTrans.HasNotBeenSettled
            {
                totalBalance += custTrans.AmountMST;
            }
        }

        info(strFmt("Customers in group %1: %2", this.parmCustGroup(), customerCount));
        info(strFmt("Total outstanding balance: %1", totalBalance));
    }
}

// Job to run the service
static void exercise17_sysOperation(Args _args)
{
    SysOperationServiceController controller = new SysOperationServiceController(
        classStr(CustBalanceService),
        "CustBalanceService",
        SysOperationServiceController::getDefaultConfiguration());

    controller.parmArgs(new CustBalanceServiceContract());
    controller.parmArgs().parmCustGroup("CORP");
    controller.startOperation();
}
```

---

## Exercise Index

| # | Topic | Key Concept |
|---|---|---|
| 1 | Containers & Type Casting | `conPeek`, `typeid()` |
| 2 | While Select with Filtering | `while select` with `where` |
| 3 | Bulk Update | `update_recordset` |
| 4 | Transactions | `ttsBegin`/`ttsCommit`/`ttsAbort` |
| 5 | Method Overriding | `super()` in table extensions |
| 6 | Deadlock Handling | Retry pattern with `catch (Exception::Deadlock)` |
| 7 | Class Design | Constructor, private helpers, static methods |
| 8 | Inheritance & Polymorphism | `extends`, method overriding |
| 9 | Event Handlers | `[SubscribesTo]` attribute |
| 10 | Delegates | `delegate` keyword, `+=` subscription |
| 11 | Chain of Command | `next` keyword, multiple extensions |
| 12 | Data Entities | `DataEntity`, `Query`, OData exposure |
| 13 | SSRS Data Provider | `SrsReportDataProvider`, `processReport()` |
| 14 | Error Handling Best Practices | `super()`, `exists join`, transactions |
| 15 | Putting It All Together | Complete end-to-end job |
| 16 | Number Sequence | `NumberSeq`, `NumberSeqReference` |
| 17 | SysOperation Service | `SysOperationServiceBase`, `SysOperationServiceController` |

| # | Topic | Key Concept |
|---|---|---|
| 1 | Containers & Type Casting | `conPeek`, `typeid()` |
| 2 | While Select with Filtering | `while select` with `where` |
| 3 | Bulk Update | `update_recordset` |
| 4 | Transactions | `ttsBegin`/`ttsCommit`/`ttsAbort` |
| 5 | Method Overriding | `super()` in table extensions |
| 6 | Deadlock Handling | Retry pattern with `catch (Exception::Deadlock)` |
| 7 | Class Design | Constructor, private helpers, static methods |
| 8 | Inheritance & Polymorphism | `extends`, method overriding |
| 9 | Event Handlers | `[SubscribesTo]` attribute |
| 10 | Delegates | `delegate` keyword, `+=` subscription |
| 11 | Chain of Command | `next` keyword, multiple extensions |
| 12 | Data Entities | `DataEntity`, `Query`, OData exposure |
| 13 | SSRS Data Provider | `SrsReportDataProvider`, `processReport()` |
| 14 | Error Handling Best Practices | `super()`, `exists join`, transactions |
| 15 | Putting It All Together | Complete end-to-end job |
