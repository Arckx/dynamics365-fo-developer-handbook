---
name: d365-testing-patterns
description: D365 F&O testing patterns — property-based testing, test data factories, SysTest + TestFramework integration
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Testing Patterns Guide

> **Target audience:** Developers writing unit, integration, and property-based tests for D365 F&O. Assumes SysTest basics.

---

## 1. Testing Strategy Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      TEST PYRAMID                                │
│                                                                  │
│                    ┌─────────────┐                               │
│                    │   E2E/UI    │  ← Few (5%)  - RSAT, Manual   │
│                   └─────────────┘                               │
│              ┌───────────────────┐                              │
│              │  Integration      │  ← Some (15%) - SysTest + DB │
│             └───────────────────┘                              │
│       ┌───────────────────────────────┐                        │
│       │   Unit (Property-Based)       │  ← Many (80%) - Fast  │
│      └───────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

| Test Type | Speed | Scope | Tools | When to Run |
|-----------|-------|-------|-------|-------------|
| **Unit** | <100ms | Single class/method | SysTest, Property-based | Every build |
| **Integration** | 1-30s | Cross-table, services | SysTest + Test Data | PR validation |
| **E2E** | 30s-5min | Full user flows | RSAT, Playwright | Nightly/Release |

---

## 2. Property-Based Testing in X++

### 2.1 Why Property-Based Testing?

Traditional unit tests check **specific examples**. Property-based tests verify **invariants** across **thousands of generated inputs**.

```xpp
// Traditional: One example
[SysTestMethod]
public void testQtyPositive()
{
    InventQty qty = 10;
    assertTrue(qty > 0);
}

// Property-based: Thousands of examples
[SysTestMethod]
public void testQtyInvariant_NonNegative()
{
    // Property: Qty must never be negative after any operation
    // Generator: Random positive/negative quantities
    // Shrinker: Finds minimal failing case
}
```

### 2.2 FsCheck Port for X++ (Custom Implementation)

Since X++ doesn't have FsCheck, we build a lightweight generator framework:

```xpp
/// <summary>
/// Property-based testing utilities for X++
/// </summary>
class PropertyTest
{
    /// <summary>
    /// Runs a property test with random generation
    /// </summary>
    public static void check(
        str _propertyName,
        int _iterations,
        SysTestCase _testCase,
        delegate boolean _property(anytype _input),
        delegate anytype _generator(),
        delegate anytype _shrinker(anytype _input) = null)
    {
        int i;
        anytype input;
        boolean result;
        anytype shrunk;
        ;
        
        for (i = 1; i <= _iterations; i++)
        {
            input = _generator();
            result = _property(input);
            
            if (!result)
            {
                // Try to shrink to minimal failing case
                if (_shrinker)
                {
                    shrunk = _shrinker(input);
                    while (shrunk != input && !_property(shrunk))
                    {
                        input = shrunk;
                        shrunk = _shrinker(input);
                    }
                }
                
                _testCase.fail(strFmt("Property '%1' failed on iteration %2 with input: %3", 
                    _propertyName, i, anytype2str(input)));
                return;
            }
        }
        
        _testCase.pass(strFmt("Property '%1' passed %2 iterations", _propertyName, _iterations));
    }
}

/// <summary>
/// Generators for common types
/// </summary>
class Generators
{
    public static int genInt(int _min = -1000, int _max = 1000)
    {
        return _min + (new Random().nextInt() % (_max - _min + 1));
    }
    
    public static real genReal(real _min = -1000.0, real _max = 1000.0)
    {
        return _min + (new Random().nextReal() * (_max - _min));
    }
    
    public static str genString(int _maxLen = 50)
    {
        str chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -_.";
        str result = "";
        int len = Generators::genInt(0, _maxLen);
        int i;
        for (i = 1; i <= len; i++)
        {
            result += subStr(chars, Generators::genInt(1, strLen(chars)), 1);
        }
        return result;
    }
    
    public static date genDate(date _min = mkDate(1,1,2000), date _max = mkDate(31,12,2050))
    {
        int daysDiff = _max - _min;
        return _min + Generators::genInt(0, daysDiff);
    }
    
    public static AmountMST genAmount(AmountMST _min = -1000000, AmountMST _max = 1000000)
    {
        return Generators::genReal(_min, _max);
    }
    
    public static List(anytype) genList(delegate anytype _elementGen, int _maxSize = 10)
    {
        List list = new List(Types::AnyType);
        int size = Generators::genInt(0, _maxSize);
        int i;
        for (i = 1; i <= size; i++)
        {
            list.addEnd(_elementGen());
        }
        return list;
    }
    
    // Shrinkers
    public static int shrinkInt(int _value)
    {
        if (_value == 0) return 0;
        return _value > 0 ? _value - 1 : _value + 1;
    }
    
    public static str shrinkString(str _value)
    {
        if (strLen(_value) <= 1) return "";
        return subStr(_value, 1, strLen(_value) - 1);
    }
}
```

