# D365 F&O Handbook Appendices

---

## Appendix 1: Common EDT Reference Table

| EDT | Description |
| :--- | :--- |
| **CustAccount** | Unique identifier for a Customer account. |
| **VendAccount** | Unique identifier for a Vendor account. |
| **ItemId** | Unique identifier for a product/item master record. |
| **AmountMST** | Monetary amount in the company's Main System Currency. |
| **Qty** | Numeric representation of a quantity. |
| **TransDate** | Date associated with a financial or inventory transaction. |
| **LedgerJournalId** | Unique identifier for a general ledger journal header. |
| **Voucher** | Document number used for financial tracking. |

---

## Appendix 2: X++ -> SQL Translation Cheat Sheet

| X++ Code | SQL Equivalent |
| :--- | :--- |
| `select * from custTable where custTable.AccountNum == '1001';` | `SELECT * FROM CUSTTABLE WHERE ACCOUNTNUM = '1001';` |
| `update_recordset custTable setting CreditMax = 5000 where custTable.AccountNum == '1001';` | `UPDATE CUSTTABLE SET CREDITMAX = 5000 WHERE ACCOUNTNUM = '1001';` |
| `delete_from custTable where custTable.AccountNum == '1001';` | `DELETE FROM CUSTTABLE WHERE ACCOUNTNUM = '1001';` |
| `while select sum(AmountMST) from custTrans group by AccountNum` | `SELECT SUM(AMOUNTMST), ACCOUNTNUM FROM CUSTTRANS GROUP BY ACCOUNTNUM;` |

---

## Appendix 3: Debugging Cookbook

### 1. Breakpoint not hitting
*   **Build/Deploy:** Ensure the project was built successfully and deployed to the server.
*   **Debugger process:** Ensure you are attached to the correct `w3wp.exe` or `Microsoft.Dynamics.AX.Batch.Service.exe` process.
*   **Symbol files:** Ensure PDBs are correctly generated and loaded by the debugger.
*   **Client vs Server:** Check if the code is running on the AOS (Server) or Client (Browser/Form). Set breakpoints in the appropriate tier.

### 2. Infolog missing
*   **Form pattern:** Ensure you are using `info()` or `error()` methods properly.
*   **Transaction scope:** If inside an `ttsBegin`/`ttsCommit` block that aborts, info messages may be rolled back.
*   **Batch job:** If running in batch, check the "Batch job history" -> "Log" for the output instead of the screen.

### 3. Trace Parser basics
*   **Capture:** Use the Trace Parser tool to capture a trace while performing the slow operation.
*   **Analysis:** Look for high-latency SQL statements or long-running X++ methods in the "Call Tree" and "SQL" tabs.

---

## Appendix 4: Microsoft Learn Master URL List

### Development Fundamentals
*   [X++ Programming Language](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language) <!-- Verified: 2026-11-22 -->
*   [Development Environment](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/development-tools-overview) <!-- Verified: 2026-11-22 -->

### Data Management
*   [Data Entities](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-data-management-framework) <!-- Verified: 2026-11-22 -->
*   [Extensible Data Security (XDS)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/extensible-data-security-policies) <!-- Verified: 2026-11-22 -->

### Administration & Operations
*   [Batch Processing](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-processing-overview) <!-- Verified: 2026-11-22 -->
*   [Workflow System](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/workflow/workflow-system-architecture) <!-- Verified: 2026-11-22 -->

---

## Appendix 5: SysQueryRangeUtil Quick Reference

| Method | Syntax | Example Usage |
|---|---|---|
| `dateRange` | `dateRange(fromDate, toDate)` | `qbr.value(SysQueryRangeUtil::dateRange(today()-30, today()));` |
| `monthRange` | `monthRange(year, fromMonth, toMonth)` | `qbr.value(SysQueryRangeUtil::monthRange(2026, 1, 3));` |
| `yearRange` | `yearRange(fromYear, toYear)` | `qbr.value(SysQueryRangeUtil::yearRange(2025, 2026));` |
| `dayRange` | `dayRange(fromDay, toDay)` | `qbr.value(SysQueryRangeUtil::dayRange(1, 15));` |
| `customerRange` | `customerRange(fromCust, toCust)` | `qbr.value(SysQueryRangeUtil::customerRange('CUST-001', 'CUST-100'));` |
| `vendorRange` | `vendorRange(fromVend, toVend)` | `qbr.value(SysQueryRangeUtil::vendorRange('VEND-001', 'VEND-100'));` |
| `itemRange` | `itemRange(fromItem, toItem)` | `qbr.value(SysQueryRangeUtil::itemRange('ITEM-001', 'ITEM-100'));` |
| `intRange` | `intRange(fromInt, toInt)` | `qbr.value(SysQueryRangeUtil::intRange(100, 200));` |

**Key Pattern:** Always use with `QueryBuildRange.value()` for dynamic query filters in `executeQuery()` or data source `init()` methods.
