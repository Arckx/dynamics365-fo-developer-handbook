# Chapter 12 — SysTest Framework: Complete Guide

> **Prerequisites:** Basic X++ knowledge, Visual Studio with D365 F&O tools, access to a D365 F&O development environment  
> **Time Investment:** 4–6 hours to read, 8–12 hours to practice all examples  
> **Microsoft Learn References:** [SysTest framework](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework), [Unit testing in D365 F&O](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/unit-testing), [Test automation](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-automation)

---

## Table of Contents

1. [The SysTest Framework — Core Components](#1-the-systest-framework--core-components)
2. [Assert Methods — Complete Reference](#2-assert-methods--complete-reference)
3. [Test Data Creation Patterns](#3-test-data-creation-patterns)
4. [Test Isolation and Data-Driven Testing](#4-test-isolation-and-data-driven-testing)
5. [Test Coverage Metrics in LCS](#5-test-coverage-metrics-in-lcs)
6. [Integration Testing with LCS Test Case Management](#6-integration-testing-with-lcs-test-case-management)
7. [Activity: Complete Test Class for Sales Order Discount Calculation](#7-activity-complete-test-class-for-sales-order-discount-calculation)
8. [Best Practices, Common Mistakes, and CI/CD Integration](#8-best-practices-common-mistakes-and-cicd-integration)

---

## 1. The SysTest Framework — Core Components

### 1.1 What Is SysTest? (Layman Explanation)

**SysTest is D365 F&O's built-in unit testing framework.** Think of it as a **quality gate** that runs your code in a controlled environment and tells you whether it behaves as expected. Unlike manual testing where a human clicks through forms, SysTest runs automatically, can be executed hundreds of times per minute, and integrates with your build pipeline so broken code never reaches production.

**Analogy:** If D365 F&O is a factory, SysTest is the automated quality control scanner on the assembly line — it checks every widget (code unit) against specifications before it ships.

### 1.2 Core Classes and Attributes

| Component | Type | Purpose | When It Runs |
|-----------|------|---------|--------------|
| `SysTestCase` | Base class | Every test class must extend this | — |
| `SysTestMethodAttribute` | Attribute | Marks a method as a test method | Per test execution |
| `setUp()` | Instance method | Creates shared test data for the class | Once before all test methods |
| `tearDown()` | Instance method | Cleans up shared test data | Once after all test methods |
| `SysTestTransactionAttribute` | Attribute | Controls transaction isolation level | Per test method |

### 1.3 Test Class Structure — Complete Example

```xpp
/// <summary>
/// Test class for vendor compliance validation logic.
/// Demonstrates the standard SysTest class structure.
/// </summary>
class VendComplianceTest extends SysTestCase
{
    // ========================================
    // SHARED SETUP — Runs ONCE before all tests
    // ========================================
    public void setUp()
    {
        // Create test data that ALL test methods need
        // Example: reference data, configuration records, lookup values
        
        // Create a standard vendor group for tests
        VendGroup vendGroup;
        vendGroup.initValue();
        vendGroup.VendGroup = 'TESTGROUP';
        vendGroup.Name = 'Test Vendor Group';
        vendGroup.insert();
    }

    // ========================================
    // TEST METHOD — Each is an independent test case
    // ========================================
    [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_FailsForHighCredit()
    {
        // AAA Pattern: Arrange → Act → Assert
        
        // ARRANGE — Set up test-specific data
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = 'HIGHVENDOR01';
        vendTable.Name = 'High Credit Vendor';
        vendTable.CreditMax = 600000;  // Above $500K threshold
        vendTable.VendGroup = 'TESTGROUP';
        vendTable.insert();

        // ACT — Execute the code under test
        boolean validationResult = VendComplianceValidator::validate(vendTable, '');

        // ASSERT — Verify the outcome
        this.assertFalse(validationResult, 'Validation should fail for vendor >$500K without compliance code');
        
        // CLEANUP — Remove test-specific data (optional with AutoRollback)
        vendTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_PassesForLowCredit()
    {
        // ARRANGE
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = 'LOWVENDOR01';
        vendTable.Name = 'Low Credit Vendor';
        vendTable.CreditMax = 100000;  // Below $500K threshold
        vendTable.VendGroup = 'TESTGROUP';
        vendTable.insert();

        // ACT
        boolean validationResult = VendComplianceValidator::validate(vendTable, '');

        // ASSERT
        this.assertTrue(validationResult, 'Validation should pass for vendor <$500K without compliance code');
        
        // CLEANUP
        vendTable.delete();
    }

    // ========================================
    // SHARED TEARDOWN — Runs ONCE after all tests
    // ========================================
    public void tearDown()
    {
        // Clean up shared test data created in setUp()
        VendGroup vendGroup;
        while select vendGroup
            where vendGroup.VendGroup == 'TESTGROUP'
        {
            vendGroup.delete();
        }
    }
}
```

### 1.4 Alternative: Test Method Naming Convention

Instead of `[SysTestMethodAttribute]`, you can prefix methods with `test`:

```xpp
class VendComplianceTest extends SysTestCase
{
    // This works the same as [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_FailsForHighCredit()
    {
        // Test logic
    }
    
    // This is NOT a test method (missing "test" prefix)
    public static void helperMethod()
    {
        // Helper logic
    }
}
```

**Best Practice:** Use `[SysTestMethodAttribute]` explicitly — it's clearer, searchable, and allows additional attributes like `[SysTestCategory]`.

### 1.5 Key Differences: `setUp()` vs Per-Method Setup

| Aspect | `setUp()` (Class-Level) | Per-Method Setup |
|--------|------------------------|------------------|
| **Runs** | Once per test class | Before each test method |
| **Scope** | Shared across all tests | Isolated to one test |
| **Use For** | Reference data, lookup tables, configuration | Test-specific transactional data |
| **Cleanup** | In `tearDown()` | In same test method |

---

## 2. Assert Methods — Complete Reference

### 2.1 Core Assertion Methods (Inherited from `SysTestCase`)

All assertion methods are instance methods on `SysTestCase` — call them with `this.assertXxx()` or just `assertXxx()` within test methods.

| Method | Signature | Purpose | When to Use |
|--------|-----------|---------|-------------|
| **Equality** |
| `assertEquals` | `assertEquals(expected, actual, message)` | Verifies two values are equal | Primary assertion for most tests |
| `assertNotEquals` | `assertNotEquals(unexpected, actual, message)` | Verifies two values are NOT equal | Negative assertions |
| **Boolean** |
| `assertTrue` | `assertTrue(condition, message)` | Verifies condition is true | Boolean results, flags |
| `assertFalse` | `assertFalse(condition, message)` | Verifies condition is false | Boolean results, flags |
| **Null Checks** |
| `assertNull` | `assertNull(value, message)` | Verifies value is null | Return values that should be null |
| `assertNotNull` | `assertNotNull(value, message)` | Verifies value is NOT null | Return values that must exist |
| **Numeric Comparisons** |
| `assertGreater` | `assertGreater(actual, expected, message)` | Verifies actual > expected | Counts, amounts, thresholds |
| `assertLess` | `assertLess(actual, expected, message)` | Verifies actual < expected | Limits, boundaries |
| `assertGreaterOrEqual` | `assertGreaterOrEqual(actual, expected, message)` | Verifies actual >= expected | Minimum thresholds |
| `assertLessOrEqual` | `assertLessOrEqual(actual, expected, message)` | Verifies actual <= expected | Maximum caps |
| **Exception & Message Validation** |
| `assertException` | `assertException(className, methodName, expectedException, message)` | Verifies a method throws an exception | Error handling paths |
| `assertError` | `assertError(statement, message)` | Verifies statement produces an error | Form validation, `validateWrite()` |
| `assertWarning` | `assertWarning(statement, message)` | Verifies statement produces a warning | Business logic warnings |
| `assertInfo` | `assertInfo(statement, message)` | Verifies statement produces an info message | Success messages, logging |

### 2.2 Assertion Examples — Real-World Scenarios

#### 2.2.1 Basic Equality Assertions

```xpp
[SysTestMethodAttribute]
public static void testDiscountCalculation_Basic()
{
    SalesOrderDiscount discountCalculator;
    Real discountPercent;
    
    // ARRANGE
    discountCalculator = SalesOrderDiscount::construct();
    SalesTable salesTable = TestSalesTable::newTest('CUST001', 15000);
    salesTable.insert();
    
    // ACT
    discountPercent = discountCalculator.calculateDiscount(salesTable);
    
    // ASSERT — Exact value comparison
    this.assertEquals(5.0, discountPercent, 'Standard discount should be 5% for orders over $10K');
    
    // ASSERT — Not equal (negative assertion)
    this.assertNotEquals(0.0, discountPercent, 'Discount should not be zero for qualifying orders');
    
    salesTable.delete();
}
```

#### 2.2.2 Boolean Assertions

```xpp
[SysTestMethodAttribute]
public static void testCustomerValidation_IsValid()
{
    CustTable custTable = TestCustTable::constructValid();
    custTable.insert();
    
    // ACT — Returns boolean
    boolean isValid = CustomerValidator::isEligibleForCredit(custTable);
    
    // ASSERT — Boolean checks
    this.assertTrue(isValid, 'Valid customer should be eligible for credit');
    
    // Negative case
    custTable.Blocked = CustVendorBlocked::All;
    custTable.update();
    
    isValid = CustomerValidator::isEligibleForCredit(custTable);
    this.assertFalse(isValid, 'Blocked customer should NOT be eligible for credit');
    
    custTable.delete();
}
```

#### 2.2.3 Null Assertions

```xpp
[SysTestMethodAttribute]
public static void testFindCustomer_NotFound()
{
    // ACT — Try to find non-existent customer
    CustTable custTable = CustTable::find('NONEXISTENT');
    
    // ASSERT — Should return null/empty record
    this.assertNull(custTable.RecId, 'Non-existent customer should return empty record');
    this.assertEquals('', custTable.AccountNum, 'AccountNum should be empty for non-existent customer');
}

[SysTestMethodAttribute]
public static void testCreateSalesOrder_ReturnsRecord()
{
    SalesTable salesTable = SalesOrderService::create('CUST001');
    
    // ASSERT — Must return a valid record
    this.assertNotNull(salesTable.RecId, 'Created sales order should have RecId');
    this.assertNotEquals('', salesTable.SalesId, 'Created sales order should have SalesId');
}
```

#### 2.2.4 Numeric Comparison Assertions

```xpp
[SysTestMethodAttribute]
public static void testInventoryReservation_QuantityChecks()
{
    InventSum inventSum = InventSum::find('ITEM001', 'WH01');
    
    // ARRANGE — Reserve 50 units
    InventoryReservation::reserve('ITEM001', 'WH01', 50);
    inventSum.reread();
    
    // ASSERT — Numeric thresholds
    this.assertGreater(inventSum.ReservPhysical, 0, 'Should have physical reservations');
    this.assertGreaterOrEqual(inventSum.ReservPhysical, 50, 'Should have at least 50 reserved');
    this.assertLessOrEqual(inventSum.ReservPhysical, inventSum.AvailPhysical, 'Reserved cannot exceed available');
    
    // Cleanup
    InventoryReservation::unreserve('ITEM001', 'WH01', 50);
}
```

#### 2.2.5 Exception and Message Assertions

```xpp
[SysTestMethodAttribute]
public static void testValidateWrite_ThrowsErrorForNegativeAmount()
{
    SalesLine salesLine;
    salesLine.initValue();
    salesLine.ItemId = 'ITEM001';
    salesLine.SalesQty = -10;  // Invalid: negative quantity
    salesLine.LineAmount = -5000;
    
    // ASSERT — ValidateWrite should throw an error
    this.assertError(salesLine.validateWrite(), 'Negative quantity should produce an error');
}

[SysTestMethodAttribute]
public static void testCheckCreditLimit_ProducesWarning()
{
    CustTable custTable = TestCustTable::newTest('CUST001', 100000);  // $100K credit limit
    custTable.insert();
    
    SalesTable salesTable = TestSalesTable::newTest(custTable.AccountNum, 150000);  // $150K order
    salesTable.insert();
    
    // ASSERT — Should produce a warning (not an error) for exceeding credit limit
    this.assertWarning(CustCreditCheck::check(salesTable), 'Should warn when order exceeds credit limit');
    
    salesTable.delete();
    custTable.delete();
}

[SysTestMethodAttribute]
public static void testProcessOrder_ProducesInfoMessage()
{
    SalesTable salesTable = TestSalesTable::constructConfirmed();
    salesTable.insert();
    
    // ASSERT — Process should produce info message
    this.assertInfo(SalesOrderProcessor::process(salesTable), 'Processing should log info message');
    
    salesTable.delete();
}

[SysTestMethodAttribute]
public static void testDivideByZero_ThrowsException()
{
    // ASSERT — Static method should throw when dividing by zero
    this.assertException(
        classStr(MathHelper),
        methodStr(MathHelper, divide),
        error::Error,  // Expected exception type
        'Division by zero should throw Error exception'
    );
}
```

### 2.3 Assertion Method Signatures — Quick Reference

```xpp
// All methods accept an optional message parameter as the last argument
// Message is displayed in test output when assertion fails

// Equality
void assertEquals(anyType _expected, anyType _actual, str _message = '')
void assertNotEquals(anyType _expected, anyType _actual, str _message = '')

// Boolean
void assertTrue(boolean _condition, str _message = '')
void assertFalse(boolean _condition, str _message = '')

// Null
void assertNull(anyType _value, str _message = '')
void assertNotNull(anyType _value, str _message = '')

// Numeric (Real/Int)
void assertGreater(Real _actual, Real _expected, str _message = '')
void assertLess(Real _actual, Real _expected, str _message = '')
void assertGreaterOrEqual(Real _actual, Real _expected, str _message = '')
void assertLessOrEqual(Real _actual, Real _expected, str _message = '')

// Exception & Messages
void assertException(str _className, str _methodName, int _expectedException, str _message = '')
void assertError(boolean _statement, str _message = '')
void assertWarning(boolean _statement, str _message = '')
void assertInfo(boolean _statement, str _message = '')
```

---

## 3. Test Data Creation Patterns

### 3.1 Why Test Data Patterns Matter

Creating test data is **the most time-consuming part of writing tests**. Good patterns make tests:
- **Readable** — Intent is clear from the test code
- **Maintainable** — Changes to table structure only need updates in one place
- **Isolated** — Tests don't interfere with each other
- **Fast** — Minimal database operations

### 3.2 Pattern 1: Factory Class with `construct()` — Recommended

```xpp
/// <summary>
/// Test data factory for VendTable records.
/// Provides sensible defaults that tests can customize.
/// </summary>
class TestVendTable
{
    /// <summary>
    /// Creates a vendor with standard defaults.
    /// Caller must call insert().
    /// </summary>
    public static VendTable construct()
    {
        VendTable vendTable;
        
        vendTable.initValue();
        vendTable.AccountNum = 'TESTVENDOR';  // Will be overridden if needed
        vendTable.Name = 'Test Vendor';
        vendTable.CreditMax = 50000;
        vendTable.Currency = 'USD';
        vendTable.VendGroup = 'VENDGROUP1';
        vendTable.PaymTermId = 'NET30';
        vendTable.TaxGroup = 'TAXGROUP1';
        
        return vendTable;
    }

    /// <summary>
    /// Creates a vendor with specific test parameters.
    /// </summary>
    public static VendTable newTest(
        AccountNum _accountNum, 
        Currency _currency, 
        Real _creditMax,
        VendGroup _vendGroup = 'VENDGROUP1'
    )
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.AccountNum = _accountNum;
        vendTable.Currency = _currency;
        vendTable.CreditMax = _creditMax;
        vendTable.VendGroup = _vendGroup;
        return vendTable;
    }

    /// <summary>
    /// Creates a high-credit vendor (>$500K) for compliance testing.
    /// </summary>
    public static VendTable newHighCreditVendor(AccountNum _accountNum)
    {
        return TestVendTable::newTest(_accountNum, 'USD', 750000);
    }

    /// <summary>
    /// Creates a VIP vendor for discount testing.
    /// </summary>
    public static VendTable newVIPVendor(AccountNum _accountNum)
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.AccountNum = _accountNum;
        vendTable.CustGroup = 'VIP';  // Assuming CustGroup field exists
        vendTable.CreditMax = 1000000;
        return vendTable;
    }
}
```

**Usage in Tests:**

```xpp
[SysTestMethodAttribute]
public static void testWithConstruct()
{
    VendTable vendTable = TestVendTable::construct();
    vendTable.AccountNum = 'UNIQUE001';  // Override for uniqueness
    vendTable.insert();
    
    // Test logic
    this.assertEquals('TESTVENDOR', vendTable.AccountNum);
    
    vendTable.delete();
}

[SysTestMethodAttribute]
public static void testWithNewTest()
{
    VendTable vendTable = TestVendTable::newTest('VEND001', 'EUR', 750000);
    vendTable.insert();
    
    this.assertEquals('EUR', vendTable.Currency);
    this.assertEquals(750000, vendTable.CreditMax);
    
    vendTable.delete();
}
```

### 3.3 Pattern 2: Test Data Builder (Fluent API) — Maximum Flexibility

```xpp
/// <summary>
/// Fluent builder for creating complex test SalesOrder scenarios.
/// </summary>
class TestSalesOrderBuilder
{
    SalesTable salesTable;
    List salesLines;  // List of SalesLine records
    
    private void new()
    {
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesLines = new List(Types::Record);
    }
    
    public static TestSalesOrderBuilder create()
    {
        return new TestSalesOrderBuilder();
    }
    
    public TestSalesOrderBuilder withCustomer(CustAccount _custAccount)
    {
        salesTable.CustomerAccount = _custAccount;
        return this;
    }
    
    public TestSalesOrderBuilder withDate(TransDate _date)
    {
        salesTable.SalesDate = _date;
        return this;
    }
    
    public TestSalesOrderBuilder withSalesId(SalesId _salesId)
    {
        salesTable.SalesId = _salesId;
        return this;
    }
    
    public TestSalesOrderBuilder addLine(
        ItemId _itemId, 
        Qty _qty, 
        Amount _lineAmount,
        InventDimId _inventDimId = '')
    {
        SalesLine salesLine;
        salesLine.initValue();
        salesLine.ItemId = _itemId;
        salesLine.SalesQty = _qty;
        salesLine.LineAmount = _lineAmount;
        salesLine.InventDimId = _inventDimId ? _inventDimId : InventDim::findOrCreate('_').InventDimId;
        salesLines.addEnd(salesLine);
        return this;
    }
    
    public TestSalesOrderBuilder withPaymentTerms(PaymTermId _paymTermId)
    {
        salesTable.PaymTermId = _paymTermId;
        return this;
    }
    
    public SalesTable build()
    {
        // Insert header
        salesTable.insert();
        
        // Insert lines
        SalesLine salesLine;
        while select salesLine from salesLines
        {
            salesLine.SalesTableId = salesTable.SalesId;
            salesLine.insert();
        }
        
        return salesTable;
    }
    
    public void cleanup()
    {
        SalesLine salesLine;
        while select salesLine from salesLines
        {
            salesLine.delete();
        }
        salesTable.delete();
    }
}
```

**Usage:**

```xpp
[SysTestMethodAttribute]
public static void testComplexOrderWithBuilder()
{
    // Arrange — Fluent, readable test setup
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer('CUST001')
        .withDate(today())
        .addLine('ITEM001', 10, 5000)
        .addLine('ITEM002', 5, 2500)
        .withPaymentTerms('NET30')
        .build();
    
    // Act
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // Assert
    this.assertEquals(5, discount);
    
    // Cleanup
    TestSalesOrderBuilder::create().cleanup();  // Or track builder instance
}
```

### 3.4 Pattern 3: Shared Setup with `setUp()` — For Reference Data

```xpp
class SalesOrderTest extends SysTestCase
{
    // Shared reference data — created ONCE for entire test class
    public void setUp()
    {
        // Create standard customers used by multiple tests
        CustTable custTable;
        
        // Standard customer
        custTable = TestCustTable::newTest('STD001', 'Standard Customer', 'STD');
        custTable.insert();
        
        // VIP customer
        custTable = TestCustTable::newTest('VIP001', 'VIP Customer', 'VIP');
        custTable.CustGroup = 'VIP';
        custTable.insert();
        
        // Standard items
        InventTable inventTable;
        inventTable = TestInventTable::newTest('ITEM001', 'Test Item 1', 'RAW');
        inventTable.insert();
        inventTable = TestInventTable::newTest('ITEM002', 'Test Item 2', 'FG');
        inventTable.insert();
        
        // Standard warehouse
        InventLocation location;
        location.initValue();
        location.InventLocationId = 'TESTWH';
        location.Name = 'Test Warehouse';
        location.insert();
        
        // Create default InventDim for TESTWH
        InventDim inventDim;
        inventDim.initValue();
        inventDim.InventLocationId = 'TESTWH';
        InventDim::findOrCreate(inventDim);
    }
    
    public void tearDown()
    {
        // Clean up shared data
        CustTable custTable;
        while select custTable where custTable.AccountNum like 'STD%' || custTable.AccountNum like 'VIP%'
        {
            custTable.delete();
        }
        
        InventTable inventTable;
        while select inventTable where inventTable.ItemId like 'ITEM%'
        {
            inventTable.delete();
        }
        
        InventLocation location;
        while select location where location.InventLocationId == 'TESTWH'
        {
            location.delete();
        }
    }
    
    [SysTestMethodAttribute]
    public static void testStandardCustomerOrder()
    {
        // Uses shared customer 'STD001' and item 'ITEM001'
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 100, 15000)
            .build();
        
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        this.assertEquals(5, discount);
        
        salesTable.delete();  // Per-test cleanup
    }
}
```

### 3.5 Using Number Sequences for Unique IDs

**Critical:** Never hardcode IDs like `'VEND001'` in parallel test runs — they'll collide. Use number sequences or GUIDs.

```xpp
class TestDataHelper
{
    /// <summary>
    /// Generates a unique test account number using number sequence.
    /// </summary>
    public static AccountNum generateTestAccountNum(str _prefix = 'TEST')
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestAccountNum', true);
        if (!numberSeq)
        {
            // Fallback: use timestamp-based unique ID
            return strFmt('%1_%2', _prefix, DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('%1_%2', _prefix, numberSeq.num());
    }
    
    /// <summary>
    /// Generates a unique test sales ID.
    /// </summary>
    public static SalesId generateTestSalesId()
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestSalesId', true);
        if (!numberSeq)
        {
            return strFmt('TESTSO_%1', DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('TESTSO_%1', numberSeq.num());
    }
    
    /// <summary>
    /// Generates a unique test item ID.
    /// </summary>
    public static ItemId generateTestItemId()
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestItemId', true);
        if (!numberSeq)
        {
            return strFmt('TESTITEM_%1', DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('TESTITEM_%1', numberSeq.num());
    }
}

// Usage in factory classes
class TestVendTable
{
    public static VendTable construct()
    {
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = TestDataHelper::generateTestAccountNum('VEND');
        vendTable.Name = strFmt('Test Vendor %1', vendTable.AccountNum);
        // ... other defaults
        return vendTable;
    }
}
```

**Number Sequence Setup (in model):**

```xml
<!-- Number sequence references in model manifest -->
<NumberSequenceReferences>
    <NumberSequenceReference>
        <Name>TestAccountNum</Name>
        <Description>Test vendor/customer account numbers</Description>
        <Scope>Company</Scope>
        <Format>TEST_####</Format>
    </NumberSequenceReference>
    <NumberSequenceReference>
        <Name>TestSalesId</Name>
        <Description>Test sales order IDs</Description>
        <Scope>Company</Scope>
        <Format>TESTSO_######</Format>
    </NumberSequenceReference>
</NumberSequenceReferences>
```

### 3.6 Pattern 4: CompanyData / Data Partition Isolation

For tests that need specific company data:

```xpp
class CrossCompanyTest extends SysTestCase
{
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::AutoRollback)]
    public static void testCrossCompanyDataAccess()
    {
        // Switch to specific company for test
        changeCompany('USMF')
        {
            // Create data in USMF
            CustTable custTable = TestCustTable::construct();
            custTable.insert();
            
            // Verify visible in USMF
            CustTable found = CustTable::find(custTable.AccountNum);
            this.assertNotNull(found.RecId);
        }
        
        // Data automatically rolled back due to AutoRollback
    }
}
```

---

## 4. Test Isolation and Data-Driven Testing

### 4.1 Test Isolation — Why It Matters

**Test isolation** means each test runs independently — no test depends on another's data or state. Without isolation:
- Tests pass/fail depending on run order
- Parallel test execution fails
- Debugging becomes a nightmare

### 4.2 `SysTestTransactionAttribute` — Transaction Isolation Modes

```xpp
class IsolationModeExamples extends SysTestCase
{
    // DEFAULT: AutoRollback — Best isolation, fastest
    // Uses SQL savepoints — all changes rolled back automatically
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::AutoRollback)]
    public static void testWithAutoRollback()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // No cleanup needed — AutoRollback handles it
        this.assertNotNull(VendTable::find(vendTable.AccountNum).RecId);
    }
    
    // LegacyRollback — Tracks INSERTs, deletes them on cleanup
    // Use when testing concurrency/locking behavior
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::LegacyRollback)]
    public static void testWithLegacyRollback()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // Inserts tracked, deleted after test
        this.assertNotNull(VendTable::find(vendTable.AccountNum).RecId);
    }
    
    // LegacyRollbackWithUpdateTracking — Tracks INSERT, UPDATE, DELETE
    // Slowest — use only when testing complex transactional behavior
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::LegacyRollbackWithUpdateTracking)]
    public static void testWithFullTracking()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        vendTable.CreditMax = 999999;
        vendTable.update();  // Tracked and reverted
        
        this.assertEquals(999999, VendTable::find(vendTable.AccountNum).CreditMax);
        // Reverted after test
    }
    
    // None — NO isolation, data persists
    // ONLY for debugging — NEVER in committed tests
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::None)]
    public static void testWithNoIsolation_DebugOnly()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // Data remains in database after test!
        // Use to inspect data in browser/SQL after test runs
        // REMOVE THIS ATTRIBUTE BEFORE COMMITTING
    }
}
```

| Mode | Isolation Level | Speed | Use Case |
|------|-----------------|-------|----------|
| `AutoRollback` | ✅ Full (savepoints) | ⚡ Fastest | **Default — use for 95% of tests** |
| `LegacyRollback` | ⚠️ INSERT only | 🐢 Slower | Concurrency/locking tests |
| `LegacyRollbackWithUpdateTracking` | ⚠️ INSERT/UPDATE/DELETE | 🐢🐢 Slowest | Complex transaction tests |
| `None` | ❌ None | ⚡ Fast | **Debugging only — never commit** |

### 4.3 Database Snapshots — Advanced Isolation

For integration tests needing clean database state:

```xpp
class DatabaseSnapshotTest extends SysTestCase
{
    // Use with Tier-2+ environments that support database snapshots
    // Not available in standard Tier-1 dev boxes
    
    [SysTestMethodAttribute]
    public static void testWithSnapshot()
    {
        // This requires LCS environment with snapshot capability
        // Typically used in Test/QA environments, not dev
        
        // 1. Create snapshot before test suite
        // 2. Run tests
        // 3. Restore snapshot after test suite
        
        // Implementation is environment-specific
        // See: LCS documentation on database refresh/snapshots
    }
}
```

### 4.4 Data-Driven Testing with `SysTestRow` (v10.0.25+)

Test multiple inputs with a single test method — each row becomes a separate test result.

```xpp
class MathTests extends SysTestCase
{
    // Each SysTestRow = one test execution
    // Results appear as: squareTests#1, squareTests#2, etc.
    [SysTestMethodAttribute,
    SysTestRow(0, 0),
    SysTestRow(1, 1),
    SysTestRow(2, 4),
    SysTestRow(3, 9),
    SysTestRow(4, 16),
    SysTestRow(-1, 1),
    SysTestRow(-2, 4),
    SysTestRow(-3, 9)]
    public static void squareTests(int _value, int _expected)
    {
        int result = MathHelper::square(_value);
        this.assertEquals(_expected, result, strFmt('Square of %1 should be %2', _value, _expected));
    }
    
    // Disable specific rows with SysTestRowInactive
    [SysTestMethodAttribute,
    SysTestRow(10, 100),
    SysTestRowInactive(11, 121),  // This row will be skipped
    SysTestRow(12, 144)]
    public static void squareTests_LargerNumbers(int _value, int _expected)
    {
        int result = MathHelper::square(_value);
        this.assertEquals(_expected, result);
    }
}
```

**Data-Driven Discount Test Example:**

```xpp
class SalesOrderDiscountDataDrivenTest extends SysTestCase
{
    // Test data: CustomerType, OrderAmount, ExpectedDiscount, TestDescription
    [SysTestMethodAttribute,
    SysTestRow('Standard', 5000, 0, 'Standard customer under $10K'),
    SysTestRow('Standard', 10000, 5, 'Standard customer at $10K boundary'),
    SysTestRow('Standard', 15000, 5, 'Standard customer over $10K'),
    SysTestRow('Standard', 50000, 15, 'Standard customer at $50K boundary'),
    SysTestRow('Standard', 60000, 15, 'Standard customer over $50K'),
    SysTestRow('VIP', 5000, 10, 'VIP customer under $10K'),
    SysTestRow('VIP', 10000, 15, 'VIP customer at $10K (10% VIP + 5% standard)'),
    SysTestRow('VIP', 50000, 25, 'VIP customer at $50K (10% VIP + 15% volume)'),
    SysTestRow('VIP', 60000, 25, 'VIP customer over $50K'),
    SysTestRow('VIP', 100000, 30, 'VIP large order capped at 30%')]
    public static void testDiscountCalculation(
        CustGroup _custGroup, 
        Amount _orderAmount, 
        Real _expectedDiscount,
        str _description)
    {
        // ARRANGE — Create customer and order using parameters
        CustTable custTable = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('CUST'), 
            _custGroup, 
            1000000
        );
        custTable.insert();
        
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer(custTable.AccountNum)
            .addLine('ITEM001', 1, _orderAmount)
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(_expectedDiscount, discount, _description);
        
        // CLEANUP (not needed with AutoRollback, but explicit is clear)
        salesTable.delete();
        custTable.delete();
    }
}
```

### 4.5 Test Filtering Attributes — Organize Test Runs

```xpp
class SalesOrderTest extends SysTestCase
{
    // Category: Run in specific pipelines (CheckIn, Nightly, Integration)
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]  // Higher = runs first (1-10)
    [SysTestOwner('john.doe@company.com')]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'DiscountCalculation')]
    [SysTestMethodAttribute]
    public static void testStandardDiscount()
    {
        // Fast unit test — runs in every check-in build
    }
    
    [SysTestCategory('Nightly')]
    [SysTestPriority(5)]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'DiscountCalculation')]
    [SysTestMethodAttribute]
    public static void testComplexDiscountScenarios()
    {
        // Slower integration test — runs nightly
    }
    
    [SysTestCategory('Integration')]
    [SysTestPriority(10)]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'EndToEnd')]
    [SysTestMethodAttribute]
    public static void testFullOrderToInvoiceFlow()
    {
        // Full integration test — runs in test environment
    }
}
```

**CI/CD Pipeline Filtering:**

```yaml
# Azure DevOps — Run only CheckIn category tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'TestCategory=CheckIn'

# Run only Priority 1-3 tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'Priority<=3'

# Run only Sales module tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'Property=module=Sales'
```

---

## 5. Test Coverage Metrics in LCS

### 5.1 What LCS Coverage Measures

LCS (Lifecycle Services) provides **code coverage metrics** when you run tests in a build pipeline:

| Metric | Definition | Target |
|--------|------------|--------|
| **Line Coverage** | % of executable lines executed by tests | > 80% |
| **Method Coverage** | % of methods called by tests | > 75% |
| **Class Coverage** | % of classes with at least one test | > 70% |
| **Assembly Coverage** | % of assemblies covered | > 80% |

### 5.2 Enabling Code Coverage in Build Pipeline

```yaml
# Azure DevOps pipeline — Full coverage configuration
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'windows-latest'

variables:
  - name: BuildConfiguration
    value: 'Release'
  - name: CollectCoverage
    value: 'true'

steps:
# ... restore, build steps ...

# Run tests with coverage collection
- task: Dynamics365Test@1
  displayName: 'Run SysTest with Coverage'
  inputs:
    solution: '**/*.sln'
    testClasses: '*Test'
    configuration: '$(BuildConfiguration)'
    collectCoverage: true
    coverageThreshold: 70  # Fail build if coverage < 70%
    publishResults: true

# Publish coverage to LCS
- task: PublishCodeCoverageResults@1
  displayName: 'Publish Coverage to LCS'
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
    reportDirectory: '$(Agent.TempDirectory)/**/coverage/'
    failIfCoverageEmpty: true
```

### 5.3 Interpreting LCS Coverage Reports

**LCS Coverage Tab — Key Views:**

1. **Coverage Summary** — Overall percentages by assembly
2. **Class Coverage** — Drill into specific classes
3. **Method Coverage** — See which methods are untested
4. **Line Coverage** — Line-by-line highlighting (green=covered, red=uncovered)

**Reading the Report:**

```
┌─────────────────────────────────────────────────────────────┐
│ Coverage Summary                                            │
├──────────────────┬──────────┬──────────┬──────────┬─────────┤
│ Assembly         │ Lines    │ Methods  │ Classes  │ Status  │
├──────────────────┼──────────┼──────────┼──────────┼─────────┤
│ Acme.Sales       │ 87%      │ 82%      │ 90%      │ ✅ Pass │
│ Acme.Inventory   │ 45%      │ 38%      │ 52%      │ ❌ Fail │
│ Acme.Finance     │ 72%      │ 68%      │ 75%      │ ⚠️ Warn │
└──────────────────┴──────────┴──────────┴──────────┴─────────┘
```

**Action Items by Coverage Level:**

| Coverage | Action |
|----------|--------|
| **> 80%** | ✅ Excellent — maintain |
| **60–80%** | 📝 Good — add tests for critical untested paths |
| **40–60%** | ⚠️ Moderate — prioritize testing core business logic |
| **< 40%** | 🚨 Low — block merge, require test plan |

### 5.4 Coverage ≠ Quality — Critical Distinction

```xpp
// BAD: High coverage, low quality
[SysTestMethodAttribute]
public static void testCalculateDiscount_CoverageOnly()
{
    SalesTable salesTable = TestSalesTable::construct();
    salesTable.insert();
    
    SalesOrderDiscount discount = SalesOrderDiscount::construct();
    Real result = discount.calculateDiscount(salesTable);
    
    // Only checks method runs — doesn't verify CORRECTNESS
    this.assertNotNull(result);  // Weak assertion!
    
    salesTable.delete();
}

// GOOD: Lower coverage, high quality
[SysTestMethodAttribute]
public static void testCalculateDiscount_VerifiesBusinessRules()
{
    // Test exact business rule: 5% for orders > $10K
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer('STD001')
        .addLine('ITEM001', 100, 15000)  // $15K order
        .build();
    
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // Verifies CORRECT behavior, not just execution
    this.assertEquals(5.0, discount, 'Standard discount should be 5% for orders > $10K');
    
    salesTable.delete();
}
```

**Best Practice:** Aim for **meaningful coverage** — test edge cases, error paths, and business rule boundaries. A test that covers 10 lines with 5 assertions is better than one covering 50 lines with 1 assertion.

---

## 6. Integration Testing with LCS Test Case Management

### 6.1 LCS Test Case Management Overview

LCS provides **Test Case Management** — a bridge between manual test cases and automated SysTest methods.

```
┌────────────────────────────────────────────────────────────────────┐
│                    LCS TEST CASE LIFECYCLE                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [1] DEFINE              [2] AUTOMATE              [3] EXECUTE    │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐   │
│  │ Test Plan   │───────▶│ Map to      │───────▶│ Run in      │   │
│  │ Test Suite  │        │ SysTest     │        │ Environment │   │
│  │ Test Cases  │        │ Methods     │        │ (Dev/Test/  │   │
│  └─────────────┘        └─────────────┘        │  UAT)       │   │
│         │                      │               └──────┬──────┘   │
│         ▼                      ▼                      ▼          │
│  [4] TRACK               [5] REPORT              [6] PROMOTE   │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐   │
│  │ Execution   │        │ Pass/Fail   │        │ Gate to     │   │
│  │ History     │        │ Metrics     │        │ Next Env    │   │
│  │ Screenshots │        │ Coverage    │        │             │   │
│  └─────────────┘        └─────────────┘        └─────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.2 Creating Test Cases in LCS

**Step 1: Create Test Plan**
1. Navigate to LCS Project → **Test Management** → **Test Plans**
2. Click **New Test Plan**
3. Name: `Sprint 23 - Sales Order Discount Feature`
4. Select **Test Suite** structure (e.g., by module/feature)

**Step 2: Create Test Cases**
For each test case:

| Field | Value | Example |
|-------|-------|---------|
| **Title** | Descriptive name | `Validate VIP + Volume discount stacks to 25%` |
| **Area** | Module/Feature | `Sales / Discount Calculation` |
| **Priority** | 1=Critical, 2=High, 3=Medium | `1` |
| **Automation Status** | Automated/Manual/Not Automated | `Automated` |
| **Associated Test Method** | SysTest class::method | `SalesOrderDiscountTest::testVIPVolumeDiscount_Over50K` |
| **Test Steps** | Step-by-step | See below |
| **Expected Result** | What should happen | `Discount = 25%` |
| **Test Data** | Required data | `VIP customer, order > $50K` |

**Test Steps Example:**
```
1. Create VIP customer (CustGroup = VIP)
2. Create sales order for VIP customer
3. Add line with amount > $50,000
4. Calculate discount
5. Verify discount = 25% (10% VIP + 15% Volume)
```

### 6.3 Associating SysTest Methods with LCS Test Cases

**Method 1: Naming Convention (Automatic)**
```xpp
class SalesOrderDiscountTest extends SysTestCase
{
    // LCS auto-matches by method name if "Automation Status = Automated"
    [SysTestMethodAttribute]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // LCS Test Case: "Validate VIP + Volume discount stacks to 25%"
    }
}
```

**Method 2: Explicit Mapping (Test Properties)**
```xpp
class SalesOrderDiscountTest extends SysTestCase
{
    [SysTestMethodAttribute]
    [SysTestProperty('lcsTestCaseId', '12345')]
    [SysTestProperty('lcsTestPlan', 'Sprint 23 - Sales Order Discount')]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // Explicitly linked to LCS Test Case ID 12345
    }
}
```

**Method 3: Test Case Management API (Advanced)**
```xpp
// For bulk import/sync from external tools (Azure DevOps, TestRail, etc.)
// Use LCS REST API to sync test cases
```

### 6.4 Running Tests in LCS

**Option A: Manual Execution (LCS UI)**
1. Go to **Test Management** → **Test Plans**
2. Select test plan → **Run** → **New Test Run**
3. Choose environment (Dev/Test/UAT)
4. Select test cases/suites
5. Click **Run** — LCS executes and shows live results

**Option B: CI/CD Pipeline (Automated)**
```yaml
# Azure DevOps — Runs tests and publishes to LCS
- task: Dynamics365Test@1
  displayName: 'Run SysTest and Publish to LCS'
  inputs:
    solution: '**/*.sln'
    testClasses: 'SalesOrderDiscountTest'
    configuration: 'Release'
    publishResults: true
    lcsProjectId: $(LCS_PROJECT_ID)
    lcsEnvironmentId: $(LCS_TEST_ENV_ID)
```

**Option C: Scheduled Runs (Nightly)**
1. LCS → **Test Management** → **Test Plans** → **Schedule**
2. Configure: Daily at 2 AM, Test Environment, All Test Cases
3. Results emailed to team, failures create work items

### 6.5 Test Execution Results in LCS

**LCS Test Run Dashboard shows:**

| Column | Description |
|--------|-------------|
| **Test Case** | Linked test case title |
| **Outcome** | Passed/Failed/Blocked/Not Run |
| **Duration** | Execution time |
| **Error Message** | Failure details (stack trace) |
| **Attachments** | Screenshots, logs |
| **Run By** | Pipeline or user |
| **Timestamp** | When executed |

**Failed Test Drill-Down:**
```
Test Case: Validate VIP + Volume discount stacks to 25%
Status: FAILED
Duration: 3.2s
Error: Assert.AreEqual failed. Expected: 25. Actual: 20.
Stack Trace:
  at SalesOrderDiscountTest.testVIPVolumeDiscount_Over50K()
  at SysTestRunner.executeTestMethod()
  
Attachments: 
  - screenshot_20240115_143201.png (order form)
  - test_log_20240115_143201.txt
```

---

## 7. Activity: Complete Test Class for Sales Order Discount Calculation

### 7.1 Requirements Recap

| Rule | Description |
|------|-------------|
| 1 | Standard discount: 5% for orders over $10,000 |
| 2 | VIP discount: 10% for VIP customers (CustGroup = 'VIP') |
| 3 | Volume discount: 15% for orders over $50,000 |
| 4 | Combined: VIP + Volume stack (25% for VIP orders > $50K) |
| 5 | No discount for orders < $10K (unless VIP = 10%) |
| 6 | Maximum discount cap: 30% |

### 7.2 Complete Test Class — Production Ready

```xpp
/// <summary>
/// Comprehensive test suite for SalesOrderDiscount calculation.
/// Covers all business rules, edge cases, and error conditions.
/// 
/// Run with: AutoRollback isolation (default)
/// Categories: CheckIn (fast), Nightly (comprehensive)
/// </summary>
class SalesOrderDiscountTest extends SysTestCase
{
    // ═══════════════════════════════════════════════════════════
    // SHARED TEST DATA — Created once for all test methods
    // ═══════════════════════════════════════════════════════════
    
    public void setUp()
    {
        // Create standard customer (non-VIP)
        CustTable stdCust = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('STD'),
            'Standard Customer',
            'STD'
        );
        stdCust.insert();
        
        // Create VIP customer
        CustTable vipCust = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('VIP'),
            'VIP Customer',
            'VIP'
        );
        vipCust.CustGroup = 'VIP';
        vipCust.insert();
        
        // Create test item
        InventTable item = TestInventTable::newTest(
            TestDataHelper::generateTestItemId(),
            'Test Item',
            'FG'
        );
        item.insert();
        
        // Create warehouse and InventDim
        InventLocation location;
        location.initValue();
        location.InventLocationId = 'TESTWH';
        location.Name = 'Test Warehouse';
        location.insert();
        
        InventDim inventDim;
        inventDim.initValue();
        inventDim.InventLocationId = 'TESTWH';
        InventDim::findOrCreate(inventDim);
    }
    
    public void tearDown()
    {
        // Clean up shared data
        CustTable custTable;
        while select custTable
            where custTable.AccountNum like 'STD%'
               || custTable.AccountNum like 'VIP%'
        {
            custTable.delete();
        }
        
        InventTable item;
        while select item
            where item.ItemId like 'TESTITEM%'
        {
            item.delete();
        }
        
        InventLocation location;
        while select location
            where location.InventLocationId == 'TESTWH'
        {
            location.delete();
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // TEST METHODS — One per business rule + edge cases
    // ═══════════════════════════════════════════════════════════
    
    /// <summary>
    /// Rule 1: Standard discount 5% for orders over $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'StandardDiscount_Over10K')]
    public static void testStandardDiscount_Over10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')  // Standard customer from setUp
            .addLine('ITEM001', 100, 15000)  // $15K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(5.0, discount, 'Standard discount should be 5% for orders over $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 2: VIP discount 10% for orders under $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'VIPDiscount_Under10K')]
    public static void testVIPDiscount_Under10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')  // VIP customer from setUp
            .addLine('ITEM001', 10, 5000)  // $5K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(10.0, discount, 'VIP discount should be 10% even for orders under $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 4: Combined VIP (10%) + Volume (15%) = 25% for orders over $50K
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'CombinedVIPVolume_Over50K')]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 500, 60000)  // $60K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(25.0, discount, 'VIP + Volume discount should be 25% for orders over $50K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 3: Volume discount 15% for non-VIP orders over $50,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'VolumeDiscount_NonVIP_Over50K')]
    public static void testVolumeDiscount_NonVIP_Over50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 500, 60000)  // $60K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(15.0, discount, 'Volume discount should be 15% for non-VIP orders over $50K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 5: No discount for non-VIP orders under $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'NoDiscount_NonVIP_Under10K')]
    public static void testNoDiscount_Under10K_NonVIP()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 5, 5000)  // $5K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(0.0, discount, 'No discount for non-VIP orders under $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 6: Maximum discount cap of 30%
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'MaxDiscountCap_30Percent')]
    public static void testMaxDiscountCap_30Percent()
    {
        // ARRANGE — VIP + Volume + hypothetical "Special" = 35% but capped at 30%
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 1000, 100000)  // $100K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Cap enforced
        this.assertLessOrEqual(discount, 30.0, 'Discount should never exceed 30%');
        this.assertEquals(30.0, discount, 'Discount should be capped at exactly 30%');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Boundary value — exactly $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_Exactly10K')]
    public static void testBoundaryValue_Exactly10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 100, 10000)  // Exactly $10K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Boundary: >= $10K qualifies for standard discount
        this.assertEquals(5.0, discount, 'Standard discount should apply at exactly $10K (>= boundary)');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Boundary value — exactly $50,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_Exactly50K')]
    public static void testBoundaryValue_Exactly50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 500, 50000)  // Exactly $50K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Boundary: >= $50K qualifies for volume discount
        this.assertEquals(15.0, discount, 'Volume discount should apply at exactly $50K (>= boundary)');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Zero order total
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(3)]
    [SysTestProperty('rule', 'EdgeCase_ZeroTotal')]
    public static void testZeroOrderTotal()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 0, 0)  // Zero quantity and amount
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(0.0, discount, 'No discount for $0 order total');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Negative order total — should throw error
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(3)]
    [SysTestProperty('rule', 'EdgeCase_NegativeTotal')]
    public static void testNegativeOrderTotal_ThrowsError()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 1, -5000)  // Negative amount
            .build();
        
        // ASSERT — Should throw error for negative total
        this.assertException(
            classStr(SalesOrderDiscount),
            methodStr(SalesOrderDiscount, calculateDiscount),
            error::Error,
            'Negative order total should throw Error exception'
        );
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: VIP customer at exactly $10K boundary
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_VIP_Exactly10K')]
    public static void testVIPBoundary_Exactly10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 100, 10000)  // Exactly $10K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — VIP gets 10% + standard 5% = 15% at $10K boundary
        this.assertEquals(15.0, discount, 'VIP at $10K boundary gets 10% VIP + 5% standard = 15%');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Data-Driven Test: Multiple scenarios in one method
    /// </summary>
    [SysTestMethodAttribute,
    SysTestRow('STD', 5000, 0, 'Standard < 10K'),
    SysTestRow('STD', 10000, 5, 'Standard = 10K'),
    SysTestRow('STD', 15000, 5, 'Standard > 10K'),
    SysTestRow('STD', 50000, 15, 'Standard = 50K'),
    SysTestRow('STD', 60000, 15, 'Standard > 50K'),
    SysTestRow('VIP', 5000, 10, 'VIP < 10K'),
    SysTestRow('VIP', 10000, 15, 'VIP = 10K (10+5)'),
    SysTestRow('VIP', 15000, 15, 'VIP > 10K (10+5)'),
    SysTestRow('VIP', 50000, 25, 'VIP = 50K (10+15)'),
    SysTestRow('VIP', 60000, 25, 'VIP > 50K (10+15)'),
    SysTestRow('VIP', 100000, 30, 'VIP large capped at 30%')]
    [SysTestCategory('Nightly')]
    [SysTestPriority(5)]
    [SysTestProperty('rule', 'DataDriven_AllScenarios')]
    public static void testDiscountCalculation_DataDriven(
        CustGroup _custGroup,
        Amount _orderAmount,
        Real _expectedDiscount,
        str _description)
    {
        // ARRANGE
        AccountNum custAccount = _custGroup == 'VIP' ? 'VIP001' : 'STD001';
        
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer(custAccount)
            .addLine('ITEM001', 1, _orderAmount)
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(_expectedDiscount, discount, _description);
        
        // CLEANUP
        salesTable.delete();
    }
}
```

### 7.3 Supporting Classes (Factory & Builder)

```xpp
/// <summary>
/// Test data factory for CustTable
/// </summary>
class TestCustTable
{
    public static CustTable newTest(AccountNum _accountNum, str _name, CustGroup _custGroup)
    {
        CustTable custTable;
        custTable.initValue();
        custTable.AccountNum = _accountNum;
        custTable.Name = _name;
        custTable.CustGroup = _custGroup;
        custTable.Currency = 'USD';
        custTable.PaymTermId = 'NET30';
        custTable.InvoiceAccount = _accountNum;
        return custTable;
    }
}

