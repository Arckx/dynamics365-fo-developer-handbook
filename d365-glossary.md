---
name: d365-glossary
description: Comprehensive glossary of D365 F&O terms with one-sentence definitions and security hierarchy reference
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-17T19:57:18.865Z
---

# D365 Finance & Operations — Glossary

> **Key terms and concepts in Dynamics 365 Finance & Operations development.**
> Each entry includes a one-sentence definition and, where helpful, a cross-reference to the relevant chapter in the Desktop Guide.

---

## A

| Term | Definition |
|---|---|
| **AOS (Application Object Server)** | The server-side runtime engine that executes X++ IL code, manages transactions, serves metadata, and handles database connections. |
| **Alternate Index** | A non-clustered, unique constraint on a table that enforces uniqueness for a specific field or set of fields. |
| **Application Platform** | The lowest model layer in the D365 F&O stack — provides interfaces with the kernel and base infrastructure (AIF, Batch, RunBase, DictXX objects). |
| **Application Foundation** | The framework layer shared across all applications — includes dimension framework, GAB, number sequences, security, workflow, and BI. |
| **Application Suite** | The application-specific business logic layer — covers SCM, HCM, Professional Services, Retail, etc. |
| **AOT (Application Object Tree)** | The hierarchical, metadata-driven repository that contains every object in D365 F&O — tables, classes, forms, views, security roles, reports, and more. |
| **Azure Active Directory (Azure AD)** | The identity and authentication service that every D365 F&O user authenticates through; role-based access flows through the D365 security model. |
| **Azure DevOps** | The CI/CD platform used to build, test, and deploy D365 F&O solutions — compiles X++, produces `.axmodel` artifacts, and deploys to environments. |

## B

| Term | Definition |
|---|---|
| **Batch Processing** | Running long-running or scheduled jobs in the background using the `RunBaseBatch` framework, which queues work for the Batch server. |
| **Batch Header** | The `BatchHeader` class that manages batch job metadata — job name, recurrence schedule, execution priority, and target server. |
| **BI (Business Intelligence)** | The analytics and reporting capabilities in D365 F&O — includes SSRS paginated reports, analytical reporting (Power BI), and the Financial Reporting module. |
| **CacheLookup** | A table property that controls how SQL Server caches lookups of that table — values include `NotInTTS`, `Found`, `FoundNotInTTS`, and `All`. |
| **Chain of Command (CoC)** | A pattern for resolving method conflicts between a base class and its extensions — the `next` keyword calls the next handler in the execution chain. |
| **Configuration Key** | An encrypted credential that controls feature visibility in D365 F&O — used to enable or disable modules and functionality at runtime. |
| **Container** | A typed ordered list in X++ (similar to an array) that can hold elements of different types — accessed with `conPeek()` and `conLen()`. |
| **Cross-Reference DB** | A SQL Server Express LocalDB installed with Visual Studio that tracks object dependencies — enables "Find References" and "Depends on" queries. |

## D

| Term | Definition |
|---|---|
| **Data Entity** | A D365 F&O object that exposes table data to external systems via OData/REST APIs — consists of a `DataEntity` node, a `Query`, and optionally a staging table. |
| **Data Project** | A Visual Studio project that groups data entities and their dependencies for deployment — used to build and export data integration packages. |
| **Data Area** | The top-level organizational unit in D365 F&O — also called a Legal Entity; represents a distinct legal entity for financial reporting and regulatory compliance. |
| **Delegate** | A type-safe function pointer in X++ that allows consumers to inject custom logic into a publisher class — subscribed to using the `+=` operator. |
| **Deployment** | The process of pushing compiled `.axmodel` artifacts from a build environment to a target environment (Dev → Test → Production). |
| **Development Lifecycle** | The end-to-end workflow for D365 F&O development: code → build → deploy → test → promote → production, managed through LCS and Azure DevOps. |
| **DGML** | Directed Graph Markup Language — a diagram format used in Visual Studio to visualize model dependency graphs in the AOT. |

## E

