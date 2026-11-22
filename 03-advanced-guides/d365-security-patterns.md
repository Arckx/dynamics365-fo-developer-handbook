---
name: d365-security-patterns
description: D365 F&O security patterns — role/privilege design, XDS policies, audit logging, compliance
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Security Patterns Guide

> **Target audience:** Developers and security architects designing role-based access, XDS policies, and audit compliance for D365 F&O.

---

## 1. Security Model Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    D365 F&O SECURITY HIERARCHY                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  AZURE AD (Identity Provider)                                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SECURITY ROLE                                     │    │
│  │  (e.g., "Accounts Payable Clerk", "Warehouse Manager")              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      DUTIES                                          │    │
│  │  (e.g., "Process vendor invoices", "Manage inventory")              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     PRIVILEGES                                       │    │
│ │  (e.g., "View vendors", "Create purchase orders", "Approve invoices")│    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PERMISSIONS                                       │    │
│  │  (Table: CustTable, Access: Read/Write/Create/Delete/Correct)       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    XDS POLICIES (Record-Level)                       │    │
│  │  (Filter: "DataAreaId == currentCompany()", "CustGroup == 'INT'")   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Role Design Worksheet

### 2.1 Role Definition Template

```markdown
# Role: [Role Name]
## Description
[Business purpose of this role]

## Assignment
- **Assigned to:** [Job titles / Azure AD groups]
- **Segregation of Duties conflicts:** [List conflicting roles]
- **License type:** [Operations / Team Members / Activity]

## Duties Included
| Duty Name | Duty Description | Required? |
|-----------|------------------|-----------|
| Duty1 | Description | Yes/No |

## Privileges Included (Direct)
| Privilege Name | Access Level | Tables/Menu Items |
|----------------|--------------|-------------------|
| Priv1 | Read/Write/Create/Delete | CustTable, CustInvoiceJournal |

## XDS Policies Applied
| Policy Name | Filter Expression | Tables Affected |
|-------------|-------------------|-----------------|
| Policy1 | DataAreaId == currentCompany() | CustTable, VendTable |

## Menu Items Granted
| Menu Item | Type | Access |
|-----------|------|--------|
| CustTableListPage | Display | Read |
| CustInvoiceJournal | Display | Read/Write |

## Compliance Notes
- **SOX:** [Relevant controls]
- **GDPR:** [PII access]
- **Segregation:** [Conflicts documented]
```

### 2.2 Example: Accounts Payable Clerk Role

```xml
<!-- Role definition (AOT XML) -->
<Role Name="AccountsPayableClerk" Description="Processes vendor invoices and payments">
  <Duties>
    <Duty Name="ProcessVendorInvoices" />
    <Duty Name="ManageVendorPayments" />
    <Duty Name="InquireVendorBalances" />
  </Duties>
  
  <Privileges>
    <Privilege Name="VendInvoiceView" Access="Read" />
    <Privilege Name="VendInvoiceCreate" Access="Create" />
    <Privilege Name="VendInvoiceEdit" Access="Update" />
    <Privilege Name="VendPaymentCreate" Access="Create" />
    <Privilege Name="VendPaymentPost" Access="Update" />
  </Privileges>
  
  <XDSPolicies>
    <Policy Name="CompanyDataPolicy" />
  </XDSPolicies>
</Role>
```

---

## 3. XDS (Extensible Data Security) Patterns

### 3.1 XDS Policy Types

| Type | Use Case | Example |
|------|----------|---------|
| **Constrained** | Filter by fixed value | `DataAreaId == 'USMF'` |
| **Contextual** | Filter by user context | `DataAreaId == currentCompany()` |
| **Role-based** | Filter by user role | `CustGroup == 'INTERNAL' && UserHasRole('InternalSales')` |
| **Hierarchical** | Filter by org hierarchy | `RecId in (select RecId from DirParty where PartyHierarchy == userOrg())` |
| **Time-based** | Filter by date range | `TransDate >= @StartOfFiscalYear && TransDate <= @EndOfFiscalYear` |