/// <summary>
/// Test data factory for InventTable
/// </summary>
class TestInventTable
{
    public static InventTable newTest(ItemId _itemId, str _name, ItemType _itemType)
    {
        InventTable item;
        item.initValue();
        item.ItemId = _itemId;
        item.Name = _name;
        item.ItemType = _itemType;
        item.ItemGroupId = 'RAW';
        item.UnitId = 'EA';
        item.PurchUnit = 'EA';
        item.SalesUnit = 'EA';
        item.InventUnit = 'EA';
        return item;
    }
}

/// <summary>
/// Fluent builder for SalesTable with lines
/// </summary>
class TestSalesOrderBuilder
{
    SalesTable salesTable;
    List salesLines;
    
    private void new()
    {
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.SalesDate = today();
        salesLines = new List(Types::Record);
    }
    
    public static TestSalesOrderBuilder create()
    {
        return new TestSalesOrderBuilder();
    }
    
    public TestSalesOrderBuilder withCustomer(CustAccount _custAccount)
    {
        salesTable.CustomerAccount = _custAccount;
        salesTable.initFromCustTable(CustTable::find(_custAccount));
        return this;
    }
    
    public TestSalesOrderBuilder withSalesId(SalesId _salesId)
    {
        salesTable.SalesId = _salesId;
        return this;
    }
    
