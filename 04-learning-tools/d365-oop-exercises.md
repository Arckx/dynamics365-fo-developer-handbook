---
name: d365-oop-exercises
description: 10 hands-on OOP exercises with solutions — beginner to intermediate, mapped to X++ patterns
metadata:
  type: reference
  last-verified: 2026-11-22
---

# OOP Exercises for D365 F&O Developers

> **Do these BEFORE Chapter 7** if new to OOP. Each has problem, hints, solution, and X++ mapping.
> Time estimates assume reading + coding + testing.

---

## Exercise 1: Classes and Objects — Customer Service

> **Difficulty:** ⭐ Beginner | **Time:** 30 min | **Concepts:** Class, constructor, fields, methods, encapsulation

### Problem

Create a `CustomerService` class that:
1. Stores a `CustTable` record (private field)
2. Has a constructor accepting `CustTable`
3. Has a public method `validate()` that returns `true` if:
   - Customer has `AccountNum` set
   - Customer has `CustGroup` = "10" or "20"
   - Customer `CreditLimit` > 0
4. Has a private helper method `checkCredit()` used by `validate()`

### Hints

- Use `private` for fields and helper methods
- Constructor in X++ is `public void new(...)`
- Access fields via `this._fieldName`
- Return `boolean` from validation methods

### Solution

```xpp
public class CustomerService
{
    // Private fields - encapsulated
    private CustTable _customer;
    private boolean _isValidated;

    // Constructor
    public void new(CustTable _cust)
    {
        _customer = _cust;
        _isValidated = false;
    }

    // Public API
    public boolean validate()
    {
        if (!_customer)
        {
            return false;
        }

        _isValidated = this.checkAccountNum() 
                    && this.checkCustGroup() 
                    && this.checkCreditLimit();
        
        return _isValidated;
    }

    // Private helpers - internal implementation
    private boolean checkAccountNum()
    {
        return _customer.AccountNum != "";
    }

    private boolean checkCustGroup()
    {
        return _customer.CustGroup == "10" || _customer.CustGroup == "20";
    }

    private boolean checkCreditLimit()
    {
        return _customer.CreditLimit > 0;
    }
}
```

### Usage

```xpp
static void TestCustomerService(Args _args)
{
    CustTable cust;
    select firstOnly cust where cust.AccountNum == "US-001";

    CustomerService service = new CustomerService(cust);
    
    if (service.validate())
    {
        info("Customer is valid");
    }
    else
    {
        error("Customer validation failed");
    }
}
```

### X++ Mapping

| OOP Concept | X++ Implementation |
|-------------|-------------------|
| Private field | `private CustTable _customer;` |
| Constructor | `public void new(CustTable _cust)` |
| Public method | `public boolean validate()` |
| Private method | `private boolean checkCreditLimit()` |
| Encapsulation | Fields hidden, access via methods |

---

## Exercise 2: Inheritance — Document Processor

> **Difficulty:** ⭐ Beginner | **Time:** 45 min | **Concepts:** Abstract class, inheritance, `super()`, template method

### Problem

Create a document processing hierarchy:

1. **Abstract base class** `DocumentProcessor` with:
   - Protected field `_document` (type `DocuRef`)
   - Constructor taking `DocuRef`
   - **Template method** `process()` that calls: `validate()` → `transform()` → `save()` → `notify()`
   - **Abstract method** `transform()` (must be implemented by children)
   - Virtual methods `validate()`, `save()`, `notify()` with defaults

2. **Derived class** `SalesOrderProcessor` that:
   - Calls `super()` in constructor
   - Implements `transform()` to set document name = "SO: " + SalesId
   - Overrides `validate()` to also check `SalesStatus != Invoiced`

3. **Derived class** `PurchaseOrderProcessor` that:
   - Implements `transform()` to set name = "PO: " + PurchId

### Hints

- Abstract class: `public abstract class DocumentProcessor`
- Abstract method: `protected abstract void transform()`
- Virtual method: `protected void validate() { ... }`
- Call parent: `super(_doc)` in constructor, `super()` in override

### Solution

