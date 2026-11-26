---
name: d365-sql-primer
description: SQL basics mapped to X++ — SELECT, JOIN, INDEX, transactions, query plans for D365 F&O developers
metadata:
  type: reference
  last-verified: 2026-11-22
---

# SQL Primer for D365 F&O Developers

> **Glossary:** See the [Business Glossary](d365-business-glossary.md) for term definitions.

> **Read this alongside Chapter 5 (X++ Data Types) and Chapter 6 (Control Flow & CRUD)** if you're new to relational databases.

---

## 1. Why SQL Matters in D365 F&O

Every X++ `select`, `insert`, `update`, `delete` **becomes a SQL statement** executed against Azure SQL Database.

```
X++ Code                    →     SQL Generated
─────────────────────────────────────────────────────────────────
select CustTable            →     SELECT * FROM CUSTTABLE
    where CustGroup == '10'        WHERE CUSTGROUP = '10'

insert_recordset CustTable  →     INSERT INTO CUSTTABLE (...)
    setting ...                   SELECT ... FROM ...

update_recordset CustTable  →     UPDATE CUSTTABLE SET ...
    setting ... WHERE ...         WHERE ...

while select CustTable      →     Cursor-based fetch loop
    join SalesTable              (one round-trip per row!)
```

**Understanding SQL = writing performant X++.**

---

## 2. Relational Database Basics

### 2.1 Tables, Rows, Columns

```sql
-- A table = entity (Customer)
-- A row  = instance (Customer US-001)
-- A column = attribute (Name, Currency, CreditLimit)

-- CUSTTABLE example:
| ACCOUNTNUM | NAME           | CUSTGROUP | CURRENCY | CREDITLIMIT |
|------------|----------------|-----------|----------|-------------|
| US-001     | Contoso Ltd    | 10        | USD      | 50000.00    |
| US-002     | Fabrikam Inc   | 20        | USD      | 75000.00    |
| DE-001     | GmbH Corp      | 10        | EUR      | 100000.00   |
```

### 2.2 Keys

| Key Type | Purpose | Example |
|----------|---------|---------|
| **Primary Key (PK)** | Uniquely identifies each row | `ACCOUNTNUM` in CUSTTABLE |
| **Foreign Key (FK)** | Links to another table's PK | `CUSTACCOUNT` in SALESTABLE → `ACCOUNTNUM` in CUSTTABLE |
| **Alternate Key** | Unique but not PK | `EMAIL` in CUSTTABLE (if unique) |
| **Surrogate Key** | System-generated (RecId) | `RECID` in every table |

### 2.3 Normalization (1NF → 3NF)

```
1NF: Atomic values, no repeating groups
     ❌ BAD: Items = "Item1, Item2, Item3"
     ✅ GOOD: Separate SALESLINE rows

2NF: No partial dependencies (all non-key cols depend on WHOLE PK)
     ❌ BAD: SALESLINE has CUSTNAME (depends on SALESID only)
     ✅ GOOD: CUSTNAME only in CUSTTABLE

3NF: No transitive dependencies (non-key → non-key)
     ❌ BAD: CUSTTABLE has STATE_TAX_RATE (depends on STATE, not CUST)
     ✅ GOOD: Move to STATE table
```

---

## 3. SELECT → X++ Mapping

### 3.1 Basic Queries

| SQL | X++ | Notes |
|-----|-----|-------|
| `SELECT * FROM CUSTTABLE` | `select custTable` | Avoid `*` in production |
| `SELECT ACCOUNTNUM, NAME FROM CUSTTABLE` | `select AccountNum, Name from custTable` | **Always list columns** |
| `SELECT * FROM CUSTTABLE WHERE CUSTGROUP = '10'` | `select custTable where custTable.CustGroup == '10'` | Single quotes in SQL, double in X++ |
| `SELECT * FROM CUSTTABLE WHERE CREDITLIMIT > 10000` | `select custTable where custTable.CreditLimit > 10000` | Same operators |
| `SELECT TOP 10 * FROM CUSTTABLE` | `select firstOnly10 custTable` | `firstOnly`, `firstOnly10`, etc. |
| `SELECT DISTINCT CUSTGROUP FROM CUSTTABLE` | Not directly supported | Use `group by` or temp table |

