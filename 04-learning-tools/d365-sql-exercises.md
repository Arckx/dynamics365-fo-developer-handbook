---
name: d365-sql-exercises
description: 10 hands-on SQL exercises with practice schema, X++ mappings, and solutions
metadata:
  type: reference
  last-verified: 2026-11-22
---

# SQL Exercises for D365 F&O Developers

> **Do these BEFORE Chapter 6** if new to SQL. Each exercise includes SQL, X++ equivalent, and explanation.
> Practice schema provided — run in any SQL environment (Azure SQL, SQL Server, SQLite).

---

## Practice Schema

Run this first to create your practice database:

```sql
-- ============================================
-- PRACTICE SCHEMA: Simple Sales Database
-- ============================================

-- 1. Customers
CREATE TABLE CustTable (
    AccountNum     VARCHAR(20) PRIMARY KEY,
    Name           VARCHAR(100) NOT NULL,
    CustGroup      VARCHAR(10) NOT NULL,
    Currency       VARCHAR(3) DEFAULT 'USD',
    CreditLimit    DECIMAL(18,2) DEFAULT 0,
    Blocked        VARCHAR(10) DEFAULT 'None',
    CreatedDateTime DATETIME DEFAULT GETDATE(),
    ModifiedDateTime DATETIME DEFAULT GETDATE()
);

-- 2. Customer Groups (reference table)
CREATE TABLE CustGroup (
    CustGroup      VARCHAR(10) PRIMARY KEY,
    Name           VARCHAR(60) NOT NULL,
    PaymentTerms   VARCHAR(10)
);

-- 3. Items
CREATE TABLE InventTable (
    ItemId         VARCHAR(20) PRIMARY KEY,
    Name           VARCHAR(100) NOT NULL,
    ItemGroupId    VARCHAR(10) NOT NULL,
    UnitId         VARCHAR(10) DEFAULT 'PCS',
    StandardCost   DECIMAL(18,4) DEFAULT 0,
    SalesPrice     DECIMAL(18,4) DEFAULT 0
);

-- 4. Item Groups
CREATE TABLE InventItemGroup (
    ItemGroupId    VARCHAR(10) PRIMARY KEY,
    Name           VARCHAR(60) NOT NULL
);

-- 5. Sales Orders (Header)
CREATE TABLE SalesTable (
    SalesId        VARCHAR(20) PRIMARY KEY,
    CustAccount    VARCHAR(20) NOT NULL,
    OrderDate      DATE NOT NULL,
    DeliveryDate   DATE,
    SalesStatus    VARCHAR(20) DEFAULT 'OpenOrder',
    DocumentStatus VARCHAR(20) DEFAULT 'OpenOrder',
    CurrencyCode   VARCHAR(3) DEFAULT 'USD',
    SalesAmount    DECIMAL(18,2) DEFAULT 0,
    FOREIGN KEY (CustAccount) REFERENCES CustTable(AccountNum)
);

-- 6. Sales Lines
CREATE TABLE SalesLine (
    SalesId        VARCHAR(20) NOT NULL,
    LineNum        INT NOT NULL,
    ItemId         VARCHAR(20) NOT NULL,
    SalesQty       DECIMAL(18,4) NOT NULL,
    SalesPrice     DECIMAL(18,4) NOT NULL,
    LineAmount     DECIMAL(18,2) DEFAULT 0,
    DeliveryDate   DATE,
    PRIMARY KEY (SalesId, LineNum),
    FOREIGN KEY (SalesId) REFERENCES SalesTable(SalesId),
    FOREIGN KEY (ItemId) REFERENCES InventTable(ItemId)
);

-- 7. Inventory On-Hand
CREATE TABLE InventSum (
    ItemId         VARCHAR(20) NOT NULL,
    InventLocationId VARCHAR(10) NOT NULL,
    AvailPhysical  DECIMAL(18,4) DEFAULT 0,
    ReservedPhysical DECIMAL(18,4) DEFAULT 0,
    PRIMARY KEY (ItemId, InventLocationId)
);

-- 8. Vendors
CREATE TABLE VendTable (
    AccountNum     VARCHAR(20) PRIMARY KEY,
    Name           VARCHAR(100) NOT NULL,
    VendGroup      VARCHAR(10) NOT NULL,
    Currency       VARCHAR(3) DEFAULT 'USD',
    PaymentTerms   VARCHAR(10)
);

-- ============================================
-- SAMPLE DATA
-- ============================================

INSERT INTO CustGroup VALUES ('10', 'Domestic', 'Net30');
INSERT INTO CustGroup VALUES ('20', 'International', 'Net60');
INSERT INTO CustGroup VALUES ('30', 'Government', 'Net90');

INSERT INTO CustTable VALUES 
('US-001', 'Contoso Ltd', '10', 'USD', 50000, 'None', GETDATE(), GETDATE()),
('US-002', 'Fabrikam Inc', '10', 'USD', 75000, 'None', GETDATE(), GETDATE()),
('DE-001', 'GmbH Corp', '20', 'EUR', 100000, 'None', GETDATE(), GETDATE()),
('FR-001', 'Société SA', '20', 'EUR', 200000, 'Cust', GETDATE(), GETDATE()),
('US-003', 'Northwind', '30', 'USD', 10000, 'None', GETDATE(), GETDATE());

INSERT INTO InventItemGroup VALUES ('RAW', 'Raw Materials'), ('FIN', 'Finished Goods'), ('SVC', 'Services');

INSERT INTO InventTable VALUES
('ITEM-001', 'Steel Plate', 'RAW', 'KG', 10.50, 25.00),
('ITEM-002', 'Bolt M10', 'RAW', 'PCS', 0.25, 1.50),
('ITEM-003', 'Widget A', 'FIN', 'PCS', 50.00, 150.00),
('ITEM-004', 'Widget B', 'FIN', 'PCS', 75.00, 200.00),
('ITEM-005', 'Consulting', 'SVC', 'HRS', 0, 250.00);

INSERT INTO SalesTable VALUES
('SO-001', 'US-001', '2024-01-15', '2024-01-22', 'OpenOrder', 'OpenOrder', 'USD', 3000),
('SO-002', 'US-001', '2024-01-20', '2024-01-27', 'OpenOrder', 'OpenOrder', 'USD', 1500),
('SO-003', 'DE-001', '2024-01-10', '2024-01-20', 'Invoiced', 'Invoiced', 'EUR', 5000),
('SO-004', 'FR-001', '2024-01-18', '2024-01-25', 'OpenOrder', 'OpenOrder', 'EUR', 8000),
('SO-005', 'US-002', '2024-01-22', '2024-01-29', 'Delivered', 'PackingSlip', 'USD', 2500);

INSERT INTO SalesLine VALUES
('SO-001', 1, 'ITEM-003', 10, 150.00, 1500.00, '2024-01-22'),
('SO-001', 2, 'ITEM-004', 5, 300.00, 1500.00, '2024-01-22'),
('SO-002', 1, 'ITEM-001', 100, 15.00, 1500.00, '2024-01-27'),
('SO-003', 1, 'ITEM-003', 20, 150.00, 3000.00, '2024-01-20'),
('SO-003', 2, 'ITEM-004', 10, 200.00, 2000.00, '2024-01-20'),
('SO-004', 1, 'ITEM-004', 40, 200.00, 8000.00, '2024-01-25'),
('SO-005', 1, 'ITEM-001', 50, 15.00, 750.00, '2024-01-29'),
('SO-005', 2, 'ITEM-002', 500, 3.50, 1750.00, '2024-01-29');

INSERT INTO InventSum VALUES
('ITEM-001', 'WH-001', 500, 50),
('ITEM-002', 'WH-001', 10000, 200),
('ITEM-003', 'WH-001', 200, 20),
('ITEM-004', 'WH-001', 100, 10),
('ITEM-001', 'WH-002', 300, 0),
('ITEM-003', 'WH-002', 50, 0);

INSERT INTO VendTable VALUES
('VEND-001', 'Steel Supply Co', '10', 'USD', 'Net30'),
('VEND-002', 'Fastener Fast', '10', 'USD', 'Net15'),
('VEND-003', 'Euro Parts GmbH', '20', 'EUR', 'Net60');
```