### 2.3 Property Test Examples

```xpp
/// <summary>
/// Property-based tests for Inventory Qty operations
/// </summary>
[SysTestCase]
class InventQtyPropertyTests extends SysTestCase
{
    // Property: Adding zero doesn't change quantity
    [SysTestMethod]
    public void testAddZeroIdentity()
    {
        PropertyTest::check(
            "AddZeroIdentity",
            1000,
            this,
            delegate boolean(InventQty _qty)
            {
                return InventQtyOp::add(_qty, 0) == _qty;
            },
            delegate InventQty() { return Generators::genInt(-10000, 10000); },
            delegate InventQty(InventQty _q) { return Generators::shrinkInt(_q); }
        );
    }
    
    // Property: Addition is commutative
    [SysTestMethod]
    public void testAddCommutative()
    {
        PropertyTest::check(
            "AddCommutative",
            500,
            this,
            delegate boolean(List _pair)
            {
                InventQty a = _pair.item(1);
                InventQty b = _pair.item(2);
                return InventQtyOp::add(a, b) == InventQtyOp::add(b, a);
            },
            delegate List()
            {
                List pair = new List(Types::Int64);
                pair.addEnd(Generators::genInt(-1000, 1000));
                pair.addEnd(Generators::genInt(-1000, 1000));
                return pair;
            }
        );
    }
    
    // Property: Subtracting self gives zero
    [SysTestMethod]
    public void testSubtractSelfZero()
    {
        PropertyTest::check(
            "SubtractSelfZero",
            1000,
            this,
            delegate boolean(InventQty _qty)
            {
                return InventQtyOp::sub(_qty, _qty) == 0;
            },
            delegate InventQty() { return Generators::genInt(-10000, 10000); }
        );
    }
    
    // Property: Round-trip conversion (Qty → String → Qty)
    [SysTestMethod]
    public void testQtyStringRoundTrip()
    {
        PropertyTest::check(
            "QtyStringRoundTrip",
            500,
            this,
            delegate boolean(InventQty _qty)
            {
                str s = _qty;
                InventQty parsed = str2num(s);
                return parsed == _qty;
            },
            delegate InventQty() { return Generators::genInt(-10000, 10000); }
        );
    }
}

/// <summary>
/// Property-based tests for Price calculations
/// </summary>
[SysTestCase]
class PriceCalculationPropertyTests extends SysTestCase
{
    // Property: Discount never increases price
    [SysTestMethod]
    public void testDiscountNeverIncreasesPrice()
    {
        PropertyTest::check(
            "DiscountNeverIncreasesPrice",
            1000,
            this,
            delegate boolean(List _input)
            {
                Price price = _input.item(1);
                DiscPct discount = _input.item(2);
                
                Price discounted = price * (100 - discount) / 100;
                return discounted <= price;
            },
            delegate List()
            {
                List input = new List(Types::Real);
                input.addEnd(Generators::genReal(0.01, 100000));
                input.addEnd(Generators::genReal(0, 100)); // 0-100% discount
                return input;
            }
        );
    }
    
    // Property: Tax calculation is distributive
    [SysTestMethod]
    public void testTaxDistributive()
    {
        PropertyTest::check(
            "TaxDistributive",
            500,
            this,
            delegate boolean(List _input)
            {
                Price price1 = _input.item(1);
                Price price2 = _input.item(2);
                TaxRate tax = _input.item(3);
                
                Price taxOnSum = (price1 + price2) * tax / 100;
                Price sumOfTaxes = (price1 * tax / 100) + (price2 * tax / 100);
                
                // Allow small floating point difference
                return abs(taxOnSum - sumOfTaxes) < 0.01;
            },
            delegate List()
            {
                List input = new List(Types::Real);
                input.addEnd(Generators::genReal(0.01, 10000));
                input.addEnd(Generators::genReal(0.01, 10000));
                input.addEnd(Generators::genReal(0, 30)); // 0-30% tax
                return input;
            }
        );
    }
}
```

