---
name: d365-migration-guide
description: AX 2012 to D365 F&O migration guide — code upgrade patterns, metadata mapping, data migration via DMF
metadata:
  type: reference
  last-verified: 2026-11-22
---

# AX 2012 → D365 F&O Migration Guide

> **Target audience:** Developers migrating existing AX 2012 solutions to D365 F&O. Assumes familiarity with AX 2012 architecture.

---

## 1. Architecture Shifts at a Glance

| Area | AX 2012 | D365 F&O | Migration Impact |
|------|---------|----------|------------------|
| **Deployment** | On-prem / hosted | Cloud-only (SaaS) | No direct server access; LCS-managed |
| **AOT Storage** | Model store in SQL | File-based packages (`PackagesLocalDirectory`) | Different build/deploy pipeline |
| **Client** | Windows rich client | Browser-based HTML5 | Form patterns changed; no ActiveX |
| **Code Layer** | SYP/GLS/USR layers | SYS/ISV/VAR/CUS/USR (extensions only) | No over-layering; use CoC/Events |
| **Batch** | `RunBaseBatch` | `SysOperation` (preferred) | Rewrite batch jobs |
| **SSRS** | VS Business Intelligence | VS Report Designer + SSRS | RDL format compatible; redeploy |
| **Integration** | AIF, .NET Business Connector | OData, REST, Logic Apps, DMF | Rewrite integrations |
| **Security** | Role-based (AOT) | Role-based + XDS + Azure AD | Redesign roles; map to Azure AD groups |
| **EDTs** | Extended Data Types | Same concept + more system EDTs | Review EDT usage; adopt system EDTs |
| **Queries** | Query objects | Same + `QueryBuild*` runtime API | Compatible; test performance |

---

## 2. Code Upgrade Process — Step by Step

### 2.1 Pre-Upgrade Assessment (Run in AX 2012)

```xpp
// 1. Run Code Upgrade Checklist (AX 2012)
// Tools > Code upgrade > Check best practices
// Export results to Excel for triage

// 2. Identify over-layered objects
// Query: SELECT * FROM ModelElement WHERE Layer > 0 AND Layer < 8
// Focus: Tables, Classes, Forms, Reports modified in CUS/VAR/USR

// 3. Inventory customizations by type
static void InventoryCustomizations(Args _args)
{
    Map customMap = new Map(Types::Integer, Types::Integer);
    ModelElement element;
    ;
    while select element
        where element.Layer > 0 && element.Layer < 8
        && element.ElementType != UtilElementType::TableField
    {
        if (customMap.exists(element.ElementType))
            customMap.insert(element.ElementType, customMap.lookup(element.ElementType) + 1);
        else
            customMap.insert(element.ElementType, 1);
    }
    // Output to Infolog or file
}
```

### 2.2 Metadata Migration (LCS Code Upgrade)

1. **Create LCS project** → **Code upgrade tile** → **New upgrade**
2. **Upload AX 2012 model store** (`.axmodel` or database backup)
3. **Run upgrade scripts** — Microsoft provides version-specific scripts (2012 R2/R3 → 7.0 → 10.0)
4. **Review conflicts** — Three-way merge tool in LCS
5. **Download upgraded models** → Import to D365 F&O dev environment

### 2.3 Post-Upgrade Code Remediation

| Pattern | AX 2012 | D365 F&O Fix |
|---------|---------|--------------|
| **Table field access** | `table.Field` | `table.Field` (same) but use EDTs |
| **Over-layered methods** | Modify base `validateWrite()` | `[ExtensionOf] class Ext { next validateWrite() }` |
| **Event subscriptions** | `PrePost` handlers in base | `[SubscribesTo] static void handler()` in extension |
| **Form modifications** | Edit base form | Form Extension + CoC on `init()`, `run()` |
| **RunBaseBatch jobs** | `class MyJob extends RunBaseBatch` | `class MyService extends SysOperationServiceBase` + Controller |
| **AIF Services** | `AifService` classes | Custom Service (`SysOperation`) + OData/Data Entity |
| **Client APIs** | `WinAPI`, `ActiveX`, `COM` | Remove — not supported in browser |
| **File I/O** | `TextIo`, `BinaryIo` | `System.IO` via .NET interop (server-side only) |
| **Direct SQL** | `Statement`, `ResultSet` | Remove — use X++ `select` or Data Entities |
| **Dialog** | `Dialog` class | `SysOperation` dialog (auto-generated) or `Dialog` (still works) |

---

## 3. Common Migration Fixes — Code Patterns

### 3.1 Over-layered Table Method → Extension with CoC