```xpp
// Abstract base class
public abstract class DocumentProcessor
{
    protected DocuRef _document;

    public void new(DocuRef _doc)
    {
        _document = _doc;
    }

    // Template method - FINAL (cannot override)
    public final void process()
    {
        this.validate();
        this.transform();
        this.save();
        this.notify();
    }

    // MUST implement in derived class
    protected abstract void transform();

    // Can override
    protected void validate()
    {
        if (!_document)
        {
            throw error("No document provided");
        }
    }

    protected void save()
    {
        _document.update();
    }

    protected void notify()
    {
        info(strFmt("Processed: %1", _document.Name));
    }
}

// Derived: Sales Order
public class SalesOrderProcessor extends DocumentProcessor
{
    public void new(DocuRef _doc)
    {
        super(_doc);
    }

    protected void transform()
    {
        SalesTable sales = SalesTable::find(_document.RefRecId);
        if (sales)
        {
            _document.Name = strFmt("SO: %1", sales.SalesId);
        }
    }

    protected void validate()
    {
        super(); // Run base validation first
        
        SalesTable sales = SalesTable::find(_document.RefRecId);
        if (sales && sales.SalesStatus == SalesStatus::Invoiced)
        {
            throw error("Cannot process invoiced order");
        }
    }
}

// Derived: Purchase Order
public class PurchaseOrderProcessor extends DocumentProcessor
{
    public void new(DocuRef _doc)
    {
        super(_doc);
    }

    protected void transform()
    {
        PurchTable purch = PurchTable::find(_document.RefRecId);
        if (purch)
        {
            _document.Name = strFmt("PO: %1", purch.PurchId);
        }
    }
}
```

### Usage

```xpp
static void TestDocumentProcessors(Args _args)
{
    DocuRef doc1, doc2;
    // Assume doc1.RefRecId = SalesTable, doc2.RefRecId = PurchTable
    
    List processors = new List(Types::Class);
    processors.addEnd(new SalesOrderProcessor(doc1));
    processors.addEnd(new PurchaseOrderProcessor(doc2));
    
    // Polymorphism - same call, different behavior
    ListEnumerator enum = processors.getEnumerator();
    while (enum.moveNext())
    {
        DocumentProcessor processor = enum.current();
        processor.process(); // Calls correct transform() for each type
    }
}
```

### X++ Mapping

| OOP Concept | X++ Keyword |
|-------------|-------------|
| Abstract class | `public abstract class` |
| Abstract method | `protected abstract void method()` |
| Inheritance | `extends DocumentProcessor` |
| Parent constructor | `super(_doc)` |
| Template method | `public final void process()` |
| Override | Same signature + `super()` call |

---

## Exercise 3: Interfaces — Exportable Data

> **Difficulty:** ⭐ Beginner | **Time:** 30 min | **Concepts:** Interface, implementation, polymorphism via interface

### Problem

1. Create interface `IExportable` with methods:
   - `str exportToJson()`
   - `str exportToXml()`

2. Create interface `IValidatable` with:
   - `boolean validate()`
   - `str getErrors()`

3. Create class `CustomerData` implementing **both** interfaces:
   - Wraps `CustTable`
   - `exportToJson()` returns `{"AccountNum":"...","Name":"..."}`
   - `exportToXml()` returns `<Customer><AccountNum>...</AccountNum>...</Customer>`
   - `validate()` checks AccountNum and Name not empty
   - `getErrors()` returns semicolon-separated error messages

4. Write code that accepts `List` of `IExportable` and exports all

### Hints

- Interface: `public interface IExportable`
- Implementation: `public class CustomerData implements IExportable, IValidatable`
- Interface methods are implicitly `public`
- Use `implements` keyword for interfaces

### Solution

```xpp
// Interfaces
public interface IExportable
{
    str exportToJson();
    str exportToXml();
}

public interface IValidatable
{
    boolean validate();
    str getErrors();
}

// Implementation
public class CustomerData implements IExportable, IValidatable
{
    private CustTable _customer;
    private str _errors;

    public void new(CustTable _cust)
    {
        _customer = _cust;
        _errors = "";
    }

    // IExportable
    public str exportToJson()
    {
        return strFmt('{"AccountNum":"%1","Name":"%2","CustGroup":"%3"}',
            _customer.AccountNum, _customer.Name, _customer.CustGroup);
    }

    public str exportToXml()
    {
        return strFmt('<Customer><AccountNum>%1</AccountNum><Name>%2</Name><CustGroup>%3</CustGroup></Customer>',
            _customer.AccountNum, _customer.Name, _customer.CustGroup);
    }

    // IValidatable
    public boolean validate()
    {
        _errors = "";
        
        if (!_customer.AccountNum)
            _errors += "Missing AccountNum; ";
        if (!_customer.Name)
            _errors += "Missing Name; ";
        
        return _errors == "";
    }

    public str getErrors()
    {
        return _errors;
    }
}
```

