---
name: d365-glossary
description: Comprehensive glossary of D365 F&O terms with one-sentence definitions and security hierarchy reference
metadata: 
  node_type: memory
  type: reference
  originSessionId: 369838ab-9513-4fe8-9b6d-09784c222811
  modified: 2026-08-10T17:48:07.602Z
---

# D365 Finance & Operations — Glossary

> **Key terms and concepts in Dynamics 365 Finance & Operations development.**
> Each entry includes a one-sentence definition and, where helpful, a cross-reference to the relevant chapter in the Desktop Guide.

---

## A

| Term | Definition | Primary Chapter |
|---|---|---|
| **AOS (Application Object Server)** | The server-side runtime engine that executes X++ IL code, manages transactions, serves metadata, and handles database connections. | Ch 1.1 |
| **Alternate Index** | A non-clustered, unique constraint on a table that enforces uniqueness for a specific field or set of fields. | Ch 9.1 |
| **Application Platform** | The lowest model layer in the D365 F&O stack — provides interfaces with the kernel and base infrastructure (AIF, Batch, RunBase, DictXX objects). | Ch 1–2 |
| **Application Foundation** | The framework layer shared across all applications — includes dimension framework, GAB, number sequences, security, workflow, and BI. | Ch 1–2 |
| **Application Suite** | The application-specific business logic layer — covers SCM, HCM, Professional Services, Retail, etc. | Ch 1–2 |
| **AOT (Application Object Tree)** | The hierarchical, metadata-driven repository that contains every object in D365 F&O — tables, classes, forms, views, security roles, reports, and more. | Ch 1.2 |
| **Azure Active Directory (Azure AD)** | The identity and authentication service that every D365 F&O user authenticates through; role-based access flows through the D365 security model. | Ch 1.1, 15 |
| **Azure DevOps** | The CI/CD platform used to build, test, and deploy D365 F&O solutions — compiles X++, produces `.axmodel` artifacts, and deploys to environments. | Ch 4, 20, 27 |

## B

| Term | Definition | Primary Chapter |
|---|---|---|
| **Batch Processing** | Running long-running or scheduled jobs in the background using the `RunBaseBatch` or `SysOperation` framework, which queues work for the Batch server. | Ch 18, 33 |
| **Batch Header** | The `BatchHeader` class that manages batch job metadata — job name, recurrence schedule, execution priority, and target server. | Ch 18 |
| **BI (Business Intelligence)** | The analytics and reporting capabilities in D365 F&O — includes SSRS paginated reports, analytical reporting (Power BI), and the Financial Reporting module. | Ch 17 |
| **CacheLookup** | A table property that controls how SQL Server caches lookups of that table — values: `None`, `NotInTTS`, `Found`, `FoundAndEmpty`, `EntireTable`. | Ch 9.1, 21 |
| **Chain of Command (CoC)** | A pattern for resolving method conflicts between a base class and its extensions — the `next` keyword calls the next handler in the execution chain. | Ch 10, 14 |
| **Configuration Key** | A boolean property set on AOT objects that a system administrator enables/disables via the License Configuration form to control which features/modules are visible. | Ch 4.1 |
| **Container** | A typed ordered list in X++ (similar to an array) that can hold elements of different types — accessed with `conPeek()` and `conLen()`. | Ch 5.1 |
| **Cross-Reference DB** | A SQL Server Express LocalDB installed with Visual Studio that tracks object dependencies — enables "Find References" and "Depends on" queries. | Ch 8.1 |

## D

