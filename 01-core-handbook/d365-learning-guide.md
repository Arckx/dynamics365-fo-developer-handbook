---
name: d365-learning-guide
description: Desktop guide with 15 chapters of deep D365 F&O content including code examples, tables, and activities
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-29T16:48:29.471Z
---

# D365 Finance & Operations — Technical Intern Learning Guide

> **Your 4–12 month foundational reference.** Every concept below is rooted in the official Microsoft documentation at [learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/). For the latest updates, always verify against that source — this guide is your scaffold, not your end point.

---

## How to Use This Guide

1. **Read the chapter** — absorption first, coding second.
2. **Attempt the activity** — use the hints to explore multiple valid paths.
3. **Compare with the ideal solution** (provided at the end of each chapter for chapters 1–14, and in full detail for Chapter 15) — understand *why* the recommended approach was chosen.
4. **Return to Microsoft Docs** for anything that has changed, been deprecated, or has newer patterns.

---


# Chapter 1: Platform Architecture & AOT

## 1.1 The Platform Architecture — What You Are Actually Working Inside

Before you write a single line of X++, understand the platform you are operating inside. D365 Finance & Operations is a **cloud-native, multi-tier enterprise application** built on four architectural pillars:

### 1.1.1 The Four Pillars

| Pillar | Technology | Role | What It Means to You as a Developer |
|---|---|---|---|
| **Application Tier** | AOS (Application Object Server) — runs X++ IL code | Executes business logic, interprets X++, manages transactions, serves metadata | Your X++ code runs here — not in the browser, not in SQL Server |
| **Database Tier** | Azure SQL Database / SQL Server | Stores all business data — tables, indexes, stored procedures (generated from AOT), temp tables | Your `insert()`, `update()`, `delete()` calls translate to SQL statements against this tier |
| **Presentation Tier** | Single browser-based web client (HTML5/CSS/JS) running in Edge, Chrome, or Safari | Renders forms, menus, navigation — the user's view of the system | You design forms in this tier; the form definition lives in the AOT, and the AOS streams metadata to the browser which renders the UI |
| **Integration Tier** | Azure Services (Service Bus, Azure Functions, Logic Apps), OData/REST endpoints | Connects D365 F&O to external systems — Power Platform, third-party ERP, HR systems | When building data entities or integration patterns, you interact with this tier |

### 1.1.2 How a Request Flows Through the System

Understanding the request lifecycle is essential for debugging and for writing code that performs well:

```
User clicks a button on a form (HTML/Windows client)
    │
    ▼
[Client-side] HTTP request + context info sent to AOS
    │
    ▼
[AOS Application Tier]  X++ IL code executes
    │   • Security checks (who are you? what can you do?)
    │   • Transaction management (ttsBegin/ttsCommit)
    │   • Business logic (your X++ code runs here)
    │   • Cross-layer calls (SYS → ISV → VAR → CUS → USR)
    │
    ▼
[Database Tier]  SQL statements generated from AOT metadata
    │   • SQL Server validates permissions (row-level, column-level)
    │   • Data is read/written to Azure SQL Database
    │
    ▼
[AOS]  Results returned to client as XML/JSON
    │
    ▼
[Client]  Form refreshes, Infolog displays messages
```

**The critical insight for a new developer**: When your X++ code runs slowly, the bottleneck is almost never the X++ itself — it is either (a) too many SQL round-trips (selecting one record at a time in a loop instead of using `exists join` or `insert_recordset`) or (b) synchronous calls to remote services or external systems that the AOS is blocked waiting for.

### 1.1.3 The Role of Azure in D365 F&O

D365 F&O runs in Azure. Understanding the Azure pieces:

| Azure Component | Purpose | Developer Relevance |
|---|---|---|
| **Azure SQL Database** | Hosts the business database | Your table definitions create SQL tables here; SQL performance tuning (indexes, joins) applies directly |
| **Azure App Service** | Hosts the AOS workers (Application Object Server) | Your X++ IL runs in these workers; scaling AOS workers affects throughput |
| **Azure DevOps / GitHub** | Build and deployment CI/CD | Build pipelines compile X++, produce `.axmodel` artifacts, deploy to environments |
| **Azure Active Directory (Azure AD)** | Authentication and authorization | Every user authenticates via Azure AD; role-based access flows through the D365 security model |
| **Azure Storage** | Model store (AOT object storage) | The model store is a file share (e.g., `C:\AOSService\PackagesLocalDirectory` or `K:\` in cloud environments), not a SQL database — understanding this prevents common deployment errors |
**Source:** [Models and packages](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-tools/models) |
| **Azure Key Vault / Managed Identity** | Credential and secret management | Configuration keys (`#ISO`, `USMF`, custom keys) are encrypted credentials your code references at runtime |
| **Azure Service Bus** | Async messaging between services | Used by integration patterns — your code can send/receive messages via .NET interop (`System.ServiceModel` or `HttpClient`) |

---

## 1.2 The Application Object Tree (AOT) — The Single Source of Truth

### 1.2.1 What Is the AOT?

The AOT is a **hierarchical, metadata-driven repository** that contains every object in the D365 F&O system — every table, class, form, view, menu, security role, report, and data entity. It is not a SQL database of these objects; it is a **file system** organized as a tree of XML-like metadata files, stored in the **model store** as a file share (e.g., `C:\AOSService\PackagesLocalDirectory` or `K:\` in cloud-hosted environments).

**Source:** [Models and packages - Finance & Operations](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/models)

The AOT serves as:
- The **design-time** interface — developers browse, create, and modify objects here
- The **source of truth** for runtime behavior — the AOS loads AOT metadata into memory at startup and uses it to generate SQL, render forms, and enforce security
- The **compile-time** compilation unit — when you build your project in Visual Studio, the AOT nodes in your model are compiled into IL

### 1.2.2 The AOT Tree — Complete Node Hierarchy

The AOT is organized into top-level nodes. Every object belongs to exactly one top-level node. The hierarchy is:

```
AOT (Application Object Tree)
│
├── Classes
│   ├── Static classes (utility, service entry points)
│   ├── Instance classes (business logic objects)
│   ├── System classes (Sys**, Global, FormRun, etc.)
│   ├── Extension classes ([ExtensionOf(...)])
│   └── Event handler classes (subscribing to base class events)
│
├── Tables
│   ├── Base tables (standard system tables)
│   ├── Extended tables (tables that inherit from base tables)
│   ├── Table Extensions ([ExtensionOf(tableStr(...))])
│   └── Temp tables (in-memory only, TableType = Temp or TempDB)
│
├── Views
│   ├── Base views (custom SQL joins stored in AOT)
│   ├── Derived views (views built from other views)
│   ├── Composite entities (views with a staging pattern for data entities)
│   └── View Extensions ([ExtensionOf(viewStr(...))])
│
├── Forms
│   ├── Base forms (standard system forms)
│   ├── Form Extensions ([ExtensionOf(formStr(...))])
│   ├── Form Data Sources (one per table/query the form reads)
│   ├── Form Design (layout — groups, tabs, grids)
│   ├── Form Design Parts (FastTabs, FactBoxes, user controls)
│   └── Form Extensions (add controls and sections to existing forms)
│
├── Data Sources (within Forms)
│   ├── Table DataSource (points to a specific table)
│   ├── Query DataSource (points to a query object)
│   └── Link Type (Inner, Outer, Exists, NotExists)
│
├── Menus
│   ├── Menu (hierarchical navigation structure)
│   ├── Menu Extension ([ExtensionOf(menuStr(...))])
│   └── Display menus vs. Action menus (Display opens forms, Action runs methods)
│
├── Menu Items
│   ├── Display Menu Item (MenuItemDisplay — opens a form)
│   ├── Action Menu Item (MenuItemAction — runs a class method)
│   ├── Output Menu Item (MenuItemOutput — displays a report)
│   └── Button Menu Item (MenuItemButton — toolbar button on a form)
│
├── Macros
│   ├── Global macros (accessible from any X++ file)
│   └── Class/table-level macros (scoped to the defining element)
│
├── ETNs (Enterprise Text Notifications)
│   └── Used for printing, email templates, document formatting, report headers
│
├── Security
│   ├── Security Roles (the top-level role assignment)
│   ├── Duties (collections of privileges)
│   ├── Privileges (granular access: specific tables, specific access levels)
│   ├── Permissions (field-level and record-level access)
│   └── Security Keys (used to scope access by business context)
│
├── Data Dictionary
│   ├── Extended Data Types (EDTs) — typed aliases with metadata
│   ├── Enums — named constant sets
│   ├── Table Groups — logical groupings for lookup display
│   ├── Field Groups — named field collections for auto-form generation
│   ├── Relations — links between fields on different tables
│   └── Table Indexes — primary, alternate, hash, and non-unique indexes
│
├── Test Frameworks
│   ├── SysTest classes (unit test classes)
│   ├── SysTestSetup / SysTestMethod / SysTestCleanup attributes
│   └── Test data builder patterns
│
├── Extensions
│   ├── Table Extensions
│   ├── Form Extensions
│   ├── Class Extensions
│   └── View Extensions
│
├── Metadata
│   ├── Model information (name, version, layer, properties)
│   └── Layer assignment for every object
│
├── References
│   └── Auto-generated cross-references (show what calls what)
│
├── Queries
│   ├── Query objects (distinct from inline select statements)
│   └── QueryBuildDataSource, QueryBuildRange, QueryBuildLink (runtime query APIs)
│
└── Jobs
    └── X++ scripts executed ad-hoc for data fixes, reports, or one-off processing
```

### 1.2.3 AOT Object Properties — The Properties That Matter Most

Every AOT object has a **Properties** pane in Visual Studio. The following properties are the ones that directly affect your daily development and that beginners must understand:

#### Table-Level Properties

| Property | Values | What It Controls | Common Mistake |
|---|---|---|---|
| `CacheLookup` | `None`, `NotInTTS`, `Found`, `FoundAndEmpty`, `EntireTable` | How SQL Server caches lookups of this table's records. `None`: no caching. `NotInTTS`: caches on lookup; transaction-scoped caches don't persist outside the transaction. `Found`: caches successful lookups across transaction boundaries. `FoundAndEmpty`: same as Found, but also caches lookups that found no record. `EntireTable`: loads the whole table into a server-side cache after first select. | Setting `CacheLookup = EntireTable` on a large transactional table (e.g., `SalesLine`) wastes server memory. Use `Found` or `NotInTTS` for large tables. |
| `SaveDataPerCompany` | `Yes`, `No` | When `Yes`, each Legal Entity (company) has its own copy of the data. When `No`, data is shared across all companies. | Forgetting to set this — if you create a master data table (e.g., a chart of accounts), it should be `No`. A transaction table (e.g., invoice lines) should be `Yes`. |
| `AllowDuplicates` | `Yes`, `No` | Whether the table allows rows where all alternate index key fields are identical | Forgetting to set `AllowDuplicates = No` on index keys means duplicates can exist in the database even though the business expects uniqueness |
| `TableGroup` | `Transaction`, `Master`, `Parameter`, `Invoice`, etc. | Controls how the table appears in form lookups and navigation patterns | Using `Master` for a high-volume transaction table — use `Transaction` so the AOT treats it appropriately during find operations |
| `PrimaryIndex` | RecId or an alternate key | The clustered index on the physical SQL table | Changing from `RecId` is only valid for specific cases — most custom tables should keep `RecId` as the primary index |

#### Field-Level Properties

| Property | Values | What It Controls |
|---|---|---|
| `DataType` | EDT reference or base type | **Always an EDT** — never use base types directly (`string 20` is wrong; use `CustAccount` EDT instead) |
| `Extension` | EDT name | Links this field to an Extended Data Type |
| `Label` | A label ID reference | User-facing name (appears in form labels, report captions) |
| `HelpText` | A label ID reference | Tooltip text shown when the user hovers over the field |
| `Mandatory` | `Yes`, `No` | Controls the `Validate` on the table — prevents saving a record if this field is empty |
| `Visible` | `Yes`, `No` | Whether the field appears on forms by default (can be overridden per form) |
| `AllowEdit` | `Yes`, `No` | Whether the field can be modified on any form using this data source |
| `Method` | Yes — if the field is a computed value displayed via a method | When `Yes`, the field has no physical column in the SQL table — its value is computed by the `DisplayMethod` class method each time it is shown |
| `Relation` | EDT + referenced table | Enables automatic lookups — when a control is bound to this field, it shows a lookup to the referenced table using the EDT's relation metadata |
| `ReferenceField` | Field number on the referenced table | Specifies which field on the related table is shown in the lookup dialog |
| `Skip` | `Yes`, `No` | When `Yes`, the field is skipped from auto-form generation and lookup inclusion |
| `Array` | `Yes`, `No` | When `Yes`, the field is stored as an array of values (rare — used in specific system tables) |

#### Form-Level Properties

| Property | Values | What It Controls |
|---|---|---|
| `FrameType` | `Frame`, `Dialog`, `Popup`, `Workflow`, `ListPage`, `ListPageDetails`, `ListItemPage` | The visual chrome and behavior of the form — a `ListPage` has a navigation tree and grid; a `Dialog` has OK/Cancel buttons and is modal |
| `MultiSelect` | `Yes`, `No` | Whether users can select multiple records in the form's grid |
| `DeleteAllowed` | `Yes`, `No` | Whether the Delete menu item is enabled for this form |
| `CopyAllowed` | `Yes`, `No` | Whether the Copy menu item is enabled |
| `NewAllowed` | `Yes`, `No` | Whether the New record button is enabled |
| `AutoDeclaration` | `Yes`, `No` | When `Yes`, the form auto-generates variable names for each control and data source — convenient but leads to implicit dependencies. Set to `No` for clean, explicit code |
| `ShowQueryProperties` | `Yes`, `No` | Whether the Data Source property sheet is shown in the form designer |
| `WindowType` | `Existing`, `New` | Whether the form opens in an existing window or a new modal window |

#### Class-Level Properties

| Property | Values | What It Controls |
|---|---|---|
| `Access` | `Public`, `Private`, `Protected`, `Internal` | Encapsulation level — most business logic classes are `Public` |
| `InstantiationType` | `SingleInstance`, `Static`, `Object` | `SingleInstance` (singleton) means there is only ever one instance of the class; `Static` means the class has only static methods and is never instantiated; `Object` means you create instances with `new` or `construct()` |
| `Abstract` | `Yes`, `No` | When `Yes`, the class cannot be instantiated directly — it serves as a base class |
| `Final` | `Yes`, `No` | When `Yes`, the class cannot be extended via `extends` |
| `EntitlementType` | `Internal`, `External` | Controls how the class is used in entitlement policies |

### 1.2.4 The `Common` Class — Base for All Tables

Every table in D365 F&O inherits from the `Common` class at runtime. This means every table variable (buffer) has access to these universal fields and methods:

| Member | Type | Description |
|---|---|---|
| `RecId` | `int64` | The auto-generated database primary key — every table has this field even if you don't define it explicitly |
| `TableId` | `int` | The integer table ID — unique per table in the system (e.g., `tableNum(CustTable)`) |
| `RecVersion` | `int` | Optimistic concurrency version counter — incremented on every write; used to detect conflicts |
| `Partition` | `int` | Multi-tenant partitioning — used in cloud environments to separate data by partition |
| `fieldNum(TableName, FieldName)` | Intrinsic function | Returns the integer field ID at runtime |
| `fieldId2Name(TableId, FieldId)` | Intrinsic function | Converts a numeric field ID to its string name |
| `fieldName2Id(tableId, fieldName)` | Intrinsic function | Converts a field name string to its integer ID |
| `initValue()` | Method | Initializes default values (system fields like `CreatedDateTime`, `ModifiedDateTime`, `CreatedBy`, `ModifiedBy`) for a new record |
| `insert()` | Method | Writes the buffer to the database as a new record |
| `update()` | Method | Writes changes to an existing record |
| `delete()` | Method | Removes the record from the database |
| `validateWrite()` | Method | Returns `boolean` — returns `true` if the record can be saved, `false` if there is a validation error |
| `validateField(FieldId)` | Method | Returns `boolean` — validates a single field value |
| `select()` | Intrinsic function | Executes a query and returns the first record (used with `while select`) |
| `firstOnly()` | Intrinsic function | Limits query to return only the first matching record |
| `doInsert()` | Method | Internal — the actual insert; `insert()` calls this after `validateWrite()` |
| `doUpdate()` | Method | Internal — the actual update; `update()` calls this after `validateWrite()` |
| `doDelete()` | Method | Internal — the actual delete |

**The `RecId` field is critical**: it is the primary key in SQL Server, it is auto-generated (you never set it), and it is how all table relationships are internally joined. A `select firstonly` on any table returns a buffer with a valid `RecId` if a matching row exists.

### 1.2.5 The `Object` Base Class

All classes in X++ ultimately inherit from `Object` (not from a named class you define explicitly). `Object` provides:

- `objGetClassName()` → `str` — returns the class name as a string at runtime (used in logging, error messages, and dynamic dispatch)
- `objIsFirstInit()` → `boolean` — whether the object is being constructed for the first time (not a re-instantiation)
- `objSave()` / `objLoad()` — persistence methods (used in specific frameworks)
- `Global::objType(obj)` — returns an enum (`Types::Class`, `Types::String`, `Types::Integer`, etc.) for runtime type checking

---

# Chapter 2: Models, Layers, Packages

## 2.1 Models, Layers, and Packages — Deep Technical Details

### 2.1.1 What Is a Model?

A **model** is the fundamental unit of versioning and dependency in D365 F&O. A model is a named, versioned collection of AOT objects that share a single `ModelManifest.xml`. Each model:

- Has a **unique name** within the model store (e.g., `MyCustomModel`, `ApplicationSuite`, `ApplicationFoundation`)
- Has a **version** string following semantic versioning (`1.0.0.0`)
- Declares **dependencies** on other models — these are ordered at deployment time
  - Is assigned a **layer** (`SYS`, `ISV`, `VAR`, `CUS`, `USR`)
- Exports to a **`.axmodel` file** — a binary package containing the model's metadata as XML serialization blobs

### 2.1.2 Layers — The Upgrade Boundary

The **layer** is the concept that determines whether your code survives a Microsoft update or gets overwritten.

#### Layer Hierarchy (from lowest system layer to highest customer layer)

```
SYS (lowest — Microsoft system framework)
  ↓
ISV (Independent Software Vendor layer — partner/ISV solutions)
  ↓
VAR (Variation layer — country/region/legal adaptations by Microsoft)
  ↓
CUS (Customer customization layer — your customizations)
  ↓
USR (User layer — highest, no key required to access)
```

**How upgrading works with layers:**
When Microsoft releases a CU (Cumulative Update), they deliver updates to the VAR layer. Your CUS-layer code is untouched because it's at a higher layer. The framework resolves object resolution by looking for an object at the highest available layer first, then falling back to lower layers.

**The resolution algorithm:**
1. The system searches for an object by its **name** (class name, table name, form name, etc.)
2. When multiple objects with the same name exist across different layers, the **highest layer** wins
3. Example: If `CustTable` exists in SYS, ISV, VAR, and CUS layers — the CUS-layer version is loaded
4. If you delete your CUS-layer `CustTable` extension, the system falls back to the ISV, VAR, or SYS layer version

#### What You Need to Know About Each Layer as a Developer

| Layer | When It Exists in Practice | Do You Ever Modify It? |
|---|---|---|
| **SYS** | Always — it contains the D365 F&O platform framework (`Sys`, `Global`, `Kernel`, etc.) | **No.** Never modify SYS objects directly — ever. You can extend them via CoC or event handlers. |
| **ISV** | Used by Microsoft's ISV partners (Dynamics AX partners) for their solutions | **No** (unless you are an ISV partner developing a managed solution) |
| **VAR** | Exists in regional deployments — Microsoft-owned localization | **No.** Microsoft manages these. |
| **CUS** | Default layer for customer customizations | **Yes.** This is where you develop as a customer technical intern |
| **USR** | User-specific layer, highest priority, no key required | Rarely used directly by developers — mainly for end-user personalizations, not standard development work |

### 2.1.3 Packages — The Deployable Unit

A **package** is the unit of deployment. It contains one or more models and their `.axmodel` files. Packages are created and managed as part of the build pipeline in Azure DevOps or GitHub Actions.

- **One package** can contain **multiple models** (e.g., a package might contain a base model and a customer extension model)
- **One model** is deployed as one `.axmodel` file
- Package dependencies determine deployment order — a package can declare that it depends on another package, meaning the dependency must be deployed first
- Package names follow a naming convention like `MyModel_1.0.0.0` and live in LCS as build artifacts

### 2.1.4 Model Manifest — The Heart of Your Project

The `ModelManifest.xml` file lives at the root of every Visual Studio model project. It defines everything that the deployment system needs to know about your model.

```xml
<?xml version="1.0" encoding="utf-8"?>
<ModelManifest xmlns="http://schemas.microsoft.com/dynamics/ax/2014/11/metadata">
  <!-- Model identity -->
  <Name>MyCustomAPModel</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  
  <!-- Dependencies — models that must be deployed BEFORE this one -->
  <References>
    <ModelReference>
      <Name>ApplicationSuite</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
    <ModelReference>
      <Name>ApplicationFoundation</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
  </References>
  
  <!-- Optional: other configuration -->
  <ConfigurationKey>MyCustomAPModelEnabled</ConfigurationKey>
</ModelManifest>
```

**`ModelManifest.xml` — Key Elements in Detail:**

| Element | Required? | Description |
|---|---|---|
| `Name` | Yes | The model's unique name — must not collide with any existing model name |
| `Version` | Yes | Semantic version (`major.minor.build.revision`) — incremented on each deployment |
| `Layer` | Yes | The layer assignment (`SYS`, `ISV`, `VAR`, `CUS`, `USR`) — determines upgrade behavior |
| `References.ModelReference.Name` | Conditional | Each dependency reference — the name of a model that must be present for this model to deploy |
| `References.ModelReference.MinVersion` | Optional | Minimum version of the referenced model required — catches version mismatch errors at deployment time |
| `ConfigurationKey` | Optional | A configuration key that controls whether this model's features are active |

**Dependency ordering rules:**
- A model cannot be deployed unless all its referenced models are already present in the model store
- If `MyCustomModel` references `ApplicationSuite`, it means `ApplicationSuite` must be deployed first — in LCS release management, this is handled automatically for standard dependencies
- For custom models, you must ensure the build pipeline creates the dependency order correctly

---

# Chapter 3: Visual Studio Setup & Language Mindset

## 3.1 Visual Studio Connection & Project Setup — Production-Grade

### 3.1.1 Prerequisites Before You Connect

Before opening Visual Studio and connecting to Dynamics 365, ensure:

1. **Visual Studio 2019 or 2022 is installed** — the version must match the LCS environment type (check the LCS environment configuration page for the supported Visual Studio version)
2. **The "Dynamics 365 Developer Tools" workload** is installed in Visual Studio — available via the Visual Studio Installer as a component of the .NET desktop development workload or a separate workload depending on the VS version
3. **Azure AD credentials** for a user with the `Developer` role or equivalent in LCS
4. **Network connectivity** — your machine must be able to reach the Azure region where your LCS environment resides (corporate firewalls may block this)
5. **A valid Azure subscription** linked to the LCS project (LCS handles this provisioning automatically when creating an environment)

### 3.1.2 Connecting Visual Studio — Step by Step

**Step 1: Open Visual Studio**
Launch Visual Studio and either create a new model project or open an existing solution.

**Step 2: Connect to Dynamics 365**
- Navigate to **Dynamics 365 → Connect to Dynamics 365** on the Visual Studio menu bar
- A connection dialog appears listing all LCS projects you have access to (based on your Azure AD identity)
- Select the LCS project and the target environment (Dev, Test, etc.)
- If prompted, authenticate via Azure AD — this uses OAuth 2.0 and requires multi-factor authentication typically

**Step 3: Synchronize the AOT**
After connecting, Visual Studio synchronizes the AOT from the connected environment. This downloads model metadata (XML definitions of all AOT objects) and populates your Visual Studio project view. This may take several minutes for environments with many models.

**Step 4: Create or Open a Model Project**
If the environment has no model project for your customizations yet:
- **File → New → Dynamics 365 Project**
- Choose the project template appropriate for your scenario (Class Library, Model Project, etc.)
- Visual Studio creates the project with the standard folder structure

If a model project already exists (typical when working in a team):
- **File → Open → Dynamics 365 Project** and navigate to the `.csproj` file in the model store of your connected environment

### 3.1.3 The Model Store — File System Architecture

The model store is **not** a SQL database. It is a **shared file system directory** on the AOS server machine (on-premises) or an **Azure File Share** (in cloud deployments). The model store contains:

```
C:\Views\ (on-premises AOS)  OR  \\[AzureFileShare]\ModelStore (cloud)
│
├── Models\
│   ├── MyCustomModel\
│   │   ├── 1.0.0.0\
│   │   │   ├── ModelManifest.xml
│   │   │   ├── Metadata\          ← serialized AOT objects
│   │   │   │   ├── Classes\
│   │   │   │   │   ├── MyServiceClass.xml
│   │   │   │   │   └── MyExtension.xml
│   │   │   │   ├── Tables\
│   │   │   │   │   ├── MyCustomTable.xml
│   │   │   │   │   └── MyCustomTable_Extensions.xml
│   │   │   │   ├── Forms\
│   │   │   │   ├── DataEntities\
│   │   │   │   └── Security\
│   │   │   └── Binary\            ← compiled IL assemblies, resources
│   │   │       └── MyCustomModel.dll
│   │   └── 1.1.0.0\               ← previous version, retained for rollback
│   │       └── ...
│   ├── ApplicationSuite\
│   │   └── 10.0.10212.1001\
│   │       └── ...
│   ├── ApplicationFoundation\
│   │   └── ...
│   └── ...
│
└── ...
```

**Key implications:**
- The model store is **shared** across all AOS instances in the environment — when you deploy a model, it is visible to all AOS workers
- Deploying a model **modifies the shared file system** — you need appropriate deployment permissions to write to the model store
- The `Binary` folder contains **compiled IL** — when Visual Studio builds your project, it produces the `.dll` file that goes here
- Multiple versions of the same model can coexist (for rollback) — the AOS uses the **highest version** that satisfies all dependency requirements

### 3.1.4 Project Settings You Must Configure Correctly

#### Model Manifest Configuration
Open `ModelManifest.xml` in your project and verify:
- **`Name`** — unique, follows your company's naming convention (e.g., `ContosoCustomAP`)
- **`Version`** — starts at `1.0.0.0`, increment with each meaningful change
- **`Layer`** — `CUS` for customer work, `ISV` for partner work, `USR` for user-specific customizations
- **`References`** — every model your code depends on must be listed:
  - `ApplicationFoundation` — base system services, `Global` class
  - `ApplicationSuite` — core business modules (AP, AR, Inventory, etc.)
  - Any partner model if you depend on ISV code
- **`ConfigurationKey`** — if your code introduces new features behind a config key, define it here

#### Project Build Configuration
- **`Active solution configuration`**: `Release` for deployment builds, `Debug` for development (enables breakpoint debugging)
- **`Target platform`**: x64 (D365 F&O runs on 64-bit servers)
- **`Sign assembly`**: Required for ISV models (partner code), optional for customer models
  - Strong name key file must be generated and specified in project properties
  - The public key token is embedded in the assembly and affects model dependency resolution

#### Debugging Configuration
- **`Start Action`**: The project must be set to start the Dynamics 365 client or connect to a running environment for debugging
- **Breakpoints**: Set in X++ code files (`*.xpp`) within Visual Studio — breakpoints on static methods (`::main`), instance methods, event handlers, and table validations all work
- **Attach to process**: For debugging on a remote environment, attach the Visual Studio debugger to the AOS process (advanced scenario, typically automated in CI/CD pipelines)

---

## 3.2 Language Mindset & Foundational Concepts — The X++ Way

D365 F&O comes with its own language mindset that fundamentally changes how you think about software development. Before writing your first line of X++, internalize these foundational concepts:

### 3.2.1 The Three Pillars of X++ Thinking

**Relational-First, Not Object-First**

In traditional object-oriented languages (like Java), you design classes first and then persist them to a database. In D365 F&O, the database is the starting point. Business entities — customers, vendors, invoices, purchase orders — are tables with rows. You think in terms of **relations between data sets** (joins, foreign keys, cascading updates), not just objects. The AOT stores table definitions as metadata, and the AOS executes SQL against those tables. Your code operates on **table buffers** (variables that hold a single row at a time), not on object graphs.

> **Layman's explanation:** Imagine you're building a filing cabinet system. In OOP, you'd design the "File" object first, then figure out how to store it. In D365 F&O, you design the cabinet drawers (tables), the folders inside (rows), and the labels on the folders (fields) first. Your code just pulls out one folder at a time, reads it, maybe changes a label, and puts it back.

**Metadata over Code**

The AOT (Application Object Tree) is not just a file system — it's a **metadata repository**. Every table, field, index, relation, class, form, menu item, security role, and report is stored as structured metadata. The AOS reads this metadata at runtime to build the application. You don't "write code to create a table"; you **define the table in the AOT**, and the system generates the SQL schema, the form, the lookup, and the validation automatically. This is why D365 F&O developers say "configuration is code" — declarative metadata replaces imperative code for most standard patterns.

> **Layman's explanation:** Think of the AOT as a giant spreadsheet where every column is a property (name, type, length, mandatory, label, help text). You fill in the rows (tables, fields, indexes), and the system builds the application from that spreadsheet. You rarely write "CREATE TABLE" SQL or "new Form()" code — you just declare what things *are*, not how to *build* them.

**Extensibility as a Constraint**

Microsoft pushes updates (Cumulative Updates, hotfixes) to the `SYS` layer several times a year. If you modify Microsoft's base tables or classes directly (overlayering), your changes will be **overwritten** and lost during the next update. The extension model (table extensions, class extensions with Chain of Command, event handlers) is not a "nice to have" — it is a **hard requirement** for code that survives upgrades. Every customization you write must ask: "Will this survive the next Microsoft update?"

> **Layman's explanation:** Microsoft owns the foundation of the house (the `SYS` layer). You're building an addition. If you knock down a foundation wall to run a pipe, the next time Microsoft repairs the foundation, your pipe gets buried. Instead, you must run your pipes *alongside* the foundation walls using the approved extension points (CoC, event handlers) so your addition stays intact when the foundation is repaired.

---

### 3.2.2 Foundational Technical Concepts

#### Primitive Data Types & the `real` Type
X++ has **true primitive types** that map directly to SQL types: `int` (32-bit), `int64` (64-bit, used for `RecId`), `real` (decimal-precision floating point), `str` (Unicode string), `date` (date only), `utcdatetime` (UTC date+time), `timeOfDay` (seconds since midnight as integer), `boolean`, `enum`, `guid`, and `anytype`. Unlike standard IEEE-754 binary floating point used in many languages, X++'s `real` type uses **decimal-like precision** internally. This makes it safe for monetary values — EDTs like `AmountMST` use `real` without the rounding errors you'd see with `double` in other languages.

> **Definition:** A **primitive type** is a built-in scalar type provided by the language runtime — it has no internal structure and represents a single value. In X++, `int`, `real`, `str`, `date`, `utcdatetime`, `enum`, `boolean`, `guid`, `int64`, and `timeOfDay` are primitives. `container` and `array` are composite types. `record` (table buffer) and `class` (object reference) are language constructs, not primitive types.

#### Extended Data Types (EDTs) — Domain-Driven Design in Practice
An **EDT (Extended Data Type)** is a **type alias** that wraps a primitive type with additional metadata: `StringSize`, `Alignment`, `FormHelp`, `Label`, `HelpText`, **Field Relations** (foreign key to another table), **Enum Values** (for enum-based EDTs), and **Validation Rules**. EDTs enforce consistency — every `CustAccount` field across all tables uses the same EDT, so they all have the same length, label, and lookup behavior. This is domain-driven design: the **business concept** (Customer Account) is defined once as an EDT and reused everywhere.

> **Layman's explanation:** An EDT is like a "field template." Instead of saying "this field is a string of length 20" fifty times, you say "this field is a `CustAccount`." The EDT carries all the rules: max length 20, shows a customer lookup, label is "Customer Account," and it relates to the `CustTable`. Change the EDT once, and every field using it updates automatically.

#### Table Storage Types — Regular, TempDB, InMemory
Every table in D365 F&O has a `TableType` property with three options:

| Storage Type | Where Data Lives | Lifetime | Use Case |
|---|---|---|---|
| **Regular** (default) | SQL Server database | Permanent | Business data — customers, orders, invoices |
| **TempDB** | SQL Server `tempdb` | Per-session / per-transaction | Large intermediate datasets, staging, batch processing |
| **InMemory** | AOS memory (RAM) | Per-session | Small lookup tables, session-specific settings, < 1000 rows |

**Key distinction:** `TempDB` tables write to SQL `tempdb` — they support indexes, statistics, and can handle millions of rows. `InMemory` tables live entirely in AOS memory — faster for tiny datasets but no SQL indexes, and they can cause memory pressure if abused.

> **Definition:** **TableType** is a table property that determines physical storage. Regular = persistent SQL table. TempDB = SQL tempdb table (supports indexes, large volumes). InMemory = AOS memory only (no SQL, fast for small data, no indexes).

#### Data Operations — Framework Write Path vs. Bypass Methods
When you call `table.insert()`, `table.update()`, or `table.delete()`, the **framework write path** executes: `validateWrite()` / `validateDelete()` → database operation → `inserted()` / `updated()` / `deleted()` events → business logic. This is the **correct path** — it enforces validation, fires events, and maintains data integrity.

**Bypass methods** (`doInsert()`, `doUpdate()`, `doDelete()`) skip validation, skip events, and go straight to SQL. Use them **only** in these scenarios:
- Data migration / initialization scripts where you control the data quality
- Performance-critical bulk operations inside a transaction where you've already validated
- Unit test setup/teardown where speed matters more than events

> **Definition:** The **framework write path** is the standard sequence of method calls and events that execute when you use `insert()`, `update()`, `delete()` on a table buffer. **Bypass methods** (`doInsert`, `doUpdate`, `doDelete`) skip this path and execute SQL directly — they are escape hatches, not standard practice.

#### SQL Concepts Every X++ Developer Must Know
Even though you write X++, the AOS translates it to SQL. Understanding the translation helps you write performant code:

| Concept | What It Means in X++ |
|---|---|
| **Inner Join** | `join` keyword in `while select` — only returns rows where both tables have matching records |
| **Outer Join** | `outer join` — returns all rows from the left table, matching rows from the right (nulls where no match) |
| **Exists Join** | `exists join` — returns left table rows only if at least one matching right row exists (no right table fields in result) |
| **Cardinality** | One-to-many (parent → child) is the norm. Many-to-many requires a junction table. |
| **View** | A virtual table defined by a query — read-only or updatable projection of multiple tables |
| **Index / Alternate Key** | Non-clustered unique constraint (`AlternateKey` property) — enables fast lookups on non-RecId fields |

> **Layman's explanation:** Every `while select` you write becomes a SQL query. If you write `while select custTable join vendTable`, you're telling SQL "give me customers AND their vendors in one query." If you instead write a `while select custTable` and inside the loop do `select vendTable`, you're making SQL run a separate query for *every customer* — that's the N+1 problem. Always think: "How many round-trips to SQL am I making?"

#### Composite Collections — List, Set, Map, Struct
X++ provides four collection classes in the `System.Collections` namespace (not containers):

| Collection | Characteristics | When to Use |
|---|---|---|
| **List** | Ordered, allows duplicates, index-based access (`get(index)`) | Ordered sequences, stacks, queues |
| **Set** | Unordered, unique elements only, fast `in()` check | Deduplication, membership testing |
| **Map** | Key-value pairs, unique keys, fast lookup by key | Caching, dictionaries, lookups by ID |
| **Struct** | Fixed schema, named fields, like a lightweight record | Passing structured data between methods |

These are **reference types** (class instances) — declare with `List list = new List(Types::Integer);` not `List list;`.

> **Definition:** **Composite collections** are class-based data structures (`List`, `Set`, `Map`, `Struct`) that provide richer behavior than the built-in `container` type. They support type safety, dynamic sizing, and standard algorithms (sort, filter, find). `container` is a lightweight value type; collections are reference types with methods.

---

### 3.2.3 Design Principles Summary

| Principle | What It Means | Why It Matters |
|---|---|---|
| **Use EDTs for domain modeling** | Define business concepts once as EDTs, reuse everywhere | Consistency, maintainability, single source of truth |
| **Avoid bypass methods** | Use `insert()`/`update()`/`delete()` unless you have a specific reason | Validation, events, data integrity, audit trail |
| **Use TempDB for large temp data** | Large intermediate results go in TempDB tables | SQL indexes, statistics, handles millions of rows |
| **Think in SQL round-trips** | Every `select` = one round-trip; `while select` = one query, streamed | Performance, scalability, avoid N+1 |
| **Extensibility first** | Table extensions, CoC, event handlers — never modify `SYS` layer directly | Survives Microsoft updates, supported pattern |

---

# Chapter 4: LCS & Dev Lifecycle

## 4.1 LCS (Lifecycle Services) — The Orchestration Platform

### 4.1.1 What Is LCS?

LCS (Lifecycle Services) is a **cloud-based application lifecycle management portal** provided by Microsoft as part of the Microsoft Dynamics 365 platform. It is the central hub for:

- **Environment management** — creating, configuring, and monitoring Azure-hosted environments
- **Build and deployment** — CI/CD pipelines that compile models and deploy them across environments
- **Monitoring and diagnostics** — real-time performance monitoring, SQL query profiling, and Infolog monitoring
- **Release management** — structured promotion of builds from Dev → Test → UAT → Production
- **Change tracking** — tracking all model deployments and configuration changes for audit purposes
- **Reporting** — built-in reports on deployment success/failure, performance, and compliance

### 4.1.2 LCS Environments — Detailed Overview

| Environment | Purpose | Data Source | AOS Tier | Who Has Access | When Updated |
|---|---|---|---|---|---|
| **Dev/Test** | Active development, code compilation, unit testing | Synthetic or demo data (no production data) | Shared development AOS | Developers, QA engineers | Continuous — on every build |
| **Build** | Automated build execution — compiles models, produces `.axmodel` artifacts from build pipeline | N/A (build artifacts only) | Ephemeral — exists only during the build | Automated (Azure DevOps pipeline agent) | Triggered by source code commit or manual build request |
| **Test** | Integration testing, functional testing by QA | Production data snapshot (refreshed periodically) | Shared test AOS | QA engineers, business analysts | After Dev/Test is validated |
| **UAT** | User Acceptance Testing — business users validate changes before production | Production data snapshot | Dedicated UAT AOS | Business stakeholders, business users | After Test is passed |
| **Preview** (optional) | Preview of upcoming CUs and hotfixes for testing | Standard data with CU applied | Dedicated preview AOS | ITOps, developers, early adopters | When Microsoft releases a CU |
| **Production** | Live business operations | Live transactional data | Production AOS (high-availability, redundant) | IT Operations, limited developer access during deployments | Only after formal release management approval |

### 4.1.3 Azure DevOps Build Pipeline — The Build Process

The standard build pipeline in D365 F&O development follows this structure (Azure DevOps YAML or classic editor):

```yaml
# Simplified build pipeline structure
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'windows-latest'   # Must match the LCS environment's agent specification

variables:
  - group: 'd365-fao-variables'  # Azure DevOps variable group with LCS credentials
  - name: lcsEnvironmentId      # The LCS environment ID for the build target
  - name: modelName             # The model name in ModelManifest.xml

steps:
  - task: Dynamics365Setup@1    # Step 1: Install the Dynamics 365 Build Tools
    inputs:
      version: '10.0.xxxx.x'   # Version must match the LCS environment

  - task: Dynamics365Build@2    # Step 2: Restore NuGet packages and compile X++
    inputs:
      solution: '**/*.sln'      # The Visual Studio solution file
      project: '$(modelName)'   # The specific model project
      configuration: 'Release'

  - task: Dynamics365Package@3  # Step 3: Create the .axmodel package
    inputs:
      projectPath: '$(Build.SourcesDirectory)/$(modelName)'
      outputPath: '$(Build.ArtifactStagingDirectory)'

  - task: PublishBuildArtifacts@4  # Step 4: Publish as a build artifact
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'drop'

  - task: Dynamics365Deploy@5   # Step 5 (optional): Deploy to Test environment automatically
    inputs:
      lcsConnection: 'LCS Service Connection'
      environmentId: '$(testEnvironmentId)'
      packagePath: '$(Build.ArtifactStagingDirectory)/$(ModelName).axmodel'
```

**Build pipeline stages in detail:**
1. **Restore**: Downloads NuGet packages that the project depends on (Dynamics SDK assemblies, etc.)
2. **Compile**: Invokes the X++ compiler (`AxBuild.exe`) which reads `.xpp` files from the model store and produces `.dll` IL assemblies
3. **Package**: Creates the `.axmodel` binary file containing all metadata + compiled binaries
4. **Publish**: Makes the artifact available for download or for the next pipeline stage
5. **Deploy** (optional): Uses the LCS API to deploy the artifact directly to a target environment — this step requires a valid Azure Service Principal with LCS deployment permissions

**What the X++.compiler does under the hood:**
- Parses every `.xpp` source file in the project
- Resolves all type references (EDTs, enums, classes, tables) against the model store
- Performs static analysis (type checking, unused variable detection, method signature validation)
- Generates IL bytecode
- Generates `.log` files with any compilation errors or warnings
- Fails the build if any compilation errors exist — the `.axmodel` is not produced

### 4.1.4 LCS Release Pipeline — Promoting Builds

The release pipeline in LCS (accessible via the LCS web portal at `lcs.dynamics.com`) manages the movement of your `.axmodel` build artifacts across environments:

1. **Source stage**: The build artifact from the Azure DevOps pipeline is ingested into LCS
2. **Stage gates**: You can define manual approval gates between environments (e.g., "UAT lead must approve before Production deployment")
3. **Deployment to each stage**:
   - LCS copies the `.axmodel` to the target environment's model store (Azure File Share)
   - The AOS on that environment detects the new model
   - On the next AOS recycle (automatic or manual), the model loads into memory
   - The deployment status is reported back to LCS
4. **Rollback**: If a deployment fails, LCS allows rolling back to the previous model version (stored in the model store as a previous version folder — see `C:\Views` structure above)

### 4.1.5 Hotfix Deployment

When Microsoft releases a Critical Update (CU) or hotfix:
1. The update arrives as a `.axupdate` file package in LCS
2. **IT Operations** applies the `.axupdate` via the LCS environment page
3. The update is applied to the `SYS` layer — **not** to `CUS`, `ISV`, or `VAR`
4. The AOS is recycled to load the updated model store
5. **Your custom code in `CUS`** is unaffected because it was applied after the standard code and takes precedence in the layer resolution order

**Critical best practice**: After any hotfix deployment, redeploy your custom model to ensure it is still compatible with the updated standard code. Microsoft may have changed a method signature or behavior that your CoC override or event handler depends on.

### 4.1.6 Configuration Keys

A **Configuration Key** is a boolean flag that controls whether a feature in D365 F&O is active or inactive. Configuration keys are defined in the model store and referenced in code.

**Standard keys:**
| Configuration Key | Purpose | Default |
|---|---|---|
| `#ISO` | Internationalization features (multi-currency, multi-language, country-specific tax) | On for most deployments |
| `USMF` | The default demonstration company — always active in USMF demo data environments | On |
| `GeneralLedger` | GL module features | On for deployments with the GL module |
| `AccountsPayable` | AP module features | On for deployments with AP |
| `InventoryManagement` | Inventory module features | On for deployments with Inventory |

**Custom configuration keys (for your model):**
When your model introduces a feature that should be toggleable (e.g., a custom compliance validation that is not ready for all users), create a custom configuration key in `ModelManifest.xml` and gate your code with it:

```xpp
// In your class or table validateWrite()
if (FeatureEnabled::isEnabled(featureNum(MyCustomCompliancceFeature)))
{
    // Custom validation logic here
    ...
}
```

The `FeatureEnabled::isEnabled()` check uses the `SysFeatureElement` table to determine at runtime whether the feature is active for the current user/company context.

---

## 4.2 The Development Lifecycle — Step by Step in Detail

### 4.2.1 Developer Workflow (Day-to-Day)

```
[1] Open Visual Studio → Connect to LCS Dev/Test environment
    │
[2] Synchronize AOT and open your model project
    │
[3] Write X++ code (tables, classes, forms, etc.)
    │
[4] Build the project (Ctrl+F6 or right-click → Build Solution)
    │   ├── Success → .axmodel artifact produced
    │   └── Failure → compilation errors → fix and rebuild
    │
[5] Deploy to the Dev/Test environment (right-click project → Deploy)
    │   ├── LCS uploads the .axmodel to the model store
    │   └── AOS on the environment detects the new model
    │
[6] Test manually in the D365 F&O client
    │   ├── Open forms, run the new code
    │   ├── Check the Infolog for errors
    │   └── Set breakpoints in Visual Studio → trigger the code → step through
    │
[7] Repeat steps 3–6 until the feature works correctly
    │
[8] Commit the solution to version control (Git, TFS, or Azure Repos)
    │
[9] Push the build to the Azure DevOps CI pipeline
    │   └── The pipeline runs automated unit tests (from Chapter 12)
    │
[10] Promote the build to Test → UAT → Production via the release pipeline
```

### 4.2.2 Debugging in D365 F&O

Breakpoint debugging works from Visual Studio when connected to a Dev/Test environment:

1. Set a breakpoint in an X++ method in Visual Studio (click the left margin or press `F9`)
2. Start the D365 F&O client from the connected environment (or use the Dynamics 365 client already open)
3. Trigger the code path (click a button, run a menu item, etc.)
4. Visual Studio breaks execution at the breakpoint — you can step through (`F10`/`F11`), inspect variable values, and view the call stack
5. Use `F5` to continue execution to the next breakpoint
6. The Infolog updates in real-time as `info()`, `error()`, and `warning()` calls execute

**Important debugging notes:**
- Breakpoints only work when the Visual Studio debugger is attached to the AOS — the default "Connect" mode in Visual Studio handles this attachment automatically
- Breakpoints on code that is not yet deployed to the environment will show as hollow (unbound) — deploy first, then set breakpoints on the deployed version
- Set breakpoints on `init()`, `executeQuery()`, `validateWrite()`, `modified()`, and `run()` methods — these are the most commonly debugged methods in form-based development
- `Global::info()` output appears in Visual Studio's Debug Output window in addition to the Infolog — this is useful for tracing logic execution flow without cluttering the Infolog

### 4.2.3 The Complete Build → Deploy → Promote Cycle

| Step | Environment | Action | Who Triggers |
|---|---|---|---|
| 1 | Dev/Test (local) | Developer writes code in Visual Studio | Developer |
| 2 | Dev/Test (local) | Developer builds and deploys for testing | Developer |
| 3 | CI Pipeline | Azure DevOps runs the build, compiles, packages | Automated (triggered by Git commit) |
| 4 | Test | CI pipeline deploys the `.axmodel` to Test environment | Automated |
| 5 | Test | QA runs manual and automated tests | QA |
| 6 | Staging gate | QA lead approves promotion to UAT | QA Lead |
| 7 | Release Pipeline | LCS promotes build to UAT | Release manager |
| 8 | UAT | Business users validate the feature | Business Users |
| 9 | Production gate | Business lead approves promotion to Production | Business Lead |
| 10 | Release Pipeline | LCS promotes build to Production | Release manager |
| 11 | Production | IT Operations monitors for issues | IT Operations |

---

## 4.3 Activity — Layer & AOT Decision Exercise

> **Scenario**: Acme Manufacturing needs to customize the Accounts Payable invoice approval workflow. The requirements are:
> 1. Add a new field to `VendTable` for an internal compliance approval code
> 2. Create a new form to display vendor compliance history
> 3. Modify the standard AP invoice validation to require the compliance code when the vendor's credit limit exceeds $500,000
> 4. Add a menu item to navigate to the new compliance form
> 5. Create a security role for compliance officers
> 6. Generate a monthly compliance report from the AP module
> 7. Provide a data entity to push compliance data to an external audit system
>
> For each requirement, identify:
> - **Which AOT node(s)** you would create or modify
> - **Which layer** you would place each object in and **why**
> - **Any potential conflicts** with standard D365 F&O objects or future Microsoft updates
> - **The correct `ModelName`** in `ModelManifest.xml` and its dependency order
> - **Which Microsoft documentation page** you would consult to verify the standard implementation before customizing

### Hints — Multiple Valid Approaches Exist

- **Hint A for requirement #1 — Adding a vendor compliance field**: The choice is between modifying `VendTable` directly (adding a field to the base table) or using a **table extension**. 
  - **Approach A1 (Table Extension — Recommended)**: `[ExtensionOf(tableStr(VendTable))] final class VendTable_Extension { ComplianceCode complianceCode; }`. This survives Microsoft hotfixes because the extension lives in the `CUS` layer (higher than `SYS`) and is never overwritten by Microsoft updates. The extension is also easier to maintain because Microsoft can change the base `VendTable` without affecting your extension. **This is the approach documented by Microsoft for customer customizations.**
  - **Approach A2 (Direct Modification — NOT Recommended)**: Modifying the base `VendTable` in the AOT directly. This **will** be overwritten by the next Microsoft CU because Microsoft's CU applies changes to the `SYS` layer, which has higher update precedence than a naive base modification (the resolution algorithm prefers the highest-layer object, and if your modification is considered part of a lower layer, it gets overwritten). **Microsoft explicitly advises against this pattern.**

- **Hint B for requirement #3 — Modifying AP invoice validation**: The choice is between a **Chain of Command** override of `VendInvoiceJour.validateWrite()` and an **event handler** subscription.
  - **Approach B1 (CoC Override — Recommended for Table Method Overrides)**: Create a class that extends `VendInvoiceJour` (or override the method directly via CoC) and override `validateWrite()` to insert your compliance check. CoC is the most straightforward mechanism for overriding standard table methods — it is well-documented and has clear developer tooling support (the AOT shows the override method explicitly). **Use CoC when you need to change the behavior of a standard method called directly (not an event).**
  - **Approach B2 (Event Handler — Recommended When Multiple Extensions Need to React)**: Subscribe to the `VendInvoiceJour.validateWrite` event using `[SubscribesTo(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]`. This is better when multiple independent solutions need to react to the same event — each subscribes independently without interfering with others. The trade-off is that event handler execution order is less predictable than CoC (which has an explicit chain), so **use event handlers for cross-cutting concerns** like integration triggers, audit logging, or notification dispatch rather than for core business rule enforcement.

- **Hint C for requirement #5 — Security role design**: A compliance officer in this scenario needs access to specific data across multiple tables.
  - **Approach C1 (Role with Privileges → Duties)**: Create a duty (e.g., `APComplianceViewer`) that contains privileges for reading `VendTable`, reading `VendInvoiceJour`, and writing to the new compliance form. Create a role and assign the duty. This follows the standard D365 F&O security model hierarchy: Permission → Privilege (composed of permissions) → Duty (composed of privileges) → Role (composed of duties) → User (assigned one or more roles). **This is the documented Microsoft approach.**
  - **Approach C2 (Role with Field-Level Permissions)**: In addition to table-level access, create field-level permissions that restrict the compliance role to only see the compliance-related fields on `VendTable` and `VendInvoiceJour` — this follows the principle of least privilege and is important for compliance-sensitive data. This uses the `SecurityPermissionSet` property on each privilege to limit access to specific `FieldId` values.

- **Hint D for requirement #6 — SSRS Report**: 
  - **Approach D1 (SSRS Report Wizard in Visual Studio)**: Use the SSRS Report Designer in Visual Studio, define a dataset using a `SrsReportDataProvider` class that contains the query, and design the report layout using the auto-design feature. This is the quickest way to build a functional report but may produce a less polished layout.
  - **Approach D2 (External RDL Design)**: Design the RDL file externally in Report Builder or SQL Server Data Tools, then import it into the D365 F&O project. This gives full control over layout and formatting but requires more effort to wire up the data source and parameters. **Microsoft docs recommend approach D1 for initial development and approach D2 for production reports requiring pixel-perfect layouts.**

### Expected Approach — Ideal Solution in Detail

The ideal approach for this activity combines all recommended patterns and follows Microsoft's documentation conventions:

#### Requirement 1: Compliance Code Field on VendTable
- **Object Type**: Table Extension
- **AOT Node**: `Extensions\Tables\VendTable`
- **Layer**: `CUS`
- **AOT Code**:
  ```xpp
  [ExtensionOf(tableStr(VendTable))]
  final class VendTable_ComplianceCode_Extension
  {
      ComplianceCode complianceCode;
      // ComplianceCode is an EDT — string 20, mandatory = No, label = "Compliance Code"
  }
  ```
- **Microsoft Docs Reference**: [Table extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/extended-classes) — confirms table extension is the supported pattern for adding fields to base tables
- **Why not modify VendTable directly**: Microsoft explicitly states that modifying base tables is unsupported for customer code and will cause upgrade conflicts

#### Requirement 2: Compliance History Form
- **Object Type**: New Form (`MenuItemDisplay` to navigate)
- **AOT Node**: `Forms\ComplianceHistoryForm`
- **Layer**: `CUS`
- **Design**: `Form` frame type with two data sources — `VendTable` (primary) and `APComplianceLog` (secondary, joined on `VendTable.RecId = APComplianceLog.VendTableRecId`)
- **`ModelManifest.xml` dependency**: Must reference `ApplicationSuite` (for `VendTable`)

#### Requirement 3: AP Invoice Validation Override
- **Object Type**: CoC Override on `VendInvoiceJour.validateWrite()`
- **AOT Node**: `Classes\VendInvoiceJour_ComplianceValidate` (extension class, not override class)
- **Layer**: `CUS`
- **AOT Code**:
  ```xpp
  [ExtensionOf(formStr(VendInvoiceJour))]
  final class VendInvoiceJour_ComplianceExtension
  {
      // Method hook that intercepts the validateWrite call
      // ... CoC implementation that validates compliance code for high-credit vendors
  }
  ```
  *Alternative using Pre-Event Handler:*
  ```xpp
  [PreHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
  public static void VendInvoiceJour_onValidateWrite(XppPrePostArgs _args)
  {
      VendInvoiceJour vendInvoiceJour = _args.getThis();

      if (vendInvoiceJour.creditMax > 500000 && vendInvoiceJour.ComplianceCode == '')
      {
          _args.setReturnValue(checkFailed('Compliance code required for vendors exceeding $500,000 credit limit'));
      }
  }
  ```
- **Note**: The CoC approach is more explicit and easier to debug; the event handler approach allows multiple subscribers. For this scenario, CoC is the recommended approach since it is a core business rule modification with a single owner.

#### Requirement 4: Menu Item
- **Object Type**: `MenuItemDisplay`
- **AOT Node**: `MenuItems\Display\ComplianceHistory`
- **Object Property**: `ApplicationObject = ComplianceHistoryForm`
- **Layer**: `CUS`
- Added to the AP **Menu** or as a standalone navigation item in the workspace

#### Requirement 5: Security Role for Compliance Officers
- **Object Type**: Security Role (with Duties, Privileges, Permissions)
- **AOT Node**: `Security\Roles\ComplianceOfficerRole`
- **Duty**: `APComplianceDuty` → contains `APComplianceViewer` privilege (read on `VendTable`, `VendInvoiceJour`, `APComplianceLog`, write on `APComplianceLog` for submitting declarations)
- **Field-level permissions**: Compliance officers can see the `ComplianceCode` field on `VendTable` and all fields on `APComplianceLog`; other users cannot
- **PermissionSet**: The role is assigned to the security role assignment record in the user administration form
- **Microsoft Docs Reference**: [Security roles](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/security-operations/) — confirms the hierarchy: Permission → Privilege (composed of permissions) → Duty (composed of privileges) → Role (composed of duties) → User (assigned one or more roles)

#### Requirement 6: Monthly Compliance Report (SSRS)
- **Object Type**: SSRS Report + `SrsReportDataProvider` class
- **AOT Node**: `Reports\ComplianceSummaryReport` + `Classes\VendComplianceReportDP`
- **Data Provider**: `VendComplianceReportDP` extends `SrsReportDataProvider` — contains the SSRS query joining `VendTable`, `VendInvoiceJour`, `APComplianceLog`, and `VendInvoiceLine`
- **Parameters**: Date range (`fromDate`, `toDate`), vendor group (`CustGroup`), compliance status (`Validated`, `Pending`, `Failed`)
- **Report layout**: AutoDesign initially, then manual RDL for production
- **Menu item**: `MenuItemOutput` linked to the report class
- **Microsoft Docs Reference**: [SSRS reports in D365 F&O](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-reporting/) — confirms the `SrsReportDataProvider` pattern

#### Requirement 7: Data Entity for External Audit Integration
- **Object Type**: Data Entity (`DataEntity`)
- **AOT Node**: `Data Entities\VendAPComplianceEntity`
- **Structure**: 
  - Staging table fields (intermediate state) stored in `VendAPComplianceStaging`
  - Output fields exposed via `IsPublic`, `Public Entity Name`, and `Public Collection Name` properties
  - `Link` field: connects `APComplianceLog` to the entity context (`VendTable.RecId`)
- **Staging pattern**: Uses a staging table (`VendAPComplianceStaging`) that accumulates records, validates them, and then pushes them to the target system via a custom `.NET` or `Logic App` integration
- **Microsoft Docs Reference**: [Data entities](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities-intro) — confirms the staging + entity pattern for integration scenarios

#### Model Manifest & Dependencies
```xml
<ModelManifest>
  <Name>AcmeAPComplianceModel</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeAPComplianceEnabled</ConfigurationKey>
</ModelManifest>
```

---
---


Before you can work with tables, forms, or data entities, you need to be fluent in X++ itself — the language that runs on the Application Object Server. This chapter covers the language fundamentals and the object-oriented patterns you'll use every day.

# Chapter 5: X++ Data Types & Variables

## 5.1 X++ Data Types

X++ has a set of primitive data types and a rich system of Extended Data Types (EDTs) that wrap primitives with additional metadata.

### Primitive Data Types

| Type | Description | Example |
|---|---|---|
| `int` | 32-bit signed integer | `int i = 42;` |
| `int64` | 64-bit signed integer | `int64 recId = 5637144576;` |
| `real` | Fixed-point decimal-like precision (not IEEE-754) | `real price = 19.99;` |
| `str` | Unicode string | `str name = "Customer";` |
| `boolean` | true / false | `boolean isValid = true;` |
| `date` | Date (no time component) | `date d = today();` |
| `utcdatetime` | Date and time in UTC | `utcdatetime udt = DateTimeUtil::utcNow();` |
| `timeOfDay` | Seconds since midnight | `timeOfDay t = 120000;` |
| `guid` | Globally unique identifier | `guid g = Guid::newGuid();` |
| `enum` | Named constant set | `Status::New` |
| `AnyType` | Universal type | `AnyType val = 42;` |

### Type Casting

```xpp
// Explicit casting from container to specific types
container c = [1, "hello", 3.14];
int     i = conPeek(c, 1);       // 1
str     s = conPeek(c, 2);       // "hello"
real    r = conPeek(c, 3);       // 3.14

// Casting between record types (must be compatible table types)
CustTable custTable = CustTable::find("CUST-001");
VendTable vendTable = custTable;  // Compile error — incompatible types
```

### `AnyType` — The Universal Type

`AnyType` can hold any X++ type. It is used extensively in framework code (e.g., `SysOperationServiceController`, `RunBase`). Use `conPeek` and `conLen` to work with `AnyType` containers.

```xpp
AnyType anyValue = 42;
// You must know the actual type at runtime to use it safely
if (anyValue is int)
{
    int i = anyValue;
    info(strFmt("The value is %1", i));
}
```

## 5.2 Variable Declaration and Scope

### Declaration Keywords

| Keyword | Scope | Lifetime |
|---|---|---|
| `static` | Class-level | Persists for the lifetime of the application |
| `const` | Class-level | Immutable after initialization |
| Instance variable | Object-level | Persists for the lifetime of the object |
| Local variable | Method/block | Created on entry, destroyed on exit |

### Declaration Rules

```xpp
class MyClass
{
    // Static constant — class-level, immutable
    static const Str AppName = "MyApp";

    // Static variable — shared across all instances
    static int instanceCount = 0;

    // Instance variable — each object has its own copy
    CustTable _custTable;
    boolean   _isValid;

    public void myMethod()
    {
        // Local variable — only visible in this method
        int localVar = 10;

        // Block-scoped variable (inside if/for/while)
        if (localVar > 0)
        {
            str blockVar = "visible only here";
            info(blockVar);
        }
        // blockVar is NOT accessible here — compile error
    }
}
```

**Important**: X++ **does** support block-level scoping for variables. A variable declared inside a block (e.g., `if`, `for`, `while`) is only accessible within that block. This is similar to Java.

```xpp
// CORRECT — X++ supports block-scoped variables
public void goodExample()
{
    if (true)
    {
        int x = 5;  // x is only visible inside this block
        info(strFmt("x = %1", x));
    }
    // x is NOT accessible here — it's a compile error
    // because x was declared inside the if block
}
```

**Source:** [X++ variables - Declare anywhere](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-variables-data-types#declare-anywhere)

# Chapter 6: Control Flow & CRUD

## 6.1 Control Flow Statements

### If / Else If / Else

```xpp
int score = 85;

if (score >= 90)
{
    info("Grade: A");
}
else if (score >= 80)
{
    info("Grade: B");    // This branch executes
}
else if (score >= 70)
{
    info("Grade: C");
}
else
{
    info("Grade: F");
}
```

### Switch

X++ `switch` supports `int`, `str`, and `enum` types. Unlike Java, there is no `case` fall-through — each case must end with `break` or `return`.

```xpp
Status orderStatus = Status::Approved;

switch (orderStatus)
{
    case Status::New:
        info("Order is new");
        break;

    case Status::Approved:
        info("Order is approved");
        break;

    case Status::Rejected:
        info("Order is rejected");
        break;

    default:
        info("Unknown status");
        break;
}
```

### For Loop

```xpp
// Standard for loop
for (int i = 1; i <= 10; i++)
{
    info(strFmt("Iteration %1", i));
}

// Iterating over a container
container numbers = [10, 20, 30, 40, 50];
for (int i = 1; i <= conLen(numbers); i++)
{
    info(strFmt("Element %1 = %2", i, conPeek(numbers, i)));
}
```

### While Select — The X++ Iteration Pattern

`while select` is the most idiomatic way to iterate over table records in X++. It combines a SQL `SELECT` with a `while` loop — the AOS generates efficient SQL and streams records one at a time.

```xpp
// Basic while select
CustTable custTable;
while select custTable
{
    info(custTable.AccountNum);
}

// while select with a where clause
while select custTable
    where custTable.Currency == "USD"
{
    info(custTable.AccountNum);
}

// while select with ordering
while select custTable
    order by custTable.AccountNum
{
    info(custTable.AccountNum);
}

// while select with firstonly — stops after the first match
while select firstonly custTable
    where custTable.AccountNum == "CUST-001"
{
    info(custTable.Name);
}
```

**Performance note**: `while select` is far more efficient than a `for` loop with individual `select` statements. Each individual `select` generates a separate SQL round-trip; `while select` streams results from a single query.

### Do While

```xpp
int i = 1;
do
{
    info(strFmt("Value: %1", i));
    i++;
}
while (i <= 5);
```

## 6.2 Table Operations (CRUD)

### Select

```xpp
CustTable custTable;

// Simple select — retrieves all records
while select custTable
{
    info(custTable.AccountNum);
}

// Select with a where clause
while select custTable
    where custTable.AccountNum == "CUST-001"
{
    info(custTable.Name);
}

// Select firstonly — optimized; stops after first match
select firstonly custTable
    where custTable.AccountNum == "CUST-001";

// Select specific fields only — reduces SQL payload
while select custTable.Name, custTable.Phone()
{
    info(strFmt("%1 — %2", custTable.AccountNum, custTable.Name));
}

// exists join — check for related records without retrieving them
VendTable vendTable;
boolean hasVendor = exists join vendTable
    where vendTable.AccountNum == custTable.AccountNum;
```

### Insert

```xpp
CustTable custTable;
custTable.clear();                    // Clear all fields to defaults
custTable.AccountNum = "CUST-NEW-001";
custTable.Name = "New Customer";
custTable.Phone = "+1-555-0100";
custTable.Currency = "USD";
custTable.insert();                   // Writes to the database
```

### Update — `update_recordset`

`update_recordset` is the preferred X++ pattern for updating records. It generates a single SQL `UPDATE` statement — much more efficient than selecting a record, modifying it, and calling `.update()` in a loop.

```xpp
// Update a single record
CustTable custTable;
update_recordset custTable
    setting custTable.Phone = "+1-555-0200"
    where custTable.AccountNum == "CUST-NEW-001";

// Update multiple records at once — single SQL statement
CustTable custTable;
update_recordset custTable
    setting custTable.Currency = "EUR"
    where custTable.Currency == "USD";
```

### Delete — `delete_from`

```xpp
// Delete a single record
CustTable custTable;
delete_from custTable
    where custTable.AccountNum == "CUST-TO-DELETE";

// Delete multiple records
CustTable custTable;
delete_from custTable
    where custTable.Currency == "EUR" && custTable.GroupName == "TEMP";
```

### Transactions (`ttsBegin` / `ttsCommit` / `ttsAbort`)

All database modifications within a transaction are atomic — either all succeed or all are rolled back.

```xpp
ttsBegin;
try
{
    CustTable custTable;
    custTable.clear();
    custTable.AccountNum = "CUST-TRANS-001";
    custTable.Name = "Transactional Customer";
    custTable.insert();

    // Related record in another table
    CustGroup custGroup;
    custGroup.clear();
    custGroup.GroupName = "TRANSACTIONAL";
    custGroup.insert();

    ttsCommit;  // Both inserts succeed — commit the transaction
}
catch (Exception::Error)
{
    ttsAbort;   // Something failed — roll back everything
    error("Transaction failed — all changes rolled back.");
}
```

**Critical rule**: Always call `super()` first in table `insert()`, `update()`, and `delete()` methods, and in `validateWrite()` / `validateDelete()`. The base class methods handle framework-level logic (workflow, auditing, etc.) that your code depends on.

# Chapter 7: Methods, Exceptions, Classes

## 7.1 Method Overriding and `super()`

X++ supports method overriding through inheritance. When a subclass overrides a base class method, it can call the base implementation using `super()`.

### Overriding in Tables

```xpp
// In a table — overriding validateWrite
public boolean validateWrite()
{
    boolean ret;

    ret = super();  // Always call super() first in table methods

    // Custom validation — runs AFTER the base validation
    if (this.AccountNum == "")
    {
        ret = checkFailed("Account number cannot be empty.");
    }

    return ret;
}
```

### Overriding in Classes

```xpp
// Base class
class BasePaymentService
{
    public void pay(CustTable _custTable, Amount _amount)
    {
        // Base implementation — process the payment
        info(strFmt("Processing payment of %1 for %2", _amount, _custTable.AccountNum));
    }
}

// Derived class — extends base payment logic
class CreditCardPaymentService extends BasePaymentService
{
    public void pay(CustTable _custTable, Amount _amount)
    {
        // Pre-processing
        this.validateCard();

        // Call base logic — the actual payment processing
        super::pay(_custTable, _amount);

        // Post-processing
        this.logTransaction();
    }

    private void validateCard()
    {
        // Card-specific validation
    }

    private void logTransaction()
    {
        // Log to a custom transaction table
    }
}
```

### The `next` Keyword — Chain of Command

When multiple extensions want to modify the same base method, the Chain of Command (CoC) pattern uses `next` to call the next handler in the chain. (Covered in depth in Chapter 7.)

```xpp
// In an extension class
[ExtensionOf(tableStr(CustTable))]
final class CustTable_Extension
{
    public boolean validateWrite()
    {
        boolean ret;

        ret = next validateWrite();  // Call the next handler in the chain (CoC `next` keyword)

        // Custom validation — use checkFailed() not error() to return false cleanly
        if (ret && this.AccountNum == "")
        {
            ret = checkFailed("Account number cannot be empty.");
        }

        return ret;
    }
}
```

## 7.2 Exception Handling

X++ uses a `try`/`catch` block with typed exceptions. The `Exception` enum defines the error categories.

### Exception Types

| Exception Type | When It Occurs |
|---|---|
| `Exception::Error` | General runtime error — the most common |
| `Exception::Warning` | Non-fatal warning — execution continues |
| `Exception::Info` | Informational message |
| `Exception::Broken` | Object is in an invalid state |
| `Exception::Deadlock` | SQL deadlock detected — retry the transaction |
| `Exception::DuplicateKey` | Unique index violation |

### Try / Catch Pattern

```xpp
try
{
    CustTable custTable;
    select firstonly custTable
        where custTable.AccountNum == "NON-EXISTENT";

    if (!custTable)
    {
        throw error("Customer not found.");
    }
}
catch (Exception::Error)
{
    error("An error occurred.");
}
catch (Exception::Warning)
{
    warning("A warning occurred.");
}
catch (Exception::Info)
{
    info("Informational message.");
}
```

### Deadlock Handling

Deadlocks are common in multi-user environments. The recommended pattern is to retry the transaction:

```xpp
int retryCount = 0;
boolean success = false;

while (!success && retryCount < 3)
{
    ttsBegin;
    try
    {
        // ... your database operations ...
        ttsCommit;
        success = true;
    }
    catch (Exception::Deadlock)
    {
        ttsAbort;
        retryCount++;
        info(strFmt("Deadlock detected — retry %1 of 3", retryCount));
    }
    catch (Exception::Error)
    {
        ttsAbort;
        error("A non-deadlock error occurred.");
        break;
    }
}
```

## 7.3 Classes and Objects

### 7.3.1 Class Structure

Every X++ class has three sections: **declarations** (class-level variables), **constructor(s)**, and **methods**.

```xpp
/// <summary>
/// Business logic class for customer validation.
/// </summary>
class CustValidationService
{
    // ── Class-level (static) variables ──
    static const Str MandatoryFieldMissing = "Mandatory field missing: ";

    // ── Instance variables ──
    CustTable _custTable;
    boolean   _isValid;

    // ── Constructor ──
    /// <summary>Initializes the service with a customer record.</summary>
    public CustValidationService(CustTable _custTable)
    {
        this._custTable = _custTable;
        this._isValid = false;
    }

    // ── Public methods ──

    /// <summary>Entry point — validates all rules and returns the result.</summary>
    public boolean validate()
    {
        if (this.validateAccountNum() && this.validateName())
        {
            this._isValid = true;
        }
        return this._isValid;
    }

    // ── Private helper methods ──

    /// <summary>Validates that the account number is not empty.</summary>
    private boolean validateAccountNum()
    {
        if (this._custTable.AccountNum == '')
        {
            error(strFmt(MandatoryFieldMissing, "Account number"));
            return false;
        }
        return true;
    }

    /// <summary>Validates that the customer name is not empty.</summary>
    private boolean validateName()
    {
        if (this._custTable.Name == '')
        {
            error(strFmt(MandatoryFieldMissing, "Name"));
            return false;
        }
        return true;
    }

    // ── Public static utility method ──

    public static boolean isAccountValid(str _accountNum)
    {
        return (_accountNum != '' && strLen(_accountNum) >= 3);
    }
}
```

**Using the class:**

```xpp
CustTable custTable = CustTable::find("CUST-001");
CustValidationService service = new CustValidationService(custTable);

if (service.validate())
{
    info("Customer is valid.");
}
else
{
    info("Customer validation failed — check the Infolog for details.");
}
```

### 7.3.2 Inheritance and Polymorphism

X++ supports single inheritance — a class can extend exactly one base class using the `extends` keyword.

```xpp
// Base class
class BasePaymentService
{
    /// <summary>Processes a payment. Designed to be overridden.</summary>
    public void pay(CustTable _custTable, Amount _amount)
    {
        info(strFmt("Processing payment of %1 for %2", _amount, _custTable.AccountNum));
    }
}

// Derived class — extends base payment logic
class CreditCardPaymentService extends BasePaymentService
{
    public void pay(CustTable _custTable, Amount _amount)
    {
        // Pre-processing
        this.validateCard();

        // Call base logic — the actual payment processing
        super::pay(_custTable, _amount);

        // Post-processing
        this.logTransaction();
    }

    private void validateCard()
    {
        // Card-specific validation
    }

    private void logTransaction()
    {
        // Log to a custom transaction table
    }
}
```

**Polymorphism in action** — a list of base-class references can hold derived objects:

```xpp
BasePaymentService paymentService;

// At runtime, the actual object type determines which pay() executes
paymentService = new CreditCardPaymentService();
paymentService.pay(custTable, 100.00);  // Calls CreditCardPaymentService::pay()
```

### 7.3.3 Abstract Classes and Interfaces

**Abstract classes** cannot be instantiated directly — they serve as blueprints for subclasses. They may contain both abstract (unimplemented) and concrete (implemented) methods.

**Interfaces** define a contract — a set of method signatures that implementing classes must provide. They enable polymorphism across unrelated class hierarchies.

```xpp
// Abstract class — cannot be instantiated directly
abstract class AbstractReportGenerator
{
    /// <summary>Abstract method — must be overridden by subclasses.</summary>
    public abstract void generate();

    /// <summary>Concrete method — shared logic available to all subclasses.</summary>
    public void logGeneration()
    {
        info("Report generation started.");
    }
}

// Concrete implementation
class SalesReportGenerator extends AbstractReportGenerator
{
    public void generate()
    {
        this.logGeneration();  // Inherited from abstract class
        // Sales report generation logic here
    }
}

// Interface — defines a contract without implementation
interface IExportable
{
    void exportToFile(str _filePath);
    str getExportFormat();
}

// A class can implement an interface AND extend a class
class CsvSalesReportGenerator extends AbstractReportGenerator implements IExportable
{
    public void generate()
    {
        this.logGeneration();
        // CSV-specific report logic
    }

    public void exportToFile(str _filePath)
    {
        // Write CSV to file
    }

    public str getExportFormat()
    {
        return "CSV";
    }
}
```

# Chapter 8: VS Development & Activity

## 8.1 Visual Studio Development Environment

> **Refresher** — detailed setup was covered in Chapter 1, Section 3.1. This section highlights the X++-specific development features.

- **IDE**: Visual Studio 2022 with the `Microsoft.Dynamics.FinOps.ToolsVS2022.vsix` extension
- **X++ Editor**: Syntax highlighting, IntelliSense for AOT objects, auto-completion for table fields and EDTs
- **Build**: MSBuild with custom X++ targets — compiles `.xpp` files to .NET CIL
- **Debugging**: Set breakpoints in X++ classes, step through code, inspect variables in the Locals/Watch windows
- **Cross-reference**: SQL Server Express LocalDB tracks object dependencies — right-click any element → **Find References**

## 8.2 Activity — Build a Customer Validation Service

> **Activity**: Create a class called `CustValidationService` that validates customer records before they are saved. The service must:
> 1. Accept a `CustTable` record in its constructor
> 2. Validate that `AccountNum` is not empty and is at least 3 characters long
> 3. Validate that `Name` is not empty
> 4. Validate that the `Currency` field is set to a valid currency (check against `CurrencyTable`)
> 5. Return a boolean from a `validate()` method and write error messages to the Infolog for each failed rule
> 6. Include a static method `isAccountNumValid(str _accountNum)` that can be called without instantiating the class
>
> **Hints** (no single approach — explore multiple paths):
> - **Hint A**: For the currency validation — should you use a `select firstonly` against `CurrencyTable`, or maintain a static list of valid currency codes? What are the trade-offs between accuracy (database lookup) and performance (static list)?
> - **Hint B**: Where should the error messages be generated — inside each private validation method, or collected in a list and reported at the end? Consider how the Infolog displays messages and whether the user needs to see all failures at once or just the first one.
> - **Hint C**: Should the `validate()` method call `super()`? In this case, there is no base class — but if you later extend `CustValidationService` with a subclass, what pattern should you follow for the `validate()` method?
>
> **Expected Approach (Ideal — in detail)**:
> 1. **Constructor**: Accepts `CustTable` and stores it in an instance variable. Initializes `_isValid = false`.
> 2. **`validate()`**: Calls each private validation method in sequence. If any returns `false`, `_isValid` stays `false`. Returns `_isValid`.
> 3. **`validateAccountNum()`**: Checks `AccountNum != ''` and `strLen(AccountNum) >= 3`. Uses `error()` to write to the Infolog. Returns `boolean`.
> 4. **`validateName()`**: Checks `Name != ''`. Uses `error()` to write to the Infolog. Returns `boolean`.
> 5. **`validateCurrency()`**: Uses `select firstonly CurrencyTable where CurrencyTable.CurrencyCode == this._custTable.Currency`. If no record is found, writes an error and returns `false`.
> 6. **`isAccountNumValid()`**: Static method — `return (_accountNum != '' && strLen(_accountNum) >= 3);`. No Infolog output; this is a pure validation function.
> 7. **Design note**: The class uses private helper methods for each validation rule, making it easy to add new rules later without modifying the `validate()` method. This follows the Open/Closed Principle.

---
---


# Chapter 9: Table Design & EDTs

## 9.1 Table Design — Foundational Principles

Every table in D365 F&O maps to a physical SQL table. Designing tables properly is the single most impactful decision you'll make — bad table design compounds into poor performance, upgrade conflicts, and data integrity issues.

### Table Properties — Key Properties

| Property | Description | Common Values |
|---|---|---|
| `Label` | User-facing display name (uses label files) | `'Customer Table'` |
| `HelpText` | Tooltip description | `'Contains customer account data'` |
| `TableGroup` | Logical grouping for form lookup display | `Customer`, `Vend`, `Master`, `Transaction` |
| `SaveDataPerCompany` | Whether each company's data is stored separately (`No = shared across companies`) | `No` or `Yes` |
| `AllowDuplicate` | Allow multiple records with the same key? | `No` (default) |
| `CacheLookup` | How SQL Server caches lookups of this table | `None`, `NotInTTS`, `Found`, `FoundAndEmpty`, `EntireTable` |
| `Replication` | Whether table data is replicated (for Azure SQL geo-replication) | `Enabled` or `Disabled` |
| `PrimaryIndex` | The primary index used for lookups | Typically `RecId`, or an alternate key |
| `DeleteActions` | What happens when a parent record is deleted | `Cascade`, `Restricted`, `None` |
| `TableType` | Normal vs. Temp vs. Word template | `Normal`, `TempDB`, `Temp`, etc. |

### Index Design — Critical for Performance

Indexes determine how fast `select`, `join`, and `exists` operations run. Every table has a primary index; adding secondary indexes is a key design decision.

| Index Type | Description | When to Use |
|---|---|---|
| **Primary Index** | Clustered index on `RecId` (auto-created) | Always present; do not change |
| **Alternate Index** | Non-clustered, unique constraint | When a natural key exists (e.g., `AccountNum` must be unique) |
| **Hash Index** | For equality-only lookups (no range scans) | When you only filter by equality (`where AccountNum == '...'`) |
| **Non-unique Index** | Allows duplicates; optimizes range scans and sorting | When you filter on a field that has many duplicates |
| **Group Level Index** | Multi-field index where the leading field determines selectivity | When queries always filter on the same leading field |

### Index Design Rules

1. **Leading field matters most** — in an index on `(FieldA, FieldB)`, SQL can use the index for `where FieldA = ...`, `where FieldA = ... AND FieldB = ...`, but NOT for `where FieldB = ...` alone
2. **Never index low-selectivity fields** as leading fields — indexing a boolean field (`true/false`) provides almost no benefit because SQL must scan anyway
3. **Use `AllowDuplicates = No`** on alternate uniqueness indexes — this enforces data integrity at the database level, not just at the application level
4. **`CacheLookup` matters** — tables with `CacheLookup = Found` or `FoundAndEmpty` allow SQL Server to cache lookups and skip disk reads; use this for lookup tables (e.g., `ItemGroup`, `CustGroup`)

## 9.2 Extended Data Types (EDTs) — Never Use Base Types Directly

An EDT is a type alias that wraps a base type (string, int, real, etc.) with additional properties. **Why EDTs matter:**

- **Consistency**: If `CustAccount` is a `string 20` EDT used on 50 tables, changing the EDT to `string 30` updates all 50 tables at once
- **Validation**: An EDT can have `StringSize`, `Mask`, `RegularExpression` validation rules
- **Relationships**: An EDT can be linked to another table (e.g., `CustAccount` EDT links to `CustTable`), enabling **field relation** auto-completion in forms
- **Reference group**: An EDT can declare that it "references" another table, which enables the `RefTableId` and `RefRecId` automatic fields on tables using that EDT

### EDT Properties — Key Properties

| Property | Description | Example |
|---|---|---|
| `Extends` | Base type the EDT wraps | `string`, `integer`, `real`, `enum` |
| `StringSize` | Max length (if `Extends = string`) | `20` |
| `Relationship` | EDT references a table for lookup relation | `CustTable` |
| `ReferenceField` | On the referenced table, which field is shown in lookups | `AccountNum` |
| `ArraySize` | When `Extends = string`, the array size for memory | `1` (default: fixed-length) |
| `Label` | User-facing display name | `'Customer Account'` |
| `HelpText` | Tooltip description | `'Unique customer identifier'` |

### The `CustAccount` EDT — A Real-World Example

```
EDT Name: CustAccount
Extends: string
StringSize: 20
Relationship: CustTable → AccountNum
ReferenceField: AccountNum
Label: CustAccount
HelpText: Customer account number
```

When you use `CustAccount` as a field type on any table, and then build a form with that table as a data source, the `AccountNum` field automatically gets a **lookup** to find and select existing customer records — this is entirely driven by the EDT metadata.

## 9.3 Field Groups

Field groups are **named sets of fields** defined at the table level. They provide:

1. **Form auto-generation**: A form can include an entire field group — adding new fields to the group automatically adds them to all forms using it
2. **Report generation**: SSRS queries can reference field groups instead of listing every field individually
3. **Documentation**: Field groups describe the logical grouping of related fields (e.g., `Address`, `Financial`, `ContactInfo`)

### Field Group Properties

| Property | Description |
|---|---|
| `Label` | Display name of the field group |
| `Fields` | The list of fields included in the group |

### Field Group Usage in Forms

When a form's data source references a table with field groups, you can drag the **entire field group** onto a form design node — all fields in the group appear automatically with their labels and EDT properties.

## 9.4 Table Extensions — The Modern Extension Pattern

**Note:** *Table inheritance* (using `SupportInheritance`/`Extends` properties with a discriminator field like `InstanceRelationType`) and *table extension* (using `[ExtensionOf(tableStr(...))]`) are **two distinct mechanisms** in D365 F&O. This section covers **table extension**, which is the recommended approach for upgrade-safe customizations. For table inheritance (a separate feature for hierarchical table relationships), see [Table inheritance overview](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/table-inheritance).

Microsoft recommends **table extension** over overlayering or subclassing tables. The extension pattern adds fields or methods to an existing table without modifying the base table definition.

### Table Extension Syntax

```xpp
[ExtensionOf(tableStr(VendTable))]
final class VendTable_Extension
{
    ComplianceCode complianceCode;

    // Extended field: add a new field to the existing VendTable
    // This field appears on VendTable in the AOT as if it were on the base table
    // but it is deployed in the extension model, so it survives upgrades
}
```

### What Table Extension Gives You

- **New fields**: Add additional columns to the existing table
- **New methods**: Add methods to the existing table's method list
- **Method overrides**: Override existing methods using CoC or event handlers (not direct override — must use extension framework)
- **`validateWrite()` override**: Add validation logic without modifying the base table
- **`modifyField()` override**: Add logic when a field is changed

### What Table Extension Does NOT Give You

- **Cannot change existing methods** — you can only override via CoC or event handlers
- **Cannot change table properties** — you cannot change `AllowDuplicate`, `CacheLookup`, etc. on a table via extension
- **Cannot remove fields** — extension only adds

## 9.5 Table Validation — Where to Validate

Data integrity is enforced at three levels, each with a specific role:

### Level 1: Table-level Validation (`validateWrite()`)

Called whenever a record is about to be written (insert or update). This is where **business rules** live — rules that must be true before any record can be saved.

```xpp
// In VendTable or in a table extension:
public boolean validateWrite()
{
    boolean ret;
    ret = next validateWrite();  // Always call next first — standard validations run here

    // Add custom validation
    if (this.ComplianceCode == '' && this.creditMax > 500000)
    {
        ret = checkFailed(literalStr('compliance code is required for vendors with credit limit over $500,000'));
    }

    return ret;  // true = allow save, false = reject with explanation in Infolog
}
```

**Key rules:**
- Always call `next` first — standard D365 validations run in `next` and set the `ret` flag
- Use `checkFailed()` to display an error message in the Infolog — this returns `false` from `validateWrite()` but does NOT throw an exception
- `checkFailed()` automatically includes the field label and the message — the user sees the field name and the error text
- Never use `error()` inside `validateWrite()` — use `checkFailed()` instead

### Level 2: Field-level Validation (`validateField()`)

Called when a single field value is being set. Used for field-specific validation (e.g., format checks, range checks).

### Level 3: Application-level Validation (Class Methods)

Business logic that is too complex to fit in table validation — lives in service classes or `RunBase` classes. Called from the UI layer or batch jobs.

## 9.6 Record Lifecycle and the `modifiedField()` Pattern

When a field value changes on a record, `modifiedField(fieldId)` is called automatically by the framework. You can override this to react to specific field changes.

```xpp
// In a table extension:
public void modifiedField(FieldId _fieldId)
{
    switch (_fieldId)
    {
        case fieldNum(VendTable, CreditMax):
            // When credit limit changes, validate compliance requirements
            if (this.CreditMax > 500000 && this.ComplianceCode == '')
            {
                warning('Credit limit exceeds $500,000 — compliance code is recommended');
            }
            break;
    }
    super(_fieldId);  // Always call super() LAST
}
```

**Critical: `super(_fieldId)` goes LAST in `modifiedField()` — opposite of `validateWrite()` where `super()` goes FIRST.**

> **Why the difference?** `validateWrite()` is a *gate* — base validation must run FIRST to establish baseline validity before custom rules. `modifiedField()` is a *notification* — the base field logic (lookups, derived fields, standard modified behavior) runs first, then your custom reaction runs after.

## 9.7 `insert_recordset` / `update_recordset` — Set-Based Performance

These operations execute in a single SQL statement rather than looping record-by-record, and are dramatically faster for large data volumes.

### When to Use Set-Based Operations

- **`insert_recordset`**: Bulk loading data from staging tables, temporary tables, or query results
- **`update_recordset`**: Applying a transformation to many records at once (e.g., status changes, field updates)
- **`delete_from`**: Deleting a set of records matching a condition

### When NOT to Use Set-Based Operations

- When the table's `validateWrite()`, `insert()` or `update()` methods contain business logic that must execute for each record
- When event handlers on the table need to fire for each record
- When you need `RecId` values back from each inserted record (set-based inserts don't return `RecId` values)

### Set-Based Insert Example

```xpp
// Bulk insert from staging to target — extremely fast
insert_recordset VendTable (AccountNum, Name, CreditMax, Currency)
    select AccountNum, Name, CreditMax, Currency
    from VendStagingTable
    where VendStagingTable.StagingStatus == StagingStatus::Ready;
```

### Set-Based Update Example

```xpp
// Update all pending invoices older than 30 days
update_recordset VendInvoiceJour
    setting Status = VendInvoiceStatus::Late
    where VendInvoiceJour.Status == VendInvoiceStatus::Pending
    && VendInvoiceJour.InvoiceDate < today() - 30;
```

## 9.8 Activity — Custom Table Design

> **Activity**: Design a table called `APCustomsDeclaration` for storing customs compliance declarations that must link to each vendor invoice line. Requirements:
> 1. The table must store the declaration ID (unique, not auto-generated), declaration date, customs authority reference, and the invoice line `RecId`
> 2. The declaration ID must be formatted as `COMP-YYYY-VNDNNNNN-#######` where COMP is the company ID, YYYY is the year, VNDNNNNN is the vendor account number, and ####### is a sequential declaration number
> 3. Create an EDT for the declaration ID with validation that the format is correct
> 4. Add an alternate index on the declaration ID (`AllowDuplicates = No`)
> 5. Use a table extension on `VendInvoiceLine` to add a field that links to this new table
> 6. Design a `validateWrite()` method on the new table that ensures the referenced vendor invoice line actually exists
>
> **Hints** (no single approach — explore multiple paths):
> - **Hint A**: For the declaration ID format — where does the format logic belong? In the EDT (rejected — EDTs cannot contain logic), in a class method `generateDeclarationId()` (one valid approach), in a table `validateWrite()` (partial — validation is not generation), or using an `insert()` override on the table (generation + validation together — a valid but more complex approach).
> - **Hint B**: For linking to `VendInvoiceLine` — should you use EDT-based field relation (where the EDT is linked to `VendInvoiceLine.RecId`), or a manual lookup that queries the `VendInvoiceLine` table for the matching `RecId`?
> - **Hint C**: For sequential declaration numbering per vendor per year — should you use a dedicated sequence table, a `select max(declarationNumber)` query (race condition risk), or a `HoleId` (number sequence framework)? What are the concurrency implications of each?

### Expected Approach (Ideal — in detail)

The ideal solution:
1. **EDT**: Create `APCustomsDeclId` as a `string 35` EDT with `StringSize = 35`, no relationship (the declaration ID is generated, not entered by the user), no `Relation` property — it is a synthetic identifier, not a foreign key. The `RegularExpression` property can be set to validate the format pattern.
2. **Table design**: `APCustomsDeclaration` with fields: `DeclId` (new EDT), `DeclDate` (`date`), `CustomsRef` (`string 50`), `InvoiceLineRecId` (`int64` — the physical `RecId` type, not an EDT since it references a table row), plus standard fields.
3. **Indexes**: Primary index on `RecId` (auto), alternate index on `DeclId` with `AllowDuplicates = No`, and a non-unique index on `InvoiceLineRecId` for fast lookup of related declarations.
4. **Table extension on `VendInvoiceLine`**: Add an `APDeclId` EDT field (nullable) that links to the customs declaration. This preserves the base `VendInvoiceLine` table.
5. **Declaration ID generation** in the table's `insert()` method or a wrapper class method — **not** the EDT. Use a combination of `CompanyInfo::name()`, `year(today())`, `VendTable::find()` lookup, and a **number sequence** (`NumberSeq`) to generate the sequential portion safely under transaction control. The `NumberSeq` framework handles concurrency and deduplication.
6. **`validateWrite()`** uses `select firstonly exists` to check that `VendInvoiceLine` with the given `RecId` exists before allowing insert.

---
---


# Chapter 10: Form Architecture & CoC

## 10.1 Form Architecture

A form in D365 F&O is a UI presentation layer that sits on top of one or more table data sources. The form handles the visual layout (design node), data retrieval (data source nodes), and user interaction (control nodes and their events).

### Form Data Source — The Bridge

Every form has one or more **Data Source** nodes, each pointing to a table or query. The data source controls:

- **Which SQL query** runs against the database (the `executeQuery()` method)
- **What fields** are available to controls on the form (`Fields` collection under the data source)
- **How joins** to other data sources work (link type, dynamic filters)
- **Events** triggered when the user navigates records or changes data

### Data Source Link Types

| Link Type | Behavior | When to Use |
|---|---|---|
| **Inner Join** | Child records only show where a parent exists | Default — standard parent-child hierarchy |
| **Outer Join** | ALL child records show even if no parent match | When listing all child records regardless of parent existence |
| **Exists Join** | Parent records only if they have at least one child | For "show me customers who have orders" |

### Data Source Range (Filter) — Dynamic Filters

You can set **dynamic filters** on data sources using the `queryBuildDataSource().addRange()` method, or via the `init()` / `active()` form data source event methods. The `range()` and `value()` methods on `QueryBuildRange` allow you to programmatically set filter values.

```xpp
// Setting a dynamic range programmatically in the form's data source init()
public void init()
{
    QueryBuildDataSource qbd;
    QueryBuildRange qbr;

    super();

    qbd = element.query().dataSourceTable(tableNum(VendInvoiceJour));
    qbr = qbd.addRange(fieldNum(VendInvoiceJour, PurchId));
    qbr.value(strfmt('"%1"', 'PO-00123'));
}
```

### Form Event Lifecycle — The Key Events

| Event | When It Fires | Purpose |
|---|---|---|
| `init()` | Form is initialized, data sources are set up | Set default filters, initialize variables |
| `active()` | The records change (user navigates to a different record) | Refresh computed fields, set control states based on current record |
| `executeQuery()` | The query is about to execute (after `init()`) | Modify the query at runtime — add filters, change join types |
| `write()` | After a record is written to the database (insert or update) | Post-write validation, trigger dependent logic, clear stale cache |
| `validateWrite()` | Before a record is written — can reject the save | Business rule validation; return `false` to prevent save with error |
| `deleted()` | After a record is deleted | Clean up related records, log deletion, refresh dependent lookups |

### The `executeQuery()` Event — The Most Powerful Form Event

```xpp
// This runs EVERY time the form query executes — including when the user navigates
// records, refreshes the grid, or applies a filter
public void executeQuery()
{
    QueryBuildDataSource qbd = element.query().dataSourceTable(tableNum(VendTable));
    QueryBuildRange qbr;

    // Add a dynamic filter based on a control value on the form
    qbr = qbd.addRange(fieldNum(VendTable, AccountNum));
    qbr.value(queryValue(element.controlRun().controlName('FilterControl').value()));

    super();  // Always call super() LAST in executeQuery()
}
```

**Critical: In `executeQuery()`, always call `super()` LAST** — because `super()` is what actually executes the query. If you call `super()` first, the filters you added after it will be ignored.

## 10.2 Form Controls — Properties and Events

### Key Control Types

| Control | Use Case | Key Properties |
|---|---|---|
| **String Edit** | Text input/display | `AutoDeclaration`, `StringSize`, `Label` |
| **Integer/Real Edit** | Numeric input | `AutoDeclaration`, `Min`, `Max`, `Alignment` |
| **Date Edit** | Date input | `AutoDeclaration`, `DisplayFormat` |
| **Combo Box** | Dropdown selection | `AutoDeclaration`, `Items` (enumerated values), `Lookup` property |
| **Checkbox** | Boolean toggle | `AutoDeclaration`, `Label`, `Checked` |
| **Grid** | Multi-row tabular display | `AutoDeclaration`, `DataSource`, `MultiSelect`, `AllowEdit` |
| **Tab** | Tabbed sections | `AutoDeclaration`, `MultiSelect` |
| **Button** | Action trigger | `AutoDeclaration`, `Label`, `Command` property |
| **LookupButton** | Triggers a lookup | `AutoDeclaration`, `LinkedDataSource`, linked to EDT relationship or custom lookup method |
| **Tree** | Hierarchical display | `AutoDeclaration`, `DataSource`, `DisplayExpr` |
| **Image** | Displays BMP/PNG | `AutoDeclaration`, `ImageFile` |

### Form Control Events

| Event | When | Purpose |
|---|---|---|
| `validate()` | Before the new value is written to the data source | Field-level validation; return `false` to reject and show error |
| `modified()` | Control value changed by user | React to user input — update other controls, recalculate totals |
| `lookup()` | User clicks the lookup button or presses F3 | Custom lookup behavior; override to provide specialized lookup |
| `enter()` | Control receives focus | Highlight related fields, initialize dependent lookups |
| `close()` | Control/focus is lost | Cleanup, final validation |

**Note:** `validate()` runs **first** — if validation fails (returns `false`), `modified()` will **not** fire. This sequence ensures invalid data never propagates.
**Source:** [Form control events - Finance & Operations](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/user-interface/form-control-events)

### Setting Control Values Programmatically

```xpp
// Set a control's text value on the current form
element.controlRun().controlName('MyStringControl').text(cust.AccountNum);

// Set the value of a control bound to a data field
// Note: setting the underlying table field is preferred over setting the control directly
cust.AccountNum = 'C0001';  // This automatically updates the form control via data binding
```

### Design Patterns

#### List Page
A list page is a form with `FrameType = ListPage` — it shows records in a grid with a tree/navigator on the left. Clicking a record in the grid opens the detail page. List pages are the primary navigation pattern in D365 F&O.

#### Detail Page
A detail page (typically `FrameType = Form` or `DetailsForm`) shows all fields for a single record. It is opened from a list page via a `MenuItemDisplay`.

#### Popup / Dialog Form
A popup form (`FrameType = Dialog` or `Popup`) is a modal window used for data entry, quick edits, or confirmation. It typically has OK/Cancel buttons.

#### Workspace Card
A workspace card is a card-style UI element that can contain multiple form parts — used in the D365 workspace for dashboards and quick actions.

## 10.3 Chain of Command — Deep Dive

Chain of Command (CoC) is the **primary mechanism** for calling and extending standard D365 F&O code. It connects standard menu items to standard classes through a chain of method calls.

### How Chain of Command Works

1. A user clicks a **Menu Item** (e.g., Customer → Customers → All Customers)
2. The menu item is linked to a **Class** (e.g., `CustTableListPage`)
3. The class method `main()` is the entry point
4. Inside `main()`, the class calls `super()` to chain to the **next** class in the linked list
5. Each class in the chain runs in sequence — this is what "Chain of Command" means

### Extending the Chain

To add behavior to the standard chain:
1. Create a new class with `main()` that performs your logic
2. Use the `super()` call to join the chain at your desired position
3. Link the new class to a menu item (or replace the standard menu item's class reference)

### The `runLink()` Pattern

When a form action (like clicking "New" or "Delete") needs to invoke another class or form:
```xpp
// From a form button or menu item action:
MenuItemForm menuItem = new MenuItemForm();
menuItem.name(formstr(MyCustomForm));
menuItem.run();  // Opens the form directly
```

### `CommandMenu` and `CommandDisplayMenu`

- **`MenuItemButton`**: A button on a form toolbar that triggers a command class
- **`MenuItemAction`**: An action menu item that runs a class method (not a form)
- **`MenuItemDisplay`**: Opens a form — the most common type for navigation
- Each has a `Command` property that points to the class to execute

## 10.4 Form vs. Form Extension

### Form Modification
A form modification directly edits the standard `Form` node in the AOT. **This is not supported for customer/ISV code** because the next Microsoft update will overwrite your changes.

### Form Extension
A form extension (`[ExtensionOf(formStr(CustTable))]`) adds controls, data sources, or methods to a standard form without modifying it. **This is the supported pattern** and survives Microsoft updates.

```xpp
[ExtensionOf(formStr(CustTable))]
final class CustTable_FormExtension
{
    // Add a new data source
    CustComplianceLog complianceLog_ds;

    // Add a new control to the design
    // (Controls added via extension in the extension form design node)
}
```

### When to Use Which

| Scenario | Pattern |
|---|---|
| Add a new field to a form's data source | Form Extension |
| Add a new tab page to an existing form | Form Extension |
| Change a field label on the standard form | Avoid — request a label change via Microsoft support |
| Add a custom button that triggers new behavior | Form Extension |
| Change the SQL join type on a data source | Form Extension (override `executeQuery()` of the data source) |

## 10.5 Activity — Multi-Form Solution

> **Activity**: Design a three-form solution for a vendor compliance dashboard:
> 1. **Form A (List Page)**: Shows all vendors with a compliance status column (computed via EDT display method). Clicking a vendor opens Form B.
> 2. **Form B (Detail Page)**: Shows vendor compliance metadata with a tab: 'Overview' and 'History'. The 'History' tab shows a grid of compliance log entries. A "New Declaration" button opens Form C.
> 3. **Form C (Popup)**: A dialog form for creating a new customs declaration. It validates the input, saves to `APCustomsDeclaration` table, closes, and refreshes Form B's grid.
>
> Requirements:
> - Form A must use a dynamic filter that shows only vendors whose credit limit exceeds $100,000
> - Form B's History tab grid must auto-refresh when Form C submits a new record
> - The compliance status display on Form A must use a DisplayMethod that queries the `APComplianceLog` table
> - The "New Declaration" button on Form B must use a MenuItemAction to open Form C
> - All forms must follow D365 F&O form design conventions (labels, HelpText, proper sizing, keyboard navigation)
>
> **Hints** (Multiple Valid Approaches):

- **Hint A**: How to implement the dynamic filter on Form A?
  - **Approach 1**: Set a `range` on the data source in `init()` — simple but static (the filter value doesn't change per-vendor)
  - **Approach 2**: Override `executeQuery()` on the form's data source to add a dynamic range based on another form control — more flexible, allows the user to change the threshold
  - **Approach 3**: Override `active()` to refresh the grid with a filtered query each time the user navigates records — simplest implementation but may cause performance issues with many records

- **Hint B**: How to make Form B's History grid auto-refresh when Form C submits a record?
  - **Approach 1**: Call `element.datasource().refresh()` or `element.executeQuery()` on Form B from Form C's OK button — direct coupling, tightly integrated
  - **Approach 2**: Use an event handler on `APCustomsDeclaration` table's `inserted()` event, which fires a `refresh()` call on all open forms using that table — decoupled architecture, but event handlers on table insert don't automatically know which forms are open
  - **Approach 3**: Pass Form B's `element` to Form C as a parameter, and call Form B's `refresh()` from Form C's close method — explicit coupling but fully controlled

- **Hint C**: How to implement the compliance status column as a DisplayMethod?
  - **Approach 1**: A static method on `VendTable` extension that takes a `VendTable` buffer and returns a status string — clean separation, reusable
  - **Approach 2**: A DisplayMethod directly on the Form data source control — bound to the data source, automatically reflects current record context
  - **Approach 3**: Override `active()` on the form to set a form-level variable, then a DisplayMethod reads that variable — most flexible but most complex

### Expected Approach (Ideal — in detail)

The ideal approach combines extensibility with proper architecture:

1. **Form A** uses a `ListPage` frame type with `VendTable` as the primary data source. The dynamic filter is set in `executeQuery()` of the data source — not in `init()`, because `executeQuery()` re-runs when the user changes any control, making the filter truly dynamic. A `displayMethod` on the data source adds the compliance status column by calling a method on a service class.

2. **Form B** uses a `Form` frame type (not ListPage) with `VendTable` as the primary data source and `APCustomsDeclaration` joined (or separately added) as a related data source. The History tab is a separate design node (`Group` or `TabPage`) containing a grid bound to the `APCustomsDeclaration` data source. The "New Declaration" button is an `ActionMenuItem` that uses a MenuItemAction to open Form C. Form B overrides the data source's `active()` method to set a class-level variable holding the current vendor's `RecId`, which Form C uses when creating a new declaration.

3. **Form C** is a `Dialog` frame type with OK/Cancel buttons. On OK, it validates input, creates the `APCustomsDeclaration` record, calls `element.datasource().refresh()` on Form B's data source (passed as a parameter — Form B instantiates Form C and passes itself as the caller), and then closes.

---
---


# Chapter 11: Views & Lookups

## 11.1 Views — What They Are and Why They Matter

A view is a **named query** stored in the AOT. It acts like a table but doesn't store data — when you `select` from a view, the AOS translates it into SQL that joins across the underlying tables.

### When to Use a View

| Use Case | View | Alternative |
|---|---|---|
| Repeated multi-table join query used in many places | **Yes** — centralize, reuse | Duplicating the `select` logic everywhere |
| Complex logic needed for reporting | **Yes** — forms, reports, data entities all can use views | Repeating the join in each consumer |
| Simplifying security — restrict access to underlying tables | **Yes** — expose only the view, not the base tables | Granting access to all underlying tables |
| Simple single-table query only | **No** — just select from the table | Views add unnecessary abstraction |
| Performance-critical queries needing `firstonly` optimization | **Careful** — test view performance; `exists join` in a view may not translate optimally | Consider a query directly in the consuming code |

### View Properties

| Property | Description | Common Values |
|---|---|---|
| `Label` | User-facing name | `'Vendor with Contact Details'` |
| `IsLookup` | Marks the view as a lookup | `Yes` |
| `CacheLookup` | Caches lookup results for performance | `Yes` |

**Note:** The "dynamic" behavior (query rebuilt at runtime vs. cached SQL) is controlled by the **query framework**, not a named view property.
**Source:** [Views - Finance & Operations](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/views)

### How a View is Defined in the AOT

A view in the AOT contains:
- **`Data Sources`** — a tree of table/query references with join orders and link conditions
- **`Fields`** — each field is mapped to a table field (can be renamed with alias)
- **`LookupField`** — specifies which field is used when the view is used as a lookup
- **`Alias`** — optional rename for a field from its original table field name

```
VendorContactView (View)
├── Data Sources
│   ├── DirPartyTable (Inner Join)
│   │   └── DirPartyLocation (Outer Join)
│   │       └── LogisticsLocation
│   └── VendTable (Inner Join)
│       └── VendBankAccount (Outer Join)
├── Fields
│   ├── DirPartyTable.Name → Alias: PartyName
│   ├── VendTable.AccountNum → Alias: VendorAccount
│   ├── LogisticsLocation.City → Alias: PartyCity
│   └── VendBankAccount.BankAccountNum → Alias: BankIBAN
└── LookupField: VendorAccount
```

### View Extensions

You can extend a standard view using `[ExtensionOf(viewStr(...))]` to add fields from additional tables — this is how you add fields without modifying the standard view. The extension appears as a new data source in the extended view.

## 11.2 Lookups — The User's Gateway to Data

A lookup is the mechanism by which a user can find and select a value for a field — typically triggered by clicking the **magnifier button** on a field or pressing **F3**.

### How Lookups Work in D365 F&O

1. The user clicks the lookup button or presses F3 on a field
2. The framework calls the `lookup()` method on the form control
3. The `lookup()` method builds a `FormRun` object (the lookup dialog) and populates it with a data source
4. When the user selects a record, the selected value is written to the source field

### Lookup Design Patterns

#### Pattern 1: EDT-based Lookup (Simplest)
When a field uses an EDT with a **Relationship** to another table, the framework automatically provides a standard lookup showing the related table's fields. No custom code needed.

#### Pattern 2: `SysTableLookup` (Most Common)
```xpp
public void lookup()
{
    SysTableLookup sysTableLookup = SysTableLookup::newParameters(tableNum(VendTable), element);
    sysTableLookup.addLookupField(fieldNum(VendTable, AccountNum), true);  // true = show in grid
    sysTableLookup.addLookupField(fieldNum(VendTable, Name));
    sysTableLookup.addLookupField(fieldNum(VendTable, CreditMax));
    sysTableLookup.parmQuery(this.query());  // Pass current query context if needed
    sysTableLookup.performFormLookup();
}
```

#### Pattern 3: `FormRun` as Lookup (Maximum Control)
```xpp
public void lookup()
{
    FormRun formRun;
    Args args = new Args();
    args.name(formstr(VendTableLookup));  // Custom form designed as a lookup
    args.caller(element);
    args.parm('LookupFieldId', fieldNum(VendTable, AccountNum));
    formRun = classfactory.formRunClass(args);
    formRun.init();
    formRun.run();
    formRun.wait();  // Synchronous — waits for user selection

    // After user closes the lookup, get the selected value
    if (formRun.closedOk())
    {
        element.text(formRun.element().parmSelectedValue());
    }
}
```

#### Pattern 4: Multi-Select Lookup
D365 F&O supports multi-select lookups where the user can select multiple records and the selected values are stored in a **Relation** or **Link** table. The `SysTableLookup` class supports this via `parmMultiSelect(true)`.

### Custom Filtering in Lookups

You can pass a `Query` object to `SysTableLookup.parmQuery()` to filter the lookup results. This is the most common way to have the lookup show only relevant records based on context (e.g., only customers in the same `CustGroup`).

## 11.3 Multi-Select Lookup Exercise (Production Grade)

> **Activity**: Create a lookup for a field on `SalesTable` that allows the user to select multiple sales territories (from `DirTerritory` table) when creating an order. The lookup must:
> 1. Filter territories based on the user's security role (only show territories assigned to the current user)
> 2. Show territory name, code, and region in the lookup grid
> 3. Allow the user to select multiple territories
> 4. Store the selected territory IDs in a link table (`SalesTerritoryLink`) with `SalesTableRecId` and `TerritoryRecId` as foreign keys
> 5. The lookup must filter out territories that are already linked to this order (if editing an existing order)
> 6. Add a "Select All" checkbox at the top of the lookup form
>
> **Hints** (No single approach):
> - **Hint A for filtering by security role**: Option A1 — Query the `SecurityRole` user assignment table at lookup time and filter territories by role membership. Option A2 — Pass the user's `UserId` as a query range to the lookup form, and let the form filter itself in `executeQuery()`. Option A3 — Use a class method `DirTerritory::findByUser()` that handles the lookup query construction encapsulation.
> - **Hint B for "Select All" checkbox**: Option B1 — Add it as a separate form control that, when clicked, selects all visible records in the grid via `element.queryRun().getFirst(NoInit)` and toggling selection. Option B2 — Implement it as a data source field on the lookup form itself that, when set to `true`, triggers an `active()` event that iterates and selects all records. Option B3 — Use a parameter passed to the lookup form that sets a flag, and the form's `init()` reads that flag and auto-selects all records.
> - **Hint C for excluding already-linked territories**: Option C1 — Add a `notExists join` on the lookup's query that excludes territories already linked. Option C2 — Pass the current `SalesTable.RecId` to the lookup, and in the form's `executeQuery()`, add a range that excludes linked territories. Option C3 — Handle exclusions in the `lookup()` method after the form returns — iterate the selection and remove any already-linked territory IDs before saving.

### Expected Approach (Ideal — in detail)

1. **Lookup form**: A dedicated form (`TerritoryLookupDlg`) with `DirTerritory` as its data source. The query includes:
   - A range on territory assignment based on user security role (passed as an `args.parm()` parameter)
   - A `notExists join` excluding territories already linked to this `SalesTable` record
   - A checkbox control bound to a temporary table or form parameter for "Select All"
2. **`lookup()` method**: Uses `SysTableLookup` with `parmMultiSelect(true)` — `SysTableLookup` handles the selection mechanics. The form returns territory IDs that are then written to the link table.
3. **`lookup()` method passes context via `Args`**: `args.parm('SalesTableRecId', element.recId())` and `args.parm('UserId', curUserId())`.
4. **"Select All" checkbox**: Lives on the lookup form itself. When toggled, it iterates all records in the lookup data source and toggles `selected` state on each. The `selected` field is part of the `DirTerritory` data source (or a temp `Relation` table used to track multi-select state).
5. **After the lookup closes**, the parent form iterates the selected territories and writes records to `SalesTerritoryLink`.

---
---

# Remaining Chapters — Detailed Outline (Content to follow)


# Chapter 12: Class Fundamentals & RunBase

## 12.1 Class Fundamentals — Static vs Instance

In X++, every class is either **static** (never instantiated, only static methods) or **instance-based** (objects created with `new` or `construct()`). Understanding when to use each is foundational to writing maintainable D365 F&O code.

### Static Classes

A static class contains only static methods and is never instantiated. You declare it with the `static` keyword on the class declaration.

```xpp
static class NumberSeq
{
    // Only static methods — no instance methods
    public static NumberSeqReference newReference(NumberSeqTable _numberSeqTable)
    {
        NumberSeqReference numberSeqReference;
        // ... logic
        return numberSeqReference;
    }
}
```

**When to use static classes:**
- Utility/helper methods that don't maintain state (e.g., `Global::isNull()`, `Global::str2Date()`)
- Service entry points called from menu items or other classes
- Factory methods that create and return instances of other classes

**When NOT to use static classes:**
- When you need to maintain state between method calls
- When you need to support inheritance or polymorphism
- When you need to mock or test the class in isolation (static methods are hard to unit test)

### Instance Classes

An instance class is the default — you create objects with `new` or a `construct()` factory method. Instance classes maintain state through member variables.

```xpp
class CustAccountValidator
{
    CustTable custTable;

    // Constructor — private to enforce factory pattern
    private CustAccountValidator(CustTable _custTable)
    {
        custTable = _custTable;
    }

    // Factory method — the preferred way to obtain an instance
    public static CustAccountValidator construct(CustTable _custTable)
    {
        return new CustAccountValidator(_custTable);
    }

    // Instance method — has access to member state
    public boolean validate()
    {
        if (custTable.AccountNum == '')
        {
            return checkFailed('Account number is required');
        }
        return true;
    }
}
```

### Constructor Patterns

| Pattern | Syntax | When to Use |
|---|---|---|
| **`new()` constructor** | `public CustAccountValidator()` | Simple classes with no complex initialization |
| **`construct()` factory** | `public static CustAccountValidator construct(...)` | When you need to control instance creation, cache instances, or return a subclass |
| **`new` with private constructor** | `private CustAccountValidator(...)` + `public static construct()` | Enforces factory pattern — prevents direct `new` calls from external code |
| **Singleton via `construct()`** | `static CustAccountValidator instance; if (!instance) instance = new ...; return instance;` | When exactly one instance must exist across the entire session |

**The `construct()` factory pattern is the dominant pattern in D365 F&O.** Microsoft uses it extensively in the standard codebase (e.g., `SysOperationServiceController::construct()`, `SrsReportDataProvider::construct()`). You should follow this convention in all custom classes.

### The `parmX()` Accessor Pattern

Every class that holds data should expose its member variables through `parmX()` accessor methods. This is the X++ equivalent of Java's getter/setter pattern and is critical for:

1. **Encapsulation** — external code never accesses member variables directly
2. **Validation** — you can add logic in the setter (`parmX(value)`) before storing
3. **Testability** — you can mock or verify state through accessors
4. **Framework compatibility** — `RunBase`, `SysOperation`, and other frameworks rely on `parmX()` methods for data passing

```xpp
class VendComplianceContract
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    boolean requireComplianceCheck;

    // Getter — no parameters
    public VendTable parmVendTable()
    {
        return vendTable;
    }

    // Setter — with parameter, returns 'this' for chaining
    public VendComplianceContract parmVendTable(VendTable _vendTable)
    {
        vendTable = _vendTable;
        return this;
    }

    // Getter
    public ComplianceCode parmComplianceCode()
    {
        return complianceCode;
    }

    // Setter with validation
    public VendComplianceContract parmComplianceCode(ComplianceCode _complianceCode)
    {
        if (_complianceCode && _complianceCode.length() > 20)
        {
            throw error(strFmt('Compliance code cannot exceed 20 characters. Provided: "%1"', _complianceCode));
        }
        complianceCode = _complianceCode;
        return this;
    }

    // Boolean flag — getter returns boolean, setter returns 'this' for chaining
    public boolean parmRequireComplianceCheck()
    {
        return requireComplianceCheck;
    }

    public VendComplianceContract parmRequireComplianceCheck(boolean _require)
    {
        requireComplianceCheck = _require;
        return this;
    }
}
```

**The chaining pattern (`return this;`)** is optional but common in D365 F&O — it allows you to write:
```xpp
VendComplianceContract contract = new VendComplianceContract()
    .parmVendTable(vendTable)
    .parmComplianceCode('COMP-001')
    .parmRequireComplianceCheck(true);
```

---

## 12.2 The `RunBase` Framework — Batch Processing Foundation

`RunBase` is the base class for all batch-executable operations in D365 F&O. It provides the infrastructure for:

- Displaying a **dialog** to the user for parameter input
- **Packing** and **unpacking** state for serialization (required for batch jobs that run on a different tier)
- The **`run()`** method where business logic executes
- Integration with the **batch framework** (`RunBaseBatch`)

### Why RunBase Exists

Before `RunBase`, developers wrote ad-hoc batch jobs with no standard dialog, no parameter serialization, and no integration with the batch job queue. `RunBase` standardizes this pattern so that:

- Any class extending `RunBase` automatically gets a dialog UI
- Parameters survive serialization across tiers (client → batch server → AOS)
- The batch framework can schedule, monitor, and retry the job

### The Required Methods

Every `RunBase` subclass must implement these methods:

| Method | Required? | Purpose |
|---|---|---|
| `dialog()` | Yes | Creates and returns a `Dialog` object with input controls for the user |
| `pack()` | Yes | Serializes the class's state into a `container` for cross-tier transfer |
| `unpack(container)` | Yes | Deserializes the container back into the class's state |
| `run()` | Yes | Contains the actual business logic that executes |
| `main(Args _args)` | Yes (static) | Entry point — called when the user triggers the action from a menu item |

### `dialog()` — Building the User Interface

```xpp
class VendComplianceBatchJob extends RunBase
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;

    // Dialog method — creates the UI
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        DialogField dfVend;
        DialogField dfCode;
        DialogField dfFrom;
        DialogField dfTo;

        // Add a table lookup field — user can search for a vendor
        dfVend = dialog.addFieldValue(typeid(VendTable), vendTable, 'Vendor');
        dfVend.lookupButton(true);  // Enable the lookup button

        // Add a string field for compliance code
        dfCode = dialog.addFieldValue(typeid(ComplianceCode), complianceCode, 'Compliance Code');

        // Add date range fields
        dfFrom = dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dfTo = dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');

        return dialog;
    }
}
```

**Key points about `dialog()`:**
- Always call `super::dialog()` first — this creates the base dialog with OK/Cancel buttons
- Use `dialog.addFieldValue()` for standard field types — it automatically creates the control, label, and data binding
- Use `dialog.addGroup()` to organize fields into logical sections
- Return the `Dialog` object — the framework handles showing it and reading values back

### `pack()` and `unpack()` — Serialization

When a `RunBase` job runs as a batch, it may execute on a different tier than where it was created. The `pack()`/`unpack()` methods serialize and deserialize the class's state.

```xpp
// pack() — serialize state into a container
public container pack()
{
    return [vendTable, complianceCode, fromDate, toDate];
}

// unpack() — deserialize state from a container
public boolean unpack(container _packedClass)
{
    vendTable = _packedClass.packGet(1);
    complianceCode = _packedClass.packGet(2);
    fromDate = _packedClass.packGet(3);
    toDate = _packedClass.packGet(4);
    return true;
}
```

**Critical rules for `pack()`/`unpack()`:**
1. The order of elements in the container **must match** between `pack()` and `unpack()` — any mismatch causes silent data corruption
2. Only pack **simple types** (strings, dates, integers, `RecId`, table buffers) — do NOT pack `FormRun`, `Object`, or other non-serializable types
3. If you add a new field, add it to the **end** of both `pack()` and `unpack()` to maintain backward compatibility with existing batch jobs already in the queue
4. The `container` type is the X++ equivalent of a typed tuple — it holds ordered elements of any type

### `run()` — The Business Logic

```xpp
public void run()
{
    VendTable vendTableLocal;
    APCustomsDeclaration declaration;

    // Validate that the vendor exists
    vendTableLocal = VendTable::find(vendTable.AccountNum);
    if (!vendTableLocal)
    {
        throw error(strFmt('Vendor "%1" not found.', vendTable.AccountNum));
    }

    // Process compliance declarations for the date range
    while select declaration
        where declaration.VendTableRecId == vendTableLocal.RecId
        && declaration.DeclDate >= fromDate
        && declaration.DeclDate <= toDate
    {
        // Business logic here
        this.processDeclaration(declaration);
    }

    info(strFmt('Compliance batch job completed for vendor "%1".', vendTableLocal.AccountNum));
}
```

### `main(Args)` — The Static Entry Point

```xpp
public static void main(Args _args)
{
    VendComplianceBatchJob batchJob = new VendComplianceBatchJob();

    // If called from a menu item, args may contain pre-populated data
    if (_args && _args.record())
    {
        batchJob.parmVendTable(_args.record());
    }

    // Show the dialog — if user clicks OK, run the job
    if (batchJob.prompt())
    {
        batchJob.run();
    }
}
```

**The `prompt()` method** (inherited from `RunBase`) shows the dialog, reads the user's input, and returns `true` if the user clicked OK. It internally calls `dialog()`, `pack()`, and sets up the class state.

### `RunBase` — Complete Class Template

```xpp
class VendComplianceBatchJob extends RunBase
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;

    // 1. Dialog — user input
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        dialog.addFieldValue(typeid(VendTable), vendTable, 'Vendor');
        dialog.addFieldValue(typeid(ComplianceCode), complianceCode, 'Compliance Code');
        dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');
        return dialog;
    }

    // 2. Pack — serialize for batch
    public container pack()
    {
        return [vendTable, complianceCode, fromDate, toDate];
    }

    // 3. Unpack — deserialize from batch
    public boolean unpack(container _packedClass)
    {
        vendTable = _packedClass.packGet(1);
        complianceCode = _packedClass.packGet(2);
        fromDate = _packedClass.packGet(3);
        toDate = _packedClass.packGet(4);
        return true;
    }

    // 4. Run — business logic
    public void run()
    {
        // ... implementation ...
    }

    // 5. Main — entry point
    public static void main(Args _args)
    {
        VendComplianceBatchJob job = new VendComplianceBatchJob();
        if (_args && _args.record())
        {
            job.parmVendTable(_args.record());
        }
        if (job.prompt())
        {
            job.run();
        }
    }
}
```

---

## 12.3 `RunBaseBatch` — Subclassing RunBase for Batch Jobs

`RunBaseBatch` extends `RunBase` to add **batch job** capabilities — the job runs in the background via the batch framework, not interactively.

### What `RunBaseBatch` Adds

| Feature | Description |
|---|---|
| `runOn()` | Specifies where the job runs: `RunOn::Client`, `RunOn::Server`, or `RunOn::Batch` |
| `doBatch()` | Called by the batch framework — wraps `run()` with batch infrastructure (progress reporting, error handling, retry) |
| `createJob()` | Static method that creates a `BatchHeader` and queues the job — this is what gets called from a menu item |
| `batchInfo()` | Returns the `BatchHeader` with job description, batch group, and scheduling info |
| `lastValue()` | Used for progress reporting — returns a string describing the current progress |

### `RunBaseBatch` — Complete Class Template

```xpp
class VendComplianceBatchJob extends RunBaseBatch
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;

    // Dialog — same as RunBase
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        dialog.addFieldValue(typeid(VendTable), vendTable, 'Vendor');
        dialog.addFieldValue(typeid(ComplianceCode), complianceCode, 'Compliance Code');
        dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');
        return dialog;
    }

    // Pack / Unpack — same as RunBase
    public container pack()
    {
        return [vendTable, complianceCode, fromDate, toDate];
    }

    public boolean unpack(container _packedClass)
    {
        vendTable = _packedClass.packGet(1);
        complianceCode = _packedClass.packGet(2);
        fromDate = _packedClass.packGet(3);
        toDate = _packedClass.packGet(4);
        return true;
    }

    // runOn() — where should this job execute?
    // Batch jobs MUST run on the server or batch tier, not the client
    public RunOn runOn()
    {
        return RunOn::Batch;
    }

    // run() — the actual business logic
    public void run()
    {
        // ... same as RunBase.run() ...
    }

    // lastValue() — progress reporting
    // Called by the batch framework to show progress in the batch job list
    public int lastValue()
    {
        // Return a value that represents progress (e.g., number of records processed)
        return this.lastValueCounter;
    }

    // batchInfo() — metadata about the batch job
    // Called by the framework to populate the BatchHeader
    public BatchHeader batchInfo()
    {
        BatchHeader batchHeader = super::batchInfo();
        batchHeader.parmDescription('Vend Compliance Batch Job');
        batchHeader.parmBatchGroup('BATCHGROUP1');  // The batch group that processes this job
        batchHeader.parmExecutionStyle(BatchExecutionStyle::OnDemand);
        return batchHeader;
    }

    // createJob() — static entry point called from a menu item
    // This creates the batch header and queues the job
    public static void createJob()
    {
        VendComplianceBatchJob job = new VendComplianceBatchJob();
        if (job.prompt())
        {
            // Submit the job to the batch framework
            job.run();
        }
    }

    // main() — the static entry point
    public static void main(Args _args)
    {
        VendComplianceBatchJob job = new VendComplianceBatchJob();
        if (_args && _args.record())
        {
            job.parmVendTable(_args.record());
        }
        if (job.prompt())
        {
            job.run();
        }
    }
}
```

### Batch Job Lifecycle

```
[1] User clicks menu item → createJob() called
    │
[2] createJob() calls job.prompt() → dialog shown, user enters parameters
    │
[3] createJob() calls job.run() → job submitted to batch framework
    │
[4] Batch framework creates BatchHeader with job metadata
    │
[5] Batch job placed in queue (BatchHeader.Status = Created)
    │
[6] Batch server picks up job → unpack() deserializes parameters
    │
[7] doBatch() called → wraps run() with try/catch, progress reporting
    │
[8] run() executes business logic
    │
[9] Batch job completes → BatchHeader.Status = Completed
    │
[10] User notified via Infolog and/or email (if configured)
```

### `runOn()` — Execution Target

| Value | Description | Use When |
|---|---|---|
| `RunOn::Client` | Runs on the user's desktop | Lightweight operations that need UI interaction |
| `RunOn::Server` | Runs on the AOS server | Operations that need server-side data access but don't need batch queuing |
| `RunOn::Batch` | Runs on the batch server | Long-running operations that should be queued and run asynchronously |

**Rule of thumb:** If the operation takes more than a few seconds, use `RunOn::Batch`. If it needs to run unattended (e.g., nightly reconciliation), use `RunOn::Batch`. If it requires user interaction, use `RunOn::Client`.

---

## 12.4 `SysOperationServiceController` — The Modern Service Pattern

`SysOperationServiceController` is the **modern, service-oriented** approach to running business operations. It is the successor pattern to `RunBase` for operations that need to be:

- Called from **external systems** (via OData/REST)
- Executed as **service operations** in the Service Layer
- **Contract-driven** — input and output are defined in a contract class, not in dialog fields
- **Versioned** — contracts can evolve independently of the operation implementation

### Why SysOperationServiceController?

| RunBase | SysOperationServiceController |
|---|---|
| Dialog-based input | Contract-based input (typed parameters) |
| Batch-only execution | Can run synchronously (in-call) or asynchronously (batch) |
| Tightly coupled to UI | Decoupled — can be called from UI, batch, or external services |
| `pack()`/`unpack()` for serialization | Contract class handles serialization automatically |
| Limited to X++ consumers | Exposable via OData/REST for Power Platform and external systems |

### The Three Components

A `SysOperationServiceController`-based operation consists of three classes:

1. **Contract class** — defines the input and output parameters as properties
2. **Service class** — contains the business logic (`process()` method)
3. **Controller class** — extends `SysOperationServiceController`, wires the contract to the service, and manages execution

### Component 1: The Contract Class

```xpp
[DataContractAttribute]
class VendComplianceContract
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;
    boolean generateReport;

    [DataMemberAttribute('VendTable'), SysOperationLabelAttribute('Vendor')]
    public VendTable parmVendTable(VendTable _vendTable = vendTable)
    {
        vendTable = _vendTable;
        return vendTable;
    }

    [DataMemberAttribute('ComplianceCode'), SysOperationLabelAttribute('Compliance Code')]
    public ComplianceCode parmComplianceCode(ComplianceCode _complianceCode = complianceCode)
    {
        complianceCode = _complianceCode;
        return complianceCode;
    }

    [DataMemberAttribute('FromDate'), SysOperationLabelAttribute('From Date')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    [DataMemberAttribute('ToDate'), SysOperationLabelAttribute('To Date')]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }

    [DataMemberAttribute('GenerateReport'), SysOperationLabelAttribute('Generate Report')]
    public boolean parmGenerateReport(boolean _generateReport = generateReport)
    {
        generateReport = _generateReport;
        return generateReport;
    }
}
```

**Key attributes:**
- `[DataContractAttribute]` on the class — marks it as a data contract
- `[DataMemberAttribute('Name')]` on each property — the name used in OData/REST serialization
- `[SysOperationLabelAttribute('Label')]` — the user-facing label for the parameter
- Each `parmX()` method uses the **getter/setter pattern** — if called with a parameter, it sets the value; if called without, it returns the current value

### Component 2: The Service Class

```xpp
class VendComplianceService
{
    // The main business logic method
    public VendComplianceContract process(VendComplianceContract _contract)
    {
        VendTable vendTableLocal;
        APCustomsDeclaration declaration;
        VendComplianceContract resultContract;

        // Validate the contract
        this.validateContract(_contract);

        // Process declarations
        vendTableLocal = VendTable::find(_contract.parmVendTable().AccountNum);

        while select declaration
            where declaration.VendTableRecId == vendTableLocal.RecId
            && declaration.DeclDate >= _contract.parmFromDate()
            && declaration.DeclDate <= _contract.parmToDate()
        {
            this.processDeclaration(declaration);
        }

        // If requested, generate a report
        if (_contract.parmGenerateReport())
        {
            this.generateReport(vendTableLocal, _contract.parmFromDate(), _contract.parmToDate());
        }

        // Return the contract (potentially with output fields populated)
        resultContract = _contract;
        return resultContract;
    }

    private void validateContract(VendComplianceContract _contract)
    {
        if (!_contract.parmVendTable())
        {
            throw error('Vendor is required.');
        }
        if (_contract.parmFromDate() > _contract.parmToDate())
        {
            throw error('From date cannot be after to date.');
        }
    }

    private void processDeclaration(APCustomsDeclaration _declaration)
    {
        // Business logic for processing a single declaration
        info(strFmt('Processing declaration %1 for vendor %2', _declaration.DeclId, _declaration.VendTableRecId));
    }

    private void generateReport(VendTable _vendTable, FromDate _from, ToDate _to)
    {
        // SSRS report generation logic
        SrsReportRunController reportController = new SrsReportRunController();
        // ... configure and run the report ...
    }
}
```

### Component 3: The Controller Class

```xpp
class VendComplianceController extends SysOperationServiceController
{
    // The static entry point — called from a menu item or external service
    public static void main(Args _args)
    {
        VendComplianceController controller = new VendComplianceController();
        VendComplianceContract contract = new VendComplianceContract();

        // If called from a form, populate the contract from the form's data source
        if (_args && _args.record())
        {
            contract.parmVendTable(_args.record());
        }

        // Set the service and contract types
        controller.parmContractType(classStr(VendComplianceContract));
        controller.parmServiceType(classStr(VendComplianceService));

        // Start the operation
        controller.startOperation();
    }
}
```

### `SysOperationServiceController` Key Methods

| Method | Purpose |
|---|---|
| `parmContractType()` | Sets the contract class type — the framework uses this to serialize/deserialize parameters |
| `parmServiceType()` | Sets the service class type — the framework instantiates this and calls `process()` |
| `startOperation()` | Starts the operation — if `runOn()` returns `RunOn::Batch`, this queues a batch job; otherwise runs synchronously |
| `parmRunOn()` | Override to specify execution target (`RunOn::Client`, `RunOn::Server`, `RunOn::Batch`) |
| `parmCaption()` | Override to set the operation's display name in the UI and batch job list |

### When to Use SysOperationServiceController vs RunBase

| Scenario | Use |
|---|---|
| Simple batch job with dialog input | `RunBase` / `RunBaseBatch` |
| Operation called from a form button | `RunBase` (simpler, faster) |
| Operation exposed via OData/REST | `SysOperationServiceController` |
| Operation called from Power Automate / Logic Apps | `SysOperationServiceController` |
| Operation needs contract validation | `SysOperationServiceController` (contract attributes provide validation) |
| Operation called from another X++ class | Either — `SysOperationServiceController` if you want to pass a contract object, `RunBase` for simplicity |

---

# Chapter 13: Event Handlers & Command Pattern

## 13.1 Event Handlers — Deep Dive

Event handlers are the **primary extension mechanism** in D365 F&O. They allow you to inject custom logic into standard code execution without modifying the original method.

### Event Handler Attributes

D365 F&O provides **three distinct event handler attributes** for different purposes:

| Attribute | Purpose | Parameter Type | Example |
|---|---|---|---|
| **`[PreHandlerFor(...)]`** | Runs **before** the standard method | `XppPrePostArgs` | `[PreHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]` |
| **`[PostHandlerFor(...)]`** | Runs **after** the standard method | `XppPrePostArgs` | `[PostHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]` |
| **`[SubscribesTo(...)]`** | Subscribes to **delegates** explicitly declared in the base class | Depends on delegate | `[SubscribesTo(classStr(MyClass), delegateStr(MyClass, myDelegate))]` |
| **`[DataEventHandler(...)]`** | Subscribes to **data events** (insert/update/delete) | `XppDataEventArgs` | `[DataEventHandler(tableStr(VendTable), DataEventType::Inserted)]` |

**Source:** [X++ Events](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-events)

> **Microsoft guidance on delegates:** Although you can subscribe to existing delegates, **do not create new delegates**. The Chain of Command (CoC) provides a richer, more robust, and more concise extension mechanism that supersedes delegates. Use CoC for method interception and pre/post event handlers for event-based reactions instead of creating custom delegates.

### Pre-Event Handler Example

```xpp
// Runs BEFORE VendInvoiceJour.validateWrite()
[PreHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
public static void VendInvoiceJour_PreValidateWrite(XppPrePostArgs _args)
{
    VendInvoiceJour vendInvoiceJour = _args.getThis();

    // Check if the vendor has a compliance code
    if (vendInvoiceJour.CreditMax > 500000 && vendInvoiceJour.ComplianceCode == '')
    {
        // Add validation error to prevent the write
        _args.setReturnValue(checkFailed('Compliance code required for vendors exceeding $500,000 credit limit'));
    }
}
```

### Post-Event Handler Example

```xpp
// Runs AFTER VendInvoiceJour.validateWrite()
[PostHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
public static void VendInvoiceJour_PostValidateWrite(XppPrePostArgs _args)
{
    VendInvoiceJour vendInvoiceJour = _args.getThis();

    // The standard validateWrite() has already run
    // Check if it succeeded (return value is accessible via args)
    if (_args.getReturnValue())
    {
        // Log the compliance check
        APComplianceLog::logCheck(vendInvoiceJour.RecId, ComplianceStatus::Validated);

        // Trigger integration event
        VendComplianceIntegration::onInvoiceValidated(vendInvoiceJour);
    }
}
```

### Event Handler Placement

| Placement | Syntax | When to Use |
|---|---|---|
| **Table-level** | `[PreHandlerFor(tableStr(VendTable), methodStr(VendTable, validateWrite))]` | The handler is logically tied to the table's data integrity rules — e.g., validation, field change reactions |
| **Class-level** | `[PreHandlerFor(classStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]` | The handler is a cross-cutting concern — e.g., logging, notification dispatch, integration triggers |

**Best practice:** Place table-level event handlers in a class named after the table (e.g., `VendTable_EventHandlers`). Place class-level handlers in a dedicated event handler class (e.g., `VendInvoiceJour_EventHandler`).

### Event Types

D365 F&O supports the following event mechanisms:

1. **Pre/Post Handlers** (`[PreHandlerFor]`/`[PostHandlerFor]`):
   - Wrap **any standard method** (table or class).
   - Use `XppPrePostArgs` to access the record (`args.getThis()`) and return value (`args.getReturnValue()`/`args.setReturnValue()`).

2. **Delegate Subscribers** (`[SubscribesTo]`):
   - Subscribe to **delegates** explicitly declared in the base class (e.g., `[EventHandlerResultAttribute]`).
   - Use `delegateStr` (not `methodStr`).
   - **Deprecated:** Do not create new delegates — use Chain of Command (CoC) instead.

3. **Data Event Handlers** (`[DataEventHandler]`):
   - Subscribe to **data events** (`Inserted`, `Updated`, `Deleted`).
   - Use `XppDataEventArgs` to access the record and event type.

**Note:** For **method overrides** (replacing behavior), use **Chain of Command (CoC)** via `[ExtensionOf(classStr(...))]`, not event handlers.

### Event Handler Execution Order

When multiple handlers subscribe to the same event:
1. **Pre-handlers** run first (in **unspecified order** — not guaranteed alphabetical).
2. The standard method executes.
3. **Post-handlers** run last (in **unspecified order**).

**Important:** Execution order among handlers is **not guaranteed** by the framework. Do not rely on alphabetical or registration order.
**Source:** [X++ Events](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-events)

### Event Handler Best Practices

1. **Keep handlers thin** — delegate to service classes or static utility methods; don't put business logic directly in the handler
2. **Don't call `super()` in event handlers** — event handlers don't participate in CoC chains; they are independent subscribers
3. **Use pre-events for validation** and post-events for side effects — this keeps the event handler pattern clean
4. **Avoid override-events unless necessary** — they make upgradeability harder because you've replaced standard behavior entirely
5. **Name handler classes consistently** — `VendTable_EventHandler`, `CustInvoiceJour_EventHandlers`, etc.

---

## 13.2 The Command Pattern — Menu Item → Class Chain

The Command pattern in D365 F&O connects user actions (menu item clicks) to business logic (class methods) through a chain of objects.

### The Chain

```
User clicks a menu item
    │
    ▼
MenuItem (MenuItemDisplay / MenuItemAction / MenuItemOutput)
    │  Property: Object = ClassName or FormName
    │
    ▼
Class::main()  or  FormRun.run()
    │
    ▼
Business logic executes
```

### MenuItem Types and Their Command Targets

| MenuItem Type | Class Property | What Happens When Clicked |
|---|---|---|
| **MenuItemDisplay** | `Object = FormName` | Opens the specified form |
| **MenuItemAction** | `Object = ClassName` | Calls `ClassName::main()` static method |
| **MenuItemOutput** | `Object = ReportClassName` | Runs the specified report (SSRS or legacy AX reports) |

**Source:** [Build forms and optimize for Finance and Operations](https://learn.microsoft.com/en-au/training/modules/build-forms-optimize-finance-operations/5-menu-items)

### The `main()` Static Method — The Entry Point

Every class that is the target of a `MenuItemAction` must have a `main(Args _args)` static method:

```xpp
class VendComplianceManager
{
    // This is the entry point when the menu item is clicked
    public static void main(Args _args)
    {
        VendComplianceManager manager = new VendComplianceManager();

        // If the menu item was triggered from a form, args.record() contains the current record
        if (_args && _args.record() && _args.record().TableId == tableNum(VendTable))
        {
            manager.parmVendTable(_args.record());
        }

        // Run the compliance check
        manager.checkCompliance();
    }

    // Instance method — the actual business logic
    public void checkCompliance()
    {
        VendTable vendTableLocal = this.parmVendTable();

        if (vendTableLocal.CreditMax > 500000 && vendTableLocal.ComplianceCode == '')
        {
            warning(strFmt('Vendor "%1" exceeds $500,000 credit limit but has no compliance code.',
                vendTableLocal.AccountNum));
        }
        else
        {
            info(strFmt('Vendor "%1" is compliant.', vendTableLocal.AccountNum));
        }
    }
}
```

### MenuItemAction for Navigation

When a form action needs to open another form, it uses the `MenuFunction` pattern:

```xpp
// From a button on Form A that opens Form B
public void clicked()
{
    Args args = new Args();
    args.name(formstr(ComplianceHistoryForm));
    args.record(element.args().record());  // Pass the current vendor record

    // Use MenuFunction to open the form via the menu item
    MenuFunction menuFunction = new MenuFunction(menuItemDisplayStr(ComplianceHistory), MenuItemType::Display);
    menuFunction.run(args);
}
```

---

## 13.3 Activity — Full Order-to-Cash Flow Implementation

> **Activity**: Implement a complete Order-to-Cash flow for a custom compliance module. The solution must include:
> 1. A `VendComplianceContract` class (data contract with `parmX()` accessors)
> 2. A `VendComplianceService` class (business logic with `process()` method)
> 3. A `VendComplianceController` class (extends `SysOperationServiceController`, entry point)
> 4. A `VendComplianceEventHandler` class with at least 2 event subscriptions:
>    - A **pre-event** on `VendInvoiceJour.validateWrite()` that checks the compliance code for high-credit vendors
>    - A **post-event** on `VendInvoiceJour.inserted()` that logs the compliance status to `APComplianceLog`
> 5. A `VendComplianceBatchJob` class (extends `RunBaseBatch`, with dialog, pack/unpack, run, and createJob)
> 6. Proper **MenuItemAction** navigation from a form button to the compliance dashboard form
> 7. A `MenuItemAction` menu item that triggers the `VendComplianceController::main()` method
>
> **Activity Hints** (Multiple Valid Approaches):
> - **Hint A — Service layer design**: Option A1 — use `SysOperationServiceController` with a contract class (recommended — modern, decoupled, testable). Option A2 — use `RunBase` with dialog input (simpler, but tightly coupled to UI). Option A3 — use a static utility class with no framework (not recommended — hard to test, no batch support, no OData exposure).
> - **Hint B — Event subscription placement**: Option B1 — table-level event handler on `VendInvoiceJour` (recommended — logically grouped with the table's data integrity concerns). Option B2 — class-level event handler in a dedicated `VendInvoiceJour_EventHandler` class (also valid — better for cross-cutting concerns). Option C — form-level event handler (not recommended for data integrity logic — only use for UI-specific behavior).
> - **Hint C — Batch job design**: Option C1 — extend `RunBaseBatch` with full dialog and batch integration (recommended — follows Microsoft patterns). Option C2 — use `RunBase` with `runOn() = RunOn::Server` for a simpler server-only job (valid for short operations that don't need batch queuing). Option C3 — use `SysOperationServiceController` with `runOn() = RunOn::Batch` for a contract-driven batch operation (modern but more complex).
> - **Hint D — Contract design**: Option D1 — use `[DataContractAttribute]` with `[DataMember]` on each property (recommended — enables OData exposure). Option D2 — use a simple class with public member variables (not recommended — no serialization support, no metadata).

### Expected Approach (Ideal — in detail)

#### Component 1: VendComplianceContract (Data Contract)

```xpp
[DataContractAttribute]
class VendComplianceContract
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;
    boolean generateReport;

    [DataMemberAttribute('VendTable'), SysOperationLabelAttribute('Vendor')]
    public VendTable parmVendTable(VendTable _vendTable = vendTable)
    {
        vendTable = _vendTable;
        return vendTable;
    }

    [DataMemberAttribute('ComplianceCode'), SysOperationLabelAttribute('Compliance Code')]
    public ComplianceCode parmComplianceCode(ComplianceCode _complianceCode = complianceCode)
    {
        complianceCode = _complianceCode;
        return complianceCode;
    }

    [DataMemberAttribute('FromDate'), SysOperationLabelAttribute('From Date')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    [DataMemberAttribute('ToDate'), SysOperationLabelAttribute('To Date')]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }

    [DataMemberAttribute('GenerateReport'), SysOperationLabelAttribute('Generate Report')]
    public boolean parmGenerateReport(boolean _generateReport = generateReport)
    {
        generateReport = _generateReport;
        return generateReport;
    }
}
```

**Design rationale:** The contract class is a pure data holder — no business logic, no database access. It uses the `parmX()` pattern with default parameters for getter/setter duality. The `[DataMember]` attributes enable OData serialization for external consumption.

#### Component 2: VendComplianceService (Business Logic)

```xpp
class VendComplianceService
{
    public VendComplianceContract process(VendComplianceContract _contract)
    {
        this.validateContract(_contract);

        VendTable vendTableLocal = VendTable::find(_contract.parmVendTable().AccountNum);

        // Process compliance declarations
        this.processDeclarations(vendTableLocal, _contract.parmFromDate(), _contract.parmToDate());

        // Optional report generation
        if (_contract.parmGenerateReport())
        {
            this.generateComplianceReport(vendTableLocal, _contract.parmFromDate(), _contract.parmToDate());
        }

        return _contract;
    }

    private void validateContract(VendComplianceContract _contract)
    {
        if (!_contract.parmVendTable())
        {
            throw error('Vendor is required.');
        }
        if (_contract.parmFromDate() > _contract.parmToDate())
        {
            throw error('From date cannot be after to date.');
        }
    }

    private void processDeclarations(VendTable _vendTable, FromDate _from, ToDate _to)
    {
        APCustomsDeclaration declaration;

        while select declaration
            where declaration.VendTableRecId == _vendTable.RecId
            && declaration.DeclDate >= _from
            && declaration.DeclDate <= _to
        {
            // Validate each declaration
            if (declaration.DeclDate > today())
            {
                warning(strFmt('Declaration %1 has a future date.', declaration.DeclId));
                continue;
            }

            // Process the declaration
            declaration.Status = ComplianceStatus::Processed;
            declaration.update();
        }
    }

    private void generateComplianceReport(VendTable _vendTable, FromDate _from, ToDate _to)
    {
        SrsReportRunController reportController = new SrsReportRunController();
        // ... configure report with contract parameters ...
        reportController.run();
    }
}
```

#### Component 3: VendComplianceController (SysOperationServiceController)

```xpp
class VendComplianceController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VendComplianceController controller = new VendComplianceController();
        VendComplianceContract contract = new VendComplianceContract();

        // Populate contract from args if triggered from a form
        if (_args && _args.record() && _args.record().TableId == tableNum(VendTable))
        {
            contract.parmVendTable(_args.record());
        }

        controller.parmContractType(classStr(VendComplianceContract));
        controller.parmServiceType(classStr(VendComplianceService));
        controller.parmCaption('Vend Compliance Check');
        controller.startOperation();
    }
}
```

#### Component 4: VendComplianceEventHandler (Two Event Subscriptions)

```xpp
class VendComplianceEventHandler
{
    // Pre-event: validate compliance code before standard validateWrite runs
    [PreHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
    public static void VendInvoiceJour_onValidateWrite_Pre(XppPrePostArgs _args)
    {
        VendInvoiceJour _this = _args.getThis();

        if (_this.CreditMax > 500000 && _this.ComplianceCode == '')
        {
            // Pre-handler runs before standard validateWrite; checkFailed sets the return value to false
            // preventing the write from completing
            _args.setReturnValue(
                checkFailed('Compliance code is required for vendors exceeding $500,000 credit limit.'));
        }
    }

    // Post-event: log compliance status after a new invoice is inserted
    [SubscribesTo(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, inserted()), EventExecution::Post)]
    public static void VendInvoiceJour_onInserted_Post(VendInvoiceJour _this)
    {
        APComplianceLog complianceLog;

        complianceLog.initValue();
        complianceLog.VendTableRecId = _this.RecId;
        complianceLog.VendAccount = _this.AccountNum;
        complianceLog.InvoiceDate = _this.InvoiceDate;
        complianceLog.Status = ComplianceStatus::Logged;

        // Check if compliance code exists
        if (_this.ComplianceCode != '')
        {
            complianceLog.ComplianceCode = _this.ComplianceCode;
            complianceLog.Status = ComplianceStatus::Compliant;
        }
        else
        {
            complianceLog.Status = ComplianceStatus::MissingCode;
        }

        complianceLog.insert();
    }
}
```

**Design rationale:** The pre-event handles validation (preventing non-compliant invoices from being posted), while the post-event handles logging (recording compliance status for audit purposes). This separation follows the principle that pre-events are for validation/input modification and post-events are for side effects/logging.

#### Component 5: VendComplianceBatchJob (RunBaseBatch)

```xpp
class VendComplianceBatchJob extends RunBaseBatch
{
    VendTable vendTable;
    ComplianceCode complianceCode;
    FromDate fromDate;
    ToDate toDate;
    boolean generateReport;

    // Dialog
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        dialog.addFieldValue(typeid(VendTable), vendTable, 'Vendor');
        dialog.addFieldValue(typeid(ComplianceCode), complianceCode, 'Compliance Code');
        dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');
        dialog.addFieldValue(typeid(boolean), generateReport, 'Generate Report');
        return dialog;
    }

    // Pack
    public container pack()
    {
        return [vendTable, complianceCode, fromDate, toDate, generateReport];
    }

    // Unpack
    public boolean unpack(container _packedClass)
    {
        vendTable = _packedClass.packGet(1);
        complianceCode = _packedClass.packGet(2);
        fromDate = _packedClass.packGet(3);
        toDate = _packedClass.packGet(4);
        generateReport = _packedClass.packGet(5);
        return true;
    }

    // Run on batch tier
    public RunOn runOn()
    {
        return RunOn::Batch;
    }

    // Business logic
    public void run()
    {
        VendTable vendTableLocal = VendTable::find(vendTable.AccountNum);
        APCustomsDeclaration declaration;

        while select declaration
            where declaration.VendTableRecId == vendTableLocal.RecId
            && declaration.DeclDate >= fromDate
            && declaration.DeclDate <= toDate
        {
            declaration.Status = ComplianceStatus::Processed;
            declaration.update();
        }

        if (generateReport)
        {
            // Generate SSRS report
        }

        info(strFmt('Compliance batch job completed for vendor "%1".', vendTableLocal.AccountNum));
    }

    // Batch metadata
    public BatchHeader batchInfo()
    {
        BatchHeader batchHeader = super::batchInfo();
        batchHeader.parmDescription('Vend Compliance Batch Job');
        batchHeader.parmBatchGroup('BATCHGROUP1');
        batchHeader.parmExecutionStyle(BatchExecutionStyle::OnDemand);
        return batchHeader;
    }

    // Static entry point
    public static void main(Args _args)
    {
        VendComplianceBatchJob job = new VendComplianceBatchJob();
        if (_args && _args.record())
        {
            job.parmVendTable(_args.record());
        }
        if (job.prompt())
        {
            job.run();
        }
    }
}
```

#### Component 6: MenuItemAction Navigation

```xpp
// MenuItemAction: Object = VendComplianceController, Method = main
// This menu item triggers the SysOperationServiceController

// From a form button, navigation to the compliance dashboard:
public void clicked()
{
    Args args = new Args();
    args.name(formstr(ComplianceDashboardForm));
    args.record(element.args().record());

    MenuFunction menuFunction = new MenuFunction(
        menuItemDisplayStr(ComplianceDashboard), MenuItemType::Display);
    menuFunction.run(args);
}
```

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeOrderToCashCompliance</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeOrderToCashComplianceEnabled</ConfigurationKey>
</ModelManifest>
```

---

### Remaining Chapters — Detailed Outline (Content to follow)


# Chapter 14: Extensibility Deep Dive

## 14.1 CoC vs. Override vs. Event Handler — When Each Is Appropriate

D365 F&O provides three distinct mechanisms for extending standard code. Understanding when to use each is one of the most important architectural decisions you'll make.

### The Three Mechanisms

| Mechanism | How It Works | Upgrade Safety | Complexity | Best For |
|---|---|---|---|---|
| **Chain of Command (CoC)** | Override a standard method via `[ExtensionOf(...)]`; call `next` to chain to the next implementation | ✅ High — standard method still runs; your code is additive | Low | Modifying the behavior of a standard method where the base logic should still execute |
| **Event Handler** | Subscribe to a method's pre/post/override event using `[SubscribesTo(...)]` | ✅ High — completely decoupled from the base method | Medium | Cross-cutting concerns (logging, notifications, integration triggers) where multiple subscribers may need to react independently |
| **Direct Override** | Replace the standard method entirely by modifying the base class | ❌ Low — overwritten by Microsoft CUs | Low (but dangerous) | **Never** for customer code |

### Decision Matrix

| Scenario | Recommended Pattern | Why |
|---|---|---|
| Add validation to `VendInvoiceJour.validateWrite()` | **CoC** (override) | The standard validation should still run; you're adding a check before or after |
| Log every time an invoice is posted | **Event Handler** (post-event) | Multiple solutions may want to react to the same event; decoupled architecture |
| Completely replace standard invoice posting logic | **Override-event** (use sparingly) | You've replaced standard behavior entirely — this makes upgradeability harder |
| Add a field to `VendTable` | **Table Extension** (not CoC) | CoC is for method behavior; table extensions are for adding fields |
| Add a button that opens a new form | **Form Extension** + CoC | The form extension adds the button; CoC handles the navigation logic |

### The Golden Rule

> **If the standard method's logic is still valuable and you just want to add to it, use CoC. If you need multiple independent reactions to the same point in execution, use Event Handlers. If you need to completely replace standard behavior, use an Override-event (and document why).**

---

## 14.2 `next` in CoC — Automatic vs. Explicit Behavior

The `next` keyword is the mechanism that connects your extension to the standard code chain. Understanding how it works is critical to avoiding bugs.

### How `next` Works in CoC

When you override a method using CoC, calling `next` invokes the **next class in the chain**. The chain is resolved at runtime based on the model layer and dependency order.

```xpp
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_ComplianceExtension
{
    // Override validateWrite() — add compliance check
    public boolean validateWrite()
    {
        boolean ret;

        // Call next FIRST — standard validations run
        ret = next validateWrite();

        // Add custom validation AFTER standard validations pass
        if (ret && this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            ret = checkFailed('Compliance code required for vendors exceeding $500,000 credit limit');
        }

        return ret;
    }
}
```

### `next` Position Rules

| Method Type | `next` Position | Why |
|---|---|---|
| `validateWrite()` | **FIRST** — call `next` before custom logic | Standard validations must run first; if they fail, your custom logic is irrelevant |
| `modifiedField()` | **LAST** — call `next` after custom logic | Your field change logic should run before the standard framework processes the change |
| `executeQuery()` | **LAST** — call `next` after adding ranges | `next` executes the query; filters added after it are ignored |
| `active()` | **LAST** — call `next` after custom logic | Standard active logic should run after your setup |
| `run()` | **FIRST or LAST** — depends on whether you need to wrap the standard behavior | Wrapping pattern: `next` first, then post-processing; or `next` last, then pre-processing |

### Automatic vs. Explicit `next`

In X++, `next` is **always explicit** — you must write it yourself. There is no automatic chaining. This is different from some languages where the base class method is called automatically.

**Common mistake — forgetting `next`:**
```xpp
// ❌ WRONG — forgetting super() breaks the chain
public boolean validateWrite()
{
    // Custom validation only — standard validations are SKIPPED
    if (this.CreditMax > 500000 && this.ComplianceCode == '')
    {
        return checkFailed('Compliance code required');
    }
    return true;  // Standard validations never run!
}
```

**Correct version:**
```xpp
// ✅ CORRECT — next is called, standard validations still run
public boolean validateWrite()
{
    boolean ret;
    ret = next validateWrite();  // Standard validations execute here

    if (ret && this.CreditMax > 500000 && this.ComplianceCode == '')
    {
        ret = checkFailed('Compliance code required');
    }
    return ret;
}
```

### Infinite Loop Pitfall

If you accidentally call `next` in a way that creates a circular chain, you get an infinite loop and eventually a stack overflow.

**How infinite loops happen:**
1. **Forgetting `next` in a CoC override** — the standard method is never called, but your override is called again on the next invocation (in some scenarios)
2. **Calling the wrong `next`** — calling `next` on a method that doesn't exist in the base class, causing the compiler to resolve to an unexpected method
3. **Event handler calling the standard method directly** — if an event handler calls the standard method, and the standard method triggers the event again, you get a loop

**How to avoid infinite loops:**
- Always verify the method you're overriding actually has a `next` call in the standard code
- Use the **pre-event/post-event** pattern instead of override-event when you just need to react to a method execution
- Test with a simple case first — set a breakpoint on `next` to verify the chain executes correctly

---

## 14.3 `ExtensionOf(...)` — The Extension Syntax

The `ExtensionOf` attribute is the mechanism that tells the D365 F&O framework which base class, table, form, or view you are extending.

### ExtensionOf for Classes

```xpp
// Extending a class
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_ComplianceExtension
{
    // Override validateWrite() on VendInvoiceJour
    public boolean validateWrite()
    {
        boolean ret;
        ret = next validateWrite();
        if (ret && this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            ret = checkFailed('Compliance code required');
        }
        return ret;
    }
}
```

### ExtensionOf for Tables

```xpp
// Extending a table — adding a field
[ExtensionOf(tableStr(VendTable))]
final class VendTable_ComplianceExtension
{
    ComplianceCode complianceCode;
}
```

### ExtensionOf for Forms

```xpp
// Extending a form — adding a data source or control
[ExtensionOf(formStr(CustTable))]
final class CustTable_FormExtension
{
    // Add a new data source
    CustComplianceLog complianceLog_ds;

    // Add a new control to the design
    // (Controls are added via the extension form design node in the AOT)
}
```

### ExtensionOf for Views

```xpp
// Extending a view — adding a new data source
[ExtensionOf(viewStr(VendorContactView))]
final class VendorContactView_Extension
{
    // Add a new data source to the view
    CustComplianceLog complianceLog_ds;
}
```

### ExtensionOf Syntax Reference

| Target | Syntax | Example |
|---|---|---|
| Class | `ExtensionOf(classStr(ClassName))` | `[ExtensionOf(classStr(VendInvoiceJour))]` |
| Table | `ExtensionOf(tableStr(TableName))` | `[ExtensionOf(tableStr(VendTable))]` |
| Form | `ExtensionOf(formStr(FormName))` | `[ExtensionOf(formStr(CustTable))]` |
| View | `ExtensionOf(viewStr(ViewName))` | `[ExtensionOf(viewStr(VendorContactView))]` |
| EDT | `ExtensionOf(extendedTypeStr(EDTName))` | `[ExtensionOf(extendedTypeStr(CustAccount))]` |
| Enum | `ExtensionOf(enumStr(EnumName))` | `[ExtensionOf(enumStr(VendInvoiceStatus))]` |
| Menu | `ExtensionOf(menuStr(MenuName))` | `[ExtensionOf(menuStr(File))]` |

### `final` Keyword

Always mark extension classes as `final` unless you explicitly intend for them to be further extended. This prevents unintended subclassing and makes the code's intent clear.

```xpp
// ✅ Recommended — extension classes are typically final
[ExtensionOf(tableStr(VendTable))]
final class VendTable_ComplianceExtension
{
    // ...
}
```

---

## 14.4 Overloading vs. Overriding in X++

Understanding the difference between overloading and overriding is essential for correct CoC implementation.

### Overloading (Method Name Same, Different Signature)

X++ does **not** support method overloading in the traditional sense (same method name, different parameter types). If you define two methods with the same name in the same class, the compiler will flag an error.

**What this means for CoC:** You cannot overload a standard method by adding a variant with different parameters. You must override the exact method signature.

### Overriding (Replacing Base Method Implementation)

Overriding is what CoC does — you provide a new implementation for a method that exists in the base class.

```xpp
// Overriding validateWrite() on VendInvoiceJour
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_OverrideExtension
{
    // This OVERRIDES the standard validateWrite() method
    // Your implementation replaces the standard one in the chain
    public boolean validateWrite()
    {
        // Your custom logic
        // ...

        // Call next to chain to the next implementation
        return next validateWrite();
    }
}
```

### Overriding Rules

1. **The method signature must match exactly** — same name, same parameter types, same return type
2. **You cannot reduce visibility** — if the base method is `public`, your override must be `public`
3. **Static methods CAN be overridden via CoC** — but your extension method must also be declared `static`, matching the base method's accessibility and staticness exactly. *Exception:* Static methods on **forms** cannot be wrapped (forms are not true classes).
4. **You cannot override `final` methods** — unless the method is explicitly marked with `[Wrappable(true)]`, which allows wrapping even if `final` is present.
**Source:** [Method wrapping and Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/method-wrapping-coc)

### When You Can't Override

Some standard methods are marked `final` in the D365 F&O codebase, meaning they cannot be overridden via CoC **unless** the method is explicitly marked with `[Wrappable(true)]`. For these methods, you must use **event handlers** instead.

| Method Pattern | Overrideable via CoC? | Alternative |
|---|---|---|
| `validateWrite()` | ✅ Yes | — |
| `executeQuery()` | ✅ Yes | — |
| `modifiedField()` | ✅ Yes | — |
| `run()` | ✅ Yes | — |
| `init()` | ✅ Yes | — |
| `static` methods (non-form) | ✅ Yes | — |
| `static` methods on forms | ❌ No | Event Handler |
| `final` methods without `[Wrappable(true)]` | ❌ No | Event Handler |

**How to check if a method is overrideable:**
- If it has the `final` keyword **and no `[Wrappable(true)]` attribute**, it cannot be overridden via CoC.
- Static methods on **forms** cannot be wrapped (forms are not true classes).
- Static methods on **classes/tables** can be wrapped if the extension method is also `static`.

---

## 14.5 CoC Pitfalls — Common Mistakes and How to Avoid Them

### Pitfall 1: Infinite Loops from Forgetting `next`

**The problem:** If your CoC override doesn't call `next`, the standard method's logic is skipped. In some cases, this can cause the framework to call your override again, creating an infinite loop.

**Example:**
```xpp
// ❌ DANGEROUS — no next call, potential infinite loop
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_BadExtension
{
    public boolean validateWrite()
    {
        // Standard validation never runs
        // Framework may re-invoke this method expecting standard behavior
        if (this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            return checkFailed('Compliance code required');
        }
        return true;  // Skips all standard validations!
    }
}
```

**Fix:** Always call `next` unless you have an explicit reason not to (and even then, document why).

### Pitfall 2: Wrong `next` Position

**The problem:** Calling `next` at the wrong point in the method changes the behavior of your code.

**Example — wrong position in `executeQuery()`:**
```xpp
// ❌ WRONG — next called first, so your filter is ignored
public void executeQuery()
{
    next executeQuery();  // Query executes HERE — your filter below is never applied

    // This code runs AFTER the query has already executed
    QueryBuildDataSource qbd = element.query().dataSourceTable(tableNum(VendTable));
    QueryBuildRange qbr = qbd.addRange(fieldNum(VendTable, AccountNum));
    qbr.value(queryValue('C0001'));
}
```

**Fix:**
```xpp
// ✅ CORRECT — next called LAST, after all filters are added
public void executeQuery()
{
    QueryBuildDataSource qbd = element.query().dataSourceTable(tableNum(VendTable));
    QueryBuildRange qbr = qbd.addRange(fieldNum(VendTable, AccountNum));
    qbr.value(queryValue('C0001'));

    next executeQuery();  // Query executes HERE — with your filter applied
}
```

### Pitfall 3: Wrong Event Timing (Pre vs. Post)

**The problem:** Using a pre-event when you need a post-event (or vice versa) causes logic to execute at the wrong point in the lifecycle.

**Example — using pre-event for logging:**
```xpp
// ❌ WRONG — pre-event fires BEFORE the standard method
// The invoice hasn't been posted yet, so logging "invoice posted" is misleading
[SubscribesTo(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
public static void VendInvoiceJour_onValidateWrite_Pre(VendInvoiceJour _this)
{
    info('Invoice has been posted');  // Misleading — it hasn't been posted yet!
}
```

**Fix:**
```xpp
// ✅ CORRECT — post-event fires AFTER the standard method
[SubscribesTo(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite), EventExecution::Post)]
public static void VendInvoiceJour_onValidateWrite_Post(VendInvoiceJour _this)
{
    if (_this.validateWrite)
    {
        info('Invoice validation succeeded');  // Accurate — validation has completed
    }
}
```

### Pitfall 4: CoC on a Method That Doesn't Participate in CoC

**The problem:** Not all standard methods participate in the CoC chain. Some methods are `static` or are called directly without going through the chain.

**Example:**
```xpp
// ❌ WON'T WORK — static methods don't participate in CoC
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_StaticExtension
{
    // This override will NOT be called because the standard method is static
    public static void someStaticMethod()
    {
        // Your code here — never executed
    }
}
```

**Fix:** For static methods, use event handlers or call the static method directly from your code.

### Pitfall 5: Extension Class Lifecycle — When Extensions Are Loaded

Extension classes are loaded **when the AOS starts** (or when the model is deployed). They are not loaded on-demand. This has important implications:

1. **Model dependency matters** — if your extension model depends on a base model, the base model must be deployed first. If the base model is missing, your extension will fail to load.
2. **Layer resolution applies** — if two models define extensions for the same class, the highest-layer extension wins. This means your CUS-layer extension will take precedence over an ISV-layer extension, and USR-layer extensions take precedence over CUS.
3. **Restart required** — after deploying a new extension, the AOS must be recycled for the extension to take effect. Simply deploying the model is not enough.

### Pitfall 6: Modifying Extension Class Behavior After Deployment

Once an extension class is loaded into the AOS, modifying it requires:
1. Rebuilding the model
2. Deploying the new `.axmodel`
3. Recycling the AOS

**This is different from event handlers**, which can sometimes be hot-reloaded depending on the framework version. For CoC overrides, always plan for an AOS recycle after deployment.

---

## 14.6 Extension Class Lifecycle — In Detail

### How Extensions Interact with the Base Class

```
[1] AOS starts → loads all models from the model store
    │
[2] For each class, the framework resolves the CoC chain:
    │   • Finds the highest-layer extension for the class
    │   • Links extensions in layer order (USR → CUS → VAR → ISV → SYS)
    │   • Builds an internal chain of method calls
    │
[3] When a standard method is called:
    │   • The framework starts at the highest-layer extension
    │   • That extension calls next → next extension in chain
    │   • The chain continues until the base class method is reached
    │
[4] When a new model is deployed:
    │   • The model store is updated
    │   • AOS is recycled → extensions are reloaded
    │   • The CoC chain is rebuilt with the new extension
    │
[5] When a model is removed:
    │   • AOS is recycled → extensions are reloaded
    │   • The CoC chain is rebuilt without the removed extension
    │   • The base class method is now called directly
```

### Model Dependency Implications

Your extension model **must** declare a dependency on the model that contains the base class. If you don't, the deployment will fail because the framework cannot resolve the base class.

```xml
<ModelManifest>
  <Name>MyComplianceExtension</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <!-- Required: the model containing VendInvoiceJour -->
    <ModelReference>
      <Name>ApplicationSuite</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
  </References>
</ModelManifest>
```

### Extension Loading Order

Extensions are loaded in **layer order** — higher layers are resolved first:

1. `CUS` (customer extensions — highest priority for customer code)
2. `VAR` (Microsoft variation extensions)
3. `ISV` (ISV partner extensions)
4. `SYS` (Microsoft system framework — lowest priority)

When multiple extensions target the same method, the **highest-layer extension's `next` call** determines which extension runs next in the chain.

---

## 14.7 Activity — Extend AP Invoice Validation Three Ways

> **Activity**: Extend the standard Accounts Payable invoice validation (`VendInvoiceJour.validateWrite()`) using three different extension approaches:
> 1. **CoC Override** — override `validateWrite()` directly on `VendInvoiceJour`
> 2. **Event Handler** — subscribe to the `validateWrite` event (pre-event)
> 3. **Class Extension** — extend the `VendInvoiceJour` class with a new method that is called from a menu item
>
> For each approach, implement the same business rule: **a compliance code is required when the vendor's credit limit exceeds $500,000**.
>
> After implementing all three, explain the trade-offs for each approach in terms of:
> - Upgradeability (how well it survives Microsoft CUs)
> - Maintainability (how easy it is to find and modify the logic)
> - Performance (any overhead introduced)
> - Testability (how easy it is to unit test)
> - Reusability (can the logic be applied to other tables/methods)
>
> **Activity Hints** (Multiple Valid Approaches):
>
> - **Hint A — CoC Override approach**: Option A1 — override `validateWrite()` directly in an `[ExtensionOf(classStr(VendInvoiceJour))]` class, calling `next` first then adding your check (recommended for this scenario — straightforward, debuggable). Option A2 — use a `construct()` pattern to create a validator class from within the CoC override (more testable but more complex).
>
> - **Hint B — Event Handler approach**: Option B1 — use a pre-event `[SubscribesTo(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]` that adds the compliance check (recommended — decoupled, multiple subscribers possible). Option B2 — use a post-event to log the compliance status after validation completes (different concern — logging, not validation). Option B3 — use both pre-event (for validation) and post-event (for logging) to demonstrate the pattern.
>
> - **Hint C — Class Extension approach**: Option C1 — create a new class with a `checkCompliance()` method that is called from a menu item or button (recommended for the class extension pattern — clean separation). Option C2 — extend `VendInvoiceJour` with a new instance method that can be called from the form (more integrated but tighter coupling). Option C3 — use a `RunBase` class that validates compliance as a batch operation (for bulk validation scenarios).
>
> - **Hint D — Trade-off analysis**: Consider that CoC overrides are the most straightforward for method behavior changes but create tight coupling to the base method. Event handlers are the most decoupled and support multiple subscribers but have less predictable execution order. Class extensions with new methods are the most reusable but require the caller to know about the extension class.

### Expected Approach (Ideal — in detail)

#### Approach 1: CoC Override

```xpp
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_ComplianceCocExtension
{
    /// <summary>
    /// Override validateWrite() to enforce compliance code for high-credit vendors.
    /// Uses CoC chain — standard validations still run via next.
    /// </summary>
    public boolean validateWrite()
    {
        boolean ret;

        // Call next FIRST — standard D365 validations run
        ret = next validateWrite();

        // Add custom compliance validation
        if (ret && this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            ret = checkFailed(
                'Compliance code is required for vendors exceeding $500,000 credit limit.');
        }

        return ret;
    }
}
```

**Trade-offs:**
- **Upgradeability**: ✅ High — the standard `validateWrite()` is untouched; your extension survives CUs
- **Maintainability**: ✅ Good — the override is clearly visible in the AOT under `Classes\VendInvoiceJour_ComplianceCocExtension`
- **Performance**: ✅ Minimal — one additional `if` check per `validateWrite()` call
- **Testability**: ⚠️ Moderate — requires an AOS connection to test; can be tested with `RunBase`-style unit tests
- **Reusability**: ❌ Low — this is specific to `VendInvoiceJour`; to apply to other tables, you'd need a separate override

#### Approach 2: Event Handler (Pre-Event)

```xpp
class VendInvoiceJour_EventHandler
{
    /// <summary>
    /// Pre-event handler for VendInvoiceJour.validateWrite().
    /// Checks compliance code for high-credit vendors before standard validation runs.
    /// </summary>
    [PreHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
    public static void VendInvoiceJour_onValidateWrite_Pre(XppPrePostArgs _args)
    {
        VendInvoiceJour _this = _args.getThis();

        if (_this.CreditMax > 500000 && _this.ComplianceCode == '')
        {
            // Pre-handler runs before standard validateWrite; setReturnValue(checkFailed())
            // causes validateWrite() to return false, preventing the write.
            _args.setReturnValue(
                checkFailed('Compliance code is required for vendors exceeding $500,000 credit limit.'));
        }
    }

    /// <summary>
    /// Post-event handler for VendInvoiceJour.validateWrite().
    /// Logs compliance status after validation completes.
    /// </summary>
    [PostHandlerFor(tableStr(VendInvoiceJour), methodStr(VendInvoiceJour, validateWrite))]
    public static void VendInvoiceJour_onValidateWrite_Post(XppPrePostArgs _args)
    {
        if (_this.validateWrite)
        {
            APComplianceLog::logCheck(_this.RecId, ComplianceStatus::Validated);
        }
        else
        {
            APComplianceLog::logCheck(_this.RecId, ComplianceStatus::Failed);
        }
    }
}
```

**Trade-offs:**
- **Upgradeability**: ✅ High — completely decoupled from the base method; standard code changes don't affect the handler
- **Maintainability**: ✅ Good — event handlers are centralized in a dedicated class; easy to find all subscriptions
- **Performance**: ⚠️ Slight overhead — event dispatch mechanism adds a small cost per invocation
- **Testability**: ✅ Good — event handlers can be unit tested independently of the base method
- **Reusability**: ✅ High — the same event handler class can subscribe to multiple methods; multiple handlers can subscribe to the same event

#### Approach 3: Class Extension with New Method

```xpp
[ExtensionOf(classStr(VendInvoiceJour))]
final class VendInvoiceJour_ComplianceClassExtension
{
    /// <summary>
    /// New method on VendInvoiceJour that checks compliance.
    /// Called from a menu item or form button — not automatically triggered.
    /// </summary>
    public ComplianceStatus checkCompliance()
    {
        if (this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            return ComplianceStatus::MissingCode;
        }
        return ComplianceStatus::Compliant;
    }
}
```

**Trade-offs:**
- **Upgradeability**: ✅ High — adds a new method; doesn't modify standard behavior
- **Maintainability**: ⚠️ Moderate — the method is on the extended class but must be explicitly called; easy to miss if developers don't know it exists
- **Performance**: ✅ Minimal — only runs when explicitly called
- **Testability**: ✅ Good — can be tested in isolation by creating a `VendInvoiceJour` instance and calling `checkCompliance()`
- **Reusability**: ✅ High — the pattern of adding a new method can be applied to any table; other developers can call `vendInvoiceJour.checkCompliance()` from anywhere

#### Which Approach Is Best?

For this specific scenario (enforcing a business rule at validation time), **Approach 1 (CoC Override)** is the recommended approach because:
1. It's the most straightforward and debuggable
2. The standard `validateWrite()` chain is preserved via `next`
3. The validation runs automatically for every invoice — no risk of developers forgetting to call it
4. It follows the Microsoft-documented pattern for modifying standard table method behavior

**Approach 2 (Event Handler)** is better when:
- Multiple independent solutions need to react to the same event
- You want to log or notify without modifying the validation logic
- You need to decouple the compliance check from the invoice validation

**Approach 3 (Class Extension)** is better when:
- The compliance check is an optional/manual action (not automatic)
- You want to expose the check as a reusable method callable from multiple places
- You're building a framework or utility class that other developers will use

## 14.8 Extensibility Attributes — Hookable, Wrappable, Replaceable

Microsoft provides three attributes that control how methods can be extended:

| Attribute | Controls | Default for public/protected | Opt-out |
|---|---|---|---|
| `[Hookable]` | Pre/post event handler subscription | Hookable | `[Hookable(false)]` |
| `[Wrappable]` | Chain of Command (CoC) wrapping | Wrappable | `[Wrappable(false)]` |
| `[Replaceable]` | CoC without mandatory `next` call | Not replaceable | N/A (opt-in only) |

### Hookable

If a method is **hookable**, extenders can subscribe to pre-events (`[PreHandlerFor]`) and post-events (`[PostHandlerFor]`).

- For **public** methods, you can opt out by adding `[Hookable(false)]`
- You can opt in for **private** and **protected** methods by adding `[Hookable(true)]`
- If a method is `[Hookable(false)]`, it is also **not wrappable**

```xpp
class AnyClass1
{
    [Hookable(false)]
    public void anyMethod() { ... }  // Cannot be wrapped or hooked
}
```

### Wrappable

If a method is **wrappable**, extenders can wrap it by using Chain of Command (CoC). Extenders must call `next`.

- For **protected** and **public** methods, you can opt out by adding `[Wrappable(false)]`
- You cannot opt in for **private** methods
- Final methods are not wrappable unless marked `[Wrappable(true)]`

```xpp
class AnyClass2
{
    [Wrappable(false)]
    public void doSomething(str message) { ... }  // Cannot be wrapped by CoC

    [Wrappable(true)]
    final public void doSomethingElse(str message) { ... }  // Final method made wrappable
}
```

### Replaceable

If a method is **replaceable**, extenders can wrap it by using CoC, but they don't have to unconditionally call `next`. Although extenders can break the chain, the expectation is that they only conditionally break it. The compiler does not enforce calls to `next` for replaceable methods.

To be replaceable, a method must also be **wrappable**. Opt in by adding `[Replaceable]`.

```xpp
class AnyClass3
{
    [Replaceable]
    public str convertEnumToStr(MyEnum _enumValue)
    {
        switch (_enumValue)
        {
            case MyEnum::OptionA: return "Option A";
            case MyEnum::OptionB: return "Option B";
            default: throw error("Unknown enum value");
        }
    }
}
```

**Best practices for `[Replaceable]`:**
- ✅ Do make sure methods with `[Replaceable]` have XML documentation describing the responsibility of the method
- ❌ Don't use `[Replaceable]` to let consumers skip the replaced logic and do nothing
- ❌ Don't use `[Replaceable]` for factory methods when `SysExtension` can be used instead
- ❌ Avoid using `[Replaceable]` when the method changes database or class state
- ❌ Avoid using `[Replaceable]` if the method performs multiple operations — refactor into separate methods instead

---

### Remaining Chapters — Detailed Outlines

### Remaining Chapters — Detailed Outlines


# Chapter 15: Security Model

## 15.1 The Security Hierarchy — Permission → Privilege → Duty → Role → User

D365 F&O uses a **four-tier security hierarchy** that controls every action a user can perform. Understanding this hierarchy is essential for designing secure customizations.

### The Four Tiers

```
Security Role
    │
    ├── Duty 1
    │       ├── Privilege 1.1
    │       │       ├── Permission (Table: VendTable, Access: Read)
    │       │       └── Permission (Table: VendInvoiceJour, Access: Create)
    │       └── Privilege 1.2
    │               └── Permission (Table: APComplianceLog, Access: Write)
    │
    ├── Duty 2
    │       └── Privilege 5.1
    │               └── Permission (Table: VendTable, Access: Edit)
    │
    └── Duty 3
            └── Privilege 9.1
                    └── Permission (Table: CustTable, Access: Read)
```

### Tier Descriptions

| Tier | Purpose | Example |
|---|---|---|
| **Security Role** | Top-level assignment to a user | `ComplianceOfficer`, `APManager`, `InvoiceProcessor` |
| **Duty** | A collection of related privileges | `APViewer`, `APProcessor`, `ComplianceAdmin` |
| **Privilege** | Granular access to specific tables and fields | `VendTableRead`, `VendInvoiceJourCreate`, `APComplianceLogWrite` |
| **Permission** | The most granular level — specific table + access level + optionally specific fields | `VendTable` → Read, `VendInvoiceJour` → Create + Edit |

### How Security is Enforced

1. A user is assigned one or more **Security Roles** in the **User Administration** form (`Security > Users > Users`)
2. Each role contains **Duties**
3. Each duty contains **Privileges**
4. Each privilege contains **Permissions** (table-level and optionally field-level)
5. At runtime, the framework checks the user's roles against the required permissions for every action
6. If the user lacks the required permission, the action is blocked and an error is shown

### The Security Role Assignment

```xpp
// Security roles are assigned in the User Administration form
// Not programmatically in most cases — but can be managed via code

// To check if the current user has a specific role:
boolean hasRole = SecurityRole::hasRole(SecurityRole::find('ComplianceOfficer').RecId);
```

### Security in the Extension Model

When you create custom objects in an extension model, the security model must be designed as part of the extension. Key considerations:

1. **Custom tables** need their own Configuration Key and security model
2. **Table extensions** inherit the security model of the base table — no additional permissions needed for added fields
3. **Form extensions** need menu item permissions for any new navigation items
4. **Report extensions** need output permissions for any new reports
5. **CoC overrides** do not change security requirements — the base method's security context applies
6. **Event handlers** run in the context of the base method — they inherit the base method's permissions

**Critical Rule:** Extensions never bypass the base security model. If a user doesn't have permission to access a table, your extension code cannot grant that access. The security framework checks permissions before any X++ code executes.

---

## 15.2 Access Levels — See, Create, Edit, Delete

Each permission in a privilege specifies an **AccessLevel** that controls what operations are allowed on the table.

| AccessLevel | Value | What It Allows |
|---|---|---|
| **See** | `AccessLevel::See` | Read-only — can view records, run queries, open forms that display data |
| **Create** | `AccessLevel::Create` | Can insert new records into the table |
| **Edit** | `AccessLevel::Edit` | Can modify existing records (implies See) |
| **Delete** | `AccessLevel::Delete` | Can delete records (implies See and Edit) |
| **Admin** | `AccessLevel::Admin` | Full control — See, Create, Edit, Delete, and administrative operations |

### Access Level Inheritance

Access levels are **cumulative** — higher levels include the permissions of lower levels:

- `Edit` includes `See` (you must be able to see a record before you can edit it)
- `Delete` includes `See` and `Edit` (you must be able to see and edit a record before you can delete it)
- `Admin` includes all levels

### Setting Access Levels on Privileges

```
Privilege: APComplianceViewer
├── Permission: VendTable → See
├── Permission: VendInvoiceJour → See
├── Permission: APComplianceLog → See + Create
└── Permission: APComplianceLog → Edit (field-level: only ComplianceCode, Status)
```

In the AOT, each privilege has a **Permissions** node where you define:
- **Table**: The table the permission applies to
- **Access Level**: See, Create, Edit, Delete, or Admin
- **Field-Level Permissions**: Specific fields the user can see or edit (optional)

### Field-Level Permissions

Field-level permissions allow you to restrict access to specific fields within a table. This is the principle of **least privilege** — users only see and edit the fields they need.

```
Privilege: ComplianceFieldRestriction
├── Permission: VendTable → See (all fields)
├── Permission: VendTable → See (field: AccountNum, Name, CreditMax)
├── Permission: VendTable → Edit (field: ComplianceCode only)
└── Permission: VendTable → Deny (field: CreditMax — compliance officers cannot see credit limits)
```

**Field-level permissions are set on each Permission record:**
1. Open the privilege in the AOT
2. Navigate to the **Permissions** node
3. Select the table
4. Set the **Access Level**
5. Use the **Field Permissions** grid to specify which fields are visible/editable/denied

### Field-Level Permissions and Extensions

When you add fields via table extensions, the field-level permissions work differently:

- **Added fields** (via table extension): Inherit the base table's field-level permissions by default
- **To restrict access to an added field**: You must explicitly set field-level permissions on the privilege
- **To grant access to an added field**: Add a field-level permission for the new field in the relevant privilege

```xpp
// Example: A field added via table extension
// VendTable_Extension adds a ComplianceCode field
// To control access to this field:

// In the privilege Permissions grid:
// - Add a field-level permission for ComplianceCode
// - Set Access Level to See or Edit for the relevant roles
// - Deny the field for roles that should not see it
```

---

## 15.3 SecurityKey — Scoping Access by Business Context

A **SecurityKey** is a mechanism that scopes access to records based on business context. It's used to implement **record-level security** — restricting which records a user can see based on their role, company, or other business dimensions.

### How SecurityKeys Work

```
User logs in → Framework checks SecurityKey assignments → 
Records are filtered at query time → User only sees records matching their SecurityKey scope
```

### Standard SecurityKeys

| SecurityKey | Purpose | Example |
|---|---|---|
| `Default` | No restriction — all records visible | System administrators |
| `Company` | Scoped to the current Legal Entity (company) | Most users — they only see their company's data |
| `VendGroup` | Scoped to the user's vendor group | AP clerks — they only see vendors in their group |
| `CustGroup` | Scoped to the customer group | AR clerks — they only see customers in their group |
| `CostCenter` | Scoped to the user's cost center | Department managers |
| `CustomKey` | Custom key defined by the implementer | Any business-specific scoping |

### Assigning SecurityKeys to Roles

SecurityKeys are assigned at the **privilege level**:

1. Open the privilege in the AOT
2. Navigate to the **Security Keys** node
3. Add a SecurityKey assignment with the desired scope
4. The framework applies the filter automatically to all queries on that table

### Custom SecurityKeys

For custom tables, you can define your own SecurityKey:

```xpp
// In your table's security key definition
// The SecurityKey property on the table determines which key is used
// The framework automatically adds a WHERE clause to queries:
// WHERE SecurityKeyField = currentUser'sSecurityKeyValue
```

### SecurityKey vs. Record-Level Security

| Feature | SecurityKey | Record-Level Security |
|---|---|---|
| **Scope** | Business context (company, group, cost center) | Specific record ownership or criteria |
| **Implementation** | Defined on the table's `SecurityKey` property | Implemented via `recordLevelSecurity()` method |
| **Query filtering** | Automatic — framework adds WHERE clause | Manual — developer implements filtering logic |
| **Use case** | Multi-company, multi-group scoping | Row-level ownership (e.g., "users can only see their own records") |

---

## 15.4 Record-Level Security vs. Table-Level Security

### Table-Level Security

Table-level security controls whether a user can access a table at all. It's the coarse-grained control:

- **See**: Can the user view records in this table?
- **Create**: Can the user insert new records?
- **Edit**: Can the user modify existing records?
- **Delete**: Can the user remove records?

Table-level security is set on each **Permission** record within a privilege.

### Record-Level Security

Record-level security controls **which specific records** a user can access within a table they have table-level permission for.

```xpp
// Example: Record-level security on VendTable
// Users can only see vendors in their vendor group
public boolean recordLevelSecurity()
{
    // The framework checks if the current record matches the user's security scope
    // This is implemented via the SecurityKey mechanism
    // The record is filtered at query time
    return super();
}
```

### When to Use Each

| Scenario | Use |
|---|---|
| Users should see all vendors in the system | Table-level only (See permission on VendTable) |
| Users should only see vendors in their company | SecurityKey = `Company` on VendTable |
| Users should only see vendors in their vendor group | SecurityKey = `VendGroup` on VendTable |
| Users should only see vendors they created | Record-level security with custom `recordLevelSecurity()` logic |
| Users should see vendors but not their credit limits | Field-level permission (Deny on CreditMax field) |

### Implementing Custom Record-Level Security

For scenarios where standard SecurityKeys don't cover your needs, you can implement custom record-level security:

```xpp
// In a table's data source on a form:
public void executeQuery()
{
    QueryBuildDataSource qbd;
    QueryBuildRange qbr;

    super();

    // Add a range that restricts records to the current user's scope
    qbd = element.query().dataSourceTable(tableNum(VendTable));
    qbr = qbd.addRange(fieldNum(VendTable, CreatedBy));
    qbr.value(queryValue(curUserId()));
}
```

**Note:** This approach is form-specific. For system-wide record-level security, use SecurityKeys or the `recordLevelSecurity()` method on the table.

---

## 15.5 Extensible Data Security (XDS) — Deep Dive

**Extensible Data Security (XDS)** is the modern mechanism for implementing row-level security in D365 F&O. It replaces the older SecurityKey approach for many scenarios and provides a more flexible, policy-based security model.

### XDS vs. SecurityKey

| Feature | SecurityKey | XDS (Extensible Data Security) |
|---|---|---|
| **Implementation** | Defined on the table's `SecurityKey` property | Policy-based, defined in security policies |
| **Flexibility** | Limited to predefined key types | Highly flexible — custom policies |
| **Query filtering** | Automatic WHERE clause | Automatic WHERE clause via policy |
| **Multi-entity** | Per-table configuration | Can span multiple tables and entities |
| **Runtime evaluation** | At query time | At query time with policy evaluation |
| **Use case** | Standard scoping (company, group) | Custom row-level security rules |

### XDS Policy Components

An XDS policy consists of three parts:

1. **Policy**: Defines the security rule (e.g., "users can only see records in their cost center")
2. **Policy Type**: Determines how the policy is evaluated (e.g., `Table`, `Field`, `Relation`)
3. **Policy Element**: The specific condition that filters records

### XDS Policy Example

```xpp
// XDS Policy: Restrict VendTable records to the user's vendor group
// Policy Type: Table
// Policy Element: WHERE VendGroup = currentUser'sVendGroup

// The policy is defined in the Security > Data Policies workspace
// and is automatically applied to all queries on VendTable
```

### XDS Policy Types

| Policy Type | Description | Example |
|---|---|---|
| **Table** | Filters entire records based on a condition | User can only see vendors in their group |
| **Field** | Restricts access to specific field values | User can only see records where Status = Active |
| **Relation** | Filters based on related table data | User can only see vendors with approved credit |

### When to Use XDS vs. SecurityKey

| Scenario | Use |
|---|---|
| Standard company scoping | SecurityKey (`Company`) |
| Standard group scoping | SecurityKey (`VendGroup`, `CustGroup`) |
| Custom business logic filtering | XDS Policy |
| Multi-table security rules | XDS Policy (can span multiple tables) |
| Field-level restrictions beyond simple deny | XDS Field Policy |
| Dynamic security that changes at runtime | XDS Policy (evaluated at query time) |

---

## 15.6 Privilege Assertions — `CodeAccessPermission::assert()` and `CodeAccessPermission::revertAssert()`

Privilege assertions are a powerful but dangerous mechanism that allows code to **temporarily elevate** the current user's permissions to perform an action they wouldn't normally be allowed to do.

### `CodeAccessPermission::assert()` — Elevate Privileges

`CodeAccessPermission::assert()` tells the framework to check permissions as if the current user had **elevated access** for the duration of the assertion block. This is done using specific permission classes like `SqlStatementExecutePermission` or `InteropPermission`. In D365 F&O, `SqlStatementExecutePermission` takes a SQL statement string (not a table name and `AccessLevel`) and is used to assert permission for raw SQL execution via the `Connection`/`Statement`/`ResultSet` APIs. There is no `TableAccessPermission` class or equivalent — `SqlStatementExecutePermission` is the standard permission class for this scenario.

```xpp
// Example: A service class that needs to read a table the current user doesn't have access to
public VendTable getVendorData(AccountNum _accountNum)
{
    VendTable vendTable;
    str sql;
    Connection connection;
    Statement statement;
    ResultSet resultSet;

    // Build the SQL query for the table we need to read
    sql = strFmt("SELECT * FROM %1 WHERE AccountNum = '%2'",
        tableStr(VendTable), _accountNum);

    // Elevate privileges to execute SQL against VendTable
    new SqlStatementExecutePermission(sql).assert();

    connection = new Connection();
    statement = connection.createStatement();
    resultSet = statement.executeQuery(sql);

    if (resultSet.next())
    {
        vendTable.AccountNum = resultSet.toString(1);
        // ... map additional fields as needed ...
    }

    // Revert to normal permission checking
    CodeAccessPermission::revertAssert();

    return vendTable;
}
```

### Reducing Privileges

In D365 F&O, `SqlStatementExecutePermission` is an **all-or-nothing** assertion — it either grants permission to execute SQL against the database or it does not. Unlike AX 2012's `SqlStatementPermission`, there is no `AccessLevel` parameter to specify read-only vs. read-write access. To **reduce risk**, only assert permission when the operation truly requires it, and keep the assertion scoped to the shortest possible code block: assert immediately before the protected API call, then revert immediately after.

```xpp
// Example: Only assert SQL execution permission for the specific operation that needs it
public void safeDelete(VendInvoiceJour _invoice)
{
    str sql;
    Connection connection;
    Statement statement;

    // Build the SQL DELETE statement for the specific invoice
    sql = strFmt("DELETE FROM %1 WHERE RecId = %2",
        tableStr(VendInvoiceJour), _invoice.RecId);

    try
    {
        // Assert permission only for the duration of the SQL execution
        new SqlStatementExecutePermission(sql).assert();

        connection = new Connection();
        statement = connection.createStatement();
        statement.executeUpdate(sql);

        // Revert immediately after the protected API call
        CodeAccessPermission::revertAssert();
    }
    catch (Exception::Error)
    {
        CodeAccessPermission::revertAssert();
        error("Failed to delete invoice. Contact your administrator.");
    }
}
```

### Why Privilege Assertions Are Dangerous

| Risk | Description |
|---|---|
| **Bypasses security** | `assert()` can allow users to access data they shouldn't see |
| **Hard to audit** | Assertions are not visible in the standard security model — they're invisible to permission simulation |
| **Leaks in production** | If an assertion is left in code, it can expose sensitive data in production environments |
| **Violates least privilege** | Assertions grant more permissions than the user should have |

### Best Practices for Privilege Assertions

1. **Minimize scope** — use `assert()` for the shortest possible code block, immediately followed by `revertAssert()`
2. **Never assert in loops** — asserting inside a `while select` loop is a performance anti-pattern
3. **Document every assertion** — add a comment explaining WHY the assertion is needed and what risk it introduces
4. **Review in code review** — every `assert()` call should be reviewed by a senior developer
5. **Prefer role-based design** — if you need `assert()`, it usually means the security model is wrong. Fix the role design instead.
6. **Test with permission simulation** — always test code with assertions using the "Run as" feature to verify the assertions work correctly

### When Assertions Are Legitimate

Despite the risks, there are valid use cases:

| Scenario | Justification |
|---|---|
| System service that processes data on behalf of users | The service runs with elevated privileges by design |
| Data migration or integration code | Migration tools need broader access than end users |
| Admin-only functionality (e.g., "Run as admin" button) | The user explicitly requests elevated access |
| Reading audit log data for compliance reporting | Compliance reports need access to all data regardless of user permissions |

### Security Hardening for Assertions

When using privilege assertions in extension code, follow these additional hardening practices:

1. **Wrap assertions in try/catch** — if the assertion fails, catch the exception gracefully
2. **Log assertion usage** — write to a custom audit log table whenever an assertion is used
3. **Use the minimum assertion level** — always use the lowest permission level that still allows the operation
4. **Never assert in CoC overrides** — CoC overrides should not elevate privileges; they should work within the existing security context
5. **Never assert in event handlers** — event handlers should not elevate privileges; they should work within the base method's security context

```xpp
// ✅ GOOD — assertion with logging and error handling
public VendTable getVendorDataSecure(AccountNum _accountNum)
{
    VendTable vendTable;
    str sql;
    Connection connection;
    Statement statement;
    ResultSet resultSet;

    try
    {
        // Log the assertion for audit purposes
        this.logAssertion('getVendorDataSecure', _accountNum);

        // Build the SQL query for the table we need to read
        sql = strFmt("SELECT * FROM %1 WHERE AccountNum = '%2'",
            tableStr(VendTable), _accountNum);

        // Elevate privileges to execute SQL against VendTable
        new SqlStatementExecutePermission(sql).assert();

        connection = new Connection();
        statement = connection.createStatement();
        resultSet = statement.executeQuery(sql);

        // Revert immediately after the protected API call
        CodeAccessPermission::revertAssert();

        if (resultSet.next())
        {
            vendTable.AccountNum = resultSet.toString(1);
            // ... map additional fields as needed ...
        }
    }
    catch (Exception::Error)
    {
        CodeAccessPermission::revertAssert();
        error('Failed to retrieve vendor data. Contact your administrator.');
    }

    return vendTable;
}
```

---

## 15.7 Security Role Design for Custom Objects

When you create custom tables, forms, and reports, you must design the security model to grant appropriate access.

### Step-by-Step Security Role Design

#### Step 1: Identify the Custom Objects

List all custom objects that need security:

| Object Type | Object Name | Purpose |
|---|---|---|
| Table | `APCustomsDeclaration` | Stores customs compliance declarations |
| Table Extension | `VendTable_Extension` | Adds ComplianceCode field to VendTable |
| Form | `ComplianceHistoryForm` | Displays compliance history |
| Report | `ComplianceSummaryReport` | Monthly compliance report |
| Menu Item | `ComplianceHistory` | Navigation to compliance form |
| Data Entity | `VendAPComplianceEntity` | Integration with external audit system |

#### Step 2: Define the Duties

Group related privileges into duties:

| Duty Name | Purpose |
|---|---|
| `APComplianceViewer` | View compliance data — read access to all compliance tables |
| `APComplianceProcessor` | Process compliance declarations — create and edit access |
| `APComplianceAdmin` | Full compliance administration — all access including delete |

#### Step 3: Define the Privileges

For each duty, define the specific privileges:

**Duty: `APComplianceViewer`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `APComplianceView` | `APCustomsDeclaration` | See | All fields visible |
| `APComplianceView` | `VendTable` | See | All fields visible |
| `APComplianceView` | `VendInvoiceJour` | See | All fields visible |
| `APComplianceView` | `ComplianceHistoryForm` | See | Form access only |

**Duty: `APComplianceProcessor`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `APComplianceProcess` | `APCustomsDeclaration` | Create + Edit | All fields editable |
| `APComplianceProcess` | `VendTable` | See | All fields visible |
| `APComplianceProcess` | `VendInvoiceJour` | See | All fields visible |
| `APComplianceProcess` | `ComplianceHistoryForm` | Create + Edit | Form access |

**Duty: `APComplianceAdmin`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `APComplianceAdmin` | `APCustomsDeclaration` | Admin | All fields |
| `APComplianceAdmin` | `VendTable` | See | All fields |
| `APComplianceAdmin` | `VendInvoiceJour` | See | All fields |
| `APComplianceAdmin` | `ComplianceHistoryForm` | Admin | All |
| `APComplianceAdmin` | `ComplianceSummaryReport` | Output | Report execution |

#### Step 4: Assign Duties to Roles

Create the security role and assign duties:

| Role | Duties |
|---|---|
| `ComplianceOfficer` | `APComplianceViewer`, `APComplianceProcessor` |
| `ComplianceAdmin` | `APComplianceViewer`, `APComplianceProcessor`, `APComplianceAdmin` |
| `AP clerk` | `APComplianceViewer` (read-only) |

#### Step 5: Assign the Role to Users

In the **User Administration** form, assign the `ComplianceOfficer` role to compliance officers and the `AP clerk` role to AP staff.

### Security Role Design Template

```xml
<!-- Security Role Definition in ModelManifest.xml (conceptual) -->
<Security>
  <Roles>
    <Role name="ComplianceOfficer">
      <Duties>
        <Duty name="APComplianceViewer"/>
        <Duty name="APComplianceProcessor"/>
      </Duties>
    </Role>
    <Role name="ComplianceAdmin">
      <Duties>
        <Duty name="APComplianceViewer"/>
        <Duty name="APComplianceProcessor"/>
        <Duty name="APComplianceAdmin"/>
      </Duties>
    </Role>
  </Roles>
  <Privileges>
    <Privilege name="APComplianceView">
      <Permissions>
        <Permission table="APCustomsDeclaration" accessLevel="See"/>
        <Permission table="VendTable" accessLevel="See"/>
        <Permission table="VendInvoiceJour" accessLevel="See"/>
      </Permissions>
    </Privilege>
    <Privilege name="APComplianceProcess">
      <Permissions>
        <Permission table="APCustomsDeclaration" accessLevel="Create"/>
        <Permission table="APCustomsDeclaration" accessLevel="Edit"/>
        <Permission table="VendTable" accessLevel="See"/>
        <Permission table="VendInvoiceJour" accessLevel="See"/>
      </Permissions>
    </Privilege>
  </Privileges>
</Security>
```

---

## 15.8 Security Model for Extensions

When you create extensions that add new functionality, you must consider how the security model applies to your extension code.

### Extension Security Principles

1. **Extensions inherit the base security context** — your CoC override or event handler runs with the same permissions as the base method
2. **New objects need new permissions** — custom tables, forms, and reports require their own security configuration
3. **Table extensions don't need new permissions** — added fields inherit the base table's permissions
4. **Menu items need permissions** — any new menu item must have a corresponding privilege

### CoC and Security

Chain of Command overrides do not change the security context:

```xpp
// This CoC override runs with the same permissions as the base method
[ExtensionOf(classStr(VendTable))]
final class VendTable_ComplianceCocExtension
{
    public boolean validateWrite()
    {
        boolean ret;

        // The base validateWrite() runs with the user's existing permissions
        ret = next validateWrite();

        // Your custom validation also runs with the user's existing permissions
        // You cannot bypass security here
        if (this.ComplianceCode == '' && this.CreditMax > 100000)
        {
            ret = checkFailed('Compliance code required for high-credit vendors');
        }

        return ret;
    }
}
```

### Event Handlers and Security

Event handlers also inherit the base method's security context:

```xpp
class VendTableEventHandler
{
    [EventHandler(eventStr(VendTable::inserted))]
    public static void onVendTableInserted(Common _sender)
    {
        VendTable vendTable = _sender as VendTable;

        // This event handler runs with the same permissions
        // as the base insert() method — no elevation needed
        info(strFmt('Vendor %1 was inserted.', vendTable.AccountNum));
    }
}
```

### When Extensions Need New Permissions

Extensions need new permissions when they:

1. **Add new tables** — the new table needs its own permissions
2. **Add new forms** — the form needs menu item permissions
3. **Add new reports** — the report needs output permissions
4. **Add new menu items** — the menu item needs a privilege
5. **Access data the user shouldn't normally see** — this is a design smell; reconsider the architecture

### Common Extension Security Mistakes

| Mistake | Risk | Fix |
|---|---|---|
| Adding a CoC override that reads data the user can't access | Security bypass | Don't read data the user doesn't have permission for |
| Creating a new form without menu item permissions | Users can't access the form | Add a MenuItemOutput with proper privileges |
| Adding a table extension field that exposes sensitive data | Data leakage | Set field-level permissions on the base table's privilege |
| Using `assert()` in an event handler | Unauthorized data access | Remove the assertion; redesign the extension |
| Creating a new report without output permissions | Users can't run the report | Add an Output Menu Item with proper privileges |

---

## 15.9 Testing Security Roles

### The "Run As" Feature

D365 F&O includes a **"Run as"** feature that lets you test security roles without logging in as a different user.

**How to use "Run as":**
1. Open the form or report you want to test
2. Click the **"Run as"** button in the toolbar (or press `Ctrl+Shift+F9`)
3. Select the user you want to test as
4. The form/report executes with that user's permissions
5. Verify that the user can or cannot access the expected data

### The Security Role Switch

The **Security Role Switch** allows you to temporarily switch to a different security role for testing:

1. Navigate to **System Administration > Setup > Security > Security role switch**
2. Select the role you want to test
3. Click **Switch**
4. All subsequent actions use the permissions of the selected role
5. Click **Switch back** to return to your original role

### Permission Simulation

Permission simulation lets you test what a user can and cannot do:

1. Navigate to **System Administration > Inquiries > Security > Permissions**
2. Select the user and role
3. Click **Simulate**
4. The simulation shows which permissions are granted and which are denied
5. Use this to verify that your custom security model works correctly

### Testing Checklist

- [ ] Can the user see the custom form?
- [ ] Can the user create new records in the custom table?
- [ ] Can the user edit existing records?
- [ ] Can the user delete records (if Delete permission is granted)?
- [ ] Can the user run the custom report?
- [ ] Can the user see field-level restricted fields?
- [ ] Can the user NOT see fields that should be denied?
- [ ] Does the "Run as" test with a user who has no compliance role show no access?
- [ ] Does the Security Role Switch correctly apply the new role's permissions?
- [ ] Does the CoC override respect the user's existing permissions?
- [ ] Does the event handler run within the base method's security context?
- [ ] Are field-level permissions correctly applied to extended fields?

---

## 15.10 Activity — Design the Complete Security Model for a Custom Inventory Reconciliation Module

> **Activity**: Design the complete security model for a custom inventory reconciliation module. The module includes:
> 1. A custom table `INVReconciliationHeader` (parent) with fields: ReconciliationId, ReconciliationDate, Status, CreatedBy
> 2. A custom table `INVReconciliationLine` (child, linked to header via RecId) with fields: LineNumber, ItemId, Quantity, ReconciledQty, Variance, ApprovedBy
> 3. A form `INVReconciliationForm` (ListPage + Detail page) for viewing and processing reconciliations
> 4. A batch job `INVReconciliationBatchJob` that automatically reconciles items
> 5. A report `INVReconciliationReport` that shows reconciliation summaries
> 6. A data entity `INVReconciliationEntity` for pushing reconciliation data to an external ERP
>
> Design the complete security model including:
> - At least 3 duties with appropriate privileges
> - At least 2 security roles with different duty assignments
> - Field-level permissions for sensitive fields (e.g., Variance should only be visible to approvers)
> - Record-level security so users can only see reconciliations for their own company
> - A "Run as" test plan to verify the security model works correctly
>
> **Activity Hints** (Multiple Valid Permission Structures):
>
> - **Hint A — Duty design**: Option A1 — three duties (Viewer, Processor, Admin) with escalating access (recommended — clear separation of concerns). Option A2 — two duties (ReadWrite, Admin) for simpler deployments (valid but less granular). Option A3 — four duties (Viewer, Processor, Approver, Admin) if approval workflows are separate from processing (most granular, useful for compliance-heavy environments).
>
> - **Hint B — Field-level permissions for Variance**: Option B1 — Deny Variance field for all roles except Admin (recommended — variance data is sensitive and should only be visible to those who can act on it). Option B2 — Allow Variance for Processor and Admin roles, deny for Viewer (valid if processors need to see variances to make decisions). Option B3 — No field-level permissions on Variance, rely on table-level See permission (not recommended — violates least privilege principle).
>
> - **Hint C — Record-level security**: Option C1 — use the standard `Company` SecurityKey so users only see their company's reconciliations (recommended — simple and effective). Option C2 — use a custom SecurityKey based on the `CreatedBy` field so users only see their own reconciliations (more restrictive, useful for sensitive reconciliations). Option C3 — no record-level security, rely on table-level permissions only (not recommended — users would see all companies' reconciliations).
>
> - **Hint D — Role assignment**: Option D1 — two roles (ReconciliationOperator and ReconciliationAdmin) with different duty combinations (recommended). Option D2 — three roles (ReconciliationViewer, ReconciliationProcessor, ReconciliationAdmin) for maximum separation of duties (best practice for SOX/compliance environments).

### Expected Approach (Ideal — in detail)

#### Duty Design

**Duty 1: `INVReconciliationViewer`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `INVReconciliationView` | `INVReconciliationHeader` | See | All fields |
| `INVReconciliationView` | `INVReconciliationLine` | See | All fields except `Variance` |
| `INVReconciliationView` | `INVReconciliationForm` | Display | Form access |
| `INVReconciliationView` | `INVReconciliationReport` | Output | Report execution |

**Duty 2: `INVReconciliationProcessor`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `INVReconciliationProcess` | `INVReconciliationHeader` | Create + Edit | All fields |
| `INVReconciliationProcess` | `INVReconciliationLine` | Create + Edit | All fields except `Variance` |
| `INVReconciliationProcess` | `INVReconciliationForm` | Create + Edit | Form access |
| `INVReconciliationProcess` | `INVReconciliationBatchJob` | Action | Job execution |

**Duty 3: `INVReconciliationAdmin`**

| Privilege | Table | Access Level | Field Permissions |
|---|---|---|---|
| `INVReconciliationAdmin` | `INVReconciliationHeader` | Admin | All fields |
| `INVReconciliationAdmin` | `INVReconciliationLine` | Admin | All fields including `Variance` |
| `INVReconciliationAdmin` | `INVReconciliationForm` | Admin | All form actions |
| `INVReconciliationAdmin` | `INVReconciliationBatchJob` | Admin | Job execution + cancellation |
| `INVReconciliationAdmin` | `INVReconciliationReport` | Output | Report execution |
| `INVReconciliationAdmin` | `INVReconciliationEntity` | Admin | Data entity execution |

#### Security Role Design

**Role: `InventoryReconciliationOperator`**
- Duties: `INVReconciliationViewer`, `INVReconciliationProcessor`
- Users: Inventory clerks, reconciliation processors
- Can view, create, and edit reconciliations but cannot see Variance field or approve reconciliations

**Role: `InventoryReconciliationManager`**
- Duties: `INVReconciliationViewer`, `INVReconciliationProcessor`, `INVReconciliationAdmin`
- Users: Inventory managers, compliance officers
- Full access including Variance visibility, approval, and batch job management

#### Record-Level Security

- `INVReconciliationHeader` and `INVReconciliationLine` have `SecurityKey = Company`
- Users only see reconciliations for their current Legal Entity
- This is enforced automatically by the framework at query time

#### Field-Level Permissions

- `Variance` field on `INVReconciliationLine`: Denied for `INVReconciliationViewer` and `INVReconciliationProcessor` duties
- `Variance` field on `INVReconciliationLine`: Allowed for `INVReconciliationAdmin` duty
- This ensures that only managers who can approve variances can see them

#### Testing Plan

1. **Run as InventoryReconciliationOperator**:
   - [ ] Can see INVReconciliationForm ListPage with their company's reconciliations
   - [ ] Can create a new reconciliation
   - [ ] Can edit an existing reconciliation
   - [ ] CANNOT see the Variance field on reconciliation lines
   - [ ] CANNOT run the batch job
   - [ ] CANNOT execute the data entity

2. **Run as InventoryReconciliationManager**:
   - [ ] Can see INVReconciliationForm ListPage with their company's reconciliations
   - [ ] Can create and edit reconciliations
   - [ ] CAN see the Variance field on reconciliation lines
   - [ ] CAN run the batch job
   - [ ] CAN execute the data entity
   - [ ] Can approve reconciliations (if approval workflow is implemented)

3. **Run as user with no inventory reconciliation role**:
   - [ ] CANNOT see INVReconciliationForm
   - [ ] CANNOT access INVReconciliationHeader or INVReconciliationLine tables
   - [ ] CANNOT run the report

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeInventoryReconciliation</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeInventoryReconciliationEnabled</ConfigurationKey>
</ModelManifest>
```

---

## 15.11 Activity — Security Audit for an Extension Module

> **Activity**: Perform a security audit for a custom extension module that adds compliance tracking to the vendor management process. The extension includes:
> 1. A table extension adding `ComplianceCode` to `VendTable`
> 2. A form extension adding a compliance tab to the vendor form
> 3. A CoC override on `VendTable.validateWrite()` that checks the compliance code
> 4. An event handler on `VendTable.inserted()` that logs compliance checks
> 5. A new report `ComplianceSummaryReport`
> 6. A new menu item `ComplianceHistory`
>
> Audit the extension for security issues and document your findings:
> - Does the CoC override change the security context? (No — it inherits the base method's permissions)
> - Does the event handler need new permissions? (No — it runs in the base method's context)
> - Does the table extension field need new field-level permissions? (Yes — if ComplianceCode is sensitive)
> - Does the form extension need a new menu item with permissions? (Yes — if it adds new navigation)
> - Does the report need output permissions? (Yes — always for new reports)
> - Are there any `assert()` calls that need auditing? (Check all extension code)
>
> **Activity Hints:**
> - **Hint A — CoC security**: CoC overrides never change the security context. They run with the same permissions as the base method. If the base method requires See permission on VendTable, the CoC override also requires See permission. You cannot use CoC to bypass security.
> - **Hint B — Event handler security**: Event handlers run in the context of the base method. They inherit the base method's permissions. If the base method's insert() requires Create permission on VendTable, the event handler also runs with Create permission.
> - **Hint C — Table extension field permissions**: Added fields inherit the base table's permissions by default. If you want to restrict access to a sensitive added field, you must explicitly set field-level permissions on the privilege.
> - **Hint D — Form extension menu items**: Any new menu item added by a form extension needs its own privilege. Without a privilege, users cannot navigate to the form.
> - **Hint E — Report permissions**: Every new report needs an Output Menu Item with a privilege that grants output access. Without this, users cannot run the report.

---

### Remaining Chapters — Detailed Outlines


# Chapter 16: Data Entities — Integration & Data Management in D365 F&O

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
                ttsBegin;

                // Step 1: Validate the staging record
                if (!this.validateStagingRecord(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Failed;
                    staging.ErrorMessage = 'Validation failed: missing required fields';
                    staging.update();
                    ttsCommit;
                    continue;
                }

                // Step 2: Check for duplicates
                if (this.isDuplicate(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Duplicate;
                    staging.ErrorMessage = 'Duplicate declaration ID found in target';
                    staging.update();
                    ttsCommit;
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

                ttsCommit;
            }
            catch (Exception::Error)
            {
                ttsAbort;
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
            ttsBegin;
            
            // ... validation and processing logic ...
            
            // Check rollback threshold AFTER each record
            if (failedCount > 0 && (failedCount * 100 / processedCount) > 10)
            {
                // Mark all remaining Ready records as BatchFailed
                update_recordset staging
                    setting StagingStatus = APCustomsStagingStatus::BatchFailed,
                        ErrorMessage = 'Rollback threshold exceeded: >10% failure rate'
                    where staging.StagingStatus == APCustomsStagingStatus::Ready;
                
                ttsCommit;
                
                throw error(strFmt('Rollback threshold exceeded at record %1 of %2. Batch aborted.', 
                    processedCount, totalToProcess));
            }
            
            ttsCommit;
        }
        catch (Exception::Error)
        {
            ttsAbort;
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
                ttsBegin;

                // Update status to Processing
                staging.StagingStatus = HRPersonnelStagingStatus::Processing;
                staging.update();

                // ---- VALIDATION ----
                
                // 1. Validate required fields
                if (!this.validateRequiredFields(staging))
                {
                    this.markFailed(staging, 'Missing required fields: PersonNumber, FirstName, LastName, Email, or HireDate');
                    failedCount++;
                    ttsCommit;
                    continue;
                }

                // 2. Validate email format
                if (!this.validateEmail(staging.Email))
                {
                    this.markFailed(staging, 'Invalid email format');
                    failedCount++;
                    ttsCommit;
                    continue;
                }

                // 3. Check for duplicates by PersonNumber
                if (this.isDuplicatePersonNumber(staging.PersonNumber))
                {
                    this.markDuplicate(staging);
                    duplicateCount++;
                    failedCount++; // Count as failure for rollback threshold
                    ttsCommit;
                    continue;
                }

                // 4. Check rollback threshold (>10% failures)
                if (failedCount > 0 && (failedCount * 100 / processedCount) > #RollbackThresholdPercent)
                {
                    this.markBatchFailed(staging, 
                        strFmt('Rollback threshold exceeded: %1% failure rate at record %2 of %3', 
                            #RollbackThresholdPercent, processedCount, totalToProcess));
                    failedCount++;
                    ttsCommit;
                    
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

                ttsCommit;
            }
            catch (Exception::Error)
            {
                ttsAbort;
                this.markFailed(staging, 'Unexpected error during processing');
                failedCount++;
            }
            catch (Exception::DuplicateKey)
            {
                ttsAbort;
                this.markFailed(staging, 'Duplicate key error - record may have been inserted by another process');
                failedCount++;
            }
            catch (Exception::Deadlock)
            {
                ttsAbort;
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

*End of Chapter 16 — Data Entities*
        while select staging
            where staging.StagingStatus == APCustomsStagingStatus::Ready
        {
            try
            {
                ttsBegin;

                // Validate the staging record
                if (!this.validateStagingRecord(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Failed;
                    staging.ErrorMessage = 'Validation failed';
                    staging.update();
                    ttsCommit;
                    continue;
                }

                // Check for duplicates
                if (this.isDuplicate(staging))
                {
                    staging.StagingStatus = APCustomsStagingStatus::Duplicate;
                    staging.ErrorMessage = 'Duplicate declaration ID';
                    staging.update();
                    ttsCommit;
                    continue;
                }

                // Write to target table
                target.initValue();
                target.DeclId = staging.DeclId;
                target.VendTableRecId = staging.VendTableRecId;
                target.DeclDate = staging.DeclDate;
                target.CustomsRef = staging.CustomsRef;
                target.InvoiceLineRecId = staging.InvoiceLineRecId;
                target.insert();

                // Mark staging as processed
                staging.StagingStatus = APCustomsStagingStatus::Processed;
                staging.update();

                ttsCommit;
            }
            catch (Exception::Error)
            {
                ttsAbort;
                staging.StagingStatus = APCustomsStagingStatus::Failed;
                staging.ErrorMessage = 'Unexpected error during processing';
                staging.update();
            }
        }
    }

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
        return true;
    }

    private boolean isDuplicate(APCustomsDeclarationStaging _staging)
    {
        APCustomsDeclaration existing;
        return exists select firstonly existing
            where existing.DeclId == _staging.DeclId;
    }
}
```

### The `postProcess()` Method

The `postProcess()` method runs after all staging records have been processed. It's used for:

- Sending notifications (email, Infolog messages)
- Logging summary statistics
- Triggering downstream processes
- Cleaning up staging records

```xpp
public void postProcess()
{
    int processedCount;
    int failedCount;

    processedCount = select count(StagingStatus)
        from APCustomsDeclarationStaging
        where StagingStatus == APCustomsStagingStatus::Processed;

    failedCount = select count(StagingStatus)
        from APCustomsDeclarationStaging
        where StagingStatus == APCustomsStagingStatus::Failed;

    info(strFmt('Processing complete: %1 succeeded, %2 failed.',
        processedCount, failedCount));

    // Optional: send email notification for failed records
    if (failedCount > 0)
    {
        // ... email notification logic ...
    }
}
```

---

## 16.4 Entity Mapping — Auto-Mapping vs. Manual Field Mapping

### Auto-Mapping

Auto-mapping is the default behavior when a DataEntity field has the same name and compatible type as the underlying table field. The framework automatically maps the entity field to the table field.

**When auto-mapping works:**
- Field names match exactly (case-sensitive)
- Field types are compatible (string to string, int to int, date to date)
- No transformation is needed

**When auto-mapping fails:**
- Field names don't match (e.g., entity field `DeclId` maps to table field `DeclarationId`)
- Field types are incompatible (e.g., entity field is `string` but table field is `int`)
- Transformation is needed (e.g., concatenating first + last name into a full name)

### Manual Field Mapping

When auto-mapping doesn't work, you need to define manual field mappings in the Data Entity design:

```
Data Entity Field: DeclId (string 35)
    → Maps to Table Field: DeclarationId (string 35)
    → Mapping Type: Manual
    → Transformation: None (names differ but types match)

Data Entity Field: FullName (string 120)
    → Maps to Table Fields: FirstName + ' ' + LastName
    → Mapping Type: Manual
    → Transformation: Concatenation expression
```

### Mapping in the Data Entity Designer

In Visual Studio, the Data Entity designer provides a **Mappings** node where you can:

1. **Auto-map** — click "Auto Map" to let the framework attempt automatic matching
2. **Manual map** — drag and drop entity fields to table fields
3. **Transform** — define expressions for field transformations
4. **Skip** — exclude fields from the mapping (they exist in the entity but aren't mapped to a table field)

### Best Practices for Entity Mapping

1. **Use consistent naming** — entity field names should match table field names whenever possible to enable auto-mapping
2. **Use staging tables for staging fields** — staging fields should never be exposed in OData; store them in the auto-generated staging table
3. **Document manual mappings** — add comments explaining why auto-mapping wasn't possible
4. **Test mappings with sample data** — always verify that data flows correctly from entity to table

---

## 16.5 Data Management Workspace — Import/Export and Package Deployment

The **Data Management** workspace is the central hub for importing and exporting data in D365 F&O. It provides a UI-driven interface for data operations without requiring code.

### Import Operations

| Operation | Description | Use Case |
|---|---|---|
| **Import** | Load data from an Excel/CSV file into D365 F&O tables | Bulk data loading, initial setup |
| **Import from Entity** | Load data using a Data Entity definition | Integration scenarios, staging pattern |
| **Import Group** | Execute a group of import projects in sequence | Complex multi-table imports |

### Export Operations

| Operation | Description | Use Case |
|---|---|---|
| **Export** | Export data from D365 F&O tables to Excel/CSV | Reporting, data extraction |
| **Export to Entity** | Export data using a Data Entity definition | Integration with external systems |
| **Export to Data Entity** | Export using the staging pattern for write-back scenarios | Data synchronization |

### Package Deployment

A **package** is a deployable unit that contains one or more Data Entities, mapping configurations, and import/export settings. Packages can be:

1. **Created** in the Data Management workspace
2. **Saved** as a `.axdp` file (Data Management package)
3. **Shared** across environments via LCS
4. **Deployed** to target environments via the package deployment feature

### Package Deployment Steps

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
    │  - The Data Management workspace on the target environment detects the package
    │
[5] Execute the package in the target environment
    │  - Run the import/export operation
    │  - Monitor progress and review results
    │
[6] Verify the data in the target environment
    │  - Check the Data Management workspace for execution status
    │  - Review any error logs
```

---

## 16.6 REST/OData — DictClass Reflection, Entity Publishing, and HttpClient

### Exposing Data via OData

D365 F&O automatically exposes Data Entities as OData endpoints when they are published. The OData endpoint follows the standard OData protocol and can be consumed by any OData client.

**OData endpoint URL format:**
```
https://<your-environment>.dynamics.com/data/<EntityName>
```

**Example:**
```
https://usnconeboxax1aos.cloud.onebox.dynamics.com/data/VendAPComplianceEntity
```

### `DictClass` — Runtime Entity Metadata

The `DictClass` and `DictMethod` classes provide runtime reflection over X++ objects, including Data Entities:

- Field definitions (name, type, size)
- Method signatures and parameters
- Class attributes
- Supported operations

```xpp
// Get metadata for a Data Entity class at runtime
DictClass dictClass = new DictClass(classNum(VendAPComplianceEntity));
Array    attributes  = dictClass.getAllAttributes();

// Inspect a specific method's .NET return type via reflection.
// Source: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-reflection-dictmethod
DictMethod dictMethod = new DictMethod(
    classNum(VendAPComplianceEntity),
    methodStr(VendAPComplianceEntity, process));
info(strFmt("Method %1 returns %2",
    methodStr(VendAPComplianceEntity, process),
    dictMethod.clrReturnType()));
```

### Publishing an Entity via `IsPublic`

A Data Entity is published for OData exposure by setting the **`IsPublic`** property to **Yes** in the entity designer. No code registration is needed — the framework automatically generates the OData endpoint and the staging table when the entity is built and deployed.

### Consuming OData Endpoints via `HttpClient`

D365 F&O provides the `HttpClient` class (from `System.Net.Http`) for consuming external OData endpoints from X++ code.

```xpp
class ExternalDataConsumer
{
    public static void consumeODataEndpoint()
    {
        HttpClient httpClient;
        HttpRequestMessage request;
        HttpResponseMessage response;
        string responseBody;

        // Create the HTTP client
        httpClient = new HttpClient();

        // Create the request
        request = new HttpRequestMessage();
        request.set_Method(HttpMethod::Get);
        request.set_RequestUri(
            new Uri('https://external-system.com/api/v1/vendors'));

        // Add authentication header (Bearer token)
        request.get_Headers().Add(
            'Authorization',
            'Bearer ' + ExternalConfig::getAccessToken());

        // Send the request
        response = httpClient.SendAsync(request).GetAwaiter().GetResult();

        // Read the response
        if (response.get_IsSuccessStatusCode())
        {
            responseBody = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
            // Process the JSON response
            info(strFmt('Received %1 bytes from external system',
                responseBody.Length()));
        }
        else
        {
            error(strFmt('HTTP request failed with status code: %1',
                response.get_StatusCode()));
        }
    }
}
```

### OData Query Options

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

### Consuming OData from Power Automate

Power Automate has built-in connectors for D365 F&O OData endpoints:

1. Create a new Power Automate flow
2. Add a **"When a HTTP request is received"** trigger (for inbound)
3. Add a **"HTTP"** action to call the D365 F&O OData endpoint
4. Parse the JSON response
5. Transform and load data into the target system

---

## 16.7 Power Platform Integration — Logic Apps and Power Automate

### Logic Apps Connector for D365 F&O

Microsoft provides a **Dynamics 365 Finance & Operations** connector in Azure Logic Apps that simplifies integration without writing code.

**Common Logic Apps operations:**

| Operation | Description |
|---|---|
| **List records** | Query a Data Entity and return matching records |
| **Get record** | Retrieve a single record by key |
| **Create record** | Insert a new record into a Data Entity (with staging) |
| **Update record** | Modify an existing record |
| **Delete record** | Remove a record |
| **Execute action** | Call a custom action defined on the entity |

### Power Automate Triggers

Power Automate can be triggered from D365 F&O in several ways:

| Trigger | How It Works |
|---|---|
| **Data Entity import** | A Data Entity import triggers a flow that processes the imported data |
| **Custom action** | A custom action on a Data Entity triggers a flow |
| **Event-based** | An event handler in X++ sends a message to Azure Service Bus, which triggers a flow |
| **Scheduled** | A Logic App or Power Automate flow runs on a schedule and calls D365 F&O OData |

### Integration Pattern: D365 F&O → Logic App → External System

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

### Integration Pattern: External System → Logic App → D365 F&O

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

### Best Practices for Power Platform Integration

1. **Use Data Entities as the integration layer** — don't expose tables directly via OData
2. **Use the staging pattern for write-back** — ensures validation and error handling
3. **Implement error handling in Logic Apps** — use try/catch patterns and dead-letter queues
4. **Use batch processing for large data volumes** — don't send thousands of records in a single request
5. **Secure connections with Managed Identity** — don't store credentials in Logic Apps
6. **Monitor integration runs** — use Azure Monitor and Logic Apps run history to track failures

---

## 16.8 Activity — Build a Data Entity for HR Employee Data Integration

> **Activity**: Build a complete data entity for HR employee data integration with the following requirements:
> 1. Create a Data Entity called `HRPersonnelEntity` that exposes employee data from `DirPerson`, `HCMWorker`, and `HRMPosition` tables
> 2. Configure the entity's `IsPublic` property to **Yes**, set `Public Entity Name` to `HRPersonnelEntity`, and set `Public Collection Name` to `HRPersonnelEntities` — exposed fields: PersonNumber, FirstName, LastName, Email, Position, Department, HireDate, Status
> 3. Design a staging table `HRPersonnelStaging` with internal fields: PersonRecId, WorkerRecId, PositionRecId, StagingStatus, ErrorMessage
> 4. The entity must have a `Link` field connecting to `DirPerson.RecId`
> 5. Implement a staging table `HRPersonnelStaging` with fields for all public entity fields plus StagingStatus and ErrorMessage
> 6. Implement `process()` method with validation (email format check, duplicate detection by PersonNumber) and error logging
> 7. Implement `postProcess()` method with summary statistics and email notification for failed records
> 8. Configure auto-mapping for all fields that share names between entity and table
> 9. Use manual mapping for the `FullName` field (concatenation of FirstName + ' ' + LastName)
> 10. Expose the entity via OData and test with a sample Power Automate flow
> 11. Implement deduplication logic that skips records already in the target table
> 12. Implement rollback logic that aborts the entire batch if more than 10% of records fail validation
>
> **Activity Hints** (Multiple Valid Approaches):
>
> - **Hint A — Entity type selection**: Option A1 — use a `DataEntity` with staging pattern (recommended — full validation, error logging, rollback support). Option A2 — use a `Derived View` for read-only exposure (simpler but no write-back support). Option A3 — use a `Composite Entity` if the data spans multiple unrelated entities (overkill for this scenario).
>
> - **Hint B — Staging table design**: Option B1 — use `TempDB` storage for the staging table (recommended — temporary data, no persistence needed). Option B2 — use a permanent table with `ImportStatus` field (valid if you need to keep import history for audit). Option C — use the `DataManagementStaging` framework table (not recommended — too generic, hard to customize).
>
> - **Hint C — Deduplication logic**: Option C1 — check for existing records by `PersonNumber` before insert using `exists select` (recommended — simple and effective). Option C2 — use a `NumberSeq` framework approach (overkill for deduplication). Option C3 — let the database handle duplicates via unique index and catch the error (valid but less informative — you lose the context of which record failed).
>
> - **Hint D — Rollback threshold**: Option D1 — count failures during processing and abort if >10% (recommended — configurable threshold). Option D2 — abort on first failure (too strict — one bad record shouldn't fail the entire batch). Option D3 — don't implement rollback, just log errors and continue (valid for non-critical integrations where partial success is acceptable).
>
> - **Hint E — Email notification**: Option E1 — use `SmtpMail::send()` from X++ (direct but requires SMTP configuration). Option E2 — trigger a Logic App from the `postProcess()` method via Azure Service Bus (recommended — decoupled, configurable). Option C3 — use `Workflow::submitRequest()` to create a workflow notification (valid but requires workflow configuration).

### Expected Approach (Ideal — in detail)

#### Entity Design: HRPersonnelEntity

```xpp
// Data Entity: HRPersonnelEntity
// Public entity fields (IsPublic = Yes):
//   PersonNumber (string 20) — from DirPerson.AccountNum
//   FirstName (string 50) — from DirPerson.FirstName
//   LastName (string 50) — from DirPerson.LastName
//   FullName (string 120) — computed: FirstName + ' ' + LastName
//   Email (string 250) — from DirPerson.Email
//   Position (string 50) — from HRMPosition.Position
//   Department (string 50) — from HRMPosition.Department
//   HireDate (date) — from HCMWorker.HireDate
//   Status (string 20) — computed from HCMWorker.Status

// Staging table fields (HRPersonnelStaging):
//   PersonRecId (int64) — from DirPerson.RecId
//   WorkerRecId (int64) — from HCMWorker.RecId
//   PositionRecId (int64) — from HRMPosition.RecId
//   StagingStatus (enum) — processing state
//   ErrorMessage (string 250) — error tracking

// Link field:
//   PersonRecId → DirPerson.RecId
```

#### Staging Table: HRPersonnelStaging

```xpp
table 50101 HRPersonnelStaging
{
    DataClassification = CustomerContent;
    Storage = TempDB;

    fields
    {
        field(1; RecId; int64) { }
        field(2; PersonNumber; Code[20]) { }
        field(3; FirstName; Text[50]) { }
        field(4; LastName; Text[50]) { }
        field(5; Email; Text[250]) { }
        field(6; Position; Text[50]) { }
        field(7; Department; Text[50]) { }
        field(8; HireDate; Date) { }
        field(9; Status; Text[20]) { }
        field(10; StagingStatus; Enum HRPersonnelStagingStatus) { }
        field(11; ErrorMessage; Text[250]) { }
        field(12; ImportBatchId; Guid) { }
        field(13; CreatedDateTime; DateTime) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_PersonNumber; PersonNumber) { }
    }
}
```

#### process() Method with Validation, Deduplication, and Rollback

```xpp
class HRPersonnelEntityHandler
{
    public void process()
    {
        HRPersonnelStaging staging;
        DirPerson targetPerson;
        HCMWorker targetWorker;
        int totalProcessed = 0;
        int totalFailed = 0;
        int totalSuccess = 0;
        Guid batchId = Guid::newGuid();

        // Count total records to process
        totalProcessed = select count(RecId) from staging
            where staging.StagingStatus == HRPersonnelStagingStatus::Ready;

        while select staging
            where staging.StagingStatus == HRPersonnelStagingStatus::Ready
        {
            try
            {
                ttsBegin;

                // Validate email format
                if (!this.validateEmail(staging.Email))
                {
                    this.markFailed(staging, 'Invalid email format');
                    totalFailed++;
                    ttsCommit;
                    continue;
                }

                // Check for duplicates by PersonNumber
                if (this.isDuplicate(staging.PersonNumber))
                {
                    this.markDuplicate(staging);
                    totalFailed++;
                    ttsCommit;
                    continue;
                }

                // Check rollback threshold (>10% failures)
                if (totalFailed > (totalProcessed * 0.1))
                {
                    this.markBatchFailed(staging, 'Rollback threshold exceeded: >10% failures');
                    totalFailed++;
                    ttsCommit;
                    break;  // Stop processing
                }

                // Write to DirPerson
                targetPerson.initValue();
                targetPerson.AccountNum = staging.PersonNumber;
                targetPerson.FirstName = staging.FirstName;
                targetPerson.LastName = staging.LastName;
                targetPerson.Email = staging.Email;
                targetPerson.insert();

                // Write to HCMWorker
                targetWorker.initValue();
                targetWorker.PersonRecId = targetPerson.RecId;
                targetWorker.HireDate = staging.HireDate;
                targetWorker.Status = staging.Status;
                targetWorker.insert();

                // Mark staging as processed
                this.markProcessed(staging);
                totalSuccess++;

                ttsCommit;
            }
            catch (Exception::Error)
            {
                ttsAbort;
                this.markFailed(staging, 'Unexpected error during processing');
                totalFailed++;
            }
        }

        // Store summary for postProcess
        this.setBatchSummary(batchId, totalSuccess, totalFailed);
    }

    private boolean validateEmail(str _email)
    {
        // Simple email format validation
        return strScan(_email, '@', 1, strlen(_email)) > 0
            && strScan(_email, '.', strScan(_email, '@', 1, strlen(_email)), strlen(_email)) > 0;
    }

    private boolean isDuplicate(str _personNumber)
    {
        DirPerson existing;
        return exists select firstonly existing
            where existing.AccountNum == _personNumber;
    }

    private void markFailed(HRPersonnelStaging _staging, str _error)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Failed;
        _staging.ErrorMessage = _error;
        _staging.update();
    }

    private void markDuplicate(HRPersonnelStaging _staging)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Duplicate;
        _staging.ErrorMessage = 'Duplicate PersonNumber';
        _staging.update();
    }

    private void markProcessed(HRPersonnelStaging _staging)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::Processed;
        _staging.update();
    }

    private void markBatchFailed(HRPersonnelStaging _staging, str _error)
    {
        _staging.StagingStatus = HRPersonnelStagingStatus::BatchFailed;
        _staging.ErrorMessage = _error;
        _staging.update();
    }

    private void setBatchSummary(Guid _batchId, int _success, int _failed)
    {
        // Store summary for postProcess to use
        // This could be in a configuration table or a static variable
    }
}
```

#### postProcess() Method with Summary and Notification

```xpp
public void postProcess()
{
    int successCount = this.getSuccessCount();
    int failedCount = this.getFailedCount();
    int totalCount = successCount + failedCount;

    info(strFmt('HR Personnel import complete: %1 succeeded, %2 failed, %3 total.',
        successCount, failedCount, totalCount));

    // Send notification for failed records
    if (failedCount > 0)
    {
        // Option 1: Direct email (requires SMTP configuration)
        // SmtpMail::send(...);

        // Option 2: Trigger Logic App via Service Bus (recommended)
        this.triggerIntegrationNotification(successCount, failedCount);
    }
}
```

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeHRIntegration</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeHRIntegrationEnabled</ConfigurationKey>
</ModelManifest>
```

---

### Remaining Chapters — Detailed Outlines


# Chapter 17: SSRS & Electronic Reporting

> **Complete reference for building, deploying, and troubleshooting SSRS reports and Electronic Reporting (ER) in Dynamics 365 Finance & Operations.**
> Covers report architecture, `SrsReportDataProvider` patterns, data contracts, ER configurations, and a production-ready capstone activity.

---

## Table of Contents

1. [SSRS Report Architecture](#1-ssrs-report-architecture)
2. [SrsReportDataProvider — The Bridge](#2-srsreportdataprovider--the-bridge)
3. [Data Contracts and Parameters](#3-data-contracts-and-parameters)
4. [TempDB Pre-Processing Pattern](#4-tempdb-pre-processing-pattern)
5. [Report Design: RDL Layout and Visual Studio](#5-report-design-rdl-layout-and-visual-studio)
6. [Electronic Reporting (ER) Overview](#6-electronic-reporting-er-overview)
7. [ER Configurations and Format Designer](#7-er-configurations-and-format-designer)
8. [Power BI Integration](#8-power-bi-integration)
9. [Capstone Activity: Build a Multi-Company Vendor Compliance Report](#9-capstone-activity-build-a-multi-company-vendor-compliance-report)
10. [Common Mistakes to Avoid](#10-common-mistakes-to-avoid)
11. [Microsoft Learn References](#11-microsoft-learn-references)

---

## 1. SSRS Report Architecture

### 1.1 The Three-Tier Reporting Model

D365 F&O SSRS reports follow a three-tier architecture that separates concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT TIER (Browser)                        │
│  • User views rendered report (HTML/PDF/Excel)                      │
│  • Report parameters entered via UI                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION TIER (AOS)                         │
│  • SrsReportDataProvider (X++) — Business logic & data retrieval   │
│  • SrsReportRunController — Orchestration & parameter handling     │
│  • TempDB — Intermediate data storage for pre-processing           │
│  • SSRS Report Server — Rendering engine                           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ SQL
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE TIER (Azure SQL)                    │
│  • Business tables (VendTable, CustTable, etc.)                    │
│  • Temp tables (ReportTmp) — populated by data provider            │
│  • System tables (SysReportRun, etc.)                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Report Project Structure

When you add an SSRS report to a D365 F&O project, Visual Studio creates the following structure:

```
MyModelProject
├── Reports/
│   └── ComplianceSummaryReport.rdl
├── Classes/
│   └── VendComplianceReportDP.cs  (Data Provider class)
├── Data Sources/
│   └── VendComplianceDataSource  (shared data source)
└── ModelManifest.xml
```

### 1.3 Report Execution Flow

```
[1] User opens report from menu item
    │
[2] SrsReportRunController.main() executes
    │  - Instantiates data provider
    │  - Shows parameter dialog (if any)
    │  - Calls dataProvider.processReport()
    │
[3] Data Provider populates TempDB table
    │  - Runs queries against business tables
    │  - Inserts records into ReportTmp table
    │
[4] SSRS Renderer reads TempDB table
    │  - Executes RDL layout
    │  - Formats data (grouping, sorting, calculations)
    │
[5] Report rendered to client (HTML/PDF/Excel)
```

### 1.4 Key Report Classes

| Class | Purpose | Extends |
|---|---|---|
| `SrsReportDataProvider` | Standard data provider — query-based | `Object` |
| `SrsReportDataProviderPreProcessTempDB` | TempDB pre-processing data provider | `SrsReportDataProvider` |
| `SrsReportRunController` | Controller for report execution | `SrsReportRunController` |
| `SrsReportDataContract` | Parameter contract for reports | `Object` |

---

## 2. SrsReportDataProvider — The Bridge

`SrsReportDataProvider` is the bridge between the SSRS report layout and the D365 F&O data. It is the most critical class in the reporting architecture.

### 2.1 The `SrsReportDataProvider` Pattern

Every SSRS report in D365 F&O requires a data provider class that extends `SrsReportDataProvider`. This class:

1. Defines the query that retrieves data from the database
2. Provides parameters to the report
3. Handles report-level logic (grouping, calculations)
4. Bridges the gap between the AOS and the SSRS renderer

### 2.2 Key Methods

| Method | Purpose | Required? |
|---|---|---|
| `parmQuery()` | Gets/sets the query object that defines the data source | Yes |
| `parmPrintJobSettings()` | Gets/sets the print job settings (routing, format) | Yes |
| `processReport()` | Called by the reporting framework at runtime; populates a temp table member with the report data | Yes |
| `getVendorComplianceReportTmp()` (tagged with `[SRSReportDataSetAttribute]`) | Returns the populated temp table; the report dataset binds to this method | Yes |
| `parmReportName()` | Gets/sets the report name | Yes |
| `parmParameters()` | Gets/sets the report parameters | Optional |

### 2.3 Complete `SrsReportDataProvider` Example

```xpp
[SRSReportQueryAttribute('VendComplianceReport'), SRSReportParameterAttribute(classstr(VendComplianceReportContract))]
class VendComplianceReportDP extends SrsReportDataProvider
{
    VendComplianceReportTmp tmpTable;
    VendTable vendTable;
    FromDate fromDate;
    ToDate toDate;
    ComplianceStatus complianceStatus;

    /// <summary>
    /// Called by the SSRS framework when the report is rendered.
    /// Populates the temp table with report data.
    /// </summary>
    public void processReport()
    {
        VendComplianceReportContract contract;

        // Get the contract (parameters) from the controller
        contract = this.parmDataContract() as VendComplianceReportContract;

        // Build the query to retrieve compliance data
        this.buildQuery(contract);

        // Execute the query and populate the temp table
        this.fetchData(contract, tmpTable);
    }

    /// <summary>
    /// Returns the populated temp table to the report dataset.
    /// The SRSReportDataSetAttribute binds this method to the report.
    /// </summary>
    [SRSReportDataSetAttribute(tableStr(VendComplianceReportTmp))]
    public VendComplianceReportTmp getVendorComplianceReportTmp()
    {
        return tmpTable;
    }

    private void buildQuery(VendComplianceReportContract _contract)
    {
        Query query = new Query();
        QueryBuildDataSource qbdVend;
        QueryBuildDataSource qbdDeclaration;
        QueryBuildRange qbr;

        // Primary data source: VendTable
        qbdVend = query.addDataSource(tableNum(VendTable));
        qbdVend.relations(true);  // Include related tables

        // Add range for vendor group
        if (_contract.parmVendGroup())
        {
            qbr = qbdVend.addRange(fieldNum(VendTable, CustGroup));
            qbr.value(queryValue(_contract.parmVendGroup()));
        }

        // Join to APCustomsDeclaration
        qbdDeclaration = qbdVend.addDataSource(tableNum(APCustomsDeclaration));
        qbdDeclaration.joinMode(JoinMode::InnerJoin);
        qbdDeclaration.relations(true);

        // Add date range filter
        qbr = qbdDeclaration.addRange(fieldNum(APCustomsDeclaration, DeclDate));
        qbr.value(strfmt('"%1" .. "%2"', _contract.parmFromDate(), _contract.parmToDate()));

        // Add compliance status filter
        if (_contract.parmComplianceStatus())
        {
            qbr = qbdDeclaration.addRange(fieldNum(APCustomsDeclaration, Status));
            qbr.value(queryValue(_contract.parmComplianceStatus()));
        }

        // Set the query on the data provider
        this.parmQuery(query);
    }

    private void fetchData(VendComplianceReportContract _contract, VendComplianceReportTmp _tmp)
    {
        VendTable vendTableLocal;
        APCustomsDeclaration declaration;

        while select vendTableLocal
            join declaration
            where declaration.VendTableRecId == vendTableLocal.RecId
            && declaration.DeclDate >= _contract.parmFromDate()
            && declaration.DeclDate <= _contract.parmToDate()
        {
            _tmp.clear();
            _tmp.AccountNum = vendTableLocal.AccountNum;
            _tmp.VendorName = vendTableLocal.Name;
            _tmp.DeclId = declaration.DeclId;
            _tmp.DeclDate = declaration.DeclDate;
            _tmp.CustomsRef = declaration.CustomsRef;
            _tmp.Status = declaration.Status;
            _tmp.insert();
        }
    }

    // Parameter getters/setters
    public VendTable parmVendTable(VendTable _vendTable = vendTable)
    {
        vendTable = _vendTable;
        return vendTable;
    }

    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }
}
```

---

## 3. Data Contracts and Parameters

### 3.1 The Contract Class

The contract class defines the report parameters and is passed between the controller and the data provider:

```xpp
/// <summary>
/// Data contract for VendComplianceReport parameters.
/// </summary>
[DataContractAttribute]
class VendComplianceReportContract extends SrsReportDataContract
{
    VendGroup _vendGroup;
    FromDate _fromDate;
    ToDate _toDate;
    ComplianceStatus _complianceStatus;

    [DataMemberAttribute('VendGroup')]
    public VendGroup parmVendGroup(VendGroup _vendGroup = _vendGroup)
    {
        return _vendGroup;
    }

    [DataMemberAttribute('FromDate')]
    public FromDate parmFromDate(FromDate _fromDate = _fromDate)
    {
        return _fromDate;
    }

    [DataMemberAttribute('ToDate')]
    public ToDate parmToDate(ToDate _toDate = _toDate)
    {
        return _toDate;
    }

    [DataMemberAttribute('ComplianceStatus')]
    public ComplianceStatus parmComplianceStatus(ComplianceStatus _complianceStatus = _complianceStatus)
    {
        return _complianceStatus;
    }
}
```

### 3.2 The Controller Class

The controller orchestrates report execution, shows the parameter dialog, and launches the rendering:

```xpp
/// <summary>
/// Controller for VendComplianceReport.
/// </summary>
class VendComplianceReportController extends SrsReportRunController
{
    /// <summary>
    /// Main entry point — called from menu item.
    /// </summary>
    public static void main(Args _args)
    {
        VendComplianceReportController controller = new VendComplianceReportController();
        
        controller.parmReportName(ssrsReportStr(VendComplianceReport, Report));
        controller.parmShowDialog(true);
        controller.startOperation();
    }

    /// <summary>
    /// Pre-run validation.
    /// </summary>
    public void preRunValidate()
    {
        super();
        
        // Validate date range
        if (this.parmDataContract() is VendComplianceReportContract)
        {
            VendComplianceReportContract contract = this.parmDataContract();
            
            if (contract.parmFromDate() > contract.parmToDate())
            {
                throw error('From Date cannot be after To Date');
            }
        }
    }
}
```

### 3.3 Menu Item Configuration

Create a **Display Menu Item** to launch the report:

| Property | Value |
|---|---|
| **Name** | `VendComplianceReport` |
| **Object Type** | `Class` |
| **Object** | `VendComplianceReportController` |
| **Label** | `Vendor Compliance Report` |

---

## 4. TempDB Pre-Processing Pattern

### 4.1 Why Use `SrsReportDataProviderPreProcessTempDB`?

For large datasets, the standard `SrsReportDataProvider` can be slow because it executes the query at render time. The **TempDB pre-processing pattern** moves data retrieval to a batch job, populating a TempDB table beforehand. At render time, the report simply reads the pre-populated table — dramatically faster.

### 4.2 `SrsReportDataProviderPreProcessTempDB` Pattern

```xpp
[SRSReportQueryAttribute('VendComplianceReport'), SRSReportParameterAttribute(classstr(VendComplianceReportContract))]
class VendComplianceReportDP extends SrsReportDataProviderPreProcessTempDB
{
    VendComplianceReportTmp tmpTable;

    /// <summary>
    /// Called by the batch job to pre-process data.
    /// Populates the temp table asynchronously.
    /// </summary>
    public void processReport()
    {
        VendComplianceReportContract contract;
        Query query;

        contract = this.parmDataContract() as VendComplianceReportContract;

        // Build the same query as the standard pattern
        query = this.buildQuery(contract);

        // Execute query and populate temp table
        this.populateTempTable(query, tmpTable);
    }

    /// <summary>
    /// Returns the temp table to the report dataset.
    /// </summary>
    [SRSReportDataSetAttribute(tableStr(VendComplianceReportTmp))]
    public VendComplianceReportTmp getVendorComplianceReportTmp()
    {
        return tmpTable;
    }

    private Query buildQuery(VendComplianceReportContract _contract)
    {
        Query query = new Query();
        QueryBuildDataSource qbdVend = query.addDataSource(tableNum(VendTable));
        qbdVend.relations(true);

        if (_contract.parmVendGroup())
        {
            qbdVend.addRange(fieldNum(VendTable, CustGroup))
                .value(queryValue(_contract.parmVendGroup()));
        }

        QueryBuildDataSource qbdDecl = qbdVend.addDataSource(tableNum(APCustomsDeclaration));
        qbdDecl.joinMode(JoinMode::InnerJoin);
        qbdDecl.relations(true);

        qbdDecl.addRange(fieldNum(APCustomsDeclaration, DeclDate))
            .value(strfmt('"%1" .. "%2"', _contract.parmFromDate(), _contract.parmToDate()));

        if (_contract.parmComplianceStatus())
        {
            qbdDecl.addRange(fieldNum(APCustomsDeclaration, Status))
                .value(queryValue(_contract.parmComplianceStatus()));
        }

        return query;
    }

    private void populateTempTable(Query _query, VendComplianceReportTmp _tmp)
    {
        VendTable vendTable;
        APCustomsDeclaration decl;

        // Clear existing data
        _tmp.deleteFrom();

        QueryRun queryRun = new QueryRun(_query);
        while (queryRun.next())
        {
            vendTable = queryRun.get(tableNum(VendTable));
            decl = queryRun.get(tableNum(APCustomsDeclaration));

            _tmp.clear();
            _tmp.AccountNum = vendTable.AccountNum;
            _tmp.VendorName = vendTable.Name;
            _tmp.DeclId = decl.DeclId;
            _tmp.DeclDate = decl.DeclDate;
            _tmp.CustomsRef = decl.CustomsRef;
            _tmp.Status = decl.Status;
            _tmp.insert();
        }
    }
}
```

### 4.3 TempDB Table Definition

The temp table must use `Storage = TempDB`:

```xpp
table VendComplianceReportTmp
{
    DataClassification = CustomerContent;
    Storage = TempDB;  // Critical — uses TempDB, not InMemory

    fields
    {
        field(AccountNum; AccountNum) { }
        field(VendorName; Name) { }
        field(DeclId; Code[35]) { }
        field(DeclDate; Date) { }
        field(CustomsRef; Code[50]) { }
        field(Status; Text[20]) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_AccountNum; AccountNum) { }
    }
}
```

### 4.4 Execution Modes Comparison

| Mode | When Data Is Fetched | Best For |
|---|---|---|
| **Standard (`SrsReportDataProvider`)** | At render time (synchronous) | Small datasets (< 10K rows), interactive reports |
| **TempDB Pre-Process (`SrsReportDataProviderPreProcessTempDB`)** | In batch job (asynchronous) | Large datasets (> 10K rows), scheduled reports, complex queries |

---

## 5. Report Design: RDL Layout and Visual Studio

### 5.1 Visual Studio Report Designer

1. **Open** the `.rdl` file in Visual Studio
2. **Report Data** pane: Datasets, Parameters, Images
3. **Design** surface: Tablix, Matrix, Chart, Gauge
4. **Properties** window: Formatting, visibility, expressions

### 5.2 Dataset Binding

The report dataset binds to the data provider's getter method:

```xpp
// In RDL, the dataset is bound to:
// Fields → getVendorComplianceReportTmp()
// The dataset fields correspond to the temp table fields
```

### 5.3 Common RDL Patterns

| Pattern | Implementation |
|---|---|
| **Grouping** | Row Groups → Add Group → Group By: `AccountNum` |
| **Page Breaks** | Group Properties → Page Break → Between each instance |
| **Conditional Formatting** | Text Box Properties → Fill → Expression: `=IIf(Fields!Status.Value = "Failed", "Red", "Green")` |
| **Running Totals** | `=RunningValue(Fields!Amount.Value, Sum, "DataSet1")` |
| **Subreports** | Insert → Subreport → Use another report as child |

### 5.4 Performance Tips for RDL

1. **Limit fields in dataset** — only include fields used in layout
2. **Use server-side grouping** — do grouping in SQL query, not RDL
3. **Avoid complex expressions** — move calculations to data provider
4. **Use page breaks sparingly** — each break adds rendering overhead

---

## 6. Electronic Reporting (ER) Overview

### 6.1 What Is Electronic Reporting?

**Electronic Reporting (ER)** is a no-code/low-code framework for generating electronic documents (XML, JSON, Excel, PDF, TXT) from D365 F&O data. Unlike SSRS, ER is designed for **regulatory reporting**, **integration files**, and **document generation** where format changes frequently.

### 6.2 ER vs SSRS Comparison

| Aspect | SSRS | Electronic Reporting |
|---|---|---|
| **Primary Use** | Operational reports, dashboards, analytics | Regulatory filings, integration files, document generation |
| **Design Tool** | Visual Studio (RDL) | Web-based Format Designer |
| **Code Required** | Yes (`SrsReportDataProvider` X++) | Minimal (formula-based) |
| **Format Changes** | Requires VS rebuild & deploy | Hot-swappable without code deploy |
| **Regulatory Updates** | Slow — code change + deploy | Fast — config change in UI |
| **Output Formats** | PDF, Excel, Word, HTML | XML, JSON, Excel, PDF, TXT, CSV |
| **Versioning** | Model versioning | Built-in configuration versioning |

### 6.3 ER Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ER CONFIGURATION HIERARCHY                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODEL (Root)                                                   │
│  │                                                              │
│  ├── DATA MODEL — Defines the data structure (entities, fields) │
│  │    └── Model Mapping — Maps data model to D365 tables        │
│  │                                                              │
│  ├── FORMAT (Child of Model)                                    │
│  │    └── Format Designer — Visual layout (Excel/JSON/XML)      │
│  │         └── Format Mapping — Binds format to data model      │
│  │                                                              │
│  └── FILE — Actual generated output                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. ER Configurations and Format Designer

### 7.1 Creating an ER Configuration

**Step 1: Create the Model**
1. Navigate to **Organization Administration > Electronic Reporting > Configurations**
2. Click **Create Configuration** → **Model**
3. Name: `Vendor Compliance Model`
4. Add data model elements: `Vendor`, `ComplianceDeclaration`, `CustomsReference`

**Step 2: Create Model Mapping**
1. Select model → **Designer** → **Map model to datasource**
2. Add data sources:
   - `VendTable` (Table records)
   - `APCustomsDeclaration` (Table records)
3. Bind model fields to table fields

**Step 3: Create the Format**
1. Click **Create Configuration** → **Format** (based on model)
2. Name: `Vendor Compliance XML Format`
3. Open **Format Designer**

### 7.2 Format Designer — Visual Layout

The Format Designer provides a tree-based visual editor:

```
Format: Vendor Compliance XML
├── VendorComplianceReport (Root Element)
│   ├── Header (Sequence)
│   │   ├── ReportName (String)
│   │   ├── GeneratedDateTime (DateTime)
│   │   └── CompanyCode (String)
│   │
│   ├── Vendors (Collection)
│   │   ├── Vendor (Sequence)
│   │   │   ├── AccountNum (String)
│   │   │   ├── Name (String)
│   │   │   └── Group (String)
│   │   │
│   │   ├── Declarations (Collection)
│   │   │   ├── Declaration (Sequence)
│   │   │   │   ├── DeclId (String)
│   │   │   │   ├── DeclDate (Date)
│   │   │   │   ├── CustomsRef (String)
│   │   │   │   └── Status (String)
│   │   │   │
│   │   └── Footer (Sequence)
│   │       ├── TotalVendors (Integer)
│   │       └── TotalDeclarations (Integer)
```

### 7.3 Formula Expressions

ER uses Excel-like formulas for calculations:

| Function | Example | Purpose |
|---|---|---|
| `COUNT` | `COUNT(Vendors.Declaration)` | Count child records |
| `SUM` | `SUM(Vendors.Declaration.Amount)` | Sum numeric field |
| `CONCATENATE` | `CONCATENATE("COMP-", CompanyInfo::Name())` | Build strings |
| `FORMAT` | `FORMAT(TODAY(), "yyyy-MM-dd")` | Format dates |
| `IF` | `IF(Status = "Failed", "ERROR", "OK")` | Conditional logic |
| `FILTER` | `FILTER(Vendors, Group = "VIP")` | Filter collections |

### 7.4 Running ER Configurations

```xpp
/// <summary>
/// Runs an ER configuration programmatically.
/// </summary>
class ERRunner
{
    public static void runVendorComplianceExport()
    {
        ERFormatMappingRun formatRun;
        ERFormatMapping formatMapping;
        ERModelMapping modelMapping;
        
        // Find the format mapping by name
        formatMapping = ERFormatMapping::findByName('Vendor Compliance XML Format');
        
        if (formatMapping)
        {
            formatRun = ERFormatMappingRun::construct(formatMapping);
            
            // Set parameters
            formatRun.parmCompany(CompanyInfo::find().DataArea);
            formatRun.parmFileName('VendorCompliance_' + DateTimeUtil::toStr(DateTimeUtil::utcNow()) + '.xml');
            
            // Execute
            formatRun.run();
            
            info('ER export completed');
        }
        else
        {
            error('Format mapping not found');
        }
    }
}
```

---

## 8. Power BI Integration

### 8.1 Power BI and D365 F&O

Power BI can connect to D365 F&O data through:
1. **OData Feed** — Direct connection to Data Entities
2. **Azure SQL Database** — Direct database access (read-only replica)
3. **Entity Store** — Pre-aggregated analytical data (BYOD)
4. **Composite Data Entities** — For complex analytical models

### 8.2 Connecting Power BI via OData

1. Open Power BI Desktop
2. **Get Data** → **OData Feed**
3. URL: `https://<env>.dynamics.com/data/`
4. Select entities: `Vendors`, `Customers`, `SalesOrders`
5. **Load** or **Transform Data** (Power Query)

### 8.3 Best Practices for Power BI

| Practice | Reason |
|---|---|
| Use **Data Entities** as source | Abstraction, security, performance |
| Enable **incremental refresh** | Large datasets, scheduled updates |
| Use **Entity Store** for analytics | Pre-aggregated, optimized for BI |
| Limit columns in query | Reduce data transfer |
| Implement **row-level security** | Match D365 security model |

---

## 9. Capstone Activity: Build a Multi-Company Vendor Compliance Report

> **Objective**: Build a production-ready SSRS report with TempDB pre-processing and an ER configuration for XML export.

### 9.1 Requirements

**SSRS Report:**
1. **Report Name**: `MultiCompanyVendorComplianceReport`
2. **Parameters**: Company (multi-select), Date Range, Compliance Status
3. **Data Provider**: `SrsReportDataProviderPreProcessTempDB` (batch pre-processing)
4. **Layout**: Grouped by Company → Vendor → Declarations
5. **Output**: PDF for compliance officers, Excel for analysis

**ER Configuration:**
1. **Format Name**: `MultiCompanyVendorComplianceXML`
2. **Output**: XML for external audit system
2. **Fields**: All report fields + Company code
3. **Delivery**: Logic App triggered from `postProcess()`

---

### 9.2 SSRS Implementation

**TempDB Table:**
```xpp
table MultiCompanyVendorComplianceTmp
{
    Storage = TempDB;
    DataClassification = CustomerContent;

    fields
    {
        field(CompanyCode; Code[4]) { }
        field(AccountNum; AccountNum) { }
        field(VendorName; Name) { }
        field(DeclId; Code[35]) { }
        field(DeclDate; Date) { }
        field(CustomsRef; Code[50]) { }
        field(Status; Text[20]) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_Company; CompanyCode, AccountNum) { }
    }
}
```

**Data Provider:**
```xpp
[SRSReportQueryAttribute('MultiCompanyVendorComplianceReport'), 
 SRSReportParameterAttribute(classstr(MultiCompanyVendorComplianceContract))]
class MultiCompanyVendorComplianceDP extends SrsReportDataProviderPreProcessTempDB
{
    MultiCompanyVendorComplianceTmp tmpTable;

    public void processReport()
    {
        MultiCompanyVendorComplianceContract contract;
        Query query;
        Container companyList;

        contract = this.parmDataContract() as MultiCompanyVendorComplianceContract;
        companyList = contract.parmCompanyList();

        query = this.buildQuery(contract, companyList);
        this.populateTempTable(query, tmpTable);
    }

    [SRSReportDataSetAttribute(tableStr(MultiCompanyVendorComplianceTmp))]
    public MultiCompanyVendorComplianceTmp getMultiCompanyVendorComplianceTmp()
    {
        return tmpTable;
    }

    private Query buildQuery(MultiCompanyVendorComplianceContract _contract, Container _companyList)
    {
        Query query = new Query();
        QueryBuildDataSource qbdVend = query.addDataSource(tableNum(VendTable));
        qbdVend.relations(true);

        // Multi-company filter
        if (conLen(_companyList) > 0)
        {
            qbdVend.addRange(fieldNum(VendTable, DataAreaId))
                .value(this.buildCompanyRange(_companyList));
        }

        // Date range on declarations
        QueryBuildDataSource qbdDecl = qbdVend.addDataSource(tableNum(APCustomsDeclaration));
        qbdDecl.joinMode(JoinMode::InnerJoin);
        qbdDecl.relations(true);

        qbdDecl.addRange(fieldNum(APCustomsDeclaration, DeclDate))
            .value(strfmt('"%1" .. "%2"', _contract.parmFromDate(), _contract.parmToDate()));

        if (_contract.parmComplianceStatus())
        {
            qbdDecl.addRange(fieldNum(APCustomsDeclaration, Status))
                .value(queryValue(_contract.parmComplianceStatus()));
        }

        return query;
    }

    private str buildCompanyRange(Container _companyList)
    {
        str range = '';
        int i;
        for (i = 1; i <= conLen(_companyList); i++)
        {
            range += conPeek(_companyList, i);
            if (i < conLen(_companyList)) { range += ','; }
        }
        return range;
    }

    private void populateTempTable(Query _query, MultiCompanyVendorComplianceTmp _tmp)
    {
        VendTable vendTable;
        APCustomsDeclaration decl;

        _tmp.deleteFrom();

        QueryRun queryRun = new QueryRun(_query);
        while (queryRun.next())
        {
            vendTable = queryRun.get(tableNum(VendTable));
            decl = queryRun.get(tableNum(APCustomsDeclaration));

            _tmp.clear();
            _tmp.CompanyCode = vendTable.DataAreaId;
            _tmp.AccountNum = vendTable.AccountNum;
            _tmp.VendorName = vendTable.Name;
            _tmp.DeclId = decl.DeclId;
            _tmp.DeclDate = decl.DeclDate;
            _tmp.CustomsRef = decl.CustomsRef;
            _tmp.Status = decl.Status;
            _tmp.insert();
        }
    }
}
```

**Contract:**
```xpp
[DataContractAttribute]
class MultiCompanyVendorComplianceContract extends SrsReportDataContract
{
    Container _companyList;
    FromDate _fromDate;
    ToDate _toDate;
    ComplianceStatus _complianceStatus;

    [DataMemberAttribute('CompanyList')]
    public Container parmCompanyList(Container _companyList = _companyList)
    {
        return _companyList;
    }

    [DataMemberAttribute('FromDate')]
    public FromDate parmFromDate(FromDate _fromDate = _fromDate)
    {
        return _fromDate;
    }

    [DataMemberAttribute('ToDate')]
    public ToDate parmToDate(ToDate _toDate = _toDate)
    {
        return _toDate;
    }

    [DataMemberAttribute('ComplianceStatus')]
    public ComplianceStatus parmComplianceStatus(ComplianceStatus _complianceStatus = _complianceStatus)
    {
        return _complianceStatus;
    }
}
```

---

### 9.3 ER Configuration

**Model:** `MultiCompanyVendorComplianceModel`
**Format:** `MultiCompanyVendorComplianceXML`

**Format Designer Layout:**
```
Root: VendorComplianceExport
├── Header
│   ├── ExportDateTime = DATETIMEFORMAT(NOW(), "yyyy-MM-ddTHH:mm:ss")
│   ├── CompanyCount = COUNT(Companies)
│   └── TotalDeclarations = SUM(Companies.Vendors.Declarations)
│
├── Companies (Collection)
│   ├── CompanyCode = DataAreaId
│   ├── CompanyName = CompanyInfo::Name()
│   │
│   ├── Vendors (Collection)
│   │   ├── AccountNum
│   │   ├── Name
│   │   │
│   │   ├── Declarations (Collection)
│   │   │   ├── DeclId
│   │   │   ├── DeclDate = FORMAT(DeclDate, "yyyy-MM-dd")
│   │   │   ├── CustomsRef
│   │   │   └── Status
│   │
│   └── CompanySummary
│       ├── VendorCount = COUNT(Vendors)
│       └── DeclarationCount = COUNT(Vendors.Declarations)
```

---

## 10. Common Mistakes to Avoid

| # | Mistake | Why It's Wrong | Correct Approach |
|---|---|---|---|
| 1 | **Using `SrsReportDataProvider` for large datasets** | Times out at render time; blocks user session | Use `SrsReportDataProviderPreProcessTempDB` with batch pre-processing |
| 2 | **TempDB table uses `InMemory` storage** | Memory pressure, data loss on AOS restart | Always use `Storage = TempDB` for report temp tables |
| 3 | **Complex calculations in RDL expressions** | Slow rendering, hard to debug | Move calculations to data provider X++ code |
| 4 | **No indexing on temp table** | Slow report rendering on large datasets | Add indexes on grouping/filtering fields |
| 5 | **Hardcoded company filter** | Report only works in one company | Use `DataAreaId` range from parameter |
| 6 | **Missing `deleteFrom()` in pre-process** | Duplicate data on re-run | Always clear temp table at start of `processReport()` |
| 7 | **ER format hardcoded to one company** | Can't generate multi-company output | Use `CompanyInfo::Name()` and `DataAreaId` in format |
| 8 | **SSRS and ER duplicating logic** | Maintenance nightmare | Use SSRS for operational reports, ER for regulatory/integration |
| 9 | **No parameter validation in controller** | Invalid dates/ranges cause confusing errors | Validate in `preRunValidate()` |
| 10 | **Not testing with production data volumes** | Performance issues only appear in prod | Test with Tier-2 data or generated test data |

---

## 11. Microsoft Learn References

### SSRS Reporting
- **SSRS Reports Overview**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-reporting/
- **SrsReportDataProvider**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-report-data-provider
- **Report Design Best Practices**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/report-design-best-practices
- **TempDB Pre-Processing**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/ssrs-tempdb-preprocessing

### Electronic Reporting
- **ER Overview**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/electronic-reporting
- **ER Format Designer**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/er-format-designer
- **ER Formula Language**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/er-formula-language
- **ER Model Mapping**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/er-model-mapping

### Power BI
- **Power BI Integration**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/power-bi-integration
- **Entity Store**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/entity-store

---

*End of Chapter 17 — SSRS & Electronic Reporting*

```xpp
[DataContractAttribute]
class VendComplianceReportContract
{
    VendGroup vendGroup;
    FromDate fromDate;
    ToDate toDate;
    ComplianceStatus complianceStatus;

    [DataMemberAttribute('VendGroup'), SysOperationLabelAttribute('Vendor Group')]
    public VendGroup parmVendGroup(VendGroup _vendGroup = vendGroup)
    {
        vendGroup = _vendGroup;
        return vendGroup;
    }

    [DataMemberAttribute('FromDate'), SysOperationLabelAttribute('From Date')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    [DataMemberAttribute('ToDate'), SysOperationLabelAttribute('To Date')]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }

    [DataMemberAttribute('ComplianceStatus'), SysOperationLabelAttribute('Compliance Status')]
    public ComplianceStatus parmComplianceStatus(ComplianceStatus _status = complianceStatus)
    {
        complianceStatus = _status;
        return complianceStatus;
    }
}
```

---

## 17.3 `PrintJobSettings` — Routing Reports

`PrintJobSettings` controls how reports are routed to their destination — printer, PDF, email, or preview.

### PrintJobSettings Properties

| Property | Description | Common Values |
|---|---|---|
| `PrinterName` | The target printer | `'\\PrintServer\Printer1'` or empty for PDF |
| `PrintMedium` | Output medium | `PrintMedium::Printer`, `PrintMedium::File`, `PrintMedium::Email` |
| `FileName` | Output file path (when `PrintMedium = File`) | `'C:\Reports\Compliance.pdf'` |
| `EmailTo` | Recipient email address | `'compliance@acme.com'` |
| `EmailSubject` | Email subject line | `'Monthly Compliance Report'` |
| `EmailBody` | Email body text | `'Please find the compliance report attached.'` |
| `FileFormat` | Output format | `FileFormat::PDF`, `FileFormat::Excel`, `FileFormat::Word` |
| `NumberOfCopies` | Number of copies to print | `1` |
| `Sides` | Single or double-sided | `Sides::OneSided`, `Sides::TwoSidedLongEdge` |

### Setting PrintJobSettings Programmatically

```xpp
class VendComplianceReportController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VendComplianceReportController controller = new VendComplianceReportController();
        VendComplianceReportContract contract = new VendComplianceReportContract();

        // Populate contract from args
        if (_args && _args.record())
        {
            contract.parmVendTable(_args.record());
        }

        controller.parmContractType(classStr(VendComplianceReportContract));
        controller.parmServiceType(classStr(VendComplianceService));
        controller.parmCaption('Vend Compliance Report');

        // Configure print job settings
        PrintJobSettings printJobSettings = controller.parmPrintJobSettings();
        printJobSettings.parmPrintMedium(PrintMedium::File);
        printJobSettings.parmFileFormat(FileFormat::PDF);
        printJobSettings.parmFileName(@"C:\Reports\VendCompliance_" + date2str(today(), 123, 2, 3, 2, 3, 4));

        controller.startOperation();
    }
}
```

### PrintJobSettings in the Report Dialog

When a user runs a report from the D365 F&O client, the `PrintJobSettings` dialog appears:

1. **Printer selection** — choose a printer or "Print to PDF"
2. **Format** — PDF, Excel, Word, or HTML
3. **Range** — print all pages, current page, or a page range
4. **Copies** — number of copies
5. **Email** — enter recipient email to send the report as an attachment

---

## 17.4 `AutoDesign` vs. Manual RDL Layout

### AutoDesign

`AutoDesign` is the quickest way to generate a report layout. Visual Studio automatically creates a tabular layout based on the dataset fields.

**Pros:**
- Fastest way to get a functional report
- Automatically generates columns for all dataset fields
- Good for initial prototyping and internal reports

**Cons:**
- Limited customization — the layout is generic
- No control over grouping, formatting, or visual design
- Not suitable for production reports that require pixel-perfect layouts

### Manual RDL Layout

Manual RDL design gives full control over the report layout. You design the report in Report Builder or SQL Server Data Tools (SSDT), then import the `.rdl` file into the D365 F&O project.

**Pros:**
- Full control over layout, formatting, fonts, colors
- Support for grouped sections, subtotals, charts, and matrices
- Professional, pixel-perfect output
- Can include conditional formatting, drill-downs, and interactive features

**Cons:**
- More effort to design and wire up
- Requires knowledge of RDL/XML syntax
- Changes to the dataset require manual updates to the layout

### Importing a Manual RDL File

1. Design the report in **Report Builder** or **SSDT**
2. Save as `.rdl` file
3. In Visual Studio, right-click the **Reports** node in the project
4. Select **Add → Existing Item** → choose the `.rdl` file
5. Map the dataset fields in the RDL to the data provider's fields
6. Deploy the model to test

### When to Use Which

| Scenario | Use |
|---|---|
| Initial prototype or internal report | AutoDesign |
| Production report requiring professional layout | Manual RDL |
| Report with grouped sections and subtotals | Manual RDL |
| Report with charts or matrices | Manual RDL |
| Quick one-off data extraction | AutoDesign |
| Report that will be maintained long-term | Manual RDL |

---

## 17.5 `ReportRun` Class — Programmatic Report Execution

The `ReportRun` class allows you to instantiate and run reports programmatically from X++ code.

### Basic Report Execution

```xpp
class VendComplianceReportRunner
{
    public static void runReport()
    {
        ReportRun reportRun;
        VendComplianceReportContract contract;

        // Create the contract with parameters
        contract = new VendComplianceReportContract();
        contract.parmFromDate(01\01\2026);
        contract.parmToDate(31\12\2026);
        contract.parmVendGroup('VENDGROUP1');

        // Instantiate the report
        reportRun = new ReportRun(ReportStr(VendComplianceSummaryReport));

        // Set the contract as the report's data source
        reportRun.parmReportContract(contract);

        // Run the report
        reportRun.runReport();
    }
}
```

### Programmatic PrintJobSettings Configuration

```xpp
// Configure print settings before running
PrintJobSettings printJobSettings = reportRun.parmPrintJobSettings();
printJobSettings.parmPrintMedium(PrintMedium::Email);
printJobSettings.parmEmailTo('compliance@acme.com');
printJobSettings.parmEmailSubject('Monthly Compliance Report');
printJobSettings.parmFileFormat(FileFormat::PDF);
```

### Running Reports from Batch Jobs

```xpp
// From a RunBaseBatch class
public void run()
{
    ReportRun reportRun;
    VendComplianceReportContract contract;

    contract = new VendComplianceReportContract();
    contract.parmFromDate(fromDate);
    contract.parmToDate(toDate);
    contract.parmVendGroup(vendGroup);

    reportRun = new ReportRun(ReportStr(VendComplianceSummaryReport));
    reportRun.parmReportContract(contract);

    // Configure for file output (batch jobs typically output to file)
    PrintJobSettings printJobSettings = reportRun.parmPrintJobSettings();
    printJobSettings.parmPrintMedium(PrintMedium::File);
    printJobSettings.parmFileFormat(FileFormat::PDF);
    printJobSettings.parmFileName(@"C:\Reports\Compliance_" + date2str(today(), 123, 2, 3, 2, 3, 4) + ".pdf");

    reportRun.runReport();

    info(strFmt('Compliance report generated: %1', printJobSettings.parmFileName()));
}
```

---

## 17.6 Legacy AX Reports (Pre-SSRS)

Legacy AX Reports (from AX 2012 or earlier) used `.rpt` files and are sometimes still encountered in older codebases and on-premises deployments. While SSRS is the recommended approach for new development, these legacy reports may still exist in some environments.

### Legacy AX Reports vs. SSRS — Key Differences

| Feature | Legacy AX Reports (`.rpt`) | SSRS (Modern) |
|---|---|---|
| **Report designer** | Report Builder in AX client | Visual Studio SSRS Designer |
| **File format** | `.rpt` | `.rdl` |
| **Data access** | Direct SQL queries | `SrsReportDataProvider` with AOT queries |
| **Deployment** | Manual upload to AOT | Model project deployment via VS |
| **Security** | AOS-level security | Azure AD + D365 F&O security roles |
| **Performance** | No pre-processing optimization | TempDB pre-processing support |
| **OData exposure** | Not supported | Automatic via Data Entities |
| **Maintenance** | Harder to maintain | Model-based, version-controlled |

### When Legacy AX Reports Are Still Relevant

- **On-premises deployments** that haven't been upgraded to the modern SSRS pattern
- **Existing `.rpt` reports** that are still in production and haven't been migrated
- **Custom RDL files** that were designed outside of Visual Studio and need to be integrated

### Migrating from Legacy AX Reports to SSRS

1. **Identify the legacy report** — locate the `.rpt` file in the AOT under `Reports`
2. **Create a new SSRS report** in Visual Studio with the same data source
3. **Recreate the layout** in the SSRS Report Designer — import the old RDL as a starting point
4. **Create a `SrsReportDataProvider`** class to replace the legacy data provider
5. **Test the new report** against the same data set
6. **Update menu items** to point to the new report controller
7. **Deprecate the old report** — mark it as obsolete in the AOT

**Key takeaway:** If you encounter legacy `.rpt` reports in an existing codebase, plan to migrate them to SSRS. The modern SSRS pattern with `SrsReportDataProvider` and AOT Query objects is more maintainable, upgrade-safe, and integrates with the D365 F&O security model.

---

## 17.7 Pre-Processing Optimization for Long-Running Reports

Long-running SSRS reports (>10 minutes) can timeout in D365 F&O. The solution is to use **pre-processing** with TempDB tables instead of InMemory tables.

### The Problem

By default, `SrsReportDataProvider` uses `InMemory` temporary tables for report data. For large datasets, this causes:
- Report timeouts (>10 minutes)
- High memory consumption on the AOS
- Poor user experience with slow report loading

### The Solution: TempDB Pre-Processing

Switch from `InMemory` to `TempDB` table type and use `SrsReportDataProviderPreProcessTempDB`:

```xpp
// ❌ SLOW — InMemory table for large datasets
class VendComplianceReportDP extends SrsReportDataProvider
{
    VendComplianceReportTmp tmpTable;  // InMemory — slow for large data

    public void processReport()
    {
        // Data is held in memory — causes timeout for large datasets
    }
}

// ✅ FAST — TempDB table with pre-processing
class VendComplianceReportDP extends SrsReportDataProviderPreProcessTempDB
{
    VendComplianceReportTmp tmpTable;  // TempDB — fast for large data

    public void processReport()
    {
        // Pre-process: retrieve and store data in TempDB before report renders
    }

    [SRSReportDataSetAttribute(tableStr(VendComplianceReportTmp))]
    public VendComplianceReportTmp getReportDataTmp()
    {
        // Data is pre-processed into TempDB before report rendering
        // The report reads from TempDB — no timeout issues
        return tmpTable;
    }
}
```

### Pre-Processing Pattern

The pre-processing pattern separates data retrieval (which can be slow) from report rendering (which must be fast):

```xpp
class VendComplianceReportDP extends SrsReportDataProviderPreProcessTempDB
{
    VendComplianceReportTmp tmpTable;  // Class member — persists in TempDB across calls
    VendTable vendTable;
    FromDate fromDate;
    ToDate toDate;

    /// <summary>
    /// Pre-process: retrieve and store data in TempDB before report renders.
    /// Called once when the report is first requested.
    /// </summary>
    public void processReport()
    {
        // Retrieve data and store in TempDB
        while select vendTable
            where vendTable.CreatedDate >= fromDate
            && vendTable.CreatedDate <= toDate
        {
            tmpTable.clear();
            tmpTable.AccountNum = vendTable.AccountNum;
            tmpTable.VendorName = vendTable.Name;
            tmpTable.CreditMax = vendTable.CreditMax;
            tmpTable.insert();
        }
    }

    /// <summary>
    /// Return the pre-processed data from TempDB to the report dataset.
    /// The SRSReportDataSetAttribute binds this method to the report.
    /// Called by the SSRS framework during rendering.
    /// </summary>
    [SRSReportDataSetAttribute(tableStr(VendComplianceReportTmp))]
    public VendComplianceReportTmp getReportDataTmp()
    {
        return tmpTable;
    }
}
```

### When to Use Pre-Processing

| Report Size | InMemory | TempDB Pre-Processing |
|---|---|---|
| < 1,000 records | ✅ Fine | Not needed |
| 1,000–10,000 records | ⚠️ May be slow | Recommended |
| 10,000–100,000 records | ❌ Timeout risk | Required |
| > 100,000 records | ❌ Will timeout | Required + optimize query |

### Performance Comparison

| Approach | 10K Records | 100K Records | 1M Records |
|---|---|---|---|
| InMemory + direct query | 5s | 45s (timeout risk) | Timeout |
| TempDB pre-processing | 3s | 8s | 25s |
| TempDB + indexed TempDB table | 2s | 5s | 12s |

---

## 17.8 Electronic Reporting (ER)

Electronic Reporting (ER) is a format-based reporting engine used for tax reporting, regulatory compliance, and data exchange with external systems. It's the standard mechanism for formats like SAF-T, VAT declarations, and other regulatory reports.

### ER Components

| Component | Purpose | Example |
|---|---|---|
| **Format** | Defines the output structure (XML, JSON, CSV, etc.) | SAF-T format, VAT XML schema |
| **Data source** | Defines where the data comes from (tables, views, entities) | `VendTable`, `VendInvoiceJour` |
| **Mapping** | Maps source fields to format fields | `VendTable.AccountNum` → `SupplierID` |
| **Configuration** | Links format, data source, and mapping together | One ER configuration per report |

### ER Format Design

ER formats are designed in the **Electronic Reporting** workspace:

1. Navigate to **Organization Administration → Inquiries → Electronic Reporting → Formats**
2. Create a new format or extend an existing one
3. Define the XML/JSON schema for the output
4. Create mappings that connect source fields to format fields
5. Test the format with sample data

### ER Configuration Example

```xpp
// ER Configuration for VAT Declaration
// Format: VAT XML Schema (e.g., SAF-T EU)
// Data Source: VendInvoiceJour + VendInvoiceLine + TaxTrans
// Mapping: Invoice fields → VAT declaration fields
```

### ER vs. SSRS — When to Use Which

| Scenario | Use ER | Use SSRS |
|---|---|---|
| Tax reporting (VAT, SAF-T) | ✅ Yes | ❌ No |
| Regulatory compliance format | ✅ Yes | ❌ No |
| Data exchange with external systems | ✅ Yes | ❌ No |
| Internal management reports | ❌ No | ✅ Yes |
| Printable invoices/purchase orders | ❌ No | ✅ Yes |
| Financial statements | ❌ No | ✅ Yes |
| Pixel-perfect layout required | ❌ No | ✅ Yes |

### ER Format Extension

You can extend standard ER formats to add custom fields:

1. Open the standard format in the ER workspace
2. Click **Extend** to create a format extension
3. Add your custom fields to the extended format
4. Create mappings for the new fields
5. Activate the extension

```xpp
// ER format extension for custom compliance fields
// The extension adds custom fields to the standard VAT declaration format
// Custom fields: ComplianceCode, AuditReference, InternalNote
```

---

## 17.9 Analytical Reports — Deep Dive

### Analytical Report Architecture

Analytical reports in D365 F&O differ from operational reports (SSRS) in several key ways:

| Aspect | Operational Report | Analytical Report |
|---|---|---|
| **Data source** | `SrsReportDataProvider` with AOT Query | `SysOperationServiceController` with contract |
| **Output** | PDF, Excel, printed | Interactive grid, charts, pivot tables |
| **User interaction** | View/print/export | Filter, drill down, pivot, slice |
| **Framework** | SSRS | Analytical Workspace + Power BI |
| **Data volume** | Detailed transactional | Aggregated summaries |
| **Real-time** | Near real-time (batch) | Near real-time (cached) |

### Analytical Report with Drill-Down

Analytical reports support drill-down from summary to detail:

```xpp
// Analytical report contract with drill-down support
class VendComplianceAnalyticsContract
{
    VendGroup vendGroup;
    FromDate fromDate;
    ToDate toDate;
    ComplianceStatus complianceStatus;
    boolean includeCharts;
    boolean drillDown;       // Enable drill-down to detail
    VendTable drillDownRecord; // The record to drill into
}

class VendComplianceAnalyticsService
{
    public VendComplianceAnalyticsContract process(VendComplianceAnalyticsContract _contract)
    {
        if (_contract.parmDrillDown())
        {
            // Return detailed data for the drilled-in record
            return this.getDrillDownData(_contract);
        }
        else
        {
            // Return aggregated summary data
            return this.getSummaryData(_contract);
        }
    }

    private VendComplianceAnalyticsContract getSummaryData(VendComplianceAnalyticsContract _contract)
    {
        // Aggregate data by vendor group
        // Calculate compliance rates, totals, averages
        // Return summary for the Analytical Workspace
        return _contract;
    }

    private VendComplianceAnalyticsContract getDrillDownData(VendComplianceAnalyticsContract _contract)
    {
        // Return detailed records for the selected vendor
        // This is called when the user clicks a summary row to drill down
        return _contract;
    }
}
```

### Integration with Power BI

D365 F&O's Analytical Workspace integrates with Power BI for advanced analytics:

1. **OData feed**: Analytical reports expose data via OData feeds
2. **Power BI Desktop**: Connect to the OData feed and build interactive dashboards
3. **Power BI Service**: Publish dashboards to the Power BI service
4. **Analytical Workspace**: Pin Power BI tiles to the F&O workspace

### Analytical Report Best Practices

1. **Use aggregation** — analytical reports should summarize data, not show every transaction
2. **Enable drill-down** — users should be able to click a summary row to see detail
3. **Cache results** — use the `SysOperation` framework's caching for frequently accessed reports
4. **Limit data volume** — use date ranges and filters to limit the data returned
5. **Use measures and dimensions** — organize data into measures (numeric) and dimensions (categorical)

---

## 17.10 Activity — Build an End-to-End SSRS Report

> **Activity**: Build an end-to-end SSRS report for the compliance module with the following requirements:
> 1. **Parameters**: Date range (`fromDate`, `toDate`), vendor group (`CustGroup`), compliance status (`Validated`, `Pending`, `Failed`)
> 2. **Data source**: Query joining `VendTable`, `VendInvoiceJour`, `APCustomsDeclaration`, and `VendInvoiceLine` (4+ table joins)
> 3. **Grouped sections**: Group by vendor group, then by vendor, then by compliance status
> 4. **Subtotals**: Show subtotals for each vendor group and each vendor
> 5. **Grand total**: Show a grand total row at the bottom with record count and summary statistics
> 6. **Graceful empty-data handling**: When no records match the filter criteria, display a friendly "No data found" message instead of an empty report
> 7. **Professional layout**: Use a corporate-style header with company logo, report title, date range, and page numbers
> 8. **Export options**: Configure the report to support PDF, Excel, and email delivery
> 9. **Menu item**: Create a `MenuItemOutput` linked to the report class
> 10. **Security**: Restrict report access to the `ComplianceOfficer` role
>
> **Activity Hints** (Multiple Valid Approaches):
>
> - **Hint A — Dataset query design**: Option A1 — use a `SrsReportDataProvider` class with a `Query` object that joins all 4 tables (recommended — follows Microsoft patterns, supports dynamic filtering). Option A2 — use a `View` object as the data source (simpler but less flexible — can't dynamically add filters at runtime). Option A3 — use inline `select` statements in the data provider (most flexible but doesn't leverage the AOT query infrastructure).
>
> - **Hint B — Report layout strategy**: Option B1 — use `AutoDesign` for initial development, then manually refine the RDL for production (recommended — fastest path to a working report). Option B2 — design the entire RDL manually from scratch in Report Builder (most control but slowest). Option A3 — use a hybrid approach — AutoDesign for the initial layout, then manually edit the RDL XML to add grouping, subtotals, and formatting.
>
> - **Hint C — Empty-data handling**: Option C1 — add a `NoRowsMessage` property on the Tablix control (recommended — simplest approach). Option C2 — add a separate text box that is visible when the dataset returns no records, using an expression like `=IIF(CountRows("Dataset1") = 0, "No compliance data found for the selected criteria.", "")` (more flexible, allows custom formatting). Option C3 — handle empty data in the `processReport()` method of the data provider by inserting a dummy record into the temp table with a "No data" message (not recommended — pollutes the data layer).
>
> - **Hint D — Subtotals and grouping**: Option D1 — use the SSRS grouping feature in the Report Designer — right-click a column group → "Add Group" → "Parent Group" (recommended — visual and intuitive). Option D2 — handle subtotals in the data provider by pre-calculating group totals in the `get()` method (more control but more complex). Option D3 — use a matrix/tablix with row and column groups for a pivot-style layout (good for analytical reports but overkill for this scenario).
>
> - **Hint E — Email delivery**: Option E1 — configure `PrintJobSettings` in the report controller to send via email (recommended — standard D365 F&O pattern). Option E2 — use a Logic App triggered by the report execution to send the email (more flexible but more complex). Option E3 — use `SmtpMail::send()` from X++ (direct but requires SMTP configuration).

### Expected Approach (Ideal — in detail)

#### Step 1: Create the Data Provider Class

```xpp
class VendComplianceSummaryReportDP extends SrsReportDataProvider
{
    VendTable vendTable;
    FromDate fromDate;
    ToDate toDate;
    ComplianceStatus complianceStatus;

    public VendComplianceReportContract get()
    {
        VendComplianceReportContract contract;
        VendComplianceReportTmp tmpTable;

        contract = this.parmContract();

        // Build the query
        Query query = new Query();
        QueryBuildDataSource qbdVend;
        QueryBuildDataSource qbdInvoice;
        QueryBuildDataSource qbdDeclaration;
        QueryBuildRange qbr;

        // Primary data source: VendTable
        qbdVend = query.addDataSource(tableNum(VendTable));

        // Join to VendInvoiceJour
        qbdInvoice = qbdVend.addDataSource(tableNum(VendInvoiceJour));
        qbdInvoice.joinMode(JoinMode::InnerJoin);
        qbdInvoice.addLink(fieldNum(VendTable, RecId), fieldNum(VendInvoiceJour, VendTable));

        // Join to APCustomsDeclaration
        qbdDeclaration = qbdInvoice.addDataSource(tableNum(APCustomsDeclaration));
        qbdDeclaration.joinMode(JoinMode::InnerJoin);
        qbdDeclaration.addLink(fieldNum(VendInvoiceJour, RecId), fieldNum(APCustomsDeclaration, VendInvoiceLineRecId));

        // Add date range filter
        qbr = qbdDeclaration.addRange(fieldNum(APCustomsDeclaration, DeclDate));
        qbr.value(strfmt('"%1" .. "%2"', contract.parmFromDate(), contract.parmToDate()));

        // Add vendor group filter
        if (contract.parmVendGroup())
        {
            qbr = qbdVend.addRange(fieldNum(VendTable, CustGroup));
            qbr.value(queryValue(contract.parmVendGroup()));
        }

        // Add compliance status filter
        if (contract.parmComplianceStatus())
        {
            qbr = qbdDeclaration.addRange(fieldNum(APCustomsDeclaration, Status));
            qbr.value(queryValue(contract.parmComplianceStatus()));
        }

        this.parmQuery(query);

        // Fetch data into temp table
        while select vendTable
            join invoice
            where invoice.VendTable == vendTable.RecId
            join declaration
            where declaration.VendInvoiceLineRecId == invoice.RecId
        {
            tmpTable.clear();
            tmpTable.AccountNum = vendTable.AccountNum;
            tmpTable.VendorName = vendTable.Name;
            tmpTable.VendGroup = vendTable.CustGroup;
            tmpTable.InvoiceId = invoice.InvoiceId;
            tmpTable.InvoiceDate = invoice.InvoiceDate;
            tmpTable.DeclId = declaration.DeclId;
            tmpTable.DeclDate = declaration.DeclDate;
            tmpTable.Status = declaration.Status;
            tmpTable.insert();
        }

        return contract;
    }

    // Parameter getters/setters
    public VendTable parmVendTable(VendTable _vendTable = vendTable)
    {
        vendTable = _vendTable;
        return vendTable;
    }

    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }
}
```

#### Step 2: Design the Report Layout (Manual RDL)

The report layout should include:

1. **Header section**: Company logo, report title, date range, page number
2. **Tablix with 3-level grouping**:
   - Row group 1: Vendor Group (`CustGroup`)
   - Row group 2: Vendor (`AccountNum`, `Name`)
   - Row group 3: Compliance Status (`Status`)
3. **Columns**: Invoice ID, Invoice Date, Declaration ID, Declaration Date, Status
4. **Subtotals**: Count of declarations and count by status for each vendor group
5. **Grand total row**: Total declarations, total by status
6. **NoRowsMessage**: "No compliance data found for the selected criteria."
7. **Conditional formatting**: Color-code status cells (Green = Validated, Yellow = Pending, Red = Failed)

#### Step 3: Create the Report Controller

```xpp
class VendComplianceSummaryReportController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VendComplianceSummaryReportController controller = new VendComplianceSummaryReportController();
        VendComplianceReportContract contract = new VendComplianceReportContract();

        // Populate contract from args if triggered from a form
        if (_args && _args.record() && _args.record().TableId == tableNum(VendTable))
        {
            contract.parmVendTable(_args.record());
        }

        controller.parmContractType(classStr(VendComplianceReportContract));
        controller.parmServiceType(classStr(VendComplianceSummaryReportDP));
        controller.parmCaption('Vend Compliance Summary Report');
        controller.startOperation();
    }
}
```

#### Step 4: Configure PrintJobSettings for Email Delivery

```xpp
// In the controller or a menu item action:
PrintJobSettings printJobSettings = new PrintJobSettings();
printJobSettings.parmPrintMedium(PrintMedium::Email);
printJobSettings.parmEmailTo('compliance@acme.com');
printJobSettings.parmEmailSubject(strFmt('Compliance Report - %1 to %1', fromDate, toDate));
printJobSettings.parmFileFormat(FileFormat::PDF);
printJobSettings.parmEmailBody('Please find the monthly compliance report attached.');
```

#### Step 5: Create the MenuItemOutput

```xpp
// MenuItemOutput: Object = VendComplianceSummaryReportController, Method = main
// Label: 'Compliance Summary Report'
// Added to the AP Menu or as a standalone workspace tile
```

#### Step 6: Security Configuration

- Create a privilege `VendComplianceReportView` with `AccessLevel::See` on the report
- Add the privilege to the `APComplianceViewer` duty
- Assign the duty to the `ComplianceOfficer` role
- Test with "Run as" to verify only compliance officers can access the report

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeComplianceReporting</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeComplianceReportingEnabled</ConfigurationKey>
</ModelManifest>
```

---

## 17.11 Activity — Electronic Reporting Configuration

> **Activity**: Configure an Electronic Reporting format for VAT declarations in a multi-company D365 F&O environment.
>
> **Requirements:**
> 1. Create a new ER format based on the EU SAF-T XML schema
> 2. Define data sources for `VendTable`, `VendInvoiceJour`, `VendInvoiceLine`, and `TaxTrans`
> 3. Create mappings that transform D365 F&O data into the SAF-T XML structure
> 4. Add a custom extension to the standard format for your company's additional fields
> 5. Configure the ER configuration to run as a batch job for monthly VAT reporting
> 6. Test the format with sample data from two different legal entities
> 7. Validate the output XML against the SAF-T schema
>
> **Activity Hints:**
> - **Hint A — Format design**: Option A1 — start with the standard EU SAF-T format and extend it (recommended — Microsoft provides the base format). Option A2 — create a completely custom format from scratch (only if no standard format exists for your country). Option A3 — use an existing JSON or CSV format and modify the mappings (valid for simpler formats).
> - **Hint B — Data source design**: Option B1 — use `VendInvoiceJour` as the root data source with `VendInvoiceLine` and `TaxTrans` as child sources (recommended — follows the standard invoice structure). Option B2 — use a Data Entity as the data source (simpler but less flexible for ER-specific transformations). Option B3 — use direct table queries in the mapping (most flexible but hardest to maintain).
> - **Hint C — Batch execution**: Option C1 — configure the ER format to run as a batch job using the `ElectronicReportingStaging` table (recommended — standard D365 F&O pattern). Option C2 — trigger ER from a custom menu item with `PrintJobSettings` (valid but less automated). Option C3 — use Power Automate to trigger ER on a schedule (modern but adds complexity).
> - **Hint D — Multi-company validation**: Option D1 — run the ER format for each company separately and validate the output (recommended — ensures data isolation). Option D2 — run a single ER job that processes all companies and validates each output file (faster but more complex). Option D3 — use the `MultiCompany` property on the data source to process all companies in one run (simplest but requires careful validation).

---

## 17.12 Activity — Report Performance Optimization

> **Activity**: A compliance report takes 15 minutes to run and times out with 500,000+ records. Diagnose the issue and apply three different optimization strategies with comparisons.
>
> **Scenario Details:**
> - The report joins `VendTable`, `VendInvoiceJour`, `APCustomsDeclaration`, `VendInvoiceLine`, and `TaxTrans` (5 table joins)
> - The data provider uses `InMemory` temporary tables
> - The report has 4-level grouping (Company → Vendor Group → Vendor → Compliance Status)
> - The report includes subtotals and a grand total row
> - The report is run monthly for all companies
>
> **Three Optimization Proposals:**
>
> **Proposal 1: Switch to TempDB pre-processing**
> - Change the data provider from `SrsReportDataProvider` to `SrsReportDataProviderPreProcessTempDB`
> - Move data retrieval to the `processReport()` method
> - Add indexes on the TempDB table for the grouping columns
> - **Expected improvement**: 15 min → 3 min (80% faster)
> - **Trade-off**: The report takes slightly longer to start (pre-processing phase), but the rendering is fast
>
> **Proposal 2: Optimize the query with exists joins**
> - Replace `join` with `exists join` where full data retrieval isn't needed
> - Add indexes on join columns (`VendTable.RecId`, `VendInvoiceJour.VendTable`)
> - Use `firstonly` where only one record is needed per group
> - **Expected improvement**: 15 min → 6 min (60% faster)
> - **Trade-off**: Some detail data may not be available for all groupings
>
> **Proposal 3: Pre-aggregate data in a batch job**
> - Create a batch job that pre-aggregates the data nightly
> - The report reads from the pre-aggregated table instead of joining 5 tables
> - The batch job updates a `ComplianceSummaryTmp` table with grouped totals
> - **Expected improvement**: 15 min → 30 seconds (99% faster)
> - **Trade-off**: Data is not real-time — it reflects the last nightly run, not the current state
>
> **Activity Hints:**
> - **Hint A — Root cause identification**: Option A1 — InMemory tables for large datasets is the primary bottleneck (most likely — 500K+ records in memory causes timeout). Option A2 — Missing indexes on join columns (possible — check SQL execution plan). Option A3 — The 5-table join is too complex (possible — consider denormalizing the data model). Option A4 — Multiple root causes combined (most realistic).
> - **Hint B — Optimization strategy**: Option B1 — TempDB pre-processing (recommended — highest impact, lowest risk). Option B2 — Query optimization with exists joins (good — complementary to TempDB). Option B3 — Pre-aggregation in a batch job (advanced — best for very large datasets but adds complexity).
> - **Hint C — Validation approach**: Option C1 — Measure before and after with `SysPerformance` (recommended — data-driven). Option C2 — Compare report execution times in the batch job history (valid but less precise). Option C3 — Use SQL Server Profiler to trace the queries (most accurate — shows exactly what SQL is being generated).

---

### Remaining Chapters — Detailed Outlines


# Chapter 18: Batch Processing

> **Complete reference for designing, implementing, and operating batch jobs in Dynamics 365 Finance & Operations.**
> Covers RunBaseBatch vs SysOperation frameworks, batch architecture, parallel processing patterns, retry logic, and a production-ready capstone activity.

---

## Table of Contents

1. [Batch Processing Fundamentals — The Restaurant Analogy](#1-batch-processing-fundamentals--the-restaurant-analogy)
2. [RunBaseBatch vs SysOperation — Framework Comparison](#2-runbasebatch-vs-sysoperation--framework-comparison)
3. [Batch Architecture at Platform Level](#3-batch-architecture-at-platform-level)
4. [RunBaseBatch — The Legacy Pattern](#4-runbasebatch--the-legacy-pattern)
5. [SysOperation Framework — The Modern Pattern](#5-sysoperation-framework--the-modern-pattern)
6. [Side-by-Side Comparison](#6-side-by-side-comparison)
7. [Production Environment Behavior](#7-production-environment-behavior)
8. [Parallel Processing Patterns](#8-parallel-processing-patterns)
9. [Transaction Design for Batch Jobs](#9-transaction-design-for-batch-jobs)
10. [Capstone Activity: Nightly Overdue Customer Blocking](#10-capstone-activity-nightly-overdue-customer-blocking)
11. [Microsoft Learn References](#11-microsoft-learn-references)

---

## 1. Batch Processing Fundamentals — The Restaurant Analogy

Imagine you're at a restaurant.

- **Interactive/synchronous work** is you ordering at the counter and waiting right there while the cook makes your sandwich. You can't do anything else until it's in your hand.
- **Batch processing** is you filling out a to-go order form, dropping it in a box, and walking away. The kitchen picks it up whenever a cook is free, makes it, and you're notified (or you check back later) when it's ready. You didn't have to stand there, and the kitchen can queue up dozens of these orders, prioritize the urgent ones, and retry if something goes wrong with your specific order — without stopping the whole kitchen.

In D365 F&O, the "kitchen" is the **AOS (Application Object Server)**, and the "order form in a box" is a row written to the **`BatchJob`** table, with one or more **`BatchJobTask`** rows underneath it — think of these as the individual line items on the order. A background process on the server, the **batch server**, continuously works through that queue.

So when someone says "make this class batch-able," they mean: *let this piece of code be dropped into that order queue instead of forcing a user to sit and wait for it.*

There are two different **recipes** (frameworks) for writing the code that goes into that order box:

1. **RunBase / RunBaseBatch** — the older recipe, from the AX 2009/2012 era. Still fully supported and still used across a lot of existing D365 F&O standard code.
2. **SysOperation Framework** — the newer, cleaner recipe, and the one used for all new development.

Both recipes end up producing the exact same kind of order, sitting in the exact same queue, worked by the exact same kitchen staff. The difference is entirely in how the recipe is written — not in how the kitchen processes it.

That's the single most useful idea to carry into both real development work and interviews: **the framework choice is a development-time decision; the production execution engine underneath is shared and identical.**

---

## 2. RunBaseBatch vs SysOperation — Framework Comparison

### 2.1 The One-Person Restaurant (RunBase)

`RunBase` is the base framework class providing the skeleton: *dialog → validate → run → pack/unpack*. `RunBaseBatch` extends `RunBase` and implements the `Batchable` interface — this is what actually allows a class to be submitted as a `BatchJob`. Any job that must be able to run in batch inherits from this class.

**Core lifecycle methods:**

| Method | Purpose |
|---|---|
| `dialog()` | Builds the interactive parameter dialog |
| `getFromDialog()` | Reads dialog values back into member variables |
| `pack()` | Serializes the object's state into a `container` for storage on the `BatchJob` record |
| `unpack()` | Deserializes that container back into a fresh object instance when the job actually runs |
| `run()` | The actual business logic |
| `canGoBatch()` | Defaults to `false` — must be overridden to return `true` to allow batch submission |
| `batchInfo()` | Returns the `BatchInfo` object — the API into the batch table for that job |

**The `pack()`/`unpack()` trap:**
Submitting a RunBase class to batch doesn't keep the object alive in memory. It's serialized via `pack()` into a `container` and stored on the `BatchJob` record. When the batch server later picks it up — possibly after an AOS restart, possibly hours later — it builds a **brand-new object** and calls `unpack()` to restore state, then calls `run()`. The safe pattern uses a version macro so future schema changes don't silently break already-queued jobs:

```xpp
class MyBatchClass extends RunBaseBatch
{
    str myParameter = "Default value";

    #define.CurrentVersion(1)
    #localmacro.CurrentList
        myParameter
    #endmacro

    public container pack()
    {
        return [#CurrentVersion, #CurrentList];
    }

    public boolean unpack(container _packedClass)
    {
        Integer version = RunBase::getVersion(_packedClass);
        switch (version)
        {
            case #CurrentVersion:
                [version, #CurrentList] = _packedClass;
                break;
            default:
                return false; // unrecognized version — refuse to run with stale/unknown state
        }
        return true;
    }

    public boolean canGoBatch()
    {
        return true; // must explicitly opt in
    }
}
```

If a new member variable is added to the class but not to both `pack()` and `unpack()` (with the version bumped), that value silently disappears the moment the job actually executes in batch — a bug that won't show up in interactive testing, only in production, hours after the developer has moved on.

**Pros**
- Fast to stand up for a simple, self-contained job — one class, one file
- Battle-tested and still fully supported in current D365 F&O
- Straightforward mental model once internalized: pack → queue → unpack → run

**Cons**
- UI (dialog), state (pack/unpack), and logic (run) are all fused into one class — poor separation of concerns
- `container`-based serialization is untyped and version-fragile; easy to introduce silent data-loss bugs on schema changes
- Hard to unit test in isolation — dialog and business logic aren't cleanly separable
- No natural way to reuse the same parameter definition across a UI dialog, an external service call, and a batch job — each has to be solved separately

---

### 2.2 The Restaurant Becomes a Team (SysOperation)

SysOperation replaces the RunBase framework as the standard way to build interaction dialogs and integrate with the batch server. It follows an **MVC-style pattern** — Model, View (auto-generated), Controller — which cleanly separates the three concerns that RunBase fuses together.

| Piece | Class shape | Responsibility |
|---|---|---|
| **Data Contract** | Plain class, `[DataContractAttribute]` on the class, `[DataMemberAttribute]` on each parm-method | Defines *what* parameters exist — strongly typed, no manual serialization code |
| **Service** | Plain class with one public method taking the contract as its parameter | Defines *what happens* — pure business logic, unaware of whether it's called interactively, asynchronously, or from batch |
| **Controller** | Extends `SysOperationServiceController` | Defines *how* it runs — wires the contract to the service, sets the execution mode, and is the entry point from a menu item |

```xpp
// 1. Data Contract
[DataContractAttribute]
class VSICustBlockContract
{
    CustAccount custAccount;

    [DataMemberAttribute('CustAccount')]
    public CustAccount parmCustAccount(CustAccount _custAccount = custAccount)
    {
        custAccount = _custAccount;
        return custAccount;
    }
}

// 2. Service — pure logic, framework-agnostic, unit-testable
class VSICustBlockService extends SysOperationServiceBase
{
    public void blockCustomer(VSICustBlockContract _contract)
    {
        CustTable custTable = CustTable::find(_contract.parmCustAccount(), true);
        ttsBegin;
        custTable.Blocked = CustVendorBlocked::All;
        custTable.update();
        ttsCommit;
    }
}

// 3. Controller — the entry point a menu item points to
class VSICustBlockController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VSICustBlockController controller = new VSICustBlockController();
        controller.parmClassName(classStr(VSICustBlockService));
        controller.parmMethodName(methodStr(VSICustBlockService, blockCustomer));
        controller.startOperation();
    }
}
```

Because the service method (`blockCustomer`) never touches dialog code or batch plumbing, the exact same logic can be invoked interactively, from batch, or directly from another X++ class in a unit test — with zero duplication.

**The four execution modes (`SysOperationExecutionMode`):**

| Mode | What actually happens |
|---|---|
| `Synchronous` | Runs on the server but **freezes the client** for the duration — the user waits |
| `Asynchronous` | Runs on the server without blocking the client, but requires the service class to have a Service node in the AOT and be deployed as part of a service group — otherwise it silently falls back to `Synchronous` |
| `ReliableAsynchronous` | The default mode when none is set. Spins up two threads — one on the batch server doing the work, one on the client polling for the result. Once complete, it remains visible in **Batch Job History** for traceability |
| `ScheduledBatch` | Submits as a proper, schedulable `BatchJob` — equivalent to checking the batch tab in a RunBase dialog. This is the mode for true unattended, recurring, retryable batch execution |

Worth committing to memory precisely: "SysOperation always runs in batch" is a common misconception. Batch is one of four modes it can run in, selected via `controller.parmExecutionMode(...)`.

**Pros**
- Clean separation of Contract / Service / Controller — the service class is genuinely unit-testable with no framework dependency
- Strongly typed `[DataMember]` contracts instead of untyped containers — far safer across upgrades
- One data contract is reusable across the UI dialog, external service exposure (via `SysEntryPointAttribute`), and batch submission
- Dialog is auto-generated from the contract's attributes — less boilerplate than a hand-built `dialog()` override
- Clean fit with F&O's patterns for scaling out to multiple parallel batch tasks

**Cons**
- More ceremony (three classes instead of one) for genuinely trivial one-off tasks
- Attribute-driven metadata can feel opaque until you understand what it's generating
- Slightly steeper initial learning curve than RunBase's single-class model

---

## 3. Batch Architecture at Platform Level

### 3.1 What "Batch" Means at the Platform Level

A class becomes batch-eligible when its execution is represented as a persisted `BatchJob` (parent) and one or more `BatchJobTask` (child) records, picked up and executed by a **batch server** — an AOS instance flagged as "Is batch server" in **System administration > Setup > System > Server configuration**.

Batch processing is the right tool whenever a piece of logic:
- Shouldn't block a user's session (long-running reports, mass updates, postings)
- Needs to run unattended on a schedule (nightly jobs, recurring imports)
- Needs the reliability of being queued, retried, prioritized, and monitored independently of any one user's client session

Both frameworks below are simply two different ways to get a class into that queue.

### 3.2 BatchJob and BatchJobTask Tables

| Table | Key Fields | Purpose |
|---|---|---|
| **BatchJob** | `BATCHJOBID`, `CAPTION`, `STATUS`, `SERVERID`, `BATCHGROUP` | Parent job record — metadata, scheduling, status |
| **BatchJobTask** | `BATCHJOBID`, `TASKID`, `CLASSNAME`, `METHODNAME`, `STATUS` | Child task — actual execution unit, one per parallel worker |

### 3.3 Batch Status Lifecycle

```
Waiting → Executing → Finished/Error/Canceled
    │
    ├── Hold (0) — manually paused
    ├── Waiting (1) — queued, ready for pickup
    ├── Executing (2) — running on batch server
    ├── Error (3) — failed
    ├── Finished (4) — succeeded
    ├── Ready (5) — ready to schedule
    ├── NotRun (6) — dependencies failed
    ├── Cancelling (7) — user requested cancel
    ├── Canceled (8) — user canceled
    └── Scheduled (9) — future run time
```

### 3.4 Batch Groups and Server Configuration

- **Batch groups** route jobs to specific batch servers
- **Concurrency** controlled by max threads per batch server
- **Priority** (Low/Medium/High) affects queue order — not simple FIFO
- **Recurrence** via `BatchRecurrence` creates next occurrence automatically
- **Security** — server-bound jobs run under submitting user's permissions via `runsImpersonated()`

---

## 4. RunBaseBatch — The Legacy Pattern

### 4.1 Complete RunBaseBatch Template

```xpp
class VendReconciliationBatchJob extends RunBaseBatch
{
    VendTable vendTable;
    FromDate fromDate;
    ToDate toDate;
    int maxRecords;
    boolean sendEmail;

    // Dialog — user input
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        DialogField dfVend;
        DialogField dfFrom;
        DialogField dfTo;
        DialogField dfMax;
        DialogField dfEmail;

        dfVend = dialog.addFieldValue(typeid(VendTable), vendTable, 'Vendor');
        dfVend.lookupButton(true);

        dfFrom = dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dfTo = dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');

        dfMax = dialog.addFieldValue(typeid(int), maxRecords, 'Max Records');
        dfMax.helpText('Maximum number of records to process (0 = unlimited)');

        dfEmail = dialog.addFieldValue(typeid(boolean), sendEmail, 'Send email notification');

        return dialog;
    }

    // getFromDialog — read dialog values back
    public void getFromDialog()
    {
        super();
        // Values automatically bound via addFieldValue
    }

    // Pack — serialize for batch
    public container pack()
    {
        #define.CurrentVersion(1)
        #localmacro.CurrentList
            vendTable, fromDate, toDate, maxRecords, sendEmail
        #endmacro

        return [#CurrentVersion, #CurrentList];
    }

    // Unpack — deserialize from batch
    public boolean unpack(container _packedClass)
    {
        Integer version = RunBase::getVersion(_packedClass);
        #define.CurrentVersion(1)
        #localmacro.CurrentList
            vendTable, fromDate, toDate, maxRecords, sendEmail
        #endmacro

        switch (version)
        {
            case #CurrentVersion:
                [version, #CurrentList] = _packedClass;
                break;
            default:
                return false;
        }
        return true;
    }

    // Run — the actual business logic
    public void run()
    {
        VendTable vendTableLocal;
        
        select vendTableLocal
            where vendTableLocal.AccountNum == vendTable.AccountNum;
        
        if (vendTableLocal)
        {
            // Process logic here
            this.processVendor(vendTableLocal);
        }
    }

    // Must override to allow batch
    public boolean canGoBatch()
    {
        return true;
    }

    private void processVendor(VendTable _vendTable)
    {
        // Business logic
    }
}
```

### 4.2 When to Use RunBaseBatch

- Maintaining existing RunBase codebases
- Simple, self-contained jobs where the ceremony of SysOperation isn't justified
- Quick prototyping before migrating to SysOperation
- Jobs that don't need service reuse or unit test isolation

---

## 5. SysOperation Framework — The Modern Pattern

### 5.1 Complete SysOperation Template

```xpp
// 1. DATA CONTRACT — Strongly typed parameters
[DataContractAttribute]
class CustReconciliationContract
{
    CustAccount custAccount;
    FromDate fromDate;
    ToDate toDate;
    int maxRecords;
    boolean sendEmail;

    [DataMemberAttribute('CustAccount')]
    public CustAccount parmCustAccount(CustAccount _custAccount = custAccount)
    {
        custAccount = _custAccount;
        return custAccount;
    }

    [DataMemberAttribute('FromDate')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

    [DataMemberAttribute('ToDate')]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }

    [DataMemberAttribute('MaxRecords')]
    public int parmMaxRecords(int _maxRecords = maxRecords)
    {
        maxRecords = _maxRecords;
        return maxRecords;
    }

    [DataMemberAttribute('SendEmail')]
    public boolean parmSendEmail(boolean _sendEmail = sendEmail)
    {
        sendEmail = _sendEmail;
        return sendEmail;
    }
}

// 2. SERVICE — Pure business logic, framework-agnostic
class CustReconciliationService extends SysOperationServiceBase
{
    public void processReconciliation(CustReconciliationContract _contract)
    {
        CustTable custTable;
        int processedCount = 0;

        while select custTable
            where custTable.AccountNum == _contract.parmCustAccount()
        {
            // Process each customer
            this.processCustomer(custTable, _contract);
            processedCount++;

            // Progress reporting (optional)
            if (this.parmProgress())
            {
                this.parmProgress().setProgress(processedCount, 100);
            }
        }

        info(strFmt('Processed %1 customers', processedCount));
    }

    private void processCustomer(CustTable _custTable, CustReconciliationContract _contract)
    {
        // Business logic here
    }
}

// 3. CONTROLLER — Entry point and execution mode
class CustReconciliationController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        CustReconciliationController controller = new CustReconciliationController();
        controller.parmClassName(classStr(CustReconciliationService));
        controller.parmMethodName(methodStr(CustReconciliationService, processReconciliation));
        controller.parmExecutionMode(SysOperationExecutionMode::ScheduledBatch); // For true batch
        controller.startOperation();
    }
}
```

### 5.2 Execution Mode Selection

```xpp
// In controller or when calling programmatically:
controller.parmExecutionMode(SysOperationExecutionMode::ScheduledBatch);  // True batch — queued, retryable, schedulable
controller.parmExecutionMode(SysOperationExecutionMode::ReliableAsynchronous);  // Default — background with polling
controller.parmExecutionMode(SysOperationExecutionMode::Asynchronous);  // Fire-and-forget (needs service group)
controller.parmExecutionMode(SysOperationExecutionMode::Synchronous);  // Blocks client — interactive
```

### 5.3 UI Builder (Optional Customization)

For custom dialogs beyond auto-generated fields:

```xpp
class CustReconciliationUIBuilder extends SysOperationAutomaticUIBuilder
{
    public void postBuild()
    {
        super();
        
        // Customize dialog: hide fields, add groups, set lookups
        DialogField dfCustAccount = this.bindInfo().getDialogField(
            this.dataContractObject(), methodStr(CustReconciliationContract, parmCustAccount));
        dfCustAccount.lookupButton(true);
        dfCustAccount.helpText('Select the customer to reconcile');
    }
}
```

Register in controller:
```xpp
class CustReconciliationController extends SysOperationServiceController
{
    public void new()
    {
        super();
        this.parmUIBuilderClassName(classStr(CustReconciliationUIBuilder));
    }
}
```

---

## 6. Side-by-Side Comparison

| Aspect | RunBase / RunBaseBatch | SysOperation Framework |
|---|---|---|
| Era | AX 2009/2012 | AX 2012 R2+ → current standard in D365 F&O |
| Structure | One monolithic class | Three classes: Contract, Service, Controller |
| Parameter storage | `pack()`/`unpack()` into untyped `container` | Strongly typed `[DataMember]` attributes on contract |
| Testability | Poor — logic entangled with dialog code | Strong — service logic is pure and isolatable |
| Reuse across UI / batch / external service | Manual, duplicated per use case | Native — one contract, many entry points |
| Getting into batch queue | Override `canGoBatch()` to `true`; user checks Batch tab | Controller sets `parmExecutionMode(ScheduledBatch)` |
| Parallel/multi-threaded execution | Manual — task-splitting logic built directly against `BatchHeader`/`BatchJobTask` | Fits cleanly with F&O's standard parallel-task-splitting patterns |
| Current guidance | Legacy, still supported | **Recommended for all new development** |
| Where it still shows up | Older standard modules (parts of AR/AP, older Trade code) | Most standard batch/service code added since AX 2012 R2 onward |

---

## 7. Production Environment Behavior

Once a job becomes a `BatchJob` row, both frameworks are executed by the identical batch engine. Everything below applies equally regardless of which framework produced the job.

- **Batch groups** — Batch servers are configured to service specific batch groups, so heavy jobs (e.g. a large costing or MRP run) can be routed to a dedicated server and kept from starving lighter, time-sensitive batch work on a shared one.
- **Threads/concurrency** — Each batch server has a configured maximum number of concurrent threads it can process.
- **Priority** — Jobs carry a priority (Low/Medium/High); the engine picks the highest-priority *ready* task first, not simple FIFO.
- **Recurrence** — `BatchRecurrence` automatically creates the next occurrence once a recurring job finishes, identically for both frameworks.
- **Retry/failure** — An unhandled exception marks the task **Error**; retry behavior is configurable. Neither framework auto-manages transaction boundaries — `ttsBegin`/`ttsCommit` discipline is entirely on the developer, same as any other X++ code. A RunBase class with incomplete `pack()` state is a uniquely legacy-framework risk here; a typed SysOperation contract makes that specific failure mode much harder to introduce.
- **Security** — Server-bound batch jobs (via `runsImpersonated()` returning `true`) run under the submitting user's permissions and have restricted interaction with the client, making them more secure than non-server-bound execution.
- **Monitoring** — Both surface identically at **System administration > Inquiries > Batch jobs**, showing status (Waiting/Executing/Ended/Error/Canceled), full history, and the ability to requeue. From the Batch Jobs form alone, there's no way to tell whether the underlying class is RunBase or SysOperation — that distinction is invisible at runtime.

---

## 8. Parallel Processing Patterns

When your batch job becomes large, you start asking questions such as:
> Who owns this piece of work? Has somebody already processed it? What happens if processing fails? Can we retry it? How do we know what succeeded? What happens if the batch server crashes? How many workers should run simultaneously? Are multiple workers locking the same records? Should everything be inside one transaction?

These are not really RunBase-vs-SysOperation questions anymore. They are **batch architecture questions**.

### 8.1 Three Approaches to Task Splitting

| Approach | Best for | Fit for high-volume scenario |
|---|---|---|
| **Individual task modeling** | A handful of items, or items with real dependencies | Works fine for a dozen; at "thousands," batch engine's task-tracking overhead becomes the bottleneck |
| **Batch bundling** | Evenly distributed, uniform workload, no staging table needed | Reasonable for constant-time work — lacks built-in progress tracking |
| **Top picking pattern** | Uneven workload at real volume, bounded parallel tasks with shared queue | **The right fit** — same mechanism F&O uses for high-volume journal batch posting |

### 8.2 Top Picking Pattern — The Production Standard

**Mechanism:** A bounded number of `BatchJobTask`s (say, 5 or 10 — not one per customer) are scheduled. Each task runs the same worker loop: inside a short transaction, claim the next `Ready` row from the staging table (mark it `InProgress`, tag it with the task's own identity), commit quickly, then do the actual work outside that claiming transaction, and finally mark the row `Done` (or `Error`).

```xpp
// Staging/queue table: VSICustBlockQueue
// Fields: RecId, CustAccount, Status (Ready/InProgress/Done/Error), BatchTaskId, ErrorText

// --- Producer: populates the queue from the contract's criteria ---
class VSICustBlockSelectorService extends SysOperationServiceBase
{
    public void selectOverdueCustomers(VSICustBlockSelectionContract _contract)
    {
        CustTable custTable;
        VSICustBlockQueue queueRecord;

        while select custTable
            where custTable.overdueDate() <= _contract.parmOverdueSinceDate() // conceptual filter
        {
            queueRecord.clear();
            queueRecord.CustAccount = custTable.AccountNum;
            queueRecord.Status      = VSICustBlockQueueStatus::Ready;
            queueRecord.insert();
        }
    }
}

// --- Worker: top-picking loop, run by each parallel batch task ---
class VSICustBlockWorkerService extends SysOperationServiceBase
{
    public void processQueue()
    {
        VSICustBlockQueue queueRecord;
        boolean            hasWork = true;

        while (hasWork)
        {
            hasWork = false;
            ttsBegin;
            // Claim the next ready row — short, fast transaction
            select firstOnly forUpdate queueRecord
                where queueRecord.Status == VSICustBlockQueueStatus::Ready;

            if (queueRecord.RecId)
            {
                queueRecord.Status      = VSICustBlockQueueStatus::InProgress;
                queueRecord.BatchTaskId = this.getCurrentBatchTaskRecId(); // conceptual
                queueRecord.update();
                hasWork = true;
            }
            ttsCommit;

            if (hasWork)
            {
                this.blockOneCustomer(queueRecord.CustAccount, queueRecord);
            }
        }
    }

    private void blockOneCustomer(CustAccount _custAccount, VSICustBlockQueue _queueRecord)
    {
        CustTable custTable;
        try
        {
            ttsBegin;
            custTable = CustTable::find(_custAccount, true);
            custTable.Blocked = CustVendorBlocked::All;
            custTable.update();

            _queueRecord.selectForUpdate(true);
            _queueRecord.Status = VSICustBlockQueueStatus::Done;
            _queueRecord.update();
            ttsCommit;
        }
        catch (Exception::Error)
        {
            ttsBegin;
            _queueRecord.selectForUpdate(true);
            _queueRecord.Status    = VSICustBlockQueueStatus::Error;
            _queueRecord.ErrorText = "Block failed"; // capture real infolog text in practice
            _queueRecord.update();
            ttsCommit;
        }
    }
}
```

---

## 9. Transaction Design for Batch Jobs

### 9.1 Per-Item Transactions — Never One Big Transaction

**Per customer — never one transaction for the whole run.** Two reasons, both load-bearing:

1. **Blast radius of failure.** If customer #4,000 of 10,000 throws (locked record, validation failure, whatever), a single outer transaction rolls back the entire run, including the 3,999 customers already processed successfully. There'd be zero visibility into which ones actually succeeded, and re-running would mean redoing all 4,000 from scratch.

2. **Retry safety requires idempotency, and idempotency requires per-item commit.** With the queue-table design above, a retried or requeued batch task simply resumes: it queries for `Ready` (and optionally `Error`, for auto-retry) rows and picks up exactly where the last run left off. `Done` rows are never touched again. This only works because each customer's block, and its queue-status update, are committed together, atomically, the moment that customer finishes — not deferred until the whole batch completes. The queue table's per-row status *is* the retry-safety mechanism, and it only functions correctly because commits happen at the per-item boundary, not the per-job boundary.

### 9.2 Deadlock Retry Pattern

```xpp
int retryCount = 0;
boolean success = false;

while (!success && retryCount < 3)
{
    ttsBegin;
    try
    {
        // ... your database operations ...
        ttsCommit;
        success = true;
    }
    catch (Exception::Deadlock)
    {
        ttsAbort;
        retryCount++;
        info(strFmt("Deadlock detected — retry %1 of 3", retryCount));
        sleep(100); // Brief pause
    }
    catch (Exception::Error)
    {
        ttsAbort;
        error("A non-deadlock error occurred.");
        break;
    }
}
```

---

## 10. Capstone Activity: Nightly Overdue Customer Blocking

> **Scenario:** Build a job that blocks a *list* of overdue customers (not just one) for invoicing. It must be schedulable nightly, safely retryable, and — since the list can run into the thousands — ideally process customers in parallel chunks in production.

### 10.1 Requirements

1. **Framework**: SysOperation (modern pattern)
2. **Parameters**: Overdue date threshold, optional customer group filter
3. **Execution**: `ScheduledBatch` mode (nightly at 2 AM)
4. **Parallelism**: Top-picking pattern with 5-10 workers
5. **Transactions**: Per-customer commits (not one big transaction)
6. **Retry Safety**: Queue table with status tracking (Ready/InProgress/Done/Error)
7. **Monitoring**: Batch job history visibility, email/Logic App notification on completion
8. **Idempotency**: Re-runnable without double-processing

### 10.2 Complete Implementation

**1. Data Contract:**
```xpp
[DataContractAttribute]
class CustOverdueBlockContract
{
    Date overdueSinceDate;
    CustGroup custGroup;
    int workerCount;

    [DataMemberAttribute('OverdueSinceDate')]
    public Date parmOverdueSinceDate(Date _overdueSinceDate = overdueSinceDate)
    {
        overdueSinceDate = _overdueSinceDate;
        return overdueSinceDate;
    }

    [DataMemberAttribute('CustGroup')]
    public CustGroup parmCustGroup(CustGroup _custGroup = custGroup)
    {
        custGroup = _custGroup;
        return custGroup;
    }

    [DataMemberAttribute('WorkerCount')]
    public int parmWorkerCount(int _workerCount = workerCount)
    {
        workerCount = _workerCount;
        return workerCount;
    }
}
```

**2. Staging/Queue Table:**
```xpp
table 50103 CustOverdueBlockQueue
{
    Storage = TempDB;
    DataClassification = CustomerContent;

    fields
    {
        field(RecId; int64) { }
        field(CustAccount; CustAccount) { }
        field(Status; Enum CustOverdueBlockQueueStatus) { }
        field(BatchTaskId; int64) { }
        field(ErrorText; Text[250]) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_Status; Status) { }
    }
}

enum CustOverdueBlockQueueStatus
{
    Ready = 0,
    InProgress = 1,
    Done = 2,
    Error = 3
}
```

**3. Selector Service (Producer):**
```xpp
class CustOverdueBlockSelectorService extends SysOperationServiceBase
{
    public void populateQueue(CustOverdueBlockContract _contract)
    {
        CustTable custTable;
        CustOverdueBlockQueue queueRecord;
        
        CustOverdueBlockQueue::delete_all(); // Clear previous run
        
        while select custTable
            where custTable.overdueDate() <= _contract.parmOverdueSinceDate()
               && (_contract.parmCustGroup() == '' || custTable.CustGroup == _contract.parmCustGroup())
        {
            queueRecord.clear();
            queueRecord.CustAccount = custTable.AccountNum;
            queueRecord.Status      = CustOverdueBlockQueueStatus::Ready;
            queueRecord.insert();
        }
        
        info(strFmt('Queue populated with %1 customers', 
            select count(RecId) from CustOverdueBlockQueue where Status == CustOverdueBlockQueueStatus::Ready));
    }
}
```

**4. Worker Service (Consumer — Top Picking):**
```xpp
class CustOverdueBlockWorkerService extends SysOperationServiceBase
{
    public void processQueue()
    {
        CustOverdueBlockQueue queueRecord;
        boolean hasWork = true;
        int processedCount = 0;
        int errorCount = 0;

        while (hasWork)
        {
            hasWork = false;
            ttsBegin;
            
            // Claim next ready row — fast, short transaction
            select firstOnly forUpdate queueRecord
                where queueRecord.Status == CustOverdueBlockQueueStatus::Ready;

            if (queueRecord.RecId)
            {
                queueRecord.Status = CustOverdueBlockQueueStatus::InProgress;
                queueRecord.update();
                hasWork = true;
            }
            ttsCommit;

            if (hasWork)
            {
                try
                {
                    this.blockCustomer(queueRecord.CustAccount);
                    processedCount++;
                    
                    // Mark done
                    ttsBegin;
                    queueRecord.selectForUpdate(true);
                    queueRecord.Status = CustOverdueBlockQueueStatus::Done;
                    queueRecord.update();
                    ttsCommit;
                }
                catch (Exception::Error)
                {
                    errorCount++;
                    ttsBegin;
                    queueRecord.selectForUpdate(true);
                    queueRecord.Status = CustOverdueBlockQueueStatus::Error;
                    queueRecord.ErrorText = "Blocking failed";
                    queueRecord.update();
                    ttsCommit;
                }
            }
        }
        
        info(strFmt('Worker completed: %1 processed, %2 errors', processedCount, errorCount));
    }

    private void blockCustomer(CustAccount _custAccount)
    {
        CustTable custTable = CustTable::find(_custAccount, true);
        if (!custTable)
        {
            throw error(strFmt('Customer %1 not found', _custAccount));
        }
        
        custTable.Blocked = CustVendorBlocked::All;
        custTable.update();
    }
}
```

**5. Controller:**
```xpp
class CustOverdueBlockController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        CustOverdueBlockController controller = new CustOverdueBlockController();
        controller.parmClassName(classStr(CustOverdueBlockWorkerService));
        controller.parmMethodName(methodStr(CustOverdueBlockWorkerService, processQueue));
        controller.parmExecutionMode(SysOperationExecutionMode::ScheduledBatch);
        controller.startOperation();
    }
}
```

**6. Recurrence Setup (in LCS / Batch Job form):**
- Recurrence: Daily at 2:00 AM
- Batch Group: `BATCHGROUP2` (high priority)
- Max Threads: 5-10 (configured on batch server)

---

## 11. Microsoft Learn References

### Batch Processing
- **Batch Processing Overview**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-processing-overview
- **RunBase Framework**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/runbase-framework
- **SysOperation Framework**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-framework
- **Batch OData API**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-odata-api

### SysOperation
- **SysOperation Service Pattern**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-service-pattern
- **Data Contract Attributes**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-data-contract
- **UI Builder**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-ui-builder
- **Execution Modes**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-execution-modes

### Batch Architecture
- **Batch Groups**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-groups
- **Batch Server Configuration**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-server-configuration
- **Batch Retry Logic**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-retry-logic

---

*End of Chapter 18 — Batch Processing*
    public RunOn runOn()
    {
        return RunOn::Batch;
    }

    // Business logic
    public void run()
    {
        VendTable vendTableLocal;
        int processedCount = 0;
        int failedCount = 0;

        while select vendTableLocal
            where vendTableLocal.AccountNum == vendTable.AccountNum
        {
            // Check cancellation
            if (this.checkCancel())
            {
                info('Job was cancelled by the user.');
                break;
            }

            // Check max records limit
            if (maxRecords > 0 && processedCount >= maxRecords)
            {
                info(strFmt('Reached max records limit of %1.', maxRecords));
                break;
            }

            try
            {
                ttsBegin;
                this.reconcileVendor(vendTableLocal);
                ttsCommit;
                processedCount++;
            }
            catch (Exception::Error)
            {
                ttsAbort;
                failedCount++;
                warning(strFmt('Failed to reconcile vendor %1.', vendTableLocal.AccountNum));
            }

            // Update progress
            this.lastValue(strFmt('Processed %1 records...', processedCount));
        }

        info(strFmt('Reconciliation complete: %1 succeeded, %2 failed.', processedCount, failedCount));

        // Send email notification if requested
        if (sendEmail && failedCount == 0)
        {
            this.sendNotification(processedCount);
        }
    }

    private void reconcileVendor(VendTable _vendTable)
    {
        // Reconciliation logic here
        info(strFmt('Reconciling vendor %1...', _vendTable.AccountNum));
    }

    private void sendNotification(int _processedCount)
    {
        // Email notification logic
        // ...
    }

    // Batch metadata
    public BatchHeader batchInfo()
    {
        BatchHeader batchHeader = super::batchInfo();
        batchHeader.parmDescription('Vendor Reconciliation Batch Job');
        batchHeader.parmBatchGroup('BATCHGROUP1');
        batchHeader.parmExecutionStyle(BatchExecutionStyle::OnDemand);
        return batchHeader;
    }

    // Static entry point
    public static void main(Args _args)
    {
        VendReconciliationBatchJob job = new VendReconciliationBatchJob();
        if (_args && _args.record())
        {
            job.parmVendTable(_args.record());
        }
        if (job.prompt())
        {
            job.run();
        }
    }
}
```

### `runOn()` — Execution Target

| Value | Description | Use When |
|---|---|---|
| `RunOn::Client` | Runs on the user's desktop | Lightweight operations that need UI interaction |
| `RunOn::Server` | Runs on the AOS server | Operations that need server-side data access but don't need batch queuing |
| `RunOn::Batch` | Runs on the batch server | Long-running operations that should be queued and run asynchronously |

---

## 18.4 `SysOperationServiceController` — Service-Based Batch Pattern

As covered in Chapter 6, `SysOperationServiceController` provides a modern, contract-driven approach to batch operations. It is particularly useful when:

- The operation needs to be called from external systems (OData/REST)
- The operation needs contract-based parameter validation
- The operation should be versioned independently of the implementation

### SysOperationServiceController for Batch

```xpp
class VendReconciliationController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        VendReconciliationController controller = new VendReconciliationController();
        VendReconciliationContract contract = new VendReconciliationContract();

        controller.parmContractType(classStr(VendReconciliationContract));
        controller.parmServiceType(classStr(VendReconciliationService));
        controller.parmCaption('Vendor Reconciliation');
        controller.startOperation();
    }
}
```

### When to Use SysOperationServiceController vs RunBaseBatch

| Feature | RunBaseBatch | SysOperationServiceController |
|---|---|---|
| Dialog-based input | ✅ Yes | ❌ No (contract-based) |
| Batch queuing | ✅ Yes | ✅ Yes |
| OData/REST exposure | ❌ No | ✅ Yes |
| Contract validation | ❌ No | ✅ Yes |
| Simplicity | ✅ Simpler | ❌ More complex |
| Modern pattern | ⚠️ Legacy | ✅ Recommended for new development |

---

## 18.5 Progress Reporting

Progress reporting keeps users informed about the status of long-running batch operations.

### `lastValue()` — Progress String

The `lastValue()` method returns a string that describes the current progress of the job. This string is displayed in the batch job list in LCS.

```xpp
public int lastValue()
{
    // Return the number of records processed so far
    return this.processedCount;
}
```

### `lastValueCounter` — Built-in Counter

`RunBaseBatch` provides a built-in `lastValueCounter` that automatically increments. You can use it for simple progress reporting:

```xpp
// In the run() method:
this.lastValueCounter++;
```

### Percent Complete Reporting

For more detailed progress reporting, calculate the percentage complete:

```xpp
public int lastValue()
{
    int totalRecords = this.getTotalRecordCount();
    int processedRecords = this.getProcessedCount();

    if (totalRecords > 0)
    {
        return (processedRecords * 100) / totalRecords;
    }
    return 0;
}
```

### Status Messages

Use `info()`, `warning()`, and `error()` in the `run()` method to provide real-time status updates:

```xpp
public void run()
{
    info('Starting vendor reconciliation...');

    while select vendTable
    {
        // Process each vendor
        if (this.checkCancel())
        {
            warning('Job cancelled by user.');
            break;
        }

        try
        {
            this.reconcileVendor(vendTable);
            info(strFmt('Reconciled vendor %1 successfully.', vendTable.AccountNum));
        }
        catch (Exception::Error)
        {
            error(strFmt('Failed to reconcile vendor %1.', vendTable.AccountNum));
        }
    }

    info('Vendor reconciliation complete.');
}
```

---

## 18.6 Cancellation — `checkCancel()` in Batch Loops

The `checkCancel()` method checks whether the user has requested cancellation of the batch job. It should be called inside long-running loops to allow graceful cancellation.

### How `checkCancel()` Works

```xpp
public void run()
{
    while select vendTable
    {
        // Check if the user has cancelled the job
        if (this.checkCancel())
        {
            info('Batch job was cancelled by the user.');
            break;
        }

        // Process the record
        this.processVendor(vendTable);
    }
}
```

### Cancellation Behavior

| Behavior | Description |
|---|---|
| `checkCancel()` returns `true` | The loop breaks and the job finishes gracefully |
| `checkCancel()` returns `false` | The loop continues processing |
| After cancellation | The job status is set to `Completed` (not `Failed`) — cancellation is a normal exit |

### Best Practices for Cancellation

1. **Call `checkCancel()` inside every `while select` loop** — long-running loops must check for cancellation
2. **Call `checkCancel()` at reasonable intervals** — don't call it on every record if processing is very fast (performance impact)
3. **Handle cancellation gracefully** — clean up any partial work, log the cancellation, and exit the loop
4. **Don't throw exceptions on cancellation** — cancellation is a normal exit path, not an error

### Cancellation with Transaction Control

```xpp
public void run()
{
    VendTable vendTable;

    while select vendTable
    {
        if (this.checkCancel())
        {
            info('Cancellation requested. Finishing current transaction...');
            break;
        }

        ttsBegin;
        try
        {
            this.processVendor(vendTable);
            ttsCommit;
        }
        catch (Exception::Error)
        {
            ttsAbort;
            warning(strFmt('Failed to process vendor %1.', vendTable.AccountNum));
        }
    }
}
```

**Important:** When `checkCancel()` returns `true` inside a `ttsBegin/ttsCommit` block, the current transaction is still committed. The cancellation check happens after the transaction completes. This ensures data consistency — partial records are not left in an inconsistent state.

---

## 18.7 Retry Logic — `Global::retry()` and Custom Retry Counters

Retry logic allows a batch job to recover from transient failures (e.g., network timeouts, deadlocks, temporary service unavailability).

### `Global::retry()` — Built-in Retry

`Global::retry()` is a simple retry mechanism that retries the current operation a specified number of times with a delay between retries.

```xpp
public void processVendor(VendTable _vendTable)
{
    int retryCount = 0;
    int maxRetries = 3;
    boolean success = false;

    while (!success && retryCount < maxRetries)
    {
        try
        {
            // Attempt the operation
            this.callExternalService(_vendTable);
            success = true;
        }
        catch (Exception::Error)
        {
            retryCount++;
            if (retryCount < maxRetries)
            {
                // Wait before retrying (exponential backoff)
                Global::retry(retryCount * 5);  // Wait 5, 10, 15 seconds
                warning(strFmt('Retry %1 of %2 for vendor %3...',
                    retryCount, maxRetries, _vendTable.AccountNum));
            }
            else
            {
                error(strFmt('Failed to process vendor %1 after %2 retries.',
                    _vendTable.AccountNum, maxRetries));
            }
        }
    }
}
```

### Custom Retry Counters

For more control over retry behavior, implement custom retry logic:

```xpp
class VendReconciliationRetryHandler
{
    static int maxRetries = 3;
    static int retryDelaySeconds = 5;

    public static boolean executeWithRetry(Container _operation)
    {
        int attempt = 0;
        boolean success = false;

        while (!success && attempt < maxRetries)
        {
            attempt++;
            try
            {
                // Execute the operation
                _operation.call();
                success = true;
            }
            catch (Exception::Error)
            {
                if (attempt < maxRetries)
                {
                    // Exponential backoff: 5s, 10s, 20s
                    int delay = retryDelaySeconds * (2 ^ (attempt - 1));
                    Global::retry(delay);
                    info(strFmt('Attempt %1 failed. Retrying in %2 seconds...', attempt, delay));
                }
                else
                {
                    error(strFmt('Operation failed after %1 attempts.', maxRetries));
                }
            }
        }

        return success;
    }
}
```

### When to Retry vs. When to Fail

| Error Type | Action |
|---|---|
| **Transient errors** (network timeout, deadlock, temporary service unavailability) | Retry |
| **Permanent errors** (invalid data, missing records, permission denied) | Fail immediately — retry won't help |
| **Resource errors** (disk full, memory low) | Retry with backoff, but also alert the operator |
| **Logic errors** (bug in code, incorrect configuration) | Fail immediately — fix the code |

### Retry Best Practices

1. **Use exponential backoff** — wait longer between each retry attempt (5s, 10s, 20s, 40s...)
2. **Limit retry attempts** — 3-5 retries is typically sufficient; more retries waste resources
3. **Log each retry attempt** — include the attempt number, error message, and wait time
4. **Distinguish transient from permanent errors** — don't retry permanent errors
5. **Alert on final failure** — if all retries fail, send a notification to the operations team
6. **Make retry counts configurable** — use a parameter or configuration key so operators can adjust without code changes

---

## 18.8 Activity — Batch Reconciliation Job for 100K+ Records

> **Activity**: Create a batch reconciliation job for 100K+ vendor records with the following requirements:
> 1. The job must process vendors in batches of 1,000 records at a time to avoid memory issues
> 2. The job must display progress (percent complete and records processed)
> 3. The job must support cancellation — the user should be able to stop the job at any time
> 4. The job must implement retry logic with exponential backoff for transient failures
> 5. The job must send an email notification upon completion (success or failure summary)
> 6. The job must log all errors to a custom error log table for later review
> 7. The job must support a "dry run" mode that simulates processing without writing to the database
> 8. The job must handle the case where the batch is cancelled mid-transaction (rollback the current batch, not the entire job)
> 9. The job must be configurable via a dialog with parameters: vendor group, date range, batch size, max retries, dry run mode
> 10. The job must be scheduled to run nightly via the batch framework
>
> **Activity Hints** (Multiple Valid Architectural Choices):
>
> - **Hint A — Retry/cancellation/notification patterns**: Option A1 — use `Global::retry()` with exponential backoff, `checkCancel()` inside the loop, and `PrintJobSettings` for email notification (recommended — follows Microsoft patterns). Option A2 — implement custom retry logic with a retry counter table (more control but more complex). Option A3 — use `RunBaseBatch` with built-in retry support (simplest but least configurable).
>
> - **Hint B — Batch processing strategy**: Option B1 — process in chunks of 1,000 records using `while select` with `next` and a counter (recommended — memory-efficient, allows cancellation between batches). Option B2 — use `insert_recordset`/`update_recordset` for set-based processing (fastest but less granular control over cancellation and error handling). Option B3 — use a cursor-based approach (not recommended — cursors are slow and don't scale).
>
> - **Hint C — Dry run mode**: Option C1 — use a boolean flag that skips `insert()`/`update()` calls and only logs what would have happened (recommended — simple and effective). Option C2 — use a separate staging table that captures all changes without writing to the target tables (more detailed but more complex). Option C3 — run the job in a test company (valid but requires a separate environment).
>
> - **Hint D — Error logging**: Option D1 — write errors to a custom `BatchErrorLog` table with fields for batch ID, vendor, error message, timestamp (recommended — persistent, queryable). Option D2 — use the Infolog and rely on the batch job history (simpler but less structured). Option D3 — write errors to a file (valid for external systems but not queryable from D365 F&O).
>
> - **Hint E — Scheduling**: Option E1 — use the LCS release pipeline to schedule the batch job (recommended — integrates with the standard deployment process). Option E2 — use the `BatchHeader` to schedule the job for a specific time (more direct control). Option C3 — use Azure DevOps cron trigger to submit the batch job (valid but requires CI/CD pipeline setup).

### Expected Approach (Ideal — in detail)

#### Batch Error Log Table

```xpp
table 50102 BatchErrorLog
{
    DataClassification = CustomerContent;

    fields
    {
        field(1; RecId; int64) { }
        field(2; BatchId; Guid) { }
        field(3; VendorAccount; AccountNum) { }
        field(4; ErrorMessage; Text[250]) { }
        field(5; ErrorDateTime; DateTime) { }
        field(6; RetryCount; int) { }
        field(7; Resolved; boolean) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_BatchId; BatchId) { }
    }
}
```

#### Complete Batch Job Implementation

```xpp
class VendReconciliationBatchJob extends RunBaseBatch
{
    VendGroup vendGroup;
    FromDate fromDate;
    ToDate toDate;
    int batchSize;
    int maxRetries;
    boolean dryRun;
    boolean sendEmail;

    // Progress tracking
    int totalProcessed = 0;
    int totalFailed = 0;
    int totalSkipped = 0;
    Guid batchId;

    // Dialog
    public Object dialog()
    {
        Dialog dialog = super::dialog();
        dialog.addFieldValue(typeid(VendGroup), vendGroup, 'Vendor Group');
        dialog.addFieldValue(typeid(FromDate), fromDate, 'From Date');
        dialog.addFieldValue(typeid(ToDate), toDate, 'To Date');
        dialog.addFieldValue(typeid(int), batchSize, 'Batch Size');
        dialog.addFieldValue(typeid(int), maxRetries, 'Max Retries');
        dialog.addFieldValue(typeid(boolean), dryRun, 'Dry Run Mode');
        dialog.addFieldValue(typeid(boolean), sendEmail, 'Send Email Notification');
        return dialog;
    }

    // Pack
    public container pack()
    {
        return [vendGroup, fromDate, toDate, batchSize, maxRetries, dryRun, sendEmail];
    }

    // Unpack
    public boolean unpack(container _packedClass)
    {
        vendGroup = _packedClass.packGet(1);
        fromDate = _packedClass.packGet(2);
        toDate = _packedClass.packGet(3);
        batchSize = _packedClass.packGet(4);
        maxRetries = _packedClass.packGet(5);
        dryRun = _packedClass.packGet(6);
        sendEmail = _packedClass.packGet(7);
        return true;
    }

    // Run on batch tier
    public RunOn runOn()
    {
        return RunOn::Batch;
    }

    // Business logic
    public void run()
    {
        VendTable vendTable;
        int batchCount = 0;
        int currentBatchSize = 0;

        batchId = Guid::newGuid();
        info(strFmt('Starting vendor reconciliation batch job. Batch ID: %1', batchId));

        while select vendTable
            where vendTable.CustGroup == vendGroup
        {
            // Check cancellation
            if (this.checkCancel())
            {
                info('Job was cancelled by the user.');
                break;
            }

            // Check batch size limit
            if (batchSize > 0 && currentBatchSize >= batchSize)
            {
                info(strFmt('Batch size limit of %1 reached. Pausing...', batchSize));
                // In a real implementation, you would commit the current batch
                // and resume in the next batch execution
                break;
            }

            // Process with retry logic
            if (this.processVendorWithRetry(vendTable))
            {
                totalProcessed++;
            }
            else
            {
                totalFailed++;
            }

            currentBatchSize++;
            totalProcessed++;

            // Update progress
            this.lastValue(strFmt('Processed %1 records, %2 failed...',
                totalProcessed, totalFailed));
        }

        // Summary
        info(strFmt('Reconciliation complete: %1 processed, %2 failed, %3 skipped.',
            totalProcessed, totalFailed, totalSkipped));

        // Send email notification
        if (sendEmail)
        {
            this.sendNotification(totalProcessed, totalFailed);
        }
    }

    private boolean processVendorWithRetry(VendTable _vendTable)
    {
        int retryCount = 0;
        boolean success = false;

        while (!success && retryCount <= maxRetries)
        {
            try
            {
                if (!dryRun)
                {
                    ttsBegin;
                    this.reconcileVendor(_vendTable);
                    ttsCommit;
                }
                success = true;
            }
            catch (Exception::Error)
            {
                retryCount++;
                if (retryCount <= maxRetries)
                {
                    int delay = 5 * (2 ^ (retryCount - 1));  // Exponential backoff
                    Global::retry(delay);
                    warning(strFmt('Retry %1 of %2 for vendor %3...',
                        retryCount, maxRetries, _vendTable.AccountNum));
                }
                else
                {
                    // Log the error
                    this.logError(_vendTable, 'Max retries exceeded');
                    error(strFmt('Failed to reconcile vendor %1 after %2 retries.',
                        _vendTable.AccountNum, maxRetries));
                }
            }
        }

        return success;
    }

    private void reconcileVendor(VendTable _vendTable)
    {
        // Actual reconciliation logic
        info(strFmt('Reconciling vendor %1...', _vendTable.AccountNum));
    }

    private void logError(VendTable _vendTable, str _error)
    {
        BatchErrorLog errorLog;
        errorLog.initValue();
        errorLog.BatchId = batchId;
        errorLog.VendorAccount = _vendTable.AccountNum;
        errorLog.ErrorMessage = _error;
        errorLog.ErrorDateTime = datetimeUtil::getSystemDateTime();
        errorLog.RetryCount = maxRetries;
        errorLog.insert();
    }

    private void sendNotification(int _processed, int _failed)
    {
        PrintJobSettings printJobSettings = new PrintJobSettings();
        printJobSettings.parmPrintMedium(PrintMedium::Email);
        printJobSettings.parmEmailTo('compliance@acme.com');
        printJobSettings.parmEmailSubject(strFmt('Vendor Reconciliation: %1 processed, %2 failed',
            _processed, _failed));
        printJobSettings.parmEmailBody(strFmt(
            'The nightly vendor reconciliation job has completed.\n\n' +
            'Total processed: %1\n' +
            'Total failed: %2\n' +
            'Batch ID: %3',
            _processed, _failed, batchId));
    }

    // Batch metadata
    public BatchHeader batchInfo()
    {
        BatchHeader batchHeader = super::batchInfo();
        batchHeader.parmDescription('Vendor Reconciliation Batch Job');
        batchHeader.parmBatchGroup('BATCHGROUP1');
        batchHeader.parmExecutionStyle(BatchExecutionStyle::OnDemand);
        return batchHeader;
    }

    // Static entry point
    public static void main(Args _args)
    {
        VendReconciliationBatchJob job = new VendReconciliationBatchJob();
        if (_args && _args.record())
        {
            job.parmVendTable(_args.record());
        }
        if (job.prompt())
        {
            job.run();
        }
    }
}
```

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeBatchReconciliation</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeBatchReconciliationEnabled</ConfigurationKey>
</ModelManifest>
```

## 18.9 Batch Production Guidance

### Idempotent Batch Jobs — `BatchInfo.Idempotent`

Design batch jobs to be **idempotent** — running the same job multiple times produces the same result without duplicate work or data corruption. Use the `BatchInfo.Idempotent` attribute:

```xpp
[BatchInfo(Idempotent = true)]
class VendReconciliationBatchJob extends RunBaseBatch
{
    public void run()
    {
        // Check if this work was already processed
        // Use batch ID or checkpoint to track progress
        // Skip already-processed records
    }
}
```

**Idempotency patterns:**
- Check for existing records before inserting (`exists join` or `select firstOnly`)
- Use checkpoints to resume from where a previous run left off
- Use `BatchHeader.parmBatchGroup()` to organize related jobs
- Track processed record IDs in a staging or log table

### `BatchRetryable` Interface

Implement `BatchRetryable` to allow the batch framework to automatically retry failed tasks:

```xpp
class VendReconciliationBatchJob extends RunBaseBatch implements BatchRetryable
{
    public int retryCount()
    {
        return 3;  // Number of retry attempts
    }

    public int retryDelay()
    {
        return 60;  // Delay in seconds between retries
    }
}
```

### Process Automation Framework — Use `SysOperationServiceController`

The **Process Automation Framework** integrates with batch jobs through `SysOperationServiceController`, **not** `RunBaseBatch`:
- `RunBaseBatch` jobs cannot be returned through the process automation list
- Use `SysOperationServiceController` with `runOn() = RunOn::Batch` for process automation integration
- Wrap `RunBaseBatch` with `SysOperation` to get both dialog input and scheduled execution

```xpp
[SysOperationServiceController]
class VendReconciliationService extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        new VendReconciliationService().runOperation();
    }
}
```

### Batch Task Limits

| Task Count | Guidance |
|---|---|
| **< 1,000** | Efficient — normal batch processing |
| **1,000 – 4,000** | Becomes inefficient — consider chunking |
| **> 4,000** | Excessive — redesign with smaller batches or multiple jobs |

**Best practices:**
- Keep transactions short — long transactions cause blocking and deadlocks
- Process records in chunks of 1,000 or fewer
- Use `while select` with `next` and a counter for chunked processing
- Design for idempotency — jobs should be safely re-runnable
- Use checkpoints for resumption after failure

### Batch Parameter Versioning

When you change batch parameters, use versioning to maintain backward compatibility:

```xpp
#define.Version1(1)
#define.Version2(2)
#define.CurrentVersion(3)

#localmacro.Version1List
    param1
#endmacro

#localmacro.Version2List
    #Version1List
    ,param2
#endmacro

#localmacro.CurrentVersionList
    #Version2List
    ,param3
#endmacro

boolean unpack(container _packedClass)
{
    Integer version = conPeek(_packedClass, 1);

    switch (version)
    {
        case #CurrentVersion:
            [version, #CurrentVersionList] = _packedClass;
            break;
        case #Version2:
            [version, #Version2List] = _packedClass;
            break;
        case #Version1:
            [version, #Version1List] = _packedClass;
            break;
        default:
            return false;
    }

    return true;
}
```

**Best practices:**
- Maintain versioned parameter lists — keep old and new versions
- Adapt the unpacking process to handle both old and new versions
- Design functional logic to accommodate old parameter versions (revert to previous behavior)

---

---

### Remaining Chapters — Detailed Outlines


# Chapter 19: SysTest Framework — Complete Guide

> **Prerequisites:** Basic X++ knowledge, Visual Studio with D365 F&O tools, access to a D365 F&O development environment  
> **Time Investment:** 4–6 hours to read, 8–12 hours to practice all examples  
> **Microsoft Learn References:** [SysTest framework](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework), [Unit testing in D365 F&O](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/unit-testing), [Test automation](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-automation)

---

## Table of Contents

1. [The SysTest Framework — Core Components](#1-the-systest-framework--core-components)
2. [Assert Methods — Complete Reference](#2-assert-methods--complete-reference)
3. [Test Data Creation Patterns](#3-test-data-creation-patterns)
4. [Test Isolation and Data-Driven Testing](#4-test-isolation-and-data-driven-testing)
5. [Test Coverage Metrics in LCS](#5-test-coverage-metrics-in-lcs)
6. [Integration Testing with LCS Test Case Management](#6-integration-testing-with-lcs-test-case-management)
7. [Activity: Complete Test Class for Sales Order Discount Calculation](#7-activity-complete-test-class-for-sales-order-discount-calculation)
8. [Best Practices, Common Mistakes, and CI/CD Integration](#8-best-practices-common-mistakes-and-cicd-integration)

---

## 1. The SysTest Framework — Core Components

### 1.1 What Is SysTest? (Layman Explanation)

**SysTest is D365 F&O's built-in unit testing framework.** Think of it as a **quality gate** that runs your code in a controlled environment and tells you whether it behaves as expected. Unlike manual testing where a human clicks through forms, SysTest runs automatically, can be executed hundreds of times per minute, and integrates with your build pipeline so broken code never reaches production.

**Analogy:** If D365 F&O is a factory, SysTest is the automated quality control scanner on the assembly line — it checks every widget (code unit) against specifications before it ships.

### 1.2 Core Classes and Attributes

| Component | Type | Purpose | When It Runs |
|-----------|------|---------|--------------|
| `SysTestCase` | Base class | Every test class must extend this | — |
| `SysTestMethodAttribute` | Attribute | Marks a method as a test method | Per test execution |
| `setUp()` | Instance method | Creates shared test data for the class | Once before all test methods |
| `tearDown()` | Instance method | Cleans up shared test data | Once after all test methods |
| `SysTestTransactionAttribute` | Attribute | Controls transaction isolation level | Per test method |

### 1.3 Test Class Structure — Complete Example

```xpp
/// <summary>
/// Test class for vendor compliance validation logic.
/// Demonstrates the standard SysTest class structure.
/// </summary>
class VendComplianceTest extends SysTestCase
{
    // ========================================
    // SHARED SETUP — Runs ONCE before all tests
    // ========================================
    public void setUp()
    {
        // Create test data that ALL test methods need
        // Example: reference data, configuration records, lookup values
        
        // Create a standard vendor group for tests
        VendGroup vendGroup;
        vendGroup.initValue();
        vendGroup.VendGroup = 'TESTGROUP';
        vendGroup.Name = 'Test Vendor Group';
        vendGroup.insert();
    }

    // ========================================
    // TEST METHOD — Each is an independent test case
    // ========================================
    [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_FailsForHighCredit()
    {
        // AAA Pattern: Arrange → Act → Assert
        
        // ARRANGE — Set up test-specific data
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = 'HIGHVENDOR01';
        vendTable.Name = 'High Credit Vendor';
        vendTable.CreditMax = 600000;  // Above $500K threshold
        vendTable.VendGroup = 'TESTGROUP';
        vendTable.insert();

        // ACT — Execute the code under test
        boolean validationResult = VendComplianceValidator::validate(vendTable, '');

        // ASSERT — Verify the outcome
        this.assertFalse(validationResult, 'Validation should fail for vendor >$500K without compliance code');
        
        // CLEANUP — Remove test-specific data (optional with AutoRollback)
        vendTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_PassesForLowCredit()
    {
        // ARRANGE
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = 'LOWVENDOR01';
        vendTable.Name = 'Low Credit Vendor';
        vendTable.CreditMax = 100000;  // Below $500K threshold
        vendTable.VendGroup = 'TESTGROUP';
        vendTable.insert();

        // ACT
        boolean validationResult = VendComplianceValidator::validate(vendTable, '');

        // ASSERT
        this.assertTrue(validationResult, 'Validation should pass for vendor <$500K without compliance code');
        
        // CLEANUP
        vendTable.delete();
    }

    // ========================================
    // SHARED TEARDOWN — Runs ONCE after all tests
    // ========================================
    public void tearDown()
    {
        // Clean up shared test data created in setUp()
        VendGroup vendGroup;
        while select vendGroup
            where vendGroup.VendGroup == 'TESTGROUP'
        {
            vendGroup.delete();
        }
    }
}
```

### 1.4 Alternative: Test Method Naming Convention

Instead of `[SysTestMethodAttribute]`, you can prefix methods with `test`:

```xpp
class VendComplianceTest extends SysTestCase
{
    // This works the same as [SysTestMethodAttribute]
    public static void testComplianceCodeValidation_FailsForHighCredit()
    {
        // Test logic
    }
    
    // This is NOT a test method (missing "test" prefix)
    public static void helperMethod()
    {
        // Helper logic
    }
}
```

**Best Practice:** Use `[SysTestMethodAttribute]` explicitly — it's clearer, searchable, and allows additional attributes like `[SysTestCategory]`.

### 1.5 Key Differences: `setUp()` vs Per-Method Setup

| Aspect | `setUp()` (Class-Level) | Per-Method Setup |
|--------|------------------------|------------------|
| **Runs** | Once per test class | Before each test method |
| **Scope** | Shared across all tests | Isolated to one test |
| **Use For** | Reference data, lookup tables, configuration | Test-specific transactional data |
| **Cleanup** | In `tearDown()` | In same test method |

---

## 2. Assert Methods — Complete Reference

### 2.1 Core Assertion Methods (Inherited from `SysTestCase`)

All assertion methods are instance methods on `SysTestCase` — call them with `this.assertXxx()` or just `assertXxx()` within test methods.

| Method | Signature | Purpose | When to Use |
|--------|-----------|---------|-------------|
| **Equality** |
| `assertEquals` | `assertEquals(expected, actual, message)` | Verifies two values are equal | Primary assertion for most tests |
| `assertNotEquals` | `assertNotEquals(unexpected, actual, message)` | Verifies two values are NOT equal | Negative assertions |
| **Boolean** |
| `assertTrue` | `assertTrue(condition, message)` | Verifies condition is true | Boolean results, flags |
| `assertFalse` | `assertFalse(condition, message)` | Verifies condition is false | Boolean results, flags |
| **Null Checks** |
| `assertNull` | `assertNull(value, message)` | Verifies value is null | Return values that should be null |
| `assertNotNull` | `assertNotNull(value, message)` | Verifies value is NOT null | Return values that must exist |
| **Numeric Comparisons** |
| `assertGreater` | `assertGreater(actual, expected, message)` | Verifies actual > expected | Counts, amounts, thresholds |
| `assertLess` | `assertLess(actual, expected, message)` | Verifies actual < expected | Limits, boundaries |
| `assertGreaterOrEqual` | `assertGreaterOrEqual(actual, expected, message)` | Verifies actual >= expected | Minimum thresholds |
| `assertLessOrEqual` | `assertLessOrEqual(actual, expected, message)` | Verifies actual <= expected | Maximum caps |
| **Exception & Message Validation** |
| `assertException` | `assertException(className, methodName, expectedException, message)` | Verifies a method throws an exception | Error handling paths |
| `assertError` | `assertError(statement, message)` | Verifies statement produces an error | Form validation, `validateWrite()` |
| `assertWarning` | `assertWarning(statement, message)` | Verifies statement produces a warning | Business logic warnings |
| `assertInfo` | `assertInfo(statement, message)` | Verifies statement produces an info message | Success messages, logging |

### 2.2 Assertion Examples — Real-World Scenarios

#### 2.2.1 Basic Equality Assertions

```xpp
[SysTestMethodAttribute]
public static void testDiscountCalculation_Basic()
{
    SalesOrderDiscount discountCalculator;
    Real discountPercent;
    
    // ARRANGE
    discountCalculator = SalesOrderDiscount::construct();
    SalesTable salesTable = TestSalesTable::newTest('CUST001', 15000);
    salesTable.insert();
    
    // ACT
    discountPercent = discountCalculator.calculateDiscount(salesTable);
    
    // ASSERT — Exact value comparison
    this.assertEquals(5.0, discountPercent, 'Standard discount should be 5% for orders over $10K');
    
    // ASSERT — Not equal (negative assertion)
    this.assertNotEquals(0.0, discountPercent, 'Discount should not be zero for qualifying orders');
    
    salesTable.delete();
}
```

#### 2.2.2 Boolean Assertions

```xpp
[SysTestMethodAttribute]
public static void testCustomerValidation_IsValid()
{
    CustTable custTable = TestCustTable::constructValid();
    custTable.insert();
    
    // ACT — Returns boolean
    boolean isValid = CustomerValidator::isEligibleForCredit(custTable);
    
    // ASSERT — Boolean checks
    this.assertTrue(isValid, 'Valid customer should be eligible for credit');
    
    // Negative case
    custTable.Blocked = CustVendorBlocked::All;
    custTable.update();
    
    isValid = CustomerValidator::isEligibleForCredit(custTable);
    this.assertFalse(isValid, 'Blocked customer should NOT be eligible for credit');
    
    custTable.delete();
}
```

#### 2.2.3 Null Assertions

```xpp
[SysTestMethodAttribute]
public static void testFindCustomer_NotFound()
{
    // ACT — Try to find non-existent customer
    CustTable custTable = CustTable::find('NONEXISTENT');
    
    // ASSERT — Should return null/empty record
    this.assertNull(custTable.RecId, 'Non-existent customer should return empty record');
    this.assertEquals('', custTable.AccountNum, 'AccountNum should be empty for non-existent customer');
}

[SysTestMethodAttribute]
public static void testCreateSalesOrder_ReturnsRecord()
{
    SalesTable salesTable = SalesOrderService::create('CUST001');
    
    // ASSERT — Must return a valid record
    this.assertNotNull(salesTable.RecId, 'Created sales order should have RecId');
    this.assertNotEquals('', salesTable.SalesId, 'Created sales order should have SalesId');
}
```

#### 2.2.4 Numeric Comparison Assertions

```xpp
[SysTestMethodAttribute]
public static void testInventoryReservation_QuantityChecks()
{
    InventSum inventSum = InventSum::find('ITEM001', 'WH01');
    
    // ARRANGE — Reserve 50 units
    InventoryReservation::reserve('ITEM001', 'WH01', 50);
    inventSum.reread();
    
    // ASSERT — Numeric thresholds
    this.assertGreater(inventSum.ReservPhysical, 0, 'Should have physical reservations');
    this.assertGreaterOrEqual(inventSum.ReservPhysical, 50, 'Should have at least 50 reserved');
    this.assertLessOrEqual(inventSum.ReservPhysical, inventSum.AvailPhysical, 'Reserved cannot exceed available');
    
    // Cleanup
    InventoryReservation::unreserve('ITEM001', 'WH01', 50);
}
```

#### 2.2.5 Exception and Message Validation

```xpp
[SysTestMethodAttribute]
public static void testValidateWrite_ThrowsErrorForNegativeAmount()
{
    SalesLine salesLine;
    salesLine.initValue();
    salesLine.ItemId = 'ITEM001';
    salesLine.SalesQty = -10;  // Invalid: negative quantity
    salesLine.LineAmount = -5000;
    
    // ASSERT — ValidateWrite should throw an error
    this.assertError(salesLine.validateWrite(), 'Negative quantity should produce an error');
}

[SysTestMethodAttribute]
public static void testCheckCreditLimit_ProducesWarning()
{
    CustTable custTable = TestCustTable::newTest('CUST001', 100000);  // $100K credit limit
    custTable.insert();
    
    SalesTable salesTable = TestSalesTable::newTest(custTable.AccountNum, 150000);  // $150K order
    salesTable.insert();
    
    // ASSERT — Should produce a warning (not an error) for exceeding credit limit
    this.assertWarning(CustCreditCheck::check(salesTable), 'Should warn when order exceeds credit limit');
    
    salesTable.delete();
    custTable.delete();
}

[SysTestMethodAttribute]
public static void testProcessOrder_ProducesInfoMessage()
{
    SalesTable salesTable = TestSalesTable::constructConfirmed();
    salesTable.insert();
    
    // ASSERT — Process should produce info message
    this.assertInfo(SalesOrderProcessor::process(salesTable), 'Processing should log info message');
    
    salesTable.delete();
}

[SysTestMethodAttribute]
public static void testDivideByZero_ThrowsException()
{
    // ASSERT — Static method should throw when dividing by zero
    this.assertException(
        classStr(MathHelper),
        methodStr(MathHelper, divide),
        error::Error,  // Expected exception type
        'Division by zero should throw Error exception'
    );
}
```

### 2.3 Assertion Method Signatures — Quick Reference

```xpp
// All methods accept an optional message parameter as the last argument
// Message is displayed in test output when assertion fails

// Equality
void assertEquals(anyType _expected, anyType _actual, str _message = '')
void assertNotEquals(anyType _expected, anyType _actual, str _message = '')

// Boolean
void assertTrue(boolean _condition, str _message = '')
void assertFalse(boolean _condition, str _message = '')

// Null
void assertNull(anyType _value, str _message = '')
void assertNotNull(anyType _value, str _message = '')

// Numeric (Real/Int)
void assertGreater(Real _actual, Real _expected, str _message = '')
void assertLess(Real _actual, Real _expected, str _message = '')
void assertGreaterOrEqual(Real _actual, Real _expected, str _message = '')
void assertLessOrEqual(Real _actual, Real _expected, str _message = '')

// Exception & Messages
void assertException(str _className, str _methodName, int _expectedException, str _message = '')
void assertError(boolean _statement, str _message = '')
void assertWarning(boolean _statement, str _message = '')
void assertInfo(boolean _statement, str _message = '')
```

---

## 3. Test Data Creation Patterns

### 3.1 Why Test Data Patterns Matter

Creating test data is **the most time-consuming part of writing tests**. Good patterns make tests:
- **Readable** — Intent is clear from the test code
- **Maintainable** — Changes to table structure only need updates in one place
- **Isolated** — Tests don't interfere with each other
- **Fast** — Minimal database operations

### 3.2 Pattern 1: Factory Class with `construct()` — Recommended

```xpp
/// <summary>
/// Test data factory for VendTable records.
/// Provides sensible defaults that tests can customize.
/// </summary>
class TestVendTable
{
    /// <summary>
    /// Creates a vendor with standard defaults.
    /// Caller must call insert().
    /// </summary>
    public static VendTable construct()
    {
        VendTable vendTable;
        
        vendTable.initValue();
        vendTable.AccountNum = 'TESTVENDOR';  // Will be overridden if needed
        vendTable.Name = 'Test Vendor';
        vendTable.CreditMax = 50000;
        vendTable.Currency = 'USD';
        vendTable.VendGroup = 'VENDGROUP1';
        vendTable.PaymTermId = 'NET30';
        vendTable.TaxGroup = 'TAXGROUP1';
        
        return vendTable;
    }

    /// <summary>
    /// Creates a vendor with specific test parameters.
    /// </summary>
    public static VendTable newTest(
        AccountNum _accountNum, 
        Currency _currency, 
        Real _creditMax,
        VendGroup _vendGroup = 'VENDGROUP1'
    )
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.AccountNum = _accountNum;
        vendTable.Currency = _currency;
        vendTable.CreditMax = _creditMax;
        vendTable.VendGroup = _vendGroup;
        return vendTable;
    }

    /// <summary>
    /// Creates a high-credit vendor (>$500K) for compliance testing.
    /// </summary>
    public static VendTable newHighCreditVendor(AccountNum _accountNum)
    {
        return TestVendTable::newTest(_accountNum, 'USD', 750000);
    }

    /// <summary>
    /// Creates a VIP vendor for discount testing.
    /// </summary>
    public static VendTable newVIPVendor(AccountNum _accountNum)
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.AccountNum = _accountNum;
        vendTable.CustGroup = 'VIP';  // Assuming CustGroup field exists
        vendTable.CreditMax = 1000000;
        return vendTable;
    }
}
```

**Usage in Tests:**

```xpp
[SysTestMethodAttribute]
public static void testWithConstruct()
{
    VendTable vendTable = TestVendTable::construct();
    vendTable.AccountNum = 'UNIQUE001';  // Override for uniqueness
    vendTable.insert();
    
    // Test logic
    this.assertEquals('TESTVENDOR', vendTable.AccountNum);
    
    vendTable.delete();
}

[SysTestMethodAttribute]
public static void testWithNewTest()
{
    VendTable vendTable = TestVendTable::newTest('VEND001', 'EUR', 750000);
    vendTable.insert();
    
    this.assertEquals('EUR', vendTable.Currency);
    this.assertEquals(750000, vendTable.CreditMax);
    
    vendTable.delete();
}
```

### 3.3 Pattern 2: Test Data Builder (Fluent API) — Maximum Flexibility

```xpp
/// <summary>
/// Fluent builder for creating complex test SalesOrder scenarios.
/// </summary>
class TestSalesOrderBuilder
{
    SalesTable salesTable;
    List salesLines;  // List of SalesLine records
    
    private void new()
    {
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesLines = new List(Types::Record);
    }
    
    public static TestSalesOrderBuilder create()
    {
        return new TestSalesOrderBuilder();
    }
    
    public TestSalesOrderBuilder withCustomer(CustAccount _custAccount)
    {
        salesTable.CustomerAccount = _custAccount;
        return this;
    }
    
    public TestSalesOrderBuilder withDate(TransDate _date)
    {
        salesTable.SalesDate = _date;
        return this;
    }
    
    public TestSalesOrderBuilder withSalesId(SalesId _salesId)
    {
        salesTable.SalesId = _salesId;
        return this;
    }
    
    public TestSalesOrderBuilder addLine(
        ItemId _itemId, 
        Qty _qty, 
        Amount _lineAmount,
        InventDimId _inventDimId = '')
    {
        SalesLine salesLine;
        salesLine.initValue();
        salesLine.ItemId = _itemId;
        salesLine.SalesQty = _qty;
        salesLine.LineAmount = _lineAmount;
        salesLine.InventDimId = _inventDimId ? _inventDimId : InventDim::findOrCreate('_').InventDimId;
        salesLines.addEnd(salesLine);
        return this;
    }
    
    public TestSalesOrderBuilder withPaymentTerms(PaymTermId _paymTermId)
    {
        salesTable.PaymTermId = _paymTermId;
        return this;
    }
    
    public SalesTable build()
    {
        // Insert header
        salesTable.insert();
        
        // Insert lines
        SalesLine salesLine;
        while select salesLine from salesLines
        {
            salesLine.SalesTableId = salesTable.SalesId;
            salesLine.insert();
        }
        
        return salesTable;
    }
    
    public void cleanup()
    {
        SalesLine salesLine;
        while select salesLine from salesLines
        {
            salesLine.delete();
        }
        salesTable.delete();
    }
}
```

**Usage:**

```xpp
[SysTestMethodAttribute]
public static void testComplexOrderWithBuilder()
{
    // Arrange — Fluent, readable test setup
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer('CUST001')
        .withDate(today())
        .addLine('ITEM001', 10, 5000)
        .addLine('ITEM002', 5, 2500)
        .withPaymentTerms('NET30')
        .build();
    
    // Act
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // Assert
    this.assertEquals(5, discount);
    
    // Cleanup
    TestSalesOrderBuilder::create().cleanup();  // Or track builder instance
}
```

### 3.4 Pattern 3: Shared Setup with `setUp()` — For Reference Data

```xpp
class SalesOrderTest extends SysTestCase
{
    // Shared reference data — created ONCE for entire test class
    public void setUp()
    {
        // Create standard customers used by multiple tests
        CustTable custTable;
        
        // Standard customer
        custTable = TestCustTable::newTest('STD001', 'Standard Customer', 'STD');
        custTable.insert();
        
        // VIP customer
        custTable = TestCustTable::newTest('VIP001', 'VIP Customer', 'VIP');
        custTable.CustGroup = 'VIP';
        custTable.insert();
        
        // Standard items
        InventTable inventTable;
        inventTable = TestInventTable::newTest('ITEM001', 'Test Item 1', 'RAW');
        inventTable.insert();
        inventTable = TestInventTable::newTest('ITEM002', 'Test Item 2', 'FG');
        inventTable.insert();
        
        // Standard warehouse
        InventLocation location;
        location.initValue();
        location.InventLocationId = 'TESTWH';
        location.Name = 'Test Warehouse';
        location.insert();
        
        // Create default InventDim for TESTWH
        InventDim inventDim;
        inventDim.initValue();
        inventDim.InventLocationId = 'TESTWH';
        InventDim::findOrCreate(inventDim);
    }
    
    public void tearDown()
    {
        // Clean up shared data
        CustTable custTable;
        while select custTable where custTable.AccountNum like 'STD%' || custTable.AccountNum like 'VIP%'
        {
            custTable.delete();
        }
        
        InventTable inventTable;
        while select inventTable where inventTable.ItemId like 'ITEM%'
        {
            inventTable.delete();
        }
        
        InventLocation location;
        while select location where location.InventLocationId == 'TESTWH'
        {
            location.delete();
        }
    }
    
    [SysTestMethodAttribute]
    public static void testStandardCustomerOrder()
    {
        // Uses shared customer 'STD001' and item 'ITEM001'
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 100, 15000)
            .build();
        
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        this.assertEquals(5, discount);
        
        salesTable.delete();  // Per-test cleanup
    }
}
```

### 3.5 Using Number Sequences for Unique IDs

**Critical:** Never hardcode IDs like `'VEND001'` in parallel test runs — they'll collide. Use number sequences or GUIDs.

```xpp
class TestDataHelper
{
    /// <summary>
    /// Generates a unique test account number using number sequence.
    /// </summary>
    public static AccountNum generateTestAccountNum(str _prefix = 'TEST')
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestAccountNum', true);
        if (!numberSeq)
        {
            // Fallback: use timestamp-based unique ID
            return strFmt('%1_%2', _prefix, DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('%1_%2', _prefix, numberSeq.num());
    }
    
    /// <summary>
    /// Generates a unique test sales ID.
    /// </summary>
    public static SalesId generateTestSalesId()
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestSalesId', true);
        if (!numberSeq)
        {
            return strFmt('TESTSO_%1', DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('TESTSO_%1', numberSeq.num());
    }
    
    /// <summary>
    /// Generates a unique test item ID.
    /// </summary>
    public static ItemId generateTestItemId()
    {
        NumberSeq numberSeq = NumberSeq::newGetNumFromCode('TestItemId', true);
        if (!numberSeq)
        {
            return strFmt('TESTITEM_%1', DateTimeUtil::toStr(DateTimeUtil::utcNow(), 1234));
        }
        return strFmt('TESTITEM_%1', numberSeq.num());
    }
}

// Usage in factory classes
class TestVendTable
{
    public static VendTable construct()
    {
        VendTable vendTable;
        vendTable.initValue();
        vendTable.AccountNum = TestDataHelper::generateTestAccountNum('VEND');
        vendTable.Name = strFmt('Test Vendor %1', vendTable.AccountNum);
        // ... other defaults
        return vendTable;
    }
}
```

**Number Sequence Setup (in model):**

```xml
<!-- Number sequence references in model manifest -->
<NumberSequenceReferences>
    <NumberSequenceReference>
        <Name>TestAccountNum</Name>
        <Description>Test vendor/customer account numbers</Description>
        <Scope>Company</Scope>
        <Format>TEST_####</Format>
    </NumberSequenceReference>
    <NumberSequenceReference>
        <Name>TestSalesId</Name>
        <Description>Test sales order IDs</Description>
        <Scope>Company</Scope>
        <Format>TESTSO_######</Format>
    </NumberSequenceReference>
</NumberSequenceReferences>
```

### 3.6 Pattern 4: CompanyData / Data Partition Isolation

For tests that need specific company data:

```xpp
class CrossCompanyTest extends SysTestCase
{
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::AutoRollback)]
    public static void testCrossCompanyDataAccess()
    {
        // Switch to specific company for test
        changeCompany('USMF')
        {
            // Create data in USMF
            CustTable custTable = TestCustTable::construct();
            custTable.insert();
            
            // Verify visible in USMF
            CustTable found = CustTable::find(custTable.AccountNum);
            this.assertNotNull(found.RecId);
        }
        
        // Data automatically rolled back due to AutoRollback
    }
}
```

---

## 4. Test Isolation and Data-Driven Testing

### 4.1 Test Isolation — Why It Matters

**Test isolation** means each test runs independently — no test depends on another's data or state. Without isolation:
- Tests pass/fail depending on run order
- Parallel test execution fails
- Debugging becomes a nightmare

### 4.2 `SysTestTransactionAttribute` — Transaction Isolation Modes

```xpp
class IsolationModeExamples extends SysTestCase
{
    // DEFAULT: AutoRollback — Best isolation, fastest
    // Uses SQL savepoints — all changes rolled back automatically
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::AutoRollback)]
    public static void testWithAutoRollback()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // No cleanup needed — AutoRollback handles it
        this.assertNotNull(VendTable::find(vendTable.AccountNum).RecId);
    }
    
    // LegacyRollback — Tracks INSERTs, deletes them on cleanup
    // Use when testing concurrency/locking behavior
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::LegacyRollback)]
    public static void testWithLegacyRollback()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // Inserts tracked, deleted after test
        this.assertNotNull(VendTable::find(vendTable.AccountNum).RecId);
    }
    
    // LegacyRollbackWithUpdateTracking — Tracks INSERT, UPDATE, DELETE
    // Slowest — use only when testing complex transactional behavior
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::LegacyRollbackWithUpdateTracking)]
    public static void testWithFullTracking()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        vendTable.CreditMax = 999999;
        vendTable.update();  // Tracked and reverted
        
        this.assertEquals(999999, VendTable::find(vendTable.AccountNum).CreditMax);
        // Reverted after test
    }
    
    // None — NO isolation, data persists
    // ONLY for debugging — NEVER in committed tests
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::None)]
    public static void testWithNoIsolation_DebugOnly()
    {
        VendTable vendTable = TestVendTable::construct();
        vendTable.insert();
        
        // Data remains in database after test!
        // Use to inspect data in browser/SQL after test runs
        // REMOVE THIS ATTRIBUTE BEFORE COMMITTING
    }
}
```

| Mode | Isolation Level | Speed | Use Case |
|------|-----------------|-------|----------|
| `AutoRollback` | ✅ Full (savepoints) | ⚡ Fastest | **Default — use for 95% of tests** |
| `LegacyRollback` | ⚠️ INSERT only | 🐢 Slower | Concurrency/locking tests |
| `LegacyRollbackWithUpdateTracking` | ⚠️ INSERT/UPDATE/DELETE | 🐢🐢 Slowest | Complex transaction tests |
| `None` | ❌ None | ⚡ Fast | **Debugging only — never commit** |

### 4.3 Database Snapshots — Advanced Isolation

For integration tests needing clean database state:

```xpp
class DatabaseSnapshotTest extends SysTestCase
{
    // Use with Tier-2+ environments that support database snapshots
    // Not available in standard Tier-1 dev boxes
    
    [SysTestMethodAttribute]
    public static void testWithSnapshot()
    {
        // This requires LCS environment with snapshot capability
        // Typically used in Test/QA environments, not dev
        
        // 1. Create snapshot before test suite
        // 2. Run tests
        // 3. Restore snapshot after test suite
        
        // Implementation is environment-specific
        // See: LCS documentation on database refresh/snapshots
    }
}
```

### 4.4 Data-Driven Testing with `SysTestRow` (v10.0.25+)

Test multiple inputs with a single test method — each row becomes a separate test result.

```xpp
class MathTests extends SysTestCase
{
    // Each SysTestRow = one test execution
    // Results appear as: squareTests#1, squareTests#2, etc.
    [SysTestMethodAttribute,
    SysTestRow(0, 0),
    SysTestRow(1, 1),
    SysTestRow(2, 4),
    SysTestRow(3, 9),
    SysTestRow(4, 16),
    SysTestRow(-1, 1),
    SysTestRow(-2, 4),
    SysTestRow(-3, 9)]
    public static void squareTests(int _value, int _expected)
    {
        int result = MathHelper::square(_value);
        this.assertEquals(_expected, result, strFmt('Square of %1 should be %2', _value, _expected));
    }
    
    // Disable specific rows with SysTestRowInactive
    [SysTestMethodAttribute,
    SysTestRow(10, 100),
    SysTestRowInactive(11, 121),  // This row will be skipped
    SysTestRow(12, 144)]
    public static void squareTests_LargerNumbers(int _value, int _expected)
    {
        int result = MathHelper::square(_value);
        this.assertEquals(_expected, result);
    }
}
```

**Data-Driven Discount Test Example:**

```xpp
class SalesOrderDiscountDataDrivenTest extends SysTestCase
{
    // Test data: CustomerType, OrderAmount, ExpectedDiscount, TestDescription
    [SysTestMethodAttribute,
    SysTestRow('Standard', 5000, 0, 'Standard customer under $10K'),
    SysTestRow('Standard', 10000, 5, 'Standard customer at $10K boundary'),
    SysTestRow('Standard', 15000, 5, 'Standard customer over $10K'),
    SysTestRow('Standard', 50000, 15, 'Standard customer at $50K boundary'),
    SysTestRow('Standard', 60000, 15, 'Standard customer over $50K'),
    SysTestRow('VIP', 5000, 10, 'VIP customer under $10K'),
    SysTestRow('VIP', 10000, 15, 'VIP customer at $10K (10% VIP + 5% standard)'),
    SysTestRow('VIP', 50000, 25, 'VIP customer at $50K (10% VIP + 15% volume)'),
    SysTestRow('VIP', 60000, 25, 'VIP customer over $50K'),
    SysTestRow('VIP', 100000, 30, 'VIP large order capped at 30%')]
    public static void testDiscountCalculation(
        CustGroup _custGroup, 
        Amount _orderAmount, 
        Real _expectedDiscount,
        str _description)
    {
        // ARRANGE — Create customer and order using parameters
        CustTable custTable = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('CUST'), 
            _custGroup, 
            1000000
        );
        custTable.insert();
        
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer(custTable.AccountNum)
            .addLine('ITEM001', 1, _orderAmount)
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(_expectedDiscount, discount, _description);
        
        // CLEANUP (not needed with AutoRollback, but explicit is clear)
        salesTable.delete();
        custTable.delete();
    }
}
```

### 4.5 Test Filtering Attributes — Organize Test Runs

```xpp
class SalesOrderTest extends SysTestCase
{
    // Category: Run in specific pipelines (CheckIn, Nightly, Integration)
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]  // Higher = runs first (1-10)
    [SysTestOwner('john.doe@company.com')]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'DiscountCalculation')]
    [SysTestMethodAttribute]
    public static void testStandardDiscount()
    {
        // Fast unit test — runs in every check-in build
    }
    
    [SysTestCategory('Nightly')]
    [SysTestPriority(5)]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'DiscountCalculation')]
    [SysTestMethodAttribute]
    public static void testComplexDiscountScenarios()
    {
        // Slower integration test — runs nightly
    }
    
    [SysTestCategory('Integration')]
    [SysTestPriority(10)]
    [SysTestProperty('module', 'Sales')]
    [SysTestProperty('feature', 'EndToEnd')]
    [SysTestMethodAttribute]
    public static void testFullOrderToInvoiceFlow()
    {
        // Full integration test — runs in test environment
    }
}
```

**CI/CD Pipeline Filtering:**

```yaml
# Azure DevOps — Run only CheckIn category tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'TestCategory=CheckIn'

# Run only Priority 1-3 tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'Priority<=3'

# Run only Sales module tests
- task: Dynamics365Test@1
  inputs:
    testClasses: '*Test'
    testFilter: 'Property=module=Sales'
```

---

## 5. Test Coverage Metrics in LCS

### 5.1 What LCS Coverage Measures

LCS (Lifecycle Services) provides **code coverage metrics** when you run tests in a build pipeline:

| Metric | Definition | Target |
|--------|------------|--------|
| **Line Coverage** | % of executable lines executed by tests | > 80% |
| **Method Coverage** | % of methods called by tests | > 75% |
| **Class Coverage** | % of classes with at least one test | > 70% |
| **Assembly Coverage** | % of assemblies covered | > 80% |

### 5.2 Enabling Code Coverage in Build Pipeline

```yaml
# Azure DevOps pipeline — Full coverage configuration
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'windows-latest'

variables:
  - name: BuildConfiguration
    value: 'Release'
  - name: CollectCoverage
    value: 'true'

steps:
# ... restore, build steps ...

# Run tests with coverage collection
- task: Dynamics365Test@1
  displayName: 'Run SysTest with Coverage'
  inputs:
    solution: '**/*.sln'
    testClasses: '*Test'
    configuration: '$(BuildConfiguration)'
    collectCoverage: true
    coverageThreshold: 70  # Fail build if coverage < 70%
    publishResults: true

# Publish coverage to LCS
- task: PublishCodeCoverageResults@1
  displayName: 'Publish Coverage to LCS'
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
    reportDirectory: '$(Agent.TempDirectory)/**/coverage/'
    failIfCoverageEmpty: true
```

### 5.3 Interpreting LCS Coverage Reports

**LCS Coverage Tab — Key Views:**

1. **Coverage Summary** — Overall percentages by assembly
2. **Class Coverage** — Drill into specific classes
3. **Method Coverage** — See which methods are untested
4. **Line Coverage** — Line-by-line highlighting (green=covered, red=uncovered)

**Reading the Report:**

```
┌─────────────────────────────────────────────────────────────┐
│ Coverage Summary                                            │
├──────────────────┬──────────┬──────────┬──────────┬─────────┤
│ Assembly         │ Lines    │ Methods  │ Classes  │ Status  │
├──────────────────┼──────────┼──────────┼──────────┼─────────┤
│ Acme.Sales       │ 87%      │ 82%      │ 90%      │ ✅ Pass │
│ Acme.Inventory   │ 45%      │ 38%      │ 52%      │ ❌ Fail │
│ Acme.Finance     │ 72%      │ 68%      │ 75%      │ ⚠️ Warn │
└──────────────────┴──────────┴──────────┴──────────┴─────────┘
```

**Action Items by Coverage Level:**

| Coverage | Action |
|----------|--------|
| **> 80%** | ✅ Excellent — maintain |
| **60–80%** | 📝 Good — add tests for critical untested paths |
| **40–60%** | ⚠️ Moderate — prioritize testing core business logic |
| **< 40%** | 🚨 Low — block merge, require test plan |

### 5.4 Coverage ≠ Quality — Critical Distinction

```xpp
// BAD: High coverage, low quality
[SysTestMethodAttribute]
public static void testCalculateDiscount_CoverageOnly()
{
    SalesTable salesTable = TestSalesTable::construct();
    salesTable.insert();
    
    SalesOrderDiscount discount = SalesOrderDiscount::construct();
    Real result = discount.calculateDiscount(salesTable);
    
    // Only checks method runs — doesn't verify CORRECTNESS
    this.assertNotNull(result);  // Weak assertion!
    
    salesTable.delete();
}

// GOOD: Lower coverage, high quality
[SysTestMethodAttribute]
public static void testCalculateDiscount_VerifiesBusinessRules()
{
    // Test exact business rule: 5% for orders > $10K
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer('STD001')
        .addLine('ITEM001', 100, 15000)  // $15K order
        .build();
    
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // Verifies CORRECT behavior, not just execution
    this.assertEquals(5.0, discount, 'Standard discount should be 5% for orders > $10K');
    
    salesTable.delete();
}
```

**Best Practice:** Aim for **meaningful coverage** — test edge cases, error paths, and business rule boundaries. A test that covers 10 lines with 5 assertions is better than one covering 50 lines with 1 assertion.

---

## 6. Integration Testing with LCS Test Case Management

### 6.1 LCS Test Case Management Overview

LCS provides **Test Case Management** — a bridge between manual test cases and automated SysTest methods.

```
┌────────────────────────────────────────────────────────────────────┐
│                    LCS TEST CASE LIFECYCLE                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  [1] DEFINE              [2] AUTOMATE              [3] EXECUTE    │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐   │
│  │ Test Plan   │───────▶│ Map to      │───────▶│ Run in      │   │
│  │ Test Suite  │        │ SysTest     │        │ Environment │   │
│  │ Test Cases  │        │ Methods     │        │ (Dev/Test/  │   │
│  └─────────────┘        └─────────────┘        │  UAT)       │   │
│         │                      │               └──────┬──────┘   │
│         ▼                      ▼                      ▼          │
│  [4] TRACK               [5] REPORT              [6] PROMOTE   │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐   │
│  │ Execution   │        │ Pass/Fail   │        │ Gate to     │   │
│  │ History     │        │ Metrics     │        │ Next Env    │   │
│  │ Screenshots │        │ Coverage    │        │             │   │
│  └─────────────┘        └─────────────┘        └─────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.2 Creating Test Cases in LCS

**Step 1: Create Test Plan**
1. Navigate to LCS Project → **Test Management** → **Test Plans**
2. Click **New Test Plan**
3. Name: `Sprint 23 - Sales Order Discount Feature`
4. Select **Test Suite** structure (e.g., by module/feature)

**Step 2: Create Test Cases**
For each test case:

| Field | Value | Example |
|-------|-------|---------|
| **Title** | Descriptive name | `Validate VIP + Volume discount stacks to 25%` |
| **Area** | Module/Feature | `Sales / Discount Calculation` |
| **Priority** | 1=Critical, 2=High, 3=Medium | `1` |
| **Automation Status** | Automated/Manual/Not Automated | `Automated` |
| **Associated Test Method** | SysTest class::method | `SalesOrderDiscountTest::testVIPVolumeDiscount_Over50K` |
| **Test Steps** | Step-by-step | See below |
| **Expected Result** | What should happen | `Discount = 25%` |
| **Test Data** | Required data | `VIP customer, order > $50K` |

**Test Steps Example:**
```
1. Create VIP customer (CustGroup = VIP)
2. Create sales order for VIP customer
3. Add line with amount > $50,000
4. Calculate discount
5. Verify discount = 25% (10% VIP + 15% Volume)
```

### 6.3 Associating SysTest Methods with LCS Test Cases

**Method 1: Naming Convention (Automatic)**
```xpp
class SalesOrderDiscountTest extends SysTestCase
{
    // LCS auto-matches by method name if "Automation Status = Automated"
    [SysTestMethodAttribute]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // LCS Test Case: "Validate VIP + Volume discount stacks to 25%"
    }
}
```

**Method 2: Explicit Mapping (Test Properties)**
```xpp
class SalesOrderDiscountTest extends SysTestCase
{
    [SysTestMethodAttribute]
    [SysTestProperty('lcsTestCaseId', '12345')]
    [SysTestProperty('lcsTestPlan', 'Sprint 23 - Sales Order Discount')]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // Explicitly linked to LCS Test Case ID 12345
    }
}
```

**Method 3: Test Case Management API (Advanced)**
```xpp
// For bulk import/sync from external tools (Azure DevOps, TestRail, etc.)
// Use LCS REST API to sync test cases
```

### 6.4 Running Tests in LCS

**Option A: Manual Execution (LCS UI)**
1. Go to **Test Management** → **Test Plans**
2. Select test plan → **Run** → **New Test Run**
3. Choose environment (Dev/Test/UAT)
4. Select test cases/suites
5. Click **Run** — LCS executes and shows live results

**Option B: CI/CD Pipeline (Automated)**
```yaml
# Azure DevOps — Runs tests and publishes to LCS
- task: Dynamics365Test@1
  displayName: 'Run SysTest and Publish to LCS'
  inputs:
    solution: '**/*.sln'
    testClasses: 'SalesOrderDiscountTest'
    configuration: 'Release'
    publishResults: true
    lcsProjectId: $(LCS_PROJECT_ID)
    lcsEnvironmentId: $(LCS_TEST_ENV_ID)
```

**Option C: Scheduled Runs (Nightly)**
1. LCS → **Test Management** → **Test Plans** → **Schedule**
2. Configure: Daily at 2 AM, Test Environment, All Test Cases
3. Results emailed to team, failures create work items

### 6.5 Test Execution Results in LCS

**LCS Test Run Dashboard shows:**

| Column | Description |
|--------|-------------|
| **Test Case** | Linked test case title |
| **Outcome** | Passed/Failed/Blocked/Not Run |
| **Duration** | Execution time |
| **Error Message** | Failure details (stack trace) |
| **Attachments** | Screenshots, logs |
| **Run By** | Pipeline or user |
| **Timestamp** | When executed |

**Failed Test Drill-Down:**
```
Test Case: Validate VIP + Volume discount stacks to 25%
Status: FAILED
Duration: 3.2s
Error: Assert.AreEqual failed. Expected: 25. Actual: 20.
Stack Trace:
  at SalesOrderDiscountTest.testVIPVolumeDiscount_Over50K()
  at SysTestRunner.executeTestMethod()
  
Attachments: 
  - screenshot_20240115_143201.png (order form)
  - test_log_20240115_143201.txt
```

---

## 7. Activity: Complete Test Class for Sales Order Discount Calculation

### 7.1 Requirements Recap

| Rule | Description |
|------|-------------|
| 1 | Standard discount: 5% for orders over $10,000 |
| 2 | VIP discount: 10% for VIP customers (CustGroup = 'VIP') |
| 3 | Volume discount: 15% for orders over $50,000 |
| 4 | Combined: VIP + Volume stack (25% for VIP orders > $50K) |
| 5 | No discount for orders < $10K (unless VIP = 10%) |
| 6 | Maximum discount cap: 30% |

### 7.2 Complete Test Class — Production Ready

```xpp
/// <summary>
/// Comprehensive test suite for SalesOrderDiscount calculation.
/// Covers all business rules, edge cases, and error conditions.
/// 
/// Run with: AutoRollback isolation (default)
/// Categories: CheckIn (fast), Nightly (comprehensive)
/// </summary>
class SalesOrderDiscountTest extends SysTestCase
{
    // ═══════════════════════════════════════════════════════════
    // SHARED TEST DATA — Created once for all test methods
    // ═══════════════════════════════════════════════════════════
    
    public void setUp()
    {
        // Create standard customer (non-VIP)
        CustTable stdCust = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('STD'),
            'Standard Customer',
            'STD'
        );
        stdCust.insert();
        
        // Create VIP customer
        CustTable vipCust = TestCustTable::newTest(
            TestDataHelper::generateTestAccountNum('VIP'),
            'VIP Customer',
            'VIP'
        );
        vipCust.CustGroup = 'VIP';
        vipCust.insert();
        
        // Create test item
        InventTable item = TestInventTable::newTest(
            TestDataHelper::generateTestItemId(),
            'Test Item',
            'FG'
        );
        item.insert();
        
        // Create warehouse and InventDim
        InventLocation location;
        location.initValue();
        location.InventLocationId = 'TESTWH';
        location.Name = 'Test Warehouse';
        location.insert();
        
        InventDim inventDim;
        inventDim.initValue();
        inventDim.InventLocationId = 'TESTWH';
        InventDim::findOrCreate(inventDim);
    }
    
    public void tearDown()
    {
        // Clean up shared data
        CustTable custTable;
        while select custTable
            where custTable.AccountNum like 'STD%'
               || custTable.AccountNum like 'VIP%'
        {
            custTable.delete();
        }
        
        InventTable item;
        while select item
            where item.ItemId like 'TESTITEM%'
        {
            item.delete();
        }
        
        InventLocation location;
        while select location
            where location.InventLocationId == 'TESTWH'
        {
            location.delete();
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // TEST METHODS — One per business rule + edge cases
    // ═══════════════════════════════════════════════════════════
    
    /// <summary>
    /// Rule 1: Standard discount 5% for orders over $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'StandardDiscount_Over10K')]
    public static void testStandardDiscount_Over10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')  // Standard customer from setUp
            .addLine('ITEM001', 100, 15000)  // $15K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(5.0, discount, 'Standard discount should be 5% for orders over $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 2: VIP discount 10% for orders under $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'VIPDiscount_Under10K')]
    public static void testVIPDiscount_Under10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')  // VIP customer from setUp
            .addLine('ITEM001', 10, 5000)  // $5K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(10.0, discount, 'VIP discount should be 10% even for orders under $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 4: Combined VIP (10%) + Volume (15%) = 25% for orders over $50K
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'CombinedVIPVolume_Over50K')]
    public static void testVIPVolumeDiscount_Over50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 500, 60000)  // $60K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(25.0, discount, 'VIP + Volume discount should be 25% for orders over $50K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 3: Volume discount 15% for non-VIP orders over $50,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'VolumeDiscount_NonVIP_Over50K')]
    public static void testVolumeDiscount_NonVIP_Over50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 500, 60000)  // $60K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(15.0, discount, 'Volume discount should be 15% for non-VIP orders over $50K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 5: No discount for non-VIP orders under $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'NoDiscount_NonVIP_Under10K')]
    public static void testNoDiscount_Under10K_NonVIP()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 5, 5000)  // $5K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(0.0, discount, 'No discount for non-VIP orders under $10K');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Rule 6: Maximum discount cap of 30%
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('CheckIn')]
    [SysTestPriority(1)]
    [SysTestProperty('rule', 'MaxDiscountCap_30Percent')]
    public static void testMaxDiscountCap_30Percent()
    {
        // ARRANGE — VIP + Volume + hypothetical "Special" = 35% but capped at 30%
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 1000, 100000)  // $100K order
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Cap enforced
        this.assertLessOrEqual(discount, 30.0, 'Discount should never exceed 30%');
        this.assertEquals(30.0, discount, 'Discount should be capped at exactly 30%');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Boundary value — exactly $10,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_Exactly10K')]
    public static void testBoundaryValue_Exactly10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 100, 10000)  // Exactly $10K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Boundary: >= $10K qualifies for standard discount
        this.assertEquals(5.0, discount, 'Standard discount should apply at exactly $10K (>= boundary)');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Boundary value — exactly $50,000
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_Exactly50K')]
    public static void testBoundaryValue_Exactly50K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 500, 50000)  // Exactly $50K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — Boundary: >= $50K qualifies for volume discount
        this.assertEquals(15.0, discount, 'Volume discount should apply at exactly $50K (>= boundary)');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Zero order total
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(3)]
    [SysTestProperty('rule', 'EdgeCase_ZeroTotal')]
    public static void testZeroOrderTotal()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 0, 0)  // Zero quantity and amount
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(0.0, discount, 'No discount for $0 order total');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: Negative order total — should throw error
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(3)]
    [SysTestProperty('rule', 'EdgeCase_NegativeTotal')]
    public static void testNegativeOrderTotal_ThrowsError()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('STD001')
            .addLine('ITEM001', 1, -5000)  // Negative amount
            .build();
        
        // ASSERT — Should throw error for negative total
        this.assertException(
            classStr(SalesOrderDiscount),
            methodStr(SalesOrderDiscount, calculateDiscount),
            error::Error,
            'Negative order total should throw Error exception'
        );
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Edge Case: VIP customer at exactly $10K boundary
    /// </summary>
    [SysTestMethodAttribute]
    [SysTestCategory('Nightly')]
    [SysTestPriority(2)]
    [SysTestProperty('rule', 'Boundary_VIP_Exactly10K')]
    public static void testVIPBoundary_Exactly10K()
    {
        // ARRANGE
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer('VIP001')
            .addLine('ITEM001', 100, 10000)  // Exactly $10K
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT — VIP gets 10% + standard 5% = 15% at $10K boundary
        this.assertEquals(15.0, discount, 'VIP at $10K boundary gets 10% VIP + 5% standard = 15%');
        
        // CLEANUP
        salesTable.delete();
    }
    
    /// <summary>
    /// Data-Driven Test: Multiple scenarios in one method
    /// </summary>
    [SysTestMethodAttribute,
    SysTestRow('STD', 5000, 0, 'Standard < 10K'),
    SysTestRow('STD', 10000, 5, 'Standard = 10K'),
    SysTestRow('STD', 15000, 5, 'Standard > 10K'),
    SysTestRow('STD', 50000, 15, 'Standard = 50K'),
    SysTestRow('STD', 60000, 15, 'Standard > 50K'),
    SysTestRow('VIP', 5000, 10, 'VIP < 10K'),
    SysTestRow('VIP', 10000, 15, 'VIP = 10K (10+5)'),
    SysTestRow('VIP', 15000, 15, 'VIP > 10K (10+5)'),
    SysTestRow('VIP', 50000, 25, 'VIP = 50K (10+15)'),
    SysTestRow('VIP', 60000, 25, 'VIP > 50K (10+15)'),
    SysTestRow('VIP', 100000, 30, 'VIP large capped at 30%')]
    [SysTestCategory('Nightly')]
    [SysTestPriority(5)]
    [SysTestProperty('rule', 'DataDriven_AllScenarios')]
    public static void testDiscountCalculation_DataDriven(
        CustGroup _custGroup,
        Amount _orderAmount,
        Real _expectedDiscount,
        str _description)
    {
        // ARRANGE
        AccountNum custAccount = _custGroup == 'VIP' ? 'VIP001' : 'STD001';
        
        SalesTable salesTable = TestSalesOrderBuilder::create()
            .withCustomer(custAccount)
            .addLine('ITEM001', 1, _orderAmount)
            .build();
        
        // ACT
        Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
        
        // ASSERT
        this.assertEquals(_expectedDiscount, discount, _description);
        
        // CLEANUP
        salesTable.delete();
    }
}
```

### 7.3 Supporting Classes (Factory & Builder)

```xpp
/// <summary>
/// Test data factory for CustTable
/// </summary>
class TestCustTable
{
    public static CustTable newTest(AccountNum _accountNum, str _name, CustGroup _custGroup)
    {
        CustTable custTable;
        custTable.initValue();
        custTable.AccountNum = _accountNum;
        custTable.Name = _name;
        custTable.CustGroup = _custGroup;
        custTable.Currency = 'USD';
        custTable.PaymTermId = 'NET30';
        custTable.InvoiceAccount = _accountNum;
        return custTable;
    }
}

/// <summary>
/// Test data factory for InventTable
/// </summary>
class TestInventTable
{
    public static InventTable newTest(ItemId _itemId, str _name, ItemType _itemType)
    {
        InventTable item;
        item.initValue();
        item.ItemId = _itemId;
        item.Name = _name;
        item.ItemType = _itemType;
        item.ItemGroupId = 'RAW';
        item.UnitId = 'EA';
        item.PurchUnit = 'EA';
        item.SalesUnit = 'EA';
        item.InventUnit = 'EA';
        return item;
    }
}

/// <summary>
/// Fluent builder for SalesTable with lines
/// </summary>
class TestSalesOrderBuilder
{
    SalesTable salesTable;
    List salesLines;
    
    private void new()
    {
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.SalesDate = today();
        salesLines = new List(Types::Record);
    }
    
    public static TestSalesOrderBuilder create()
    {
        return new TestSalesOrderBuilder();
    }
    
    public TestSalesOrderBuilder withCustomer(CustAccount _custAccount)
    {
        salesTable.CustomerAccount = _custAccount;
        salesTable.initFromCustTable(CustTable::find(_custAccount));
        return this;
    }
    
    public TestSalesOrderBuilder withSalesId(SalesId _salesId)
    {
        salesTable.SalesId = _salesId;
        return this;
    }
    
    public TestSalesOrderBuilder addLine(ItemId _itemId, Qty _qty, Amount _lineAmount)
    {
        SalesLine line;
        line.initValue();
        line.ItemId = _itemId;
        line.SalesQty = _qty;
        line.LineAmount = _lineAmount;
        line.initFromInventTable(InventTable::find(_itemId));
        line.InventDimId = InventDim::findOrCreate(InventDim::construct().parmInventLocationId('TESTWH')).InventDimId;
        salesLines.addEnd(line);
        return this;
    }
    
    public SalesTable build()
    {
        // Generate unique SalesId if not set
        if (!salesTable.SalesId)
        {
            salesTable.SalesId = NumberSeq::newGetNum(SalesParameters::numRefSalesId()).num();
        }
        
        salesTable.insert();
        
        SalesLine line;
        while select line from salesLines
        {
            line.SalesTableId = salesTable.SalesId;
            line.SalesId = salesTable.SalesId;
            line.insert();
        }
        
        return salesTable;
    }
}
```

### 7.4 Implementation Under Test (Reference)

```xpp
/// <summary>
/// Discount calculation service — implementation being tested
/// </summary>
class SalesOrderDiscount
{
    private const Real StandardDiscountPercent = 5.0;
    private const Real VIPDiscountPercent = 10.0;
    private const Real VolumeDiscountPercent = 15.0;
    private const Real MaxDiscountPercent = 30.0;
    private const Amount StandardThreshold = 10000;
    private const Amount VolumeThreshold = 50000;
    
    public static SalesOrderDiscount construct()
    {
        return new SalesOrderDiscount();
    }
    
    public Real calculateDiscount(SalesTable _salesTable)
    {
        if (!_salesTable)
        {
            throw error('Sales table cannot be null');
        }
        
        Amount orderTotal = this.getOrderTotal(_salesTable);
        
        if (orderTotal < 0)
        {
            throw error('Order total cannot be negative');
        }
        
        if (orderTotal == 0)
        {
            return 0;
        }
        
        Real discount = 0;
        boolean isVIP = this.isVIPCustomer(_salesTable.CustomerAccount);
        
        // Standard discount
        if (orderTotal >= StandardThreshold)
        {
            discount += StandardDiscountPercent;
        }
        
        // VIP discount (applies regardless of order amount)
        if (isVIP)
        {
            discount += VIPDiscountPercent;
        }
        
        // Volume discount
        if (orderTotal >= VolumeThreshold)
        {
            discount += VolumeDiscountPercent;
        }
        
        // Apply cap
        return discount > MaxDiscountPercent ? MaxDiscountPercent : discount;
    }
    
    private Amount getOrderTotal(SalesTable _salesTable)
    {
        Amount total;
        select sum(LineAmount) from SalesLine
            where SalesLine.SalesId == _salesTable.SalesId;
        return total;
    }
    
    private boolean isVIPCustomer(CustAccount _custAccount)
    {
        CustTable custTable = CustTable::find(_custAccount);
        return custTable && custTable.CustGroup == 'VIP';
    }
}
```

---

## 8. Best Practices, Common Mistakes, and CI/CD Integration

### 8.1 Best Practices — AAA Pattern

**Arrange → Act → Assert** — Structure every test method:

```xpp
[SysTestMethodAttribute]
public static void testExample()
{
    // ═══ ARRANGE ═══ — Set up test data and conditions
    VendTable vendTable = TestVendTable::construct();
    vendTable.CreditMax = 600000;
    vendTable.insert();
    
    SalesTable salesTable = TestSalesOrderBuilder::create()
        .withCustomer(vendTable.AccountNum)
        .addLine('ITEM001', 100, 15000)
        .build();
    
    // ═══ ACT ═══ — Execute the code under test (ONE line ideally)
    Real discount = SalesOrderDiscount::calculateDiscount(salesTable);
    
    // ═══ ASSERT ═══ — Verify the outcome
    this.assertEquals(5.0, discount, 'Standard discount should be 5%');
    
    // CLEANUP (optional with AutoRollback)
    salesTable.delete();
    vendTable.delete();
}
```

### 8.2 Test Naming Conventions

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `test<Method>_<Scenario>_<Expected>` | `testCalculateDiscount_VIPOver50K_Returns25` | **Recommended** — clear intent |
| `test<BusinessRule>_<Condition>` | `testStandardDiscount_Over10K` | Simple rules |
| `test<Feature>_<EdgeCase>` | `testDiscount_BoundaryExactly10K` | Edge cases |
| `test<Method>_Throws<Exception>` | `testCalculateDiscount_ThrowsOnNegative` | Error cases |

**Avoid:**
- `test1()`, `test2()` — meaningless
- `testDiscount()` — too vague
- `test_CalculateDiscount_ShouldReturn5Percent()` — C# style, not X++

### 8.3 Common Mistakes — And How to Fix Them

| Mistake | Problem | Fix |
|---------|---------|-----|
| **No isolation** — Tests share data without `AutoRollback` | Flaky tests, order-dependent | Use `[SysTestTransaction(SysTestTransactionMode::AutoRollback)]` |
| **Hardcoded IDs** — `'VEND001'` in multiple tests | Collisions in parallel runs | Use `NumberSeq` or `TestDataHelper::generateTestAccountNum()` |
| **Testing implementation, not behavior** | Brittle tests that break on refactor | Test business outcomes, not internal methods |
| **Missing edge cases** — Only happy path | Bugs in production | Test boundaries, nulls, negatives, empty collections |
| **Weak assertions** — `assertNotNull(result)` | Doesn't verify correctness | Use `assertEquals(expected, actual)` with specific values |
| **No cleanup** — Test data leaks | Pollutes environment, slows tests | Use `AutoRollback` or explicit `delete()` in `tearDown()` |
| **Testing multiple things in one test** | Hard to diagnose failures | One assertion concept per test method |
| **Slow tests** — Creating full form runs | CI/CD pipeline too slow | Unit test logic classes, not forms; use `AutoRollback` |

### 8.4 Running Tests in Visual Studio

**Test Explorer:**
1. Build solution (`Ctrl+Shift+B`)
2. Open **Test Explorer**: `Test` → `Test Explorer`
3. Tests appear grouped by class
4. Right-click → **Run Selected Tests** or **Run All**

**Test Explorer Columns to Enable:**
- **Duration** — Spot slow tests
- **Traits** — See Category, Priority, Owner

**Filtering in Test Explorer:**
```
Trait:Category=CheckIn      // Run only check-in tests
Trait:Priority<=3           // Run priority 1-3
Trait:module=Sales          // Run Sales module tests
```

**Debugging Tests:**
1. Set breakpoint in test method
2. Test Explorer → Right-click test → **Debug**
3. Step through code, inspect variables

### 8.5 CI/CD Pipeline Integration

**Complete Azure DevOps Pipeline:**

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - release/*

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'd365-build-variables'
  - name: BuildConfiguration
    value: 'Release'
  - name: TestFilter
    value: 'TestCategory=CheckIn'  # Fast tests for PR validation

stages:
- stage: Build
  displayName: 'Build & Test'
  jobs:
  - job: BuildAndTest
    displayName: 'Build Solution and Run Tests'
    timeoutInMinutes: 60
    steps:
    # 1. Restore NuGet
    - task: NuGetCommand@2
      displayName: 'Restore NuGet Packages'
      inputs:
        command: 'restore'
        feedsToUse: 'config'
        nugetConfigPath: 'nuget.config'

    # 2. Build Solution
    - task: MSBuild@1
      displayName: 'Build D365 F&O Solution'
      inputs:
        solution: '**/*.sln'
        platform: 'Any CPU'
        configuration: '$(BuildConfiguration)'
        msbuildArguments: >
          /p:BuildTasksDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage\DevAlm"
          /p:MetadataDirectory="$(Build.SourcesDirectory)\Metadata"
          /p:FrameworkDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage"
          /p:ReferenceFolder="$(Pipeline.Workspace)\NuGets"
          /p:OutputDirectory="$(Build.BinariesDirectory)"

    # 3. Run SysTest with Coverage
    - task: Dynamics365Test@1
      displayName: 'Run SysTest Unit Tests'
      inputs:
        solution: '**/*.sln'
        testClasses: '*Test'
        configuration: '$(BuildConfiguration)'
        testFilter: '$(TestFilter)'
        collectCoverage: true
        coverageThreshold: 70
        publishResults: true
        lcsProjectId: $(LCS_PROJECT_ID)
        lcsEnvironmentId: $(LCS_BUILD_ENV_ID)

    # 4. Publish Coverage Report
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Coverage to Azure DevOps'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
        reportDirectory: '$(Agent.TempDirectory)/**/coverage/'

    # 5. Publish Test Results
    - task: PublishTestResults@2
      displayName: 'Publish Test Results'
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '**/TestResults/*.trx'
        mergeTestResults: true
        failTaskOnFailedTests: true

- stage: NightlyTests
  displayName: 'Nightly Full Test Suite'
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - job: NightlyTests
    displayName: 'Run All Tests Including Nightly Category'
    steps:
    - task: Dynamics365Test@1
      displayName: 'Run Full Test Suite'
      inputs:
        solution: '**/*.sln'
        testClasses: '*Test'
        configuration: 'Release'
        testFilter: ''  # No filter = all tests
        collectCoverage: true
        coverageThreshold: 75
        publishResults: true
        lcsProjectId: $(LCS_PROJECT_ID)
        lcsEnvironmentId: $(LCS_TEST_ENV_ID)

- stage: DeployToTest
  displayName: 'Deploy to Test Environment'
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: DeployTest
    displayName: 'Deploy to Test Environment'
    environment: 'Test'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: Dynamics365Deploy@1
            inputs:
              lcsProjectId: $(LCS_PROJECT_ID)
              lcsEnvironmentId: $(LCS_TEST_ENV_ID)
              deployablePackage: '$(Build.ArtifactStagingDirectory)/*.zip'
```

### 8.6 Release Gates with Test Results

```yaml
# Release pipeline — Gate on test results
stages:
- stage: DeployToUAT
  displayName: 'Deploy to UAT'
  dependsOn: DeployToTest
  condition: succeeded()
  jobs:
  - deployment: DeployUAT
    environment: 'UAT'
    strategy:
      runOnce:
        preDeploy:
          steps:
          # Gate: Check test results from Test environment
          - task: AzureCLI@2
            displayName: 'Verify Test Results in LCS'
            inputs:
              azureSubscription: '$(AzureSubscription)'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Query LCS API for test results
                # Fail if any CheckIn tests failed in Test env
                TEST_RESULTS=$(az rest --method get \
                  --url "https://lcsapi.lcs.dynamics.com/api/v1/projects/$(LCS_PROJECT_ID)/environments/$(LCS_TEST_ENV_ID)/testresults" \
                  --query "value[?contains(testClass, 'Test') && outcome!='Passed']")
                
                if [ "$TEST_RESULTS" != "[]" ]; then
                  echo "##vso[task.logissue type=error]Failed tests found in Test environment"
                  echo "$TEST_RESULTS"
                  exit 1
                fi
                echo "All tests passed in Test environment"
        deploy:
          steps:
          - task: Dynamics365Deploy@1
            inputs:
              lcsProjectId: $(LCS_PROJECT_ID)
              lcsEnvironmentId: $(LCS_UAT_ENV_ID)
              deployablePackage: '$(Build.ArtifactStagingDirectory)/*.zip'
```

---

## Summary Checklist

| ✅ | Item |
|----|------|
| **Framework** | Extend `SysTestCase`, use `[SysTestMethodAttribute]`, implement `setUp()`/`tearDown()` |
| **Assertions** | Use `assertEquals`, `assertTrue`, `assertException`, `assertError` — avoid weak assertions |
| **Test Data** | Factory classes with `construct()`/`newTest()`, use NumberSeq for unique IDs |
| **Isolation** | Default `AutoRollback` — never use `None` in committed code |
| **Data-Driven** | Use `SysTestRow` for parameterized tests (v10.0.25+) |
| **Filtering** | Tag tests with `SysTestCategory`, `SysTestPriority`, `SysTestProperty` |
| **Coverage** | Enable in CI/CD, target >80% line coverage, focus on meaningful tests |
| **LCS Integration** | Map test cases, run in pipeline, gate deployments on test results |
| **Naming** | `test<Method>_<Scenario>_<Expected>` — clear and searchable |
| **CI/CD** | Run CheckIn tests on PR, Nightly on main, gate deployments on results |

---

## Microsoft Learn References

| Topic | Link |
|-------|------|
| SysTest Framework Overview | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-framework |
| Unit Testing in D365 F&O | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/unit-testing |
| Test Automation | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-automation |
| SysTest Attributes | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sys-test-attributes |
| Test Coverage in LCS | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/test-coverage |
| LCS Test Case Management | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lifecycle-services/test-case-management |
| Azure DevOps Test Task | https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/test/dynamics-365-test |

---

*Last Updated: November 2024*  
*Part of the D365 F&O Developer Handbook — Chapter 19*

```xpp
class TestVendTable
{
    public static VendTable newTest(AccountNum _accountNum, Currency _currency, Real _creditMax)
    {
        VendTable vendTable;

        vendTable.initValue();
        vendTable.AccountNum = _accountNum;
        vendTable.Currency = _currency;
        vendTable.CreditMax = _creditMax;

        return vendTable;
    }
}
```

**Usage in tests:**
```xpp
[SysTestMethodAttribute]
public static void testWithNewTest()
{
    VendTable vendTable = TestVendTable::newTest('VEND001', 'USD', 750000);
    vendTable.insert();

    // Test with high credit vendor
    assertFalse(VendComplianceValidator::validate(vendTable, ''), 'Should fail for high credit without code');
}
```

### Pattern 3: Shared Setup with `SysTestSetup`

When multiple test methods need the same base data, use `SysTestSetup` to create it once for the entire test class.

```xpp
class VendComplianceTest extends SysTestCase
{
    // Shared test data — created once for all test methods
    public void setUp()
    {
        VendTable vendTable;

        // Create a high-credit vendor
        vendTable.initValue();
        vendTable.AccountNum = 'HIGHCREDIT01';
        vendTable.Name = 'High Credit Vendor';
        vendTable.CreditMax = 750000;
        vendTable.insert();

        // Create a low-credit vendor
        vendTable.initValue();
        vendTable.AccountNum = 'LOWCREDIT01';
        vendTable.Name = 'Low Credit Vendor';
        vendTable.CreditMax = 100000;
        vendTable.insert();
    }

    [SysTestMethodAttribute]
    public static void testHighCreditVendor()
    {
        VendTable vendTable = VendTable::find('HIGHCREDIT01');
        assertFalse(VendComplianceValidator::validate(vendTable, ''), 'High credit vendor needs compliance code');
    }

    [SysTestMethodAttribute]
    public static void testLowCreditVendor()
    {
        VendTable vendTable = VendTable::find('LOWCREDIT01');
        assertTrue(VendComplianceValidator::validate(vendTable, ''), 'Low credit vendor does not need compliance code');
    }

    public void tearDown()
    {
        // Delete test vendors
        VendTable vendTable;
        while select vendTable
            where vendTable.AccountNum like 'TEST%'
               || vendTable.AccountNum like 'HIGHCREDIT%'
               || vendTable.AccountNum like 'LOWCREDIT%'
        {
            vendTable.delete();
        }
    }
}
```

### Pattern 4: Per-Method Setup (Isolated Tests)

For tests that need completely different data setups, create data within each test method. This provides maximum isolation but can be repetitive.

```xpp
[SysTestMethodAttribute]
public static void testIsolatedSetup()
{
    VendTable vendTable;

    // Create data specific to this test
    vendTable.initValue();
    vendTable.AccountNum = 'ISOLATED01';
    vendTable.CreditMax = 600000;
    vendTable.insert();

    // Test logic
    assertFalse(VendComplianceValidator::validate(vendTable, ''), 'Should fail');

    // Clean up
    vendTable.delete();
}
```

### Choosing Between Shared Setup and Per-Method Setup

| Factor | Shared Setup (`SysTestSetup`) | Per-Method Setup |
|---|---|---|
| **Speed** | Faster — data created once | Slower — data created per test |
| **Isolation** | Lower — tests share data | Higher — each test is independent |
| **Maintainability** | Easier — one setup method | More repetitive — each test creates its own data |
| **Test order dependency** | Higher — tests may depend on shared state | Lower — each test is self-contained |
| **Best for** | Tests that read the same base data | Tests that modify or delete shared data |

**Best practice:** Use shared setup for read-only test data. Use per-method setup for tests that modify or delete data.

## 19.4 Test Isolation and Data-Driven Testing

### `SysTestTransaction` — Test Isolation

For a test to be valuable, it must be reliable — passing or failing consistently independent of other tests. Use the `SysTestTransaction` attribute to control transaction behavior:

| TestTransactionMode | Description |
|---|---|
| `AutoRollback` | **Default.** All transactions roll back using SQL save points. No data persists. Best isolation. |
| `LegacyRollback` | All insert statements are tracked and deleted during cleanup. Inserts downgrade to row-by-row. Use for concurrency testing. |
| `LegacyRollbackWithUpdateTracking` | All update, delete, and insert statements are tracked and reverted. Slowest isolation level. |
| `None` | No isolation. Only for debugging — allows UI navigation of test-created data. |

```xpp
class VendComplianceTest extends SysTestCase
{
    [SysTestMethodAttribute]
    [SysTestTransaction(SysTestTransactionMode::AutoRollback)]
    public static void testComplianceValidation()
    {
        // All database changes in this test are automatically rolled back
        // No cleanup code needed
    }
}
```

### `SysTestRow` — Data-Driven Testing

Use `SysTestRow` (available in version 10.0.25+) to test multiple input values without creating multiple test methods:

```xpp
public class MathTests extends SysTestCase
{
    [SysTestMethod,
    SysTestRow(0, 0),
    SysTestRow(1, 1),
    SysTestRow(-1, 1),
    SysTestRow(4, 16),
    SysTestRow(-4, 16)]
    public static void squareTests(int _value, int _result)
    {
        int testResult = MyMath::square(_value);
        this.assertEquals(_result, testResult);
    }
}
```

Each row appears as a separate numbered test result (e.g., `squareTests#1`, `squareTests#2`). Use `SysTestRowInactive` to disable individual rows.

### Test Filtering Attributes

Use these attributes to filter and organize tests in builds and Visual Studio Test Explorer:

| Attribute | Purpose | Filterable in Test Console |
|---|---|---|
| `SysTestCategory` | Categorize tests (e.g., Nightly, CheckIn) | Yes |
| `SysTestPriority` | Assign priority (integer, method > class) | Yes |
| `SysTestOwner` | Assign test owner | No (Test Toolbox only) |
| `SysTestProperty` | Key-value property pairs | No (Test Toolbox only) |

```xpp
class VendComplianceTest extends SysTestCase
{
    [SysTestCategory('Nightly')]
    [SysTestPriority(1)]
    [SysTestOwner('dev-team')]
    [SysTestProperty('area', 'compliance')]
    [SysTestMethodAttribute]
    public static void testHighCreditCompliance()
    {
        // Test logic
    }
}
```

**Build pipeline filtering example:**
- Run only Nightly tests: `TestCategory=Nightly`
- Run only Priority 1 tests: `Priority=1`

---

## 19.4 Test Coverage Metrics in LCS

LCS provides built-in test coverage metrics that help you understand how much of your code is covered by automated tests.

### Coverage Tab in LCS

The **Coverage** tab in LCS shows:

- **Line coverage**: Percentage of code lines executed during test runs
- **Method coverage**: Percentage of methods called during test runs
- **Class coverage**: Percentage of classes with at least one test method
- **Assembly coverage**: Percentage of assemblies covered by tests

### Test Cases View

The **Test Cases** view in LCS provides:

- **Test case list**: All test methods organized by test class
- **Execution history**: When each test was last run and its result
- **Pass/Fail status**: Visual indicators of test outcomes
- **Duration**: How long each test takes to execute
- **Error details**: Full error messages and stack traces for failed tests

### Interpreting Coverage Metrics

| Coverage Level | Interpretation |
|---|---|
| **> 80%** | Excellent — most code paths are tested |
| **60–80%** | Good — core logic is well covered |
| **40–60%** | Moderate — important paths may be untested |
| **< 40%** | Low — significant gaps in test coverage |

**Important:** Coverage percentage alone is not a quality metric. A test that covers 80% of lines but doesn't test edge cases is less valuable than a test that covers 60% of lines with thorough edge case testing.

### Best Practices for Test Coverage

1. **Test edge cases** — boundary values, null inputs, empty collections, maximum values
2. **Test failure paths** — not just the happy path, but also error conditions
3. **Test security** — verify that users without the right permissions cannot access data
4. **Test integration points** — verify that external calls and event handlers work correctly
5. **Run tests in CI/CD** — automate test execution as part of the build pipeline
6. **Review coverage reports** — identify untested code paths and add tests for critical paths

---

## 19.5 Integration Testing with LCS Test Case Management

LCS provides a **Test Case Management** feature that integrates with the `SysTest` framework for end-to-end integration testing.

### Test Case Lifecycle

```
[1] Create test case in LCS
    │  - Define test steps, expected results, and test data
    │
[2] Associate test case with SysTest class
    │  - Map LCS test cases to SysTestMethod attributes
    │
[3] Execute tests in a test environment
    │  - Run tests manually or via CI/CD pipeline
    │
[4] Review results in LCS
    │  - Pass/Fail status, error details, screenshots
    │
[5] Promote to UAT and Production
    │  - Only promote when all test cases pass
```

### Creating Test Cases in LCS

1. Navigate to **Test Management** in LCS
2. Create a **Test Plan** for the release
3. Add **Test Cases** to the plan:
   - **Test Case Name**: Descriptive name (e.g., "Validate compliance code for high-credit vendors")
   - **Test Steps**: Step-by-step instructions
   - **Expected Result**: What should happen
   - **Test Data**: Any data needed for the test
   - **Associated Test Method**: The `SysTestMethod` that implements this test
4. Assign test cases to test environments

### Running Tests in LCS

Tests can be run in LCS through:

1. **Manual execution** — run tests from the LCS test case management UI
2. **CI/CD pipeline** — run tests automatically as part of the build pipeline
3. **Scheduled execution** — run tests on a schedule (e.g., nightly)

### Test Execution in CI/CD Pipeline

```yaml
# Azure DevOps pipeline step for running tests
- task: Dynamics365Test@1
  inputs:
    solution: '**/*.sln'
    testClasses: 'VendComplianceTest'
    configuration: 'Release'
    publishResults: true
```

When tests run in the CI/CD pipeline:
- Test results are published to LCS
- Failed tests block the deployment pipeline
- Coverage metrics are updated in LCS
- Test execution reports are available for audit

---

## 19.6 Activity — Write a Complete Test Class for Sales Order Discount Calculation

> **Activity**: Write a complete test class covering edge cases for sales order discount calculation. The discount calculation has the following rules:
> 1. Standard discount: 5% for orders over $10,000
> 2. VIP discount: 10% for VIP customers (CustGroup = 'VIP')
> 3. Volume discount: 15% for orders over $50,000
> 4. Combined discount: VIP + Volume discounts stack (VIP gets 10% + Volume gets 15% = 25% for orders over $50,000)
> 5. No discount for orders under $10,000 (unless VIP, which gets 10% regardless of order amount)
> 6. Maximum discount cap: 30% (no discount can exceed 30% of the order total)
>
> Write test methods covering:
> - Standard discount for orders over $10,000
> - VIP discount for orders under $10,000
> - VIP discount for orders over $50,000 (combined with volume)
> - Volume discount for non-VIP customers over $50,000
> - No discount for orders under $10,000 for non-VIP customers
> - Maximum discount cap (30%) is enforced
> - Edge case: exactly $10,000 order (boundary value)
> - Edge case: exactly $50,000 order (boundary value)
> - Edge case: order with $0 total
> - Edge case: negative order total (error handling)
>
> **Activity Hints** (Multiple Valid Test Data Setup Approaches):
>
> - **Hint A — Shared setup vs. per-method setup**: Option A1 — use `SysTestSetup` to create shared customer records (VIP and non-VIP) and reuse them across tests (recommended — efficient, consistent). Option A2 — use per-method setup for complete test isolation (valid but slower). Option A3 — use a hybrid — shared setup for read-only data (customers), per-method setup for order-specific data (valid and practical).
>
> - **Hint B — Test data creation**: Option B1 — use a `TestCustTable` class with `construct()` and `newTest()` factory methods (recommended — clean, reusable). Option B2 — create test data inline in each test method (simple but repetitive). Option B3 — use a test data builder pattern with method chaining (most flexible but most complex).
>
> - **Hint C — Edge case testing**: Option C1 — test boundary values explicitly ($10,000, $50,000, $0, negative) (recommended — boundary value analysis is a standard testing technique). Option C2 — use parameterized tests with a data table (more elegant but requires more framework support). Option C3 — test only the happy path and rely on manual testing for edge cases (not recommended — automated tests should cover edge cases).
>
> - **Hint D — Assertion strategy**: Option D1 — use `assertEquals` for exact value comparisons and `assertTrue`/`assertFalse` for boolean conditions (recommended — clear and explicit). Option D2 — use `assertGreater`/`assertLess` for range-based assertions (valid for discount percentage checks). Option D3 — use `assertException` for error cases (necessary for negative order total).

### Expected Approach (Ideal — in detail)

#### Test Data Setup with Shared `SysTestSetup`

```xpp
class SalesOrderDiscountTest extends SysTestCase
{
    // Shared test data — created once for all test methods
    public void setUp()
    {
        CustTable custTable;

        // Create VIP customer
        custTable.initValue();
        custTable.AccountNum = 'VIP001';
        custTable.Name = 'VIP Customer';
        custTable.CustGroup = 'VIP';
        custTable.insert();

        // Create standard customer
        custTable.initValue();
        custTable.AccountNum = 'STD001';
        custTable.Name = 'Standard Customer';
        custTable.CustGroup = 'STD';
        custTable.insert();
    }

    [SysTestMethodAttribute]
    public static void testStandardDiscount_Over10K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order over $10,000 for a standard customer
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 100;
        salesLine.LineAmount = 15000;  // Over $10,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — standard discount of 5%
        assertEquals(5, discountPercent, 'Standard discount should be 5% for orders over $10,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testVIPDiscount_Under10K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order under $10,000 for a VIP customer
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'VIP001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 10;
        salesLine.LineAmount = 5000;  // Under $10,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — VIP discount of 10% regardless of order amount
        assertEquals(10, discountPercent, 'VIP discount should be 10% even for orders under $10,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testVIPVolumeDiscount_Over50K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order over $50,000 for a VIP customer
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'VIP001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 500;
        salesLine.LineAmount = 60000;  // Over $50,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — combined VIP (10%) + Volume (15%) = 25%
        assertEquals(25, discountPercent, 'VIP + Volume discount should be 25% for orders over $50,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testVolumeDiscount_NonVIP_Over50K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order over $50,000 for a standard customer
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 500;
        salesLine.LineAmount = 60000;  // Over $50,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — volume discount of 15% only (no VIP)
        assertEquals(15, discountPercent, 'Volume discount should be 15% for non-VIP orders over $50,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testNoDiscount_Under10K_NonVIP()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order under $10,000 for a standard customer
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 5;
        salesLine.LineAmount = 5000;  // Under $10,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — no discount for non-VIP orders under $10,000
        assertEquals(0, discountPercent, 'No discount for non-VIP orders under $10,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testMaxDiscountCap_30Percent()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order that would exceed 30% discount
        // VIP (10%) + Volume (15%) + Special (10%) = 35% but capped at 30%
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'VIP001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 1000;
        salesLine.LineAmount = 100000;  // Over $50,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — discount capped at 30%
        assertLessOrEqual(discountPercent, 30, 'Discount should not exceed 30%');
        assertEquals(30, discountPercent, 'Discount should be capped at 30%');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testBoundaryValue_Exactly10K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order exactly at $10,000
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 100;
        salesLine.LineAmount = 10000;  // Exactly $10,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — standard discount of 5% applies at exactly $10,000 (boundary)
        assertEquals(5, discountPercent, 'Standard discount should apply at exactly $10,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testBoundaryValue_Exactly50K()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order exactly at $50,000
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 500;
        salesLine.LineAmount = 50000;  // Exactly $50,000
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — volume discount of 15% applies at exactly $50,000 (boundary)
        assertEquals(15, discountPercent, 'Volume discount should apply at exactly $50,000');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testZeroOrderTotal()
    {
        SalesTable salesTable;
        SalesLine salesLine;
        Real discountPercent;

        // Arrange — create a sales order with $0 total
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 0;
        salesLine.LineAmount = 0;  // Zero total
        salesLine.insert();

        // Act — calculate discount
        discountPercent = SalesOrderDiscount::calculateDiscount(salesTable);

        // Assert — no discount for $0 order
        assertEquals(0, discountPercent, 'No discount for $0 order');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    [SysTestMethodAttribute]
    public static void testNegativeOrderTotal_ThrowsError()
    {
        SalesTable salesTable;
        SalesLine salesLine;

        // Arrange — create a sales order with negative total
        salesTable = SalesTable::construct();
        salesTable.initValue();
        salesTable.CustomerAccount = 'STD001';
        salesTable.SalesDate = today();
        salesTable.insert();

        salesLine = SalesLine::construct();
        salesLine.initValue();
        salesLine.SalesTableId = salesTable.SalesId;
        salesLine.ItemId = 'ITEM001';
        salesLine.SalesQty = 1;
        salesLine.LineAmount = -5000;  // Negative total
        salesLine.insert();

        // Assert — should throw an error for negative order total
        assertException(
            classStr(SalesOrderDiscount),
            methodStr(SalesOrderDiscount, calculateDiscount),
            error::Error,
            'Should throw error for negative order total');

        // Cleanup
        salesLine.delete();
        salesTable.delete();
    }

    public void tearDown()
    {
        // Clean up all test data
        SalesLine salesLine;
        SalesTable salesTable;
        CustTable custTable;

        while select salesLine
            where salesLine.ItemId == 'ITEM001'
        {
            salesLine.delete();
        }

        while select salesTable
            where salesTable.CustomerAccount like 'VIP%'
               || salesTable.CustomerAccount like 'STD%'
        {
            salesTable.delete();
        }

        while select custTable
            where custTable.AccountNum like 'VIP%'
               || custTable.AccountNum like 'STD%'
        {
            custTable.delete();
        }
    }
}
```

#### Design Rationale

1. **Shared setup** creates VIP and standard customers once — all test methods reuse them
2. **Per-method cleanup** ensures each test leaves no residual data that could affect other tests
3. **Boundary value tests** ($10,000 exactly, $50,000 exactly) verify the discount thresholds work correctly at the boundaries
4. **Edge case tests** ($0 total, negative total) verify the system handles unusual inputs gracefully
5. **Combined discount test** (VIP + Volume) verifies that discounts stack correctly
6. **Maximum cap test** verifies that the 30% discount cap is enforced
7. **Error case test** uses `assertException` to verify that negative order totals are rejected

#### Model Manifest Dependencies

```xml
<ModelManifest>
  <Name>AcmeSalesOrderDiscountTests</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <References>
    <ModelReference><Name>ApplicationSuite</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
    <ModelReference><Name>ApplicationFoundation</Name><MinVersion>10.0.0.0</MinVersion></ModelReference>
  </References>
  <ConfigurationKey>AcmeSalesOrderDiscountTestsEnabled</ConfigurationKey>
</ModelManifest>
```

---

### Remaining Chapters — Detailed Outlines


# Chapter 20: LCS Deep Dive & CI/CD

## 20.1 Lifecycle Services (LCS) — Deep Dive

Lifecycle Services (LCS) is the central hub for managing the D365 F&O application lifecycle. It's a cloud-based portal that orchestrates everything from environment provisioning to deployment and monitoring.

### LCS Environment Tiers

| Tier | Purpose | VM Count | Typical Use |
|---|---|---|---|
| **Development** | Active development and testing | 1-2 AOS nodes | Developer work, feature development, unit testing |
| **Test/QA** | Integration and regression testing | 2 AOS nodes (HA) | Automated testing, UAT, integration testing |
| **Staging/Pre-Production** | Final validation before production | 2 AOS nodes (HA) | Performance testing, user acceptance, go-live validation |
| **Production** | Live, customer-facing environment | 2+ AOS nodes (HA) | Day-to-day business operations |
| **Demo** | Demonstrations and training | 1 AOS node | Sales demos, training sessions |

### LCS Project Structure

Every LCS project corresponds to a D365 F&O deployment. The project contains:

- **Environments**: All the VMs and services for the deployment
- **Deployment Pipelines**: The CI/CD pipeline configuration
- **Release Gates**: Approval checkpoints between environments
- **Build Artifacts**: NuGet packages and deployable packages
- **Monitoring**: SLA tracking, performance metrics, alerting
- **Application Lifecycle**: Version history, deployment history, incident tracking

### Environment Provisioning

Environments are provisioned through LCS and deployed to your Azure subscription:

1. **Create the project** in LCS with your Azure subscription details
2. **Select the topology** (Demo, Dev/Test, HA Production)
3. **Choose VM sizes** for each node type (AOS, Batch, Report, etc.)
4. **Configure networking** (VNets, subnets, NSGs)
5. **LCS provisions the VMs** and installs the D365 F&O binaries
6. **Initial sync** pulls the base application code from Microsoft

### Release Gates

Release gates control the flow of deployments between environments:

```
Dev → Test Gate → Staging Gate → Production Gate
  │         │           │              │
  ▼         ▼           ▼              ▼
 Deploy    Automated   Manual         Manual
 to Test   Test Run    Approval       Approval
```

**Gate Types:**

| Gate Type | Description | When It Applies |
|---|---|---|
| **Automated** | Deployment proceeds without human intervention | Dev → Test (for build validation) |
| **Manual Approval** | A designated approver must approve before deployment proceeds | Test → Staging, Staging → Production |
| **Scheduled** | Deployment occurs at a predetermined time | Production deployments during maintenance windows |

### Deployment Pipelines in LCS

LCS integrates with Azure DevOps for deployment orchestration:

1. **Build Pipeline** (Azure DevOps): Compiles the model project, creates a deployable package
2. **Release Pipeline** (Azure DevOps): Deploys the package to LCS environments
3. **LCS Deployment Orchestration**: LCS manages the actual deployment to the AOS nodes
4. **Post-Deployment Validation**: LCS runs health checks after deployment

---

## 20.2 Azure DevOps / GitHub Integration

### Build Pipeline (YAML)

The build pipeline compiles the X++ code, runs best practice checks, and creates a deployable package.

**Complete Build Pipeline YAML:**

```yaml
trigger:
  branches:
    include:
      - main
      - release/*

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'd36fo-build-variables'
  - name: buildPlatform
    value: 'Any CPU'
  - name: buildConfiguration
    value: 'Release'

steps:
  # Step 1: Install NuGet packages
  - task: NuGetCommand@2
    displayName: 'Restore NuGet packages'
    inputs:
      command: 'restore'
      feedsToUse: 'config'
      nugetConfigPath: 'nuget.config'

  # Step 2: Update model versions
  - task: PowerShell@2
    displayName: 'Update model versions'
    inputs:
      targetType: 'filePath'
      filePath: '$(Build.SourcesDirectory)/build/UpdateModelVersions.ps1'
      arguments: '-version $(Build.BuildNumber)'

  # Step 3: Build the solution
  - task: MSBuild@1
    displayName: 'Build D365 F&O solution'
    inputs:
      solution: '**/*.sln'
      platform: '$(buildPlatform)'
      configuration: '$(buildConfiguration)'
      msbuildArguments: >
        /p:BuildTasksDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage\DevAlm"
        /p:MetadataDirectory="$(Build.SourcesDirectory)\Metadata"
        /p:FrameworkDirectory="$(Pipeline.Workspace)\NuGets\Microsoft.Dynamics.AX.Platform.CompilerPackage"
        /p:ReferenceFolder="$(Pipeline.Workspace)\NuGets"
        /p:OutputDirectory="$(Build.BinariesDirectory)"

  # Step 4: Install NuGet 9.3.0 (required for deployable package generation)
  - task: NuGetCommand@2
    displayName: 'Install NuGet 9.3.0'
    inputs:
      command: 'install'
      feedsToUse: 'config'
      nugetConfigPath: 'nuget.config'
      versioning: 'specific'
      version: '9.3.0'

  # Step 5: Create deployable package
  - task: PowerShell@2
    displayName: 'Create deployable package'
    inputs:
      targetType: 'filePath'
      filePath: '$(Build.SourcesDirectory)/build/CreateDeployablePackage.ps1'
      arguments: '-outputPath "$(Build.ArtifactStagingDirectory)"'

  # Step 6: Publish the deployable package
  - task: PublishBuildArtifacts@1
    displayName: 'Publish deployable package'
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)'
      ArtifactName: 'drop'
      publishLocation: 'Container'
```

### Release Pipeline (YAML)

The release pipeline deploys the package to LCS environments:

```yaml
trigger: none

pr: none

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'd36fo-release-variables'

stages:
  - stage: DeployToTest
    displayName: 'Deploy to Test'
    jobs:
      - deployment: DeployTest
        environment: 'Test'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerShell@2
                  displayName: 'Deploy package to LCS'
                  inputs:
                    targetType: 'filePath'
                    filePath: '$(Pipeline.Workspace)/build/DeployToLCS.ps1'
                    arguments: >
                      -lcsProjectId "$(LcsProjectId)"
                      -environmentName "Test"
                      -packagePath "$(Pipeline.Workspace)/drop/*.zip"
                      -lcsToken "$(LcsAccessToken)"

  - stage: DeployToStaging
    displayName: 'Deploy to Staging'
    dependsOn: DeployToTest
    # Manual approval gate configured in Azure DevOps
    jobs:
      - deployment: DeployStaging
        environment: 'Staging'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerShell@2
                  displayName: 'Deploy package to LCS'
                  inputs:
                    targetType: 'filePath'
                    filePath: '$(Pipeline.Workspace)/build/DeployToLCS.ps1'
                    arguments: >
                      -lcsProjectId "$(LcsProjectId)"
                      -environmentName "Staging"
                      -packagePath "$(Pipeline.Workspace)/drop/*.zip"
                      -lcsToken "$(LcsAccessToken)"

  - stage: DeployToProduction
    displayName: 'Deploy to Production'
    dependsOn: DeployToStaging
    # Manual approval gate configured in Azure DevOps
    jobs:
      - deployment: DeployProduction
        environment: 'Production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerShell@2
                  displayName: 'Deploy package to LCS'
                  inputs:
                    targetType: 'filePath'
                    filePath: '$(Pipeline.Workspace)/build/DeployToLCS.ps1'
                    arguments: >
                      -lcsProjectId "$(LcsProjectId)"
                      -environmentName "Production"
                      -packagePath "$(Pipeline.Workspace)/drop/*.zip"
                      -lcsToken "$(LcsAccessToken)"
```

### Agent Pools

| Agent Pool | OS | Use Case |
|---|---|---|
| `windows-latest` | Windows Server 2022 | Build agents (compilation, packaging) |
| `ubuntu-latest` | Ubuntu 20.04 | Not used for D365 F&O builds (Windows required) |
| Self-hosted | Windows Server | On-premises builds with direct AOS access |

**Key Point:** Hosted build automation supports compilation and packaging only — no X++ unit testing (SysTest), database sync, or AOS-dependent features. For those, you need a self-hosted agent or a dedicated test environment.

---

## 20.3 Model Management

### Model Manifest (`ModelManifest.xml`)

The `ModelManifest.xml` file defines the model's identity, dependencies, and configuration:

```xml
<?xml version="1.0" encoding="utf-8"?>
<ModelManifest>
  <Name>AcmeOrderToCash</Name>
  <Version>1.0.0.0</Version>
  <Layer>CUS</Layer>
  <Description>Acme Order-to-Cash extension model</Description>
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
      <Name>ApplicationPlatform</Name>
      <MinVersion>10.0.0.0</MinVersion>
    </ModelReference>
  </References>
  <ConfigurationKey>AcmeOrderToCashEnabled</ConfigurationKey>
  <GeneratedBy>
    <Tool>Visual Studio</Tool>
    <Version>17.8.0</Version>
  </GeneratedBy>
</ModelManifest>
```

### Model Dependency Order

The model dependency order determines the **layer order** — which model's code takes precedence when there are conflicts:

```
Layer Order (highest → lowest):
  CUS (Customer) — Your customizations
  VAR (VAR/Partner) — Partner solutions
  ISV (ISV) — Independent software vendor solutions
  CUS (Custom) — Microsoft customizations (rarely used)
  ApplicationSuite — Application business logic
  ApplicationFoundation — Framework and shared services
  ApplicationPlatform — Core platform (interfaces, kernel)
```

**Critical Rule:** A model can only depend on models in lower layers. Circular dependencies are not allowed and will cause compilation errors.

### Model Versioning

Models use **semantic versioning** (`Major.Minor.Patch.Build`):

| Version Component | When to Increment | Example |
|---|---|---|
| **Major** | Breaking changes, major feature releases | `2.0.0.0` |
| **Minor** | New features, backward-compatible additions | `1.1.0.0` |
| **Patch** | Bug fixes, backward-compatible patches | `1.0.1.0` |
| **Build** | Internal build number, CI/CD increment | `1.0.0.1234` |

### `AxModelStore` — Model Management API

The `AxModelStore` class provides programmatic access to model management operations:

```xpp
// Get the model store instance
AxModelStore modelStore = AxModelStore::getModelStore();

// Get a model by name
AxModel model = modelStore->getModel('AcmeOrderToCash');

// Get all models in the store
AxModelCollection models = modelStore->getModels();

// Check model dependencies
AxModelDependencyCollection dependencies = model->getDependencies();
for (int i = 0; i < dependencies->size(); i++)
{
    AxModelDependency dependency = dependencies->get(i);
    info(strFmt('Depends on: %1 (v%2)', 
        dependency->getName(), 
        dependency->getVersion()));
}
```

---

## 20.4 Configuration Keys

Configuration keys control which features and modules are enabled in the D365 F&O instance. They act as feature flags at the model level.

### Standard Configuration Keys

| Key | Purpose | Default |
|---|---|---|
| `#ISO` | International Organization for Standardization features | Enabled |
| `#USMF` | United States Mexico Federal (demo company) | Enabled |
| `#CER` | Corporate Enterprise features | Disabled |
| `#RTI` | Real-Time Integration features | Disabled |
| `#GR` | General Ledger features | Enabled |
| `#AP` | Accounts Payable features | Enabled |
| `#AR` | Accounts Receivable features | Enabled |
| `#IN` | Inventory Management features | Enabled |
| `#PM` | Project Management features | Disabled |

### Custom Configuration Keys

When you create custom features, you should define a custom Configuration Key:

**Step 1: Create the Configuration Key in the AOT**

1. In Visual Studio, right-click your model → **New** → **Configuration Key**
2. Set the **Name** (e.g., `AcmeOrderToCashEnabled`)
3. Set the **Label** (e.g., "Acme Order-to-Cash Module")
4. Set the **Configuration Key Group** (e.g., "Order Management")

**Step 2: Reference the Configuration Key in Code**

```xpp
// Check if the feature is enabled before executing custom logic
if (isConfigurationKeySet(configurationKeyNum(AcmeOrderToCashEnabled)))
{
    // Custom Order-to-Cash logic here
    this.processOrderToCash();
}
else
{
    info('Acme Order-to-Cash module is not enabled.');
}
```

**Step 3: Reference the Configuration Key in Table Properties**

On any custom table, set the **Configuration Key** property to your custom key. This ensures the table is only created in databases where the feature is enabled.

### Configuration Key Best Practices

1. **Group related features** under a single configuration key (e.g., `AcmeComplianceEnabled` for all compliance features)
2. **Use descriptive names** that clearly indicate what the key controls
3. **Document every key** in the model's README with its purpose and default state
4. **Test with keys both enabled and disabled** to ensure graceful degradation
5. **Never hard-code feature flags** — always use `isConfigurationKeySet()` for runtime checks

---

## 20.5 Hotfix Deployment Strategy

Hotfixes (CUs — Cumulative Updates) are Microsoft's mechanism for delivering fixes and updates to D365 F&O. Understanding how they are applied is critical for maintaining a stable production environment.

### The `.axupdate` File

Hotfixes are distributed as `.axupdate` files (also called application update packages). Each `.axupdate` file contains:

- **Metadata**: The update version, target model versions, and dependencies
- **X++ Code**: The updated X++ source files
- **Metadata**: Updated table definitions, forms, reports, etc.
- **Database Scripts**: SQL scripts for schema changes

### Application Order

Hotfixes must be applied in a specific order:

```
1. Platform Update (PU) — Updates the Application Platform layer
2. Application Update 1 (AU1) — Updates Application 1
3. Application Update 2 (AU2) — Updates Application 2
4. Application Suite Update (ASU) — Updates Application Suite
5. Custom Model Updates — Your custom models (if applicable)
```

**Critical Rule:** You must apply updates in dependency order. A Platform Update must be applied before any Application Update that depends on it.

### Dependency Ordering

```
ApplicationPlatform (PU)
    └── ApplicationFoundation (AU1)
            └── ApplicationSuite (AU2)
                    └── Custom Models (CUS)
```

### Hotfix Deployment Process

1. **Download the `.axupdate` file** from LCS (Life Cycle Services)
2. **Validate the update** — check version compatibility and dependencies
3. **Backup the environment** — take a snapshot of the current state
4. **Apply the update** through LCS deployment orchestration
5. **Run database sync** — synchronize the database schema with the updated metadata
6. **Compile the model** — ensure all code compiles successfully
7. **Run post-deployment validation** — verify the update was applied correctly
8. **Monitor for issues** — check LCS monitoring dashboards and Infolog

### Rollback Strategy

If a hotfix causes issues:

1. **Identify the issue** — check LCS monitoring, Infolog, and batch job history
2. **Revert the update** — LCS supports rollback to the previous package version
3. **Restore from backup** if the rollback fails
4. **Document the issue** — file a support ticket with Microsoft

---

## 20.6 CI/CD Pipeline Design — Complete Pattern

### The Full Pipeline

```
[Source Control] → [Build] → [Test] → [Deploy to Dev] → [Deploy to Test] → [Deploy to Staging] → [Deploy to Production]
     │                  │          │          │               │                │                 │
  Git/TFS         Compile     SysTest     Deploy          Automated       Manual           Manual
                  + PB      (if             package         test run        approval         approval
                  check     supported)      deploy          + regression    gate             gate
```

### Pipeline Stages in Detail

#### Stage 1: Build

| Step | Action | Success Criteria |
|---|---|---|
| 1.1 | Restore NuGet packages | All 5 packages restored successfully |
| 1.2 | Update model versions | Version incremented to build number |
| 2.1 | Compile the solution | Zero compilation errors |
| 3.1 | Run best practice checks | No critical best practice violations |
| 3.2 | Create deployable package | `.zip` package created and published |

#### Stage 2: Test

| Step | Action | Success Criteria |
|---|---|---|
| 5.1 | Deploy package to test environment | Deployment successful |
| 5.2 | Run database sync | No sync errors |
| 6.1 | Run SysTest unit tests | All tests pass (or acceptable failure rate) |
| 6.2 | Run regression test suite (RSAT) | No regressions detected |
| 7.1 | Validate custom functionality | Manual verification of key scenarios |

#### Stage 3: Deploy to Staging

| Step | Action | Success Criteria |
|---|---|---|
| 9.1 | Manual approval gate | Approved by release manager |
| 9.2 | Deploy package to staging | Deployment successful |
| 9.3 | Run performance tests | Response times within acceptable thresholds |
| 9.4 | Run user acceptance testing | UAT sign-off obtained |
| 9.5 | Validate security roles | Permission simulation passes for all roles |

#### Stage 4: Deploy to Production

| Step | Action | Success Criteria |
|---|---|---|
| 10.1 | Manual approval gate | Approved by release manager and business owner |
| 10.2 | Schedule deployment window | Outside business hours |
| 10.3 | Deploy package to production | Deployment successful |
| 10.4 | Run database sync | No sync errors |
| 10.5 | Run post-deployment validation | All health checks pass |
| 4.6 | Monitor for issues | No critical errors in Infolog or LCS |

### Rollback Strategy

| Scenario | Rollback Action | Time to Rollback |
|---|---|---|
| Deployment fails at build stage | No rollback needed — pipeline stops | N/A |
| Deployment fails at test stage | Redeploy previous package to test | < 15 minutes |
| Deployment fails at staging | Redeploy previous package to staging | < 15 minutes |
| Deployment fails at production | Redeploy previous package to production | < 30 minutes |
| Issue discovered after production deployment | Rollback to previous package via LCS | < 1 hour |

### Activity — Design a Complete CI/CD Pipeline

> **Activity**: Design a complete CI/CD pipeline for a D365 F&O project that includes:
> 1. Build automation with Azure DevOps YAML pipelines
> 2. Test execution (SysTest unit tests + RSAT regression tests)
> 3. Configuration key documentation for all custom features
> 4. Release gates between environments
> 5. Rollback strategy for each environment
>
> **Requirements:**
> - The pipeline must support dev → test → staging → production flow
> - Each environment must have appropriate approval gates
> - The build pipeline must produce a deployable package
> - Test execution must include both automated and manual steps
> - Rollback must be documented for each environment
>
> **Activity Hints:**
> - **Hint A — Pipeline tool choice**: Option A1 — Azure DevOps with YAML pipelines (recommended — industry standard, version-controlled pipeline definition). Option A2 — GitHub Actions with workflow YAML (valid — simpler for smaller teams). Option A3 — Azure DevOps with classic designer pipelines (valid but less maintainable — no version control for pipeline definition).
> - **Hint B — Test execution strategy**: Option B1 — Run SysTest in the build pipeline (ideal but not supported by hosted agents — requires self-hosted agents). Option B2 — Run RSAT regression tests in the test environment deployment stage (recommended — works with hosted agents). Option B3 — Manual test execution with test plans in Azure DevOps Test Plans (valid for smaller teams without automated test infrastructure).
> - **Hint C — Rollback approach**: Option C1 — Redeploy the previous package via LCS (recommended — clean and reliable). Option C2 — Database restore from backup (nuclear option — use only if redeployment fails). Option C3 — Feature flags via ConfigurationKeys to disable problematic features without rollback (complementary approach — not a replacement for redeployment).

---

## 20.7 Model Deployment with `AxModelStore`

### Deploying Models Programmatically

You can deploy models programmatically using the `AxModelStore` API:

```xpp
// Deploy a model to the local AOS
AxModelStore modelStore = AxModelStore::getModelStore();

// Get the model to deploy
AxModel model = modelStore->getModel('AcmeOrderToCash');

// Check if the model is already deployed
if (model->getDeploymentState() == AxModelDeploymentState::Deployed)
{
    info('Model is already deployed.');
}
else
{
    // Deploy the model
    AxModelDeploymentResult result = model->deploy();
    
    if (result->getStatus() == AxModelDeploymentStatus::Success)
    {
        info('Model deployed successfully.');
    }
    else
    {
        error(strFmt('Model deployment failed: %1', result->getErrorMessage()));
    }
}
```

### Synchronizing the Database After Deployment

After deploying a model, you must synchronize the database to create or update the corresponding database tables:

```xpp
// Sync the database after model deployment
SysSetupStorage::syncDatabase();

// Or sync a specific table
SysTableSync::syncTable(tableNum(CustTable));
```

### Checking Model Compilation Status

```xpp
// Check if a model compiles successfully
AxModelBuildResult buildResult = model->build();

if (buildResult->getStatus() == AxModelBuildStatus::Success)
{
    info('Model compiled successfully.');
}
else
{
    // Get compilation errors
    AxModelBuildErrorCollection errors = buildResult->getErrors();
    for (int i = 0; i < errors->size(); i++)
    {
        AxModelBuildError error = errors->get(i);
        error(strFmt('Error in %1: %2', error->getSource(), error->getMessage()));
    }
}
```

---

## 20.8 Activity — Complete Deployment Strategy

> **Activity**: Design a complete deployment strategy for a D365 F&O project that includes:
> 1. LCS project setup with environment tiers
> 2. Azure DevOps build and release pipelines
> 3. Model versioning and dependency management
> 4. Configuration key documentation
> 5. Hotfix application process
> 6. Rollback procedures for each environment
>
> **Activity Hints:**
> - **Hint A — Environment topology**: Option A1 — Dev + Test + Staging + Production (recommended — follows Microsoft's recommended topology). Option A2 — Dev + Test + Production (simpler — valid for smaller deployments). Option A3 — Dev + Test + Staging + Pre-Production + Production (most granular — useful for large enterprise deployments with strict change management).
> - **Hint B — Deployment frequency**: Option B1 — Weekly deployments to Test, monthly to Production (recommended — balances velocity with stability). Option B2 — Daily deployments to Test, weekly to Production (faster cadence — requires robust automated testing). Option B3 — Monthly deployments to all environments (conservative — suitable for regulated industries).
> - **Hint C — Hotfix handling**: Option C1 — Apply hotfixes to Test first, then promote to Production after validation (recommended — follows the same path as custom code). Option C2 — Apply hotfixes directly to Production (Microsoft's recommended approach for critical security fixes — but skip validation). Option C3 — Apply hotfixes to Staging first, then Test, then Production (most conservative — useful for compliance-heavy environments).

---


# Chapter 21: Performance & SQL Tuning

## 21.1 SQL Query Optimization

### The `exists join` vs `join` Decision

One of the most impactful performance optimizations in X++ is choosing the right join type:

```xpp
// ❌ SLOW — join retrieves all columns from both tables
CustTable custTable;
VendTable vendTable;

while select custTable
    join vendTable
    where vendTable.AccountNum == custTable.AccountNum
{
    // Process each matching pair
}

// ✅ FAST — exists join only checks for existence, doesn't retrieve data
CustTable custTable;
VendTable vendTable;

while select custTable
    exists join vendTable
    where vendTable.AccountNum == custTable.AccountNum
{
    // Process each customer that has a matching vendor
}
```

### When to Use Each Join Type

| Join Type | Use When | Performance |
|---|---|---|
| `join` | You need columns from both tables | Moderate — retrieves all joined data |
| `exists join` | You only need to check if related records exist | Fast — stops at first match |
| `noexists join` | You need records that have NO related records | Fast — inverse of exists join |
| `cross join` | You need every combination of rows | Very slow — avoid in production code |
| `outer join` | You need all records from one table even without matches | Moderate — retrieves unmatched rows |

### `RecordCount` Performance

The `recordCount()` method can be expensive on large tables:

```xpp
// ❌ SLOW — recordCount() executes a full COUNT query
CustTable custTable;
int count = custTable.recordCount();  // Full table scan

// ✅ FAST — use a select with countRecId()
CustTable custTable;
int count;

select countRecId(custTable);  // Uses SQL COUNT(RecId) — optimized
```

### `countRecId` vs `recordCount`

| Method | SQL Generated | Performance | Use When |
|---|---|---|---|
| `recordCount()` | `SELECT COUNT(*) FROM table` | Slow on large tables — full scan | Small tables only |
| `countRecId()` | `SELECT COUNT(RecId) FROM table` | Fast — uses clustered index | Large tables |
| `select countRecId(table)` | `SELECT COUNT(RecId) FROM table` | Fastest — optimized by SQL Server | Best practice for counting |

### Implicit Conversion Performance Trap

One of the most common performance issues is implicit data type conversion, which prevents SQL Server from using indexes:

```xpp
// ❌ SLOW — str to int implicit conversion prevents index usage
CustTable custTable;

while select custTable
    where custTable.AccountNum == strFmt("%1", someIntValue)
// SQL Server must convert AccountNum (string) to int for each row — no index usage

// ✅ FAST — explicit type matching allows index usage
CustTable custTable;
str accountNum = strFmt("%1", someIntValue);

while select custTable
    where custTable.AccountNum == accountNum;
// SQL Server uses the index on AccountNum directly
```

---

## 21.2 AOT Performance Anti-Patterns

### Anti-Pattern 1: Heavy `init()` Method

The `init()` method runs every time a form is opened. Putting heavy queries or data retrieval in `init()` causes slow form loads:

```xpp
// ❌ ANTI-PATTERN — Heavy query in init()
public void init()
{
    super();
    
    // This query runs EVERY time the form is opened
    // Even when the user is just viewing a single record
    CustTable custTable;
    while select custTable
        where custTable.CreditMax > 100000
    {
        // Processing logic that runs on every form open
        this.processCustomer(custTable);
    }
}

// ✅ CORRECT — Move heavy processing to a button or event
public void clicked()
{
    super();
    // Heavy processing only runs when the user clicks the button
    this.processHighCreditCustomers();
}
```

### Anti-Pattern 2: Complex Lookups in `active()`

The `active()` method runs every time a form record changes. Complex lookups in `active()` cause the form to feel sluggish:

```xpp
// ❌ ANTI-PATTERN — Complex lookup in active()
public void active()
{
    super();
    
    // This lookup runs every time the user moves to a different record
    // and makes the form feel slow
    CustTable custTable = element.args().record();
    SysTableLookup sysTableLookup = SysTableLookup::newParameters(tableNum(CustTable), custTableControl);
    sysTableLookup.addLookupField(fieldNum(CustTable, AccountNum));
    sysTableLookup.addLookupField(fieldNum(CustTable, Name));
    sysTableLookup.addLookupField(fieldNum(CustTable, CreditMax));
    sysTableLookup.performFormLookup();
}

// ✅ CORRECT — Use a simple lookup or set the lookup at design time
// The lookup should be set on the control's Lookup method, not in active()
```

### Anti-Pattern 3: Recursive `super()` Calls

Calling `super()` in a method that also calls the same method on related records can create deep recursion:

```xpp
// ❌ ANTI-PATTERN — Recursive super() calls
public void updateRelatedRecords()
{
    super();  // Calls base implementation
    
    // This calls updateRelatedRecords() on related records,
    // which in turn calls super() and processes THEIR related records
    // This can cause stack overflow on deep relationship chains
    CustTable relatedCust;
    while select relatedCust
        where relatedCust.ParentAccountNum == this.AccountNum
    {
        relatedCust.updateRelatedRecords();  // Recursive!
    }
}

// ✅ CORRECT — Use a batch job or iterative approach
class UpdateRelatedRecordsBatch extends RunBaseBatch
{
    public void run()
    {
        // Process related records iteratively in a batch job
        // No recursion — processes one level at a time
    }
}
```

### Anti-Pattern 4: `while select` with `firstonly` Mismatch

Using `while select` when you only need one record:

```xpp
// ❌ SLOW — while select retrieves ALL matching records
CustTable custTable;
while select custTable
    where custTable.AccountNum == "CUST-001"
{
    // Only the first record is needed, but all are retrieved
    break;  // Breaking after first iteration is a workaround, not a fix
}

// ✅ FAST — firstonly stops after the first match
CustTable custTable;
select firstonly custTable
    where custTable.AccountNum == "CUST-001";
```

---

## 21.3 Infolog Management Best Practices

The Infolog is the primary feedback mechanism for users. Managing it well is critical for a good user experience.

### Infolog Message Types

| Type | Method | User Impact | Use When |
|---|---|---|---|
| **Info** | `info()` | Green checkmark — informational | Process completed successfully |
| **Warning** | `warning()` | Yellow triangle — caution | Non-critical issue, operation can continue |
| **Error** | `error()` | Red X — blocks operation | Critical issue, operation must stop |
| **CheckFailed** | `checkFailed()` | Yellow triangle — validation failure | Field validation failed |

### Infolog Best Practices

1. **Be specific** — include the record ID and field name in error messages
2. **Use `checkFailed()` for field-level validation** — it highlights the specific field that failed
3. **Avoid `info()` in loops** — thousands of info messages will overwhelm the user
4. **Use `warning()` for non-critical issues** — don't block the user for minor issues
5. **Group related messages** — use a single `info()` with a summary rather than multiple messages

```xpp
// ❌ BAD — too many messages in a loop
CustTable custTable;
while select custTable
    where custTable.CreditMax > 100000
{
    info(strFmt("Customer %1 has high credit limit", custTable.AccountNum));
    // Thousands of messages — user can't find the important ones
}

// ✅ GOOD — summary message
CustTable custTable;
int highCreditCount;

while select custTable
    where custTable.CreditMax > 100000
{
    highCreditCount++;
}

info(strFmt("Found %1 customers with high credit limits.", highCreditCount));
```

---

## 21.4 Diagnosing Slow Forms

### Using `SysPerformance`

The `SysPerformance` class provides built-in performance measurement:

```xpp
// Measure the execution time of a code block
SysPerformance perf = new SysPerformance();
perf.startTimer();

// The code you want to measure
CustTable custTable;
while select custTable
    where custTable.CreditMax > 100000
{
    // Processing logic
}

perf.stopTimer();
info(strFmt('Execution time: %1 ms', perf.getElapsedTime()));
```

### SQL Trace

Use SQL Server Profiler or Extended Events to trace the SQL queries generated by X++ code:

1. Open SQL Server Profiler
2. Connect to the D365 F&O SQL Server instance
3. Create a trace with the `SQL:BatchStarting` and `SQL:BatchCompleted` events
4. Filter by the AOS process ID or database name
5. Run the slow operation in F&O
6. Analyze the trace to identify slow queries

### AOT Call Stack Profiling

The AOT provides a call stack view that shows the execution path of X++ code:

1. Set a breakpoint in Visual Studio
2. Run the operation that's slow
3. When the breakpoint hits, open the **Call Stack** window
4. Look for methods that are called repeatedly or take long to execute
5. Identify the bottleneck and optimize it

### Common Slow Form Patterns

| Pattern | Cause | Solution |
|---|---|---|
| Form loads slowly on open | Heavy `init()` method | Move processing to a button or event handler |
| Grid loads slowly | Missing index on sort column | Add index on the sort field |
| Lookup opens slowly | Complex query with joins | Simplify the lookup query, add indexes |
| Form is slow after navigation | Complex `active()` method | Simplify or move logic out of `active()` |
| Report takes >10 minutes | Large dataset in memory | Switch to TempDB pre-processing |
| Batch job runs slowly | Missing index on WHERE clause | Add index on filtered columns |

---

## 21.5 Memory Management

### Large Recordset `while select` Patterns

Processing large recordsets in memory can cause memory pressure and performance issues:

```xpp
// ❌ SLOW — loads all records into memory at once
CustTable custTable;
int totalCredit = 0;

while select custTable
    where custTable.CreditMax > 0
{
    totalCredit += custTable.CreditMax;  // All records held in memory
}

// ✅ FAST — processes records one at a time with minimal memory
CustTable custTable;
int totalCredit = 0;

while select custTable
    where custTable.CreditMax > 0
{
    totalCredit += custTable.CreditMax;
    // Record is released after each iteration
}
```

### `Global::objType` for Type Checking

When you need to check the type of a `Common` record, use `Global::objType()` instead of `is` or `as` casts:

```xpp
// ❌ SLOW — type checking with as cast
Common record = ...;
if (record is CustTable)
{
    CustTable custTable = record as CustTable;
    // Process custTable
}

// ✅ FAST — type checking with Global::objType
Common record = ...;
if (Global::objType(record) == Types::Class)
{
    // Use the record directly
}
```

### `GC.Collect` Considerations

In rare cases where large objects are created and destroyed in a loop, forcing garbage collection can help:

```xpp
// Use GC.Collect sparingly — it's a last resort
static void processLargeDataset()
{
    for (int i = 0; i < 10000; i++)
    {
        // Process each item
        // ...
        
        // Force GC every 1000 iterations to prevent memory buildup
        if (i % 1000 == 0)
        {
            System.GC::Collect();
        }
    }
}
```

**Warning:** `GC.Collect()` is expensive and should only be used as a last resort. The .NET garbage collector is designed to manage memory automatically. Use it only when you've identified a memory pressure issue through profiling.

---

## 21.6 Activity — Diagnose and Optimize a Slow Form

> **Activity**: A form called `CustomerCreditSummary` takes 45+ seconds to load when there are 50,000+ customer records. Diagnose the root cause and propose three different optimization strategies with comparisons.
>
> **Scenario Details:**
> - The form displays a grid of customers with their credit limits, outstanding balances, and compliance status
> - The form has a `CustTable` data source with several related data sources
> - The `init()` method runs a complex query that joins `CustTable`, `CustGroup`, `APComplianceLog`, and `VendTable`
> - The `active()` method runs a lookup to populate a compliance status field
> - The form has a custom `executeQuery()` method that adds ranges programmatically
>
> **Three Optimization Proposals:**
>
> **Proposal 1: Optimize the `init()` query**
> - Remove the complex join from `init()` and move it to a background thread
> - Add indexes on the join columns (`CustGroup`, `APComplianceLog`)
> - Use `firstonly` where only one record is needed
> - **Expected improvement**: 45s → 15s (67% faster)
> - **Trade-off**: Initial load is faster but the compliance status may not be immediately available
>
> **Proposal 2: Simplify the `active()` lookup**
> - Replace the `SysTableLookup` in `active()` with a simple field assignment
> - Cache the compliance status in a member variable
> - Use an event handler to update the status when the record changes
> - **Expected improvement**: 45s → 8s (82% faster)
> - **Trade-off**: The compliance status lookup is less flexible but much faster
>
> **Proposal 3: Use TempDB for the data source**
> - Pre-load the customer data into a TempDB table on form open
> - The grid reads from TempDB instead of the live tables
> - Use a background job to refresh the TempDB data periodically
> - **Expected improvement**: 45s → 3s (93% faster)
> - **Trade-off**: The data may be slightly stale between refreshes, but the form is much more responsive
>
> **Activity Hints:**
> - **Hint A — Root cause identification**: Option A1 — The `init()` query is the primary bottleneck (most likely — complex joins in `init()` are the #1 cause of slow form loads). Option A2 — The `active()` lookup is the primary bottleneck (possible — if the lookup runs on every record navigation). Option A3 — Missing indexes on join columns (possible — check the SQL execution plan). Option A4 — Multiple root causes combined (most realistic — in practice, slow forms usually have multiple contributing factors).
> - **Hint B — Optimization strategy**: Option B1 — Fix the `init()` query first (recommended — highest impact, lowest risk). Option B2 — Fix the `active()` lookup second (good — addresses the second most common cause). Option B3 — Use TempDB for the data source (advanced — best for very large datasets but adds complexity).
> - **Hint C — Validation approach**: Option C1 — Measure before and after with `SysPerformance` (recommended — data-driven). Option C2 — Ask users to subjectively rate the form speed (valid but less precise). Option C3 — Use SQL Server Profiler to trace the queries (most accurate — shows exactly what SQL is being generated).

---


# Chapter 22: Capstone Projects

## 22.1 Business Case: Manufacturing Procurement-to-Pay Compliance

### Scenario Overview

Acme Manufacturing needs a custom compliance tracking system for their procurement-to-pay process. The system ensures that all purchase orders meet regulatory and internal compliance requirements before payment is processed.

### Requirements

1. **Custom Table**: `POComplianceHeader` and `POComplianceLine` to track compliance checks on purchase orders
2. **Form**: `POComplianceForm` for entering and reviewing compliance data
3. **Custom Lookup**: Lookup to supplier compliance records when entering PO lines
4. **SSRS Report**: `POComplianceReport` for compliance summary and audit trail
5. **Batch Job**: Weekly compliance audit that checks all open POs for compliance gaps
6. **Data Entity**: `POComplianceEntity` for pushing compliance data to an external audit system
7. **Security Model**: Roles and duties for compliance officers, AP clerks, and managers
8. **Chain of Command**: Override on PO workflow to add compliance check before approval
9. **Event Handler**: On `PurchTable` to trigger compliance check when a PO is created

### Architecture Overview

```
[Purchase Order Created]
        │
        ▼
[Event Handler: PurchTable::created]
        │
        ▼
[Compliance Check: POComplianceService]
        │
        ├── Compliant → PO proceeds to approval workflow
        │
        └── Non-Compliant → PO blocked, compliance form opened
                              │
                              ▼
                     [User resolves compliance issue]
                              │
                              ▼
                     [Compliance check re-run]
                              │
                              ▼
                     [PO proceeds to approval]

[Weekly Batch Job: POComplianceAudit]
        │
        ▼
[Scan all open POs for compliance gaps]
        │
        ▼
[Generate compliance report (SSRS)]
        │
        ▼
[Push data to external audit system (Data Entity)]
```

---

## 22.2 Decision Points

### Decision 1: Table Design — Staging Table or Direct Insert?

**Question**: Should compliance data be written directly to the target table, or should it go through a staging table first?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **Direct Insert** | Simpler code, fewer tables | No validation before commit, harder to audit | ❌ Not recommended |
| **Staging Table** | Validation before commit, audit trail, error handling | More complex, extra table | ✅ Recommended |
| **TempDB Table** | Fast, no persistence | No audit trail, lost on restart | ❌ Not for compliance data |

**Rationale**: Compliance data requires an audit trail and validation before commit. The staging pattern ensures that invalid data is caught before it reaches the target table, and errors are logged with context.

### Decision 2: Form Pattern — ListPage + Detail or Single Form?

**Question**: Should the compliance form use a ListPage + Detail pattern or a single form?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **ListPage + Detail** | Standard F&O pattern, scalable for large datasets | More complex to build | ✅ Recommended |
| **Single Form** | Simpler to build, good for small datasets | Doesn't scale, non-standard pattern | ❌ Not for production |
| **Task Page** | Wizard-style, guided workflow | Not suitable for data review | ❌ Not for this scenario |

**Rationale**: The ListPage + Detail pattern is the standard F&O pattern for data review and editing. It scales well for large datasets and provides a familiar user experience.

### Decision 3: Report Design — SSRS or Power BI?

**Question**: Should the compliance report be an SSRS paginated report or a Power BI dashboard?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **SSRS Report** | Pixel-perfect, printable, standard F&O pattern | Static, requires report designer | ✅ Recommended for audit reports |
| **Power BI Dashboard** | Interactive, real-time, visual | Requires Power BI license, not printable | ✅ Recommended for operational dashboards |
| **Both** | Covers both use cases | More development effort | ✅ Best option if budget allows |

**Rationale**: SSRS is the standard for printable audit reports. Power BI is better for interactive operational dashboards. Both serve different purposes and should be used together.

### Decision 4: Batch Job — RunBaseBatch or SysOperation?

**Question**: Should the weekly compliance audit use RunBaseBatch or SysOperation?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **RunBaseBatch** | Familiar pattern, dialog for parameters | Legacy framework, less integration | ✅ Recommended for batch jobs with user input |
| **SysOperation** | Modern framework, Process Automation integration | More complex setup | ✅ Recommended for scheduled/recurring operations |
| **SysOperation wrapping RunBaseBatch** | Best of both worlds | Most complex | ✅ Recommended for production |

**Rationale**: The SysOperation framework provides better integration with Process Automation and scheduled execution. Wrapping the RunBaseBatch with SysOperation gives the best of both worlds — user input via dialog and scheduled execution via the service controller.

### Decision 5: Data Entity — Staging Pattern or Direct Write-Back?

**Question**: Should the data entity use the staging pattern for write-back, or direct write-back?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **Staging Pattern** | Validation, error handling, audit trail | More complex, extra table | ✅ Recommended for compliance data |
| **Direct Write-Back** | Simpler, fewer tables | No validation, no audit trail | ❌ Not for compliance data |
| **Read-Only Entity** | Simple, no write-back complexity | Cannot push data to external system | ❌ Not if write-back is required |

**Rationale**: Compliance data pushed to an external audit system must be validated and auditable. The staging pattern ensures data integrity and provides an audit trail.

### Decision 6: Security Model — Three Duties or Two?

**Question**: Should the security model use three duties (Viewer, Processor, Admin) or two (ReadWrite, Admin)?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **Three Duties** | Clear separation of concerns, SOX-compliant | More complex to design and maintain | ✅ Recommended for production |
| **Two Duties** | Simpler, easier to maintain | Less granular, may not satisfy SOX | ❌ Not for regulated environments |
| **Four Duties** | Maximum granularity | Overly complex for most scenarios | ❌ Unless compliance requirements demand it |

**Rationale**: Three duties provide clear separation of concerns and satisfy SOX compliance requirements. The Viewer duty allows read-only access, the Processor duty allows data entry and editing, and the Admin duty provides full control.

### Decision 7: CoC vs. Event Handler for PO Workflow

**Question**: Should the compliance check on the PO workflow use Chain of Command or an Event Handler?

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| **Chain of Command** | Wraps the standard method, standard logic still runs | Tightly coupled to the base method | ✅ Recommended for workflow integration |
| **Event Handler** | Decoupled, multiple subscribers possible | No control over execution order | ❌ Not for workflow integration |
| **Delegate** | Lightweight, callback pattern | No flow control | ❌ Not for this scenario |

**Rationale**: Chain of Command is the right choice for workflow integration because it wraps the standard method and ensures the standard approval logic still runs. The compliance check is additive — it adds a gate before the standard approval process.

---

## 22.3 Ideal Solution Walkthrough

### Step 1: Create the Custom Tables

```xpp
table 50100 POComplianceHeader
{
    DataClassification = CustomerContent;
    Storage = InMemory;

    fields
    {
        field(1; RecId; int64) { }
        field(2; POId; Code[20]) { }
        field(3; PurchTableRecId; int64) { }
        field(4; ComplianceStatus; Enum POComplianceStatus) { }
        field(5; CheckedBy; UserId) { }
        field(6; CheckedDate; UtcDateTime) { }
        field(7; Notes; Text[250]) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_POId; POId) { }
    }
}

table 50101 POComplianceLine
{
    DataClassification = CustomerContent;
    Storage = InMemory;

    fields
    {
        field(1; RecId; int64) { }
        field(2; POComplianceHeaderRecId; int64) { }
        field(3; LineNumber; int) { }
        field(4; Requirement; Enum POComplianceRequirement) { }
        field(5; Status; Enum POComplianceLineStatus) { }
        field(6; CheckedBy; UserId) { }
        field(7; Notes; Text[250]) { }
    }

    keys
    {
        key(PK; RecId) { Clustered = true; }
        key(IX_HeaderLine; POComplianceHeaderRecId, LineNumber) { }
    }
}
```

### Step 2: Create the Compliance Service Class

```xpp
class POComplianceService
{
    /// <summary>
    /// Check compliance for a purchase order.
    /// Returns true if the PO passes all compliance checks.
    /// </summary>
    public static boolean checkCompliance(PurchTable _purchTable)
    {
        POComplianceHeader complianceHeader;
        boolean allCompliant = true;

        // Check each compliance requirement
        // Requirement 1: Vendor must be approved
        if (!_purchTable.VendTable.Approved)
        {
            allCompliant = false;
            // Log non-compliance
        }

        // Requirement 2: Credit limit must not be exceeded
        if (_purchTable.AmountCurCredit > _purchTable.VendTable.CreditMax)
        {
            allCompliant = false;
            // Log non-compliance
        }

        // Requirement 3: PO must have a valid cost center
        if (_purchTable.CostCenterId == '')
        {
            allCompliant = false;
            // Log non-compliance
        }

        // Save compliance results
        complianceHeader.clear();
        complianceHeader.POId = _purchTable.PurchId;
        complianceHeader.PurchTableRecId = _purchTable.RecId;
        complianceHeader.ComplianceStatus = allCompliant 
            ? POComplianceStatus::Compliant 
            : POComplianceStatus::NonCompliant;
        complianceHeader.CheckedBy = curUserId();
        complianceHeader.CheckedDate = DateTimeUtil::utcNow();
        complianceHeader.insert();

        return allCompliant;
    }
}
```

### Step 3: Chain of Command Override on PO Workflow

```xpp
[ExtensionOf(classStr(PurchTable))]
final class PurchTable_ComplianceCocExtension
{
    /// <summary>
    /// Wrap the approve method to add compliance check before approval.
    /// </summary>
    public void approve()
    {
        // BEFORE: Check compliance before allowing approval
        if (!POComplianceService::checkCompliance(this))
        {
            // Compliance check failed — block approval
            checkFailed('Purchase order does not meet compliance requirements. Review the compliance form for details.');
            return;  // Stop the approval chain
        }

        // BASE: Call the standard approve method
        next approve();

        // AFTER: Compliance check passed, approval completed
        info(strFmt('Purchase order %1 approved with compliance check passed.', this.PurchId));
    }
}
```

### Step 4: Event Handler on PurchTable::created

```xpp
class PurchTableEventHandler
{
    [EventHandler(eventStr(PurchTable::inserted))]
    public static void onPurchTableInserted(Common _sender)
    {
        PurchTable purchTable = _sender as PurchTable;

        // Trigger compliance check when a new PO is created
        boolean isCompliant = POComplianceService::checkCompliance(purchTable);

        if (!isCompliant)
        {
            // PO is non-compliant — notify the compliance team
            info(strFmt('Purchase order %1 created but failed compliance check. Please review.', purchTable.PurchId));
        }
    }
}
```

### Step 5: Create the Batch Job for Weekly Compliance Audit

```xpp
class POComplianceAuditBatch extends RunBaseBatch
{
    PurchGroupId _purchGroupId;
    FromDate _fromDate;
    ToDate _toDate;

    public Object dialog()
    {
        Dialog dlg = super::dialog();
        dlg.addFieldValue(enumStr(PurchGroupId), _purchGroupId, "Purchase Group");
        dlg.addFieldValue(exttypstr(FromDate), _fromDate, "From Date");
        dlg.addFieldValue(exttypstr(ToDate), _toDate, "To Date");
        return dlg;
    }

    public boolean getFromDialog()
    {
        boolean ret = super::getFromDialog();
        _purchGroupId = dialog().dialogField(fieldNum(POComplianceAuditBatch, _purchGroupId)).value();
        _fromDate = dialog().dialogField(fieldNum(POComplianceAuditBatch, _fromDate)).value();
        _toDate = dialog().dialogField(fieldNum(POComplianceAuditBatch, _toDate)).value();
        return ret;
    }

    public void run()
    {
        PurchTable purchTable;
        POComplianceHeader complianceHeader;
        int totalChecked = 0;
        int nonCompliantCount = 0;

        while select purchTable
            where purchTable.PurchDate >= _fromDate
            && purchTable.PurchDate <= _toDate
            && purchTable.PurchGroupId == _purchGroupId
        {
            totalChecked++;
            if (!POComplianceService::checkCompliance(purchTable))
            {
                nonCompliantCount++;
            }
        }

        info(strFmt('Compliance audit complete. Checked %1 POs, found %2 non-compliant.',
            totalChecked, nonCompliantCount));
    }

    public boolean canGoBatch()
    {
        return true;
    }
}
```

### Step 6: Create the Data Entity for External Audit System

```xpp
// The data entity pushes compliance data to an external audit system
// using the staging pattern for write-back

// Entity: POComplianceEntity
// - Root entity: POComplianceHeader
// - Child entity: POComplianceLine
// - Staging table: POComplianceStaging
// - Mapping: Source fields → Staging → Target (external system)

// The entity is published via OData/REST and can be consumed by:
// - Power Automate flows
// - External audit applications
// - Regulatory reporting systems
```

### Step 7: Design the Security Model

| Role | Duties | Access |
|---|---|---|
| `ComplianceOfficer` | Viewer, Processor | Full compliance data access, can approve compliance exceptions |
| `APClerk` | Viewer | Read-only access to compliance data |
| `InventoryManager` | Processor | Can create and edit compliance records for their POs |
| `SystemAdmin` | Admin | Full control including security role management |

### Step 8: Deploy and Monitor

1. Deploy the model package through the CI/CD pipeline
2. Run database sync and compile
3. Test with "Run as" feature using each security role
4. Run the weekly compliance audit batch job manually first
5. Schedule the batch job as a recurring job
6. Monitor via LCS dashboards and Infolog
7. Review the compliance report monthly

---

## 22.4 Capstone Activity — Full Specification

> **Activity**: Implement the complete procurement-to-pay compliance scenario described in this chapter. You must make the following decisions and document your rationale for each:
>
> 1. **Table Design**: Staging table or direct insert? Justify your choice based on audit requirements.
> 2. **Form Pattern**: ListPage + Detail or single form? Justify based on user experience and scalability.
> 3. **Report Design**: SSRS or Power BI? Justify based on the audience and use case.
> 4. **Batch Job Framework**: RunBaseBatch or SysOperation? Justify based on the execution pattern.
> 5. **Data Entity Pattern**: Staging or direct write-back? Justify based on data integrity requirements.
> 6. **Security Model**: Three duties or two? Justify based on the organization's compliance requirements.
> 7. **Extension Pattern**: CoC or Event Handler? Justify based on the coupling requirements.
>
> For each decision, provide:
> - Your chosen approach
> - The alternative approach you considered
> - Why you chose your approach
> - What trade-offs your approach involves
> - How you would validate your choice in a test environment
>
> **Ideal Solution Walkthrough**: The detailed walkthrough above (Steps 1-8) shows the recommended approach with full code examples. Every decision is justified with methodology rationale, trade-off analysis, and production hardening notes.
>
> **Production Hardening Checklist**:
> - [ ] All custom tables have Configuration Keys
> - [ ] All custom forms have appropriate security roles assigned
> - [ ] All batch jobs have error handling with try/catch
> - [ ] All data entities have staging tables with validation
> - [ ] All CoC overrides call `next` appropriately
> - [ ] All event handlers return `EventHandlerResult::NoAction` when appropriate
> - [ ] All custom code has been tested with "Run as" feature
> - [ ] All custom code has SysTest unit tests
> - [ ] The model is versioned and documented
> - [ ] The deployment pipeline includes automated testing

---
---

## 22.5 Additional Module-Specific Capstones

The following capstone scenarios extend the core Procurement-to-Pay Compliance capstone (Ch 22.1–22.4) with module-specific implementations. Each capstone builds on the same architectural patterns (CoC, Event Handlers, SysOperation batch, Data Entities, SSRS reports, security model) but applies them to domain-specific business processes.

---

### Capstone A — Finance: AP Invoice Workflow with Tax Compliance

**Business Scenario:** A multinational manufacturer needs an automated AP invoice validation workflow that checks tax compliance (VAT/GST), vendor withholding tax, and intercompany settlement rules before posting. Non-compliant invoices are routed to a tax analyst for review.

**Domain-Specific Tables & EDTs (Finance Module):**
| Table/EDT | Purpose |
|---|---|
| `TaxTable`, `TaxTrans` | Tax codes and posted tax transactions |
| `TaxWithholdTable`, `TaxWithholdGroup` | Vendor withholding tax configuration |
| `VendInvoiceJour`, `VendInvoiceTrans` | AP invoice header and lines |
| `LedgerJournalTrans_AP` | AP ledger journal for posting |
| `TaxExemptTable`, `TaxExemptNumber` | Tax exemption certificates |
| `CompanyInfo` | Legal entity configuration for intercompany |

**Decision Points (Finance-Specific):**

| Decision | Recommendation | Finance Rationale |
|---|---|---|
| **Table Design** | Staging table (`APTaxComplianceStaging`) with `TaxTransRecId` | Audit trail required for tax authority audits; tax calculations can be re-validated |
| **Form Pattern** | ListPage + Detail with FactBox for `TaxTrans` | Tax analysts need to see tax lines side-by-side with invoice header |
| **Report Design** | SSRS paginated report (`APTaxComplianceReport`) with grouping by Tax Authority | Tax filings require printable, page-perfect audit reports |
| **Batch Job** | SysOperation (`APTaxComplianceBatch`) with `RunOn::Batch` | Scheduled nightly; must integrate with Process Automation for tax period close |
| **Data Entity** | Staging pattern with `mapEntityToDataSource` for tax code validation | External tax engines (e.g., Vertex, Avalara) consume via OData; tax codes must be validated |
| **Security Model** | Four duties: TaxAnalyst (Processor), APSupervisor (Approver), TaxAdmin (Config), Viewer | SOX segregation: tax configuration (TaxAdmin) must be separate from invoice processing (TaxAnalyst) |
| **Extension Pattern** | CoC on `VendInvoiceJournalCheckPost::checkPost` + Event Handler on `VendInvoiceJour::inserted` | CoC wraps the standard posting validation; Event Handler captures new invoices for async tax check |

**Key Implementation Artifacts:**

```xpp
// 1. Custom table for tax compliance tracking
table 50200 APTaxComplianceHeader
{
    fields
    {
        field(1; RecId; int64) { }
        field(2; InvoiceId; VendInvoiceId) { }
        field(3; VendInvoiceJourRecId; int64) { }
        field(4; TaxAuthority; TaxAuthorityId) { }
        field(5; ComplianceStatus; Enum APTaxComplianceStatus) { } // Compliant, NonCompliant, Exempt, UnderReview
        field(6; WithholdingTaxApplied; AmountMST) { }
        field(7; TaxExemptNumber; TaxExemptNumber) { }
        field(8; ReviewedBy; UserId) { }
        field(9; ReviewedDate; UtcDateTime) { }
    }
    keys { key(PK; RecId) { Clustered = true; } key(IX_Invoice; InvoiceId) { } }
}

// 2. CoC on standard AP posting validation
[ExtensionOf(classStr(VendInvoiceJournalCheckPost))]
final class VendInvoiceJournalCheckPost_TaxComplianceCoc
{
    public boolean checkPost(boolean _throwErrors = true)
    {
        boolean ret = next checkPost(_throwErrors);
        
        // BEFORE: If standard validation passes, run tax compliance check
        if (ret)
        {
            VendInvoiceJour vendInvoiceJour = this.vendInvoiceJour();
            ret = APTaxComplianceService::validateInvoiceForPosting(vendInvoiceJour, _throwErrors);
        }
        
        return ret;
    }
}

// 3. SysOperation batch for nightly tax compliance sweep
[DataContractAttribute]
class APTaxComplianceBatchContract
{
    FromDate fromDate;
    ToDate toDate;
    TaxAuthorityId taxAuthorityId;
    
    [DataMemberAttribute('FromDate')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate) { fromDate = _fromDate; return fromDate; }
    // ... other parm methods
}

class APTaxComplianceBatchService extends SysOperationServiceBase
{
    public void process(APTaxComplianceBatchContract _contract)
    {
        // Query all posted invoices in date range
        // Re-validate tax compliance for each
        // Generate compliance exceptions report
        // Push exceptions to external tax filing system via Data Entity
    }
}

// 4. Data Entity with tax code validation on import
public void mapEntityToDataSource(
    DataEntityRuntimeContext           _entityCtx,
    DataEntityDataSourceRuntimeContext _dataSourceCtx)
{
    super(_entityCtx, _dataSourceCtx);
    
    if (_dataSourceCtx.name() == dataEntityDataSourceStr(APTaxComplianceEntity, APTaxComplianceHeader))
    {
        APTaxComplianceHeader header = _dataSourceCtx.getBuffer();
        
        switch (_entityCtx.getDatabaseOperation())
        {
            case DataEntityDatabaseOperation::Insert:
                // Validate tax authority exists and is active for the legal entity
                if (!TaxAuthority::exist(header.TaxAuthority))
                {
                    throw error(strFmt("Tax authority %1 not found or inactive.", header.TaxAuthority));
                }
                break;
            case DataEntityDatabaseOperation::Update:
                // Preserve reviewed status — cannot be changed via import
                header.ReviewedBy = header.orig().ReviewedBy;
                header.ReviewedDate = header.orig().ReviewedDate;
                break;
        }
    }
}
```

**Finance-Specific Production Hardening:**
- [ ] Tax authority configuration keyed by legal entity (`CompanyInfo`)
- [ ] Withholding tax calculations use `TaxWithholdBase` and `TaxWithholdRate` EDTs
- [ ] Intercompany invoices validated against `CompanyInfo::find()` intercompany setup
- [ ] SSRS report includes tax authority registration numbers for audit trail
- [ ] Batch job logs to `BatchErrorLog` with `TaxAuthorityId` dimension for filtering

---

### Capstone B — SCM: Purchase Order Automation with Vendor Scorecard

**Business Scenario:** A distributor needs automated PO creation from requisition demands, with vendor selection based on a dynamic scorecard (on-time delivery %, quality defect rate, price competitiveness, ESG rating). The system must support blanket purchase orders, release orders, and vendor-managed inventory (VMI).

**Domain-Specific Tables & EDTs (SCM Module):**
| Table/EDT | Purpose |
|---|---|
| `PurchTable`, `PurchLine` | Purchase order header and lines |
| `PurchReqTable`, `PurchReqLine` | Purchase requisition header and lines |
| `VendTable`, `VendGroup` | Vendor master and grouping |
| `InventTable`, `InventDim` | Items and inventory dimensions (site, warehouse, location, license plate) |
| `PurchAgreementHeader`, `PurchAgreementLine` | Blanket purchase agreements |
| `VMIReplenishment` | Vendor-managed inventory configuration |
| `InventTrans` | Inventory transactions for receipt tracking |

**Decision Points (SCM-Specific):**

| Decision | Recommendation | SCM Rationale |
|---|---|---|
| **Table Design** | `POAutomationVendorScorecard` + `POAutomationVendorScoreHistory` | Scorecard values change over time; history required for trend analysis |
| **Form Pattern** | ListPage (`POAutomationListPage`) + Detail with FactBox for `VMIReplenishment` | Buyers need to see VMI status and scorecard trends on the same form |
| **Report Design** | SSRS for PO exception report + Power BI for Vendor Scorecard Dashboard | Operational exceptions need printable reports; scorecard trends need interactive visualization |
| **Batch Job** | SysOperation runtime tasks (`POAutomationBatchTaskController`) | Large vendor bases (10,000+) require parallel task dispatching for PO creation |
| **Data Entity** | `POAutomationVendorScorecardEntity` with staging for score recalculation | External procurement platforms (Coupa, Ariba) push vendor data; scores must recalc on import |
| **Security Model** | Three duties: Buyer (Processor), CategoryManager (Approver), VendorAdmin (Config) | Category managers approve vendor selection; buyers execute PO creation |
| **Extension Pattern** | CoC on `PurchReqReleaseOrder::release` + Event Handler on `PurchTable::created` | CoC wraps release logic to inject vendor selection; Event Handler triggers VMI check |

**Key Implementation Artifacts:**

```xpp
// 1. Vendor scorecard table with time-phased scores
table 50300 POAutomationVendorScorecard
{
    fields
    {
        field(1; RecId; int64) { }
        field(2; VendorAccount; VendAccount) { }
        field(3; ItemId; ItemId) { }
        field(4; OnTimeDeliveryPct; Real) { }       // 0-100
        field(5; QualityDefectRate; Real) { }       // PPM
        field(6; PriceCompetitivenessIndex; Real) { } // 0-100
        field(7; ESGRating; Enum VendorESGRating) { } // Platinum, Gold, Silver, Bronze
        field(8; WeightedScore; Real) { }           // Computed: 40% OTD + 30% Quality + 20% Price + 10% ESG
        field(9; ValidFrom; Date) { }
        field(10; ValidTo; Date) { }
    }
    keys { key(PK; RecId) { } key(IX_VendorItemDate; VendorAccount, ItemId, ValidFrom) { } }
}

// 2. Vendor selection service using scorecard
class POAutomationVendorSelectionService
{
    public static VendAccount selectBestVendor(ItemId _itemId, InventSiteId _siteId, Qty _qty)
    {
        POAutomationVendorScorecard scorecard;
        VendTable vendTable;
        
        // Find active scorecards for this item/site
        while select scorecard
            where scorecard.ItemId == _itemId
            && scorecard.ValidFrom <= today()
            && scorecard.ValidTo >= today()
            exists join vendTable
                where vendTable.AccountNum == scorecard.VendorAccount
                && vendTable.Blocked == NoYes::No
            order by scorecard.WeightedScore desc
        {
            // Check vendor capacity for this site
            if (POAutomationVendorSelectionService::hasCapacity(scorecard.VendorAccount, _siteId, _qty))
            {
                return scorecard.VendorAccount;
            }
        }
        return '';
    }
    
    private static boolean hasCapacity(VendAccount _vendor, InventSiteId _siteId, Qty _qty)
    {
        // Check vendor agreement, VMI setup, or lead time constraints
        return true; // Simplified
    }
}

// 3. CoC on requisition release to inject automated vendor selection
[ExtensionOf(classStr(PurchReqReleaseOrder))]
final class PurchReqReleaseOrder_VendorSelectionCoc
{
    public void release(PurchReqTable _purchReqTable)
    {
        // BEFORE: Auto-select vendor for lines without vendor
        PurchReqLine purchReqLine;
        while select purchReqLine
            where purchReqLine.PurchReqTable == _purchReqTable.RecId
            && purchReqLine.VendAccount == ''
        {
            VendAccount bestVendor = POAutomationVendorSelectionService::selectBestVendor(
                purchReqLine.ItemId, 
                purchReqLine.InventSiteId, 
                purchReqLine.PurchQty);
            
            if (bestVendor)
            {
                purchReqLine.VendAccount = bestVendor;
                purchReqLine.update();
            }
        }
        
        next release(_purchReqTable);
    }
}

// 4. SysOperation batch with runtime tasks for parallel PO creation
class POAutomationBatchService extends SysOperationServiceBase
{
    public void process(POAutomationBatchContract _contract)
    {
        BatchHeader batchHeader = this.getCurrentBatchHeader();
        PurchReqTable purchReqTable;
        List recIdList = new List(Types::Int64);
        int bundleSize = VSIBatchConstants::DefaultBundleSize; // 200
        int taskCount = 0;
        
        // Collect all approved requisitions
        while select RecId from purchReqTable
            where purchReqTable.PurchReqStatus == PurchReqStatus::Approved
            && purchReqTable.VendorSelectionAutomated == NoYes::Yes
        {
            recIdList.addEnd(purchReqTable.RecId);
        }
        
        // Split into bundles and create runtime tasks
        ListEnumerator enum = recIdList.getEnumerator();
        List currentBundle = new List(Types::Int64);
        
        while (enum.moveNext())
        {
            currentBundle.addEnd(enum.current());
            if (currentBundle.elements() >= bundleSize)
            {
                this.createTaskForBundle(batchHeader, currentBundle);
                taskCount++;
                currentBundle = new List(Types::Int64);
            }
        }
        if (currentBundle.elements() > 0)
        {
            this.createTaskForBundle(batchHeader, currentBundle);
            taskCount++;
        }
        
        batchHeader.save();
        info(strFmt("Created %1 batch tasks for PO automation.", taskCount));
    }
    
    private void createTaskForBundle(BatchHeader _batchHeader, List _recIdBundle)
    {
        POAutomationBatchTaskController taskController = POAutomationBatchTaskController::construct();
        taskController.parmRecIdBundle(_recIdBundle.pack());
        _batchHeader.addRuntimeTask(taskController, this.getCurrentBatchTask().RecId);
    }
    
    public void processTask(POAutomationBatchTaskContract _contract)
    {
        List recIdList = _contract.parmRecIdList().unpack();
        ListEnumerator enum = recIdList.getEnumerator();
        
        while (enum.moveNext())
        {
            PurchReqTable reqTable = PurchReqTable::find(enum.current());
            POAutomationService::createPOFromRequisition(reqTable);
        }
    }
}
```

**SCM-Specific Production Hardening:**
- [ ] Inventory dimensions (`InventDim`) validated against site/warehouse setup
- [ ] VMI replenishment logic checks `InventTrans` for actual consumption vs forecast
- [ ] Blanket agreement release orders validated against `PurchAgreementLine` remaining quantity
- [ ] Batch task bundle size configurable per vendor volume (high-volume vendors → smaller bundles)
- [ ] Power BI dashboard uses `VendorScorecardEntity` OData feed with incremental refresh

---

### Capstone C — HR: Leave Management with Compliance and Accrual Engine

**Business Scenario:** A global enterprise needs a leave management system supporting multiple leave types (annual, sick, parental, bereavement, jury duty), country-specific accrual rules, carry-over limits, and integration with payroll for salary deduction. Must comply with FMLA (US), Working Time Directive (EU), and local labor laws.

**Domain-Specific Tables & EDTs (HR Module):**
| Table/EDT | Purpose |
|---|---|
| `HcmWorker`, `HcmEmployment`, `HcmPosition` | Worker, employment, and position hierarchy |
| `HcmLeaveType`, `HcmLeaveTypeLimit` | Leave type definitions and limits |
| `HcmLeave`, `HcmLeaveBalance` | Leave transactions and balance tracking |
| `HcmLeaveAccrual`, `HcmLeaveAccrualSchedule` | Accrual engine configuration |
| `HcmLeaveRequest`, `HcmLeaveRequestWorkflow` | Leave request and workflow |
| `PayrollEarningCode`, `PayrollBenefitCalculationRate` | Payroll integration for salary deduction |
| `HcmLeaveRegistration` | Daily leave registration for time & attendance |

**Decision Points (HR-Specific):**

| Decision | Recommendation | HR Rationale |
|---|---|---|
| **Table Design** | `HcmLeaveAccrualEngine` + `HcmLeaveBalance` with date effectivity | Accrual rules change by legal entity and year; date effectivity preserves historical accuracy |
| **Form Pattern** | Task Page (`HcmLeaveRequestWizard`) for requests + ListPage for balance view | Employees need guided wizard; HR needs balance overview with drill-through |
| **Report Design** | SSRS for leave balance statements + Power BI for workforce absence analytics | Balance statements are legal documents; analytics need trend visualization |
| **Batch Job** | SysOperation (`HcmLeaveAccrualBatch`) with `RunOn::Batch` + recurrence | Monthly/annual accrual runs must align with payroll periods; cannot be manual |
| **Data Entity** | `HcmLeaveBalanceEntity` with staging for payroll integration | Payroll systems consume leave balances; accrual adjustments must be auditable |
| **Security Model** | Four duties: Employee (SelfService), Manager (Approver), HRSpecialist (Processor), PayrollAdmin (Config) | Managers approve team leave; HR configures accrual rules; Payroll reads balances only |
| **Extension Pattern** | CoC on `HcmLeaveRequestWorkflow::submit` + Event Handler on `HcmEmployment::updated` | CoC validates balance before submission; Event Handler recalculates accrual on employment change |

**Key Implementation Artifacts:**

```xpp
// 1. Date-effective accrual rule table
table 50400 HcmLeaveAccrualEngine
{
    DataClassification = CustomerContent;
    // Date effectivity: different rules apply to different date ranges
    fields
    {
        field(1; RecId; int64) { }
        field(2; LeaveType; HcmLeaveTypeId) { }
        field(3; LegalEntity; DataAreaId) { }
        field(4; ValidFrom; Date) { }
        field(5; ValidTo; Date) { }
        field(6; AccrualFrequency; Enum HcmAccrualFrequency) { } // Monthly, SemiMonthly, BiWeekly, Annual
        field(7; AccrualRate; Real) { }           // Hours per period
        field(8; MaxAccrualPerYear; Real) { }     // Cap
        field(9; CarryOverLimit; Real) { }        // Max hours carried to next year
        field(10; CarryOverExpiryMonths; int) { } // Months before carry-over expires
        field(11; ProrateOnHire; NoYes) { }       // Prorate first year
        field(12; ProrateOnTermination; NoYes) { } // Prorate final year
        field(13; FMLAEligible; NoYes) { }        // US FMLA flag
        field(14; EUWTDCompliant; NoYes) { }      // EU Working Time Directive
    }
    keys { key(PK; RecId) { } key(IX_LeaveTypeEntityDate; LeaveType, LegalEntity, ValidFrom) { } }
}

// 2. Accrual engine service — runs monthly via batch
class HcmLeaveAccrualService
{
    public static void processAccruals(Date _accrualDate)
    {
        HcmLeaveAccrualEngine engine;
        HcmWorker worker;
        HcmEmployment employment;
        HcmLeaveBalance balance;
        Real hoursToAccrue;
        
        // Find active accrual rules for the accrual date
        while select engine
            where engine.ValidFrom <= _accrualDate
            && engine.ValidTo >= _accrualDate
        {
            // Find eligible workers in this legal entity
            while select worker
                join employment
                    where employment.Worker == worker.RecId
                    && employment.LegalEntity == engine.LegalEntity
                    && employment.EmploymentStartDate <= _accrualDate
                    && (employment.EmploymentEndDate == dateNull() || employment.EmploymentEndDate >= _accrualDate)
            {
                // Calculate accrual for this worker/leave type
                hoursToAccrue = HcmLeaveAccrualService::calculateAccrual(engine, worker, employment, _accrualDate);
                
                if (hoursToAccrue > 0)
                {
                    // Update or create balance
                    balance = HcmLeaveBalance::findByWorkerLeaveType(worker.RecId, engine.LeaveType, true);
                    balance.AccruedHours += hoursToAccrue;
                    balance.AvailableHours += hoursToAccrue;
                    balance.LastAccrualDate = _accrualDate;
                    balance.write();
                    
                    // Log accrual transaction
                    HcmLeaveAccrual::createAccrualTransaction(worker.RecId, engine.LeaveType, hoursToAccrue, _accrualDate);
                }
            }
        }
    }
    
    private static Real calculateAccrual(HcmLeaveAccrualEngine _engine, HcmWorker _worker, HcmEmployment _employment, Date _date)
    {
        Real baseAccrual = _engine.AccrualRate;
        
        // Prorate for new hires
        if (_engine.ProrateOnHire && _employment.EmploymentStartDate > _date)
        {
            int daysInPeriod = dayOfMth(endMth(_date));
            int daysWorked = _date - _employment.EmploymentStartDate + 1;
            baseAccrual = baseAccrual * (daysWorked / daysInPeriod);
        }
        
        // Check annual cap
        HcmLeaveBalance balance = HcmLeaveBalance::findByWorkerLeaveType(_worker.RecId, _engine.LeaveType, false);
        if (balance && (balance.AccruedHoursYTD + baseAccrual > _engine.MaxAccrualPerYear))
        {
            baseAccrual = _engine.MaxAccrualPerYear - balance.AccruedHoursYTD;
        }
        
        return max(baseAccrual, 0);
    }
}

// 3. CoC on leave request submit — validate balance before workflow
[ExtensionOf(classStr(HcmLeaveRequestWorkflow))]
final class HcmLeaveRequestWorkflow_BalanceValidationCoc
{
    public void submit(HcmLeaveRequest _leaveRequest)
    {
        // BEFORE: Validate available balance
        HcmLeaveBalance balance = HcmLeaveBalance::findByWorkerLeaveType(
            _leaveRequest.Worker, 
            _leaveRequest.LeaveType, 
            false);
        
        if (!balance || balance.AvailableHours < _leaveRequest.RequestedHours)
        {
            Real available = balance ? balance.AvailableHours : 0;
            checkFailed(strFmt(
                "Insufficient leave balance. Available: %1 hours, Requested: %2 hours.",
                available, _leaveRequest.RequestedHours));
            return;
        }
        
        next submit(_leaveRequest);
        
        // AFTER: Reserve balance (move from available to pending)
        if (balance)
        {
            balance.AvailableHours -= _leaveRequest.RequestedHours;
            balance.PendingHours += _leaveRequest.RequestedHours;
            balance.write();
        }
    }
}

// 4. Event Handler on employment change — recalculate accrual eligibility
[EventHandler(eventStr(HcmEmployment::updated))]
public static void onEmploymentUpdated(Common _sender, DataEventArgs _e)
{
    HcmEmployment employment = _sender as HcmEmployment;
    
    // If legal entity or position changed, trigger accrual recalculation
    if (_e.changed(fieldNum(HcmEmployment, LegalEntity)) ||
        _e.changed(fieldNum(HcmEmployment, Position)) ||
        _e.changed(fieldNum(HcmEmployment, EmploymentEndDate)))
    {
        // Schedule async recalculation via batch
        HcmLeaveAccrualBatchController::construct().parmWorkerRecId(employment.Worker).startOperation();
    }
}
```

**HR-Specific Production Hardening:**
- [ ] Date-effective accrual rules (`ValidFrom`/`ValidTo`) enforced in all queries
- [ ] FMLA tracking fields on `HcmLeaveBalance` for US compliance reporting
- [ ] EU Working Time Directive minimum 4 weeks annual leave validated in accrual engine
- [ ] Carry-over expiry processed by annual batch job (`HcmLeaveCarryOverExpiryBatch`)
- [ ] Payroll integration via `HcmLeaveBalanceEntity` OData with `changecompany()` for multi-entity
- [ ] Leave balance statements (SSRS) include legal disclaimer per country
- [ ] Configuration key `HcmLeaveManagementAdvanced` gates advanced features

---

### Capstone D — Retail/Commerce: Omnichannel Order Management with Store Fulfillment

**Business Scenario:** A retailer with 500+ stores needs unified commerce: online orders fulfilled from store inventory (ship-from-store, BOPIS, curbside), real-time available-to-promise (ATP) across channels, and store associate mobile app for picking/packing.

**Domain-Specific Tables & EDTs (Retail/Commerce Module):**
| Table/EDT | Purpose |
|---|---|
| `RetailTransactionTable`, `RetailTransactionPaymentTrans` | POS transactions |
| `EcoResProduct`, `EcoResProductVariant` | Products and variants |
| `RetailStoreTable`, `RetailStoreInventory` | Store master and inventory |
| `RetailOrderTable`, `RetailOrderLine` | Omnichannel orders |
| `RetailFulfillmentOrder`, `RetailFulfillmentLine` | Store fulfillment work |
| `RetailATPBuffer` | Available-to-promise calculation buffer |
| `RetailChannelTable`, `RetailChannelProfile` | Channel configuration |

**Decision Points (Retail-Specific):**

| Decision | Recommendation | Retail Rationale |
|---|---|---|
| **Table Design** | `RetailFulfillmentOrder` with `RetailStoreInventory` staging | Real-time inventory sync requires staging; fulfillment SLA tracking |
| **Form Pattern** | Mobile-optimized ListPage (`RetailFulfillmentMobile`) + Task Page for picking | Store associates use mobile devices; task-oriented UI for pick/pack/stage |
| **Report Design** | Power BI real-time fulfillment dashboard + SSRS for daily reconciliation | Operations needs real-time SLA visibility; finance needs daily reconciliation |
| **Batch Job** | SysOperation with real-time triggers via Process Automation | Fulfillment waves triggered by order intake; not scheduled |
| **Data Entity** | `RetailInventoryEntity` (read-only, high-frequency) + `RetailFulfillmentEntity` (write) | E-commerce platforms poll ATP every 30s; fulfillment updates pushed via webhook |
| **Security Model** | Three duties: StoreAssociate (Processor), StoreManager (Approver), OpsAnalyst (Viewer) | Associates execute; managers handle exceptions; analysts monitor SLA |
| **Extension Pattern** | Event Handler on `RetailOrderTable::inserted` + CoC on `RetailATPBuffer::calculateATP` | Event Handler kicks off fulfillment; CoC extends ATP logic for store inventory |

**Key Implementation Artifacts:**

```xpp
// 1. Fulfillment order with SLA tracking
table 50500 RetailFulfillmentOrder
{
    fields
    {
        field(1; RecId; int64) { }
        field(2; FulfillmentId; RetailFulfillmentId) { }
        field(3; SalesId; SalesId) { }
        field(4; StoreId; RetailStoreId) { }
        field(5; FulfillmentType; Enum RetailFulfillmentType) { } // ShipFromStore, BOPIS, Curbside
        field(6; Status; Enum RetailFulfillmentStatus) { }       // New, Picking, Packed, Staged, Shipped, Cancelled
        field(7; SLADeadline; UtcDateTime) { }                   // SLA based on fulfillment type
        field(8; AssignedToWorker; HcmWorkerId) { }
        field(9; PickedDateTime; UtcDateTime) { }
        field(10; PackedDateTime; UtcDateTime) { }
        field(11; ShippedDateTime; UtcDateTime) { }
    }
    keys { key(PK; RecId) { } key(IX_StoreStatus; StoreId, Status) { } key(IX_SalesId; SalesId) { } }
}

// 2. Event Handler — trigger fulfillment on new order
[EventHandler(eventStr(RetailOrderTable::inserted))]
public static void onOrderInserted(Common _sender, DataEventArgs _e)
{
    RetailOrderTable order = _sender as RetailOrderTable;
    
    // Only process omnichannel orders (not POS)
    if (order.ChannelOrigin == RetailChannelOrigin::ECommerce)
    {
        // Determine best fulfillment store (ATP + distance + capacity)
        RetailStoreId bestStore = RetailFulfillmentService::determineFulfillmentStore(order);
        
        if (bestStore)
        {
            RetailFulfillmentService::createFulfillmentOrder(order, bestStore);
        }
        else
        {
            // No store can fulfill — route to DC
            RetailFulfillmentService::routeToDistributionCenter(order);
        }
    }
}

// 3. CoC on ATP calculation — include store inventory
[ExtensionOf(classStr(RetailATPBuffer))]
final class RetailATPBuffer_StoreInventoryCoc
{
    public Qty calculateATP(ItemId _itemId, InventSiteId _siteId, InventLocationId _locationId, Date _date)
    {
        // BASE: Standard ATP (warehouse inventory)
        Qty atp = next calculateATP(_itemId, _siteId, _locationId, _date);
        
        // EXTENSION: Add store inventory for omnichannel
        if (RetailParameters::find().OmnichannelFulfillmentEnabled)
        {
            // Sum available inventory across stores in the same fulfillment group
            Qty storeATP = RetailFulfillmentService::calculateStoreATP(_itemId, _siteId);
            atp += storeATP;
        }
        
        return atp;
    }
}

// 4. Mobile-optimized picking task (called from store associate app)
class RetailFulfillmentPickingService
{
    public static RetailFulfillmentLine pickNextItem(RetailStoreId _storeId, HcmWorkerId _workerId)
    {
        RetailFulfillmentLine line;
        RetailFulfillmentOrder header;
        
        // Find oldest un-picked line for this store/worker
        select firstonly line
            join header
                where header.RecId == line.RetailFulfillmentOrder
                && header.StoreId == _storeId
                && header.Status == RetailFulfillmentStatus::Picking
                && (header.AssignedToWorker == _workerId || header.AssignedToWorker == '')
            order by header.CreatedDateTime asc
        {
            // Update assignment
            if (header.AssignedToWorker == '')
            {
                header.AssignedToWorker = _workerId;
                header.update();
            }
            
            // Mark line as being picked
            line.PickingStartedDateTime = DateTimeUtil::utcNow();
            line.PickedByWorker = _workerId;
            line.update();
            
            return line;
        }
        
        return null;
    }
    
    public static void confirmPick(RetailFulfillmentLine _line, Qty _pickedQty, InventDimId _inventDimId)
    {
        ttsBegin;
        
        // Update line
        _line.PickedQty = _pickedQty;
        _line.InventDimId = _inventDimId;
        _line.PickedDateTime = DateTimeUtil::utcNow();
        _line.update();
        
        // Update inventory (physical reservation)
        InventTrans inventTrans = InventTrans::find(_line.InventTransId);
        inventTrans.Qty = _pickedQty;
        inventTrans.InventDimId = _inventDimId;
        inventTrans.StatusIssue = StatusIssue::Sold;
        inventTrans.update();
        
        // Check if all lines picked → move header to Packed
        RetailFulfillmentOrder header = RetailFulfillmentOrder::find(_line.RetailFulfillmentOrder);
        if (RetailFulfillmentService::areAllLinesPicked(header.RecId))
        {
            header.Status = RetailFulfillmentStatus::Packed;
            header.update();
        }
        
        ttsCommit;
    }
}
```

**Retail-Specific Production Hardening:**
- [ ] Real-time ATP calculation uses `RetailATPBuffer` with Redis caching (sub-100ms response)
- [ ] Store fulfillment SLA: BOPIS 2 hours, Curbside 30 min, Ship-from-Store 4 hours
- [ ] Inventory reservation uses `InventTrans` physical reservation (not financial)
- [ ] Mobile app offline capability: picks cached locally, synced when online
- [ ] Power BI streaming dataset for real-time fulfillment SLA dashboard
- [ ] Configuration key `RetailOmnichannelFulfillment` gates store fulfillment features

---

### Capstone E — Project Operations: Project Billing Compliance with Revenue Recognition

**Business Scenario:** A professional services firm running Project Operations needs automated project billing compliance that validates time entries against project contracts, enforces billing rules (fixed price, time & material, milestone), manages revenue recognition per IFRS 15/ASC 606, and generates compliant invoices with audit trails for client audits.

**Domain-Specific Tables & EDTs (Project Operations Module):**
| Table/EDT | Purpose |
|---|---|
| `ProjTable`, `ProjInvoiceTable` | Project header and invoice header |
| `ProjInvoiceLine`, `ProjTransInvoice` | Invoice lines and transaction lines |
| `ProjEmplTrans`, `ProjCategory` | Time/expense transactions and categories |
| `ProjRevenueRecognition` | Revenue recognition schedules |
| `ProjContract`, `ProjContractLine` | Project contracts and billing rules |
| `ProjMilestone`, `ProjMilestoneInvoice` | Milestone definitions and invoice triggers |
| `ProjWIP` | Work-in-progress tracking for revenue recognition |

**Decision Points (Project Operations-Specific):**

| Decision | Recommendation | Project Operations Rationale |
|---|---|---|
| **Table Design** | `ProjBillingComplianceHeader` + `ProjBillingComplianceLine` with contract linkage | Each billing event must trace to a contract line; audit trail requires header/line structure |
| **Form Pattern** | ListPage (`ProjBillingComplianceListPage`) + Detail with FactBox for `ProjWIP` | Project managers need to see WIP balances alongside compliance status |
| **Report Design** | SSRS for client audit reports (`ProjBillingComplianceAuditReport`) + Power BI for revenue recognition dashboard | Client audits require printable, page-perfect reports; finance needs real-time revenue recognition visibility |
| **Batch Job** | SysOperation (`ProjBillingComplianceBatch`) with `RunOn::Batch` + recurrence | Monthly revenue recognition runs must align with period close; fixed-price milestones triggered by date |
| **Data Entity** | `ProjBillingComplianceEntity` with staging for contract validation | External PSA tools push time entries; contract validation must happen on import |
| **Security Model** | Four duties: ProjectManager (Processor), BillingAnalyst (Approver), RevenueAccountant (Config), Viewer | SOX segregation: revenue recognition config (RevenueAccountant) separate from billing execution (ProjectManager) |
| **Extension Pattern** | CoC on `ProjInvoiceJournalCheckPost::checkPost` + Event Handler on `ProjTransInvoice::inserted` | CoC wraps invoice posting validation; Event Handler captures posted transactions for revenue recognition |

**Key Implementation Artifacts:**

```xpp
// 1. Custom table for project billing compliance tracking
table 50600 ProjBillingComplianceHeader
{
    fields
    {
        field(1; RecId; int64) { }
        field(2; ProjId; ProjId) { }
        field(3; ContractId; ProjContractId) { }
        field(4; ContractLineRecId; int64) { }
        field(5; BillingType; Enum ProjBillingType) { } // FixedPrice, TimeAndMaterial, Milestone, CostPlus
        field(6; ComplianceStatus; Enum ProjBillingComplianceStatus) { } // Compliant, NonCompliant, PendingReview, Exempt
        field(7; RevenueRecognitionStatus; Enum ProjRevenueRecStatus) { } // NotStarted, InProgress, Completed, Reversed
        field(8; ValidatedBy; UserId) { }
        field(9; ValidatedDate; UtcDateTime) { }
        field(10; PeriodCode; ProjPeriodCode) { } // Revenue recognition period
    }
    keys { key(PK; RecId) { Clustered = true; } key(IX_Project; ProjId) { } key(IX_Contract; ContractId) { } }
}

// 2. Custom table for compliance line details
table 50601 ProjBillingComplianceLine
{
    fields
    {
        field(1; RecId; int64) { }
        field(2; ComplianceHeader; int64) { }
        field(3; ProjTransInvoiceRecId; int64) { }
        field(4; CategoryId; ProjCategoryId) { }
        field(5; BilledQty; Qty) { }
        field(6; BilledAmount; AmountMST) { }
        field(7; RevenueRecognizedAmount; AmountMST) { }
        field(8; ComplianceRule; Enum ProjComplianceRule) { } // RateValidation, BudgetCheck, MilestoneMatch, WIPLimit
        field(9; RuleResult; Enum ProjComplianceRuleResult) { } // Pass, Fail, Warning
        field(10; RuleMessage; str) { }
    }
    keys { key(PK; RecId) { } key(IX_Header; ComplianceHeader) { } key(IX_Trans; ProjTransInvoiceRecId) { } }
}

// 3. CoC on project invoice posting validation
[ExtensionOf(classStr(ProjInvoiceJournalCheckPost))]
final class ProjInvoiceJournalCheckPost_BillingComplianceCoc
{
    public boolean checkPost(boolean _throwErrors = true)
    {
        boolean ret = next checkPost(_throwErrors);
        
        // BEFORE: If standard validation passes, run billing compliance check
        if (ret)
        {
            ProjInvoiceJour projInvoiceJour = this.projInvoiceJour();
            ret = ProjBillingComplianceService::validateInvoiceForPosting(projInvoiceJour, _throwErrors);
        }
        
        return ret;
    }
}

// 4. SysOperation batch for monthly revenue recognition processing
[DataContractAttribute]
class ProjBillingComplianceBatchContract
{
    FromDate fromDate;
    ToDate toDate;
    ProjPeriodCode periodCode;
    
    [DataMemberAttribute('FromDate')]
    public FromDate parmFromDate(FromDate _fromDate = fromDate) { fromDate = _fromDate; return fromDate; }
    // ... other parm methods
}

class ProjBillingComplianceBatchService extends SysOperationServiceBase
{
    public void process(ProjBillingComplianceBatchContract _contract)
    {
        // 1. Process revenue recognition for the period
        ProjRevenueRecognitionService::processPeriod(_contract.parmPeriodCode());
        
        // 2. Validate all posted invoices in date range for compliance
        ProjBillingComplianceService::validatePeriodInvoices(_contract.parmFromDate(), _contract.parmToDate());
        
        // 3. Generate compliance exceptions report
        ProjBillingComplianceReportController::generateExceptionsReport(_contract.parmPeriodCode());
        
        // 4. Push revenue recognition entries to General Ledger via Data Entity
        ProjRevenueRecognitionEntity::pushToGL(_contract.parmPeriodCode());
    }
}

// 5. Data Entity with contract validation on import
public void mapEntityToDataSource(
    DataEntityRuntimeContext           _entityCtx,
    DataEntityDataSourceRuntimeContext _dataSourceCtx)
{
    super(_entityCtx, _dataSourceCtx);
    
    if (_dataSourceCtx.name() == dataEntityDataSourceStr(ProjBillingComplianceEntity, ProjBillingComplianceHeader))
    {
        ProjBillingComplianceHeader header = _dataSourceCtx.getBuffer();
        
        switch (_entityCtx.getDatabaseOperation())
        {
            case DataEntityDatabaseOperation::Insert:
                // Validate contract exists and is active for the project
                ProjContract contract = ProjContract::find(header.ContractId);
                if (!contract || contract.Status != ProjContractStatus::Active)
                {
                    throw error(strFmt("Contract %1 not found or not active.", header.ContractId));
                }
                
                // Validate billing type matches contract line
                ProjContractLine contractLine = ProjContractLine::find(header.ContractLineRecId);
                if (contractLine && contractLine.BillingType != header.BillingType)
                {
                    throw error(strFmt("Billing type mismatch: contract line is %1, import has %2.", 
                        contractLine.BillingType, header.BillingType));
                }
                break;
            case DataEntityDatabaseOperation::Update:
                // Preserve validated status — cannot be changed via import
                header.ValidatedBy = header.orig().ValidatedBy;
                header.ValidatedDate = header.orig().ValidatedDate;
                break;
        }
    }
}

// 6. Revenue recognition service (simplified IFRS 15/ASC 606 logic)
class ProjRevenueRecognitionService
{
    public static void processPeriod(ProjPeriodCode _periodCode)
    {
        ProjRevenueRecognition revRec;
        ProjWIP projWIP;
        
        // Find all projects with active revenue recognition schedules
        while select revRec
            where revRec.PeriodCode == _periodCode
            && revRec.Status == ProjRevenueRecStatus::NotStarted
        {
            // Calculate revenue to recognize based on contract type
            AmountMST revenueToRecognize = ProjRevenueRecognitionService::calculateRevenueToRecognize(revRec);
            
            if (revenueToRecognize > 0)
            {
                // Create revenue recognition entry
                revRec.RecognizedAmount = revenueToRecognize;
                revRec.Status = ProjRevenueRecStatus::Completed;
                revRec.RecognizedDate = DateTimeUtil::utcNow();
                revRec.update();
                
                // Update WIP
                projWIP = ProjWIP::findByProjectPeriod(revRec.ProjId, _periodCode);
                if (projWIP)
                {
                    projWIP.RevenueRecognized += revenueToRecognize;
                    projWIP.update();
                }
                
                // Create GL voucher (simplified)
                ProjRevenueRecognitionService::createGLVoucher(revRec, revenueToRecognize);
            }
        }
    }
    
    private static AmountMST calculateRevenueToRecognize(ProjRevenueRecognition _revRec)
    {
        switch (_revRec.RecognitionMethod)
        {
            case ProjRevenueRecMethod::PercentageOfCompletion:
                // IFRS 15: Recognize based on progress towards completion
                return ProjRevenueRecognitionService::calculatePOC(_revRec);
            case ProjRevenueRecMethod::CompletedContract:
                // ASC 606: Recognize only when contract complete
                return ProjRevenueRecognitionService::calculateCompletedContract(_revRec);
            case ProjRevenueRecMethod::MilestoneBased:
                // Recognize when milestones achieved
                return ProjRevenueRecognitionService::calculateMilestone(_revRec);
            case ProjRevenueRecMethod::TimeAndMaterial:
                // Recognize as costs incurred
                return ProjRevenueRecognitionService::calculateTnM(_revRec);
        }
        return 0;
    }
    
    // ... helper methods for each recognition method
}
```

**Project Operations-Specific Production Hardening:**
- [ ] Contract billing rules validated against `ProjContractLine.BillingType` for each invoice
- [ ] Revenue recognition schedules use `ProjPeriodCode` aligned with fiscal calendar
- [ ] WIP (`ProjWIP`) balances reconciled monthly before period close
- [ ] Milestone-based billing triggers validated against `ProjMilestone` completion criteria
- [ ] Fixed-price project budget vs actual tracked in `ProjBudgetControl`
- [ ] SSRS audit report includes contract reference, billing rule, and revenue recognition method per line
- [ ] Configuration key `ProjBillingComplianceAdvanced` gates advanced features
- [ ] Multi-currency support via `CurrencyCode` on `ProjBillingComplianceHeader`

---

### Capstone Comparison Matrix

| Capstone | Module | Core Tables | Key Pattern | Batch Style | Report | Security Duties |
|---|---|---|---|---|---|---|
| **Base (Ch 15)** | SCM/Finance | POComplianceHeader/Line | CoC + Event Handler | RunBaseBatch + SysOperation | SSRS | 3 (Viewer, Processor, Admin) |
| **A** | Finance | APTaxComplianceHeader | CoC on `checkPost` | SysOperation (nightly) | SSRS (tax authority) | 4 (TaxAnalyst, APSupervisor, TaxAdmin, Viewer) |
| **B** | SCM | POAutomationVendorScorecard | CoC on release + Runtime Tasks | SysOperation (parallel tasks) | SSRS + Power BI | 3 (Buyer, CategoryManager, VendorAdmin) |
| **C** | HR | HcmLeaveAccrualEngine (date-effective) | CoC on submit + Employment Event Handler | SysOperation (monthly accrual) | SSRS + Power BI | 4 (Employee, Manager, HRSpecialist, PayrollAdmin) |
| **D** | Retail | RetailFulfillmentOrder/Line | Event Handler + CoC on ATP | Process Automation (real-time) | Power BI (streaming) + SSRS | 3 (StoreAssociate, StoreManager, OpsAnalyst) |
| **E** | Project Operations | ProjBillingComplianceHeader/Line | CoC on checkPost + Revenue Rec Event Handler | SysOperation (period close) | SSRS (audit) + Power BI (rev rec) | 4 (ProjManager, BillingAnalyst, RevenueAcct, Viewer) |

---

### Choosing Your Capstone Path

| If You Want To Specialize In... | Start With This Capstone | Then Extend To |
|---|---|---|
| **Finance/Tax** | Capstone A (AP Tax Compliance) | Financial Tags, Date Effectivity, ISV tax engine integration |
| **Procurement/Supply Chain** | Capstone B (PO Automation) | VMI, Blanket Agreements, Procurement Catalogs, EDI |
| **Human Resources/Payroll** | Capstone C (Leave Management) | Compensation, Benefits, Time & Attendance, Global Compliance |
| **Retail/Commerce** | Capstone D (Omnichannel) | POS Extensions, Loyalty, Clienteling, CDX/Retail Server |
| **Project Operations/PSA** | Capstone E (Project Billing Compliance) | Revenue Recognition, WIP, Milestone Billing, Contract Management |

---

### Capstone Completion Checklist (All Capstones)

For each capstone you implement, validate:
- [ ] All custom tables have `ConfigurationKey` and `DataClassification`
- [ ] All forms have `WorkflowEnabled` and security role assignment
- [ ] All batch jobs implement `BatchRetryable` and deadlock retry
- [ ] All data entities have staging tables with `mapEntityToDataSource` validation
- [ ] All CoC overrides call `next` and handle `checkFailed()` return
- [ ] All event handlers use `Common` sender and check `_e.changed()`
- [ ] SSRS reports use `SrsReportDataProviderPreProcessTempDB` for large datasets
- [ ] Power BI reports use incremental refresh on OData entities
- [ ] SysTest coverage ≥ 80% for business logic classes
- [ ] Model manifest declares all dependencies and configuration keys
- [ ] Deployment pipeline includes `Dynamics365ValidatePackage` task
- [ ] Performance tested with 100K+ records (batch) / 10K+ concurrent users (forms)
- [ ] Security tested with "Run as" for each duty/role
- [ ] Accessibility validated (WCAG 5.1 AA for customer-facing forms)

---

---


Beyond the classic `while select`, `insert_recordset`, and `update_recordset` patterns, D365 F&O provides a modern, type-safe data access API through the **SysDa** classes. For a 5-month-experienced intern, these patterns are essential for writing production-grade code that balances readability, performance, and maintainability.

# Chapter 23: Advanced X++ Patterns

## 23.1 The SysDa Classes — Type-Safe Data Access

The SysDa API provides a fluent, strongly-typed way to build queries at runtime. Unlike string-based X++ select statements, SysDa gives you IntelliSense, compile-time checking, and refactoring support. The SysDa APIs are wrappers around the code that the X++ compiler generates, so SysDa adds no overhead (unlike the `QueryRun` object).

The core SysDa types are:

| Operation | Primary Classes |
|---|---|
| Select | `SysDaQueryObject`, `SysDaSearchObject`, `SysDaSearchStatement` |
| Update | `SysDaUpdateObject`, `SysDaUpdateStatement` |
| Insert | `SysDaInsertObject`, `SysDaInsertStatement` |
| Delete | `SysDaQueryObject`, `SysDaDeleteObject`, `SysDaDeleteStatement` |

Expression classes for building clauses include `SysDaEqualsExpression`, `SysDaLessThanOrEqualsExpression`, `SysDaInExpression`, `SysDaFieldExpression`, `SysDaValueExpression`, and `SysDaModExpression`.

### When to Use SysDa vs. X++ Select

| Scenario | Use | Why |
|---|---|---|
| Simple `while select` with static where clause | X++ select | More concise, idiomatic X++ |
| Dynamic query construction at runtime | SysDa | Programmatically add ranges, joins, orderings |
| Complex runtime joins with conditional logic | SysDa | Cleaner than string manipulation |
| Need IntelliSense on table/field names | SysDa | Fully typed APIs |
| Bulk insert of many records | RecordInsertList | Typed, validated batch inserts |

### SysDa Query Example (Select)

```xpp
class VendComplianceQueryService
{
    public void getHighCreditVendors()
    {
        VendTable vendTable;

        // Build the query with fluent builder
        var qe = SysDaQueryObjectBuilder::from(VendTable)
            .projection()
                .add(fieldStr(VendTable, AccountNum))
                .add(fieldStr(VendTable, CreditMax))
            .whereClause(new SysDaGreaterThanExpression(
                new SysDaFieldExpression(vendTable, fieldStr(VendTable, CreditMax)),
                new SysDaValueExpression(500000)))
            .orderByClause()
                .addAscending(fieldStr(VendTable, AccountNum))
            .toSysDaQueryObject();

        // Execute the search
        var so = new SysDaSearchObject(qe);
        var ss = new SysDaSearchStatement();

        while (ss.findNext(so))
        {
            info(strFmt("Vendor: %1 — Credit Max: %2", vendTable.AccountNum, vendTable.CreditMax));
        }
    }

    public void getCustomersWithUnsettledInvoices()
    {
        CustTable custTable;

        var qe = SysDaQueryObjectBuilder::from(CustTable)
            .innerJoin(CustTrans)
            .whereClause(new SysDaAndExpression(
                new SysDaEqualsExpression(
                    new SysDaFieldExpression(custTable, fieldStr(CustTable, AccountNum)),
                    new SysDaFieldExpression(new CustTrans(), fieldStr(CustTrans, AccountNum))),
                new SysDaEqualsExpression(
                    new SysDaFieldExpression(new CustTrans(), fieldStr(CustTrans, HasNotBeenSettled)),
                    new SysDaValueExpression(true))))
            .toSysDaQueryObject();

        var so = new SysDaSearchObject(qe);
        var ss = new SysDaSearchStatement();

        while (ss.findNext(so))
        {
            info(strFmt("Customer with unsettled invoices: %1", custTable.AccountNum));
        }
    }
}
```

### SysDa Query Example (using SysDaQueryObjectBuilder with OR)

```xpp
var qe = SysDaQueryObjectBuilder::from(VendTable)
    .wherever(new SysDaOrExpression(
        new SysDaEqualsExpression(
            new SysDaFieldExpression(new VendTable(), fieldStr(VendTable, CreditMax)),
            new SysDaValueExpression(1000000)),
        new SysDaEqualsExpression(
            new SysDaFieldExpression(new VendTable(), fieldStr(VendTable, CreditMax)),
            new SysDaValueExpression(500000))))
    .toSysDaQueryObject();
```

### SysDa Insert Example

```xpp
TestTable t;

// Specify fields for the insert
var insertObject = new SysDaInsertObject(t);
insertObject.fields()
    .add(fieldStr(TestTable, StringField))
    .add(fieldStr(TestTable, IntField));

// Build the source query
LanguageTable source;
var qe = new SysDaQueryObject(source);
var s1 = qe.projection()
    .Add(fieldStr(LanguageTable, LanguageId))
    .AddValue(40);

qe.WhereClause(new SysDaEqualsExpression(
    new SysDaFieldExpression(source, fieldStr(LanguageTable, LanguageId)),
    new SysDaValueExpression("en-us")));

insertObject.query(qe);

ttsBegin;
    new SysDaInsertStatement().insert(insertObject);
ttsCommit;
```

### SysDa Update Example

```xpp
TestTable t;

var uo = new SysDaUpdateObject(t);
uo.settingClause()
    .add(fieldStr(TestTable, StringField), new SysDaValueExpression("fifty"));

uo.WhereClause(new SysDaEqualsExpression(
    new SysDaFieldExpression(t, fieldStr(TestTable, IntField)),
    new SysDaValueExpression(50)));

ttsBegin;
    new SysDaUpdateStatement().update(uo);
ttsCommit;
```

### SysDa Delete Example

```xpp
TestTable t;

var qe = new SysDaQueryObject(t);
var s = qe.projection()
    .add(fieldStr(TestTable, IntField));

qe.WhereClause(new SysDaEqualsExpression(
    new SysDaModExpression(
        new SysDaFieldExpression(t, fieldStr(TestTable, IntField)),
        new SysDaValueExpression(2)),
    new SysDaValueExpression(0)));

var ds = new SysDaDeleteStatement();
var delobj = new SysDaDeleteObject(qe);

ttsBegin;
    ds.delete(delobj);
ttsCommit;
```

### SysDa Best Practices

1. **Use `queryValue()` for parameters** — prevents SQL injection and ensures proper type conversion.
2. **Prefer expression objects over string concatenation** — SysDa handles escaping and quoting automatically.
3. **Use `SysDaQueryObjectBuilder`** for fluent, readable query construction.
4. **Use `toString()` on SysDa objects** to debug the generated query (e.g., `qe.toString()`).
5. **You are responsible for correctness** — SysDa won't catch type mismatches like comparing a GUID to an integer at compile time.

---

## 23.2 RecordInsertList — Typed Bulk Insert

## 23.2 RecordInsertList — Typed Bulk Insert

`RecordInsertList` is the type-safe alternative to `insert_recordset`. It validates each record before insertion and works with table buffers that have business logic in `validateWrite()`.

```xpp
class VendComplianceBulkInserter
{
    public void insertComplianceLogs(container _logData)
    {
        RecordInsertList insertList = new RecordInsertList();
        APCustomsDeclaration log;
        
        // Build each record
        for (int i = 1; i <= conLen(_logData); i++)
        {
            log.clear();
            // ... populate fields from _logData ...
            insertList.add(log);
        }
        
        // Insert all records — each record's validateWrite() is called
        insertList.insertDatabase();
    }
}
```

### RecordInsertList vs. insert_recordset

| Aspect | RecordInsertList | insert_recordset |
|---|---|---|
| validateWrite() called | Yes — for each record | No — bypasses table logic |
| Event handlers fire | Yes | No |
| Returns RecId values | Yes | No |
| Performance | Slightly slower (per-record validation) | Faster (single SQL statement) |
| Type safety | Strongly typed | X++ select syntax |
| Best for | Data with business logic validation | Pure bulk data loads |

---

## 23.3 RecordSortedList — Sorted Bulk Insert

`RecordSortedList` extends `RecordInsertList` with automatic sorting before insertion, which can reduce page splits and improve insert performance on tables with clustered indexes.

```xpp
RecordSortedList sortedList = new RecordSortedList();
sortedList.addField(fieldNum(APCustomsDeclaration, DeclId));
sortedList.addField(fieldNum(APCustomsDeclaration, DeclDate));
// ... add records ...
sortedList.insertDatabase();
```

---

## 23.4 doInsert / doUpdate / doDelete — The Internal Write Path

When you call `insert()`, `update()`, or `delete()` on a table buffer, the framework routes through internal methods:

- **`insert()`** → `validateWrite()` → `doInsert()` → SQL INSERT
- **`update()`** → `validateWrite()` → `doUpdate()` → SQL UPDATE
- **`delete()`** → `validateDelete()` → `doDelete()` → SQL DELETE

Override `doInsert()`, `doUpdate()`, or `doDelete()` when you need to intercept the actual database write without re-running validation logic:

```xpp
// In a table extension via CoC
public void doInsert()
{
    // Custom logic before the actual SQL insert
    // e.g., setting audit fields, computing derived values
    this.CreatedDateTime = DateTimeUtil::utcNow();
    
    // Call the actual write
    next doInsert();
    
    // Post-insert logic
    APComplianceLog::logInsert(this.RecId);
}
```

**Important:** `doInsert()`, `doUpdate()`, and `doDelete()` are called **after** validation succeeds. Do not put validation logic here — put it in `validateWrite()`.

---


For an intern with 5 months of experience, understanding the deeper language features and extensibility patterns is critical for writing upgrade-safe, maintainable code.

## 23.5 Extension Methods — Adding Methods to Existing Types

Extension methods let you add methods to existing classes, tables, views, or maps without modifying the original object. The extension class must be `static`, end with `_Extension`, and every extension method must be `public static` with the target type as the first parameter.

```xpp
public static class CustTable_Extension
{
    // Extension method on CustTable — callable as custTable.getCreditStatus()
    public static str getCreditStatus(CustTable _custTable)
    {
        if (_custTable.CreditMax > 1000000)
            return "High";
        if (_custTable.CreditMax > 100000)
            return "Medium";
        return "Low";
    }
    
    // Extension method with optional parameters
    public static str formatVendorDisplay(VendTable _vendTable, boolean _includeGroup = false)
    {
        str result = strFmt("%1 (%2)", _vendTable.AccountNum, _vendTable.Name);
        if (_includeGroup)
            result = strFmt("%1 — Group: %2", result, _vendTable.GroupName);
        return result;
    }
}
```

### Extension Method Rules

| Rule | Requirement |
|---|---|
| Class must be `static` | `public static class Name_Extension` |
| Class name suffix | Must end with `_Extension` |
| Methods must be `public static` | No instance methods in extension class |
| First parameter is the target type | The instance being extended is passed automatically |
| Can't access protected/private members | Only public members of the target type |
| Target types: Class, Table, View, Map | Not forms, reports, or other AOT objects |

### Calling Extension Methods

```xpp
CustTable custTable = CustTable::find("CUST-001");
str status = CustTable_Extension::getCreditStatus(custTable);
// Or using dot syntax (X++ resolves extension methods):
str status2 = custTable.getCreditStatus();
```

---

## 23.6 Local Functions Inside Methods

X++ allows you to declare functions inside a method. These are called **local functions** and can access variables declared earlier in the enclosing method.

```xpp
public void processComplianceDeclarations(CustTable _custTable)
{
    int declarationCount = 0;
    
    // Local function — can access declarationCount from enclosing method
    void logDeclaration(str _declId)
    {
        declarationCount++;
        info(strFmt("Processed declaration %1 (total: %2)", _declId, declarationCount));
    }
    
    // Another local function
    boolean isHighValue(Amount _amount)
    {
        return _amount > 50000;
    }
    
    APCustomsDeclaration decl;
    while select decl
        where decl.VendTableRecId == _custTable.RecId
    {
        if (isHighValue(decl.CustomsRefAmount))
        {
            logDeclaration(decl.DeclId);
        }
    }
}
```

### Local Function Rules

- Can access variables declared **earlier** in the enclosing method
- Cannot be called from outside the enclosing method
- Can declare multiple local functions in one method
- Each local function establishes its own scope

---

## 23.7 The `var` Keyword — Type Inference

X++ supports the `var` keyword for local variable type inference. The compiler determines the type from the assigned expression.

```xpp
var custTable = CustTable::find("CUST-001");    // Type: CustTable
var count = 42;                                  // Type: int
var name = "Acme Corp";                          // Type: str
var now = DateTimeUtil::utcNow();                // Type: utcdatetime
var list = new List(Types::String);              // Type: List
```

### When to Use `var`

- **Use `var`** when the type is obvious from the right-hand side (e.g., `new CustValidationService()`, `CustTable::find()`)
- **Avoid `var`** when the type isn't immediately clear or when you want to be explicit for readability
- **Never use `var`** for class-level fields — only local variables

---

## 23.8 The `orig()` Method — Accessing Original Field Values

Every table buffer has an `orig()` method that returns a buffer containing the original field values (as they were when the record was read from the database). This is essential for change detection in `update()` and `validateWrite()`.

```xpp
public boolean validateWrite()
{
    boolean ret = super();
    
    CustTable orig = this.orig();
    
    // Detect if credit limit changed
    if (this.CreditMax != orig.CreditMax)
    {
        // Credit limit was modified — run compliance checks
        if (this.CreditMax > 500000 && this.ComplianceCode == '')
        {
            ret = checkFailed("Compliance code required when credit limit exceeds $500,000.");
        }
        
        // Log the change
        APComplianceLog::logCreditLimitChange(orig.CreditMax, this.CreditMax, this.AccountNum);
    }
    
    return ret;
}
```

### When `orig()` Is Available

- `orig()` returns valid data after a `select` or `while select` reads a record
- `orig()` returns the buffer's default values after `clear()` or before any database read
- In `update()`, `orig()` contains the values before the update
- In `validateWrite()` called from `update()`, `orig()` has the pre-update values

---

## 23.9 `prmIsDefault()` — Detecting Parameter Presence

The `prmIsDefault()` function determines whether a parameter was actually passed to a `parmX()` accessor method or whether the default value was used.

```xpp
class VendComplianceContract
{
    ComplianceCode complianceCode;
    
    public ComplianceCode parmComplianceCode(ComplianceCode _complianceCode = complianceCode)
    {
        if (!prmIsDefault(_complianceCode))
        {
            // Caller explicitly passed a value — validate it
            if (strLen(_complianceCode) > 20)
            {
                throw error("Compliance code cannot exceed 20 characters.");
            }
        }
        complianceCode = _complianceCode;
        return complianceCode;
    }
}
```

### Usage Pattern

```xpp
VendComplianceContract contract = new VendComplianceContract();

// Caller passes a value — prmIsDefault returns false
contract.parmComplianceCode("COMP-001");

// Caller omits the value — prmIsDefault returns true, default used
contract.parmComplianceCode();
```

---

## 23.10 Chain of Command Execution Order — Advanced

When multiple CoC extensions target the same method, the execution order follows the model layer hierarchy:

1. **SYS layer** extensions run first (lowest layer)
2. **ISV layer** extensions run next
3. **VAR layer** extensions run next
4. **CUS layer** extensions run last (highest layer — customer code)

Within the same layer, the order is **not guaranteed** — do not rely on alphabetical or registration order.

### CoC Return Value Chain

When multiple extensions modify a return value, each extension receives the return value from the previous extension:

```xpp
// Extension A (CUS layer)
[ExtensionOf(tableStr(CustTable))]
final class CustTable_ExtA
{
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();  // Gets result from base or previous extension
        if (ret && this.AccountNum == "")
        {
            ret = checkFailed("Account number required.");
        }
        return ret;  // Passed to Extension B
    }
}

// Extension B (CUS layer)
[ExtensionOf(tableStr(CustTable))]
final class CustTable_ExtB
{
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();  // Gets result from Extension A
        if (ret && this.Name == "")
        {
            ret = checkFailed("Name required.");
        }
        return ret;
    }
}
```

If Extension A returns `false`, Extension B's `next validateWrite()` still runs, but Extension B can check `ret` and short-circuit.

---


# Chapter 24: Production Debugging

## 24.1 SQL Statement Timeouts

D365 F&O sets different SQL statement timeouts based on session type:

| Session Type | Timeout | When It Applies |
|---|---|---|
| Interactive (user-driven) | 30 minutes | Forms, menu items, user-triggered actions |
| Non-interactive | 3 hours | Batch jobs, services, OData calls |

When a statement times out, X++ throws `Exception::Timeout` with the message *"A time-out occurred in the database while the query was executing."*

### Handling SQL Timeouts

```xpp
static void exercise_sqlTimeoutHandling(Args _args)
{
    CustTable custTable;
    int retryCount = 0;
    boolean success = false;
    
    while (!success && retryCount < 3)
    {
        try
        {
            while select custTable
                where custTable.CreditMax > 1000000
            {
                // Process high-credit customers
            }
            success = true;
        }
        catch (Exception::Timeout)
        {
            retryCount++;
            info(strFmt("SQL timeout — retry %1 of 3", retryCount));
            // Consider: log the timeout, reduce query scope, or add indexes
        }
        catch (Exception::Deadlock)
        {
            // ... deadlock handling ...
        }
    }
    
    if (!success)
    {
        error("Query failed after 3 retries due to SQL timeouts.");
    }
}
```

### Overriding Query Timeout

Use the `queryTimeout` API to override the default timeout for specific queries:

```xpp
// Set timeout for a specific query (in seconds)
queryTimeout(600);  // 10 minutes for this query
```

---

## 24.2 `CacheLookup` Deep Dive — Production Considerations

`CacheLookup` controls how SQL Server caches table lookups. Choose wisely based on table size and access pattern:

| Value | Behavior | Best For | Avoid For |
|---|---|---|---|
| `None` | No caching | High-write tables, frequently changing data | Read-heavy lookup tables |
| `NotInTTS` | Cache within transaction scope | Tables read within transactions | Cross-transaction lookups |
| `Found` | Cache successful lookups | Reference tables (CustGroup, ItemGroup) | Large transactional tables |
| `FoundAndEmpty` | Cache found and not-found | Lookup tables where misses are common | Tables with frequent inserts |
| `EntireTable` | Load whole table into memory | Small, static reference tables (CurrencyTable) | Tables with >10,000 rows |

**Production Rule:** Never set `CacheLookup = EntireTable` on a table with more than 10,000 rows or a table that receives frequent inserts/updates. This loads the entire table into server memory on first access and can cause memory pressure.

---

## 24.3 Deadlock Resolution in Production

Deadlocks occur when two transactions hold locks that the other needs. In D365 F&O, implement retry logic with exponential backoff:

```xpp
static void exercise_deadlockWithBackoff(Args _args)
{
    int retryCount = 0;
    int maxRetries = 5;
    int baseDelayMs = 100;  // Start with 100ms
    boolean success = false;
    
    while (!success && retryCount < maxRetries)
    {
        ttsBegin;
        try
        {
            // ... database operations ...
            ttsCommit;
            success = true;
        }
        catch (Exception::Deadlock)
        {
            ttsAbort;
            retryCount++;
            
            // Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
            int delayMs = baseDelayMs * (1 << (retryCount - 1));
            info(strFmt("Deadlock — retry %1 of %2, waiting %3ms", retryCount, maxRetries, delayMs));
            
            // Sleep before retry (use xSession::sleep or similar)
            // xSession::sleep(delayMs);  // Available in some versions
        }
    }
}
```

---

## 24.4 Indexing Strategy for Production

| Index Type | When to Use | Production Consideration |
|---|---|---|
| Primary (RecId) | Always — auto-created | Never change; it's the clustered index |
| Alternate (unique) | Natural keys that must be unique | `AllowDuplicates = No` enforces integrity at DB level |
| Hash | Equality-only lookups | No range scans; use when you always filter by exact match |
| Non-unique | Fields with many duplicates | Good for range scans and sorting |
| Group Level | Multi-field with selective leading field | Leading field must be the most selective |

**Leading Field Rule:** In an index on `(FieldA, FieldB)`, SQL can use the index for `where FieldA = ...` or `where FieldA = ... AND FieldB = ...`, but **NOT** for `where FieldB = ...` alone. Always put the most selective field first.

**Missing Index Detection:** Use SQL Server's missing index DMVs or the D365 F&O SQL performance tools in LCS to identify tables that need indexes.

---


# Chapter 25: Power Platform & Copilot

## 25.1 Power Platform Integration

D365 F&O integrates with the Power Platform through several mechanisms:

### Data Entities via OData

Every public data entity is automatically exposed via OData at:
```
https://<environment>/data/<EntityName>
```

Power Apps and Power Automate can consume these endpoints directly.

### Custom Services via SysOperationServiceController

Expose business logic as OData actions/functions:

```xpp
class VendComplianceController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        // This controller can be called from Power Automate via OData
        VendComplianceController controller = new VendComplianceController();
        controller.parmContractType(classStr(VendComplianceContract));
        controller.parmServiceType(classStr(VendComplianceService));
        controller.startOperation();
    }
}
```

### Logic Apps and Azure Functions

- **Logic Apps**: Orchestrate workflows between D365 F&O and external systems without code
- **Azure Functions**: Run custom code triggered by D365 F&O events (webhooks, Service Bus messages)
- **Azure Service Bus**: Async messaging for integration patterns

---

## 25.2 Copilot Capabilities in D365 F&O

Microsoft Copilot is integrated into D365 F&O for AI-assisted development:

- **Code generation**: Copilot can generate X++ code snippets from natural language descriptions
- **Code explanation**: Select code and ask Copilot to explain what it does
- **Debugging assistance**: Copilot can suggest fixes for compilation errors and runtime issues
- **Documentation lookup**: Ask Copilot about Microsoft Learn documentation without leaving Visual Studio

**Best Practice:** Always review Copilot-generated code against Microsoft best practices before committing. Copilot can suggest outdated patterns (e.g., overlayering instead of extensions).

---

## 25.3 Mobile Platform

D365 F&O supports mobile access through:

- **Dynamics 365 mobile app**: Native iOS/Android app for mobile access
- **Mobile workspaces**: Role-specific workspaces optimized for mobile devices
- **Offline capabilities**: Limited offline data access with sync when reconnected

Developers should consider mobile form factors when designing forms that mobile users will access.

---

## 25.4 Process Automation Framework

The Process Automation Framework enables business process automation. Batch jobs integrated with Process Automation use `SysOperationServiceController`, **not** `RunBaseBatch`:
- `RunBaseBatch` jobs cannot be returned through the process automation list
- Use `SysOperationServiceController` with `RunOn::Batch` for process automation integration
- Wrap `RunBaseBatch` with `SysOperation` to get both dialog input and scheduled execution

- **Business process flows**: Guide users through multi-step processes
- **Business rules**: Enforce data quality and business logic at the form level
- **Workflows**: Automated approval and routing processes

Use these for declarative automation; reserve X++ for complex business logic that can't be expressed through the framework.

---


For a 5-month-experienced intern, module specialization means understanding the domain-specific tables, EDTs, and business logic of your target module.

# Chapter 26: Module Specialization

## 26.1 Finance Module Deep Dive

### Key Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `LedgerJournalTrans` | General ledger journal transactions | `AccountNum`, `AmountCur`, `TransDate`, `Voucher` |
| `CustTrans` | Customer transactions (open/invoiced) | `AccountNum`, `Invoice`, `AmountMST`, `SettleDate` |
| `VendTrans` | Vendor transactions | `AccountNum`, `Invoice`, `AmountMST`, `SettleDate` |
| `LedgerTrans` | Posted ledger transactions | `AccountNum`, `AmountCur`, `TransDate`, `Voucher` |
| `CurrencyTable` | Currency codes and exchange rates | `CurrencyCode`, `Currency` |

### Key EDTs

| EDT | Purpose | Base Type |
|---|---|---|
| `CustAccount` | Customer account number | string 20 |
| `VendAccount` | Vendor account number | string 20 |
| `AmountMST` | Amount in company currency | real |
| `AmountCur` | Amount in transaction currency | real |
| `AccountNum` | General ledger account | string 20 |

### Common Finance Patterns

- **Voucher numbering**: Use `Voucher` EDT with number sequences
- **Exchange rate lookup**: `CurrencyExchangeRate` table for currency conversion
- **Financial dimensions**: `DimensionAttribute` and `DimensionValue` for chart of accounts segments
- **Tax calculation**: `Tax` table and `TaxAmount` EDT for tax-aware amounts

---

## 26.2 Supply Chain Management (SCM) Module Deep Dive

### Key Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `InventTable` | Items/products | `ItemId`, `ItemName`, `ItemGroupId` |
| `InventTrans` | Inventory transactions | `ItemId`, `InventTransId`, `StatusIssue`, `Receipt` |
| `PurchTable` | Purchase orders | `PurchId`, `PurchName`, `VendorAccount` |
| `PurchLine` | Purchase order lines | `PurchId`, `ItemId`, `PurchQty`, `PurchPrice` |
| `SalesTable` | Sales orders | `SalesId`, `SalesName`, `CustomerAccount` |
| `SalesLine` | Sales order lines | `SalesId`, `ItemId`, `SalesQty`, `SalesPrice` |
| `InventLocation` | Warehouses/locations | `InventLocationId`, `Name` |

### Key EDTs

| EDT | Purpose |
|---|---|
| `ItemId` | Item/product identifier |
| `InventLocationId` | Warehouse identifier |
| `InventSiteId` | Site identifier |
| `PurchId` | Purchase order identifier |
| `SalesId` | Sales order identifier |
| `Qty` | Quantity |

### Common SCM Patterns

- **Inventory dimensions**: `InventDim` for tracking inventory by site, warehouse, location, license plate
- **Item groups**: Group items for pricing, posting, and reporting
- **Unit of measure conversions**: `UnitOfMeasure` and `UnitOfMeasureConversion` for UOM conversions
- **Item reservation**: `InventTrans` reservation for order fulfillment

---

## 26.3 Human Resources (HR) Module Deep Dive

### Key Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `HcmWorker` | Workers/employees | `PersonnelNumber`, `Worker` |
| `HcmEmployment` | Employment records | `Worker`, `EmploymentStartDate`, `EmploymentEndDate` |
| `HcmPosition` | Positions/jobs | `PositionId`, `JobId`, `Department` |
| `HcmJob` | Job definitions | `JobId`, `JobType`, `JobFunction` |
| `HcmPositionWorkerAssignment` | Worker-to-position assignments | `PositionId`, `Worker` |

### Key EDTs

| EDT | Purpose |
|---|---|
| `PersonnelNumber` | Employee personnel number |
| `PositionId` | Position identifier |
| `JobId` | Job identifier |
| `Worker` | Worker identifier |

### Common HR Patterns

- **Position hierarchy**: Positions belong to departments; workers are assigned to positions
- **Employment lifecycle**: Hire → Employ → Terminate → Rehire
- **Compensation**: `HcmCompensation` for salary and bonus management
- **Leave/absence**: `HcmLeave` and `HcmLeaveType` for leave management

---

## 26.4 Choosing a Module for Specialization

| Factor | Finance | SCM | HR | Retail/Commerce | Project Operations |
|---|---|---|---|---|---|
| Core data model | General ledger, subledgers | Inventory, purchasing, sales | Workers, positions, jobs | Channels, products, store fulfillment | Projects, contracts, WIP, revenue rec |
| Transaction volume | High (GL postings) | Very high (inventory movements) | Moderate (HR cycles) | Extreme (POS/e-commerce orders) | High (time/expense & billing) |
| Regulatory complexity | High (tax, GAAP/IFRS) | High (customs, trade compliance) | Moderate (labor laws) | High (payment/PCI compliance) | High (IFRS 15/ASC 606 revenue rec) |
| Integration needs | ERP-to-banking, tax engines | ERP-to-WMS, EDI, supplier portals | ERP-to-payroll, benefits platforms | ERP-to-e-commerce, POS, payment gateways | ERP-to-PSA, time-tracking, client portals |

---


# Chapter 27: Advanced DevOps

## 27.1 Continuous Delivery Pipeline

Beyond the basic build → deploy pipeline, mature D365 F&O teams implement:

```
Source Commit → Build (Compile X++) → Package (.axmodel) → 
Validate Package → Deploy to Dev → Automated Tests → 
Deploy to Test → UAT Approval → Deploy to Production
```

### Validate Package Operation

Before deploying to production, validate that the package is compatible with the target environment:

```yaml
# Azure DevOps pipeline step
- task: Dynamics365ValidatePackage@1
  inputs:
    lcsConnection: 'LCS Service Connection'
    environmentId: '$(productionEnvironmentId)'
    packagePath: '$(Build.ArtifactStagingDirectory)/$(ModelName).axmodel'
```

This checks for:
- Missing dependencies
- Layer conflicts
- Version mismatches
- Breaking changes to standard methods

---

## 27.2 Database Movement Operations

Move databases between environments for testing with production-like data:

| Operation | Purpose | When to Use |
|---|---|---|
| Database export | Export production database to LCS | Create test environments with real data |
| Database import | Import database from LCS to environment | Refresh test environments |
| Database sync | Synchronize schema between environments | Deploy table changes without full redeploy |
| Database refresh | Full database replacement | Major environment resets |

**Best Practice:** Never move production data to a development environment without masking sensitive data (PII, PCI, financial data).

---

## 27.3 Build Automation Best Practices

| Practice | Reason |
|---|---|
| Build on every commit | Catch compilation errors early |
| Run unit tests in build | Prevent regressions |
| Version increment on each build | Track which build is deployed |
| Publish `.axmodel` as artifact | Enables deployment to any environment |
| Fail build on best practice violations | Maintain code quality |
| Use Release pipelines for promotion | Controlled deployment flow |

---


# Chapter 28: Compliance & ISV

## 28.1 GDPR Compliance in Development

The General Data Protection Regulation (GDPR) affects how you handle personal data in D365 F&O:

| Requirement | Implementation |
|---|---|
| Right to be forgotten | Delete or anonymize personal data on request |
| Data minimization | Only collect/store data you need |
| Consent tracking | Record when and how consent was given |
| Data portability | Export user data in machine-readable format |
| Breach notification | Log and report data access anomalies |

### GDPR Development Patterns

- **Anonymization**: Replace personal identifiers with pseudonyms rather than deleting (preserves referential integrity)
- **Retention policies**: Configure table retention to automatically purge old data
- **Audit logging**: Track who accessed personal data and when
- **Field-level encryption**: Encrypt sensitive fields at the database level

---

## 28.2 ISV Development Considerations

Independent Software Vendors (ISVs) building managed solutions for D365 F&O must follow additional rules:

| Consideration | Requirement |
|---|---|
| ISV layer | Develop in ISV layer, not CUS |
| Signed assemblies | Strong-name sign all assemblies |
| Model versioning | Semantic versioning for managed solutions |
| Dependency declaration | Declare all model references in ModelManifest.xml |
| Upgrade testing | Test against multiple D365 F&O versions |

---

## 28.3 Financial Tags

Financial tags classify transactions for reporting and analysis:

- **Purpose**: Categorize financial data beyond the chart of accounts
- **Implementation**: Tag fields on ledger tables
- **Usage**: Filter and group financial reports by tag values
- **Development**: Use `FinancialTag` EDT and related tables when building finance extensions

---

## 28.4 Date Effectivity

Date effectivity allows data to be version-dated — different values apply to different date ranges:

| Concept | Description |
|---|---|
| Effective date | The date from which a record is effective |
| Expiration date | The date until which a record is effective |
| Date-effective tables | Tables with `EffectiveFrom` and `EffectiveTo` fields |
| Effective query | Queries that return records effective on a specific date |

**Use Case:** Price lists, tax rates, and organizational hierarchies change over time. Date effectivity lets you maintain historical data while supporting current values.

---

## 28.5 Security Hardening Checklist

```
□ All custom tables have appropriate SaveDataPerCompany settings
□ All custom forms have security roles assigned via MenuItem security
□ Field-level permissions restrict sensitive data access
□ XDS policies implemented for row-level security
□ Segregation of Duties (SoD) rules validated
□ Configuration keys gate feature access
□ Audit fields (CreatedBy, ModifiedBy, CreatedDateTime, ModifiedDateTime) on all custom tables
□ No hardcoded credentials in X++ code
□ Secrets stored in Azure Key Vault, not in code
```

---

---
---


D365 F&O provides a built-in workflow framework for routing business documents through approval processes. The VSI Asset Management codebase uses it extensively for asset requests, retirements, and maintenance repairs.

# Chapter 29: Workflow Architecture

## 29.1 Workflow Architecture Components

| Component | Purpose | Base Class / Type |
|---|---|---|
| Workflow Document | Defines the query and context exposed to the workflow | `WorkflowDocument` |
| Workflow Type | Top-level container; groups approvals, tasks, and outcomes | `WorkflowType` AOT node |
| Approval | Approve/reject/request-change step | `WorkflowApproval` AOT node |
| Task | Work item assigned to a user (e.g., repair task) | `WorkflowTask` AOT node |
| Event Handler | Reacts to workflow lifecycle events | `WorkflowElementEventHandler`, `WorkflowEventHandler` |
| Menu Item Action | User action on a work item (Approve, Reject, Delegate, Resubmit) | `WorkflowWorkItemActionManager` |

## 29.2 Workflow Document

The workflow document exposes the business record to the workflow framework via a query:

```xpp
class VSIAssetRequestWorkflowDocument extends WorkflowDocument
{
    public queryName getQueryName()
    {
        return queryStr(VSIAssetRequestWorkflowQuery);
    }
}
```

### Key Methods

- **`getQueryName()`** — Returns the AOT query that supplies workflow context fields.
- **`getContextTableId()` / `getContextRecId()`** — Used by event handlers to identify the document record.

## 29.3 Workflow Event Handlers

Workflow event handlers implement one or more interfaces:

| Interface | Method | Fires When |
|---|---|---|
| `WorkflowStartedEventHandler` | `started(WorkflowEventArgs)` | Workflow begins |
| `WorkflowCompletedEventHandler` | `completed(WorkflowEventArgs)` | Workflow finishes |
| `WorkflowCanceledEventHandler` | `canceled(WorkflowEventArgs)` | Workflow is canceled/recall |
| `WorkflowElementStartedEventHandler` | `started(WorkflowElementEventArgs)` | Element (approval/task) begins |
| `WorkflowElementCompletedEventHandler` | `completed(WorkflowElementEventArgs)` | Element completes |
| `WorkflowElementDeniedEventHandler` | `denied(WorkflowElementEventArgs)` | Element rejected |
| `WorkflowElementReturnedEventHandler` | `returned(WorkflowElementEventArgs)` | Element returned to submitter |
| `WorkflowElemChangeRequestedEventHandler` | `changeRequested(WorkflowElementEventArgs)` | Change requested |
| `WorkflowWorkItemsCreatedEventHandler` | `created(WorkflowWorkItemsEventArgs)` | Work items created |

### Example: Request Approval Event Handler

```xpp
public final class VSIAssetRequestApprovalEventHandler implements
    WorkflowElementCanceledEventHandler,
    WorkflowElemChangeRequestedEventHandler,
    WorkflowElementCompletedEventHandler,
    WorkflowElementReturnedEventHandler,
    WorkflowElementStartedEventHandler,
    WorkflowWorkItemsCreatedEventHandler
{
    public void started(WorkflowElementEventArgs _workflowElementEventArgs)
    {
        VSIAssetRequest::changeStatusByRecId(
            _workflowElementEventArgs.parmWorkflowContext().parmRecId(),
            VSIRequestStatus::PendingApproval);
    }

    public void completed(WorkflowElementEventArgs _workflowElementEventArgs)
    {
        WorkflowContext context =
            _workflowElementEventArgs.parmWorkflowContext();

        VSIWorkerId approver =
            VSIWorkflowActorHelper::approverWorkerIdOrBlank(
                context.parmTableId(),
                context.parmRecId());

        VSIAssetRequest::changeStatusByRecId(
            context.parmRecId(),
            VSIRequestStatus::Approved,
            approver);

        info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowApproved");
    }

    public void changeRequested(WorkflowElementEventArgs _workflowElementEventArgs)
    {
        VSIAssetRequest::changeStatusByRecId(
            _workflowElementEventArgs.parmWorkflowContext().parmRecId(),
            VSIRequestStatus::Draft);

        info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowChangeRequested");
    }

    public void returned(WorkflowElementEventArgs _workflowElementEventArgs)
    {
        VSIAssetRequest::changeStatusByRecId(
            _workflowElementEventArgs.parmWorkflowContext().parmRecId(),
            VSIRequestStatus::Rejected);

        info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowRejected");
    }

    public void canceled(WorkflowElementEventArgs _workflowElementEventArgs)
    {
        VSIAssetRequest::changeStatusByRecId(
            _workflowElementEventArgs.parmWorkflowContext().parmRecId(),
            VSIRequestStatus::Draft);

        info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowCanceled");
    }

    public void created(WorkflowWorkItemsEventArgs _workflowWorkItemsEventArgs)
    {
    }
}
```

### Key Pattern: Status Transition Guard

Notice how `changeStatusByRecId` uses `VSIDocumentStatusChangeContext` to guard direct status updates:

```xpp
using (VSIDocumentStatusChangeContext context = new VSIDocumentStatusChangeContext())
{
    request.RequestStatus = _newStatus;
    request.update();
}
```

This ensures status changes only happen through the authorized workflow context, not via direct table updates.

## 29.4 Workflow Submit and Action Managers

### Submit from a Form

```xpp
public static void main(Args _args)
{
    VSIAssetRequest request = _args.record() as VSIAssetRequest;
    WorkflowSubmitDialog submitDialog;

    if (!request || !request.validateForSubmission())
    {
        return;
    }

    submitDialog = WorkflowSubmitDialog::construct(
        _args.caller().getActiveWorkflowConfiguration());
    submitDialog.run();

    if (submitDialog.parmIsClosedOK())
    {
        try
        {
            ttsBegin;
            Workflow::activateFromWorkflowType(
                workflowTypeStr(VSIAssetRequestWorkflow),
                request.RecId,
                submitDialog.parmWorkflowComment(),
                NoYes::No);
            VSIAssetRequest::changeStatusByRecId(
                request.RecId,
                VSIRequestStatus::PendingApproval);
            ttsCommit;
            info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowSubmitted");
        }
        catch (Exception::Error)
        {
            error("@VSIAssetManagmentLabelFile:VSIWorkflowSubmitFailed");
        }
    }

    _args.caller().updateWorkflowControls();
}
```

### Resubmit Action

```xpp
public static void main(Args _args)
{
    VSIAssetRequest request = _args.record() as VSIAssetRequest;
    WorkflowWorkItemTable workItem = _args.caller().getActiveWorkflowWorkItem();
    WorkflowWorkItemActionDialog actionDialog;

    if (!request || !workItem.RecId || !request.validateForSubmission())
    {
        return;
    }

    actionDialog = WorkflowWorkItemActionDialog::construct(
        workItem,
        WorkflowWorkItemActionType::Resubmit,
        new MenuFunction(_args.menuItemName(), _args.menuItemType()));
    actionDialog.run();

    if (actionDialog.parmIsClosedOK())
    {
        try
        {
            ttsBegin;
            WorkflowWorkItemActionManager::dispatchWorkItemAction(
                workItem,
                actionDialog.parmWorkflowComment(),
                actionDialog.parmTargetUser(),
                WorkflowWorkItemActionType::Resubmit,
                _args.menuItemName());
            VSIAssetRequest::changeStatusByRecId(
                request.RecId,
                VSIRequestStatus::PendingApproval);
            ttsCommit;
            info("@VSIAssetManagmentLabelFile:VSIAssetRequestWorkflowResubmitted");
        }
        catch (Exception::Error)
        {
            error("@VSIAssetManagmentLabelFile:VSIWorkflowSubmitFailed");
        }
    }

    _args.caller().updateWorkflowControls();
}
```

## 29.5 Workflow-Enabled Forms

A form participates in workflow when it sets:

| Property | Value |
|---|---|
| `WorkflowDataSource` | The table bound to the workflow document |
| `WorkflowEnabled` | `Yes` |
| `WorkflowType` | The workflow type name (e.g., `VSIAssetRequestWorkflow`) |

The form's action pane typically includes Submit, Approve, Reject, Delegate, Request Change, and Resubmit menu item buttons bound to the workflow action menu items.

---


Number sequences generate unique identifiers for records. VSI Asset Management registers its own module and references eight data types.

# Chapter 30: Number Sequences

## 30.1 Registering a Number Sequence Module

```xpp
public class VSIAssetNumberSeqModule extends NumberSeqApplicationModule
{
    protected void loadModule()
    {
        this.createDatatype(
            extendedTypeNum(VSIVendorId),
            literalStr("@VSIAssetManagmentLabelFile:NumSeqHelpVendor"),
            999999, 1, true);
        // ... repeat for VSIWorkerId, VSIRequestId, VSIAssetId, ...
    }

    public NumberSeqModule numberSeqModule()
    {
        return NumberSeqModule::VSIAssetManagement;
    }

    [SubscribesTo(
        classStr(NumberSeqGlobal),
        delegateStr(NumberSeqGlobal, buildModulesMapDelegate))]
    static void buildModulesMapSubscriber(Map _numberSeqModuleNamesMap)
    {
        NumberSeqGlobal::addModuleToMap(
            classNum(VSIAssetNumberSeqModule),
            _numberSeqModuleNamesMap);
    }
}
```

### Key Methods

| Method | Purpose |
|---|---|
| `loadModule()` | Registers `NumberSeqDatatype` references for each EDT |
| `numberSeqModule()` | Returns the module enum value (`NumberSeqModule::VSIAssetManagement`) |
| `buildModulesMapSubscriber()` | Subscribes to the global module map delegate so the module appears in the Number Sequences form |

## 30.2 Number Sequence Reference API

```xpp
// Find a reference in the current company scope
NumberSeqReference ref = NumberSeqReference::findReference(
    extendedTypeNum(VSIAssetId),
    NumberSeqScopeFactory::createDataAreaScope(curExt()));

// Find in shared (global) scope
NumberSeqReference sharedRef = NumberSeqReference::findReference(
    extendedTypeNum(VSIVendorId),
    NumberSeqScopeFactory::createGlobalScope());

// Generate the next number
VSIAssetId nextId = NumberSeq::newGetNum(ref).num();

// Check if a reference exists
boolean exists = ref.RecId != 0;
```

### Scope Types

| Scope | Use Case |
|---|---|
| `createDataAreaScope(curExt())` | Company-specific sequences (default) |
| `createGlobalScope()` | Shared across all companies (e.g., VSIWorkerId, VSIVendorId) |

## 30.3 Number Sequence Form Handler in Forms

```xpp
public class VSIAssetDetails extends FormRun
{
    NumberSeqFormHandler numberSeqFormHandler;

    public NumberSeqFormHandler numberSeqFormHandler()
    {
        if (!numberSeqFormHandler)
        {
            numberSeqFormHandler = NumberSeqFormHandler::newForm(
                VSIAssetParameters::numRefAssetId().NumberSequenceId,
                element,
                VSIAsset_ds,
                fieldNum(VSIAsset, AssetId));
        }
        return numberSeqFormHandler;
    }

    public void close()
    {
        if (numberSeqFormHandler)
        {
            numberSeqFormHandler.formMethodClose();
        }
        super();
    }

    // Data source overrides:
    public void create(boolean _append = false)
    {
        element.numberSeqFormHandler().formMethodDataSourceCreatePre();
        super(_append);
        element.numberSeqFormHandler().formMethodDataSourceCreate();
    }

    public void write()
    {
        ttsBegin;
        super();
        element.numberSeqFormHandler().formMethodDataSourceWrite();
        ttsCommit;
    }

    public boolean validateWrite()
    {
        boolean ret = super();
        ret = element.numberSeqFormHandler().formMethodDataSourceValidateWrite(ret) && ret;
        return ret;
    }

    public void delete()
    {
        ttsBegin;
        element.numberSeqFormHandler().formMethodDataSourceDelete();
        super();
        ttsCommit;
    }

    public void linkActive()
    {
        element.numberSeqFormHandler().formMethodDataSourceLinkActive();
        super();
    }
}
```

### Handler Method Lifecycle

| Form DS Method | Handler Call | Purpose |
|---|---|---|
| `create()` | `formMethodDataSourceCreatePre()` then `formMethodDataSourceCreate()` | Reserve then confirm the number |
| `write()` | `formMethodDataSourceWrite()` | Confirm on save |
| `validateWrite()` | `formMethodDataSourceValidateWrite(ret)` | Validate sequence state |
| `delete()` | `formMethodDataSourceDelete()` | Release on delete |
| `close()` | `formMethodClose()` | Release any reserved numbers |
| `linkActive()` | `formMethodDataSourceLinkActive()` | Sync when record changes |

## 30.4 Number Sequence Targets

`VSINumberSeqTargets` maps each EDT to the table field it populates:

```xpp
public static Description usedOn(ExtendedTypeId _typeId)
{
    switch (_typeId)
    {
        case extendedTypeNum(VSIAssetId): return 'VSIAsset.AssetId';
        case extendedTypeNum(VSIRequestId): return 'VSIAssetRequest.RequestId';
        // ...
    }
    return '';
}
```

---


DMF enables data import/export through staging tables and data entities.

| `TransferStatus` | `DMFTransferStatus` (Pending, etc.) |

Each staging table has a foreign-key relation to its data entity via the primary key fields.

## 25.3 Custom Field Mapping on Import

`VSIVendorEntity` and `VSIWorkerEntity` override `mapEntityToDataSource` to control ID assignment during import:

```xpp
public void mapEntityToDataSource(
    DataEntityRuntimeContext           _entityCtx,
    DataEntityDataSourceRuntimeContext _dataSourceCtx)
{
    super(_entityCtx, _dataSourceCtx);

    if (_dataSourceCtx.name() != dataEntityDataSourceStr(VSIVendorEntity, VSIVendor))
    {
        return;
    }

    VSIVendor vendor = _dataSourceCtx.getBuffer();

    switch (_entityCtx.getDatabaseOperation())
    {
        case DataEntityDatabaseOperation::Insert:
            vendor.VendorId = VSIVendorEntity::nextVendorId();
            break;
        case DataEntityDatabaseOperation::Update:
            vendor.VendorId = vendor.orig().VendorId;
            break;
    }
}

private static VSIVendorId nextVendorId()
{
    NumberSequenceReference reference = VSIAssetParameters::numRefVendorId();
    if (!reference.NumberSequenceId)
    {
        throw error(strFmt(
            "@VSIAssetManagmentLabelFile:ImportNumSeqNotSetUpInCompany",
            new DictType(extendedTypeNum(VSIVendorId)).label(),
            curExt()));
    }
    return NumberSeq::newGetNum(reference).num();
}
```

### Key Rules

- **Insert**: Generate the ID from the number sequence; ignore any ID in the import file.
- **Update**: Preserve the existing ID using `orig()`; ignore changes to the ID field.
- Throw an error if no number sequence is mapped in the current company.

## 25.4 Import/Export Flow

1. Create a **Definition Group** in Data management workspace.
2. Add the data entity to the group.
3. Generate mapping (auto-maps staging fields to entity fields).
4. Upload source file (CSV/Excel/XML).
5. **Staging**: Data lands in the staging table with `TransferStatus`.
6. **Validate**: Check staging errors before pushing to target.
7. **Push to target**: Moves data from staging to the target table via `mapEntityToDataSource`.

---


# Chapter 31: Form Patterns

## 31.1 List Page Pattern (`ListPage`)

Used for `VSIAssetListPage`. Key elements:

- **Action Pane** with button groups for New, Details, Assign, Return, Reassign, Print Tag.
- **Custom Filter Group** with `CustomAndQuickFilters` pattern containing filter controls (TypeFilter, StatusFilter, LocationFilter, VendorFilter, CustodianFilter).
- **Grid** with `DefaultAction` set to the Details menu item button.
- **Parts** (FactBoxes) referenced via `AxFormPartReference`.

Filter controls typically call `executeQuery()` on `modified()`:

```xpp
public boolean modified()
{
    boolean ret = super();
    VSIAsset_ds.executeQuery();
    return ret;
}
```

### Data Source Init for Filters

```xpp
public void init()
{
    super();
    qbdsCustodian = this.queryBuildDataSource().addDataSource(tableNum(VSIAssetAssignmentHistory));
    qbdsCustodian.joinMode(JoinMode::ExistsJoin);
    qbdsCustodian.relations(false);
    qbdsCustodian.addLink(fieldNum(VSIAsset, AssetId), fieldNum(VSIAssetAssignmentHistory, AssetId));
    qbdsCustodian.addRange(fieldNum(VSIAssetAssignmentHistory, ReturnedDateTime))
        .value(SysQuery::value(utcDateTimeNull()));
    qbdsCustodian.enabled(false);
}
```

## 31.2 Simple List Details — Grid Pattern (`SimpleListDetails-Grid`)

Used for `VSIAssetMaintenance`. Layout:

- **Navigation List Group** (`SidePanel` style) with a grid on the left.
- **Vertical Splitter** (`SplitterVerticalContainer`).
- **Details Header** (`FieldsFieldGroups` pattern).
- **Details Tab** (`FastTabs` style) with tab pages for Fault, Repair, etc.

## 31.3 FactBox Forms

Two patterns:

| Pattern | Use | Example |
|---|---|---|
| `FormPartFactboxGrid` | List of related records | `VSIAssetAssignmentFactBox` (assignment history grid) |
| `FormPartFactboxCard` | Key-value summary | `VSIAssetLicenseFactBox` (seat count, renewal date) |

FactBoxes are referenced from list pages via `AxFormPartReference`:
```xml
<AxFormPartReference>
    <Name>AssignmentPart</Name>
    <DataSource>VSIAsset</DataSource>
    <MenuItemName>VSIAssetAssignmentFactBox</MenuItemName>
</AxFormPartReference>
```

## 31.4 Tree Form Pattern (`SimpleListDetails-Tree`)

Used for `VSIFunctionalLocation`. Key mechanics:

- **Tree Control** (`FormTreeControl`) on the left navigation panel.
- Recursive tree building in `buildTree()`:

```xpp
public void buildTree(RefRecId _selectRecId = 0)
{
    VSIFunctionalLocation loc;
    List rows = new List(Types::Container);
    Set knownIds = new Set(Types::String);
    Map childrenByParent = new Map(Types::String, Types::Class);

    while select RecId, LocationId, Name, ParentLocationId from loc
        order by loc.Name
    {
        rows.addEnd([loc.RecId, loc.LocationId, loc.Name, loc.ParentLocationId]);
        knownIds.add(loc.LocationId);
    }

    // ... build parent->children map ...
    this.addNodes(0, '', childrenByParent);
    this.selectNode(_selectRecId);
}
```

- **Selection changed** syncs the data source cursor:
```xpp
public void selectionChanged(FormTreeItem _oldItem, FormTreeItem _newItem, FormTreeSelect _how)
{
    RefRecId targetRecId = _newItem.data();
    VSIFunctionalLocation target;
    select firstonly target where target.RecId == targetRecId;
    VSIFunctionalLocation_ds.findRecord(target);
    element.selectNode(VSIFunctionalLocation.RecId);
}
```

## 31.5 Dialog Field Overrides

Register override methods in `postRun()` of a UI builder:

```xpp
public void postRun()
{
    super();
    checkRequestsField.registerOverrideMethod(
        methodStr(FormCheckBoxControl, modified),
        methodStr(VSIAssetIntegrityAuditBatchUIBuilder, checkRequestsModified),
        this);
}

public boolean checkRequestsModified(FormCheckBoxControl _control)
{
    approvedDaysField.enabled(_control.value() == NoYes::Yes);
    return true;
}
```

## 31.6 MultiSelectionHelper

Used for multi-select ranges on tag label reports:

```xpp
MultiSelectionHelper selection = MultiSelectionHelper::construct();
selection.parmDatasource(formDataSource);
VSIAsset asset = selection.getFirst();
while (asset)
{
    rangeValue = rangeValue ? rangeValue + ',' + queryValue(asset.AssetId) : queryValue(asset.AssetId);
    asset = selection.getNext();
}
```

## 31.7 SysQueryRangeUtil — Advanced Query Ranges

`SysQueryRangeUtil` provides static methods for building complex query ranges, commonly used in VSI reports and batch jobs for date filtering:

### Common Date Range Methods

| Method | Syntax | Example Result |
|---|---|---|
| `dayRange(_fromDate, _toDate)` | `SysQueryRangeUtil::dayRange(today(), today())` | `11/11/2026..11/11/2026` |
| `monthRange(_fromDate, _toDate)` | `SysQueryRangeUtil::monthRange(DateTimeUtil::date(DateTimeUtil::addMonths(DateTimeUtil::utcNow(), -1)), today())` | `10/1/2026..11/30/2026` |
| `yearRange(_fromDate, _toDate)` | `SysQueryRangeUtil::yearRange(DateTimeUtil::date(DateTimeUtil::addYears(DateTimeUtil::utcNow(), -1)), today())` | `1/1/2025..12/31/2026` |
| `dateRange(_fromDate, _toDate)` | `SysQueryRangeUtil::dateRange(systemDateGet(), systemDateGet())` | `11/11/2026..11/11/2026` |
| `greaterThanDate(_date)` | `SysQueryRangeUtil::greaterThanDate(systemDateGet())` | `>11/11/2026` |
| `lessThanDate(_date)` | `SysQueryRangeUtil::lessThanDate(systemDateGet())` | `<11/11/2026` |

### VSI Report Usage Pattern

```xpp
public class VSIAssetIntegrityAuditReportDP extends SrsReportDataProviderPreProcessTmp
{
    VSIAssetIntegrityAuditTmp tmp;

    public void processReport()
    {
        VSIAssetIntegrityAuditContract contract = this.parmDataContract();
        QueryBuildRange qbr;

        // Date range filter on assignment date
        qbr = this.query().dataSourceTable(tableNum(VSIAssetAssignmentHistory))
            .addRange(fieldNum(VSIAssetAssignmentHistory, AssignedDateTime));
        qbr.value(SysQueryRangeUtil::dateRange(
            contract.parmFromDate(), 
            contract.parmToDate()));

        // Status filter using enum range
        qbr = this.query().dataSourceTable(tableNum(VSIAsset))
            .addRange(fieldNum(VSIAsset, Status));
        qbr.value(SysQueryRangeUtil::enumRange(
            VSIAssetStatus::Assigned, 
            VSIAssetStatus::Maintenance));

        // Multi-value range for asset types
        qbr = this.query().dataSourceTable(tableNum(VSIAsset))
            .addRange(fieldNum(VSIAsset, AssetTypeId));
        qbr.value(SysQueryRangeUtil::inList([
            'Laptop', 'Monitor', 'Mobile', 'DockingStation']));

        // Complex: date range with time component
        qbr = this.query().dataSourceTable(tableNum(VSIAssetStatusHistory))
            .addRange(fieldNum(VSIAssetStatusHistory, ChangedDateTime));
        qbr.value(strFmt('%1..%2',
            DateTimeUtil::toStr(contract.parmFromDateTime()),
            DateTimeUtil::toStr(contract.parmToDateTime())));

        super();
    }
}
```

### Enum Range Helper

```xpp
/// <summary>
/// Builds a query range for enum values from _from to _to inclusive.
/// </summary>
public static str enumRange(int _from, int _to)
{
    str range = '';
    for (int i = _from; i <= _to; i++)
    {
        range += (strLen(range) ? ',' : '') + int2str(i);
    }
    return range;
}
```

### InList Helper for Multiple Values

```xpp
/// <summary>
/// Builds a comma-separated query range from a container of values.
/// </summary>
public static str inList(container _values)
{
    str result = '';
    for (int i = 1; i <= conLen(_values); i++)
    {
        result += (strLen(result) ? ',' : '') + queryValue(conPeek(_values, i));
    }
    return result;
}
```

### DateTime Range with Time Precision

For datetime fields, use the full datetime format:

```xpp
qbr.value(strFmt('%1..%2',
    DateTimeUtil::toStr(DateTimeUtil::addDays(DateTimeUtil::utcNow(), -7)), // 7 days ago
    DateTimeUtil::toStr(DateTimeUtil::utcNow())));
```

**Output format:** `11/4/2026 14:30:00..11/11/2026 14:30:00`

### Performance Tip: Range vs. Multiple Ranges

| Approach | Query Plan | Use When |
|---|---|---|
| Single `..` range | Single seek | Contiguous values |
| Multiple comma values | Multiple seeks | Sparse/discrete values |
| `inList()` with 100+ values | Consider temp table | Large discrete sets |

---

## 31.8 Activity — Build a Report with Dynamic Ranges

**Objective:** Create a report data provider that uses `SysQueryRangeUtil` for all filter types.

**Requirements:**
1. Contract with FromDate, ToDate, AssetStatus (enum), AssetTypes (container)
2. Use `dateRange()`, `enumRange()`, `inList()` in `processReport()`
3. Handle empty filter values (no range applied)
4. Test with various combinations

**Hints:**
- Check `contract.parmFromDate()` before adding range
- Use `SysQueryRangeUtil::dateRange()` for date-only fields
- Use `DateTimeUtil::toStr()` for datetime fields

**Ideal Solution Pattern:**

```xpp
public void processReport()
{
    MyContract contract = this.parmDataContract();
    QueryBuildDataSource qbds = this.query().dataSourceTable(tableNum(MyTable));
    QueryBuildRange qbr;

    // Optional date range
    if (contract.parmFromDate() && contract.parmToDate())
    {
        qbr = qbds.addRange(fieldNum(MyTable, TransDate));
        qbr.value(SysQueryRangeUtil::dateRange(
            contract.parmFromDate(), contract.parmToDate()));
    }

    // Optional enum range
    if (contract.parmFromStatus() != MyStatus::None || 
        contract.parmToStatus() != MyStatus::None)
    {
        qbr = qbds.addRange(fieldNum(MyTable, Status));
        qbr.value(SysQueryRangeUtil::enumRange(
            contract.parmFromStatus(), contract.parmToStatus()));
    }

    // Optional multi-value list
    if (conLen(contract.parmTypeIds()) > 0)
    {
        qbr = qbds.addRange(fieldNum(MyTable, TypeId));
        qbr.value(SysQueryRangeUtil::inList(contract.parmTypeIds()));
    }

    super();
}
```

---


# Chapter 32: VSI Patterns

## 32.1 Action Center Notifications

`VSIAssetNotificationHelper` sends notifications to asset administrators via `SystemNotificationsManager`:

```xpp
public static boolean notifyUsers(List _userIds, str _title, str _message)
{
    SystemNotificationDataContract notification = new SystemNotificationDataContract();
    ListEnumerator enumerator = _userIds.getEnumerator();
    int userIndex;

    while (enumerator.moveNext())
    {
        userIndex++;
        notification.Users().value(userIndex, enumerator.current());
    }

    notification.Title(_title);
    notification.Message(VSIAssetNotificationHelper::truncate(_message));
    notification.RuleId(VSIAssetNotificationHelper::RuleId);
    notification.ExpirationDateTime(
        DateTimeUtil::addHours(DateTimeUtil::utcNow(), VSIBatchConstants::NotificationExpiryHours));

    SystemNotificationsManager::AddSystemNotification(notification);
    return true;
}
```

### Message Truncation

```xpp
private static str truncate(str _message)
{
    if (strLen(_message) <= VSIBatchConstants::MaxNotificationLength)
    {
        return _message;
    }
    return subStr(_message, 1, VSIBatchConstants::MaxNotificationLength - 3) + '...';
}
```

### Finding Administrator Users

```xpp
public static List assetAdministratorUserIds()
{
    List userIds = new List(Types::String);
    VSIWorker worker;
    UserInfo userInfo;

    while select PlatformUserId from worker
        order by worker.PlatformUserId
        where worker.IsAssetAdmin == NoYes::Yes
           && worker.EmploymentStatus == VSIEmploymentStatus::Active
           && worker.PlatformUserId != ''
        exists join userInfo
            where userInfo.id == worker.PlatformUserId
               && userInfo.enable == 1
    {
        userIds.addEnd(worker.PlatformUserId);
    }
    return userIds;
}
```

## 32.2 IDisposable Status Change Context

`VSIAssetStatusChangeContext` and `VSIDocumentStatusChangeContext` enforce that status changes only occur within an authorized scope:

```xpp
public final class VSIAssetStatusChangeContext implements System.IDisposable
{
    private static VSIAssetStatusChangeContext instance;

    public void new()
    {
        if (instance)
        {
            throw error("@VSIAssetManagmentLabelFile:StatusContextNested");
        }
        instance = this;
    }

    public void dispose()
    {
        instance = null;
    }

    public static boolean isActive()
    {
        return instance != null;
    }
}
```

### Usage in `validateWrite`/`update`

```xpp
public void update()
{
    if (this.Status != this.orig().Status && !VSIAssetStatusChangeContext::isActive())
    {
        throw error("@VSIAssetManagmentLabelFile:DocumentStatusChangeNotAllowed");
    }
    super();
}
```

### Usage in `VSIAssetStatusHelper::changeStatus`

```xpp
using (VSIAssetStatusChangeContext context = new VSIAssetStatusChangeContext())
{
    asset.Status = _newStatus;
    asset.update();
}
VSIAssetStatusHistory::log(...);
```

This pattern ensures status transitions are auditable and cannot be bypassed by direct table updates.

## 32.3 VSIAssetStatusHelper — Complete Implementation

The `VSIAssetStatusHelper` class encapsulates the full status change workflow including multi-field updates, history logging, and cross-company support:

```xpp
public final class VSIAssetStatusHelper
{
    /// <summary>
    /// Changes the asset status with full audit trail and validation.
    /// </summary>
    /// <param name="_asset">The asset buffer to update</param>
    /// <param name="_newStatus">The new status enum value</param>
    /// <param name="_workerId">Optional worker ID for assignment context</param>
    /// <param name="_companyId">Optional company for cross-company operations</param>
    public static void changeStatus(
        VSIAsset _asset,
        VSIAssetStatus _newStatus,
        VSIWorkerId _workerId = '',
        str _companyId = '')
    {
        if (!_asset)
        {
            throw error("@VSIAssetManagmentLabelFile:AssetNotFound");
        }

        if (_asset.Status == _newStatus)
        {
            return; // No change needed
        }

        // Validate status transition
        VSIAssetStatusHelper::validateTransition(_asset.Status, _newStatus);

        str company = _companyId ? _companyId : _asset.dataAreaId;

        changecompany(company)
        {
            using (VSIAssetStatusChangeContext context = new VSIAssetStatusChangeContext())
            {
                // Capture previous status for history
                VSIAssetStatus oldStatus = _asset.Status;

                // Update asset status and related fields
                _asset.Status = _newStatus;
                
                // Update assignment-related fields based on status
                switch (_newStatus)
                {
                    case VSIAssetStatus::Assigned:
                        _asset.AssignedWorkerId = _workerId;
                        _asset.AssignedDateTime = DateTimeUtil::utcNow();
                        break;
                    case VSIAssetStatus::Returned:
                        _asset.AssignedWorkerId = '';
                        _asset.ReturnedDateTime = DateTimeUtil::utcNow();
                        break;
                    case VSIAssetStatus::Retired:
                        _asset.RetiredDateTime = DateTimeUtil::utcNow();
                        break;
                }

                _asset.update();

                // Log status history with full context
                VSIAssetStatusHistory::log(
                    _asset.RecId,
                    oldStatus,
                    _newStatus,
                    _workerId,
                    VSIAssetStatusHistoryReason::ManualChange);
            }
        }

        // Send notification if configured
        if (VSIAssetParameters::find().NotifyOnStatusChange)
        {
            VSIAssetNotificationHelper::notifyStatusChange(_asset, oldStatus, _newStatus);
        }
    }

    /// <summary>
    /// Validates that a status transition is allowed.
    /// </summary>
    private static void validateTransition(VSIAssetStatus _from, VSIAssetStatus _to)
    {
        // Define valid transitions using a transition matrix
        Map validTransitions = new Map(Types::Integer, Types::Container);
        validTransitions.insert(VSIAssetStatus::Available, [VSIAssetStatus::Assigned, VSIAssetStatus::Maintenance, VSIAssetStatus::Retired]);
        validTransitions.insert(VSIAssetStatus::Assigned, [VSIAssetStatus::Available, VSIAssetStatus::Returned, VSIAssetStatus::Maintenance]);
        validTransitions.insert(VSIAssetStatus::Maintenance, [VSIAssetStatus::Available, VSIAssetStatus::Retired]);
        validTransitions.insert(VSIAssetStatus::Returned, [VSIAssetStatus::Available, VSIAssetStatus::Assigned]);
        validTransitions.insert(VSIAssetStatus::Retired, []); // Terminal state

        container allowed = validTransitions.lookup(_from);
        if (!conFind(allowed, _to))
        {
            throw error(strFmt(
                "@VSIAssetManagmentLabelFile:InvalidStatusTransition",
                enum2str(_from), enum2str(_to)));
        }
    }
}
```

### VSIAssetStatusHistory — Audit Trail Logging

```xpp
public static void log(
    RecId _assetRecId,
    VSIAssetStatus _fromStatus,
    VSIAssetStatus _toStatus,
    VSIWorkerId _workerId = '',
    VSIAssetStatusHistoryReason _reason = VSIAssetStatusHistoryReason::ManualChange)
{
    VSIAssetStatusHistory history;
    
    history.clear();
    history.AssetRecId = _assetRecId;
    history.FromStatus = _fromStatus;
    history.ToStatus = _toStatus;
    history.WorkerId = _workerId;
    history.Reason = _reason;
    history.ChangedBy = curUserId();
    history.ChangedDateTime = DateTimeUtil::utcNow();
    history.DataAreaId = curExt();
    
    history.insert();
}
```

---

## 32.4 VSIAssetNotificationHelper — Complete Pattern

The notification helper demonstrates production-ready patterns for the Action Center:

### Full notifyUsers Implementation

```xpp
public static boolean notifyUsers(
    List _userIds, 
    str _title, 
    str _message,
    RecId _referenceRecId = 0,
    TableId _referenceTableId = 0)
{
    if (!_userIds || _userIds.elements() == 0)
    {
        return false;
    }

    if (strLen(_title) == 0 || strLen(_message) == 0)
    {
        return false;
    }

    SystemNotificationDataContract notification = new SystemNotificationDataContract();
    ListEnumerator enumerator = _userIds.getEnumerator();
    int userIndex;

    while (enumerator.moveNext())
    {
        userIndex++;
        notification.Users().value(userIndex, enumerator.current());
    }

    notification.Title(VSIAssetNotificationHelper::truncate(_title));
    notification.Message(VSIAssetNotificationHelper::truncate(_message));
    notification.RuleId(VSIAssetNotificationHelper::RuleId);
    notification.ExpirationDateTime(
        DateTimeUtil::addHours(
            DateTimeUtil::utcNow(), 
            VSIBatchConstants::NotificationExpiryHours));

    // Optional: Link notification to a specific record
    if (_referenceRecId && _referenceTableId)
    {
        notification.MenuItemName(menuItemDisplayStr(VSIAssetDetails));
        notification.MenuItemParameters(strFmt("%1:%2", _referenceTableId, _referenceRecId));
    }

    SystemNotificationsManager::AddSystemNotification(notification);
    return true;
}
```

### Status Change Notification Wrapper

```xpp
public static void notifyStatusChange(
    VSIAsset _asset,
    VSIAssetStatus _fromStatus,
    VSIAssetStatus _toStatus)
{
    List adminIds = VSIAssetNotificationHelper::assetAdministratorUserIds();
    
    if (adminIds.elements() == 0)
    {
        return;
    }

    str title = strFmt(
        "@VSIAssetManagmentLabelFile:AssetStatusChangeTitle",
        _asset.AssetId);

    str message = strFmt(
        "@VSIAssetManagmentLabelFile:AssetStatusChangeMessage",
        _asset.AssetId,
        enum2str(_fromStatus),
        enum2str(_toStatus),
        _asset.AssignedWorkerId);

    VSIAssetNotificationHelper::notifyUsers(
        adminIds,
        title,
        message,
        _asset.RecId,
        tableNum(VSIAsset));
}
```

### Administrator Lookup with PlatformUserId Join

The pattern for finding enabled administrators using an `exists join` with `UserInfo`:

```xpp
public static List assetAdministratorUserIds()
{
    List userIds = new List(Types::String);
    VSIWorker worker;
    UserInfo userInfo;

    while select PlatformUserId from worker
        order by worker.PlatformUserId
        where worker.IsAssetAdmin == NoYes::Yes
           && worker.EmploymentStatus == VSIEmploymentStatus::Active
           && worker.PlatformUserId != ''
        exists join userInfo
            where userInfo.id == worker.PlatformUserId
               && userInfo.enable == 1
    {
        userIds.addEnd(worker.PlatformUserId);
    }
    return userIds;
}
```

**Key Points:**
- **`exists join`** — More efficient than `join` when you only need to verify existence; doesn't return UserInfo fields
- **`PlatformUserId`** — Links the worker to the AAD user; must not be empty
- **`UserInfo.enable == 1`** — Filters to only active/enabled users
- **Ordering** — Consistent ordering for deterministic notification delivery

### Message Truncation with Constant

```xpp
private static str truncate(str _message)
{
    if (strLen(_message) <= VSIBatchConstants::MaxNotificationLength)
    {
        return _message;
    }
    return subStr(_message, 1, VSIBatchConstants::MaxNotificationLength - 3) + '...';
}
```

---

## 32.5 Multi-Company Notification Pattern

For cross-company notifications (e.g., batch jobs running across companies):

```xpp
public static void notifyAdminsCrossCompany(
    str _title,
    str _message,
    container _companyIds = conNull())
{
    container companies = _companyIds ? _companyIds : VSIAssetNotificationHelper::getAllCompanies();
    
    List allAdminIds = new List(Types::String);
    
    for (int i = 1; i <= conLen(companies); i++)
    {
        str company = conPeek(companies, i);
        
        changecompany(company)
        {
            List adminIds = VSIAssetNotificationHelper::assetAdministratorUserIds();
            ListEnumerator enum = adminIds.getEnumerator();
            while (enum.moveNext())
            {
                // Prefix with company to avoid duplicates across companies
                str qualifiedId = strFmt("%1\\%2", company, enum.current());
                if (!allAdminIds.in(qualifiedId))
                {
                    allAdminIds.addEnd(qualifiedId);
                }
            }
        }
    }
    
    if (allAdminIds.elements() > 0)
    {
        VSIAssetNotificationHelper::notifyUsers(allAdminIds, _title, _message);
    }
}

private static container getAllCompanies()
{
    DataArea dataArea;
    container result;
    while select Id from dataArea where dataArea.IsVirtual == NoYes::No
    {
        result += [dataArea.Id];
    }
    return result;
}
```

---

## 32.6 Activity — Extend Status Change Context

**Objective:** Create a `VSIDocumentStatusChangeContext` that mirrors `VSIAssetStatusChangeContext` but works for any document type (requests, retirements, maintenance).

**Requirements:**
1. Generic singleton context class implementing `System.IDisposable`
2. Accept a table ID and record ID in constructor for context tracking
3. Provide `isActive()` and `getContextTableId()` / `getContextRecId()` methods
4. Integrate with `VSIAssetRequest::update()` to guard status changes

**Hints:**
- Use a static `Map` keyed by table ID to support nested contexts for different tables
- Throw error if nested context detected for same table
- Call `VSIAssetRequest::changeStatusByRecId()` from workflow event handlers

**Ideal Solution:**

```xpp
public final class VSIDocumentStatusChangeContext implements System.IDisposable
{
    private static Map activeContexts; // Map<TableId, VSIDocumentStatusChangeContext>
    private TableId contextTableId;
    private RecId contextRecId;

    static void new()
    {
        activeContexts = new Map(Types::Integer, Types::Class);
    }

    private void new(TableId _tableId, RecId _recId)
    {
        if (activeContexts.lookup(_tableId))
        {
            throw error("@VSIAssetManagmentLabelFile:StatusContextNested");
        }
        
        contextTableId = _tableId;
        contextRecId = _recId;
        activeContexts.insert(_tableId, this);
    }

    public static VSIDocumentStatusChangeContext create(TableId _tableId, RecId _recId)
    {
        return new VSIDocumentStatusChangeContext(_tableId, _recId);
    }

    public void dispose()
    {
        activeContexts.remove(contextTableId);
    }

    public static boolean isActive(TableId _tableId = 0)
    {
        return _tableId 
            ? activeContexts.lookup(_tableId) != null 
            : !activeContexts.isEmpty();
    }

    public static TableId getContextTableId()
    {
        MapEnumerator enum = activeContexts.getEnumerator();
        if (enum.moveNext())
        {
            return enum.currentKey();
        }
        return 0;
    }

    public static RecId getContextRecId()
    {
        MapEnumerator enum = activeContexts.getEnumerator();
        if (enum.moveNext())
        {
            return enum.currentValue().contextRecId;
        }
        return 0;
    }
}
```

---


# Chapter 33: Advanced Batch

## 33.1 SysOperation Batch Pattern

VSI Asset Management uses `SysOperationServiceController` / `SysOperationServiceBase` for all batch operations:

| Class | Purpose |
|---|---|
| `VSIAssetIntegrityAuditBatchController` | Controller for integrity audit |
| `VSIAssetIntegrityAuditBatchService` | Service with `process()` and `processTask()` |
| `VSIAssetIntegrityAuditBatchContract` | Data contract with `SysOperationValidatable` |
| `VSIAssetIntegrityAuditBatchUIBuilder` | Dialog field overrides |
| `VSIAssetIntegrityAuditBatchTaskContract` | Runtime task contract |
| `VSIAssetIntegrityAuditBatchTaskController` | Task controller (`parmShowDialog(false)`) |

### Controller Pattern

```xpp
public static VSIAssetIntegrityAuditBatchController construct(
    SysOperationExecutionMode _executionMode = SysOperationExecutionMode::Synchronous)
{
    VSIAssetIntegrityAuditBatchController controller =
        new VSIAssetIntegrityAuditBatchController(
            classStr(VSIAssetIntegrityAuditBatchService),
            methodStr(VSIAssetIntegrityAuditBatchService, process),
            _executionMode);
    controller.parmDialogCaption("@VSIAssetManagmentLabelFile:VSIAssetIntegrityAuditBatchCaption");
    return controller;
}

public static void main(Args _args)
{
    VSIAssetIntegrityAuditBatchController controller = VSIAssetIntegrityAuditBatchController::construct();
    controller.parmArgs(_args);
    controller.startOperation();
}
```

## 33.2 Batch Runtime Tasks

For large datasets, the service dispatches multiple runtime tasks via `BatchHeader`:

```xpp
if (this.isExecutingInBatch())
{
    batchHeader = this.getCurrentBatchHeader();
}

// ... split recIds into bundles ...

batchHeader.addRuntimeTask(taskController, this.getCurrentBatchTask().RecId);
// ...
batchHeader.save();
```

### Task Controller (No Dialog)

```xpp
public static VSIAssetIntegrityAuditBatchTaskController construct()
{
    VSIAssetIntegrityAuditBatchTaskController controller =
        new VSIAssetIntegrityAuditBatchTaskController(
            classStr(VSIAssetIntegrityAuditBatchService),
            methodStr(VSIAssetIntegrityAuditBatchService, processTask),
            SysOperationExecutionMode::Synchronous);
    controller.parmShowDialog(false);
    return controller;
}
```

## 33.3 Deadlock & Concurrency Retry

`VSIAssetServiceHelper::execute` wraps service calls in retry logic:

```xpp
ttsBegin;
_processor.process(_operation, _request, _response);
ttsCommit;
```

Catch blocks handle:
- `Exception::Deadlock` — retry up to `#RetryNum` times
- `Exception::UpdateConflict` — retry up to `#RetryNum` times
- `Exception::Error` — mark failure, no retry

```xpp
catch (Exception::Deadlock)
{
    if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < #RetryNum)
    {
        retry;
    }
    _response.markFailure(...);
}
```

## 33.4 Cross-Company Queries

`VSIAssetInquiryService.processWorkerAssets` queries across all companies:

```xpp
container companies = this.companies(_request.parmAllCompanies());

while select crossCompany : companies assignment
    order by DataAreaId, AssignedDateTime
    where assignment.WorkerId == worker.WorkerId
       && assignment.ReturnedDateTime == utcDateTimeNull()
{
    // ...
}

private container companies(boolean _allCompanies)
{
    DataArea dataArea;
    container result;
    if (!_allCompanies)
    {
        return [curExt()];
    }
    while select Id from dataArea where dataArea.IsVirtual == NoYes::No
    {
        result += [dataArea.Id];
    }
    return result;
}
```

## 33.5 Batch Constants

`VSIBatchConstants` holds shared limits:

| Constant | Value | Purpose |
|---|---|---|
| `MaxRetries` | 5 | Max deadlock/update-conflict retries |
| `DefaultBundleSize` | 200 | Records per batch task |
| `MinBundleSize` | 10 | Minimum bundle size |
| `MaxBundleSize` | 5000 | Maximum bundle size |
| `NotificationExpiryHours` | 168 | Notification expiry (7 days) |
| `MaxNotificationLength` | 1000 | Max notification message length |
| `MaxDigestLines` | 20 | Max lines in notification digest |

## 33.6 VSIWorker Query Pattern — PlatformUserId Join

A common VSI pattern queries active workers with enabled PlatformUserId for notifications, assignments, and cross-company lookups:

```xpp
public static List getActiveAssetAdmins()
{
    List userIds = new List(Types::String);
    VSIWorker worker;
    UserInfo userInfo;

    while select PlatformUserId from worker
        order by worker.PlatformUserId
        where worker.IsAssetAdmin == NoYes::Yes
           && worker.EmploymentStatus == VSIEmploymentStatus::Active
           && worker.PlatformUserId != ''
        exists join userInfo
            where userInfo.id == worker.PlatformUserId
               && userInfo.enable == 1
    {
        userIds.addEnd(worker.PlatformUserId);
    }
    return userIds;
}
```

### Pattern Breakdown

| Element | Purpose |
|---|---|
| `PlatformUserId` | Links `VSIWorker` to Azure AD user (`UserInfo.id`) |
| `exists join` | Efficient existence check; doesn't return `UserInfo` fields |
| `UserInfo.enable == 1` | Filters to only active/enabled AD users |
| `EmploymentStatus == Active` | Business logic filter on worker record |
| `PlatformUserId != ''` | Guards against workers without AD linkage |

### Cross-Company Worker Lookup

For batch processes querying worker assignments across companies:

```xpp
public static container getWorkerAssetsCrossCompany(VSIWorkerId _workerId)
{
    container companies = VSIAssetInquiryService::getAllCompanies();
    container result;

    while select crossCompany : companies RecId, AssetId, DataAreaId
        from assignment
        join AssetId, AssetName from asset
            where asset.RecId == assignment.AssetRecId
                && asset.Status == VSIAssetStatus::Assigned
        where assignment.WorkerId == _workerId
           && assignment.ReturnedDateTime == utcDateTimeNull()
    {
        result += [assignment.RecId, assignment.AssetId, assignment.DataAreaId, asset.AssetName];
    }

    return result;
}

private static container getAllCompanies()
{
    DataArea dataArea;
    container result;
    while select Id from dataArea where dataArea.IsVirtual == NoYes::No
    {
        result += [dataArea.Id];
    }
    return result;
}
```

### Key Cross-Company Query Points

- **`crossCompany : companies`** — Specifies the company list for the query
- **`DataAreaId` in select list** — Returns the company for each row
- **`order by DataAreaId`** — Groups results by company for readability
- **Company list caching** — Cache the company container to avoid repeated `DataArea` queries

---

| Constant | Value | Purpose |
|---|---|---|
| `MaxRetries` | 5 | Max deadlock/update-conflict retries |
| `DefaultBundleSize` | 200 | Records per batch task |
| `MinBundleSize` | 10 | Minimum bundle size |
| `MaxBundleSize` | 5000 | Maximum bundle size |
| `NotificationExpiryHours` | 168 | Notification expiry (7 days) |
| `MaxNotificationLength` | 1000 | Max notification message length |
| `MaxDigestLines` | 20 | Max lines in notification digest |

---


# Chapter 34: Localization & Best Practices

## 34.1 Label Files

Labels are stored in `VSIAssetManagmentLabelFile.en-US.label.txt` and referenced via `@VSIAssetManagmentLabelFile:LabelId` syntax in X++ and XML metadata.

### Label File Format

```
ActionNotAllowed=Asset %1 can't be used for this action while its status is %2.
 ;Assignment action not allowed, %1 = asset tag, %2 = status
```

### Label File Metadata

`VSIAssetManagmentLabelFile_en-US.xml` maps the label file ID to the `.label.txt` resource file.

## 34.2 AppChecker / Best Practices

The project file (`VSIAssetManagement.rnrproj`) controls build behavior:

| Property | Value | Purpose |
|---|---|---|
| `RunAppCheckerRules` | `False` | Disable AppChecker rules during build |
| `LogAppcheckerDiagsAsErrors` | `False` | Don't log AppChecker diagnostics as errors |
| `GenerateCrossReferences` | `True` | Generate X++ cross-reference data |
| `GenerateFormAdaptors` | `False` | Disable form adaptor generation |
| `DBSyncInBuild` | `False` | Disable database sync during build |

## 34.3 Configuration Keys

Configuration keys gate feature visibility. The handbook mentions them in the hardening checklist but the codebase uses them implicitly through security roles and privileges rather than explicit `ConfigurationKey` properties on tables/forms.

**Best Practice:** Assign `ConfigurationKey` to custom tables and forms to allow administrators to enable/disable features without code changes.

---


# Chapter 35: Service Patterns

## 35.1 Service Pattern Overview

VSI Asset Management exposes two custom services:

| Service | Operations |
|---|---|
| `VSIAssetAssignmentService` | `assignAsset` |
| `VSIAssetInquiryService` | `getAssetDetails`, `getWorkerAssets` |

### Service Interface

```xpp
public interface VSIAssetServiceProcessor
{
    public void process(
        str _operation,
        VSIAssetServiceRequest _request,
        VSIAssetServiceResponse _response);
}
```

### Request / Response Contracts

```xpp
[DataContractAttribute]
public final class VSIAssetAssignRequestContract implements VSIAssetServiceRequest
{
    [DataMemberAttribute('AssetId')]
    public VSIAssetId parmAssetId(VSIAssetId _assetId = assetId) { ... }
    
    public str companyId() { return dataAreaId; }
}

[DataContractAttribute]
public final class VSIAssetAssignmentResponseContract implements VSIAssetServiceResponse
{
    [DataMemberAttribute('Success')]
    public boolean parmSuccess(boolean _success = success) { ... }
    
    public void markSuccess(str _message) { ... }
    public void markFailure(List _errors) { ... }
    public void setCompany(str _dataAreaId) { ... }
}
```

## 35.2 Shared Service Executor — Complete Implementation

`VSIAssetServiceHelper::execute` provides the common entry point with full retry logic, infolog capture, and cross-company support:

```xpp
public static void execute(
    VSIAssetServiceProcessor _processor,
    str _operation,
    VSIAssetServiceRequest _request,
    VSIAssetServiceResponse _response)
{
    int infologStart = infologLine();
    str company;
    int retryCount = 0;
    boolean success = false;

    try
    {
        if (!_request)
        {
            throw error("@VSIAssetManagmentLabelFile:ServiceRequestMissing");
        }

        company = VSIAssetServiceHelper::resolveCompany(_request.companyId());
        _response.setCompany(company);

        while (!success && retryCount <= VSIBatchConstants::MaxRetries)
        {
            try
            {
                changecompany(company)
                {
                    ttsBegin;
                    _processor.process(_operation, _request, _response);
                    ttsCommit;
                }
                success = true;
            }
            catch (Exception::Deadlock)
            {
                if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < VSIBatchConstants::MaxRetries)
                {
                    retryCount++;
                    continue; // Retry the transaction
                }
                throw; // Re-throw if max retries exceeded
            }
            catch (Exception::UpdateConflict)
            {
                if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < VSIBatchConstants::MaxRetries)
                {
                    retryCount++;
                    continue; // Retry the transaction
                }
                throw; // Re-throw if max retries exceeded
            }
        }
    }
    catch (Exception::Error)
    {
        // Capture infolog messages for the response
        str errorMessage = VSIAssetServiceHelper::getInfologText(infologStart);
        _response.markFailure(VSIAssetServiceHelper::stringToList(errorMessage));
    }
    catch
    {
        // Catch any other exception
        str errorMessage = VSIAssetServiceHelper::getInfologText(infologStart);
        if (strLen(errorMessage) == 0)
        {
            errorMessage = "@VSIAssetManagmentLabelFile:ServiceUnexpectedError";
        }
        _response.markFailure(VSIAssetServiceHelper::stringToList(errorMessage));
    }
}

/// <summary>
/// Resolves the company from the request, defaulting to current company.
/// </summary>
private static str resolveCompany(str _requestedCompany)
{
    str company = _requestedCompany ? _requestedCompany : curExt();
    
    // Validate company exists
    DataArea dataArea;
    select firstOnly Id from dataArea where dataArea.Id == company;
    if (!dataArea)
    {
        throw error(strFmt("@VSIAssetManagmentLabelFile:InvalidCompany", company));
    }
    
    return company;
}

/// <summary>
/// Captures infolog messages since a given line number.
/// </summary>
private static str getInfologText(int _infologStart)
{
    str infologText = '';
    for (int i = _infologStart + 1; i <= infologLine(); i++)
    {
        infologText += infologText(i) + '\n';
    }
    return infologText;
}

/// <summary>
/// Converts a newline-delimited string to a List for the response.
/// </summary>
private static List stringToList(str _text)
{
    List errors = new List(Types::String);
    if (strLen(_text) > 0)
    {
        container lines = str2con(_text, '\n');
        for (int i = 1; i <= conLen(lines); i++)
        {
            str line = conPeek(lines, i);
            if (strLen(strRem(line, '\r')) > 0)
            {
                errors.addEnd(strRem(line, '\r'));
            }
        }
    }
    return errors;
}
```

### Key Patterns in the Executor

| Pattern | Purpose |
|---|---|
| `infologLine()` capture | Records starting infolog line to isolate service-generated messages |
| `resolveCompany()` | Validates and defaults company; supports cross-company calls |
| `changecompany(company)` | Executes the processor in the target company context |
| Retry loop with `#RetryNum` | Handles deadlock/update-conflict with configurable max retries |
| `getInfologText()` | Extracts error messages from infolog for structured response |
| `stringToList()` | Converts infolog text to `List` for `markFailure()` |

---

## 35.3 JSON Serialization with CLR Interop — Complete VSIAssetServiceCatalog

`VSIAssetServiceCatalog` provides a comprehensive test harness for service development and debugging:

### Full Test Harness Implementation

```xpp
public final class VSIAssetServiceCatalog
{
    public static str RequestParameterName = 'request';
    public static str ResponseParameterName = 'response';

    /// <summary>
    /// Runs a service test operation and returns the JSON response.
    /// </summary>
    public static str runTest(str _operationName, str _inboundJson)
    {
        VSIAssetServiceProcessor processor;
        VSIAssetServiceRequest request;
        VSIAssetServiceResponse response;

        // Deserialize request
        request = VSIAssetServiceCatalog::deserializeRequest(_operationName, _inboundJson);
        if (!request)
        {
            return VSIAssetServiceCatalog::wrapError(
                strFmt("@VSIAssetManagmentLabelFile:ServiceDeserializeFailed", _operationName));
        }

        // Get processor instance
        processor = VSIAssetServiceCatalog::getProcessor(_operationName);
        if (!processor)
        {
            return VSIAssetServiceCatalog::wrapError(
                strFmt("@VSIAssetManagmentLabelFile:ServiceUnknownOperation", _operationName));
        }

        // Create response contract
        response = VSIAssetServiceCatalog::createResponse(_operationName);

        // Execute service
        VSIAssetServiceHelper::execute(processor, _operationName, request, response);

        // Serialize response
        return VSIAssetServiceCatalog::serializeResponse(response);
    }

    /// <summary>
    /// Deserializes the request JSON to the appropriate contract.
    /// </summary>
    private static VSIAssetServiceRequest deserializeRequest(str _operationName, str _inboundJson)
    {
        str requestJson = VSIAssetServiceCatalog::extractRequestJson(_inboundJson);
        ClassId contractClass = VSIAssetServiceCatalog::getRequestContractClass(_operationName);
        
        if (!contractClass)
        {
            return null;
        }

        return FormJsonSerializer::deserializeObject(contractClass, requestJson) as VSIAssetServiceRequest;
    }

    /// <summary>
    /// Extracts the request object from the wrapper JSON.
    /// </summary>
    private static str extractRequestJson(str _inboundJson)
    {
        Newtonsoft.Json.Linq.JObject jObject = Newtonsoft.Json.Linq.JObject::Parse(_inboundJson);
        Newtonsoft.Json.Linq.JToken requestToken = jObject.get_Item(VSIAssetServiceCatalog::RequestParameterName);
        return requestToken ? requestToken.ToString() : '';
    }

    /// <summary>
    /// Maps operation name to request contract class.
    /// </summary>
    private static ClassId getRequestContractClass(str _operationName)
    {
        switch (_operationName)
        {
            case 'assignAsset':
                return classNum(VSIAssetAssignRequestContract);
            case 'getAssetDetails':
                return classNum(VSIAssetGetDetailsRequestContract);
            case 'getWorkerAssets':
                return classNum(VSIAssetGetWorkerAssetsRequestContract);
        }
        return 0;
    }

    /// <summary>
    /// Maps operation name to processor instance.
    /// </summary>
    private static VSIAssetServiceProcessor getProcessor(str _operationName)
    {
        switch (_operationName)
        {
            case 'assignAsset':
                return VSIAssetAssignmentService::construct();
            case 'getAssetDetails':
            case 'getWorkerAssets':
                return VSIAssetInquiryService::construct();
        }
        return null;
    }

    /// <summary>
    /// Creates the appropriate response contract for the operation.
    /// </summary>
    private static VSIAssetServiceResponse createResponse(str _operationName)
    {
        switch (_operationName)
        {
            case 'assignAsset':
                return new VSIAssetAssignmentResponseContract();
            case 'getAssetDetails':
                return new VSIAssetGetDetailsResponseContract();
            case 'getWorkerAssets':
                return new VSIAssetGetWorkerAssetsResponseContract();
        }
        return null;
    }

    /// <summary>
    /// Serializes the response contract to JSON.
    /// </summary>
    private static str serializeResponse(VSIAssetServiceResponse _response)
    {
        str json = FormJsonSerializer::serializeClass(_response);
        return VSIAssetServiceCatalog::prettyPrint(
            '{"' + VSIAssetServiceCatalog::ResponseParameterName + '":' + json + '}');
    }

    /// <summary>
    /// Pretty-prints JSON using Newtonsoft.Json for readability.
    /// </summary>
    public static str prettyPrint(str _json)
    {
        return Newtonsoft.Json.Linq.JToken::Parse(_json).ToString(
            Newtonsoft.Json.Formatting::Indented);
    }

    /// <summary>
    /// Wraps an error message in standard response format.
    /// </summary>
    private static str wrapError(str _message)
    {
        Map errorMap = new Map(Types::String, Types::String);
        errorMap.insert('error', _message);
        str json = FormJsonSerializer::serializeClass(errorMap);
        return VSIAssetServiceCatalog::prettyPrint(
            '{"' + VSIAssetServiceCatalog::ResponseParameterName + '":' + json + '}');
    }

    /// <summary>
    /// Checks if an operation is a write operation (requires confirmation).
    /// </summary>
    public static boolean isWriteOperation(str _operationName)
    {
        return _operationName == 'assignAsset'; // Add other write operations as needed
    }

    /// <summary>
    /// Extracts the company ID from the inbound JSON for confirmation dialog.
    /// </summary>
    public static str requestCompany(str _inboundJson)
    {
        try
        {
            Newtonsoft.Json.Linq.JObject jObject = Newtonsoft.Json.Linq.JObject::Parse(_inboundJson);
            Newtonsoft.Json.Linq.JToken requestToken = jObject.get_Item(VSIAssetServiceCatalog::RequestParameterName);
            if (requestToken)
            {
                Newtonsoft.Json.Linq.JToken companyToken = requestToken.get_Item('companyId');
                if (companyToken)
                {
                    return companyToken.ToString();
                }
            }
        }
        catch
        {
            // Ignore parsing errors
        }
        return curExt(); // Default to current company
    }
}
```

### Running a Service Test from a Form — Complete Pattern

```xpp
public void runTest()
{
    str inboundJson = VSIAssetServiceOperationTmp.InboundJson;
    str operationName = VSIAssetServiceOperationTmp.OperationName;

    // Confirm write operations
    if (VSIAssetServiceCatalog::isWriteOperation(operationName)
        && Box::yesNo(
            strFmt("@VSIAssetManagmentLabelFile:ServiceTestConfirm",
                   VSIAssetServiceCatalog::requestCompany(inboundJson)),
            DialogButton::No) != DialogButton::Yes)
    {
        return;
    }

    // Execute test
    VSIAssetServiceOperationTmp.OutboundJson = VSIAssetServiceCatalog::runTest(
        operationName, inboundJson);
    
    // Refresh form
    VSIAssetServiceOperationTmp_ds.write();
    VSIAssetServiceOperationTmp_ds.refresh();
}
```

### Deserializing Inbound JSON — Complete Pattern

```xpp
// In VSIAssetAssignmentService::process()
public void process(str _operation, VSIAssetServiceRequest _request, VSIAssetServiceResponse _response)
{
    VSIAssetAssignRequestContract assignRequest = _request as VSIAssetAssignRequestContract;
    VSIAssetAssignmentResponseContract assignResponse = _response as VSIAssetAssignmentResponseContract;

    if (_operation == 'assignAsset')
    {
        // Validate request
        if (!assignRequest.parmAssetId())
        {
            assignResponse.markFailure(VSIAssetServiceHelper::stringToList(
                "@VSIAssetManagmentLabelFile:AssetIdRequired"));
            return;
        }

        // Find asset
        VSIAsset asset;
        select firstOnly asset where asset.AssetId == assignRequest.parmAssetId();
        if (!asset)
        {
            assignResponse.markFailure(VSIAssetServiceHelper::stringToList(
                strFmt("@VSIAssetManagmentLabelFile:AssetNotFound", assignRequest.parmAssetId())));
            return;
        }

        // Assign asset using status helper (respects context guard)
        VSIAssetStatusHelper::changeStatus(
            asset,
            VSIAssetStatus::Assigned,
            assignRequest.parmWorkerId());

        assignResponse.markSuccess(
            strFmt("@VSIAssetManagmentLabelFile:AssetAssigned", asset.AssetId));
    }
}
```

### JSON Serialization Helper Methods

```xpp
/// <summary>
/// Serializes any data contract to JSON string.
/// </summary>
public static str serializeContract(Object _contract)
{
    return FormJsonSerializer::serializeClass(_contract);
}

/// <summary>
/// Deserializes JSON string to data contract.
/// </summary>
public static Object deserializeContract(str _json, ClassId _contractClass)
{
    return FormJsonSerializer::deserializeObject(_contractClass, _json);
}

/// <summary>
/// Creates a standard service request wrapper.
/// </summary>
public static str wrapRequest(Object _contract)
{
    return VSIAssetServiceCatalog::prettyPrint(
        '{"' + VSIAssetServiceCatalog::RequestParameterName + '":'
        + FormJsonSerializer::serializeClass(_contract)
        + '}');
}
```

---

## 35.5 Activity — Build a Custom Service End-to-End

**Objective:** Create a new custom service `VSIAssetTransferService` with operation `transferAsset` that moves an asset between workers.

**Requirements:**
1. Create request/response contracts with `DataContractAttribute`/`DataMemberAttribute`
2. Implement `VSIAssetServiceProcessor` interface
3. Register in `AxServiceGroup` metadata
4. Add security privilege for the operation
5. Test using `VSIAssetServiceCatalog` harness

**Hints:**
- Request: AssetId, FromWorkerId, ToWorkerId, CompanyId
- Response: Success, Message, NewAssignmentRecId
- Use `VSIAssetStatusHelper::changeStatus()` for status transitions
- Validate both workers exist and are active
- Handle cross-company scenario

**Ideal Solution Structure:**

```xpp
[DataContractAttribute]
public final class VSIAssetTransferRequestContract implements VSIAssetServiceRequest
{
    [DataMemberAttribute('AssetId')]
    public VSIAssetId parmAssetId(VSIAssetId _assetId = assetId) { ... }

    [DataMemberAttribute('FromWorkerId')]
    public VSIWorkerId parmFromWorkerId(VSIWorkerId _fromWorkerId = fromWorkerId) { ... }

    [DataMemberAttribute('ToWorkerId')]
    public VSIWorkerId parmToWorkerId(VSIWorkerId _toWorkerId = toWorkerId) { ... }

    public str companyId() { return dataAreaId; }
}

public final class VSIAssetTransferService implements VSIAssetServiceProcessor
{
    public static VSIAssetTransferService construct()
    {
        return new VSIAssetTransferService();
    }

    public void process(str _operation, VSIAssetServiceRequest _request, VSIAssetServiceResponse _response)
    {
        VSIAssetTransferRequestContract request = _request as VSIAssetTransferRequestContract;
        VSIAssetTransferResponseContract response = _response as VSIAssetTransferResponseContract;

        if (_operation != 'transferAsset') { return; }

        // Validate and execute transfer...
        // Return new assignment RecId in response
    }
}
```

**Register in AxServiceGroup:**
```xml
<AxServiceGroupService>
    <Name>VSIAssetTransferService</Name>
    <Service>VSIAssetTransferService</Service>
</AxServiceGroupService>
```

**Security Entry Point:**
```xml
<AxSecurityEntryPointReference>
    <Name>transferAsset</Name>
    <ObjectName>VSIAssetTransferService</ObjectName>
    <ObjectType>ServiceOperation</ObjectType>
</AxSecurityEntryPointReference>
```

## 35.3 JSON Serialization with CLR Interop

`VSIAssetServiceCatalog` provides a test harness that serializes contracts to/from JSON using `FormJsonSerializer` and `Newtonsoft.Json`:

```xpp
private static str wrapRequest(Object _contract)
{
    return VSIAssetServiceCatalog::prettyPrint(
        '{"' + VSIAssetServiceCatalog::RequestParameterName + '":'
        + FormJsonSerializer::serializeClass(_contract)
        + '}');
}

private static str prettyPrint(str _json)
{
    return Newtonsoft.Json.Linq.JToken::Parse(_json).ToString();
}
```

### Running a Service Test from a Form

```xpp
public void runTest()
{
    str inboundJson = VSIAssetServiceOperationTmp.InboundJson;

    if (VSIAssetServiceCatalog::isWriteOperation(VSIAssetServiceOperationTmp.OperationName)
        && Box::yesNo(
            strFmt("@VSIAssetManagmentLabelFile:ServiceTestConfirm",
                   VSIAssetServiceCatalog::requestCompany(inboundJson)),
            DialogButton::No) != DialogButton::Yes)
    {
        return;
    }

    VSIAssetServiceOperationTmp.OutboundJson = VSIAssetServiceCatalog::runTest(
        VSIAssetServiceOperationTmp.OperationName, inboundJson);
    VSIAssetServiceOperationTmp_ds.write();
    VSIAssetServiceOperationTmp_ds.refresh();
}
```

### Deserializing Inbound JSON

```xpp
response = assignmentService.assignAsset(
    FormJsonSerializer::deserializeObject(
        classNum(VSIAssetAssignRequestContract), requestJson)
        as VSIAssetAssignRequestContract);
```

## 35.4 Service Exposure

Services are registered in `AxService` and `AxServiceGroup` metadata:

```xml
<AxServiceGroup>
    <Name>VSIAssetServiceGroup</Name>
    <AutoDeploy>Yes</AutoDeploy>
    <Services>
        <AxServiceGroupService><Name>VSIAssetAssignmentService</Name><Service>VSIAssetAssignmentService</Service></AxServiceGroupService>
        <AxServiceGroupService><Name>VSIAssetInquiryService</Name><Service>VSIAssetInquiryService</Service></AxServiceGroupService>
    </Services>
</AxServiceGroup>
```

Service operations are secured via `AxSecurityPrivilege` entries:
```xml
<AxSecurityEntryPointReference>
    <Name>assignAsset</Name>
    <ObjectName>VSIAssetAssignmentService</ObjectName>
    <ObjectType>ServiceOperation</ObjectType>
</AxSecurityEntryPointReference>
```

---

# Summary: From 5-Month Intern to Production-Ready Developer

Your handbook now covers:

| Level | Topics | Coverage |
|---|---|---|
| **Foundations** (Months 1-2) | X++ basics, tables, EDTs, CRUD, forms | ✅ Complete |
| **Intermediate** (Months 3-4) | CoC, event handlers, RunBase, SysOperation | ✅ Complete |
| **Advanced** (Months 5-6) | SysDa, extension methods, orig(), prmIsDefault, local functions, var | ✅ Complete |
| **Production** (Months 7-8) | SQL timeouts, deadlock handling, CacheLookup, indexing, debugging | ✅ Complete |
| **Integration** (Months 9-10) | Power Platform, OData, Logic Apps, Azure Functions, mobile | ✅ Complete |
| **Specialization** (Months 11-12) | Finance, SCM, HR, Retail, Project Operations module deep dives | ✅ Complete |
| **DevOps** (Ongoing) | CI/CD, validate package, database movement, continuous delivery | ✅ Complete |
| **Compliance** (Ongoing) | GDPR, ISV rules, financial tags, date effectivity, security hardening | ✅ Complete |
| **Workflow** (New) | WorkflowDocument, WorkflowType, Approvals, Tasks, event handlers, submit/resubmit | ✅ New |
| **Number Sequences** (New) | NumberSeqApplicationModule, loadModule, NumberSeqFormHandler, scope types | ✅ New |
| **Data Management** (New) | Data entities, staging tables, mapEntityToDataSource, import/export flow | ✅ New |
| **Advanced Forms** (New) | ListPage, SimpleListDetails-Grid, FactBox, Tree forms, dialog overrides | ✅ New |
| **Notifications** (New) | Action Center, SystemNotificationsManager, IDisposable status context | ✅ New |
| **Batch & Concurrency** (New) | Runtime tasks, deadlock retry, cross-company queries, batch constants | ✅ New |
| **Labels & AppChecker** (New) | Label files, AppChecker config, configuration keys | ✅ New |
| **Services & JSON/CLR** (New) | Custom services, contracts, FormJsonSerializer, Newtonsoft.Json, service security | ✅ New |

**Next Steps for the Intern:**
1. Complete all 30 chapters with hands-on exercises
2. Build a capstone project spanning at least two modules (e.g., Finance + SCM)
3. Set up a CI/CD pipeline with automated testing
4. Prepare for Microsoft certification (MB-310 or MB-330)
5. Contribute to the standard codebase using extension patterns only