### 3.2 XDS Policy Implementation

```xpp
/// <summary>
/// XDS Policy: Restrict customers by customer group
/// </summary>
class CustGroupXDSPolicy
{
    /// <summary>
    /// Returns the filter query for the policy
    /// </summary>
    public static Query buildQuery()
    {
        Query query = new Query();
        QueryBuildDataSource qbds;
        ;
        
        qbds = query.addDataSource(tableNum(CustTable));
        
        // Add range for allowed customer groups
        // This could come from a parameter table per role
        QueryBuildRange qbr = qbds.addRange(fieldNum(CustTable, CustGroup));
        qbr.value(SysQuery::value("10,20,30")); // Allowed groups
        
        // Always enforce company filter
        qbr = qbds.addRange(fieldNum(CustTable, DataAreaId));
        qbr.value(queryValue(currentCompany()));
        
        return query;
    }
    
    /// <summary>
    /// Policy entry point - called by kernel
    /// </summary>
    [XDSFilterAttribute]
    public static Query xdsFilter()
    {
        return CustGroupXDSPolicy::buildQuery();
    }
}
```

### 3.3 Advanced: Dynamic XDS with User Context

```xpp
/// <summary>
/// Dynamic XDS policy based on user's assigned warehouse
/// </summary>
class WarehouseXDSPolicy
{
    [XDSFilterAttribute]
    public static Query xdsFilter()
    {
        Query query = new Query();
        QueryBuildDataSource qbds;
        str userWarehouse;
        ;
        
        // Get user's default warehouse from custom table
        userWarehouse = UserWarehouseMapping::getDefaultWarehouse(curUserId());
        
        if (!userWarehouse)
        {
            // No warehouse assigned - deny all (return empty result)
            qbds = query.addDataSource(tableNum(InventTable));
            qbds.addRange(fieldNum(InventTable, ItemId)).value("!EXISTS");
            return query;
        }
        
        // Filter inventory by user's warehouse
        qbds = query.addDataSource(tableNum(InventSum));
        qbds.addRange(fieldNum(InventSum, InventLocationId)).value(userWarehouse);
        
        // Join to InventTable for item details
        QueryBuildDataSource qbdsItem = qbds.addDataSource(tableNum(InventTable));
        qbdsItem.joinMode(JoinMode::InnerJoin);
        qbdsItem.relations(true);
        qbdsItem.addRange(fieldNum(InventTable, DataAreaId)).value(queryValue(currentCompany()));
        
        return query;
    }
}
```

### 3.4 XDS Policy Registration

```xpp
/// <summary>
/// Register XDS policies (run once via job)
/// </summary>
static void RegisterXDSPolicies(Args _args)
{
    XDSPolicy policy;
    ;
    
    // Policy 1: Customer Group restriction
    policy = XDSPolicy::construct();
    policy.parmName("CustGroupRestrictionPolicy");
    policy.parmDescription("Restricts customer access by group");
    policy.parmQueryClass(classStr(CustGroupXDSPolicy));
    policy.parmPolicyType(XDSPolicyType::Constrained);
    policy.save();
    
    // Policy 2: Warehouse restriction
    policy = XDSPolicy::construct();
    policy.parmName("WarehouseRestrictionPolicy");
    policy.parmDescription("Restricts inventory by user warehouse");
    policy.parmQueryClass(classStr(WarehouseXDSPolicy));
    policy.parmPolicyType(XDSPolicyType::Contextual);
    policy.save();
    
    // Assign policies to roles
    XDSPolicyRole::assignPolicyToRole("CustGroupRestrictionPolicy", "AccountsReceivableClerk");
    XDSPolicyRole::assignPolicyToRole("WarehouseRestrictionPolicy", "WarehouseWorker");
    
    info("XDS policies registered");
}
```

---

## 4. Audit Logging Patterns