| Term | Definition | Primary Chapter |
|---|---|---|
| **Data Entity** | A D365 F&O object that exposes table data to external systems via OData/REST APIs — consists of a `DataEntity` node, a `Query`, and optionally a staging table. | Ch 16 |
| **Data Project** | A Visual Studio project that groups data entities and their dependencies for deployment — used to build and export data integration packages. | Ch 16 |
| **Data Area** | The top-level organizational unit in D365 F&O — also called a Legal Entity; represents a distinct legal entity for financial reporting and regulatory compliance. | Ch 1.1 |
| **Delegate** | A type-safe function pointer in X++ that allows consumers to inject custom logic into a publisher class. **Do not create new delegates** — Chain of Command (CoC) supersedes delegates. | Ch 14 |
| **Deployment** | The process of pushing compiled `.axmodel` artifacts from a build environment to a target environment (Dev → Test → Production). | Ch 4, 20, 27 |
| **Development Lifecycle** | The end-to-end workflow for D365 F&O development: code → build → deploy → test → promote → production, managed through LCS and Azure DevOps. | Ch 4 |
| **DGML** | Directed Graph Markup Language — a diagram format used in Visual Studio to visualize model dependency graphs in the AOT. | Ch 2.1 |

## E

| Term | Definition | Primary Chapter |
|---|---|---|
| **EDT (Extended Data Type)** | A type alias that wraps a base type (string, int, real) with additional properties like `StringSize`, validation rules, and field relations — ensures consistency across the data model. | Ch 3.2, 9.2 |
| **EDT Extension** | A mechanism to add new allowed values to an existing EDT (e.g., adding a new country code to `AddressCountryRegionId`). | Ch 9.2 |
| **E-Signature** | The electronic signature framework in D365 F&O that enables digitally signed approvals and document workflows. | Ch 28 |
| **Element** | A single object in the AOT — a table, class, form, view, EDT, enum, report, data entity, or any other metadata item. | Ch 1.2 |
| **Event Handler** | A method that automatically executes in response to a specific system event (`[DataEventHandler]` or `[SubscribesTo]`). Executed within transaction scope. | Ch 13 |
| **Exception Types** | The categories of errors in X++: `Error`, `Warning`, `Info`, `Broken`, `Deadlock`, and `DuplicateKey` — each handled in a separate `catch` block. | Ch 7.2 |
| **Extension** | A customization approach that adds fields, methods, or event handlers to a base table or class without modifying the original — preferred over overlayering. | Ch 9.4, 10.4, 14 |
| **Extensible EDT** | An EDT that allows consumers to add new values to base enums, enabling customization without modifying the base EDT definition. | Ch 9.2 |

## F

| Term | Definition | Primary Chapter |
|---|---|---|
| **Field Group** | A named set of fields defined at the table level — used for form auto-generation and report generation so that adding a field to the group automatically appears in all forms/reports using it. | Ch 9.3 |
| **Field Relation** | An EDT property that links the EDT to another table (e.g., `CustAccount` EDT links to `CustTable`) — enables automatic lookup and validation in forms. | Ch 9.2 |
| **Financial Dimension** | A category axis used in the chart of accounts to classify transactions — examples include Department, Cost Center, and Business Unit; the set of active financial dimensions defines the dimension framework. | Ch 26 |
| **Three-Tier Architecture** | The architectural model for D365 F&O: Client (browser-based), Application (AOS), and Database tiers. Integration and Azure services are supporting components, not separate tiers. | Ch 1.1 |
| **Form Data Source** | A node in a form that points to a table or query — controls which SQL query runs, which fields are available, and how joins work. | Ch 10.1 |
| **Form Link Type** | Defines how parent and child data sources relate in a form — `Inner Join` (child only if parent exists), `Outer Join` (all children regardless), `Exists Join` (parent only if children exist). | Ch 10.1 |

## G

| Term | Definition | Primary Chapter |
|---|---|---|
| **Global Class** | A class declared with the `Global` prefix — its methods can be called without instantiating the class (e.g., `Global::info()`). | Ch 5 |
| **Group Level Index** | A multi-field index where the leading field determines selectivity — SQL can use the index for queries that filter on the leading field. | Ch 9.1 |

## H

| Term | Definition | Primary Chapter |
|---|---|---|
| **Hash Index** | An index type optimized for equality-only lookups (no range scans) — useful when queries always filter by exact match on a single field. | Ch 9.1 |
| **Hotfix** | A targeted patch deployed to a production environment to fix a specific bug or issue — deployed through LCS release pipeline. | Ch 4.1 |

## I