---

## 3. Test Data Factories

### 3.1 Factory Pattern for Test Data

```xpp
/// <summary>
/// Base factory for creating test entities
/// </summary>
abstract class TestDataFactory
{
    protected static Map typeFactories;
    
    static void registerFactory(TableId _tableId, SysTestDataFactory _factory)
    {
        if (!typeFactories)
            typeFactories = new Map(Types::Int64, Types::Class);
        typeFactories.insert(_tableId, _factory);
    }
    
    public static Common create(TableId _tableId, Map _overrides = null)
    {
        SysTestDataFactory factory = typeFactories.lookup(_tableId);
        if (!factory)
            throw error(strFmt("No factory registered for table %1", _tableId));
        
        return factory.create(_overrides);
    }
    
    public static List createMultiple(TableId _tableId, int _count, Map _overrides = null)
    {
        List results = new List(Types::Record);
        int i;
        for (i = 1; i <= _count; i++)
        {
            results.addEnd(TestDataFactory::create(_tableId, _overrides));
        }
        return results;
    }
}

/// <summary>
/// Interface for table-specific factories
/// </summary>
interface SysTestDataFactory
{
    Common create(Map _overrides = null);
    Map defaultValues();
}

/// <summary>
/// Customer factory with realistic defaults
/// </summary>
class CustTableTestFactory implements SysTestDataFactory
{
    public Common create(Map _overrides = null)
    {
        CustTable custTable;
        Map defaults = this.defaultValues();
        MapEnumerator enumerator;
        ;
        
        // Apply overrides
        if (_overrides)
        {
            enumerator = _overrides.getEnumerator();
            while (enumerator.moveNext())
            {
                defaults.insert(enumerator.currentKey(), enumerator.currentValue());
            }
        }
        
        // Create record
        ttsBegin;
        custTable.clear();
        custTable.AccountNum = NumberSeq::newGetNum(CustParameters::numRefCustAccount()).num();
        custTable.Name = defaults.lookup("Name");
        custTable.CustGroup = defaults.lookup("CustGroup");
        custTable.Currency = defaults.lookup("Currency");
        custTable.PaymentTerms = defaults.lookup("PaymentTerms");
        custTable.LanguageId = defaults.lookup("LanguageId");
        custTable.insert();
        ttsCommit;
        
        return custTable;
    }
    
    public Map defaultValues()
    {
        Map defaults = new Map(Types::String, Types::AnyType);
        defaults.insert("Name", strFmt("Test Customer %1", Generators::genInt(1, 9999)));
        defaults.insert("CustGroup", "10");
        defaults.insert("Currency", "USD");
        defaults.insert("PaymentTerms", "Net30");
        defaults.insert("LanguageId", "en-us");
        return defaults;
    }
}

/// <summary>
/// Sales Order factory with lines
/// </summary>
class SalesTableTestFactory implements SysTestDataFactory
{
    public Common create(Map _overrides = null)
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Map defaults = this.defaultValues();
        MapEnumerator enumerator;
        List items;
        int i;
        ;
        
        if (_overrides)
        {
            enumerator = _overrides.getEnumerator();
            while (enumerator.moveNext())
            {
                defaults.insert(enumerator.currentKey(), enumerator.currentValue());
            }
        }
        
        ttsBegin;
        salesTable.clear();
        salesTable.SalesId = NumberSeq::newGetNum(SalesParameters::numRefSalesId()).num();
        salesTable.CustAccount = defaults.lookup("CustAccount");
        salesTable.CurrencyCode = defaults.lookup("CurrencyCode");
        salesTable.DeliveryDate = defaults.lookup("DeliveryDate");
        salesTable.SalesStatus = SalesStatus::OpenOrder;
        salesTable.DocumentStatus = DocumentStatus::OpenOrder;
        salesTable.insert();
        
        // Create lines
        items = defaults.lookup("Items"); // List of [ItemId, Qty, Price]
        if (items)
        {
            for (i = 1; i <= items.elements(); i++)
            {
                List lineData = items.item(i);
                salesLine.clear();
                salesLine.SalesId = salesTable.SalesId;
                salesLine.ItemId = lineData.item(1);
                salesLine.SalesQty = lineData.item(2);
                salesLine.SalesPrice = lineData.item(3);
                salesLine.LineNum = i * 1000;
                salesLine.insert();
            }
        }
        
        ttsCommit;
        return salesTable;
    }
    
    public Map defaultValues()
    {
        // Create a customer first
        CustTable customer = TestDataFactory::create(tableNum(CustTable));
        
        Map defaults = new Map(Types::String, Types::AnyType);
        defaults.insert("CustAccount", customer.AccountNum);
        defaults.insert("CurrencyCode", "USD");
        defaults.insert("DeliveryDate", dateAdd(today(), 7));
        
        // Default items
        List items = new List(Types::Record);
        InventTable item = TestDataFactory::create(tableNum(InventTable));
        List line = new List(Types::AnyType);
        line.addEnd(item.ItemId);
        line.addEnd(10);
        line.addEnd(25.00);
        items.addEnd(line);
        
        defaults.insert("Items", items);
        return defaults;
    }
}
```

