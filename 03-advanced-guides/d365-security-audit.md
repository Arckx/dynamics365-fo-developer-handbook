---
name: d365-security-audit
description: D365 F&O security audit checklist — role segregation, XDS coverage, privilege creep, audit log retention
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Security Audit Checklist

> **Usage:** Run this checklist quarterly or before major releases. Document findings and remediation.

---

## Audit Overview

| Audit Area | Frequency | Owner | Tool/Method |
|------------|-----------|-------|-------------|
| Role & Privilege Review | Quarterly | Security Admin | Security Configuration, PowerShell |
| SoD Conflict Analysis | Quarterly | Security Admin + Auditor | Custom query, GRC tool |
| XDS Policy Coverage | Semi-annual | Developer + Security | XDS Policy list, data sampling |
| Audit Log Integrity | Monthly | DBA + Security | SQL Audit, App Insights |
| Privilege Creep Detection | Quarterly | Security Admin | Role assignment diff |
| Emergency Access Review | Monthly | Security Admin | Break-glass log review |
| Integration Security | Semi-annual | Integration Team | Service principal audit |
| Compliance Validation | Annual | Compliance Officer | GDPR, SOX, PCI checklists |

---

## 1. Role & Privilege Review

### 1.1 Custom Role Inventory

```xpp
/// <summary>
/// Export all custom roles for review
/// </summary>
static void ExportCustomRoles(Args _args)
{
    SecurityRole role;
    SecurityRoleRole dutyLink;
    SecurityDuty duty;
    SecurityDutyPrivilege privLink;
    SecurityPrivilege privilege;
    SecurityPrivilegePermission permLink;
    ;
    
    // Output to file
    System.IO.StreamWriter writer = new System.IO.StreamWriter(
        @"C:\Temp\CustomRolesExport_" + System.DateTime::Now.ToString("yyyyMMdd") + ".csv");
    
    writer.WriteLine("Role,Duty,Privilege,Permission,Table/MenuItem,AccessLevel");
    
    while select role
        where role.Type == SecurityRoleType::Custom
    {
        while select dutyLink
            join duty
            where dutyLink.SecurityRole == role.RecId
               && dutyLink.SecurityDuty == duty.RecId
        {
            while select privLink
                join privilege
                where privLink.SecurityDuty == duty.RecId
                   && privLink.SecurityPrivilege == privilege.RecId
            {
                while select permLink
                    where permLink.SecurityPrivilege == privilege.RecId
                {
                    str tableName = "";
                    str menuItemName = "";
                    str accessLevel = "";
                    
                    switch (permLink.PermissionType)
                    {
                        case SecurityPermissionType::Table:
                            tableName = tableId2Name(permLink.ObjectId);
                            accessLevel = enum2str(permLink.AccessLevel);
                            break;
                        case SecurityPermissionType::MenuItem:
                            // Resolve menu item
                            break;
                    }
                    
                    writer.WriteLine(
                        "\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\"",
                        role.Name, duty.Name, privilege.Name, 
                        permLink.PermissionType, tableName, accessLevel);
                }
            }
        }
    }
    
    writer.Close();
    info("Export complete");
}
```

### 1.2 Role Review Checklist

| Check | Description | Pass/Fail | Notes |
|-------|-------------|-----------|-------|
| **Least Privilege** | Each role has minimum permissions needed | ☐ | |
| **No Wildcards** | No `*` permissions on tables/menus | ☐ | |
| **Naming Convention** | Roles follow `Module_Function_Level` (e.g., `AP_Clerk`, `AP_Manager`) | ☐ | |
| **Documentation** | Each role has business justification documented | ☐ | |
| **Owner Assigned** | Each role has a business owner | ☐ | |
| **Review Date** | Role reviewed within last 90 days | ☐ | |
| **Unused Roles** | No roles with zero assigned users > 90 days | ☐ | |

### 1.3 Privilege Review Checklist