### 4.1 Database-Level Audit (SQL Server Audit)

```sql
-- Enable SQL Server Audit for sensitive tables
USE master;
GO

CREATE SERVER AUDIT [D365FO_SensitiveData_Audit]
TO FILE (
    FILEPATH = 'N:\AuditLogs\',
    MAXSIZE = 1 GB,
    MAX_FILES = 10,
    RESERVE_DISK_SPACE = ON
)
WITH (QUEUE_DELAY = 1000, ON_FAILURE = CONTINUE);
GO

ALTER SERVER AUDIT [D365FO_SensitiveData_Audit] WITH (STATE = ON);
GO

-- Database audit specification
USE [D365FO_Database];
GO

CREATE DATABASE AUDIT SPECIFICATION [SensitiveTables_Audit]
FOR SERVER AUDIT [D365FO_SensitiveData_Audit]
ADD (SELECT, INSERT, UPDATE, DELETE ON OBJECT::[dbo].[CustTable] BY [public]),
ADD (SELECT, INSERT, UPDATE, DELETE ON OBJECT::[dbo].[VendTable] BY [public]),
ADD (SELECT, INSERT, UPDATE, DELETE ON OBJECT::[dbo].[BankAccountTable] BY [public]),
ADD (SELECT, INSERT, UPDATE, DELETE ON OBJECT::[dbo].[HcmWorker] BY [public])
WITH (STATE = ON);
GO
```

### 4.2 Application-Level Audit (X++)

```xpp
/// <summary>
/// Audit logger for business-critical operations
/// </summary>
class AuditLogger
{
    private static AuditLogTable auditLog;
    
    /// <summary>
    /// Log a business event with full context
    /// </summary>
    public static void log(
        str _eventType,           // e.g., "VendorInvoicePosted"
        str _entityName,          // e.g., "VendInvoiceJour"
        RecId _entityRecId,       // Record ID
        str _action,              // "Create", "Update", "Delete", "Post", "Approve"
        Map _oldValues = null,    // Field values before change
        Map _newValues = null,    // Field values after change
        str _description = "")    // Human-readable description
    {
        // Only log in non-test environments
        if (SysTest::isRunning())
            return;
        
        ttsBegin;
        auditLog.clear();
        auditLog.EventType = _eventType;
        auditLog.EntityName = _entityName;
        auditLog.EntityRecId = _entityRecId;
        auditLog.Action = _action;
        auditLog.UserId = curUserId();
        auditLog.SessionId = SessionId();
        auditLog.Company = curExt();
        auditLog.Timestamp = DateTimeUtil::utcNow();
        auditLog.ClientIp = AuditLogger::getClientIp();
        auditLog.Description = _description;
        
        // Serialize changed fields
        if (_oldValues || _newValues)
        {
            auditLog.Changes = AuditLogger::serializeChanges(_oldValues, _newValues);
        }
        
        // Add correlation ID for tracing
        auditLog.CorrelationId = SysCorrelationContext::getCurrentCorrelationId();
        
        auditLog.insert();
        ttsCommit;
        
        // Also send to App Insights
        TelemetryClient::getInstance().trackEvent("AuditEvent",
            new Map(Types::String, Types::AnyType).fromArray([
                ["eventType", _eventType],
                ["entity", _entityName],
                ["action", _action],
                ["user", curUserId()]
            ]));
    }
    
    /// <summary>
    /// Capture field-level changes for update operations
    /// </summary>
    public static void logUpdate(Common _oldRecord, Common _newRecord, str _eventType)
    {
        Map oldValues = new Map(Types::String, Types::AnyType);
        Map newValues = new Map(Types::String, Types::AnyType);
        DictTable dictTable = new DictTable(_oldRecord.TableId);
        DictField dictField;
        int i;
        ;
        
        for (i = 1; i <= dictTable.fieldCnt(); i++)
        {
            dictField = dictTable.fieldCnt2Obj(i);
            if (dictField && !dictField.isSystem())
            {
                anytype oldVal = _oldRecord.(dictField.id());
                anytype newVal = _newRecord.(dictField.id());
                
                if (oldVal != newVal)
                {
                    oldValues.insert(dictField.name(), oldVal);
                    newValues.insert(dictField.name(), newVal);
                }
            }
        }
        
        if (oldValues.elements() > 0)
        {
            AuditLogger::log(
                _eventType,
                dictTable.name(),
                _newRecord.RecId,
                "Update",
                oldValues,
                newValues,
                strFmt("Updated %1 fields", oldValues.elements())
            );
        }
    }
    
    private static str serializeChanges(Map _old, Map _new)
    {
        // JSON serialization for storage
        // Implementation depends on JSON library available
        return ""; // Simplified
    }
    
    private static str getClientIp()
    {
        // Extract from HTTP context if available
        return ""; // Simplified
    }
}

/// <summary>
/// Usage in table methods
/// </summary>
[ExtensionOf(tableStr(VendInvoiceJour))]
final class VendInvoiceJour_Audit_Ext
{
    public void insert()
    {
        next insert();
        AuditLogger::log("VendorInvoiceCreated", "VendInvoiceJour", this.RecId, "Create", 
            null, null, strFmt("Invoice %1 created for vendor %2", this.InvoiceId, this.VendAccount));
    }
    
    public void update()
    {
        VendInvoiceJour oldRecord = this.orig();
        next update();
        AuditLogger::logUpdate(oldRecord, this, "VendorInvoiceUpdated");
    }
    
    public void delete()
    {
        AuditLogger::log("VendorInvoiceDeleted", "VendInvoiceJour", this.RecId, "Delete",
            null, null, strFmt("Invoice %1 deleted", this.InvoiceId));
        next delete();
    }
}
```