### 3.2 Factory Registration (Run Once)

```xpp
/// <summary>
/// Register all test factories - call from test suite setup
/// </summary>
class TestFactoryRegistrar
{
    public static void registerAll()
    {
        TestDataFactory::registerFactory(tableNum(CustTable), new CustTableTestFactory());
        TestDataFactory::registerFactory(tableNum(VendTable), new VendTableTestFactory());
        TestDataFactory::registerFactory(tableNum(InventTable), new InventTableTestFactory());
        TestDataFactory::registerFactory(tableNum(SalesTable), new SalesTableTestFactory());
        TestDataFactory::registerFactory(tableNum(PurchTable), new PurchTableTestFactory());
        TestDataFactory::registerFactory(tableNum(ProjTable), new ProjTableTestFactory());
        // ... add more
    }
    
    public static void cleanup()
    {
        // Delete test data (use with caution!)
        // Only run in test environments
        if (curUserId() != "TEST_USER")
            return;
            
        delete_from CustTable where CustTable.AccountNum like "TEST_%";
        delete_from VendTable where VendTable.AccountNum like "TEST_%";
        delete_from SalesTable where SalesTable.SalesId like "TEST_%";
        // ...
    }
}
```

### 3.3 Using Factories in Tests

```xpp
[SysTestCase]
class SalesOrderIntegrationTests extends SysTestCase
{
    public void setUp()
    {
        TestFactoryRegistrar::registerAll();
    }
    
    public void tearDown()
    {
        // Optional: cleanup test data
    }
    
    [SysTestMethod]
    public void testCreateSalesOrderWithMultipleLines()
    {
        // Given: Customer and items exist
        CustTable customer = TestDataFactory::create(tableNum(CustTable));
        InventTable item1 = TestDataFactory::create(tableNum(InventTable), 
            new Map(Types::String, Types::AnyType).fromArray([["ItemId", "ITEM-001"]]));
        InventTable item2 = TestDataFactory::create(tableNum(InventTable), 
            new Map(Types::String, Types::AnyType).fromArray([["ItemId", "ITEM-002"]]));
        
        // When: Create sales order with custom lines
        List customLines = new List(Types::Record);
        List line1 = new List(Types::AnyType); line1.addEnd(item1.ItemId); line1.addEnd(5); line1.addEnd(100.00);
        List line2 = new List(Types::AnyType); line2.addEnd(item2.ItemId); line2.addEnd(3); line2.addEnd(250.00);
        customLines.addEnd(line1); customLines.addEnd(line2);
        
        Map overrides = new Map(Types::String, Types::AnyType);
        overrides.insert("CustAccount", customer.AccountNum);
        overrides.insert("Items", customLines);
        
        SalesTable salesOrder = TestDataFactory::create(tableNum(SalesTable), overrides);
        
        // Then: Verify
        this.assertEquals(2, SalesLine::findBySalesId(salesOrder.SalesId).elements(), "Two lines created");
        this.assertEquals(1250.00, salesOrder.SalesAmount, "Correct total amount");
    }
    
    [SysTestMethod]
    public void testSalesOrderLifecycle_PropertyBased()
    {
        PropertyTest::check(
            "SalesOrderAmountConsistency",
            200,
            this,
            delegate boolean(List _lines)
            {
                // Create order with generated lines
                CustTable customer = TestDataFactory::create(tableNum(CustTable));
                
                Map overrides = new Map(Types::String, Types::AnyType);
                overrides.insert("CustAccount", customer.AccountNum);
                overrides.insert("Items", _lines);
                
                SalesTable order = TestDataFactory::create(tableNum(SalesTable), overrides);
                
                // Verify: Header amount == sum of lines
                AmountMST headerAmount = order.SalesAmount;
                AmountMST linesAmount = 0;
                
                while select salesLine
                    where salesLine.SalesId == order.SalesId
                {
                    linesAmount += salesLine.LineAmount;
                }
                
                return headerAmount == linesAmount;
            },
            delegate List()
            {
                // Generate 1-5 random lines
                int lineCount = Generators::genInt(1, 5);
                List lines = new List(Types::Record);
                int i;
                
                for (i = 1; i <= lineCount; i++)
                {
                    InventTable item = TestDataFactory::create(tableNum(InventTable));
                    List line = new List(Types::AnyType);
                    line.addEnd(item.ItemId);
                    line.addEnd(Generators::genInt(1, 100));
                    line.addEnd(Generators::genReal(1.00, 1000.00));
                    lines.addEnd(line);
                }
                return lines;
            }
        );
    }
}
```