| Term | Definition |
|---|---|
| **EDT (Extended Data Type)** | A type alias that wraps a base type (string, int, real) with additional properties like `StringSize`, validation rules, and field relations — ensures consistency across the data model. |
| **EDT Extension** | A mechanism to add new allowed values to an existing EDT (e.g., adding a new country code to `AddressCountryRegionId`). |
| **E-Signature** | The electronic signature framework in D365 F&O that enables digitally signed approvals and document workflows. |
| **Element** | A single object in the AOT — a table, class, form, view, EDT, enum, report, data entity, or any other metadata item. |
| **Event Handler** | A method that automatically executes in response to a specific system event (e.g., `inserted`, `updated`, `deleted` on a table) — registered via the `[SubscribesTo]` attribute. |
| **Exception Types** | The categories of errors in X++: `Error`, `Warning`, `Info`, `Broken`, `Deadlock`, and `DuplicateKey` — each handled in a separate `catch` block. |
| **Extension** | A customization approach that adds fields, methods, or event handlers to a base table or class without modifying the original — the preferred method over overlayering. |
| **Extensible EDT** | An EDT that allows consumers to add new values to base enums, enabling customization without modifying the base EDT definition. |

## F

| Term | Definition |
|---|---|
| **Field Group** | A named set of fields defined at the table level — used for form auto-generation and report generation so that adding a field to the group automatically appears in all forms/reports using it. |
| **Field Relation** | An EDT property that links the EDT to another table (e.g., `CustAccount` EDT links to `CustTable`) — enables automatic lookup and validation in forms. |
| **Financial Dimension** | A category axis used in the chart of accounts to classify transactions — examples include Department, Cost Center, and Business Unit; the set of active financial dimensions defines the dimension framework. |
| **Three-Tier Architecture** | The architectural model for D365 F&O: Client (browser-based), Application (AOS), and Database tiers. Integration and Azure services are supporting components, not separate tiers. |
| **Form Data Source** | A node in a form that points to a table or query — controls which SQL query runs, which fields are available, and how joins work. |
| **Form Link Type** | Defines how parent and child data sources relate in a form — `Inner Join` (child only if parent exists), `Outer Join` (all children regardless), `Exists Join` (parent only if children exist). |

## G

| Term | Definition |
|---|---|
| **Global Class** | A class declared with the `Global` prefix — its methods can be called without instantiating the class (e.g., `Global::info()`). |
| **Group Level Index** | A multi-field index where the leading field determines selectivity — SQL can use the index for queries that filter on the leading field. |

## H

| Term | Definition |
|---|---|
| **Hash Index** | An index type optimized for equality-only lookups (no range scans) — useful when queries always filter by exact match on a single field. |
| **Hotfix** | A targeted patch deployed to a production environment to fix a specific bug or issue — deployed through LCS release pipeline. |

## I

| Term | Definition |
|---|---|
| **IL (Intermediate Language)** | The compiled output of X++ — X++ compiles to .NET CIL (Common Intermediate Language), the same IL used by C# and VB.NET. |
| **Infolog** | The message window in the D365 F&O client that displays informational messages (`info`), warnings (`warning`), and errors (`error`). |
| **Integration Components** | Supporting components (not a separate tier) that connect D365 F&O to external systems — includes Azure Service Bus, Azure Functions, Logic Apps, and OData/REST endpoints. See **Three-Tier Architecture**. |
| **Inner Join** | A form data source link type where child records only show when a matching parent record exists — the default link type. |
| **Instance Variable** | A variable declared within a class (not `static`) — each object instance has its own copy. |

## J

| Term | Definition |
|---|---|
| **Job** | An ad-hoc X++ program that runs once — used for data migration, batch processing, testing, and one-time operations. Jobs are stored in the AOT under `Jobs`. |

## L

| Term | Definition |
|---|---|
| **LCS (Lifecycle Services)** | Microsoft's cloud-based orchestration platform for D365 F&O — manages environments, build pipelines, release pipelines, monitoring, and hotfix deployment. |
| **Layer** | The upgrade boundary in D365 F&O — determines the order in which model changes are applied and which changes survive upgrades. |
| **Layer Hierarchy** | From lowest to highest: `SYS` (Microsoft-owned, cannot be modified) → `ISV` (independent software vendor) → `VAR` (value-added reseller) → `CUS` (customer-specific) → `USR` (user layer, highest — no key required to access, unlike `ISV`/`VAR`/`CUS`). Higher layers override lower layers. **Current guidance:** Microsoft now strongly favors the **extension model** (table extensions, class extensions, event handlers) over layering/overlayering for customizations. Overlayering on `CUS`/`USR` is considered a legacy mechanism mainly relevant when upgrading older on-prem / AX 2012-derived solutions; new development should use extensions to maintain forward-compatibility and reduce upgrade friction. ([Models docs](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/models) | [Customization: overlayering vs. extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customization-overlayering-extensions)) |
| **Logic App** | An Azure service for automating workflows — used in D365 F&O integration patterns to connect to external systems without writing custom code. |