### 4.3 Audit Log Query & Reporting

```xpp
/// <summary>
/// Audit log inquiry form data source
/// </summary>
class AuditLogQuery
{
    public static Query buildQuery(
        str _eventType = "",
        str _entityName = "",
        str _userId = "",
        Date _fromDate = dateNull(),
        Date _toDate = dateNull())
    {
        Query query = new Query();
        QueryBuildDataSource qbds = query.addDataSource(tableNum(AuditLogTable));
        
        if (_eventType)
            qbds.addRange(fieldNum(AuditLogTable, EventType)).value(_eventType);
        
        if (_entityName)
            qbds.addRange(fieldNum(AuditLogTable, EntityName)).value(_entityName);
        
        if (_userId)
            qbds.addRange(fieldNum(AuditLogTable, UserId)).value(_userId);
        
        if (_fromDate != dateNull())
            qbds.addRange(fieldNum(AuditLogTable, Timestamp)).value(strFmt(">= %1", _fromDate));
        
        if (_toDate != dateNull())
            qbds.addRange(fieldNum(AuditLogTable, Timestamp)).value(strFmt("<= %1", _toDate));
        
        qbds.addSortField(fieldNum(AuditLogTable, Timestamp), SortOrder::Descending);
        
        return query;
    }
}
```

---

## 5. Privilege Assertion Patterns

### 5.1 Declarative Security (Menu Items)

```xpp
// On Action Menu Item properties:
// - NeededAccessLevel: Read / Write / Create / Delete / Correct
// - NeededPermission: Table name (optional, auto-inferred)

// Example: MenuItemAction for posting invoice
// Properties:
//   ObjectType: Class
//   Object: VendInvoicePost
//   NeededAccessLevel: Update
//   NeededPermission: VendInvoiceJour
```

### 5.2 Imperative Security (Code-Based)