| Term | Definition | Primary Chapter |
|---|---|---|
| **IL (Intermediate Language)** | The compiled output of X++ — X++ compiles to .NET CIL (Common Intermediate Language), a low-level format used by the .NET runtime to execute code efficiently. | Ch 1.1 |
| **Infolog** | The message window in the D365 F&O client that displays informational messages (`info`), warnings (`warning`), and errors (`error`). | Ch 6 |
| **Integration Components** | Supporting components that connect D365 F&O to external systems — includes Azure Service Bus, Azure Functions, Logic Apps, and OData/REST endpoints. | Ch 1.1, 25 |
| **Inner Join** | A form data source link type where child records only show when a matching parent record exists — the default link type. | Ch 10.1 |
| **Instance Variable** | A variable declared within a class (not `static`) — each object instance has its own copy. | Ch 7.3 |

## J

| Term | Definition | Primary Chapter |
|---|---|---|
| **Job** | An ad-hoc X++ program that runs once — used for data migration, batch processing, testing, and one-time operations. Jobs are stored in the AOT under `Jobs`. | Ch 1.2 |

## L

| Term | Definition | Primary Chapter |
|---|---|---|
| **LCS (Lifecycle Services)** | Microsoft's cloud-based orchestration platform for D365 F&O — manages environments, build pipelines, release pipelines, monitoring, and hotfix deployment. | Ch 4 |
| **Layer** | The upgrade boundary in D365 F&O — determines the order in which model changes are applied and which changes survive upgrades. | Ch 2.1 |
| **Layer Hierarchy** | From lowest to highest: `SYS` (Microsoft-owned, cannot be modified) → `ISV` (independent software vendor) → `VAR` (value-added reseller) → `CUS` (customer-specific) → `USR` (user layer, highest — no key required to access, unlike `ISV`/`VAR`/`CUS`). Higher layers override lower layers. **Current guidance:** Microsoft now strongly favors the **extension model** (table extensions, class extensions, event handlers) over layering/overlayering for customizations. Overlayering on `CUS`/`USR` is considered a legacy mechanism mainly relevant when upgrading older on-prem / AX 2012-derived solutions; new development should use extensions to maintain forward-compatibility and reduce upgrade friction. ([Models docs](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/models) | [Customization: overlayering vs. extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customization-overlayering-extensions)) | Ch 2.1 |
| **Logic App** | An Azure service for automating workflows — used in D365 F&O integration patterns to connect to external systems without writing custom code. | Ch 25 |

## M

| Term | Definition | Primary Chapter |
|---|---|---|
| **Model** | A deployable unit of metadata in D365 F&O — contains a collection of AOT objects (tables, classes, forms, etc.) and is defined by a `Model.xml` manifest file. | Ch 2.1 |
| **Model Store** | The file system (Azure File Storage in cloud) where AOT metadata is stored as XML files — not a SQL database. | Ch 2.1 |
| **Model Manifest** | The `Model.xml` file that defines a model's name, version, layer, dependencies, and configuration keys — the heart of a model project. | Ch 2.1 |
| **MICR** | Magnetic Ink Character Recognition — the standard for printing bank cheque details; D365 F&O includes MICR check printing in the Accounts Payable module. | Ch 26 |
| **Monster All-in-One Form** | A form that tries to do everything — D365 F&O best practice is to use List Pages for browsing, Details Forms for editing, and Task Pages for wizard-style workflows. | Ch 10 |

## N

| Term | Definition | Primary Chapter |
|---|---|---|
| **Number Sequence (`NumberSeq`)** | A framework for generating sequential, unique identifiers safely under concurrent access — handles deduplication and gap-free numbering. | Ch 30 |
| **NuGet Packages** | The NuGet packages required for a D365 F&O build, which vary by version — typically include X++ compiler targets, reference assemblies, and deployment tooling, restored automatically by the Dynamics365Build DevOps task. | Ch 20 |

## O