| Check | Description | Pass/Fail | Notes |
|-------|-------------|-----------|-------|
| **Granularity** | Privileges are task-specific, not broad | ☐ | |
| **Naming** | Follows `Verb_Noun` (e.g., `CreatePurchaseOrder`) | ☐ | |
| **No Orphan Privileges** | Every privilege used by at least one duty | ☐ | |
| **Access Levels** | Create/Delete limited to need; Correct rarely used | ☐ | |
| **Table Permissions** | Only required tables listed; no `All Tables` | ☐ | |

---

## 2. Segregation of Duties (SoD) Analysis

### 2.1 Critical SoD Conflicts

```markdown
# Critical SoD Conflicts - Must Not Be Assigned to Same User

| Conflict ID | Role A | Role B | Business Risk | Compensating Control |
|-------------|--------|--------|---------------|---------------------|
| SOD-001 | AP Clerk | AP Approver | Fraudulent payments | Monthly payment review by Finance Mgr |
| SOD-002 | AR Clerk | Cash Application | Lapping scheme | Weekly bank reconciliation |
| SOD-003 | Vendor Master Maintainer | AP Clerk | Fictitious vendors | Quarterly vendor audit |
| SOD-004 | Customer Master Maintainer | AR Clerk | Fictitious customers | Quarterly customer audit |
| SOD-005 | Inventory Adjuster | Warehouse Worker | Inventory theft | Monthly cycle count |
| SOD-006 | GL Journal Poster | GL Journal Approver | Hidden entries | Monthly journal review |
| SOD-007 | Payroll Processor | Payroll Approver | Ghost employees | HR headcount reconciliation |
| SOD-008 | Fixed Asset Creator | Fixed Asset Disposer | Asset misappropriation | Annual physical inventory |
| SOD-009 | Bank Account Admin | Payment Processor | Unauthorized transfers | Dual approval on bank changes |
| SOD-010 | Security Admin | Any Business Role | Privilege escalation | Break-glass only for Security Admin |
```

### 2.2 SoD Detection Script

```xpp
/// <summary>
/// Detect users with SoD conflicts
/// </summary>
static void DetectSoDConflicts(Args _args)
{
    // Define conflict pairs (Role A, Role B, Risk Level)
    Map conflicts = new Map(Types::String, Types::Container);
    conflicts.insert("AccountsPayableClerk,AccountsPayableApprover", ["Payment Fraud", "Critical"]);
    conflicts.insert("AccountsReceivableClerk,Cashier", ["Lapping", "Critical"]);
    conflicts.insert("VendorMasterMaintainer,AccountsPayableClerk", ["Fictitious Vendor", "High"]);
    conflicts.insert("InventoryAdjustmentClerk,WarehouseWorker", ["Inventory Theft", "High"]);
    conflicts.insert("GeneralJournalPoster,GeneralJournalApprover", ["Hidden Entries", "High"]);
    conflicts.insert("PayrollClerk,PayrollApprover", ["Ghost Employees", "Critical"]);
    conflicts.insert("SecurityAdministrator,*", ["Privilege Escalation", "Critical"]);
    
    UserInfo user;
    SecurityRoleUser roleUser;
    SecurityRole role;
    Set userRoles;
    List findings;
    ;
    
    while select user
        where user.Id != "admin"
           && user.Enable == NoYes::Yes
    {
        userRoles = new Set(Types::String);
        
        while select roleUser
            join role
            where roleUser.User == user.Id
               && roleUser.SecurityRole == role.RecId
        {
            userRoles.add(role.Name);
        }
        
        // Check wildcard conflict (Security Admin + any business role)
        if (userRoles.in("SecurityAdministrator") && userRoles.elements() > 1)
        {
            findings.addEnd(strFmt("User: %1 | Conflict: SecurityAdmin + Business Role | Risk: Critical", user.Id));
        }
        
        // Check defined conflicts
        MapEnumerator enum = conflicts.getEnumerator();
        while (enum.moveNext())
        {
            List roles = strSplit(enum.currentKey(), ",");
            if (roles.elements() == 2)
            {
                if (userRoles.in(roles.item(1)) && userRoles.in(roles.item(2)))
                {
                    container info = enum.currentValue();
                    findings.addEnd(strFmt("User: %1 | Conflict: %2 + %3 | Risk: %4 | Type: %5",
                        user.Id, roles.item(1), roles.item(2), conPeek(info, 2), conPeek(info, 1)));
                }
            }
        }
    }
    
    // Output findings
    if (findings.elements() == 0)
    {
        info("No SoD conflicts detected");
    }
    else
    {
        info(strFmt("Found %1 SoD conflicts:", findings.elements()));
        for (int i = 1; i <= findings.elements(); i++)
        {
            warning(findings.item(i));
        }
        
        // Export to file for audit trail
        System.IO.File::WriteAllLines(
            @"C:\Temp\SoDConflicts_" + System.DateTime::Now.ToString("yyyyMMdd") + ".txt",
            findings);
    }
}
```