    public TestSalesOrderBuilder addLine(ItemId _itemId, Qty _qty, Amount _lineAmount)
    {
        SalesLine line;
        line.initValue();
        line.ItemId = _itemId;
        line.SalesQty = _qty;
        line.LineAmount = _lineAmount;
        line.initFromInventTable(InventTable::find(_itemId));
        line.InventDimId = InventDim::findOrCreate(InventDim::construct().parmInventLocationId('TESTWH')).InventDimId;
        salesLines.addEnd(line);
        return this;
    }
    
    public SalesTable build()
    {
        // Generate unique SalesId if not set
        if (!salesTable.SalesId)
        {
            salesTable.SalesId = NumberSeq::newGetNum(SalesParameters::numRefSalesId()).num();
        }
        
        salesTable.insert();
        
        SalesLine line;
        while select line from salesLines
        {
            line.SalesTableId = salesTable.SalesId;
            line.SalesId = salesTable.SalesId;
            line.insert();
        }
        
        return salesTable;
    }
}
```

### 7.4 Implementation Under Test (Reference)

```xpp
/// <summary>
/// Discount calculation service — implementation being tested
/// </summary>
class SalesOrderDiscount
{
    private const Real StandardDiscountPercent = 5.0;
    private const Real VIPDiscountPercent = 10.0;
    private const Real VolumeDiscountPercent = 15.0;
    private const Real MaxDiscountPercent = 30.0;
    private const Amount StandardThreshold = 10000;
    private const Amount VolumeThreshold = 50000;
    