### Usage

```xpp
static void ExportCustomers(Args _args)
{
    List exportables = new List(Types::Class);
    
    // Add different exportable objects
    exportables.addEnd(new CustomerData(CustTable::find("US-001")));
    exportables.addEnd(new CustomerData(CustTable::find("US-002")));
    // Could add VendorData, ItemData if they implement IExportable
    
    ListEnumerator enum = exportables.getEnumerator();
    while (enum.moveNext())
    {
        IExportable exporter = enum.current();
        
        str json = exporter.exportToJson();
        str xml = exporter.exportToXml();
        
        info(strFmt("JSON: %1", json));
        info(strFmt("XML: %1", xml));
    }
}
```

### X++ Mapping

| OOP Concept | X++ Syntax |
|-------------|------------|
| Interface | `public interface IName` |
| Multiple interfaces | `implements IExportable, IValidatable` |
| Interface variable | `IExportable exporter = ...` |
| Polymorphism | Same variable, different implementations |

---

## Exercise 4: Encapsulation — Bank Account

> **Difficulty:** ⭐ Beginner | **Time:** 30 min | **Concepts:** Private fields, getters/setters, validation, invariants

### Problem

Create a `BankAccount` class with:
- **Private fields:** `_balance` (real), `_accountNumber` (str), `_owner` (str)
- **Read-only properties** (getters): `balance()`, `accountNumber()`, `owner()`
- **Controlled operations:**
  - `deposit(real _amount)` — only positive amounts, updates balance
  - `withdraw(real _amount)` — only positive, only if sufficient funds
  - `transfer(BankAccount _to, real _amount)` — atomic transfer
- **Invariant:** Balance never negative

### Hints

- No public setters for balance
- Validate in deposit/withdraw
- Transfer = withdraw from this + deposit to target
- Use `throw error()` for violations

### Solution

```xpp
public class BankAccount
{
    private real _balance;
    private str _accountNumber;
    private str _owner;

    public void new(str _accNum, str _ownerName, real _initialBalance = 0)
    {
        _accountNumber = _accNum;
        _owner = _ownerName;
        _balance = _initialBalance;
    }

    // Read-only properties (getters)
    public real balance()
    {
        return _balance;
    }

    public str accountNumber()
    {
        return _accountNumber;
    }

    public str owner()
    {
        return _owner;
    }

    // Controlled operations
    public void deposit(real _amount)
    {
        if (_amount <= 0)
        {
            throw error("Deposit amount must be positive");
        }
        _balance += _amount;
    }

    public void withdraw(real _amount)
    {
        if (_amount <= 0)
        {
            throw error("Withdrawal amount must be positive");
        }
        if (_amount > _balance)
        {
            throw error(strFmt("Insufficient funds. Balance: %1, Requested: %2", _balance, _amount));
        }
        _balance -= _amount;
    }

    public void transfer(BankAccount _to, real _amount)
    {
        if (!_to)
        {
            throw error("Target account required");
        }
        
        // Atomic: both succeed or both fail
        this.withdraw(_amount);  // Throws if insufficient
        _to.deposit(_amount);    // If this fails, withdrawal already happened...
        
        // Better: use transaction in real code
    }
}
```

### Usage

```xpp
static void TestBankAccount(Args _args)
{
    BankAccount checking = new BankAccount("CHK-001", "John Doe", 1000);
    BankAccount savings = new BankAccount("SAV-001", "John Doe", 5000);
    
    info(strFmt("Checking: %1", checking.balance()));  // 1000
    info(strFmt("Savings: %1", savings.balance()));    // 5000
    
    checking.deposit(500);
    info(strFmt("After deposit: %1", checking.balance())); // 1500
    
    checking.withdraw(200);
    info(strFmt("After withdrawal: %1", checking.balance())); // 1300
    
    // This throws error:
    // checking.withdraw(2000); // "Insufficient funds"
    
    checking.transfer(savings, 300);
    info(strFmt("Checking: %1, Savings: %2", checking.balance(), savings.balance()));
    // Checking: 1000, Savings: 5300
}
```

### X++ Mapping

| OOP Concept | X++ Pattern |
|-------------|-------------|
| Private field | `private real _balance;` |
| Getter (property) | `public real balance() { return _balance; }` |
| Validation in setter | `if (_amount <= 0) throw error(...)` |
| Invariant protection | No public setter for balance |