| Term | Definition | Primary Chapter |
|---|---|---|
| **OData/REST API** | The protocol used to expose D365 F&O data to external systems — data entities are automatically available via OData endpoints at `/data/<EntityName>`. | Ch 16 |
| **Outer Join** | A form data source link type where ALL child records show even if no matching parent exists — used for "show me all children regardless of parent." | Ch 10.1 |
| **Overlayering** | Modifying base Microsoft tables and classes directly — the **legacy** approach that causes upgrade conflicts; replaced by the extension pattern. Supported only to upgrade from legacy versions or for advanced customizations in models that overlay the source model. | Ch 14 |

## P

| Term | Definition | Primary Chapter |
|---|---|---|
| **Package** | The deployable unit in D365 F&O — a collection of models that are built and deployed together as a single `.axmodel` artifact. | Ch 2.1 |
| **Paginated Report** | An SSRS report format that renders as a fixed-layout document (PDF, Excel, Word) — the standard report type in D365 F&O. | Ch 17 |
| **Presentation Tier** | The web-based UI layer of D365 F&O — a single browser-based client (HTML5/CSS/JS) that runs in Edge, Chrome, and Safari; the AOS serves the web assets and the browser renders forms, menus, and navigation. | Ch 1.1 |
| **Primary Index** | The clustered index on `RecId` that is auto-created for every table — should not be modified. | Ch 9.1 |
| **Staging Table** | An auto-generated table (e.g., `EntityNameStaging`) that holds intermediate state for data entities before data is pushed to the target system. | Ch 16 |
| **Public Entity Name / Public Collection Name** | Properties on a data entity that control its OData exposure and endpoint names. | Ch 16 |

## Q

| Term | Definition | Primary Chapter |
|---|---|---|
| **Query** | An AOT node that defines data retrieval logic with ranges, joins, and sorting — used by views, forms, and reports. | Ch 11 |
| **Query Build Data Source** | The programmatic API for building queries at runtime — `addRange()`, `addLink()`, and `addDataSource()` methods allow dynamic query construction. | Ch 11 |

## R

| Term | Definition | Primary Chapter |
|---|---|---|
| **RecId** | The auto-generated 64-bit record identifier (`RecId`) that is the primary key for every table in D365 F&O — should never be manually assigned. | Ch 1.2 |
| **Reference Group** | An EDT property that declares which table the EDT references — enables `RefTableId` and `RefRecId` automatic fields on tables using that EDT. | Ch 9.2 |
| **Release Pipeline** | The LCS pipeline that promotes builds from Test to Production environments — manages staging, validation, and deployment steps. | Ch 20, 27 |
| **RunBase** | The framework for creating batchable processes — a base class that provides the UI for parameter input and the infrastructure for background execution. | Ch 12, 18 |
| **RunBaseBatch** | The batch execution variant of RunBase — queues the process for background execution on the Batch server. | Ch 18 |

## S

| Term | Definition | Primary Chapter |
|---|---|---|
| **Security Role** | A collection of duties that defines what a user can do in D365 F&O — the hierarchy is: Permission → Privilege (composed of permissions) → Duty (composed of privileges) → Role (composed of duties) → User (assigned one or more roles). | Ch 15 |
| **SSRS (SQL Server Reporting Services)** | The reporting engine used in D365 F&O for paginated reports — uses `SrsReportDataProvider` classes to supply data to report layouts. | Ch 17 |
| **SrsReportDataProvider** | The base class for SSRS report data providers — contains the `get()` method for standard providers and `processReport()` for `SrsReportDataProviderPreProcessTempDB` (TempDB pre-processing). | Ch 17 |
| **Static Variable** | A variable declared with the `static` keyword — shared across all instances of the class, persists for the lifetime of the application. | Ch 7.3 |
| **Staging Table** | An intermediate table used in data entities and integration patterns to accumulate, validate, and stage records before pushing them to the target system. | Ch 16 |
| **SysOperation** | The modern framework for service operations with parameter classes — the recommended pattern for service-based integrations and batch jobs. It separates Contract, UI Builder, Service, and Controller concerns, and provides built-in progress reporting, cancellation, and error handling. | Ch 18, 35 |
| **SoD (Segregation of Duties)** | A security principle that prevents a single user from having conflicting permissions — D365 F&O supports SoD validation through the security model and XDS policies. | Ch 15 |
| **SysTest** | The built-in unit testing framework in D365 F&O — tests are classes that extend `SysTestCase` and are executed through the Test Runner. | Ch 19 |
| **System Class** | A class in the `Sys**` namespace (e.g., `SysTableLookup`, `SrsReportDataProvider`) — provides framework-level functionality that developers use directly. | Ch 1.2 |