```xpp
/// <summary>
/// Check privilege before sensitive operation
/// </summary>
class SecurityChecker
{
    /// <summary>
    /// Verify user has specific privilege
    /// </summary>
    public static boolean hasPrivilege(str _privilegeName)
    {
        return SecurityUtil::hasPrivilege(_privilegeName);
    }
    
    /// <summary>
    /// Verify user has access to table at level
    /// </summary>
    public static boolean hasTableAccess(TableId _tableId, AccessType _access)
    {
        return SecurityUtil::hasTableAccess(_tableId, _access);
    }
    
    /// <summary>
    /// Verify user has access to menu item
    /// </summary>
    public static boolean hasMenuItemAccess(str _menuItemName, MenuItemType _type)
    {
        return SecurityUtil::hasMenuItemAccess(_menuItemName, _type);
    }
    
    /// <summary>
    /// Assert privilege - throws if not authorized
    /// </summary>
    public static void assertPrivilege(str _privilegeName, str _errorMessage = "")
    {
        if (!SecurityChecker::hasPrivilege(_privilegeName))
        {
            throw error(_errorMessage ? _errorMessage : 
                strFmt("Access denied: Requires privilege '%1'", _privilegeName));
        }
    }
    
    /// <summary>
    /// Assert table access
    /// </summary>
    public static void assertTableAccess(TableId _tableId, AccessType _access)
    {
        if (!SecurityChecker::hasTableAccess(_tableId, _access))
        {
            throw error(strFmt("Access denied: Requires %1 access to table %2", 
                _access, tableId2Name(_tableId)));
        }
    }
}

// Usage in service:
class SensitiveOperationService extends SysOperationServiceBase
{
    public void run(SensitiveOperationContract _contract)
    {
        // Assert before operation
        SecurityChecker::assertPrivilege("PostVendorInvoices");
        SecurityChecker::assertTableAccess(tableNum(VendInvoiceJour), AccessType::Update);
        
        // Proceed with operation
        this.postInvoices(_contract);
    }
}
```

### 5.3 Form-Level Security (CoC)

```xpp
[ExtensionOf(formStr(VendInvoiceJournal))]
final class VendInvoiceJournal_Security_Ext
{
    public void init()
    {
        next init();
        
        // Hide buttons based on privileges
        this.hideButtonsByPrivilege();
    }
    
    private void hideButtonsByPrivilege()
    {
        // Hide Post button if no privilege
        if (!SecurityChecker::hasPrivilege("PostVendorInvoices"))
        {
            this.controlId(FormControlIdentifier::Button, "PostButton").visible(false);
        }
        
        // Hide Delete button if no delete access
        if (!SecurityChecker::hasTableAccess(tableNum(VendInvoiceJour), AccessType::Delete))
        {
            this.controlId(FormControlIdentifier::Button, "DeleteButton").visible(false);
        }
    }
}
```

---

## 6. Segregation of Duties (SoD)

### 6.1 SoD Conflict Matrix

| Role A | Role B | Conflict | Risk | Mitigation |
|--------|--------|----------|------|------------|
| AP Clerk | AP Approver | Create + Approve invoices | Fraudulent payments | Compensating control: Review report |
| AR Clerk | Cash Receipts | Create invoice + Apply payment | Lapping | Compensating control: Bank reconciliation |
| Warehouse Worker | Inventory Adjust | Receive + Adjust inventory | Theft | Compensating control: Cycle count |
| Payroll Clerk | Payroll Approve | Create + Approve payroll | Ghost employees | Compensating control: HR review |

### 6.2 SoD Detection Query