---

## Exercise 5: Factory Pattern — Document Factory

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 45 min | **Concepts:** Factory, polymorphism, enum-based creation

### Problem

1. Create enum `DocuType` with values: `SalesOrder`, `PurchaseOrder`, `Invoice`
2. Create abstract base `DocumentProcessor` (from Exercise 2)
3. Create concrete: `SalesOrderProcessor`, `PurchaseOrderProcessor`, `InvoiceProcessor`
4. Create `DocumentFactory` with static method:
   - `static DocumentProcessor create(DocuType _type, DocuRef _doc)`
   - Returns correct processor based on type
5. Test with all three types

### Hints

- Enum: `enum DocuType { SalesOrder, PurchaseOrder, Invoice }`
- Factory method is `static`
- Use `switch` on enum
- Throw error for unknown type

### Solution

```xpp
// Enum
enum DocuType
{
    SalesOrder,
    PurchaseOrder,
    Invoice
}

// Factory
public class DocumentFactory
{
    public static DocumentProcessor create(DocuType _type, DocuRef _doc)
    {
        switch (_type)
        {
            case DocuType::SalesOrder:
                return new SalesOrderProcessor(_doc);
            case DocuType::PurchaseOrder:
                return new PurchaseOrderProcessor(_doc);
            case DocuType::Invoice:
                return new InvoiceProcessor(_doc);
            default:
                throw error(strFmt("Unknown document type: %1", _type));
        }
    }
}

// Concrete: Invoice
public class InvoiceProcessor extends DocumentProcessor
{
    public void new(DocuRef _doc)
    {
        super(_doc);
    }

    protected void transform()
    {
        VendInvoiceJour invoice = VendInvoiceJour::find(_document.RefRecId);
        if (invoice)
        {
            _document.Name = strFmt("INV: %1", invoice.InvoiceId);
        }
    }
}
```

### Usage

```xpp
static void TestFactory(Args _args)
{
    DocuRef doc;
    // ... get document
    
    DocumentProcessor processor;
    
    // Factory decides which concrete class
    processor = DocumentFactory::create(DocuType::SalesOrder, doc);
    processor.process();
    
    processor = DocumentFactory::create(DocuType::Invoice, doc);
    processor.process();
}
```

### X++ Mapping

| Pattern | X++ Implementation |
|---------|-------------------|
| Factory Method | `static DocumentProcessor create(...)` |
| Enum | `enum DocuType { ... }` |
| Switch on enum | `switch (_type) { case DocuType::SalesOrder: ... }` |

---

## Exercise 6: Strategy Pattern — Pricing

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 45 min | **Concepts:** Strategy interface, swappable algorithms

### Problem

1. Create interface `IPricingStrategy`:
   - `real calculatePrice(SalesLine _line)`

2. Implement two strategies:
   - `StandardPricing` — returns `SalesPrice * SalesQty`
   - `VolumeDiscountPricing` — 10% discount if `SalesQty > 100`

3. Create `SalesLinePricer` class:
   - Takes `IPricingStrategy` in constructor
   - Method `priceLine(SalesLine _line)` delegates to strategy

4. Test with same line, different strategies

### Hints

- Interface: `public interface IPricingStrategy`
- Implementation: `public class StandardPricing implements IPricingStrategy`
- Context class holds reference to interface

### Solution

```xpp
// Strategy interface
public interface IPricingStrategy
{
    real calculatePrice(SalesLine _line);
}

// Concrete strategies
public class StandardPricing implements IPricingStrategy
{
    public real calculatePrice(SalesLine _line)
    {
        return _line.SalesPrice * _line.SalesQty;
    }
}

public class VolumeDiscountPricing implements IPricingStrategy
{
    public real calculatePrice(SalesLine _line)
    {
        real price = _line.SalesPrice * _line.SalesQty;
        if (_line.SalesQty > 100)
        {
            price *= 0.9; // 10% discount
        }
        return price;
    }
}

// Context
public class SalesLinePricer
{
    private IPricingStrategy _strategy;

    public void new(IPricingStrategy _strategy)
    {
        _strategy = _strategy;
    }

    public real priceLine(SalesLine _line)
    {
        return _strategy.calculatePrice(_line);
    }

    // Can change strategy at runtime
    public void setStrategy(IPricingStrategy _strategy)
    {
        _strategy = _strategy;
    }
}
```