---

## 4. SysTest + TestFramework Integration

### 4.1 Test Suite Organization

```xpp
/// <summary>
/// Test suite for Inventory module
/// </summary>
[SysTestSuite]
class InventModuleTestSuite extends SysTestSuite
{
    public void initialize()
    {
        this.addTestCase(classStr(InventQtyPropertyTests));
        this.addTestCase(classStr(InventDimPropertyTests));
        this.addTestCase(classStr(InventJournalIntegrationTests));
        this.addTestCase(classStr(InventTransferIntegrationTests));
    }
}

/// <summary>
/// Test suite runner with reporting
/// </summary>
class TestRunner
{
    public static void runAll()
    {
        SysTestSuite suite = new InventModuleTestSuite();
        SysTestResult result = suite.run();
        
        // Output results
        info(strFmt("Tests run: %1, Passed: %2, Failed: %3", 
            result.testsRun(), result.testsPassed(), result.testsFailed()));
        
        // Export to JUnit XML for CI
        TestRunner::exportJUnit(result, "InventModuleTestResults.xml");
    }
    
    public static void exportJUnit(SysTestResult _result, str _fileName)
    {
        XmlDocument doc = new XmlDocument();
        XmlElement testsuite = doc.createElement("testsuite");
        testsuite.setAttribute("name", "InventModule");
        testsuite.setAttribute("tests", int2str(_result.testsRun()));
        testsuite.setAttribute("failures", int2str(_result.testsFailed()));
        testsuite.setAttribute("time", strFmt("%.3f", _result.duration() / 1000.0));
        
        // Add test cases (simplified)
        // In reality, iterate _result.getTestResults()
        
        doc.appendChild(testsuite);
        doc.save(_fileName);
    }
}
```

### 4.2 Data Fixtures for Integration Tests