## M

| Term | Definition |
|---|---|
| **Model** | A deployable unit of metadata in D365 F&O — contains a collection of AOT objects (tables, classes, forms, etc.) and is defined by a `Model.xml` manifest file. |
| **Model Store** | The file system (Azure File Storage in cloud) where AOT metadata is stored as XML files — not a SQL database. |
| **Model Manifest** | The `Model.xml` file that defines a model's name, version, layer, dependencies, and configuration keys — the heart of a model project. |
| **MICR** | Magnetic Ink Character Recognition — the standard for printing bank cheque details; D365 F&O includes MICR check printing in the Accounts Payable module. |
| **Monster All-in-One Form** | A form that tries to do everything — D365 F&O best practice is to use List Pages for browsing, Details Forms for editing, and Task Pages for wizard-style workflows. |

## N

| Term | Definition |
|---|---|
| **Number Sequence (`NumberSeq`)** | A framework for generating sequential, unique identifiers safely under concurrent access — handles deduplication and gap-free numbering. |
| **NuGet Packages** | The 5 NuGet packages required for a full D365 F&O build in Visual Studio — include X++ compiler targets, reference assemblies, and deployment tools. |

## O

| Term | Definition |
|---|---|
| **OData/REST API** | The protocol used to expose D365 F&O data to external systems — data entities are automatically available via OData endpoints at `/data/<EntityName>`. |
| **Outer Join** | A form data source link type where ALL child records show even if no matching parent exists — used for "show me all children regardless of parent." |
| **Overlayering** | Modifying base Microsoft tables and classes directly — the deprecated approach that causes upgrade conflicts; replaced by the extension pattern. |

## P

| Term | Definition |
|---|---|
| **Package** | The deployable unit in D365 F&O — a collection of models that are built and deployed together as a single `.axmodel` artifact. |
| **Paginated Report** | An SSRS report format that renders as a fixed-layout document (PDF, Excel, Word) — the standard report type in D365 F&O. |
| **Presentation Tier** | The web-based UI layer of D365 F&O — a single browser-based client (HTML5/CSS/JS) that runs in Edge, Chrome, and Safari; the AOS serves the web assets and the browser renders forms, menus, and navigation. |
| **Primary Index** | The clustered index on `RecId` that is auto-created for every table — should not be modified. |
| **PrivateCollection** | The staging fields in a data entity that hold intermediate state before data is pushed to the target system. |
| **PublicCollection** | The output fields in a data entity that are exposed to external systems via OData. |

## Q

| Term | Definition |
|---|---|
| **Query** | An AOT node that defines data retrieval logic with ranges, joins, and sorting — used by views, forms, and reports. |
| **Query Build Data Source** | The programmatic API for building queries at runtime — `addRange()`, `addLink()`, and `addDataSource()` methods allow dynamic query construction. |

## R

| Term | Definition |
|---|---|
| **RecId** | The auto-generated 64-bit record identifier (`RecId`) that is the primary key for every table in D365 F&O — should never be manually assigned. |
| **Reference Group** | An EDT property that declares which table the EDT references — enables `RefTableId` and `RefRecId` automatic fields on tables using that EDT. |
| **Release Pipeline** | The LCS pipeline that promotes builds from Test to Production environments — manages staging, validation, and deployment steps. |
| **RunBase** | The framework for creating batchable processes — a base class that provides the UI for parameter input and the infrastructure for background execution. |
| **RunBaseBatch** | The batch execution variant of RunBase — queues the process for background execution on the Batch server. |

## S