### Usage

```xpp
static void TestPricingStrategies(Args _args)
{
    SalesLine line;
    select firstOnly line where line.SalesQty == 150 && line.SalesPrice == 100;
    // Line total = 15,000
    
    // Standard pricing
    SalesLinePricer pricer = new SalesLinePricer(new StandardPricing());
    info(strFmt("Standard: %1", pricer.priceLine(line))); // 15,000
    
    // Volume discount
    pricer.setStrategy(new VolumeDiscountPricing());
    info(strFmt("Volume: %1", pricer.priceLine(line))); // 13,500 (10% off)
}
```

### X++ Mapping

| Pattern | X++ Implementation |
|---------|-------------------|
| Strategy Interface | `public interface IPricingStrategy` |
| Concrete Strategy | `implements IPricingStrategy` |
| Context | Holds `IPricingStrategy` reference |
| Runtime swap | `setStrategy(new VolumeDiscountPricing())` |

---

## Exercise 7: Dependency Inversion — Repository

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 45 min | **Concepts:** Interface, dependency injection, testability

### Problem

1. Create interface `ICustomerRepository`:
   - `CustTable find(str _accountNum)`
   - `void save(CustTable _customer)`
   - `void delete(str _accountNum)`

2. Create two implementations:
   - `SqlCustomerRepository` — uses `select` statements
   - `InMemoryCustomerRepository` — uses `Map` for testing

3. Create `CustomerService` that:
   - Takes `ICustomerRepository` in constructor (dependency injection)
   - Has method `getCustomerCredit(str _accountNum)` returning credit limit
   - Has method `increaseCreditLimit(str _accountNum, real _amount)`

4. Test with both repositories

### Hints

- Interface defines contract
- Service depends on abstraction, not concrete
- Inject via constructor

### Solution

```xpp
// Abstraction
public interface ICustomerRepository
{
    CustTable find(str _accountNum);
    void save(CustTable _customer);
    void delete(str _accountNum);
}

// Production: SQL
public class SqlCustomerRepository implements ICustomerRepository
{
    public CustTable find(str _accountNum)
    {
        CustTable cust;
        select firstOnly cust where cust.AccountNum == _accountNum;
        return cust;
    }

    public void save(CustTable _customer)
    {
        _customer.update(); // or insert
    }

    public void delete(str _accountNum)
    {
        CustTable cust = this.find(_accountNum);
        if (cust)
            cust.delete();
    }
}

// Test: In-Memory
public class InMemoryCustomerRepository implements ICustomerRepository
{
    private Map _customers = new Map(Types::String, Types::Record);

    public CustTable find(str _accountNum)
    {
        return _customers.lookup(_accountNum);
    }

    public void save(CustTable _customer)
    {
        _customers.insert(_customer.AccountNum, _customer);
    }

    public void delete(str _accountNum)
    {
        _customers.remove(_accountNum);
    }
}

// Service depends on abstraction
public class CustomerService
{
    private ICustomerRepository _repository;

    public void new(ICustomerRepository _repo)
    {
        _repository = _repo;
    }

    public real getCustomerCredit(str _accountNum)
    {
        CustTable cust = _repository.find(_accountNum);
        return cust ? cust.CreditLimit : 0;
    }

    public void increaseCreditLimit(str _accountNum, real _amount)
    {
        CustTable cust = _repository.find(_accountNum);
        if (!cust)
            throw error("Customer not found");
        
        cust.CreditLimit += _amount;
        _repository.save(cust);
    }
}
```

### Usage

```xpp
static void TestWithSql(Args _args)
{
    ICustomerRepository repo = new SqlCustomerRepository();
    CustomerService service = new CustomerService(repo);
    
    real credit = service.getCustomerCredit("US-001");
    info(strFmt("Credit: %1", credit));
}

static void TestWithMemory(Args _args)
{
    // Fast unit test - no database!
    ICustomerRepository repo = new InMemoryCustomerRepository();
    
    // Seed test data
    CustTable cust = new CustTable();
    cust.AccountNum = "TEST-001";
    cust.CreditLimit = 1000;
    repo.save(cust);
    
    CustomerService service = new CustomerService(repo);
    service.increaseCreditLimit("TEST-001", 500);
    
    real credit = service.getCustomerCredit("TEST-001");
    // credit = 1500
}
```

### X++ Mapping