```xpp
/// <summary>
/// Detect users with conflicting roles
/// </summary>
class SoDChecker
{
    public static void checkConflicts()
    {
        Map conflicts = new Map(Types::String, Types::Container);
        
        // Define conflict pairs
        conflicts.insert("AccountsPayableClerk,AccountsPayableApprover", 
            ["Create & Approve Invoices", "High"]);
        conflicts.insert("AccountsReceivableClerk,Cashier", 
            ["Create Invoice & Apply Payment", "High"]);
        conflicts.insert("WarehouseWorker,InventoryManager", 
            ["Receive & Adjust Inventory", "Medium"]);
        
        UserInfo user;
        SecurityRoleUser roleUser;
        SecurityRole role;
        Set userRoles;
        List conflictsFound;
        ;
        
        while select user
            where user.Id != "admin"
        {
            userRoles = new Set(Types::String);
            
            while select roleUser
                join role
                where roleUser.User == user.Id
                   && roleUser.SecurityRole == role.RecId
                   && role.Name != ""
            {
                userRoles.add(role.Name);
            }
            
            // Check each conflict
            MapEnumerator enum = conflicts.getEnumerator();
            while (enum.moveNext())
            {
                List conflictRoles = strSplit(enum.currentKey(), ",");
                boolean hasAll = true;
                
                for (int i = 1; i <= conflictRoles.elements(); i++)
                {
                    if (!userRoles.in(conflictRoles.item(i)))
                    {
                        hasAll = false;
                        break;
                    }
                }
                
                if (hasAll)
                {
                    container info = enum.currentValue();
                    conflictsFound.addEnd(strFmt("User: %1 | Conflict: %2 | Risk: %3", 
                        user.Id, conPeek(info, 1), conPeek(info, 2)));
                }
            }
        }
        
        // Report findings
        if (conflictsFound.elements() > 0)
        {
            // Send to audit log, email security team, etc.
            AuditLogger::log("SoDConflictDetected", "UserInfo", 0, "Report",
                null, null, strFmt("%1 conflicts found", conflictsFound.elements()));
        }
    }
}
```

---

## 7. Compliance Patterns

### 7.1 GDPR - Personal Data Handling

```xpp
/// <summary>
/// GDPR compliance utilities
/// </summary>
class GdprCompliance
{
    /// <summary>
    /// Find all tables containing personal data
    /// </summary>
    public static List findPersonalDataTables()
    {
        List tables = new List(Types::String);
        
        // Standard D365 tables with PII
        tables.addEnd("DirPartyTable");
        tables.addEnd("DirPerson");
        tables.addEnd("HcmWorker");
        tables.addEnd("HcmEmployment");
        tables.addEnd("CustTable"); // Contact info
        tables.addEnd("VendTable"); // Contact info
        tables.addEnd("BankAccountTable");
        tables.addEnd("TaxRegistration");
        
        // Custom tables - add yours
        // tables.addEnd("MyCustomTable");
        
        return tables;
    }
    
    /// <summary>
    /// Execute Right to Erasure (Article 17)
    /// </summary>
    public static void executeErasure(str _partyRecId)
    {
        DirPartyTable party = DirPartyTable::find(_partyRecId);
        if (!party)
            throw error("Party not found");
        
        ttsBegin;
        
        // 1. Anonymize personal fields
        party.Name = strFmt("ANONYMIZED_%1", party.RecId);
        party.update();
        
        // 2. Delete or anonymize related records
        GdprCompliance::anonymizeWorker(party.RecId);
        GdprCompliance::anonymizeCustomer(party.RecId);
        GdprCompliance::anonymizeVendor(party.RecId);
        
        // 3. Log erasure
        AuditLogger::log("GDPR_Erasure", "DirPartyTable", party.RecId, "Anonymize",
            null, null, "Right to Erasure executed");
        
        ttsCommit;
    }
    
    private static void anonymizeWorker(RecId _partyRecId)
    {
        HcmWorker worker = HcmWorker::findByPerson(_partyRecId);
        if (worker)
        {
            worker.PersonnelNumber = strFmt("ANON_%1", worker.RecId);
            // Clear PII fields
            worker.update();
        }
    }
    
    /// <summary>
    /// Data Portability (Article 20) - export user data
    /// </summary>
    public static str exportUserData(str _partyRecId)
    {
        // Generate JSON/XML with all personal data
        // Use DMF export or custom serialization
        return ""; // Simplified
    }
}
```

### 7.2 SOX - Financial Controls