---

## Exercise 1: Basic SELECT — Find Customers

> **Difficulty:** ⭐ Beginner | **Time:** 15 min | **Concepts:** SELECT, WHERE, ORDER BY, column list

### Problem

Write SQL to find all customers in group '10' (Domestic), showing only AccountNum, Name, Currency, CreditLimit. Order by Name.

### Solution

```sql
SELECT AccountNum, Name, Currency, CreditLimit
FROM CustTable
WHERE CustGroup = '10'
ORDER BY Name;
```

### X++ Equivalent

```xpp
while select AccountNum, Name, Currency, CreditLimit
    from custTable
    where custTable.CustGroup == '10'
    order by Name
{
    info(strFmt("%1 | %2 | %3 | %4", custTable.AccountNum, custTable.Name, custTable.Currency, custTable.CreditLimit));
}
```

### Key Points

| SQL | X++ |
|-----|-----|
| `SELECT col1, col2` | `select col1, col2` |
| `WHERE col = 'val'` | `where col == 'val'` |
| `ORDER BY col` | `order by col` |
| String literal | Single quotes in both |

---

## Exercise 2: INNER JOIN — Orders with Customer Names

> **Difficulty:** ⭐ Beginner | **Time:** 20 min | **Concepts:** INNER JOIN, table aliases, column qualification