### 3.2 ORDER BY and Pagination

```sql
-- SQL
SELECT * FROM CUSTTABLE 
ORDER BY NAME ASC 
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

```xpp
// X++ - no native pagination, use QueryRun
Query query = new Query();
QueryBuildDataSource qbds = query.addDataSource(tableNum(CustTable));
qbds.addSortField(fieldNum(CustTable, Name), SortOrder::Ascending);

QueryRun qr = new QueryRun(query);
// Skip 20
for (int i = 0; i < 20 && qr.next(); i++) { }
// Take 10
for (int i = 0; i < 10 && qr.next(); i++) {
    CustTable cust = qr.get(tableNum(CustTable));
    // Process
}
```

---

## 4. JOINs — The Critical Part

### 4.1 JOIN Types Visual

```
CUSTTABLE (Customers)          SALESTABLE (Orders)
┌─────────┬────────┐           ┌─────────┬────────────┐
│ ACCOUNT │ NAME   │           │ SALESID │ CUSTACCOUNT│
├─────────┼────────┤           ├─────────┼────────────┤
│ US-001  │ Contoso│           │ SO-001  │ US-001     │
│ US-002  │ Fabr.  │           │ SO-002  │ US-001     │
│ DE-001  │ GmbH   │           │ SO-003  │ US-003     │  ← No customer!
└─────────┴────────┘           └─────────┴────────────┘
```

| JOIN Type | SQL | X++ | Result Rows | Use When |
|-----------|-----|-----|-------------|----------|
| **INNER** | `INNER JOIN` | `join` | Only matches (US-001 × 2 orders) | Both must exist |
| **LEFT OUTER** | `LEFT JOIN` | `outer join` | All customers + orders (GmbH with null) | Keep all from left |
| **RIGHT OUTER** | `RIGHT JOIN` | N/A | All orders + customers | Keep all from right |
| **EXISTS** | `EXISTS (SELECT...)` | `exists join` | Only customers WITH orders (1 row each) | Boolean check only |
| **NOT EXISTS** | `NOT EXISTS` | `notexists join` | Customers WITHOUT orders (DE-001) | Find missing |

### 4.2 X++ JOIN Examples

```xpp
// INNER JOIN - customers with orders
while select custTable
    join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // One row per order (Contoso appears twice)
}

// OUTER JOIN - all customers, orders if exist
while select custTable
    outer join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // GmbH appears once with salesTable fields = blank/zero
}

// EXISTS JOIN - customers who HAVE orders (boolean only)
while select custTable
    exists join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // Contoso once, Fabrikam once, GmbH excluded
    // salesTable buffer NOT populated!
}

// NOTEXISTS JOIN - customers with NO orders
while select custTable
    notexists join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // Only GmbH (no matching sales)
}
```

### 4.3 JOIN Performance Rule

```xpp
// ❌ SLOW: N+1 problem - one query per customer!
while select custTable
{
    SalesTable sales;
    select firstOnly sales where sales.CustAccount == custTable.AccountNum;
    // 1000 customers = 1001 queries!
}

// ✅ FAST: Single query with JOIN
while select custTable
    exists join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // 1 query!
}

// ✅ FAST: If you need order data
while select custTable
    join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    // 1 query, all data
}
```

---

## 5. Data Modification

### 5.1 INSERT

```sql
-- SQL
INSERT INTO CUSTTABLE (ACCOUNTNUM, NAME, CUSTGROUP, CURRENCY)
VALUES ('US-003', 'New Customer', '10', 'USD');
```

```xpp
// X++
CustTable cust;
cust.clear();
cust.AccountNum = "US-003";
cust.Name = "New Customer";
cust.CustGroup = "10";
cust.Currency = "USD";
cust.insert();  // Single row
```

```xpp
// BULK INSERT - much faster!
CustTable cust;
RecordInsertList ril = new RecordInsertList(tableNum(CustTable));

for (int i = 1; i <= 10000; i++)
{
    cust.clear();
    cust.AccountNum = strFmt("IMP-%1", i);
    cust.Name = strFmt("Imported Customer %1", i);
    cust.CustGroup = "10";
    cust.Currency = "USD";
    ril.add(cust);
}