### 2.3 SoD Remediation Tracking

```markdown
# SoD Conflict Remediation Log

| User | Conflict | Risk | Status | Compensating Control | Owner | Due Date | Resolved |
|------|----------|------|--------|---------------------|-------|----------|----------|
| john.doe | AP Clerk + AP Approver | Critical | ☐ Open | Monthly review by Finance Mgr | Security Admin | 2026-12-01 | ☐ |
| jane.smith | Security Admin + AP Clerk | Critical | ☐ Mitigated | Break-glass only | Security Admin | 2026-11-15 | ☐ |

**Status Values:** Open, Mitigated (compensating control documented), Resolved (roles separated), Accepted (risk accepted with approval)
```

---

## 3. XDS Policy Coverage Audit

### 3.1 XDS Policy Inventory

```xpp
/// <summary>
/// Audit XDS policy coverage
/// </summary>
static void AuditXDSPolicies(Args _args)
{
    XDSPolicy policy;
    XDSPolicyRole policyRole;
    SecurityRole role;
    Map tableCoverage;
    ;
    
    tableCoverage = new Map(Types::String, Types::String);
    
    info("=== XDS Policy Inventory ===");
    
    while select policy
    {
        info(strFmt("Policy: %1 | Type: %2 | Query Class: %3",
            policy.Name, policy.PolicyType, policy.QueryClass));
        
        // Check assigned roles
        while select policyRole
            join role
            where policyRole.Policy == policy.RecId
               && policyRole.SecurityRole == role.RecId
        {
            info(strFmt("  -> Role: %1", role.Name));
        }
        
        // Analyze query for table coverage
        // (Would need to parse query class)
    }
    
    // Check sensitive tables for coverage
    List sensitiveTables = ["CustTable", "VendTable", "BankAccountTable", 
                            "HcmWorker", "DirPartyTable", "TaxRegistration"];
    
    info("\n=== Sensitive Table Coverage ===");
    for (int i = 1; i <= sensitiveTables.elements(); i++)
    {
        str tableName = sensitiveTables.item(i);
        boolean covered = false;
        
        // Check if any policy filters this table
        // (Simplified - would need query analysis)
        
        info(strFmt("%1: %2", tableName, covered ? "COVERED" : "NOT COVERED ⚠️"));
    }
}
```

### 3.2 XDS Coverage Checklist

| Table | Policy Name | Filter Type | Roles Applied | Tested | Pass/Fail |
|-------|-------------|-------------|---------------|--------|-----------|
| CustTable | CustGroupRestriction | Constrained | AR Clerk, AR Manager | ☐ | ☐ |
| VendTable | VendorDataPolicy | Contextual | AP Clerk, AP Manager | ☐ | ☐ |
| BankAccountTable | BankAccountSecurity | Role-based | Treasury, AP Approver | ☐ | ☐ |
| HcmWorker | HRDataPolicy | Hierarchical | HR Clerk, HR Manager | ☐ | ☐ |
| DirPartyTable | PartyDataPolicy | Contextual | All roles | ☐ | ☐ |
| [Custom] | [Policy Name] | [Type] | [Roles] | ☐ | ☐ |

### 3.3 XDS Policy Testing