### Problem

List all open sales orders with Customer Name, Order Date, Sales Amount. Only orders with status 'OpenOrder'.

### Solution

```sql
SELECT 
    st.SalesId,
    ct.Name AS CustomerName,
    st.OrderDate,
    st.SalesAmount
FROM SalesTable st
INNER JOIN CustTable ct ON st.CustAccount = ct.AccountNum
WHERE st.SalesStatus = 'OpenOrder'
ORDER BY st.OrderDate;
```

### X++ Equivalent

```xpp
SalesTable salesTable;
CustTable custTable;

while select SalesId, OrderDate, SalesAmount from salesTable
    where salesTable.SalesStatus == SalesStatus::OpenOrder
    join Name from custTable
        where custTable.AccountNum == salesTable.CustAccount
{
    info(strFmt("%1 | %2 | %3 | %4", salesTable.SalesId, custTable.Name, salesTable.OrderDate, salesTable.SalesAmount));
}
```

### Key Points

| SQL | X++ |
|-----|-----|
| `INNER JOIN table ON` | `join` + `where` clause |
| Table alias `st` | Variable name `salesTable` |
| `st.col = ct.col` | `salesTable.col == custTable.col` |
| `AS` alias | Not needed in X++ (variable names) |

---

## Exercise 3: LEFT JOIN — All Customers + Orders

> **Difficulty:** ⭐ Beginner | **Time:** 20 min | **Concepts:** LEFT JOIN, NULL handling

### Problem

List ALL customers with their order count and total sales amount. Include customers with zero orders.

### Solution

```sql
SELECT 
    ct.AccountNum,
    ct.Name,
    COUNT(st.SalesId) AS OrderCount,
    COALESCE(SUM(st.SalesAmount), 0) AS TotalSales
FROM CustTable ct
LEFT JOIN SalesTable st ON ct.AccountNum = st.CustAccount
GROUP BY ct.AccountNum, ct.Name
ORDER BY TotalSales DESC;
```

### X++ Equivalent

```xpp
CustTable custTable;
SalesTable salesTable;

while select custTable
    outer join SalesId, SalesAmount from salesTable
        where salesTable.CustAccount == custTable.AccountNum
    group by custTable.AccountNum, custTable.Name
{
    int orderCount = 0;
    real totalSales = 0;
    
    // Count orders for this customer in the joined result
    // Note: X++ outer join returns one row per match, so we count in loop
    // Better approach: use QueryRun for grouping
    info(strFmt("%1 | %2 | Orders: %3", custTable.AccountNum, custTable.Name, orderCount));
}
```

> **Note:** X++ doesn't have native GROUP BY in select statements. Use `QueryRun` or aggregate in loop.

### Better X++ Approach (QueryRun)

```xpp
Query query = new Query();
QueryBuildDataSource qbdsCust = query.addDataSource(tableNum(CustTable));
QueryBuildDataSource qbdsSales = qbdsCust.addDataSource(tableNum(SalesTable));
qbdsSales.joinMode(JoinMode::OuterJoin);
qbdsSales.relations(true);
qbdsSales.addGroupByField(fieldNum(SalesTable, SalesId));
qbdsSales.addGroupByField(fieldNum(SalesTable, SalesAmount));

QueryRun qr = new QueryRun(query);
while (qr.next())
{
    CustTable ct = qr.get(tableNum(CustTable));
    SalesTable st = qr.get(tableNum(SalesTable));
    // Process grouped results
}
```