| Principle | X++ Implementation |
|-----------|-------------------|
| Dependency Inversion | Service depends on `ICustomerRepository` interface |
| Constructor Injection | `public void new(ICustomerRepository _repo)` |
| Test Double | `InMemoryCustomerRepository` for unit tests |
| Swappable | Change one line to swap SQL ↔ Memory |

---

## Exercise 8: Observer Pattern — Event Handler

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 30 min | **Concepts:** Observer, event subscription, loose coupling

### Problem

D365 F&O uses Observer pattern for event handlers. Simulate it:

1. Create class `EventPublisher`:
   - List of subscribers (delegates)
   - Method `subscribe(delegate void _handler(EventArgs _e))`
   - Method `publish(EventArgs _e)` — calls all subscribers

2. Create `EventArgs` class with `str message`

3. Create two subscribers:
   - `EmailNotifier` — logs "EMAIL: message"
   - `LogNotifier` — logs "LOG: message"

4. Test: publish event, both notified

### Hints

- Use `List` of delegates for subscribers
- `delegate void handler(EventArgs _e)` for signature
- Iterate and invoke in `publish()`

### Solution

```xpp
// Event args
public class EventArgs
{
    public str message;
    
    public void new(str _msg)
    {
        message = _msg;
    }
}

// Publisher
public class EventPublisher
{
    private List _subscribers = new List(Types::Container);

    public void subscribe(delegate void _handler(EventArgs _e))
    {
        _subscribers.addEnd(_handler);
    }

    public void publish(EventArgs _e)
    {
        ListEnumerator enum = _subscribers.getEnumerator();
        while (enum.moveNext())
        {
            delegate void handler(EventArgs _e) = enum.current();
            handler(_e);
        }
    }
}

// Subscribers
public class EmailNotifier
{
    public void handle(EventArgs _e)
    {
        info(strFmt("EMAIL: %1", _e.message));
    }
}

public class LogNotifier
{
    public void handle(EventArgs _e)
    {
        info(strFmt("LOG: %1", _e.message));
    }
}
```

### Usage

```xpp
static void TestObserver(Args _args)
{
    EventPublisher publisher = new EventPublisher();
    EmailNotifier email = new EmailNotifier();
    LogNotifier log = new LogNotifier();
    
    // Subscribe
    publisher.subscribe(delegate void(EventArgs _e) { email.handle(_e); });
    publisher.subscribe(delegate void(EventArgs _e) { log.handle(_e); });
    
    // Publish
    EventArgs args = new EventArgs("Order SO-001 created");
    publisher.publish(args);
    
    // Output:
    // EMAIL: Order SO-001 created
    // LOG: Order SO-001 created
}
```

### D365 F&O Mapping

| Your Code | D365 F&O Equivalent |
|-----------|---------------------|
| `EventPublisher` | Base class with events |
| `subscribe()` | `[SubscribesTo(...)]` attribute |
| `publish()` | Kernel calls handlers |
| `delegate` | `delegate void handler(...)` |
| Loose coupling | Extensions don't reference each other |

---

## Exercise 9: Template Method — Report Generator

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 30 min | **Concepts:** Template method, hook methods

### Problem

Create abstract `ReportGenerator`:
- `public final void generate()` — template: `initialize()` → `fetchData()` → `formatData()` → `render()` → `cleanup()`
- Abstract methods: `fetchData()`, `formatData()`
- Hook methods (with defaults): `initialize()`, `render()`, `cleanup()`

Create two concrete reports:
- `SalesReport` — fetches SalesTable, formats as CSV
- `InventoryReport` — fetches InventTable, formats as XML

### Hints

- `public final void generate()` cannot be overridden
- Abstract methods: `protected abstract void fetchData()`
- Hooks: `protected void initialize() { }` (empty default)

### Solution

```xpp
public abstract class ReportGenerator
{
    // Template method - FINAL
    public final void generate()
    {
        this.initialize();
        this.fetchData();
        this.formatData();
        this.render();
        this.cleanup();
    }

    // Must implement
    protected abstract void fetchData();
    protected abstract void formatData();

    // Hooks (optional override)
    protected void initialize() { }
    protected void render() { info("Rendering report..."); }
    protected void cleanup() { }
}

// Concrete: Sales
public class SalesReport extends ReportGenerator
{
    private List _data;

    protected void fetchData()
    {
        _data = new List(Types::Record);
        while select SalesTable
        {
            _data.addEnd(SalesTable);
        }
    }

    protected void formatData()
    {
        // Format as CSV
        str csv = "SalesId,Customer,Amount\n";
        ListEnumerator enum = _data.getEnumerator();
        while (enum.moveNext())
        {
            SalesTable s = enum.current();
            csv += strFmt("%1,%2,%3\n", s.SalesId, s.CustAccount, s.SalesAmount);
        }
        // Store for render
    }
}

// Concrete: Inventory
public class InventoryReport extends ReportGenerator
{
    protected void fetchData()
    {
        // Fetch InventTable...
    }

    protected void formatData()
    {
        // Format as XML...
    }
}
```