```xpp
/// <summary>
/// Test XDS policy effectiveness
/// </summary>
static void TestXDSPolicies(Args _args)
{
    // Test as different users
    List testUsers = ["ar_clerk", "ap_clerk", "warehouse_user", "hr_clerk", "admin"];
    List testTables = [tableNum(CustTable), tableNum(VendTable), tableNum(InventTable)];
    
    for (int u = 1; u <= testUsers.elements(); u++)
    {
        str userId = testUsers.item(u);
        
        // Impersonate user (requires admin)
        // runAs(userId, delegate void() {
            info(strFmt("\n=== Testing as %1 ===", userId));
            
            for (int t = 1; t <= testTables.elements(); t++)
            {
                TableId tableId = testTables.item(t);
                int count = 0;
                
                // Count visible records
                // This is simplified - actual query depends on table
                switch (tableId)
                {
                    case tableNum(CustTable):
                        select count(RecId) from custTable;
                        count = custTable.RecId;
                        break;
                    // ...
                }
                
                info(strFmt("  %1: %2 records visible", tableId2Name(tableId), count));
            }
        // });
    }
}
```

---

## 4. Audit Log Integrity

### 4.1 SQL Server Audit Verification

```sql
-- 1. Verify audit is running
SELECT * FROM sys.server_audits WHERE name = 'D365FO_SensitiveData_Audit';

-- 2. Check audit file growth
SELECT 
    mf.name,
    mf.physical_name,
    mf.size * 8 / 1024 AS size_mb,
    mf.max_size * 8 / 1024 AS max_size_mb
FROM sys.master_files mf
JOIN sys.server_audits sa ON sa.audit_file_path LIKE '%' + mf.name + '%'
WHERE sa.name = 'D365FO_SensitiveData_Audit';

-- 3. Verify audit specification coverage
SELECT 
    das.name AS audit_spec_name,
    dsd.audit_action_name,
    dsd.object_name,
    dsd.principal_name
FROM sys.database_audit_specifications das
JOIN sys.database_audit_specification_details dsd ON dsd.database_specification_id = das.database_specification_id
WHERE das.name = 'SensitiveTables_Audit';

-- 4. Sample audit records (last 24 hours)
SELECT TOP 100
    event_time,
    action_id,
    succeeded,
    failed,
    server_principal_name,
    database_principal_name,
    object_name,
    statement
FROM sys.fn_get_audit_file('N:\AuditLogs\D365FO_SensitiveData_Audit*', DEFAULT, DEFAULT)
WHERE event_time > DATEADD(HOUR, -24, GETDATE())
ORDER BY event_time DESC;

-- 5. Check for audit gaps (periods with no records)
SELECT 
    CAST(event_time AS DATE) AS audit_date,
    COUNT(*) AS event_count
FROM sys.fn_get_audit_file('N:\AuditLogs\D365FO_SensitiveData_Audit*', DEFAULT, DEFAULT)
WHERE event_time > DATEADD(DAY, -30, GETDATE())
GROUP BY CAST(event_time AS DATE)
ORDER BY audit_date;
```

### 4.2 Application Audit Log Verification