---

## Exercise 4: EXISTS / NOT EXISTS — Customers With/Without Orders

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 25 min | **Concepts:** EXISTS, NOT EXISTS, correlated subquery

### Problem A: Find customers who HAVE placed at least one order

### Solution

```sql
SELECT AccountNum, Name
FROM CustTable ct
WHERE EXISTS (
    SELECT 1 FROM SalesTable st 
    WHERE st.CustAccount = ct.AccountNum
);
```

### Problem B: Find customers who have NEVER placed an order

### Solution

```sql
SELECT AccountNum, Name
FROM CustTable ct
WHERE NOT EXISTS (
    SELECT 1 FROM SalesTable st 
    WHERE st.CustAccount = ct.AccountNum
);
```

### X++ Equivalent

```xpp
// A: Customers WITH orders
CustTable custTable;
SalesTable salesTable;

while select custTable
    exists join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    info(strFmt("Has orders: %1 - %2", custTable.AccountNum, custTable.Name));
}

// B: Customers WITHOUT orders
while select custTable
    notexists join salesTable
        where salesTable.CustAccount == custTable.AccountNum
{
    info(strFmt("No orders: %1 - %2", custTable.AccountNum, custTable.Name));
}
```

### Key Points

| SQL | X++ |
|-----|-----|
| `EXISTS (SELECT 1 ...)` | `exists join` |
| `NOT EXISTS (...)` | `notexists join` |
| Correlated subquery | Automatic in join |
| Returns boolean | No fields from joined table |

---

## Exercise 5: Aggregation — Sales by Customer Group

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 20 min | **Concepts:** GROUP BY, aggregate functions, HAVING

### Problem

For each Customer Group, show:
- Group ID and Name
- Number of customers
- Number of orders
- Total sales amount
- Average order value

Only groups with total sales > 1000.

### Solution

```sql
SELECT 
    cg.CustGroup,
    cg.Name AS GroupName,
    COUNT(DISTINCT ct.AccountNum) AS CustomerCount,
    COUNT(st.SalesId) AS OrderCount,
    SUM(st.SalesAmount) AS TotalSales,
    AVG(st.SalesAmount) AS AvgOrderValue
FROM CustGroup cg
LEFT JOIN CustTable ct ON cg.CustGroup = ct.CustGroup
LEFT JOIN SalesTable st ON ct.AccountNum = st.CustAccount
GROUP BY cg.CustGroup, cg.Name
HAVING SUM(st.SalesAmount) > 1000
ORDER BY TotalSales DESC;
```

### X++ Equivalent (QueryRun)

```xpp
Query query = new Query();
QueryBuildDataSource qbdsGrp = query.addDataSource(tableNum(CustGroup));
QueryBuildDataSource qbdsCust = qbdsGrp.addDataSource(tableNum(CustTable));
qbdsCust.joinMode(JoinMode::OuterJoin);
qbdsCust.relations(true);
QueryBuildDataSource qbdsSales = qbdsCust.addDataSource(tableNum(SalesTable));
qbdsSales.joinMode(JoinMode::OuterJoin);
qbdsSales.relations(true);

// Add grouping
qbdsGrp.addGroupByField(fieldNum(CustGroup, CustGroup));
qbdsGrp.addGroupByField(fieldNum(CustGroup, Name));

// Add aggregates
qbdsCust.addSelectionField(fieldNum(CustTable, AccountNum), SelectionField::Count);
qbdsSales.addSelectionField(fieldNum(SalesTable, SalesId), SelectionField::Count);
qbdsSales.addSelectionField(fieldNum(SalesTable, SalesAmount), SelectionField::Sum);
qbdsSales.addSelectionField(fieldNum(SalesTable, SalesAmount), SelectionField::Average);

QueryRun qr = new QueryRun(query);
while (qr.next())
{
    CustGroup cg = qr.get(tableNum(CustGroup));
    // Access aggregates via qr.get(fieldId) or queryBuildDataSource
}
```

---

## Exercise 6: Subqueries — Top Customer per Group

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 30 min | **Concepts:** Correlated subquery, window functions (ROW_NUMBER)

### Problem

For each Customer Group, find the customer with the highest total sales amount.