```xpp
/// <summary>
/// Test fixture for complex scenarios
/// </summary>
class InventTransferTestFixture
{
    InventSite fromSite;
    InventSite toSite;
    InventLocation fromLoc;
    InventLocation toLoc;
    InventTable item;
    InventDim fromDim;
    InventDim toDim;
    
    public void setUp()
    {
        // Create sites
        fromSite = InventSite::create("FROM", "From Site");
        toSite = InventSite::create("TO", "To Site");
        
        // Create warehouses
        fromLoc = InventLocation::create("WH-FROM", fromSite.SiteId);
        toLoc = InventLocation::create("WH-TO", toSite.SiteId);
        
        // Create item with tracking
        item = InventTable::create("TRANSFER-ITEM", "Transfer Item");
        item.StorageDimGroup = "SiteWH";
        item.TrackingDimGroup = "Serial";
        item.update();
        
        // Create dimensions
        fromDim = InventDim::newInventSiteId(fromSite.SiteId);
        fromDim.InventLocationId = fromLoc.InventLocationId;
        fromDim = InventDim::findOrCreate(fromDim);
        
        toDim = InventDim::newInventSiteId(toSite.SiteId);
        toDim.InventLocationId = toLoc.InventLocationId;
        toDim = InventDim::findOrCreate(toDim);
        
        // Add on-hand at from site
        InventSum::updateOnHand(item.ItemId, fromDim.inventDimId, 100, false);
    }
    
    public void tearDown()
    {
        // Cleanup in reverse order
        delete_from InventSum where InventSum.ItemId == item.ItemId;
        delete_from InventDim where InventDim.inventDimId == fromDim.inventDimId;
        delete_from InventDim where InventDim.inventDimId == toDim.inventDimId;
        item.delete();
        fromLoc.delete();
        toLoc.delete();
        fromSite.delete();
        toSite.delete();
    }
}
```

---

## 5. CI/CD Integration

### 5.1 Azure DevOps Test Task

```yaml
# azure-pipelines-test.yml
- stage: Test
  displayName: 'Run SysTest Suite'
  dependsOn: Build
  jobs:
  - job: SysTest
    displayName: 'Execute SysTest'
    pool:
      vmImage: 'windows-latest'
    timeoutInMinutes: 60
    variables:
      D365FOEnvironmentUrl: $(TestEnvironmentUrl)
      D365FOClientId: $(TestClientId)
      D365FOClientSecret: $(TestClientSecret)
      D365FOTenantId: $(TestTenantId)

    steps:
    - task: DownloadBuildArtifacts@0
      inputs:
        buildType: 'current'
        artifactName: 'D365FO-Model'
        downloadPath: '$(System.ArtifactsDirectory)'

    - task: PowerShell@2
      displayName: 'Deploy Model to Test Env'
      inputs:
        targetType: 'inline'
        script: |
          # Deploy model to test environment
          # (Same as build pipeline deploy step)

    - task: PowerShell@2
      displayName: 'Run SysTest Suite'
      inputs:
        targetType: 'inline'
        script: |
          $testRunner = "C:\AOSService\PackagesLocalDirectory\Bin\Microsoft.Dynamics.AX.Xpp.SysTestRunner.exe"
          $modelName = "$(ModelName)"
          
          if (-not (Test-Path $testRunner)) {
              Write-Error "SysTest runner not found"
              exit 1
          }
          
          # Run specific test suite
          & $testRunner `
              -model $modelName `
              -testSuite "InventModuleTestSuite" `
              -output "$(Build.SourcesDirectory)/TestResults/SysTestResults.trx" `
              -verbose
          
          $exitCode = $LASTEXITCODE
          if ($exitCode -ne 0) {
              Write-Error "SysTest execution failed with exit code $exitCode"
          }
          
          exit $exitCode

    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '**/SysTestResults.trx'
        mergeTestResults: true
        testRunTitle: 'SysTest - $(ModelName)'

    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Code Coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Build.SourcesDirectory)/TestResults/coverage.cobertura.xml'
```

### 5.2 Property Test Reporting