```xpp
/// <summary>
/// Verify application audit log completeness
/// </summary>
static void VerifyAuditLogs(Args _args)
{
    AuditLogTable auditLog;
    Map expectedEvents;
    Date fromDate = dateAdd(today(), -7);
    Date toDate = today();
    ;
    
    // Define critical events that MUST be logged
    expectedEvents = new Map(Types::String, Types::Integer);
    expectedEvents.insert("VendorInvoicePosted", 0);
    expectedEvents.insert("CustomerInvoicePosted", 0);
    expectedEvents.insert("JournalPosted", 0);
    expectedEvents.insert("VendorMasterChanged", 0);
    expectedEvents.insert("CustomerMasterChanged", 0);
    expectedEvents.insert("BankAccountChanged", 0);
    expectedEvents.insert("NumberSequenceChanged", 0);
    expectedEvents.insert("RoleAssignmentChanged", 0);
    expectedEvents.insert("XDSPolicyChanged", 0);
    
    // Count actual events
    while select count(RecId) from auditLog
        where auditLog.Timestamp >= fromDate
           && auditLog.Timestamp <= toDate
        group by auditLog.EventType
    {
        if (expectedEvents.exists(auditLog.EventType))
        {
            expectedEvents.insert(auditLog.EventType, auditLog.RecId);
        }
    }
    
    // Report
    info("=== Audit Log Coverage (Last 7 Days) ===");
    MapEnumerator enum = expectedEvents.getEnumerator();
    while (enum.moveNext())
    {
        str eventType = enum.currentKey();
        int count = enum.currentValue();
        
        if (count == 0)
        {
            warning(strFmt("MISSING: %1 - No audit records found!", eventType));
        }
        else
        {
            info(strFmt("OK: %1 - %2 records", eventType, count));
        }
    }
    
    // Check for gaps in sequence (if using sequence numbers)
    // Check for tampering (hash chain verification)
}
```

### 4.3 Audit Log Retention Compliance

```markdown
# Audit Log Retention Requirements

| Regulation | Retention Period | Scope | Storage Location |
|------------|------------------|-------|------------------|
| SOX | 7 years | Financial transactions, journal entries, approvals | SQL Audit + App Logs |
| GDPR | 3 years (configurable) | Personal data access, modifications | App Logs + SQL Audit |
| PCI DSS | 1 year (3 years available) | Payment data access | SQL Audit |
| HIPAA | 6 years | Healthcare data access | App Logs + SQL Audit |
| Internal Policy | 5 years | All audit events | Azure Storage (archive) |

## Retention Validation Checklist

- [ ] SQL Audit files retained per policy (not auto-deleted)
- [ ] Application audit table (`AuditLogTable`) has retention job
- [ ] Archive process moves old logs to cold storage
- [ ] Archive integrity verified (checksums)
- [ ] Restore tested quarterly
- [ ] Legal hold process documented
```

---

## 5. Privilege Creep Detection

### 5.1 Role Assignment Drift Detection

```xpp
/// <summary>
/// Detect privilege creep by comparing role assignments over time
/// </summary>
static void DetectPrivilegeCreep(Args _args)
{
    // Requires baseline snapshot table: SecurityRoleAssignmentBaseline
    // Run monthly to create baseline, then compare
    
    SecurityRoleAssignmentBaseline baseline;
    SecurityRoleUser current;
    SecurityRole role;
    Map baselineRoles;
    Map currentRoles;
    List addedRoles;
    List removedRoles;
    ;
    
    // Get baseline (from last month)
    Date baselineDate = dateAdd(today(), -30);
    
    while select baseline
        where baseline.SnapshotDate == baselineDate
    {
        if (!baselineRoles.exists(baseline.UserId))
            baselineRoles.insert(baseline.UserId, new Set(Types::String));
        
        Set roles = baselineRoles.lookup(baseline.UserId);
        roles.add(baseline.RoleName);
    }
    
    // Get current assignments
    while select current
        join role
        where current.SecurityRole == role.RecId
           && current.User != "admin"
    {
        if (!currentRoles.exists(current.User))
            currentRoles.insert(current.User, new Set(Types::String));
        
        Set roles = currentRoles.lookup(current.User);
        roles.add(role.Name);
    }
    
    // Compare
    MapEnumerator enum = currentRoles.getEnumerator();
    while (enum.moveNext())
    {
        str userId = enum.currentKey();
        Set currentSet = enum.currentValue();
        Set baselineSet = baselineRoles.lookup(userId);
        
        if (baselineSet)
        {
            // Find added roles
            SetEnumerator currEnum = currentSet.getEnumerator();
            while (currEnum.moveNext())
            {
                if (!baselineSet.in(currEnum.current()))
                {
                    info(strFmt("PRIVILEGE CREEP: User %1 gained role %2", userId, currEnum.current()));
                    // Alert security team
                }
            }
            
            // Find removed roles (optional)
            SetEnumerator baseEnum = baselineSet.getEnumerator();
            while (baseEnum.moveNext())
            {
                if (!currentSet.in(baseEnum.current()))
                {
                    info(strFmt("ROLE REMOVED: User %1 lost role %2", userId, baseEnum.current()));
                }
            }
        }
        else
        {
            info(strFmt("NEW USER: %1 has roles: %2", userId, currentSet));
        }
    }
    
    // Check for users in baseline but not current (disabled?)
    enum = baselineRoles.getEnumerator();
    while (enum.moveNext())
    {
        if (!currentRoles.exists(enum.currentKey()))
        {
            info(strFmt("USER REMOVED: %1 no longer has roles (disabled?)", enum.currentKey()));
        }
    }
}
```