ril.insertDatabase();  // Single batch INSERT
```

### 5.2 UPDATE

```sql
-- SQL
UPDATE CUSTTABLE 
SET CREDITLIMIT = CREDITLIMIT * 1.1 
WHERE CUSTGROUP = '10';
```

```xpp
// X++ - single row
CustTable cust;
select forUpdate cust where cust.AccountNum == "US-001";
cust.CreditLimit = 55000;
cust.update();
```

```xpp
// X++ - BULK UPDATE (single SQL statement!)
update_recordset CustTable
    setting CreditLimit = CreditLimit * 1.1
    where CustTable.CustGroup == '10';
```

### 5.3 DELETE

```sql
-- SQL
DELETE FROM CUSTTABLE WHERE BLOCKED = 1;
```

```xpp
// X++ - single row
CustTable cust;
select forUpdate cust where cust.AccountNum == "BAD-001";
cust.delete();
```

```xpp
// X++ - BULK DELETE
delete_from CustTable where CustTable.Blocked == CustVendorBlocked::All;
```

---

## 6. Transactions

### 6.1 ACID Properties

| Property | Meaning | D365 F&O |
|----------|---------|----------|
| **Atomicity** | All or nothing | `ttsBegin` / `ttsCommit` / `ttsAbort` |
| **Consistency** | Valid state → valid state | Constraints, `validateWrite()` |
| **Isolation** | Concurrent txns don't interfere | Lock hints, `forUpdate` |
| **Durability** | Committed = permanent | SQL transaction log |

### 6.2 X++ Transaction Pattern

```xpp
static void TransferFunds(Args _args)
{
    CustTable fromCust, toCust;
    BankAccount fromBank, toBank;
    ;
    
    ttsBegin;  // Start transaction
    
    try
    {
        // Lock rows for update
        select forUpdate fromCust where fromCust.AccountNum == "US-001";
        select forUpdate toCust where toCust.AccountNum == "US-002";
        
        // Validate
        if (fromCust.CreditLimit < 1000)
            throw error("Insufficient credit");
        
        // Modify
        fromCust.CreditLimit -= 1000;
        fromCust.update();
        
        toCust.CreditLimit += 1000;
        toCust.update();
        
        // Create audit trail
        AuditLog::log("Transfer", fromCust.RecId, 1000);
        AuditLog::log("Transfer", toCust.RecId, -1000);
        
        ttsCommit;  // All succeed → commit
    }
    catch
    {
        ttsAbort;   // Any fail → rollback ALL
        throw;      // Re-throw
    }
}
```

### 6.3 Nested Transactions

```xpp
ttsBegin;  // Level 1
    // ... code ...
    ttsBegin;  // Level 2 (nested)
        // ... code ...
    ttsCommit; // Level 2 commits (but not really - waits for level 1)
ttsCommit;   // Level 1 commits → actual DB commit
```

> **Only the outermost `ttsCommit` writes to database.**

---

## 7. Indexes and Performance

### 7.1 Index Types

| Index | SQL | D365 F&O | Use For |
|-------|-----|----------|---------|
| **Clustered** | Data stored in index order | PK (RecId) or surrogate | Primary access path |
| **Non-clustered** | Separate structure | Alternate keys, FK | Lookups, JOINs, WHERE |
| **Unique** | No duplicates | `Unique: Yes` | PK, Alternate keys |
| **Covering** | Includes all query columns | `IncludedColumns` | Avoid key lookups |

### 7.2 When D365 Creates Indexes Automatically

```xpp
// Table: MyTable
// Fields: ItemId (FK), Date, Qty