```xpp
/// <summary>
/// Enhanced property test reporter for CI
/// </summary>
class PropertyTestReporter
{
    static Map results;
    
    public static void recordResult(str _propertyName, int _iterations, boolean _passed, 
                                    anytype _counterExample = null, int _shrunkIterations = 0)
    {
        if (!results)
            results = new Map(Types::String, Types::Container);
        
        results.insert(_propertyName, [_passed, _iterations, _counterExample, _shrunkIterations]);
    }
    
    public static void publishSummary()
    {
        MapEnumerator enum = results.getEnumerator();
        int total = 0;
        int passed = 0;
        int failed = 0;
        str summary = "Property Test Summary\n=====================\n";
        
        while (enum.moveNext())
        {
            total++;
            container data = enum.currentValue();
            boolean passed = conPeek(data, 1);
            int iterations = conPeek(data, 2);
            anytype counterExample = conPeek(data, 3);
            int shrunk = conPeek(data, 4);
            
            if (passed)
            {
                passed++;
                summary += strFmt("✅ %1: %2 iterations\n", enum.currentKey(), iterations);
            }
            else
            {
                failed++;
                summary += strFmt("❌ %1: FAILED after %2 iterations (shrunk: %3)\n", 
                    enum.currentKey(), iterations, shrunk);
                summary += strFmt("   Counter-example: %1\n", anytype2str(counterExample));
            }
        }
        
        summary += strFmt("\nTotal: %1 | Passed: %2 | Failed: %3", total, passed, failed);
        info(summary);
        
        // Write to file for CI artifact
        TextIo file = new TextIo("PropertyTestResults.txt", "W");
        file.write(summary);
        file = null;
    }
}
```

---

## 6. Test Data Management Patterns

### 6.1 Test Data Isolation Strategies

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Transaction Rollback** | Fast, automatic cleanup | Can't test commit behavior | Unit tests |
| **Dedicated Test Company** | Full isolation, realistic data | Setup overhead | Integration tests |
| **Data Partition (Legal Entity)** | Clean separation | Requires config | Multi-tenant testing |
| **In-Memory Tables** | Instant, no DB | Limited to temp tables | Pure logic tests |
| **Test Data Snapshots** | Consistent baseline | Storage, restore time | Regression testing |

### 6.2 Transaction Rollback Pattern

```xpp
[SysTestCase]
class TransactionalTests extends SysTestCase
{
    // Each test runs in its own transaction
    // Automatic rollback after test method
    
    [SysTestMethod]
    public void testInsertRollback()
    {
        CustTable cust;
        ;
        
        ttsBegin;
        cust.clear();
        cust.AccountNum = "TEST-001";
        cust.Name = "Test";
        cust.insert();
        
        // Verify exists in transaction
        select firstOnly cust where cust.AccountNum == "TEST-001";
        this.assertNotNull(cust, "Record exists in transaction");
        
        // Don't commit - framework rolls back automatically
        // ttsAbort happens in tearDown
    }
}
```

### 6.3 Test Company Pattern

```xpp
/// <summary>
/// Manages test company lifecycle
/// </summary>
class TestCompanyManager
{
    static str testCompany = "TESTCO";
    
    public static void ensureTestCompany()
    {
        DataArea dataArea;
        
        if (!DataArea::find(testCompany))
        {
            ttsBegin;
            dataArea.clear();
            dataArea.Id = testCompany;
            dataArea.Name = "Test Company";
            dataArea.ShortName = "TEST";
            dataArea.insert();
            ttsCommit;
            
            // Initialize number sequences, parameters
            TestCompanyManager::initializeParameters(testCompany);
        }
        
        // Switch to test company
        changeCompany(testCompany) { /* test runs here */ };
    }
    
    public static void initializeParameters(str _company)
    {
        changeCompany(_company)
        {
            // Initialize all module parameters
            NumberSeqReference::construct().loadModule(
                new NumberSeqModuleCustomer());
            NumberSeqReference::construct().loadModule(
                new NumberSeqModuleInvent());
            // ...
            
            // Set default parameters
            CustParameters::find().update();
            InventParameters::find().update();
        }
    }
    
    public static void cleanupTestCompany()
    {
        // Delete all data in test company
        changeCompany(testCompany)
        {
            // Delete in dependency order
            delete_from SalesLine;
            delete_from SalesTable;
            delete_from CustTrans;
            delete_from CustTable;
            // ...
        }
    }
}
```