### 5.2 Monthly Privilege Creep Report

```markdown
# Monthly Privilege Creep Report - [Month Year]

## Summary
- Total users reviewed: [X]
- Users with added roles: [Y]
- Users with removed roles: [Z]
- New users: [A]
- Disabled users: [B]

## Added Roles (Require Approval)

| User | Role Added | Date Added | Added By | Business Justification | Approved |
|------|------------|------------|----------|------------------------|----------|
| john.doe | AP Approver | 2026-10-15 | jane.admin | Coverage for vacation | ☐ |

## Removed Roles

| User | Role Removed | Date Removed | Removed By | Reason |
|------|--------------|--------------|------------|--------|

## Actions Required
- [ ] Review all added roles with managers
- [ ] Update baseline snapshot
- [ ] Revoke unapproved roles
```

---

## 6. Emergency Access (Break-Glass) Review

### 6.1 Break-Glass Process

```markdown
# Emergency Access Procedure

## When to Use
- Critical production issue requiring sysadmin access
- Security incident investigation
- Emergency deployment outside change window

## Process
1. **Request:** User submits request via ITSM with justification
2. **Approval:** Security Manager + Business Owner approve
3. **Grant:** Time-limited role assignment (max 4 hours)
4. **Monitor:** All actions logged to dedicated audit trail
5. **Revoke:** Automatic removal after time expires
6. **Review:** Post-incident review within 24 hours

## Audit Checklist

| Check | Frequency | Pass/Fail |
|-------|-----------|-----------|
| Break-glass requests logged in ITSM | Per use | ☐ |
| Dual approval documented | Per use | ☐ |
| Time limit enforced (auto-revoke) | Per use | ☐ |
| Full audit trail captured | Per use | ☐ |
| Post-use review completed | Within 24h | ☐ |
| Unused emergency accounts disabled | Monthly | ☐ |
| Emergency account passwords rotated | Quarterly | ☐ |
```

### 6.2 Break-Glass Audit Query

```xpp
static void AuditBreakGlassAccess(Args _args)
{
    // Query break-glass log table
    BreakGlassLog log;
    Date fromDate = dateAdd(today(), -30);
    ;
    
    info("=== Break-Glass Access (Last 30 Days) ===");
    
    while select log
        where log.RequestedDateTime >= fromDate
        order by log.RequestedDateTime desc
    {
        info(strFmt("%1 | User: %2 | Role: %3 | Duration: %4 min | Approved By: %5 | Reviewed: %6",
            log.RequestedDateTime,
            log.UserId,
            log.RoleName,
            log.DurationMinutes,
            log.ApprovedBy,
            log.ReviewCompleted ? "Yes" : "NO ⚠️"));
        
        if (!log.ReviewCompleted)
        {
            warning(strFmt("PENDING REVIEW: %1 by %2", log.RecId, log.UserId));
        }
    }
}
```

---

## 7. Integration Security Audit

### 7.1 Service Principal Inventory

