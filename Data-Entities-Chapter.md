# Chapter: Data Entities — Integration & Data Management in D365 F&O

> **Complete reference for building, deploying, and consuming Data Entities in Dynamics 365 Finance & Operations.**
> Covers entity types, design patterns, staging, OData/REST, Power Platform integration, and a production-ready capstone activity.

---

## Table of Contents

1. [Entity Types: DataEntity vs Composite Entity vs Derived View](#1-entity-types-dataentity-vs-composite-entity-vs-derived-view)
2. [Entity Design: IsPublic, Public Names, and Staging Tables](#2-entity-design-ispublic-public-names-and-staging-tables)
3. [The Staging Pattern: Design, Process, and PostProcess](#3-the-staging-pattern-design-process-and-postprocess)
4. [Entity Mapping: Auto-Mapping vs Manual Field Mapping](#4-entity-mapping-auto-mapping-vs-manual-field-mapping)
5. [Data Management Workspace: Import/Export and Package Deployment](#5-data-management-workspace-importexport-and-package-deployment)
6. [REST/OData: DictClass Reflection, Entity Publishing, HttpClient Consumption](#6-restoData-dictclass-reflection-entity-publishing-httpclient-consumption)
7. [Power Platform Integration: Logic Apps and Power Automate](#7-power-platform-integration-logic-apps-and-power-automate)
8. [Capstone Activity: Build an HR Employee Data Integration Entity](#8-capstone-activity-build-an-hr-employee-data-integration-entity)
9. [Definitions: Key Terms with Layman Explanations](#9-definitions-key-terms-with-layman-explanations)
10. [Comparison Tables](#10-comparison-tables)
11. [Microsoft Learn References](#11-microsoft-learn-references)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)

---

## 1. Entity Types: DataEntity vs Composite Entity vs Derived View

D365 F&O provides three distinct patterns for exposing data for integration and reporting. Choosing the right pattern is critical for performance, maintainability, and upgradeability.

### 1.1 DataEntity — The Standard Integration Pattern

A **DataEntity** is the primary and recommended pattern for data integration in D365 F&O. It is a read-optimized view that joins multiple tables and exposes the data through the OData/REST service layer.

| **Layman Definition** | A DataEntity is like a "smart view" that pulls data from multiple tables, packages it neatly, and makes it available through a standard web API (OData) so external systems can read it easily. |
|---|---|

**When to use a DataEntity:**

| Scenario | Use DataEntity? |
|---|---|
| Exposing data to Power Automate / Logic Apps | ✅ Yes |
| Pushing data to an external ERP or SaaS system | ✅ Yes |
| Consuming D365 F&O data from a custom .NET application | ✅ Yes |
| Building a report that joins multiple standard tables | ✅ Yes |
| Simple single-table read operation | ✅ Yes (works, though slightly over-engineered) |
| Write-back to D365 F&O | ❌ No — use a Data Entity with the **staging pattern** instead |

**Key Characteristics:**
- Read-only by default (for write-back, use the staging pattern)
- Exposed via OData/REST automatically when published
- Supports filtering, sorting, and pagination natively
- Can include computed/display fields (e.g., `FullName = FirstName + ' ' + LastName`)
- Uses `IsPublic`, `Public Entity Name`, and `Public Collection Name` properties for OData exposure
- Staging fields stored in a separate auto-generated staging table

**Under the hood:**
```xpp
// A DataEntity is implemented as a SQL view in the database
// Example: VendAPComplianceEntity becomes a view in SQL Server
// The framework also auto-generates a staging table: VendAPComplianceStaging
```

### 1.2 Composite Entity — For Complex Multi-Source Integration

A **Composite Entity** combines data from **multiple Data Entities** into a single integration endpoint. Use it when a single DataEntity isn't sufficient because data comes from different sources or requires complex joining logic that DataEntities can't express.

| **Layman Definition** | A Composite Entity is like a "meta-entity" — it stitches together several DataEntities into one big endpoint. Think of it as a playlist that combines songs from different albums into one continuous stream. |
|---|---|

**When to use a Composite Entity:**

| Scenario | Use Composite Entity? |
|---|---|
| Combining data from two unrelated tables into one endpoint | ✅ Yes |
| Building a master data export that spans multiple modules (e.g., Finance + HR + SCM) | ✅ Yes |
| Creating a single integration point for a partner who needs "everything about vendors" | ✅ Yes |
| Simple single-table read | ❌ No — use a DataEntity |
| Read-only reporting on a single table | ❌ No — use a DataEntity |
| Need to write back to D365 F&O | ❌ No — use DataEntity with staging pattern |

**Important Limitation:**
> **Composite entities have no X++ programmatic interface.** You cannot programmatically create, modify, or query composite entities from X++ code. They are only supported from the Data Management platform (UI-driven).

### 1.3 Derived View — For Complex SQL Logic

A **Derived View** is a low-level pattern that creates a view in the AOT with custom SQL logic. It's the most flexible but least integrated pattern — it doesn't automatically expose via OData and requires manual configuration for service layer exposure.

| **Layman Definition** | A Derived View is like writing raw SQL for a view. You get total control over the query, but you lose all the automatic integration features (OData, staging, mapping). It's the "escape hatch" when the framework can't express what you need. |
|---|---|

**When to use a Derived View:**

| Scenario | Use Derived View? |
|---|---|
| Complex SQL that can't be expressed with DataEntity (e.g., window functions, CTEs, custom UDFs) | ✅ Yes |
| Need to call custom SQL functions or stored procedures | ✅ Yes |
| Need to expose via OData/REST | ❌ No — use DataEntity (it supports OData natively) |
| Simple read operation | ❌ No — use DataEntity |
| Write-back scenarios | ❌ No — use DataEntity with staging |

### 1.4 Decision Matrix

| Feature | DataEntity | Composite Entity | Derived View |
|---|---|---|---|
| **OData/REST exposure** | ✅ Automatic | ✅ Automatic | ❌ Manual |
| **Read-only** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Write-back** | ✅ With staging pattern | ✅ With staging pattern | ❌ Manual |
| **Multi-table joins** | ✅ Via data sources | ✅ Combines multiple entities | ✅ Custom SQL |
| **Filtering/Pagination** | ✅ Built-in | ✅ Built-in | ❌ Manual |
| **Complex SQL logic** | ❌ Limited | ❌ Limited | ✅ Full control |
| **Upgrade safety** | ✅ High | ✅ High | ⚠️ Medium |
| **Ease of use** | ✅ Easy | ⚠️ Moderate | ❌ Complex |
| **X++ programmatic access** | ✅ Full | ❌ None | ✅ Full |

### 1.5 Important Considerations

| Consideration | Guidance |
|---|---|
| **Data entities are SQL views** | Entities are created as views in Microsoft SQL Server. Understand SQL implications: indexed views, indexed columns, and view performance characteristics affect query performance. |
| **Data entities don't support XDS** | Data entities don't support Extensible Data Security (XDS). XDS policies apply to tables, not data entities. If you need row-level security on entity data, apply XDS to the underlying tables instead. |
| **Composite entities — no X++ interface** | Composite entities are only supported from Data Management platform. No programmatic interface for composite entities exists in X++. |
| **XDS on backing entities** | XDS policies on backing entities (Customers, Vendors, Operating units) can affect visibility of entity-backed dimension values. If a user's role is restricted by XDS on the backing entity, corresponding dimension values may appear blank or missing. |

---

## 2. Entity Design: IsPublic, Public Names, and Staging Tables

### 2.1 OData Exposure and Staging Mechanisms

Every DataEntity controls OData exposure and staging via these mechanisms:

| Mechanism | Purpose | OData Exposure | Example |
|---|---|---|---|
| **IsPublic, Public Entity Name, Public Collection Name** | Controls whether the entity is exposed via OData and its endpoint names | ✅ Visible in OData when `IsPublic = Yes` | `VendAPComplianceEntity` with `Public Collection Name = VendAPComplianceEntities` |
| **Staging Table** | Auto-generated table (e.g., `EntityNameStaging`) for intermediate processing | ❌ Hidden from OData | `VendAPComplianceStaging` with fields like `StagingStatus`, `ProcessingFlag`, `InternalRef` |
| **Link** | Connects the entity to its context (parent record) | ✅ Visible in OData | `VendTableRecId` linking to the vendor |

### 2.2 Entity Design Pattern — Visual Breakdown

```
DataEntity: VendAPComplianceEntity
├── OData-exposed fields (IsPublic = Yes, Public Collection Name = VendAPComplianceEntities)
│   ├── AccountNum (string 20) — from VendTable
│   ├── Name (string 60) — from VendTable
│   ├── ComplianceCode (string 20) — from APCustomsDeclaration
│   ├── DeclDate (date) — from APCustomsDeclaration
│   └── Status (string 20) — computed/display field
│
├── Staging table (VendAPComplianceStaging) for intermediate processing
│   ├── VendTableRecId (int64) — for internal mapping
│   ├── StagingStatus (enum) — processing state
│   └── ErrorMessage (string 250) — error tracking
│
└── Link (connects entity to parent context)
    └── VendTableRecId → VendTable.RecId
```

### 2.3 The `Link` Property — Deep Dive

The `Link` property on a DataEntity field specifies the relationship between the entity and its underlying table. Critical for:

1. **Context filtering** — the framework uses the link to filter data based on the calling context
2. **Write-back operations** — when pushing data back to D365 F&O, the link identifies which record to update
3. **OData `$expand`** — linked entities can be expanded in OData queries

```xpp
// In the Data Entity designer:
// Link field: VendTableRecId
// Linked to: VendTable.RecId

// This allows OData consumers to filter by vendor:
// GET /data/VendAPComplianceEntity?$filter=VendTableRecId eq 12345
//
// Or expand the related vendor:
// GET /data/VendAPComplianceEntity?$expand=VendTable
```

### 2.4 Entity Properties Checklist

When creating a new DataEntity, configure these properties:

| Property | Recommended Value | Purpose |
|---|---|---|
| **IsPublic** | `Yes` | Enables OData exposure |
| **Public Entity Name** | Singular (e.g., `HRPersonnelEntity`) | OData entity set name |
| **Public Collection Name** | Plural (e.g., `HRPersonnelEntities`) | OData collection endpoint name |
| **Primary Key** | Set to unique identifying field(s) | Required for OData key navigation |
| **Enable Staging** | `Yes` (for write-back entities) | Auto-generates staging table |
| **Staging Table Name** | Auto (default) or custom | Name of staging table |

### 2.5 Computed/Display Fields

Fields that don't exist in the database but are calculated at runtime:

```xpp
// In the Data Entity, add a display method:
[DataMemberAttribute('FullName'), SysOperationLabelAttribute('Full Name')]
public str FullName()
{
    return strFmt('%1 %2', this.FirstName, this.LastName);
}

// Or use a computed column for better query performance:
// In the entity's query, add a computed column:
// FullName = FirstName + ' ' + LastName
```

---

## 3. The Staging Pattern: Design, Process, and PostProcess

The **staging pattern** is the standard approach for data entities that need to write data back to D365 F&O. It uses a three-step process:

1. **Staging** — data is first loaded into a staging table
2. **Processing** — the staging data is validated and transformed
3. **Post-processing** — the validated data is written to the target table

### 3.1 Why Staging?

| Problem | How Staging Solves It |
|---|---|
| Invalid data can't be written directly to target tables | Validation happens in staging before target write |
| Partial failures need rollback | Staging allows all-or-nothing transaction control |
| Error logging and audit trail needed | Errors captured in staging table with context |
| Deduplication needed | Staging table can check for duplicates before insert |
| Import history needed | Staging records capture batch ID and timestamp |

### 3.2 Staging Table Design — Complete Example

```xpp
/// <summary>
/// Staging table for APCustomsDeclaration entity.
/// Uses TempDB storage — data is temporary and doesn't persist across sessions.
/// </summary>
table 50100 APCustomsDeclarationStaging
{
    DataClassification = CustomerContent;
    Storage = TempDB;  // Temporary storage — cleared on session end

    fields
    {
        field(1; RecId; int64) { }
        field(2; DeclId; Code[35]) { }
        field(3; VendTableRecId; int64) { }
        field(4; DeclDate; Date) { }
        field(5; CustomsRef; Code[50]) { }
        field(6; InvoiceLineRecId; int64) { }
        field(7; StagingStatus; Enum APCustomsStagingStatus) { }
        field(8; ErrorMessage; Text[250]) { }
        field(9; ImportBatchId; Guid) { }
        field(10; CreatedDateTime; DateTime) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_DeclId; DeclId) { }
    }
}

/// <summary>
/// Staging status enumeration.
/// </summary>
enum APCustomsStagingStatus
{
    Ready = 0,        // Record is ready for processing
    Processing = 1,   // Currently being processed
    Processed = 2,    // Successfully written to target
    Failed = 3,       // Validation or write error
    Duplicate = 4,    // Duplicate detected
    BatchFailed = 5   // Batch-level failure (rollback threshold exceeded)
}
```

### 3.3 The `process()` Method — Core Implementation

The `process()` method is the core of the staging pattern. It reads records from the staging table, validates them, and writes them to the target table.

```xpp
/// <summary>
/// Handler class for APCustomsDeclaration entity staging processing.
/// Called by the Data Entity framework during import operations.
/// </summary>
class APCustomsDeclarationEntityHandler
{
    /// <summary>
    /// Process staging records and write to target table.
    /// </summary>
    public void process()
    {
        APCustomsDeclarationStaging staging;
        APCustomsDeclaration target;

        // Process all records marked as Ready
        while select staging
            where staging.StagingStatus == APCustomsStagingStatus::Ready
        {
            try
            {
                ttsbegin;

                // Step 1: Validate the staging record
                if (!this.validateStagingRecord(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Failed;
                    staging.ErrorMessage = 'Validation failed: missing required fields';
                    staging.update();
                    ttscommit;
                    continue;
                }

                // Step 2: Check for duplicates
                if (this.isDuplicate(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Duplicate;
                    staging.ErrorMessage = 'Duplicate declaration ID found in target';
                    staging.update();
                    ttscommit;
                    continue;
                }

                // Step 3: Write to target table
                target.initValue();
                target.DeclId = staging.DeclId;
                target.VendTableRecId = staging.VendTableRecId;
                target.DeclDate = staging.DeclDate;
                target.CustomsRef = staging.CustomsRef;
                target.InvoiceLineRecId = staging.InvoiceLineRecId;
                target.insert();

                // Step 4: Mark staging as processed
                staging.StagingStatus = APCustomsStagingStatus::Processed;
                staging.update();

                ttscommit;
            }
            catch (Exception::Error)
            {
                ttsabort;
                staging.StagingStatus = APCustomsStagingStatus::Failed;
                staging.ErrorMessage = 'Unexpected error during processing';
                staging.update();
            }
        }
    }

    /// <summary>
    /// Validates required fields on the staging record.
    /// </summary>
    private boolean validateStagingRecord(APCustomsDeclarationStaging _staging)
    {
        if (_staging.DeclId == '')
        {
            return false;
        }
        if (_staging.VendTableRecId == 0)
        {
            return false;
        }
        if (_staging.DeclDate == dateNull())
        {
            return false;
        }
        return true;
    }

    /// <summary>
    /// Checks if a declaration with the same DeclId already exists.
    /// </summary>
    private boolean isDuplicate(APCustomsDeclarationStaging _staging)
    {
        APCustomsDeclaration existing;
        return exists select firstonly existing
            where existing.DeclId == _staging.DeclId;
    }
}
```

### 3.4 The `postProcess()` Method — Completion Logic

The `postProcess()` method runs after all staging records have been processed. Used for:

- Sending notifications (email, Infolog messages)
- Logging summary statistics
- Triggering downstream processes
- Cleaning up staging records

```xpp
/// <summary>
/// Post-processing logic: summary, notifications, cleanup.
/// </summary>
public void postProcess()
{
    int processedCount;
    int failedCount;
    int duplicateCount;
    Guid batchId;

    // Get batch ID from context (could be stored in a temp table or config)
    batchId = this.getCurrentBatchId();

    // Count results
    processedCount = select count(StagingStatus)
        from APCustomsDeclarationStaging
        where StagingStatus == APCustomsStagingStatus::Processed
           && ImportBatchId == batchId;

    failedCount = select count(StagingStatus)
        from APCustomsDeclarationStaging
        where StagingStatus == APCustomsStagingStatus::Failed
           && ImportBatchId == batchId;

    duplicateCount = select count(StagingStatus)
        from APCustomsDeclarationStaging
        where StagingStatus == APCustomsStagingStatus::Duplicate
           && ImportBatchId == batchId;

    // Log summary to Infolog
    info(strFmt('Import batch %1 complete: %2 succeeded, %3 failed, %4 duplicates.',
        batchId, processedCount, failedCount, duplicateCount));

    // Optional: send email notification for failed records
    if (failedCount > 0 || duplicateCount > 0)
    {
        this.sendFailureNotification(batchId, failedCount, duplicateCount);
    }

    // Optional: clean up processed staging records (if using permanent table)
    // this.cleanupStagingRecords(batchId);
}

/// <summary>
/// Sends email notification via SMTP (requires SMTP configuration in D365).
/// </summary>
private void sendFailureNotification(Guid _batchId, int _failedCount, int _duplicateCount)
{
    str subject = strFmt('Data Import Failed: Batch %1', _batchId);
    str body = strFmt(
        'The data import batch %1 completed with errors.\n\n' +
        'Failed records: %2\n' +
        'Duplicate records: %3\n\n' +
        'Please review the Data Management workspace for details.',
        _batchId, _failedCount, _duplicateCount);

    try
    {
        // Requires: System Administration > Email parameters configured
        SmtpMail::send(
            'd365-alerts@company.com',
            'integration-team@company.com',
            subject,
            body);
    }
    catch (Exception::Error)
    {
        // Log but don't fail the batch
        warning('Failed to send notification email');
    }
}
```

### 3.5 Advanced: Rollback Threshold Pattern

Abort the entire batch if failure rate exceeds a threshold (e.g., 10%):

```xpp
public void process()
{
    APCustomsDeclarationStaging staging;
    int totalToProcess;
    int processedCount = 0;
    int failedCount = 0;

    // Count total records upfront
    totalToProcess = select count(RecId) from staging
        where staging.StagingStatus == APCustomsStagingStatus::Ready;

    while select staging
        where staging.StagingStatus == APCustomsStagingStatus::Ready
    {
        processedCount++;
        
        try
        {
            ttsbegin;
            
            // ... validation and processing logic ...
            
            // Check rollback threshold AFTER each record
            if (failedCount > 0 && (failedCount * 100 / processedCount) > 10)
            {
                // Mark all remaining Ready records as BatchFailed
                update_recordset staging
                    setting StagingStatus = APCustomsStagingStatus::BatchFailed,
                        ErrorMessage = 'Rollback threshold exceeded: >10% failure rate'
                    where staging.StagingStatus == APCustomsStagingStatus::Ready;
                
                ttscommit;
                
                throw error(strFmt('Rollback threshold exceeded at record %1 of %2. Batch aborted.', 
                    processedCount, totalToProcess));
            }
            
            ttscommit;
        }
        catch (Exception::Error)
        {
            ttsabort;
            failedCount++;
            // ... error handling ...
        }
    }
}
```

---

## 4. Entity Mapping: Auto-Mapping vs Manual Field Mapping

### 4.1 Auto-Mapping

Auto-mapping is the default behavior when a DataEntity field has the **same name and compatible type** as the underlying table field. The framework automatically maps the entity field to the table field.

**When auto-mapping works:**
- Field names match exactly (case-sensitive)
- Field types are compatible (string ↔ string, int ↔ int, date ↔ date)
- No transformation is needed

**When auto-mapping fails:**
- Field names don't match (e.g., entity field `DeclId` maps to table field `DeclarationId`)
- Field types are incompatible (e.g., entity field is `string` but table field is `int`)
- Transformation is needed (e.g., concatenating `FirstName + ' ' + LastName` into `FullName`)

### 4.2 Manual Field Mapping

When auto-mapping doesn't work, define manual field mappings in the Data Entity designer:

| Entity Field | Maps to Table Field(s) | Mapping Type | Transformation |
|---|---|---|---|
| `DeclId` (string 35) | `DeclarationId` (string 35) | Manual | None (names differ) |
| `FullName` (string 120) | `FirstName` + `' '` + `LastName` | Manual | Concatenation expression |
| `StatusDescription` (string 60) | `Status` (enum) | Manual | Enum-to-string lookup |
| `VendAccountNum` (string 20) | `VendTable.AccountNum` | Manual | Cross-table reference |

### 4.3 Mapping in the Data Entity Designer (Visual Studio)

In Visual Studio, the Data Entity designer provides a **Mappings** node where you can:

1. **Auto Map** — click "Auto Map" to let the framework attempt automatic matching
2. **Manual Map** — drag and drop entity fields to table fields
3. **Transform** — define expressions for field transformations
4. **Skip** — exclude fields from mapping (they exist in entity but aren't mapped to table)

### 4.4 Computed Columns vs Display Methods

| Approach | Use Case | Performance | OData Support |
|---|---|---|---|
| **Computed Column** (SQL-level) | Simple expressions, filtering needed | ✅ Best — computed in SQL | ✅ Full |
| **Display Method** (X++ method) | Complex logic, requires X++ code | ⚠️ Slower — evaluated per row | ✅ Full |
| **Unmapped Field** (staging only) | Internal processing only | N/A | ❌ Hidden |

**Computed Column Example (in entity query):**
```xpp
// In the Data Entity's query, add a computed column:
// Field: FullName
// Expression: DirPerson.FirstName + ' ' + DirPerson.LastName
// This becomes part of the SQL view definition
```

**Display Method Example (in entity class):**
```xpp
[DataMemberAttribute('FullName'), SysOperationLabelAttribute('Full Name')]
public str FullName()
{
    DirPerson person;
    select firstonly person where person.RecId == this.PersonRecId;
    return strFmt('%1 %2', person.FirstName, person.LastName);
}
```

### 4.5 Best Practices for Entity Mapping

1. **Use consistent naming** — entity field names should match table field names to enable auto-mapping
2. **Use staging tables for staging fields** — staging fields should never be exposed in OData
3. **Document manual mappings** — add comments explaining why auto-mapping wasn't possible
4. **Test mappings with sample data** — always verify data flows correctly from entity to table
5. **Prefer computed columns over display methods** for simple transformations (better query performance)

---

## 5. Data Management Workspace: Import/Export and Package Deployment

The **Data Management** workspace is the central hub for importing and exporting data in D365 F&O. It provides a UI-driven interface for data operations without requiring code.

### 5.1 Import Operations

| Operation | Description | Use Case |
|---|---|---|
| **Import** | Load data from an Excel/CSV file into D365 F&O tables | Bulk data loading, initial setup |
| **Import from Entity** | Load data using a Data Entity definition | Integration scenarios, staging pattern |
| **Import Group** | Execute a group of import projects in sequence | Complex multi-table imports |

### 5.2 Export Operations

| Operation | Description | Use Case |
|---|---|---|
| **Export** | Export data from D365 F&O tables to Excel/CSV | Reporting, data extraction |
| **Export to Entity** | Export data using a Data Entity definition | Integration with external systems |
| **Export to Data Entity** | Export using the staging pattern for write-back scenarios | Data synchronization |

### 5.3 Package Deployment

A **package** is a deployable unit that contains one or more Data Entities, mapping configurations, and import/export settings.

```
[1] Create a package in the source environment
    │  - Define the Data Entities to include
    │  - Configure mapping and transformation rules
    │  - Set up import/export settings
    │
[2] Export the package as an .axdp file
    │
[3] Upload the package to LCS
    │  - LCS stores the package as a build artifact
    │
[4] Deploy the package to the target environment
    │  - LCS copies the package to the target environment's model store
    │  - The Data Management workspace on the target detects the package
    │
[5] Execute the package in the target environment
    │  - Run the import/export operation
    │  - Monitor progress and review results
    │
[6] Verify the data in the target environment
    │  - Check the Data Management workspace for execution status
    │  - Review any error logs
```

### 5.4 Package Deployment via PowerShell (Automation)

```powershell
# Deploy a Data Management package via LCS API
# Requires: LCS API access token, project ID, environment ID

$lcsApiUrl = "https://lcs.dynamics.com/UpdateCloudAsset/UploadPackage"
$packagePath = "C:\Packages\HRIntegrationPackage.axdp"
$projectId = "123456"
$environmentId = "789012"

# Upload package to LCS
$uploadResponse = Invoke-RestMethod -Uri $lcsApiUrl -Method Post `
    -Headers @{Authorization = "Bearer $accessToken"} `
    -Form @{File = Get-Item $packagePath}

# Deploy to environment
$deployUrl = "https://lcs.dynamics.com/DeployPackage/$projectId/$environmentId"
Invoke-RestMethod -Uri $deployUrl -Method Post `
    -Headers @{Authorization = "Bearer $accessToken"} `
    -Body (@{packageId = $uploadResponse.packageId} | ConvertTo-Json)
```

### 5.5 Recurring Data Jobs

Configure recurring imports/exports using **Data Management > Recurring Data Jobs**:

| Setting | Description |
|---|---|
| **Recurrence** | Daily, Weekly, Monthly, or Custom cron expression |
| **Time Zone** | Execution time zone |
| **File Location** | Azure Blob Storage, SharePoint, or Local file |
| **Processing Options** | Skip errors, stop on error, or continue on error |
| **Notification** | Email on success/failure |

---

## 6. REST/OData: DictClass Reflection, Entity Publishing, HttpClient Consumption

### 6.1 Exposing Data via OData

D365 F&O automatically exposes Data Entities as OData endpoints when they are published.

**OData endpoint URL format:**
```
https://<your-environment>.dynamics.com/data/<EntityName>
```

**Example:**
```
https://usnconeboxax1aos.cloud.onebox.dynamics.com/data/VendAPComplianceEntity
```

### 6.2 Publishing an Entity via `IsPublic`

A Data Entity is published for OData exposure by setting the **`IsPublic`** property to **Yes** in the entity designer. No code registration is needed — the framework automatically generates the OData endpoint and the staging table when the entity is built and deployed.

| Property | Value | Effect |
|---|---|---|
| `IsPublic` | `Yes` | Entity appears in OData service document |
| `Public Entity Name` | `HRPersonnelEntity` | Single entity endpoint: `/data/HRPersonnelEntity` |
| `Public Collection Name` | `HRPersonnelEntities` | Collection endpoint: `/data/HRPersonnelEntities` |

### 6.3 OData Query Options

D365 F&O OData endpoints support standard OData query options:

| Option | Example | Description |
|---|---|---|
| `$filter` | `$filter=CreditMax gt 500000` | Filter records by condition |
| `$select` | `$select=AccountNum,Name` | Select specific fields only |
| `$orderby` | `$orderby=AccountNum asc` | Sort results |
| `$top` | `$top=100` | Limit to first N records |
| `$skip` | `$skip=50` | Skip first N records (pagination) |
| `$expand` | `$expand=VendInvoiceJour` | Include related entities |
| `$count` | `$count=true` | Include total record count |
| `$apply` | `$apply=groupby((Status), aggregate(Count as Total))` | Aggregation (limited support) |

### 6.4 `DictClass` — Runtime Entity Metadata

The `DictClass` and `DictMethod` classes provide runtime reflection over X++ objects, including Data Entities. Useful for dynamic entity discovery and metadata-driven integrations.

```xpp
/// <summary>
/// Inspect a Data Entity's metadata at runtime.
/// </summary>
class EntityMetadataInspector
{
    public static void inspectEntity(str _entityName)
    {
        DictClass dictClass;
        DictMethod dictMethod;
        int i;
        SysDictMethod sysDictMethod;

        // Get the entity class by name
        dictClass = new DictClass(className2Id(_entityName));
        
        if (!dictClass)
        {
            error(strFmt('Entity class %1 not found', _entityName));
            return;
        }

        info(strFmt('=== Entity Metadata: %1 ===', _entityName));
        info(strFmt('Class ID: %1', dictClass.classId()));
        info(strFmt('Base Class: %1', dictClass.baseClass()));
        info(strFmt('Is Abstract: %1', dictClass.isAbstract()));
        info(strFmt('Is Final: %1', dictClass.isFinal()));

        // List all methods
        info('--- Methods ---');
        for (i = 1; i <= dictClass.methods(); i++)
        {
            dictMethod = dictClass.methodObject(i);
            info(strFmt('  %1 : returns %2', 
                dictMethod.name(), 
                dictMethod.clrReturnType()));
        }

        // Inspect a specific method
        if (dictClass.hasMethod(methodStr(VendAPComplianceEntity, process)))
        {
            dictMethod = new DictMethod(
                dictClass.classId(), 
                methodStr(VendAPComplianceEntity, process));
            
            info(strFmt('\nProcess method details:'));
            info(strFmt('  Return type: %1', dictMethod.clrReturnType()));
            info(strFmt('  Is Static: %1', dictMethod.isStatic()));
            info(strFmt('  Is Final: %1', dictMethod.isFinal()));
            info(strFmt('  Parameter count: %1', dictMethod.parameterCount()));
        }
    }
}
```

**Practical Use Case: Dynamic Entity Discovery**
```xpp
/// <summary>
/// Dynamically discover all published Data Entities.
/// </summary>
public static void listAllPublishedEntities()
{
    DictClass dictClass;
    TreeNode treeNode;
    TreeNodeIterator iterator;
    #AOT
    
    // Iterate all Data Entity nodes in AOT
    treeNode = TreeNode::findNode(#DataEntitiesPath);
    iterator = treeNode.AOTiterator();
    treeNode = iterator.next();
    
    while (treeNode)
    {
        // Check if entity is public (IsPublic = Yes)
        // This requires reading the entity's properties
        // Typically done via metadata API in modern versions
        info(treeNode.treeNodeName());
        treeNode = iterator.next();
    }
}
```

### 6.5 Consuming OData Endpoints via `HttpClient`

D365 F&O provides the `HttpClient` class (from `System.Net.Http`) for consuming external OData endpoints from X++ code.

```xpp
using System.Net.Http;
using System.Net.Http.Headers;

/// <summary>
/// Consumes external OData endpoints from X++.
/// </summary>
class ExternalODataConsumer
{
    /// <summary>
    /// Calls an external OData endpoint and processes the response.
    /// </summary>
    public static void consumeVendorOData()
    {
        HttpClient httpClient;
        HttpRequestMessage request;
        HttpResponseMessage response;
        string responseBody;
        string odataUrl;
        string accessToken;

        odataUrl = 'https://external-system.com/api/v1/Vendors';
        
        // Get access token (from Azure AD, Key Vault, or config)
        accessToken = ExternalAuthHelper::getAccessToken();

        try
        {
            // Create HTTP client
            httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add('Accept', 'application/json');
            
            // Add authorization header
            httpClient.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue('Bearer', accessToken);

            // Send GET request
            response = httpClient.GetAsync(odataUrl).GetAwaiter().GetResult();

            if (response.IsSuccessStatusCode)
            {
                responseBody = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
                
                // Parse JSON and process
                // Use Newtonsoft.Json or System.Text.Json via CLR interop
                this.processVendorResponse(responseBody);
            }
            else
            {
                error(strFmt('HTTP request failed: %1 - %2', 
                    response.StatusCode, response.ReasonPhrase));
            }
        }
        catch (Exception::CLRError)
        {
            error('CLR error calling external OData endpoint');
        }
    }

    private void processVendorResponse(str _json)
    {
        // Parse JSON using CLR interop
        // Example using Newtonsoft.Json:
        /*
        var jObject = Newtonsoft.Json.Linq.JObject.Parse(_json);
        var vendors = jObject["value"] as Newtonsoft.Json.Linq.JArray;
        
        foreach (var vendor in vendors)
        {
            string accountNum = vendor["AccountNum"].ToString();
            string name = vendor["Name"].ToString();
            // Create/update in D365 via staging entity
        }
        */
    }
}
```

### 6.6 Consuming D365 F&O OData from External Systems

**C# Example (External .NET Application):**
```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

public class D365ODataClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public D365ODataClient(string baseUrl, string accessToken)
    {
        _baseUrl = baseUrl.TrimEnd('/') + "/data/";
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", accessToken);
        _httpClient.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));
    }

    public async Task<JObject> GetEntitiesAsync(string entityName, string filter = null, int top = 100)
    {
        var url = $"{_baseUrl}{entityName}";
        if (!string.IsNullOrEmpty(filter))
            url += $"?$filter={Uri.EscapeDataString(filter)}";
        if (top > 0)
            url += (url.Contains("?") ? "&" : "?") + $"$top={top}";

        var response = await _httpClient.GetAsync(url);
        response.EnsureSuccessStatusCode();
        
        var json = await response.Content.ReadAsStringAsync();
        return JObject.Parse(json);
    }

    public async Task<JObject> CreateEntityAsync(string entityName, JObject entityData)
    {
        var url = $"{_baseUrl}{entityName}";
        var content = new StringContent(entityData.ToString(), System.Text.Encoding.UTF8, "application/json");
        
        var response = await _httpClient.PostAsync(url, content);
        response.EnsureSuccessStatusCode();
        
        var json = await response.Content.ReadAsStringAsync();
        return JObject.Parse(json);
    }
}
```

---

## 7. Power Platform Integration: Logic Apps and Power Automate

### 7.1 Logic Apps Connector for D365 F&O

Microsoft provides a **Dynamics 365 Finance & Operations** connector in Azure Logic Apps that simplifies integration without writing code.

**Common Logic Apps Operations:**

| Operation | Description |
|---|---|
| **List records** | Query a Data Entity and return matching records (supports `$filter`, `$top`, `$skip`) |
| **Get record** | Retrieve a single record by key |
| **Create record** | Insert a new record into a Data Entity (uses staging pattern automatically) |
| **Update record** | Modify an existing record |
| **Delete record** | Remove a record |
| **Execute action** | Call a custom action defined on the entity |

### 7.2 Power Automate Triggers

Power Automate can be triggered from D365 F&O in several ways:

| Trigger | How It Works |
|---|---|
| **Data Entity import** | A Data Entity import triggers a flow that processes the imported data |
| **Custom action** | A custom action on a Data Entity triggers a flow |
| **Event-based** | An event handler in X++ sends a message to Azure Service Bus, which triggers a flow |
| **Scheduled** | A Logic App or Power Automate flow runs on a schedule and calls D365 F&O OData |

### 7.3 Integration Pattern: D365 F&O → Logic App → External System

```
[1] Data Entity import is executed in D365 F&O
    │
[2] Staging records are processed and written to target tables
    │
[3] postProcess() triggers an Azure Service Bus message
    │  Message contains: batch ID, record count, status
    │
[4] Logic App is triggered by the Service Bus message
    │
[5] Logic App calls external API (e.g., SAP, Salesforce, custom REST service)
    │
[6] External system receives the data and processes it
    │
[7] Logic App logs the result back to D365 F&O (optional)
```

**X++ Code to Send Service Bus Message from `postProcess()`:**
```xpp
using Microsoft.Azure.ServiceBus;

public void postProcess()
{
    int successCount = this.getSuccessCount();
    int failedCount = this.getFailedCount();
    Guid batchId = this.getCurrentBatchId();

    // Send to Service Bus
    this.sendToServiceBus(batchId, successCount, failedCount);
}

private void sendToServiceBus(Guid _batchId, int _success, int _failed)
{
    var connectionString = Parameters::find('ServiceBusConnectionString').Value;
    var queueName = 'd365-integration-events';
    
    var queueClient = new QueueClient(connectionString, queueName);
    
    var messageBody = JsonConvert.SerializeObject(new
    {
        BatchId = _batchId.ToString(),
        SuccessCount = _success,
        FailedCount = _failed,
        Timestamp = DateTime.UtcNow,
        EntityName = 'HRPersonnelEntity'
    });

    var message = new Message(Encoding.UTF8.GetBytes(messageBody));
    message.ContentType = "application/json";
    message.MessageId = Guid.NewGuid().ToString();

    queueClient.SendAsync(message).GetAwaiter().GetResult();
    queueClient.CloseAsync().GetAwaiter().GetResult();
}
```

### 7.4 Integration Pattern: External System → Logic App → D365 F&O

```
[1] External system sends data to Logic App (HTTP trigger)
    │
[2] Logic App transforms the data to match the Data Entity structure
    │
[3] Logic App calls D365 F&O OData endpoint to create/update records
    │
[4] D365 F&O processes the request through the staging pattern
    │
[5] D365 F&O returns the result (success/failure)
    │
[6] Logic App logs the result and sends a notification
```

### 7.5 Power Automate Flow Example: Scheduled Vendor Sync

**Flow Design:**
1. **Trigger**: Recurrence (Daily at 2:00 AM)
2. **Action**: HTTP - GET `https://d365-env.dynamics.com/data/Vendors?$filter=ModifiedDateTime ge yesterday`
3. **Action**: Parse JSON (schema from sample payload)
4. **Action**: Apply to Each (loop through vendors)
   - **Action**: HTTP - POST to external system (e.g., SAP Create Vendor)
   - **Action**: Condition - if success, update D365 `LastSyncedDateTime` via PATCH
5. **Action**: Send email summary

### 7.6 Best Practices for Power Platform Integration

1. **Use Data Entities as the integration layer** — don't expose tables directly via OData
2. **Use the staging pattern for write-back** — ensures validation and error handling
3. **Implement error handling in Logic Apps** — use try/catch patterns and dead-letter queues
4. **Use batch processing for large data volumes** — don't send thousands of records in a single request
5. **Secure connections with Managed Identity** — don't store credentials in Logic Apps
6. **Monitor integration runs** — use Azure Monitor and Logic Apps run history to track failures
7. **Use pagination (`$top`/`$skip`)** — avoid timeout on large datasets
8. **Implement idempotency** — use `ImportBatchId` or external IDs to prevent duplicate processing

---

## 8. Capstone Activity: Build an HR Employee Data Integration Entity

> **Objective**: Build a complete, production-ready Data Entity for HR employee data integration.

### 8.1 Requirements

Create a Data Entity called `HRPersonnelEntity` that:

1. **Exposes employee data** from `DirPerson`, `HCMWorker`, and `HRMPosition` tables
2. **Configures OData exposure**: `IsPublic = Yes`, `Public Entity Name = HRPersonnelEntity`, `Public Collection Name = HRPersonnelEntities`
3. **Exposed fields**: `PersonNumber`, `FirstName`, `LastName`, `FullName`, `Email`, `Position`, `Department`, `HireDate`, `Status`
4. **Staging table**: `HRPersonnelStaging` with internal fields: `PersonRecId`, `WorkerRecId`, `PositionRecId`, `StagingStatus`, `ErrorMessage`, `ImportBatchId`
5. **Link field**: Connects to `DirPerson.RecId`
6. **`process()` method**: Validation (email format, duplicate detection by `PersonNumber`), error logging
7. **`postProcess()` method**: Summary statistics, email/Logic App notification for failures
8. **Auto-mapping** for fields sharing names between entity and table
9. **Manual mapping** for `FullName` (concatenation of `FirstName + ' ' + LastName`)
10. **OData exposure** and test with sample Power Automate flow
11. **Deduplication logic**: Skip records already in target table
12. **Rollback logic**: Abort entire batch if >10% of records fail validation

---

### 8.2 Entity Design: HRPersonnelEntity

#### Data Sources and Joins

```
HRPersonnelEntity
├── Data Source 1: DirPerson (primary)
│   ├── Fields: RecId, AccountNum (→ PersonNumber), FirstName, LastName, Email
│
├── Data Source 2: HCMWorker
│   ├── Join: InnerJoin on HCMWorker.PersonRecId = DirPerson.RecId
│   ├── Fields: RecId (→ WorkerRecId), HireDate, Status
│
└── Data Source 3: HRMPosition
    ├── Join: LeftOuterJoin on HRMPosition.WorkerRecId = HCMWorker.RecId
    ├── Fields: RecId (→ PositionRecId), PositionId (→ Position), DepartmentId (→ Department)
```

#### Entity Fields (OData-Exposed)

| Entity Field | Source Table | Source Field | Mapping Type | Notes |
|---|---|---|---|---|
| `PersonNumber` | DirPerson | AccountNum | Auto | Primary identifier |
| `FirstName` | DirPerson | FirstName | Auto | |
| `LastName` | DirPerson | LastName | Auto | |
| `FullName` | DirPerson | FirstName + LastName | Manual | Computed: `FirstName + ' ' + LastName` |
| `Email` | DirPerson | Email | Auto | |
| `Position` | HRMPosition | PositionId | Auto | Via Position join |
| `Department` | HRMPosition | DepartmentId | Auto | Via Position join |
| `HireDate` | HCMWorker | HireDate | Auto | |
| `Status` | HCMWorker | Status | Auto | Enum → String conversion |

#### Link Field

| Property | Value |
|---|---|
| **Link Field** | `PersonRecId` |
| **Linked To** | `DirPerson.RecId` |

---

### 8.3 Staging Table: HRPersonnelStaging

```xpp
/// <summary>
/// Staging table for HRPersonnelEntity.
/// TempDB storage — temporary data, no persistence needed across sessions.
/// </summary>
table 50101 HRPersonnelStaging
{
    DataClassification = CustomerContent;
    Storage = TempDB;

    fields
    {
        // Primary key
        field(1; RecId; int64) { }

        // Business fields (match entity fields)
        field(2; PersonNumber; Code[20]) { }
        field(3; FirstName; Text[50]) { }
        field(4; LastName; Text[50]) { }
        field(5; Email; Text[250]) { }
        field(6; Position; Text[50]) { }
        field(7; Department; Text[50]) { }
        field(8; HireDate; Date) { }
        field(9; Status; Text[20]) { }

        // Internal tracking fields
        field(10; PersonRecId; int64) { }
        field(11; WorkerRecId; int64) { }
        field(12; PositionRecId; int64) { }
        field(13; StagingStatus; Enum HRPersonnelStagingStatus) { }
        field(14; ErrorMessage; Text[250]) { }
        field(15; ImportBatchId; Guid) { }
        field(16; CreatedDateTime; DateTime) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_PersonNumber; PersonNumber) { }
        key(IX_BatchId; ImportBatchId) { }
    }
}

/// <summary>
/// Staging status enumeration.
/// </summary>
enum HRPersonnelStagingStatus
{
    Ready = 0,        // Record is ready for processing
    Processing = 1,   // Currently being processed
    Processed = 2,    // Successfully written to target
    Failed = 3,       // Validation or write error
    Duplicate = 4,    // Duplicate detected (PersonNumber exists)
    BatchFailed = 5   // Batch-level failure (rollback threshold exceeded)
}
```

---

### 8.4 Complete `process()` Method with Validation, Deduplication, and Rollback

```xpp
/// <summary>
/// Handler class for HRPersonnelEntity staging processing.
/// Implements validation, deduplication, and rollback threshold.
/// </summary>
class HRPersonnelEntityHandler
{
    #define RollbackThresholdPercent(10)
    #define.MaxErrorMessageLength(250)

    public void process()
    {
        HRPersonnelStaging staging;
        DirPerson targetPerson;
        HCMWorker targetWorker;
        HRMPosition targetPosition;
        
        int totalToProcess = 0;
        int processedCount = 0;
        int successCount = 0;
        int failedCount = 0;
        int duplicateCount = 0;
        Guid batchId = Guid::newGuid();

        // Count total records to process
        totalToProcess = select count(RecId) from staging
            where staging.StagingStatus == HRPersonnelStagingStatus::Ready;

        if (totalToProcess == 0)
        {
            info('No records to process.');
            return;
        }

        info(strFmt('Starting batch %1: %2 records to process.', batchId, totalToProcess));

        while select staging
            where staging.StagingStatus == HRPersonnelStagingStatus::Ready
        {
            processedCount++;
            
            try
            {
                ttsbegin;

                // Update status to Processing
                staging.StagingStatus = HRPersonnelStagingStatus::Processing;
                staging.update();

                // ---- VALIDATION ----
                
                // 1. Validate required fields
                if (!this.validateRequiredFields(staging))
                {
                    this.markFailed(staging, 'Missing required fields: PersonNumber, FirstName, LastName, Email, or HireDate');
                    failedCount++;
                    ttscommit;
                    continue;
                }

                // 2. Validate email format
                if (!this.validateEmail(staging.Email))
                {
                    this.markFailed(staging, 'Invalid email format');
                    failedCount++;
                    ttscommit;
                    continue;
                }

                // 3. Check for duplicates by PersonNumber
                if (this.isDuplicatePersonNumber(staging.PersonNumber))
                {
                    this.markDuplicate(staging);
                    duplicateCount++;
                    failedCount++; // Count as failure for rollback threshold
                    ttscommit;
                    continue;
                }

                // 4. Check rollback threshold (>10% failures)
                if (failedCount > 0 && (failedCount * 100 / processedCount) > #RollbackThresholdPercent)
                {
                    this.markBatchFailed(staging, 
                        strFmt('Rollback threshold exceeded: %1% failure rate at record %2 of %3', 
                            #RollbackThresholdPercent, processedCount, totalToProcess));
                    failedCount++;
                    ttscommit;
                    
                    // Mark all remaining Ready records as BatchFailed
                    this.markRemainingAsBatchFailed(batchId);
                    break; // Stop processing
                }

                // ---- WRITE TO TARGET TABLES ----
                
                // 1. Create DirPerson record
                targetPerson.initValue();
                targetPerson.AccountNum = staging.PersonNumber;
                targetPerson.FirstName = staging.FirstName;
                targetPerson.LastName = staging.LastName;
                targetPerson.Email = staging.Email;
                targetPerson.insert();
                
                // 2. Create HCMWorker record
                targetWorker.initValue();
                targetWorker.PersonRecId = targetPerson.RecId;
                targetWorker.HireDate = staging.HireDate;
                targetWorker.Status = this.mapStatusStringToEnum(staging.Status);
                targetWorker.insert();

                // 3. Create HRMPosition record (if position data provided)
                if (staging.Position != '' || staging.Department != '')
                {
                    targetPosition.initValue();
                    targetPosition.WorkerRecId = targetWorker.RecId;
                    targetPosition.PositionId = staging.Position;
                    targetPosition.DepartmentId = staging.Department;
                    targetPosition.insert();
                }

                // 4. Update staging with generated RecIds for traceability
                staging.PersonRecId = targetPerson.RecId;
                staging.WorkerRecId = targetWorker.RecId;
                staging.PositionRecId = targetPosition.RecId;

                // 5. Mark staging as processed
                this.markProcessed(staging);
                successCount++;

                ttscommit;
            }
            catch (Exception::Error)
            {
                ttsabort;
                this.markFailed(staging, 'Unexpected error during processing');
                failedCount++;
            }
            catch (Exception::DuplicateKey)
            {
                ttsabort;
                this.markFailed(staging, 'Duplicate key error - record may have been inserted by another process');
                failedCount++;
            }
            catch (Exception::Deadlock)
            {
                ttsabort;
                // Deadlocks are handled by the batch framework retry logic
                // Re-throw to let framework handle retry
                throw;
            }
        }

        // Store summary for postProcess
        this.storeBatchSummary(batchId, totalToProcess, successCount, failedCount, duplicateCount);
        
        info(strFmt('Batch %1 processing complete: %2 succeeded, %3 failed (%4 duplicates).', 
            batchId, successCount, failedCount, duplicateCount));
    }

    // ===== VALIDATION METHODS =====

    private boolean validateRequiredFields(HRPersonnelStaging _staging)
    {
        return _staging.PersonNumber != ''
            && _staging.FirstName != ''
            && _staging.LastName != ''
            && _staging.Email != ''
            && _staging.HireDate != dateNull();
    }

    private boolean validateEmail(str _email)
    {
        if (strLen(_email) > 250)
        {
            return false;
        }
        
        // Basic email format validation
        int atPos = strScan(_email, '@', 1, strLen(_email));
        if (atPos <= 1 || atPos >= strLen(_email))
        {
            return false;
        }
        
        int dotPos = strScan(_email, '.', atPos + 1, strLen(_email));
        return dotPos > atPos + 1 && dotPos < strLen(_email);
    }

    private boolean isDuplicatePersonNumber(str _personNumber)
    {
        DirPerson existing;
        return exists select firstonly existing
            where existing.AccountNum == _personNumber;
    }

    // ===== STATUS MAPPING =====

    private HCMWorkerStatus mapStatusStringToEnum(str _statusStr)
    {
        switch (_statusStr.toLower())
        {
            case 'active': return HCMWorkerStatus::Active;
            case 'terminated': return HCMWorkerStatus::Terminated;
            case 'onleave': return HCMWorkerStatus::OnLeave;
            case 'pending': return HCMWorkerStatus::Pending;
            default: return HCMWorkerStatus::Active;
        }
    }

    // ===== STAGING STATUS HELPERS =====

    private void markProcessed(HRPersonnelStaging _staging)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Processed;
        _staging.ErrorMessage = '';
        _staging.update();
    }

    private void markFailed(HRPersonnelStaging _staging, str _error)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Failed;
        _staging.ErrorMessage = strLen(_error) > #MaxErrorMessageLength 
            ? subStr(_error, 1, #MaxErrorMessageLength) 
            : _error;
        _staging.update();
    }

    private void markDuplicate(HRPersonnelStaging _staging)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Duplicate;
        _staging.ErrorMessage = 'Duplicate PersonNumber';
        _staging.update();
    }

    private void markBatchFailed(HRPersonnelStaging _staging, str _error)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::BatchFailed;
        _staging.ErrorMessage = strLen(_error) > #MaxErrorMessageLength 
            ? subStr(_error, 1, #MaxErrorMessageLength) 
            : _error;
        _staging.update();
    }

    private void markRemainingAsBatchFailed(Guid _batchId)
    {
        update_recordset staging
            setting StagingStatus = HRPersonnelStagingStatus::BatchFailed,
                ErrorMessage = 'Batch aborted: rollback threshold exceeded'
            where staging.StagingStatus == HRPersonnelStagingStatus::Ready;
    }

    // ===== BATCH SUMMARY =====

    private void storeBatchSummary(Guid _batchId, int _total, int _success, int _failed, int _duplicates)
    {
        // Store in a temporary table or configuration for postProcess to retrieve
        HRPersonnelBatchSummary summary;
        
        summary.clear();
        summary.BatchId = _batchId;
        summary.TotalRecords = _total;
        summary.SuccessCount = _success;
        summary.FailedCount = _failed;
        summary.DuplicateCount = _duplicates;
        summary.ProcessedDateTime = DateTimeUtil::utcNow();
        summary.insert();
    }

    private HRPersonnelBatchSummary getBatchSummary(Guid _batchId)
    {
        HRPersonnelBatchSummary summary;
        select firstonly summary where summary.BatchId == _batchId;
        return summary;
    }
}

/// <summary>
/// Temporary table for storing batch summary between process() and postProcess().
/// </summary>
table 50102 HRPersonnelBatchSummary
{
    DataClassification = CustomerContent;
    Storage = TempDB;

    fields
    {
        field(1; RecId; int64) { }
        field(2; BatchId; Guid) { }
        field(3; TotalRecords; Int) { }
        field(4; SuccessCount; Int) { }
        field(5; FailedCount; Int) { }
        field(6; DuplicateCount; Int) { }
        field(7; ProcessedDateTime; DateTime) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_BatchId; BatchId) { }
    }
}
```

---

### 8.5 `postProcess()` Method with Summary and Notification

```xpp
public void postProcess()
{
    Guid batchId = this.getCurrentBatchId();
    HRPersonnelBatchSummary summary = this.getBatchSummary(batchId);
    
    if (!summary)
    {
        warning('No batch summary found for post-processing');
        return;
    }

    int successCount = summary.SuccessCount;
    int failedCount = summary.FailedCount;
    int duplicateCount = summary.DuplicateCount;
    int totalCount = summary.TotalRecords;

    // Log summary to Infolog
    info(strFmt('HR Personnel import complete (Batch: %1):', batchId));
    info(strFmt('  Total: %1 | Succeeded: %2 | Failed: %3 | Duplicates: %4', 
        totalCount, successCount, failedCount, duplicateCount));

    // Send notification for failed records
    if (failedCount > 0 || duplicateCount > 0)
    {
        this.sendCompletionNotification(batchId, successCount, failedCount, duplicateCount);
    }

    // Optional: Clean up batch summary record
    // summary.delete();
}

private void sendCompletionNotification(Guid _batchId, int _success, int _failed, int _duplicates)
{
    str subject = strFmt('HR Personnel Import Completed - Batch %1', _batchId);
    str body = strFmt(
        'HR Personnel data import batch %1 has completed.\n\n' +
        'Results:\n' +
        '  ✅ Successful: %2\n' +
        '  ❌ Failed: %3\n' +
        '  ⚠️ Duplicates: %4\n\n' +
        'Timestamp: %5\n\n' +
        'Review the Data Management workspace for detailed error logs.',
        _batchId, _success, _failed, _duplicates, DateTimeUtil::toStr(DateTimeUtil::utcNow()));

    // Option 1: Direct email (requires SMTP configuration)
    /*
    try
    {
        SmtpMail::send(
            'd365-noreply@company.com',
            'hr-integration@company.com',
            subject,
            body);
    }
    catch (Exception::Error)
    {
        warning('Failed to send notification email');
    }
    */

    // Option 2: Trigger Logic App via Service Bus (RECOMMENDED - decoupled)
    this.triggerLogicAppNotification(_batchId, _success, _failed, _duplicates);
}

private void triggerLogicAppNotification(Guid _batchId, int _success, int _failed, int _duplicates)
{
    // Send message to Azure Service Bus queue/topic
    // Logic App triggers on this message and sends formatted notification
    // (Email, Teams, Slack, etc.)
    
    var connectionString = Parameters::find('ServiceBusConnectionString').Value;
    var topicName = 'hr-integration-events';
    
    var topicClient = new TopicClient(connectionString, topicName);
    
    var messageBody = JsonConvert.SerializeObject(new
    {
        EventType = 'HRPersonnelImportCompleted',
        BatchId = _batchId.ToString(),
        SuccessCount = _success,
        FailedCount = _failed,
        DuplicateCount = _duplicates,
        Timestamp = DateTime.UtcNow,
        EntityName = 'HRPersonnelEntity'
    });

    var message = new Message(Encoding.UTF8.GetBytes(messageBody));
    message.ContentType = "application/json";
    message.MessageId = Guid.NewGuid().ToString();
    message.Label = 'HRPersonnelImportCompleted';

    topicClient.SendAsync(message).GetAwaiter().GetResult();
    topicClient.CloseAsync().GetAwaiter().GetResult();
}
```

---

### 8.6 Entity Mapping Configuration (Visual Studio Designer)

**Auto-Mapped Fields:**
| Entity Field | Table Field | Data Source |
|---|---|---|
| `PersonNumber` | `AccountNum` | DirPerson |
| `FirstName` | `FirstName` | DirPerson |
| `LastName` | `LastName` | DirPerson |
| `Email` | `Email` | DirPerson |
| `Position` | `PositionId` | HRMPosition |
| `Department` | `DepartmentId` | HRMPosition |
| `HireDate` | `HireDate` | HCMWorker |
| `Status` | `Status` | HCMWorker |

**Manual Mapping (Computed Column):**
| Entity Field | Expression | Data Source |
|---|---|---|
| `FullName` | `DirPerson.FirstName + ' ' + DirPerson.LastName` | DirPerson |

**Unmapped / Staging-Only Fields:**
| Field | Purpose |
|---|---|
| `PersonRecId` | Internal tracking — not exposed via OData |
| `WorkerRecId` | Internal tracking — not exposed via OData |
| `PositionRecId` | Internal tracking — not exposed via OData |
| `StagingStatus` | Internal — not exposed via OData |
| `ErrorMessage` | Internal — not exposed via OData |
| `ImportBatchId` | Internal — not exposed via OData |

---

### 8.7 Model Manifest Dependencies

```xml
<?xml version="1.0" encoding="utf-8"?>
<ModelManifest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Name>AcmeHRIntegration</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <Description>HR Personnel Data Integration Entity</Description>
  <Publisher>Acme Corporation</Publisher>
  <References>
    <ModelReference>
      <Name>ApplicationSuite</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
    <ModelReference>
      <Name>ApplicationFoundation</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
    <ModelReference>
      <Name>HcmCore</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
    <ModelReference>
      <Name>DirParty</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
  </References>
  <ConfigurationKey>AcmeHRIntegrationEnabled</ConfigurationKey>
</ModelManifest>
```

---

### 8.8 Testing with Power Automate

**Flow: Daily HR Sync from External HRIS**

1. **Trigger**: Recurrence (Daily 6:00 AM)
2. **Action**: HTTP - GET external HRIS API `/api/employees?modifiedSince=yesterday`
3. **Action**: Parse JSON
4. **Action**: Select - Map external fields to HRPersonnelEntity structure
5. **Action**: Create CSV table
6. **Action**: Create file in Azure Blob Storage (staging area)
7. **Action**: D365 F&O Connector - Import from Entity
   - Entity: `HRPersonnelEntity`
   - Source: Azure Blob Storage file
   - Import mode: Insert/Update
8. **Action**: Condition - Check import status
9. **Action (True)**: Send Teams notification "HR Sync Successful"
10. **Action (False)**: Send Teams notification "HR Sync Failed" with error details

---

## 9. Definitions: Key Terms with Layman Explanations

| Term | Technical Definition | Layman Explanation |
|---|---|---|
| **Data Entity** | A D365 F&O object that exposes table data to external systems via OData/REST APIs — consists of a DataEntity node, a Query, and optionally a staging table. | A "smart view" that packages data from multiple tables and serves it through a standard web API so other systems can read it easily. |
| **Composite Entity** | An entity that combines multiple Data Entities into a single integration endpoint for complex multi-source scenarios. | A "meta-entity" that stitches together several DataEntities into one big endpoint — like a playlist combining songs from different albums. |
| **Derived View** | A low-level view in the AOT with custom SQL logic that doesn't automatically expose via OData. | Writing raw SQL for a view — total control but you lose all automatic integration features (OData, staging, mapping). |
| **Staging Table** | An intermediate table (e.g., EntityNameStaging) that holds data temporarily before it's validated and written to target tables. | A "loading dock" where incoming data sits while it's checked for errors before being moved into the real tables. |
| **IsPublic** | A DataEntity property that controls whether the entity is exposed via OData endpoints. | The "publish" switch — when ON, the entity becomes visible and callable through the web API. |
| **Public Entity Name** | The singular name used in OData URLs for a single entity instance (e.g., `/data/HRPersonnelEntity`). | The name used when asking for ONE record: "Give me HRPersonnelEntity with ID 123." |
| **Public Collection Name** | The plural name used in OData URLs for the entity collection (e.g., `/data/HRPersonnelEntities`). | The name used when asking for a LIST: "Give me all HRPersonnelEntities." |
| **Link Field** | A field on a DataEntity that specifies the relationship to the underlying table's primary key (e.g., PersonRecId → DirPerson.RecId). | The "connector" that tells the system which record in the real table this entity row corresponds to. |
| **Auto-Mapping** | Automatic field mapping when entity field names and types match the underlying table fields exactly. | The system automatically connects fields with the same name — like matching socks by color. |
| **Manual Mapping** | Explicit field mapping defined in the Data Entity designer when auto-mapping doesn't work. | Manually telling the system "this entity field connects to THAT table field" when names don't match. |
| **Process Method** | The X++ method that reads staging records, validates them, and writes to target tables. | The "worker" that picks up each staging record, checks it, and moves it to the real table. |
| **PostProcess Method** | The X++ method that runs after all staging records are processed — used for summaries and notifications. | The "manager" that reviews how the batch went and sends a report. |
| **Rollback Threshold** | A percentage limit that aborts the entire batch if failure rate exceeds it (e.g., >10% failures). | A safety switch: "If more than 10% of records fail, stop everything and roll back." |
| **OData** | Open Data Protocol — a standard RESTful protocol for querying and updating data over HTTP. | A universal language for asking for data over the web — like SQL but for HTTP APIs. |
| **Logic Apps** | An Azure service for automating workflows and integrating systems without writing code. | A visual flowchart tool in the cloud that connects systems together — drag, drop, connect. |
| **Power Automate** | A low-code/no-code platform for building automated workflows across applications. | Like Logic Apps but designed for business users — build flows in a browser with point-and-click. |
| **Data Management Workspace** | The central UI in D365 F&O for importing, exporting, and managing data packages. | The control panel for moving data in and out of D365 — upload Excel, download CSV, run packages. |
| **Package (.axdp)** | A deployable unit containing Data Entities, mappings, and import/export settings. | A "shipping container" for data integration configuration — move it from dev to test to prod. |
| **DictClass** | An X++ system class providing runtime reflection over class metadata (methods, attributes, inheritance). | A tool that lets your code inspect other code at runtime — "What methods does this class have?" |
| **HttpClient** | A .NET class (System.Net.Http) for making HTTP requests from X++ code. | The "web browser" inside X++ — lets your code call external APIs and web services. |

---

## 10. Comparison Tables

### 10.1 Entity Type Selection Guide

| Requirement | Recommended Pattern |
|---|---|
| Read-only integration with external system | DataEntity |
| Write-back / import into D365 F&O | DataEntity + Staging Pattern |
| Combine 3+ unrelated entities into one endpoint | Composite Entity |
| Complex SQL (window functions, CTEs, UDFs) | Derived View |
| Need row-level security (XDS) | Apply XDS to underlying tables, not entity |
| High-volume recurring integration | DataEntity + Recurring Data Job + Logic Apps |
| One-time data migration | Data Management Workspace Import |
| Real-time event-driven integration | Custom Action + Service Bus + Logic Apps |

### 10.2 Staging Table Storage Options

| Storage Type | Use Case | Pros | Cons |
|---|---|---|---|
| **TempDB** (Recommended) | Standard staging — data doesn't need to persist | Fast, auto-cleanup, no database bloat | Data lost on session end / AOS restart |
| **Regular (InMemory)** | Very small datasets, high-frequency | Fastest for tiny datasets | Limited memory, not for large imports |
| **Regular (Permanent)** | Audit trail required, regulatory compliance | Full history, queryable after import | Requires manual cleanup, storage cost |

### 10.3 OData vs Direct Table Access

| Aspect | DataEntity (OData) | Direct Table Access (Not Recommended) |
|---|---|---|
| **Security** | Controlled via entity permissions | Requires table permissions — over-privileged |
| **Abstraction** | Shields consumers from schema changes | Consumers break when tables change |
| **Performance** | Optimized views, computed columns | N+1 query problems, no caching |
| **Write-back** | Staging pattern with validation | Direct writes bypass validation |
| **Upgrade Safety** | High — entity interface stable | Low — table schema changes break consumers |

### 10.4 Integration Pattern Selection

| Pattern | Latency | Volume | Complexity | Use Case |
|---|---|---|---|---|
| **Recurring Data Job** | Hours | High | Low | Daily/weekly bulk sync |
| **Logic Apps (Scheduled)** | Minutes-Hours | Medium | Low | Periodic pull/push |
| **Logic Apps (Event-Driven)** | Seconds | Low-Medium | Medium | Near real-time |
| **Custom Action + Service Bus** | Seconds | Low | High | Real-time, transactional |
| **OData Direct (HttpClient)** | Milliseconds | Low | Medium | Ad-hoc queries, lookup |
| **Batch Framework (SysOperation)** | Minutes-Hours | Very High | High | Massive data processing |

---

## 11. Microsoft Learn References

### Core Data Entities Documentation
- **Data Entities Overview**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro
- **Create a Data Entity**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/create-data-entity
- **Data Entity Properties**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entity-properties
- **Staging Tables**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/staging-tables

### OData and REST
- **OData Endpoints**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata
- **OData Query Options**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata-query-options
- **Custom OData Actions**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/custom-odata-actions

### Data Management Framework
- **Data Management Workspace**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-management-workspace
- **Import/Export Data**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/import-export-data
- **Recurring Data Jobs**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/recurring-data-jobs
- **Data Packages**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-packages

### Power Platform Integration
- **Logic Apps Connector**: https://learn.microsoft.com/en-us/connectors/dynamics365financeoperations/
- **Power Automate Connector**: https://learn.microsoft.com/en-us/connectors/dynamics365financeoperations/
- **Dual-Write**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/dual-write/dual-write-home-page

### Development References
- **DictClass Reference**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-reflection-dictclass
- **DictMethod Reference**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-reflection-dictmethod
- **HttpClient in X++**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-clr-interop
- **Service Bus Integration**: https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dotnet-get-started-with-queues

### Best Practices
- **Data Entity Best Practices**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entity-best-practices
- **Performance Tips**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entity-performance
- **Security**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entity-security

---

## 12. Common Mistakes to Avoid

| # | Mistake | Why It's Wrong | Correct Approach |
|---|---|---|---|
| 1 | **Exposing tables directly via OData** | Bypasses validation, security, and abstraction layer | Always use DataEntities as the integration layer |
| 2 | **Skipping the staging pattern for write-back** | No validation, no error handling, no rollback, no audit trail | Always use staging table + `process()`/`postProcess()` for imports |
| 3 | **Not setting `IsPublic = Yes`** | Entity won't appear in OData service document | Enable `IsPublic`, set `Public Entity Name` and `Public Collection Name` |
| 4 | **Using Derived View when DataEntity works** | Loses OData, staging, mapping, security integration | Default to DataEntity; only use Derived View for complex SQL |
| 5 | **Hardcoding OData URLs in code** | Breaks when environment changes (dev/test/prod) | Use configuration parameters or environment variables |
| 6 | **Not implementing deduplication** | Creates duplicate records on re-import | Check for existing records by business key before insert |
| 7 | **No rollback threshold** | One bad record can poison a batch of 10,000 | Implement percentage-based rollback (e.g., >10% failures) |
| 8 | **Storing credentials in Logic Apps/Power Automate** | Security risk, rotation nightmare | Use Managed Identity or Azure Key Vault references |
| 9 | **Ignoring pagination (`$top`/`$skip`)** | Timeouts and memory issues on large datasets | Always paginate; use `$top=1000` max per request |
| 10 | **Not testing with realistic data volumes** | Performance issues only appear in production | Test with production-scale data in Tier-2 environment |
| 11 | **Using Composite Entity for simple scenarios** | Adds complexity without benefit | Use Composite Entity only when combining multiple entities |
| 12 | **Forgetting to add `Link` field** | Breaks `$expand`, context filtering, write-back | Always define Link field connecting to primary table RecId |
| 13 | **Mapping staging fields in OData** | Exposes internal processing fields to consumers | Keep staging fields in staging table only; never expose via OData |
| 14 | **Not handling deadlocks in `process()`** | Batch fails on transient SQL contention | Implement retry logic or let batch framework handle it |
| 15 | **Using display methods for computed columns** | Slower — evaluated per row in X++ layer | Use computed columns (SQL-level) for simple expressions |

---

## Appendix: Quick Reference Card

### Data Entity Creation Checklist

```
☐ Define business requirement and data sources
☐ Choose entity type: DataEntity (default) / Composite / Derived View
☐ Create DataEntity in Visual Studio
☐ Add data sources and joins
☐ Select fields for OData exposure
☐ Set IsPublic = Yes
☐ Set Public Entity Name (singular)
☐ Set Public Collection Name (plural)
☐ Define Primary Key field(s)
☐ Define Link field (RecId of primary table)
☐ Enable staging (for write-back entities)
☐ Configure field mappings (auto + manual)
☐ Add computed columns for derived fields
☐ Create staging table (if not auto-generated)
☐ Implement process() method with validation
☐ Implement postProcess() with notifications
☐ Add deduplication logic
☐ Add rollback threshold logic
☐ Test with Data Management Workspace
☐ Test OData endpoint with Postman/Power Automate
☐ Document manual mappings and transformations
☐ Add to model manifest with correct dependencies
```

### Key X++ Classes for Data Entities

| Class | Purpose |
|---|---|
| `DataEntity` | Base class for all data entities |
| `DMFEntity` | Data Management Framework entity base |
| `DMFStagingTable` | Base for staging tables |
| `DictClass` / `DictMethod` | Runtime reflection |
| `HttpClient` | External HTTP calls |
| `SmtpMail` | Email notifications |
| `ServiceBusClient` | Azure Service Bus messaging |
| `JsonConvert` (Newtonsoft) | JSON serialization |

### OData URL Patterns

| Operation | URL Pattern |
|---|---|
| Get all entities | `GET /data/HRPersonnelEntities` |
| Get single entity | `GET /data/HRPersonnelEntities(PersonNumber='EMP001')` |
| Filter | `GET /data/HRPersonnelEntities?$filter=Status eq 'Active'` |
| Select fields | `GET /data/HRPersonnelEntities?$select=PersonNumber,FirstName,LastName` |
| Paginate | `GET /data/HRPersonnelEntities?$top=100&$skip=200` |
| Expand related | `GET /data/HRPersonnelEntities?$expand=Position` |
| Count | `GET /data/HRPersonnelEntities/$count` |
| Create | `POST /data/HRPersonnelEntities` |
| Update | `PATCH /data/HRPersonnelEntities(PersonNumber='EMP001')` |
| Delete | `DELETE /data/HRPersonnelEntities(PersonNumber='EMP001')` |

---

*End of Chapter — Data Entities*