    public static SalesOrderDiscount construct()
    {
        return new SalesOrderDiscount();
    }
    
    public Real calculateDiscount(SalesTable _salesTable)
    {
        if (!_salesTable)
        {
            throw error('Sales table cannot be null');
        }
        
        Amount orderTotal = this.getOrderTotal(_salesTable);
        
        if (orderTotal < 0)
        {
            throw error('Order total cannot be negative');
        }
        
        if (orderTotal == 0)
        {
            return 0;
        }
        
        Real discount = 0;
        boolean isVIP = this.isVIPCustomer(_salesTable.CustomerAccount);
        
        // Standard discount
        if (orderTotal >= StandardThreshold)
        {
            discount += StandardDiscountPercent;
        }
        
        // VIP discount (applies regardless of order amount)
        if (isVIP)
        {
            discount += VIPDiscountPercent;
        }
        
        // Volume discount
        if (orderTotal >= VolumeThreshold)
        {
            discount += VolumeDiscountPercent;
        }
        
        // Apply cap
        return discount > MaxDiscountPercent ? MaxDiscountPercent : discount;
    }
    
    private Amount getOrderTotal(SalesTable _salesTable)
    {
        Amount total;
        select sum(LineAmount) from SalesLine
            where SalesLine.SalesId == _salesTable.SalesId;
        return total;
    }
    