```xpp
// AX 2012: Direct modification of CustTable.validateWrite()
// D365 F&O: Extension
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Migration_Ext
{
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();
        
        // Custom validation migrated from over-layered code
        if (ret && this.CustGroup == "")
        {
            ret = checkFailed("@SYS123456"); // Use label
        }
        
        return ret;
    }
}
```

### 3.2 RunBaseBatch → SysOperation Service

```xpp
// AX 2012: RunBaseBatch
class MyBatchJob extends RunBaseBatch
{
    CustAccount custAccount;
    
    public Object dialog()
    {
        Dialog dialog = super();
        dialog.addFieldValue(extendedTypeStr(CustAccount), custAccount);
        return dialog;
    }
    
    public boolean run()
    {
        // Processing logic
        return true;
    }
}

// D365 F&O: SysOperation Pattern (3 classes)

// 1. Data Contract
[DataContractAttribute]
class MyBatchJobDataContract
{
    CustAccount custAccount;
    
    [DataMemberAttribute('CustAccount')]
    public CustAccount parmCustAccount(CustAccount _custAccount = custAccount)
    {
        custAccount = _custAccount;
        return custAccount;
    }
}

// 2. Service
class MyBatchJobService extends SysOperationServiceBase
{
    public void run(MyBatchJobDataContract _contract)
    {
        CustAccount custAccount = _contract.parmCustAccount();
        // Processing logic here
    }
}

// 3. Controller (Menu Item points here)
class MyBatchJobController extends SysOperationServiceController
{
    protected void new()
    {
        super(classStr(MyBatchJobService), methodStr(MyBatchJobService, run), 
              SysOperationExecutionMode::Synchronous);
    }
    
    // Optional: Customize dialog
    public static MyBatchJobController construct()
    {
        return MyBatchJobController::newFromMenuItemName(menuItemActionStr(MyBatchJob));
    }
}
```

### 3.3 AIF Inbound Port → Custom Service + Data Entity

```xpp
// AX 2012: AIF Document Service (auto-generated)
// D365 F&O: Data Entity (preferred) or Custom Service

// Option A: Data Entity (OData enabled)
[DataEntity]
public class CustCustomerV3Entity extends common
{
    // Standard entity — usually no code needed
    // Expose via OData: /data/CustCustomerV3Entities
}

// Option B: Custom Service (complex logic)
class CustCustomService extends SysOperationServiceBase
{
    [SysEntryPointAttribute(false)]
    public CustCustomResponse createCustomer(CustCustomRequest _request)
    {
        CustCustomResponse response = new CustCustomResponse();
        ttsBegin;
        try
        {
            CustTable custTable;
            custTable.clear();
            custTable.AccountNum = NumberSeq::newGetNum(CustParameters::numRefCustAccount()).num();
            custTable.Name = _request.getName();
            custTable.CustGroup = _request.getCustGroup();
            custTable.insert();
            
            response.parmAccountNum(custTable.AccountNum);
            response.parmSuccess(true);
            ttsCommit;
        }
        catch
        {
            ttsAbort;
            response.parmSuccess(false);
            response.parmErrorMessage("Creation failed");
        }
        return response;
    }
}
```

### 3.4 Client-Side Code Removal

```xpp
// AX 2012: WinAPI::shellExecute() — REMOVE
// D365 F&O: Use browser navigation
// Form: FormRun.task() or MenuItemDisplay

// AX 2012: COM/ActiveX for Excel
// D365 F&O: 
// - SSRS report with Excel rendering
// - Data Entity export to Excel (DMF)
// - Office Add-ins (Power Platform)

// AX 2012: TextIo for file read/write
// D365 F&O: .NET Interop (server-side only)
using System.IO;
using System.Text;

public static void writeFileServer(str _path, str _content)
{
    // Requires server-side execution (RunOn = Server)
    File::WriteAllText(_path, _content, Encoding::UTF8);
}
```

---

## 4. Data Migration via DMF (Data Management Framework)

### 4.1 Migration Strategy

| Data Type | Approach | Tool |
|-----------|----------|------|
| **Master data** (Customers, Vendors, Items) | Data Entities + DMF Import | DMF Workspace |
| **Transactional data** (Orders, Invoices) | Data Entities + DMF + Staging | DMF + Recurring Jobs |
| **Reference data** (Parameters, Config) | Manual setup + Data Entities | DMF / Excel Add-in |
| **Large volumes** (>1M records) | BYOD + Azure Data Factory | BYOD → ADF → DMF |
| **Delta loads** | Change tracking + Recurring DMF | DMF Change Tracking |

### 4.2 DMF Import Template (Excel)

```xpp
// Generate template programmatically
static void GenerateDMFTemplate(Args _args)
{
    DMFEntity entity = DMFEntity::findByName('CustCustomerV3Entity');
    DMFGenerateExcelTemplate::generateTemplate(entity);
    // Saves to: \Users\<user>\Documents\DMFTemplates\
}
```