### Solution (Window Function - Modern)

```sql
WITH CustomerSales AS (
    SELECT 
        ct.AccountNum,
        ct.Name,
        ct.CustGroup,
        SUM(st.SalesAmount) AS TotalSales
    FROM CustTable ct
    LEFT JOIN SalesTable st ON ct.AccountNum = st.CustAccount
    GROUP BY ct.AccountNum, ct.Name, ct.CustGroup
),
Ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY CustGroup ORDER BY TotalSales DESC) AS rn
    FROM CustomerSales
)
SELECT AccountNum, Name, CustGroup, TotalSales
FROM Ranked
WHERE rn = 1
ORDER BY CustGroup;
```

### Solution (Correlated Subquery - Compatible)

```sql
SELECT ct1.AccountNum, ct1.Name, ct1.CustGroup, cs.TotalSales
FROM CustTable ct1
JOIN (
    SELECT ct.AccountNum, SUM(st.SalesAmount) AS TotalSales
    FROM CustTable ct
    LEFT JOIN SalesTable st ON ct.AccountNum = st.CustAccount
    GROUP BY ct.AccountNum
) cs ON ct1.AccountNum = cs.AccountNum
WHERE cs.TotalSales = (
    SELECT MAX(cs2.TotalSales)
    FROM (
        SELECT ct.AccountNum, SUM(st.SalesAmount) AS TotalSales
        FROM CustTable ct
        LEFT JOIN SalesTable st ON ct.AccountNum = st.CustAccount
        GROUP BY ct.AccountNum
    ) cs2
    JOIN CustTable ct2 ON cs2.AccountNum = ct2.AccountNum
    WHERE ct2.CustGroup = ct1.CustGroup
)
ORDER BY ct1.CustGroup;
```

### X++ Approach

Use `QueryRun` with sorting + `firstOnly` per group, or process in code:

```xpp
// Get all customers with totals
Map customerTotals = new Map(Types::String, Types::Real);

while select AccountNum, CustGroup from custTable
    outer join sum(SalesAmount) from salesTable
        where salesTable.CustAccount == custTable.AccountNum
        group by custTable.AccountNum, custTable.CustGroup
{
    real total = salesTable.SalesAmount;
    customerTotals.insert(custTable.AccountNum, total);
}

// Find max per group in code
Map groupMax = new Map(Types::String, Types::Container); // [AccountNum, Total]
MapEnumerator enum = customerTotals.getEnumerator();
while (enum.moveNext())
{
    str acct = enum.currentKey();
    real total = enum.currentValue();
    CustTable ct = CustTable::find(acct);
    str group = ct.CustGroup;
    
    if (!groupMax.exists(group) || conPeek(groupMax.lookup(group), 2) < total)
    {
        groupMax.insert(group, [acct, total]);
    }
}

// Output
MapEnumerator enum2 = groupMax.getEnumerator();
while (enum2.moveNext())
{
    container data = enum2.currentValue();
    info(strFmt("Group %1: %2 (%3)", enum2.currentKey(), conPeek(data, 1), conPeek(data, 2)));
}
```

---

## Exercise 7: Data Modification — Bulk Operations

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 25 min | **Concepts:** INSERT, UPDATE, DELETE, transactions

### Problem A: Insert new customer (single)

### SQL

```sql
INSERT INTO CustTable (AccountNum, Name, CustGroup, Currency, CreditLimit)
VALUES ('US-004', 'New Customer Inc', '10', 'USD', 25000);
```

### X++

```xpp
CustTable cust;
cust.clear();
cust.AccountNum = "US-004";
cust.Name = "New Customer Inc";
cust.CustGroup = "10";
cust.Currency = "USD";
cust.CreditLimit = 25000;
cust.insert();
```

---

### Problem B: Bulk insert 1000 customers from staging

### SQL

```sql
INSERT INTO CustTable (AccountNum, Name, CustGroup, Currency, CreditLimit)
SELECT StagingAccountNum, StagingName, '10', 'USD', 10000
FROM CustStagingTable
WHERE Processed = 0;
```

### X++ (RecordInsertList - Fastest)