| Term | Definition |
|---|---|
| **Security Role** | A collection of duties that defines what a user can do in D365 F&O — the hierarchy is: Privilege → Duty → Role → User. |
| **SSRS (SQL Server Reporting Services)** | The reporting engine used in D365 F&O for paginated reports — uses `SrsReportDataProvider` classes to supply data to report layouts. |
| **SrsReportDataProvider** | The base class for SSRS report data providers — contains the `processReport()` method where query logic populates temporary tables for the report layout. |
| **Static Variable** | A variable declared with the `static` keyword — shared across all instances of the class, persists for the lifetime of the application. |
| **Staging Table** | An intermediate table used in data entities and integration patterns to accumulate, validate, and stage records before pushing them to the target system. |
| **SysOperation** | The modern framework for service operations with parameter classes — replaces the older RunBase pattern for service-based integrations. |
| **SoD (Segregation of Duties)** | A security principle that prevents a single user from having conflicting permissions — D365 F&O supports SoD validation through the security model and XDS policies. |
| **SysTest** | The built-in unit testing framework in D365 F&O — tests are classes that extend `SysTestTestCase` and are executed through the Test Runner. |
| **System Class** | A class in the `Sys**` namespace (e.g., `SysTableLookup`, `SrsReportDataProvider`) — provides framework-level functionality that developers use directly. |

## T

| Term | Definition |
|---|---|
| **Table Extension** | The pattern for adding fields, indexes, relations, and methods to an existing Microsoft table without modifying the base table — the recommended approach over overlayering. |
| **Transaction (`ttsBegin`/`ttsCommit`/`ttsAbort`)** | A unit of work that ensures all database modifications succeed or all are rolled back — wraps multi-table inserts/updates in atomic operations. |
| **TTS (Transaction Scope)** | The transaction boundary created by `ttsBegin` — all SQL statements within the scope are committed together on `ttsCommit` or rolled back on `ttsAbort`. |

## U

| Term | Definition |
|---|---|
| **Update Action** | A table property that defines what happens when a parent record is updated — options include `Cascade`, `Restricted`, and `None`. |
| **UTC DateTime** | A `utcdatetime` value that stores date and time in Coordinated Universal Time — used for audit fields and cross-timezone data. |

## V

| Term | Definition |
|---|---|
| **Validation** | The process of checking data integrity before allowing a record to be saved — implemented via `validateWrite()` on tables and custom validation methods on classes. |
| **Visual Studio (VS)** | The IDE used for D365 F&O development — VS 2022 with the `Microsoft.Dynamics.FinOps.ToolsVS2022.vsix` extension provides the Modeling SDK, X++ editor, and debugging support. |
| **View** | A virtual table defined by a query that provides a read-only or updatable projection of data from multiple tables — can be extended to add fields to existing views. |

## W

| Term | Definition |
|---|---|
| **While Select** | The standard X++ iteration pattern that combines a SQL `SELECT` with a `while` loop — generates efficient SQL and streams records one at a time from the database. |
| **Workstation** | A client machine (desktop, laptop, or tablet) accessing D365 F&O through a supported web browser (Edge, Chrome, Safari) — no separate client installation is required. |
| **Workflow** | The automated approval and business process engine in D365 F&O — workflows define routes, conditions, and actions for document approvals and task routing. |

## X

| Term | Definition |
|---|---|
| **X++** | The primary development language for D365 F&O — object-oriented, application-aware, data-aware, compiles to .NET CIL, and runs on the AOS. |
| **X++ IL** | The compiled form of X++ code — X++ compiles to .NET CIL (Common Intermediate Language), the same IL used by C# and VB.NET. |
| **XDS (Extensible Data Security)** | A policy-based security framework that controls access to data at the row and field level — applies security rules dynamically based on context, roles, and query ranges. |

---

## Quick Reference: Security Hierarchy

```
User → Role → Duty → Privilege → Permission
```

| Level | What It Controls | Example |
|---|---|---|
| **Permission** | Access to a specific table/field + read/write/delete/create | `CustTable` Read, `CustTable` Write |
| **Privilege** | A collection of permissions | `CustTable Maintenance` |
| **Duty** | A collection of privileges | `Customer Maintenance` |
| **Role** | A collection of duties assigned to a user | `Accounts Receivable Manager` |
| **User** | Assigned one or more roles | `Ahmed` → `Accounts Receivable Manager` |