### 4.3 Recurring Import Job (Automation)

```xpp
// Schedule via Batch (SysOperation)
class DMFRecurringImportController extends SysOperationServiceController
{
    protected void new()
    {
        super(classStr(DMFRecurringImportService), 
              methodStr(DMFRecurringImportService, runImport),
              SysOperationExecutionMode::Asynchronous);
    }
}

class DMFRecurringImportService extends SysOperationServiceBase
{
    [DataMemberAttribute]
    DMFExecutionId executionId;
    
    public void runImport(DMFRecurringImportContract _contract)
    {
        DMFIntegrationDMFEntityExecutionContext ctx;
        DMFExecution execution;
        ;
        
        execution = DMFExecution::find(_contract.parmExecutionId());
        if (!execution)
        {
            throw error("Execution not found");
        }
        
        ctx = DMFIntegrationDMFEntityExecutionContext::createFromExecution(execution);
        DMFIntegration::executeEntityExecutionContext(ctx);
    }
}
```

---

## 5. Testing Migration — Validation Checklist

| Category | Tests |
|----------|-------|
| **Functional** | All modified forms open, save, validate; batch jobs complete; reports render |
| **Data** | Entity record counts match source; referential integrity; number sequences continue |
| **Performance** | Query plans for top 20 queries; batch throughput; form load times |
| **Security** | Role assignments work; XDS policies filter correctly; no privilege gaps |
| **Integration** | OData endpoints return data; Logic Apps/Power Automate flows execute; DMF import/export |
| **Upgrade** | Re-run code upgrade on copy of prod data; verify no data loss |

---

## 6. Useful Queries for Migration Analysis

```sql
-- Find all over-layered objects in AX 2012
SELECT 
    element.Name,
    element.ElementType,
    CASE element.Layer 
        WHEN 0 THEN 'SYS' 
        WHEN 2 THEN 'GLS' 
        WHEN 4 THEN 'FPK' 
        WHEN 6 THEN 'SLN' 
        WHEN 8 THEN 'VAR' 
        WHEN 10 THEN 'CUS' 
        WHEN 12 THEN 'USR' 
    END as LayerName,
    model.Name as ModelName
FROM ModelElement element
JOIN Model model ON element.Model = model.Id
WHERE element.Layer > 0 AND element.Layer < 14
ORDER BY element.Layer, element.ElementType, element.Name;

-- Find modified table methods (validateWrite, insert, update, delete)
SELECT element.Name, parent.Name as TableName, element.ElementType
FROM ModelElement element
JOIN ModelElement parent ON element.ParentId = parent.Id
WHERE element.Layer > 0 
  AND element.ElementType IN (44, 45, 46, 47) -- Method types
  AND parent.ElementType = 40 -- Table
ORDER BY parent.Name, element.Name;

-- Find event handler subscriptions (AX 2012 Pre/Post)
SELECT element.Name, element.Properties
FROM ModelElement element
WHERE element.ElementType = 44 -- Method
  AND element.Properties LIKE '%Pre%' OR element.Properties LIKE '%Post%';
```

---

## 7. Microsoft Resources

- **Code Upgrade Guide**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/migration-upgrade/upgrade-overview
- **AX 2012 to F&O Migration**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/migration-upgrade/ax2012-migration
- **Data Management Framework**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro
- **SysOperation Framework**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-framework
- **Extensibility Patterns**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensibility-home-page

---

## 8. Quick Reference: Migration Decision Tree

```
START: Customization in AX 2012
│
├─ Is it a TABLE modification?
│   ├─ New fields/indices/relations → Table Extension
│   ├─ Modified validateWrite/insert/update/delete → Table Extension + CoC
│   └─ New methods → Table Extension
│
├─ Is it a FORM modification?
│   ├─ New controls/data sources → Form Extension
│   ├─ Modified init/run/validate → Form Extension + CoC
│   └─ Event handlers → Form Extension + [SubscribesTo]
│
├─ Is it a CLASS modification?
│   ├─ New methods → Class Extension
│   ├─ Modified existing methods → Class Extension + CoC
│   └─ New event subscriptions → Class Extension + [SubscribesTo]
│
├─ Is it a BATCH JOB (RunBaseBatch)?
│   └─ Rewrite as SysOperation Service + Controller
│
├─ Is it an AIF SERVICE?
│   ├─ Simple CRUD → Data Entity (OData)
│   └─ Complex logic → Custom Service (SysOperation)
│
├─ Is it CLIENT-SIDE CODE (WinAPI, COM, ActiveX)?
│   └─ REMOVE — Replace with browser-compatible pattern
│
└─ Is it DIRECT SQL?
    └─ REMOVE — Replace with X++ select or Data Entity
```

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*