```markdown
# Service Principal / App Registration Audit

| App Name | Client ID | Permissions | Owner | Last Used | Expiry | Review Status |
|----------|-----------|-------------|-------|-----------|--------|---------------|
| D365-DMF-Import | xxx-xxx | DataManagement.ReadWrite | Integration Team | 2026-11-20 | 2027-01-15 | ☐ Current |
| PowerBI-Connector | xxx-xxx | OData.Read | BI Team | 2026-11-22 | 2027-06-01 | ☐ Current |
| LogicApps-OrderSync | xxx-xxx | CustomService.Execute | Integration Team | 2026-10-01 | 2026-12-01 | ⚠️ Expired Soon |
| Legacy-AIF-Adapter | xxx-xxx | Full Access | Unknown | 2025-06-15 | 2026-01-01 | ❌ Expired |

## Checklist

- [ ] All service principals have documented owners
- [ ] Permissions follow least privilege (no "Full Access")
- [ ] Certificate/secrets not expiring within 90 days
- [ ] Unused principals (>90 days) disabled
- [ ] Conditional access policies applied
- [ ] Audit logs captured for all integrations
```

### 7.2 OData/API Endpoint Security

```xpp
/// <summary>
/// Audit OData endpoint permissions
/// </summary>
static void AuditODataEndpoints(Args _args)
{
    // Check which entities are published and their permissions
    DMFEntity entity;
    ;
    
    info("=== Published OData Entities ===");
    
    while select entity
        where entity.IsPublic == NoYes::Yes
    {
        str permissions = "";
        
        // Check entity permissions
        if (entity.AllowRead) permissions += "R";
        if (entity.AllowWrite) permissions += "W";
        if (entity.AllowCreate) permissions += "C";
        if (entity.AllowDelete) permissions += "D";
        
        info(strFmt("%1 | Permissions: %2 | Company: %3",
            entity.Name, permissions, entity.Company));
        
        // Flag overly permissive
        if (permissions == "RWCD")
        {
            warning(strFmt("OVERLY PERMISSIVE: %1 has full CRUD", entity.Name));
        }
    }
}
```

---

## 8. Compliance Validation

### 8.1 GDPR Compliance Checklist

```markdown
# GDPR Compliance Audit (Article 30 Records of Processing)

## Data Inventory
- [ ] All personal data fields identified and documented
- [ ] Data flow maps created for each module
- [ ] Legal basis documented for each processing activity
- [ ] Retention periods defined and enforced

## Data Subject Rights
- [ ] Right to Access (Article 15) - export function tested
- [ ] Right to Rectification (Article 16) - update process documented
- [ ] Right to Erasure (Article 17) - anonymization process tested
- [ ] Right to Restriction (Article 18) - blocking mechanism works
- [ ] Right to Portability (Article 20) - export format standard
- [ ] Right to Object (Article 21) - suppression lists functional

## Technical Measures
- [ ] Encryption at rest (SQL TDE) enabled
- [ ] Encryption in transit (TLS 1.2+) enforced
- [ ] Pseudonymization used in non-prod environments
- [ ] Access controls (XDS) restrict PII access
- [ ] Audit logging captures all PII access
- [ ] Data breach detection and notification process tested

## Organizational Measures
- [ ] DPO appointed and contact published
- [ ] Staff training completed annually
- [ ] Vendor agreements include GDPR clauses
- [ ] DPIA completed for high-risk processing
```

### 8.2 SOX Compliance Checklist

```markdown
# SOX Compliance Audit (Key Financial Controls)

## Control Environment
- [ ] Segregation of duties enforced for financial processes
- [ ] Privileged access limited and monitored
- [ ] Change management process for financial systems

## Key Controls

| Control ID | Description | Test Procedure | Frequency | Status |
|------------|-------------|----------------|-----------|--------|
| SOX-01 | Journal entries require approval | Sample 25 journals, verify approver ≠ preparer | Quarterly | ☐ |
| SOX-02 | Vendor master changes dual-approved | Sample 10 changes, verify two approvers | Quarterly | ☐ |
| SOX-03 | Bank reconciliation completed timely | Verify all accounts reconciled within 5 days | Monthly | ☐ |
| SOX-04 | Access reviews completed | Verify quarterly access review sign-off | Quarterly | ☐ |
| SOX-05 | Number sequences not reset in prod | Attempt reset in prod (should fail) | Quarterly | ☐ |
| SOX-06 | Audit trail immutable | Attempt to delete audit log (should fail) | Quarterly | ☐ |
| SOX-07 | Financial reports match subledgers | Reconcile GL to AP/AR/INV subledgers | Monthly | ☐ |

## Evidence Retention
- [ ] Control test workpapers retained 7 years
- [ ] System-generated evidence (logs, reports) archived
- [ ] Exception tracking and resolution documented
```