```xpp
CustStagingTable staging;
CustTable cust;
RecordInsertList ril = new RecordInsertList(tableNum(CustTable));

while select staging
    where staging.Processed == NoYes::No
{
    cust.clear();
    cust.AccountNum = staging.StagingAccountNum;
    cust.Name = staging.StagingName;
    cust.CustGroup = "10";
    cust.Currency = "USD";
    cust.CreditLimit = 10000;
    ril.add(cust);
}

ril.insertDatabase(); // Single batch INSERT
```

---

### Problem C: Increase credit limit 10% for group '10'

### SQL

```sql
UPDATE CustTable
SET CreditLimit = CreditLimit * 1.10,
    ModifiedDateTime = GETDATE()
WHERE CustGroup = '10';
```

### X++ (update_recordset - Single SQL)

```xpp
update_recordset CustTable
    setting CreditLimit = CreditLimit * 1.10,
            ModifiedDateTime = DateTimeUtil::utcNow()
    where CustTable.CustGroup == '10';
```

---

### Problem D: Delete customers with zero orders and zero credit

### SQL

```sql
DELETE FROM CustTable
WHERE CreditLimit = 0
AND NOT EXISTS (SELECT 1 FROM SalesTable WHERE CustAccount = CustTable.AccountNum);
```

### X++ (delete_from)

```xpp
delete_from CustTable
    where CustTable.CreditLimit == 0
    notexists join SalesTable
        where SalesTable.CustAccount == CustTable.AccountNum;
```

---

## Exercise 8: Transactions — Transfer Credit

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 20 min | **Concepts:** BEGIN/COMMIT/ROLLBACK, error handling

### Problem

Transfer $5000 credit limit from customer US-001 to US-002 atomically. If either fails, rollback both.

### SQL

```sql
BEGIN TRANSACTION;
BEGIN TRY
    UPDATE CustTable SET CreditLimit = CreditLimit - 5000 WHERE AccountNum = 'US-001';
    IF @@ROWCOUNT = 0 THROW 50001, 'Source not found', 1;
    
    UPDATE CustTable SET CreditLimit = CreditLimit + 5000 WHERE AccountNum = 'US-002';
    IF @@ROWCOUNT = 0 THROW 50002, 'Target not found', 1;
    
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    THROW;
END CATCH;
```

### X++

```xpp
static void TransferCredit(Args _args)
{
    CustTable fromCust, toCust;
    const real Amount = 5000;
    
    ttsBegin;
    try
    {
        select forUpdate fromCust where fromCust.AccountNum == 'US-001';
        select forUpdate toCust where toCust.AccountNum == 'US-002';
        
        if (!fromCust || !toCust)
            throw error("Customer not found");
        
        if (fromCust.CreditLimit < Amount)
            throw error("Insufficient credit limit");
        
        fromCust.CreditLimit -= Amount;
        fromCust.update();
        
        toCust.CreditLimit += Amount;
        toCust.update();
        
        ttsCommit;
        info("Transfer successful");
    }
    catch
    {
        ttsAbort;
        error("Transfer failed - rolled back");
    }
}
```

### Key Points

| SQL | X++ |
|-----|-----|
| `BEGIN TRANSACTION` | `ttsBegin` |
| `COMMIT` | `ttsCommit` |
| `ROLLBACK` | `ttsAbort` |
| `FOR UPDATE` (lock) | `select forUpdate` |
| `TRY/CATCH` | `try/catch` |

---

## Exercise 9: Index Analysis — Missing Indexes

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 20 min | **Concepts:** Execution plans, missing index DMVs

### Problem

Find missing indexes for the SalesTable queries in this workload.

### SQL (DMV Query)

```sql
SELECT 
    migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) AS improvement_measure,
    'CREATE INDEX [IX_' + OBJECT_NAME(mid.object_id) + '_' + 
     REPLACE(REPLACE(REPLACE(ISNULL(mid.equality_columns, ''), ', ', '_'), '[', ''), ']', '') + ']' +
     ' ON ' + OBJECT_SCHEMA_NAME(mid.object_id) + '.' + OBJECT_NAME(mid.object_id) +
     ' (' + ISNULL(mid.equality_columns, '') + 
     CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ',' ELSE '' END +
     ISNULL(mid.inequality_columns, '') + ')' +
     ISNULL(' INCLUDE (' + mid.included_columns + ')', '') AS create_statement,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid ON mid.index_handle = mig.index_handle
WHERE mid.database_id = DB_ID()
  AND OBJECT_NAME(mid.object_id) IN ('SalesTable', 'SalesLine', 'CustTable')
ORDER BY improvement_measure DESC;
```