    private boolean isVIPCustomer(CustAccount _custAccount)
    {
        CustTable custTable = CustTable::find(_custAccount);
        return custTable && custTable.CustGroup == 'VIP';
    }
}
```

---

## 8. Best Practices, Common Mistakes, and CI/CD Integration

### 8.1 Best Practices — AAA Pattern

**Arrange → Act → Assert** — Structure every test method:

```xpp
[SysTestMethodAttribute]
public static void testExample()
{
    // ═══ ARRANGE ═══ — Set up test data and conditions
    VendTable vendTable = TestVendTable::construct();
    vendTable.CreditMax = 600000;
    vendTable.insert();
    
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer(vendTable.AccountNum)
        .addLine('ITEM001', 100, 15000)
        .build();
    
    // ═══ ACT ═══ — Execute the code under test (ONE line ideally)
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // ═══ ASSERT ═══ — Verify the outcome
    this.assertEquals(5.0, discount, 'Standard discount should be 5%');
    
    // CLEANUP (optional with AutoRollback)
    salesTable.delete();
    vendTable.delete();
}
```

### 8.2 Test Naming Conventions

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `test<Method>_<Scenario>_<Expected>` | `testCalculateDiscount_VIPOver50K_Returns25` | **Recommended** — clear intent |
| `test<BusinessRule>_<Condition>` | `testStandardDiscount_Over10K` | Simple rules |
| `test<Feature>_<EdgeCase>` | `testDiscount_BoundaryExactly10K` | Edge cases |
| `test<Method>_Throws<Exception>` | `testCalculateDiscount_ThrowsOnNegative` | Error cases |

**Avoid:**
- `test1()`, `test2()` — meaningless
- `testDiscount()` — too vague
- `test_CalculateDiscount_ShouldReturn5Percent()` — C# style, not X++

### 8.3 Common Mistakes — And How to Fix Them

| Mistake | Problem | Fix |
|---------|---------|-----|
| **No isolation** — Tests share data without `AutoRollback` | Flaky tests, order-dependent | Use `[SysTestTransaction(SysTestTransactionMode::AutoRollback)]` |
| **Hardcoded IDs** — `'VEND001'` in multiple tests | Collisions in parallel runs | Use `NumberSeq` or `TestDataHelper::generateTestAccountNum()` |
| **Testing implementation, not behavior** | Brittle tests that break on refactor | Test business outcomes, not internal methods |
| **Missing edge cases** — Only happy path | Bugs in production | Test boundaries, nulls, negatives, empty collections |
| **Weak assertions** — `assertNotNull(result)` | Doesn't verify correctness | Use `assertEquals(expected, actual)` with specific values |
| **No cleanup** — Test data leaks | Pollutes environment, slows tests | Use `AutoRollback` or explicit `delete()` in `tearDown()` |
| **Testing multiple things in one test** | Hard to diagnose failures | One assertion concept per test method |
| **Slow tests** — Creating full form runs | CI/CD pipeline too slow | Unit test logic classes, not forms; use `AutoRollback` |

### 8.4 Running Tests in Visual Studio

**Test Explorer:**
1. Build solution (`Ctrl+Shift+B`)
2. Open **Test Explorer**: `Test` → `Test Explorer`
3. Tests appear grouped by class
4. Right-click → **Run Selected Tests** or **Run All**

**Test Explorer Columns to Enable:**
- **Duration** — Spot slow tests
- **Traits** — See Category, Priority, Owner

**Filtering in Test Explorer:**
```
Trait:Category=CheckIn      // Run only check-in tests
Trait:Priority<=3           // Run priority 1-3
Trait:module=Sales          // Run Sales module tests
```

**Debugging Tests:**
1. Set breakpoint in test method
2. Test Explorer → Right-click test → **Debug**
3. Step through code, inspect variables

### 8.5 CI/CD Pipeline Integration

**Complete Azure DevOps Pipeline:**

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - release/*

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'd365-build-variables'
  - name: BuildConfiguration
    value: 'Release'
  - name: TestFilter
    value: 'TestCategory=CheckIn'  # Fast tests for PR validation

stages:
- stage: Build
  displayName: 'Build & Test'
  jobs:
  - job: BuildAndTest
    displayName: 'Build Solution and Run Tests'
    timeoutInMinutes: 60
    steps:
    # 1. Restore NuGet
    - task: NuGetCommand@2
      displayName: 'Restore NuGet Packages'
      inputs:
        command: 'restore'
        feedsToUse: 'config'
        nugetConfigPath: 'nuget.config'

    # 2. Build Solution
    - task: MSBuild@1
      displayName: 'Build D365 F&O Solution'
      inputs:
        solution: '**/*.sln'
        platform: 'Any CPU'
        configuration: '$(BuildConfiguration)'
        msbuildArguments: >
          /p:BuildTasksDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage\DevAlm"
          /p:MetadataDirectory="$(Build.SourcesDirectory)\Metadata"
          /p:FrameworkDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage"
          /p:ReferenceFolder="$(Pipeline.Workspace)\NuGets"
          /p:OutputDirectory="$(Build.BinariesDirectory)"

    # 3. Run SysTest with Coverage
    - task: Dynamics365Test@1
      displayName: 'Run SysTest Unit Tests'
      inputs:
        solution: '**/*.sln'
        testClasses: '*Test'
        configuration: '$(BuildConfiguration)'
        testFilter: '$(TestFilter)'
        collectCoverage: true
        coverageThreshold: 70
        publishResults: true
        lcsProjectId: $(LCS_PROJECT_ID)
        lcsEnvironmentId: $(LCS_BUILD_ENV_ID)

    # 4. Publish Coverage Report
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Coverage to Azure DevOps'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
        reportDirectory: '$(Agent.TempDirectory)/**/coverage/'

    # 5. Publish Test Results
    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '**/TestResults/*.trx'
        mergeTestResults: true
        failTaskOnFailedTests: true

- stage: NightlyTests
  displayName: 'Nightly Full Test Suite'
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - job: NightlyTests
    displayName: 'Run All Tests Including Nightly Category'
    steps:
    - task: Dynamics365Test@1
      displayName: 'Run Full Test Suite'
      inputs:
        solution: '**/*.sln'
        testClasses: '*Test'
        configuration: 'Release'
        testFilter: ''  # No filter = all tests
        collectCoverage: true
        coverageThreshold: 75
        publishResults: true
        lcsProjectId: $(LCS_PROJECT_ID)
        lcsEnvironmentId: $(LCS_TEST_ENV_ID)

- stage: DeployToTest
  displayName: 'Deploy to Test Environment'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: DeployTest
    displayName: 'Deploy to Test Environment'
    environment: 'Test'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: Dynamics365Deploy@1
            inputs:
              lcsProjectId: $(LCS_PROJECT_ID)
              lcsEnvironmentId: $(LCS_TEST_ENV_ID)
              deployablePackage: '$(Build.ArtifactStagingDirectory)/*.zip'
```