## T

| Term | Definition | Primary Chapter |
|---|---|---|
| **Table Extension** | The pattern for adding fields, indexes, relations, and methods to an existing Microsoft table without modifying the base table — the recommended approach over overlayering. | Ch 9.4 |
| **Transaction (`ttsBegin`/`ttsCommit`/`ttsAbort`)** | A unit of work that ensures all database modifications succeed or all are rolled back — wraps multi-table inserts/updates in atomic operations. | Ch 6 |
| **TTS (Transaction Scope)** | The transaction boundary created by `ttsBegin` — all SQL statements within the scope are committed together on `ttsCommit` or rolled back on `ttsAbort`. | Ch 6 |

## U

| Term | Definition | Primary Chapter |
|---|---|---|
| **Update Action** | A table property that defines what happens when a parent record is updated — options include `Cascade`, `Restricted`, and `None`. | Ch 9.1 |
| **UTC DateTime** | A `utcdatetime` value that stores date and time in Coordinated Universal Time — used for audit fields and cross-timezone data. | Ch 5.1 |

## V

| Term | Definition | Primary Chapter |
|---|---|---|
| **Validation** | The process of checking data integrity before allowing a record to be saved — implemented via `validateWrite()` on tables and custom validation methods on classes. | Ch 9.5 |
| **Visual Studio (VS)** | The IDE used for D365 F&O development — VS 2022 with the `Microsoft.Dynamics.FinOps.ToolsVS2022.vsix` extension provides the Modeling SDK, X++ editor, and debugging support. | Ch 3.1 |
| **View** | A virtual table defined by a query that provides a read-only or updatable projection of data from multiple tables — can be extended to add fields to existing views. | Ch 11 |

## W

| Term | Definition | Primary Chapter |
|---|---|---|
| **While Select** | The standard X++ iteration pattern that combines a SQL `SELECT` with a `while` loop — generates efficient SQL and streams records one at a time from the database. | Ch 6.1 |
| **Workstation** | A client machine (desktop, laptop, or tablet) accessing D365 F&O through a supported web browser (Edge, Chrome, Safari) — no separate client installation is required. | Ch 1.1 |
| **Workflow** | The automated approval and business process engine in D365 F&O — workflows define routes, conditions, and actions for document approvals and task routing. | Ch 29 |

## X

| Term | Definition | Primary Chapter |
|---|---|---|
| **X++** | The primary development language for D365 F&O — object-oriented, application-aware, data-aware, compiles to .NET CIL, and runs on the AOS. | Ch 1.2, 3 |
| **X++ IL** | The compiled form of X++ code — X++ compiles to .NET CIL (Common Intermediate Language), the low-level format used by the .NET runtime to execute code efficiently. | Ch 1.1 |
| **XDS (Extensible Data Security)** | A policy-based security framework that controls access to data at the row and field level — applies security rules dynamically based on context, roles, and query ranges. | Ch 15 |

---

## Quick Reference: Security Hierarchy

```
Permission → Privilege (composed of permissions) → Duty (composed of privileges) → Role (composed of duties) → User (assigned one or more roles)
```

| Level | What It Controls | Example |
|---|---|---|
| **Permission** | Access to a specific table/field + read/write/delete/create | `CustTable` Read, `CustTable` Write |
| **Privilege** | A collection of permissions | `CustTable Maintenance` |
| **Duty** | A collection of privileges | `Customer Maintenance` |
| **Role** | A collection of duties assigned to a user | `Accounts Receivable Manager` |
| **User** | Assigned one or more roles | `Ahmed` → `Accounts Receivable Manager` |