---

## 9. Audit Execution Playbook

### 9.1 Pre-Audit Preparation

```markdown
# Pre-Audit Checklist (2 Weeks Before)

## Data Collection
- [ ] Export role/privilege matrix (SecurityRoleAssignmentBaseline)
- [ ] Export XDS policy definitions
- [ ] Export audit log samples (last 90 days)
- [ ] Export service principal inventory
- [ ] Export SoD conflict baseline
- [ ] Collect RSAT test results for critical paths

## Stakeholder Notification
- [ ] Security Admin notified
- [ ] Business process owners notified
- [ ] Internal Audit team aligned
- [ ] External auditor (if applicable) scoped

## Tool Preparation
- [ ] Audit scripts tested in UAT
- [ ] Reporting templates prepared
- [ ] Evidence repository accessible
```

### 9.2 Audit Execution (1 Week)

```markdown
# Audit Execution Schedule

## Day 1: Role & Privilege Review
- Run role inventory script
- Review against least privilege
- Document findings

## Day 2: SoD Analysis
- Run SoD detection script
- Review conflicts with business owners
- Document compensating controls

## Day 3: XDS Policy Audit
- Inventory all policies
- Test coverage on sensitive tables
- Verify policy logic

## Day 4: Audit Log Integrity
- Verify SQL Audit running
- Check application audit completeness
- Validate retention compliance

## Day 5: Integration & Emergency Access
- Review service principals
- Audit break-glass usage
- Check OData permissions

## Day 6: Compliance Validation
- GDPR checklist
- SOX control testing
- Document gaps

## Day 7: Reporting
- Compile findings
- Risk-rate each finding
- Draft remediation plan
- Present to stakeholders
```

### 9.3 Finding Risk Rating

```markdown
# Finding Risk Rating Matrix

| Rating | Criteria | Remediation Timeline |
|--------|----------|---------------------|
| **Critical** | Direct financial fraud risk, data breach, regulatory violation | 30 days |
| **High** | SoD conflict without compensating control, excessive privileges | 60 days |
| **Medium** | Missing audit coverage, privilege creep, expired certificates | 90 days |
| **Low** | Documentation gaps, naming inconsistencies, minor config | 180 days |
| **Info** | Best practice improvements, optimization opportunities | Next release |

## Finding Template

**Finding ID:** SEC-2026-001
**Rating:** Critical
**Area:** SoD Conflict
**Description:** User john.doe assigned both AP Clerk and AP Approver roles
**Risk:** Ability to create and approve fraudulent payments
**Evidence:** SoD detection script output dated 2026-11-22
**Compensating Control:** None documented
**Recommendation:** Remove AP Approver role; assign to separate user
**Owner:** Security Admin
**Due Date:** 2026-12-22
**Status:** Open
```

---

## 10. Microsoft Resources

- **Security Configuration**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/security-configuration
- **Audit Policy**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/auditing
- **SoD Management**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/segregation-of-duties
- **GDPR**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lcs-solutions/gdpr-compliance
- **Security Best Practices**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/security-best-practices

---

## 11. Quick Reference Commands

```bash
# Run all audit scripts (in X++)
# DetectSoDConflicts
# AuditXDSPolicies
# VerifyAuditLogs
# DetectPrivilegeCreep
# AuditBreakGlassAccess
# AuditODataEndpoints

# Export role matrix
# ExportCustomRoles

# SQL Audit verification
# SELECT * FROM sys.fn_get_audit_file(...)

# Baseline snapshot (monthly)
# INSERT INTO SecurityRoleAssignmentBaseline SELECT ... FROM SecurityRoleUser JOIN SecurityRole ...
```

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*