### 8.6 Release Gates with Test Results

```yaml
# Release pipeline — Gate on test results
stages:
- stage: DeployToUAT
  displayName: 'Deploy to UAT'
  dependsOn: DeployToTest
  condition: succeeded()
  jobs:
  - deployment: DeployUAT
    environment: 'UAT'
    strategy:
      runOnce:
        preDeploy:
          steps:
          # Gate: Check test results from Test environment
          - task: AzureCLI@2
            displayName: 'Verify Test Results in LCS'
            inputs:
              azureSubscription: '$(AzureSubscription)'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Query LCS API for test results
                # Fail if any CheckIn tests failed in Test env
                TEST_RESULTS=$(az rest --method get \
                  --url "https://lcsapi.lcs.dynamics.com/api/v1/projects/$(LCS_PROJECT_ID)/environments/$(LCS_TEST_ENV_ID)/testresults" \
                  --query "value[?contains(testClass, 'Test') && outcome!='Passed']")
                
                if [ "$TEST_RESULTS" != "[]" ]; then
                  echo "##vso[task.logissue type=error]Failed tests found in Test environment"
                  echo "$TEST_RESULTS"
                  exit 1
                fi
                echo "All tests passed in Test environment"
        deploy:
          steps:
          - task: Dynamics365Deploy@1
            inputs:
              lcsProjectId: $(LCS_PROJECT_ID)
              lcsEnvironmentId: $(LCS_UAT_ENV_ID)
              deployablePackage: '$(Build.ArtifactStagingDirectory)/*.zip'
```