---

## 7. Performance Testing Patterns

### 7.1 Benchmark Test Template

```xpp
[SysTestCase]
class PerformanceBenchmarks extends SysTestCase
{
    [SysTestMethod]
    public void benchmark_InsertRecordsetVsLoop()
    {
        int recordCount = 10000;
        int iterations = 5;
        Real avgLoopTime = 0;
        Real avgRecordsetTime = 0;
        int i;
        ;
        
        // Warmup
        this.runInsertLoop(100);
        this.runInsertRecordset(100);
        
        // Benchmark loop insert
        for (i = 1; i <= iterations; i++)
        {
            avgLoopTime += this.runInsertLoop(recordCount);
            this.cleanupTestTable();
        }
        avgLoopTime /= iterations;
        
        // Benchmark insert_recordset
        for (i = 1; i <= iterations; i++)
        {
            avgRecordsetTime += this.runInsertRecordset(recordCount);
            this.cleanupTestTable();
        }
        avgRecordsetTime /= iterations;
        
        info(strFmt("Loop insert: %.2f ms | insert_recordset: %.2f ms | Speedup: %.2fx",
            avgLoopTime, avgRecordsetTime, avgLoopTime / avgRecordsetTime));
        
        // Assert: insert_recordset should be at least 5x faster
        this.assertTrue(avgRecordsetTime * 5 < avgLoopTime, 
            "insert_recordset should be significantly faster");
    }
    
    Real runInsertLoop(int _count)
    {
        int i;
        MyTestTable table;
        UTCDateTime start = DateTimeUtil::utcNow();
        ;
        
        for (i = 1; i <= _count; i++)
        {
            table.clear();
            table.Field1 = int2str(i);
            table.Field2 = "Test";
            table.insert();
        }
        
        return DateTimeUtil::getDifference(DateTimeUtil::utcNow(), start) / 1000000.0;
    }
    
    Real runInsertRecordset(int _count)
    {
        MyTestTable table;
        UTCDateTime start = DateTimeUtil::utcNow();
        ;
        
        // Use a temp table as source
        MyTempTable temp;
        int i;
        for (i = 1; i <= _count; i++)
        {
            temp.clear();
            temp.Field1 = int2str(i);
            temp.Field2 = "Test";
            temp.insert();
        }
        
        insert_recordset table (Field1, Field2)
            select Field1, Field2 from temp;
        
        return DateTimeUtil::getDifference(DateTimeUtil::utcNow(), start) / 1000000.0;
    }
    
    void cleanupTestTable()
    {
        delete_from MyTestTable;
    }
}
```

---

## 8. Microsoft Resources

- **SysTest Framework**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework
- **Test Best Practices**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-best-practices
- **Property-Based Testing**: https://fsharpforfunandprofit.com/posts/property-based-testing/
- **FsCheck**: https://github.com/fscheck/FsCheck
- **Azure DevOps Testing**: https://learn.microsoft.com/en-us/azure/devops/test/

---

## 9. Quick Reference: Test Patterns

```xpp
// 1. Property test template
PropertyTest::check(
    "PropertyName",
    1000,
    this,
    delegate boolean(input) { return invariant(input); },
    delegate anytype() { return generator(); },
    delegate anytype(input) { return shrinker(input); }
);

// 2. Test factory usage
TestFactoryRegistrar::registerAll();
CustTable customer = TestDataFactory::create(tableNum(CustTable), 
    new Map(Types::String, Types::AnyType).fromArray([["Name", "Custom Name"]]));

// 3. Transactional test (auto-rollback)
[SysTestMethod]
public void testSomething()
{
    ttsBegin;
    // ... test code ...
    // Automatic rollback
}

// 4. Benchmark
UTCDateTime start = DateTimeUtil::utcNow();
// ... code ...
Real ms = DateTimeUtil::getDifference(DateTimeUtil::utcNow(), start) / 1000000.0;
```

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*