```xpp
/// <summary>
/// SOX compliance - key financial controls
/// </summary>
class SoxControls
{
    /// <summary>
    /// Control: All journal postings require approval
    /// </summary>
    public static void enforceJournalApproval(LedgerJournalTable _journal)
    {
        if (_journal.JournalType == LedgerJournalType::Daily)
        {
            SecurityChecker::assertPrivilege("ApproveGeneralJournal");
            
            // Log for audit trail
            AuditLogger::log("SOX_JournalApproval", "LedgerJournalTable", 
                _journal.RecId, "Approve", null, null, 
                strFmt("Journal %1 approved by %2", _journal.JournalNum, curUserId()));
        }
    }
    
    /// <summary>
    /// Control: Number sequences cannot be reset in production
    /// </summary>
    public static void preventNumberSequenceReset(NumberSequenceReference _ref)
    {
        if (SysGlobalConfiguration::isProductionEnvironment())
        {
            throw error("Number sequence reset not allowed in production");
        }
    }
    
    /// <summary>
    /// Control: Segregation of duties for vendor master
    /// </summary>
    public static void validateVendorMasterChange(VendTable _vendor, str _action)
    {
        // Require dual approval for sensitive changes
        if (_action == "BankAccountChange" || _action == "TaxExemptChange")
        {
            if (!SecurityChecker::hasPrivilege("ApproveVendorMasterChanges"))
            {
                throw error("Vendor master change requires approval privilege");
            }
        }
    }
}
```

---

## 8. Security Audit Checklist

### 8.1 Quarterly Security Review

```markdown
# Quarterly Security Audit Checklist

## Role & Privilege Review
- [ ] Review all custom roles for least privilege
- [ ] Remove unused roles/privileges
- [ ] Verify SoD conflicts are documented and mitigated
- [ ] Check role assignments match current org structure
- [ ] Validate XDS policies cover all sensitive data

## Access Control
- [ ] Review privileged user access (sysadmin, security admin)
- [ ] Verify service accounts have minimal permissions
- [ ] Check for orphaned user accounts (disabled in AD but active in D365)
- [ ] Validate emergency access procedures

## Audit Logging
- [ ] Verify audit logs capture all critical operations
- [ ] Check log retention meets compliance requirements
- [ ] Review audit log access controls
- [ ] Test audit log query/reporting

## Data Protection
- [ ] Verify encryption at rest (SQL TDE enabled)
- [ ] Verify encryption in transit (TLS 1.2+)
- [ ] Check PII fields are identified and protected
- [ ] Validate data masking in non-prod environments

## Integration Security
- [ ] Review OData/API endpoint permissions
- [ ] Check service principal permissions (least privilege)
- [ ] Validate certificate expiration for integrations
- [ ] Review Logic Apps/Power Automate connection security

## Configuration
- [ ] Review security configuration keys
- [ ] Check license enforcement
- [ ] Validate password policies (via Azure AD)
- [ ] Review batch job service account permissions

## Incident Response
- [ ] Review security incident log
- [ ] Test breach notification procedures
- [ ] Update contact lists for security team
```

---

## 9. Microsoft Resources

- **Security Architecture**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/security-architecture
- **Role-Based Security**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/role-based-security
- **XDS Policies**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/extensible-data-security-policies
- **Audit Logging**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/auditing
- **GDPR Compliance**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lcs-solutions/gdpr-compliance
- **SOX Compliance**: https://learn.microsoft.com/en-us/dynamics365/finance/localizations/emea-fra-sox-compliance

---

## 10. Quick Reference

```xpp
// Check privilege
SecurityUtil::hasPrivilege("PrivilegeName")

// Check table access
SecurityUtil::hasTableAccess(tableNum(TableName), AccessType::Update)

// Assert in code
SecurityChecker::assertPrivilege("PrivilegeName");

// XDS Policy method
[XDSFilterAttribute]
public static Query xdsFilter() { ... }

// Audit log
AuditLogger::log("EventType", "EntityName", recId, "Action", oldValues, newValues);
```

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*