---

## Summary Checklist

| ✅ | Item |
|----|------|
| **Framework** | Extend `SysTestCase`, use `[SysTestMethodAttribute]`, implement `setUp()`/`tearDown()` |
| **Assertions** | Use `assertEquals`, `assertTrue`, `assertException`, `assertError` — avoid weak assertions |
| **Test Data** | Factory classes with `construct()`/`newTest()`, use NumberSeq for unique IDs |
| **Isolation** | Default `AutoRollback` — never use `None` in committed code |
| **Data-Driven** | Use `SysTestRow` for parameterized tests (v10.0.25+) |
| **Filtering** | Tag tests with `SysTestCategory`, `SysTestPriority`, `SysTestProperty` |
| **Coverage** | Enable in CI/CD, target >80% line coverage, focus on meaningful tests |
| **LCS Integration** | Map test cases, run in pipeline, gate deployments on test results |
| **Naming** | `test<Method>_<Scenario>_<Expected>` — clear and searchable |
| **CI/CD** | Run CheckIn tests on PR, Nightly on main, gate deployments on results |

---

## Microsoft Learn References

| Topic | Link |
|-------|------|
| SysTest Framework Overview | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework |
| Unit Testing in D365 F&O | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/unit-testing |
| Test Automation | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-automation |
| SysTest Attributes | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-attributes |
| Test Coverage in LCS | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-coverage |
| LCS Test Case Management | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lifecycle-services/test-case-management |
| Azure DevOps Test Task | https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/test/dynamics-365-test |

---

*Last Updated: November 2024*  
*Part of the D365 F&O Developer Handbook — Chapter 12*