---
name: d365-oop-primer
description: OOP concepts mapped to X++ — classes, inheritance, interfaces, polymorphism, SOLID for D365 F&O developers
metadata:
  type: reference
  last-verified: 2026-11-22
---

# OOP Primer for D365 F&O Developers

> **Read this alongside Chapter 3 (Language Mindset) and Chapter 7 (Methods, Exceptions, Classes)** if you're new to object-oriented programming.

---

## 1. Why OOP Matters in D365 F&O

X++ is an **object-oriented language** running on .NET CLR. Understanding OOP lets you:

- **Read standard Microsoft code** (it's all classes)
- **Write extensions properly** (CoC, event handlers are OOP patterns)
- **Design maintainable solutions** (SOLID principles apply directly)
- **Debug effectively** (call stacks, inheritance chains)

---

## 2. Core OOP Concepts → X++ Mapping

| OOP Concept | X++ Equivalent | Example |
|-------------|----------------|---------|
| **Class** | `class` keyword | `class CustTable` |
| **Object/Instance** | Variable of class type | `CustTable cust = new CustTable();` |
| **Field/Property** | Table fields, class members | `cust.AccountNum` |
| **Method** | Member function | `cust.validateWrite()` |
| **Constructor** | `new()` method | `CustTable::construct()` |
| **Inheritance** | `extends` keyword | `class MyTable extends Common` |
| **Interface** | `interface` keyword | `interface SysTestMethod` |
| **Polymorphism** | Method override + `super()` | `validateWrite()` in extensions |
| **Encapsulation** | `private`/`protected`/`public` | `private str _secret;` |
| **Abstraction** | `abstract` class | `abstract class RunBase` |
| **Static/Class member** | `static` keyword | `static void main(Args _args)` |

---

## 3. Classes and Objects

### 3.1 Class Definition

```xpp
// A simple class
public class CustomerService
{
    // Fields (encapsulated - private)
    private CustTable _customer;
    private boolean _isValidated;

    // Constructor
    public void new(CustTable _cust)
    {
        _customer = _cust;
        _isValidated = false;
    }

    // Public method (behavior)
    public boolean validate()
    {
        _isValidated = this.checkCreditLimit() && this.checkAddress();
        return _isValidated;
    }

    // Private helper (internal detail)
    private boolean checkCreditLimit()
    {
        return _customer.CreditLimit > 0;
    }
}
```

### 3.2 Using the Class

```xpp
static void UseCustomerService(Args _args)
{
    CustTable cust;
    select firstOnly cust where cust.AccountNum == "US-001";

    // Create instance (object)
    CustomerService service = new CustomerService(cust);

    // Call method
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

---

## 4. Inheritance

### 4.1 Base Class (Parent)

```xpp
// Abstract base - cannot instantiate directly
public abstract class DocumentProcessor
{
    protected DocuRef _document;

    public void new(DocuRef _doc)
    {
        _document = _doc;
    }

    // Template method - defines algorithm structure
    public final void process()
    {
        this.validate();
        this.transform();
        this.save();
        this.notify();
    }

    // Abstract - MUST be implemented by derived classes
    protected abstract void transform();

    // Virtual - CAN be overridden
    protected void validate()
    {
        // Default validation
        if (!_document)
        {
            throw error("No document");
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
```

### 4.2 Derived Classes (Children)

```xpp
// Specific processor for sales orders
public class SalesOrderProcessor extends DocumentProcessor
{
    public void new(DocuRef _doc)
    {
        super(_doc); // Call parent constructor
    }

    // Must implement abstract method
    protected void transform()
    {
        SalesTable sales = SalesTable::find(_document.RefRecId);
        if (sales)
        {
            // Custom logic: add customer info to document
            _document.Name = strFmt("%1 - %2", sales.SalesId, sales.CustAccount);
        }
    }

    // Override virtual method
    protected void validate()
    {
        super(); // Run parent validation first
        // Additional validation
        SalesTable sales = SalesTable::find(_document.RefRecId);
        if (sales && sales.SalesStatus == SalesStatus::Invoiced)
        {
            throw error("Cannot process invoiced order");
        }
    }
}

// Specific processor for purchase orders
public class PurchaseOrderProcessor extends DocumentProcessor
{
    protected void transform()
    {
        PurchTable purch = PurchTable::find(_document.RefRecId);
        if (purch)
        {
            _document.Name = strFmt("%1 - Vendor: %2", purch.PurchId, purch.VendAccount);
        }
    }
}
```

### 4.3 Polymorphism in Action

```xpp
static void ProcessDocuments(Args _args)
{
    // List of base type, holding derived instances
    List processors = new List(Types::Class);
    
    processors.addEnd(new SalesOrderProcessor(docuRef1));
    processors.addEnd(new PurchaseOrderProcessor(docuRef2));
    // Could add InvoiceProcessor, ReturnProcessor, etc.

    // Same call, different behavior (polymorphism)
    ListEnumerator enum = processors.getEnumerator();
    while (enum.moveNext())
    {
        DocumentProcessor processor = enum.current();
        processor.process(); // Calls correct transform() for each type
    }
}
```

---

## 5. Interfaces

### 5.1 Definition

```xpp
// Contract - no implementation, only signatures
public interface IExportable
{
    str exportToJson();
    str exportToXml();
    void importFromJson(str _json);
}

// Another contract
public interface IValidatable
{
    boolean validate();
    str getValidationErrors();
}
```

### 5.2 Implementation

```xpp
// Class implements multiple interfaces
public class CustomerData implements IExportable, IValidatable
{
    CustTable _customer;

    public void new(CustTable _cust)
    {
        _customer = _cust;
    }

    // IExportable implementation
    public str exportToJson()
    {
        // Simplified JSON
        return strFmt('{"AccountNum":"%1","Name":"%2"}', 
            _customer.AccountNum, _customer.Name);
    }

    public str exportToXml()
    {
        return strFmt('<Customer><AccountNum>%1</AccountNum><Name>%2</Name></Customer>',
            _customer.AccountNum, _customer.Name);
    }

    public void importFromJson(str _json)
    {
        // Parse and update _customer
    }

    // IValidatable implementation
    public boolean validate()
    {
        return _customer.AccountNum != "" && _customer.Name != "";
    }

    public str getValidationErrors()
    {
        str errors = "";
        if (!_customer.AccountNum) errors += "Missing AccountNum; ";
        if (!_customer.Name) errors += "Missing Name; ";
        return errors;
    }
}
```

### 5.3 Using Interfaces

```xpp
static void ExportAnything(Args _args)
{
    // Works with ANY class implementing IExportable
    List exportables = new List(Types::Class);
    exportables.addEnd(new CustomerData(custTable));
    exportables.addEnd(new VendorData(vendTable));
    exportables.addEnd(new ItemData(inventTable));

    ListEnumerator enum = exportables.getEnumerator();
    while (enum.moveNext())
    {
        IExportable exporter = enum.current(); // Polymorphism via interface
        str json = exporter.exportToJson();
        // Write to file, send to API, etc.
    }
}
```

---

## 6. Encapsulation & Access Modifiers

### 6.1 X++ Access Levels

| Modifier | Class Members | Table Fields | Description |
|----------|---------------|--------------|-------------|
| `public` | ✓ | ✓ | Accessible from anywhere |
| `protected` | ✓ | ✗ | Accessible in class + derived classes |
| `private` | ✓ | ✗ | Accessible only in this class |
| (default) | `protected` | `public` | Class members default to protected |

### 6.2 Best Practice: Private Fields + Public Properties

```xpp
public class BankAccount
{
    // Private field - hidden from outside
    private real _balance;
    private str _accountNumber;

    // Public read-only property (getter)
    public real balance()
    {
        return _balance;
    }

    // Public read-only property
    public str accountNumber()
    {
        return _accountNumber;
    }

    // Controlled modification (setter with validation)
    public void deposit(real _amount)
    {
        if (_amount <= 0)
        {
            throw error("Deposit must be positive");
        }
        _balance += _amount;
    }

    public void withdraw(real _amount)
    {
        if (_amount <= 0)
        {
            throw error("Withdrawal must be positive");
        }
        if (_amount > _balance)
        {
            throw error("Insufficient funds");
        }
        _balance -= _amount;
    }
}
```

---

## 7. SOLID Principles in D365 F&O

### 7.1 S - Single Responsibility Principle

**Each class should have ONE reason to change.**

```xpp
// ❌ BAD: Does too many things
class OrderProcessor
{
    public void processOrder(SalesTable _order)
    {
        this.validateOrder(_order);
        this.calculatePrices(_order);
        this.reserveInventory(_order);
        this.createPickingList(_order);
        this.sendConfirmationEmail(_order);
        this.postToGL(_order);
    }
}

// ✅ GOOD: Separate concerns
class OrderValidator { public void validate(SalesTable _order) { } }
class PriceCalculator { public void calculate(SalesTable _order) { } }
class InventoryReserver { public void reserve(SalesTable _order) { } }
class PickingListCreator { public void create(SalesTable _order) { } }
class EmailSender { public void sendConfirmation(SalesTable _order) { } }
class GLPoster { public void post(SalesTable _order) { } }

// Orchestrator (thin coordinator)
class OrderProcessingService
{
    OrderValidator validator;
    PriceCalculator calculator;
    // ... dependencies injected
    
    public void process(SalesTable _order)
    {
        validator.validate(_order);
        calculator.calculate(_order);
        // ...
    }
}
```

### 7.2 O - Open/Closed Principle

**Open for extension, closed for modification.** → **This is CoC!**

```xpp
// Standard Microsoft class (CLOSED - you can't modify)
class CustTable extends Common
{
    public boolean validateWrite()
    {
        // Base validation
        return this.AccountNum != "";
    }
}

// Your extension (OPEN - you extend without modifying)
[ExtensionOf(tableStr(CustTable))]
final class CustTable_CustomValidation_Ext
{
    public boolean validateWrite()
    {
        boolean ret = next validateWrite(); // Call base
        
        if (ret && this.CustomField == "")
        {
            ret = checkFailed("Custom field required");
        }
        return ret;
    }
}
```

### 7.3 L - Liskov Substitution Principle

**Derived classes must be substitutable for base classes.**

```xpp
// Base expects any PaymentProcessor
interface PaymentProcessor
{
    void processPayment(real _amount);
}

// ✅ GOOD: CreditCardProcessor works wherever PaymentProcessor expected
class CreditCardProcessor implements PaymentProcessor
{
    public void processPayment(real _amount) { /* charge card */ }
}

// ✅ GOOD: BankTransferProcessor also works
class BankTransferProcessor implements PaymentProcessor
{
    public void processPayment(real _amount) { /* ACH transfer */ }
}

// Client code doesn't care which implementation
class PaymentService
{
    public void process(PaymentProcessor _processor, real _amount)
    {
        _processor.processPayment(_amount); // Works for any implementation
    }
}
```

### 7.4 I - Interface Segregation

**Many specific interfaces > one general interface.**

```xpp
// ❌ BAD: Fat interface forces unused methods
interface IEverything
{
    void read();
    void write();
    void delete();
    void print();
    void email();
    void archive();
}

// ✅ GOOD: Small, focused interfaces
interface IReadable { void read(); }
interface IWritable { void write(); }
interface IDeletable { void delete(); }
interface IPrintable { void print(); }

// Class implements only what it needs
class ReadOnlyReport implements IReadable, IPrintable
{
    public void read() { }
    public void print() { }
    // No write(), delete(), email(), archive() needed
}
```

### 7.5 D - Dependency Inversion

**Depend on abstractions, not concretions.**

```xpp
// ❌ BAD: High-level depends on low-level concrete class
class OrderService
{
    SqlDatabase db = new SqlDatabase(); // Tied to SQL!
    public void save(Order _order) { db.insert(_order); }
}

// ✅ GOOD: Depends on abstraction
interface IRepository
{
    void save(Order _order);
    Order find(str _id);
}

class OrderService
{
    private IRepository _repository;
    
    public void new(IRepository _repo) // Injected!
    {
        _repository = _repo;
    }
    
    public void save(Order _order)
    {
        _repository.save(_order);
    }
}

// Can swap implementations
class SqlRepository implements IRepository { /* SQL impl */ }
class InMemoryRepository implements IRepository { /* for testing */ }
class ApiRepository implements IRepository { /* REST API */ }

// Usage
OrderService service = new OrderService(new SqlRepository());
// Or for testing:
OrderService testService = new OrderService(new InMemoryRepository());
```

---

## 8. Common OOP Patterns in D365 F&O

### 8.1 Factory Pattern

```xpp
// Creates objects without specifying exact class
class DocumentFactory
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
                throw error("Unknown document type");
        }
    }
}

// Usage
DocumentProcessor processor = DocumentFactory::create(DocuType::SalesOrder, docuRef);
processor.process();
```

### 8.2 Strategy Pattern

```xpp
// Swappable algorithms
interface PricingStrategy
{
    real calculatePrice(SalesLine _line);
}

class StandardPricing implements PricingStrategy
{
    public real calculatePrice(SalesLine _line)
    {
        return _line.SalesPrice * _line.SalesQty;
    }
}

class VolumeDiscountPricing implements PricingStrategy
{
    public real calculatePrice(SalesLine _line)
    {
        real price = _line.SalesPrice * _line.SalesQty;
        if (_line.SalesQty > 100) price *= 0.9; // 10% discount
        return price;
    }
}

// Context uses strategy
class SalesLinePricer
{
    private PricingStrategy _strategy;
    
    public void new(PricingStrategy _s)
    {
        _strategy = _s;
    }
    
    public real priceLine(SalesLine _line)
    {
        return _strategy.calculatePrice(_line);
    }
}
```

### 8.3 Template Method Pattern

```xpp
// Already shown in DocumentProcessor base class
// Base defines algorithm skeleton, derived classes fill steps
abstract class ReportGenerator
{
    public final void generate()
    {
        this.initialize();
        this.fetchData();
        this.formatData();
        this.render();
        this.cleanup();
    }
    
    protected abstract void fetchData();
    protected abstract void formatData();
    
    protected void initialize() { /* default */ }
    protected void render() { /* default */ }
    protected void cleanup() { /* default */ }
}
```

---

## 9. OOP → D365 F&O Mapping Cheat Sheet

| D365 F&O Concept | OOP Pattern | Key Insight |
|------------------|-------------|-------------|
| **Table inheritance** | Class inheritance | `extends Common` |
| **Table extension** | Decorator/Extension | `[ExtensionOf]` + `next` |
| **Form extension** | Decorator | Add controls, override methods |
| **CoC (Chain of Command)** | Decorator + Template Method | `next methodName()` |
| **Event handlers** | Observer Pattern | `[SubscribesTo]` |
| **SysOperation Service** | Command Pattern | Controller → Service |
| **Data Entity** | DTO / View Model | Business document shape |
| **RunBase/SysOperation** | Template Method | `run()`, `dialog()`, `validate()` |
| **NumberSeq** | Singleton / Factory | `newGetNum()` |
| **Security Role/Duty/Privilege** | RBAC (Role-Based Access Control) | Hierarchy of permissions |

---

## 10. Self-Test Questions

1. **What's the difference between a class and an object?**
   - Class = blueprint, Object = instance created from blueprint

2. **When do you use `abstract` vs `interface`?**
   - Abstract: shared code + required overrides | Interface: contract only, multiple implementations

3. **What does `super()` do in X++?**
   - Calls the parent class's implementation of the current method

4. **What does `next` do in CoC?**
   - Calls the next method in the chain (base or previous extension)

5. **Which SOLID principle does CoC directly implement?**
   - Open/Closed Principle

6. **Why prefer composition over inheritance?**
   - More flexible, avoids fragile base class problem, easier to test

7. **What pattern is `[SubscribesTo]`?**
   - Observer Pattern (publisher/subscriber)

8. **How do you achieve Dependency Inversion in X++?**
   - Define interfaces, inject implementations via constructor

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*