### Expected Output for Practice Schema

| Table | Suggested Index | Reason |
|-------|----------------|--------|
| SalesTable | `IX_SalesTable_CustAccount` ON (CustAccount) INCLUDE (SalesAmount, SalesStatus) | Frequent filter by CustAccount |
| SalesLine | `IX_SalesLine_ItemId` ON (ItemId) | Join to InventTable |
| CustTable | `IX_CustTable_CustGroup` ON (CustGroup) INCLUDE (CreditLimit) | Filter by group |

### D365 F&O: Add Index in AOT

1. Open table in Visual Studio
2. Right-click **Indexes** → **New Index**
3. Set properties:
   - `Name`: `Idx_CustAccount`
   - `AllowDuplicates`: Yes
   - Add fields: `CustAccount` (Ascending)
4. Set `IncludedColumns`: `SalesAmount;SalesStatus`

---

## Exercise 10: Query Plan Reading

> **Difficulty:** ⭐⭐ Intermediate | **Time:** 30 min | **Concepts:** SET SHOWPLAN, operators, costs

### Problem

Analyze this query plan and identify issues:

```sql
SET SHOWPLAN_ALL ON;
GO

SELECT st.SalesId, ct.Name, st.SalesAmount
FROM SalesTable st
INNER JOIN CustTable ct ON st.CustAccount = ct.AccountNum
WHERE st.SalesStatus = 'OpenOrder'
  AND ct.CustGroup = '10'
ORDER BY st.SalesAmount DESC;
GO

SET SHOWPLAN_ALL OFF;
```

### Sample Output Analysis

```
|--Sort (ORDER BY: [st].[SalesAmount] DESC)
     |--Nested Loops (Inner Join)
          |--Index Scan (OBJECT: [SalesTable].[IX_SalesStatus])
          |--Index Seek (OBJECT: [CustTable].[PK_CustTable], SEEK: [ct].[AccountNum]=[st].[CustAccount])
```

### Issues Found

| Issue | Operator | Fix |
|-------|----------|-----|
| **Sort** | Expensive for large result sets | Add index on `SalesAmount` or limit rows |
| **Nested Loops** | OK for small, bad for large | Hash Match better for >10k rows |
| **Index Scan on SalesStatus** | Scans all 'OpenOrder' rows | Add composite index `(SalesStatus, CustAccount)` |
| **Index Seek on PK** | Good | Keep |

### Optimized Index

```sql
CREATE INDEX IX_SalesTable_Status_CustAccount 
ON SalesTable (SalesStatus, CustAccount) 
INCLUDE (SalesId, SalesAmount, OrderDate);
```

### New Plan (Estimated)

```
|--Index Seek (OBJECT: [SalesTable].[IX_SalesTable_Status_CustAccount], 
     SEEK: [SalesStatus]='OpenOrder' AND [CustAccount] IN (...))
|--Nested Loops (Inner Join)
     |--Index Seek (OBJECT: [CustTable].[PK_CustTable])
```

---

## Exercise Completion Checklist

| Exercise | Topic | Done? |
|----------|-------|-------|
| 1 | Basic SELECT | ☐ |
| 2 | INNER JOIN | ☐ |
| 3 | LEFT JOIN | ☐ |
| 4 | EXISTS/NOT EXISTS | ☐ |
| 5 | Aggregation + GROUP BY | ☐ |
| 6 | Subqueries / Window Functions | ☐ |
| 7 | Bulk INSERT/UPDATE/DELETE | ☐ |
| 8 | Transactions | ☐ |
| 9 | Missing Indexes (DMV) | ☐ |
| 10 | Query Plan Reading | ☐ |

---

## Practice Tips

1. **Run every query** — don't just read
2. **Compare SQL ↔ X++** side by side
3. **Use Trace Parser** on your X++ to see actual SQL
4. **Modify data** — break queries, see errors
5. **Time queries** — `SET STATISTICS TIME ON`

---

## Next Steps

After completing all 10:
1. **Read Chapter 6** — Control Flow & CRUD
2. **Read Chapter 21** — Performance & SQL Tuning
3. **Practice on real Tier-1** — run DMV queries there
4. **Learn Query Store** — `sys.query_store_*`

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*