### Usage

```xpp
static void TestReports(Args _args)
{
    ReportGenerator sales = new SalesReport();
    sales.generate(); // Runs full template
    
    ReportGenerator inv = new InventoryReport();
    inv.generate(); // Same template, different steps
}
```

---

## Exercise 10: Composition over Inheritance — Logger

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 30 min | **Concepts:** Composition, interface, delegating

### Problem

Instead of inheritance hierarchy for logging, use composition:

1. Create interface `ILogger`:
   - `void log(str _message)`

2. Create implementations:
   - `ConsoleLogger` — `info()`
   - `FileLogger` — writes to file (mock)
   - `MultiLogger` — composites multiple loggers

3. Create `BusinessService` that:
   - Takes `ILogger` in constructor
   - Uses it for all logging

4. Test with different logger configurations

### Hints

- `MultiLogger` holds `List` of `ILogger`
- Delegates `log()` to all contained loggers
- BusinessService doesn't know logging details

### Solution

```xpp
public interface ILogger
{
    void log(str _message);
}

public class ConsoleLogger implements ILogger
{
    public void log(str _message)
    {
        info(_message);
    }
}

public class FileLogger implements ILogger
{
    public void log(str _message)
    {
        // Mock file write
        info(strFmt("[FILE] %1", _message));
    }
}

public class MultiLogger implements ILogger
{
    private List _loggers = new List(Types::Class);

    public void addLogger(ILogger _logger)
    {
        _loggers.addEnd(_logger);
    }

    public void log(str _message)
    {
        ListEnumerator enum = _loggers.getEnumerator();
        while (enum.moveNext())
        {
            enum.current().log(_message);
        }
    }
}

public class BusinessService
{
    private ILogger _logger;

    public void new(ILogger _logger)
    {
        _logger = _logger;
    }

    public void processOrder(str _orderId)
    {
        _logger.log(strFmt("Processing order: %1", _orderId));
        // ... business logic
        _logger.log(strFmt("Order %1 completed", _orderId));
    }
}
```

### Usage

```xpp
static void TestComposition(Args _args)
{
    // Single logger
    BusinessService service1 = new BusinessService(new ConsoleLogger());
    service1.processOrder("SO-001");
    
    // Multiple loggers via composition
    MultiLogger multi = new MultiLogger();
    multi.addLogger(new ConsoleLogger());
    multi.addLogger(new FileLogger());
    
    BusinessService service2 = new BusinessService(multi);
    service2.processOrder("SO-002");
    // Logs to BOTH console and file
}
```

### Key Insight

> **Composition > Inheritance** for cross-cutting concerns (logging, caching, auth)
> - Add/remove loggers at runtime
> - No inheritance hierarchy explosion
> - Each logger single responsibility

---

## Exercise Completion Checklist

| Exercise | Concept | Done? | Notes |
|----------|---------|-------|-------|
| 1 | Class/Object/Encapsulation | ☐ | |
| 2 | Inheritance/Template Method | ☐ | |
| 3 | Interfaces/Polymorphism | ☐ | |
| 4 | Encapsulation/Invariants | ☐ | |
| 5 | Factory Pattern | ☐ | |
| 6 | Strategy Pattern | ☐ | |
| 7 | Dependency Inversion | ☐ | |
| 8 | Observer Pattern | ☐ | |
| 9 | Template Method | ☐ | |
| 10 | Composition over Inheritance | ☐ | |

---

## Next Steps

After completing all 10:
1. **Read Chapter 7** (Methods, Exceptions, Classes) — you'll understand it deeply
2. **Read Chapter 13** (Event Handlers) — you'll recognize Observer pattern
3. **Read Chapter 14** (Extensibility) — you'll understand CoC as Decorator
4. **Read Chapter 12** (SysOperation) — you'll see Command + Template Method

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*