// D365 auto-creates:
// 1. Clustered on RecId (always)
// 2. Non-clustered on ItemId (FK → join performance)
// 3. Primary index on PK (if defined)
// 4. Unique index on Alternate Key fields
```

### 7.3 Query Plans — Reading the Basics

```sql
-- Get query plan
SET SHOWPLAN_ALL ON;
SELECT * FROM CUSTTABLE WHERE CUSTGROUP = '10';
SET SHOWPLAN_ALL OFF;
```

**Key operators to recognize:**

| Operator | Meaning | Good/Bad |
|----------|---------|----------|
| **Clustered Index Seek** | Direct lookup by PK | ✅ Excellent |
| **Index Seek** | Non-clustered index lookup | ✅ Good |
| **Index Scan** | Read entire index | ⚠️ Large tables |
| **Clustered Index Scan** | Full table scan | ❌ Bad (unless tiny) |
| **Key Lookup** | Seek + fetch columns | ⚠️ Add covering index |
| **Nested Loops** | Row-by-row join | ✅ Small, ❌ Large |
| **Hash Match** | Build hash table, probe | ✅ Large joins |
| **Merge Join** | Sorted inputs merged | ✅ Pre-sorted data |

### 7.4 X++ CacheLookup Property

```xpp
// Table properties - set on TABLE level
CacheLookup values:
├── None           → Never cache (high churn)
├── NotInTTS       → Cache outside transactions (default)
├── Found          → Cache unique lookups by PK
├── FoundAndEmpty  → Cache "not found" too
└── EntireTable    → Cache ALL rows (small tables only)

// Guidelines:
| Table Type | CacheLookup | Example |
|------------|-------------|---------|
| Setup/Reference | EntireTable | CustGroup, InventItemGroup |
| Master data | Found | CustTable, VendTable, InventTable |
| Transactional | NotInTTS | SalesTable, CustTrans |
| High churn | None | InventTrans, LedgerTrans |
```

---

## 8. Common SQL Anti-Patterns in X++

| Anti-Pattern | X++ Code | Fix |
|--------------|----------|-----|
| **Select in loop** | `while select cust { select sales where sales.CustAccount == cust.AccountNum; }` | `exists join` or `join` |
| **Select *** | `select * from custTable` | `select AccountNum, Name from custTable` |
| **Update in loop** | `while select cust { cust.CreditLimit += 100; cust.update(); }` | `update_recordset` |
| **Delete in loop** | `while select cust { cust.delete(); }` | `delete_from` |
| **No WHERE on FK** | `while select sales { CustTable cust; select cust where cust.AccountNum == sales.CustAccount; }` | `join` or add index |
| **Functions in WHERE** | `where strUpp(CustGroup) == '10'` | Store normalized, or computed column |
| **OR in JOIN** | `join sales where sales.CustAccount == cust.AccountNum || sales.DeliveryName == cust.Name` | Split into two queries |

---

## 9. SQL → X++ Quick Reference

| Task | SQL | X++ |
|------|-----|-----|
| Single row by PK | `SELECT * FROM T WHERE ID = 1` | `select firstOnly T where T.Id == 1` |
| Exists check | `IF EXISTS (SELECT 1 FROM T WHERE...)` | `if (T::exist(...))` or `exists join` |
| Count rows | `SELECT COUNT(*) FROM T WHERE...` | `select count(RecId) from T where...` |
| Max value | `SELECT MAX(Col) FROM T` | `select maxOf(Col) from T` |
| Distinct values | `SELECT DISTINCT Col FROM T` | Use temp table + `group by` |
| Subquery | `WHERE Col IN (SELECT...)` | `exists join` or `in` operator |
| Case/If | `CASE WHEN... THEN...` | `if/else` or ternary `cond ? a : b` |
| String concat | `Col1 + ' ' + Col2` | `strFmt('%1 %2', Col1, Col2)` |
| Date math | `DATEADD(day, 7, GETDATE())` | `dateAdd(today(), 7)` |
| Null handling | `ISNULL(Col, 'default')` | `Col ? Col : 'default'` |

---

## 10. Practice Exercises

### Exercise 1: Find Customers Without Orders
```xpp
// Write X++ to find all customers who have never placed an order
// Hint: notexists join
```

### Exercise 2: Bulk Credit Limit Increase
```xpp
// Increase credit limit by 15% for all customers in group '20'
// Single SQL statement
```

### Exercise 3: Order with Customer Name
```xpp
// List all open sales orders with customer name
// Use outer join (some orders might have deleted customers?)
```

### Exercise 4: Transaction with Rollback
```xpp
// Transfer $500 from customer A to customer B
// If B doesn't exist, rollback A's deduction
```

---

## Official Microsoft Documentation
- [Dynamics 365 Finance & Operations docs](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/)
- [SQL guide for D365](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/sql-guide)
- [X++ programming guide](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language)

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*