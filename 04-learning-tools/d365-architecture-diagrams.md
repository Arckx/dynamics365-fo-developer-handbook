---
name: d365-architecture-diagrams
description: Mermaid.js diagrams for D365 F&O architecture - four pillars, request flow, layers, CoC, security, batch, data entities
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Architecture Diagrams

> **Glossary:** See the [Business Glossary](../00-foundations/d365-business-glossary.md) for term definitions.

> **Copy-paste these into Markdown viewers that support Mermaid** (GitHub, VS Code, Notion, Obsidian, mkdocs-material)

---

## 1. Four Pillars Architecture

```mermaid
graph TB
    subgraph Presentation["Presentation Tier"]
        Browser[Browser: Edge/Chrome/Safari]
        HTML5[HTML5/CSS/JS]
    end

    subgraph Application["⚙️ Application Tier (AOS)"]
        XPP[X++ IL Runtime]
        Security[Security Engine]
        Txn[Transaction Manager]
        Metadata[Metadata Cache]
        Batch[Batch Runtime]
    end

    subgraph Database["🗄️ Database Tier"]
        SQL[(Azure SQL Database)]
        Tables[Tables & Indexes]
        Procs[Stored Procedures]
        TempDB[TempDB]
    end

    subgraph Integration["🔗 Integration Tier"]
        OData[OData Endpoints]
        REST[REST APIs]
        ServiceBus[Azure Service Bus]
        LogicApps[Logic Apps]
        PowerPlatform[Power Platform]
    end

    Browser -->|HTTP/JSON| XPP
    XPP -->|Security Checks| Security
    XPP -->|Txn Mgmt| Txn
    XPP -->|Metadata| Metadata
    XPP -->|SQL| SQL
    SQL -->|Tables| Tables
    XPP -->|Batch Jobs| Batch
    XPP -->|OData/REST| OData
    OData -->|Async| ServiceBus
    ServiceBus --> LogicApps
    LogicApps --> PowerPlatform

    classDef tier fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef component fill:#fff3e0,stroke:#f57c00,stroke-width:1px
    class Presentation,Application,Database,Integration tier
    class Browser,HTML5,XPP,Security,Txn,Metadata,Batch,SQL,Tables,Procs,TempDB,OData,REST,ServiceBus,LogicApps,PowerPlatform component
```

---

## 2. Request Flow Lifecycle

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Browser as 🌐 Browser
    participant AOS as ⚙️ AOS
    participant SQL as 🗄️ SQL
    participant Client as Client

    User->>Browser: Click button
    Browser->>AOS: HTTP Request + Context
    AOS->>AOS: Security Check
    AOS->>AOS: ttsBegin
    AOS->>AOS: Execute X++ IL
    AOS->>SQL: Generated SQL
    SQL->>AOS: Result Set
    AOS->>AOS: ttsCommit
    AOS->>Browser: XML/JSON Response
    Browser->>Client: Form Refresh + Infolog
    Client->>User: Updated UI
```

---

## 3. Layer Hierarchy (SYS → USR)

```mermaid
graph TD
    SYS[SYS<br/>Microsoft Core<br/>🔒 Immutable]
    ISV[ISV<br/>Partner Solutions<br/>📦 Deployable Packages]
    VAR[VAR<br/>Localization/Verticals<br/>🌍 Country-specific]
    CUS[CUS<br/>Customer Customizations<br/>🏢 Your Code]
    USR[USR<br/>User Personalizations<br/>👤 Form layouts]

    SYS -->|Over-layered by| ISV
    ISV -->|Over-layered by| VAR
    VAR -->|Over-layered by| CUS
    CUS -->|Over-layered by| USR

    style SYS fill:#ffebee,stroke:#c62828
    style ISV fill:#fff3e0,stroke:#e65100
    style VAR fill:#e8f5e9,stroke:#2e7d32
    style CUS fill:#e3f2fd,stroke:#1565c0
    style USR fill:#f3e5f5,stroke:#6a1b9a
```

---

## 4. Chain of Command (CoC) Execution Order

```mermaid
sequenceDiagram
    participant Caller
    participant Base as Base Method (SYS)
    participant Ext1 as Extension 1 (ISV)
    participant Ext2 as Extension 2 (VAR)
    participant Ext3 as Extension 3 (CUS)

    Caller->>Ext3: validateWrite()
    Ext3->>Ext2: next validateWrite()
    Ext2->>Ext1: next validateWrite()
    Ext1->>Base: next validateWrite()
    Base-->>Ext1: return boolean
    Ext1-->>Ext2: return boolean
    Ext2-->>Ext3: return boolean
    Ext3-->>Caller: return boolean

    Note over Ext3,Base: Each extension can:<br/>• Modify before next()<br/>• Modify after next()<br/>• Skip next() entirely (rare)
```

---

## 5. Security Hierarchy

```mermaid
graph TD
    Role[Security Role<br/>e.g. Accounts Payable Clerk]
    Duty1[Duty<br/>Process Vendor Invoices]
    Duty2[Duty<br/>Manage Vendor Payments]
    Priv1[Privilege<br/>View Vendors]
    Priv2[Privilege<br/>Create Purchase Orders]
    Priv3[Privilege<br/>Approve Invoices]
    Perm1[Permission<br/>VendTable: Read]
    Perm2[Permission<br/>PurchTable: Create]
    Perm3[Permission<br/>VendInvoiceJour: Update]

    Role --> Duty1
    Role --> Duty2
    Duty1 --> Priv1
    Duty1 --> Priv2
    Duty2 --> Priv3
    Priv1 --> Perm1
    Priv2 --> Perm2
    Priv3 --> Perm3

    classDef role fill:#e3f2fd,stroke:#1565c0
    classDef duty fill:#fff3e0,stroke:#e65100
    classDef priv fill:#e8f5e9,stroke:#2e7d32
    classDef perm fill:#fce4ec,stroke:#c2185b
    class Role role
    class Duty1,Duty2 duty
    class Priv1,Priv2,Priv3 priv
    class Perm1,Perm2,Perm3 perm
```

---

## 6. Extensible Data Security (XDS) Flow

```mermaid
flowchart TD
    User["User Query"] --> Kernel["Kernel Query Execution"]
    Kernel --> Policy{XDS Policy Assigned to Role?}
    Policy -->|No| Normal["Normal Query All Rows"]
    Policy -->|Yes| Filter["Apply Policy Filter"]
    Filter --> Constrained["Constrained Fixed Value"]
    Filter --> Contextual["Contextual currentCompany()"]
    Filter --> RoleBased["Role-Based UserHasRole()"]
    Filter --> Hierarchical["Hierarchical Org Structure"]
    Constrained --> SQL["Modified SQL WHERE PolicyCondition"]
    Contextual --> SQL
    RoleBased --> SQL
    Hierarchical --> SQL
    SQL --> Results["Filtered Results"]

    style Policy fill:#fff3e0,stroke:#e65100
    style Normal fill:#e8f5e9,stroke:#2e7d32
    style Filter fill:#ffebee,stroke:#c62828
```

---

## 6. Batch Processing Architecture

```mermaid
graph TB
    subgraph Client["Client"]
        UI[User submits batch]
    end

    subgraph Controller["📋 SysOperation Controller"]
        Ctrl[Controller Class]
        Dialog[Auto-generated Dialog]
        Params[Parameters/DataContract]
    end

    subgraph Service["⚙️ SysOperation Service"]
        Svc[Service Class]
        Logic[Business Logic]
        Txn[Transaction Scope]
    end

    subgraph Batch["⏰ Batch Runtime"]
        Framework[Batch Framework]
        Server[Batch Server]
        Tasks[Batch Tasks]
        Retry[Retry Logic]
    end

    subgraph DB["🗄️ Database"]
        BatchTable[(Batch Table)]
        BatchJob[(Batch Job)]
        BatchHist[(Batch History)]
    end

    UI --> Ctrl
    Ctrl --> Dialog
    Dialog --> Params
    Ctrl -->|Async/Sync| Framework
    Framework --> Server
    Server --> Tasks
    Tasks --> Svc
    Svc --> Logic
    Logic --> Txn
    Txn --> DB
    Framework --> BatchTable
    Framework --> BatchJob
    Framework --> BatchHist
    Retry -.-> Tasks

    style Ctrl fill:#e3f2fd,stroke:#1565c0
    style Svc fill:#fff3e0,stroke:#e65100
    style Framework fill:#e8f5e9,stroke:#2e7d32
```

---

## 7. Data Entity Staging Pattern

```mermaid
graph LR
    Source[External Source<br/>File/API/DB] --> DMF[DMF Import]
    DMF --> Staging[(Staging Table)]
    Staging --> Validation[Validate/Transform]
    Validation -->|Success| Target[Target Entity<br/>Business Logic]
    Validation -->|Fail| Error[Error Log]
    Target --> DB[(Database)]
    DB --> Export[DMF Export]
    Export --> Staging2[(Staging Table)]
    Staging2 --> Destination[External Destination]

    style DMF fill:#e3f2fd,stroke:#1565c0
    style Staging fill:#fff3e0,stroke:#e65100
    style Target fill:#e8f5e9,stroke:#2e7d32
    style Error fill:#ffebee,stroke:#c62828
```

---

## 8. SysOperation Pattern (Controller → Service)

```mermaid
sequenceDiagram
    participant User
    participant MenuItem as MenuItemAction
    participant Controller as Controller
    participant Dialog as Dialog
    participant Service as Service
    participant DB as Database

    User->>MenuItem: Click menu item
    MenuItem->>Controller: new()
    Controller->>Dialog: Show dialog
    User->>Dialog: Enter parameters
    Dialog->>Controller: Parameters
    Controller->>Service: Execute (async/sync)
    Service->>Service: Validate
    Service->>DB: ttsBegin
    Service->>DB: Business Logic
    Service->>DB: ttsCommit
    Service-->>Controller: Result
    Controller-->>User: Infolog/Message
```

---

## 9. Number Sequence Flow

```mermaid
flowchart TD
    Request["Code calls NumberSeq_newGetNum"] --> Scope{Scope?}
    Scope -->|Company| CompanyScope["Company Scope DataAreaId"]
    Scope -->|Shared| SharedScope["Shared Scope Global"]
    Scope -->|Legal Entity| LegalScope["Legal Entity Scope Partition + Company"]
    
    CompanyScope --> Format["Format String e.g. INV-####"]
    SharedScope --> Format
    LegalScope --> Format
    
    Format --> Alloc["Allocate Next from Sequence Table"]
    Alloc --> Cache["Cache in Memory (Qty = Preallocation)"]
    Cache --> Return["Return Number"]
    Return --> DB["Persist to DB Async"]
    
    style Alloc fill:#e3f2fd,stroke:#1565c0
    style Cache fill:#fff3e0,stroke:#e65100
```

---

## 10. Form Architecture (MVC-ish)

```mermaid
graph TB
    subgraph Form["📋 Form Definition (AOT)"]
        Design[Form Design]
        DS1[Data Source 1<br/>CustTable]
        DS2[Data Source 2<br/>SalesTable]
        Controls[Controls<br/>Grid, Fields, Buttons]
        Methods[Form Methods<br/>init, run, validate]
    end

    subgraph Runtime["🏃 Runtime (FormRun)"]
        Instance[Form Instance]
        Query[QueryRun]
        Buffer1[CustTable Buffer]
        Buffer2[SalesTable Buffer]
        Event[Event Handlers]
    end

    Design --> Instance
    DS1 --> Query
    DS1 --> Buffer1
    DS2 --> Buffer2
    Controls --> Instance
    Methods --> Event
    Query --> Buffer1
    Query --> Buffer2

    style Design fill:#e3f2fd,stroke:#1565c0
    style Instance fill:#e8f5e9,stroke:#2e7d32
```

---

## 11. Test Pyramid

```mermaid
graph TD
    E2E["E2E/UI Tests RSAT, Playwright 🐢 Slow, Expensive ▲ Few (5%)"]
    Integration["Integration Tests SysTest + DB ⚡ Medium ■ Some (15%)"]
    Unit["Unit Tests Property-based, SysTest 🚀 Fast, Cheap ● Many (80%)"]

    E2E --> Integration
    Integration --> Unit

    style E2E fill:#ffebee,stroke:#c62828
    style Integration fill:#fff3e0,stroke:#e65100
    style Unit fill:#e8f5e9,stroke:#2e7d32
```

---

## 12. CI/CD Pipeline Flow

```mermaid
graph LR
    Dev[Developer] -->|Push| Git[Git Repo]
    Git -->|Trigger| Build[Build Pipeline]
    Build -->|Compile| Compile[X++ Compile]
    Compile -->|BP Check| BP[Best Practice]
    BP -->|Unit Test| Unit[SysTest]
    Unit -->|Package| Package[.axmodel]
    Package -->|Artifact| Artifacts[Build Artifacts]
    Artifacts -->|Deploy| Release[Release Pipeline]
    Release -->|Tier-1| DevEnv[Tier-1 Dev]
    DevEnv -->|Validate| Smoke[Smoke Tests]
    Smoke -->|Promote| UAT[UAT via LCS]
    UAT -->|Approve| Prod[Production via LCS]

    style Build fill:#e3f2fd,stroke:#1565c0
    style Release fill:#e8f5e9,stroke:#2e7d32
    style Artifacts fill:#fff3e0,stroke:#e65100
```

---

## 13. How to Render These

### In VS Code:
1. Install **"Markdown Preview Mermaid Support"** extension
2. Open this file → `Ctrl+Shift+V` (Preview)

### In GitHub:
- Automatically renders in `.md` files

### In Notion/Obsidian:
- Paste into a code block with `mermaid` language

### In MkDocs (Documentation Site):
```yaml
# mkdocs.yml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

---

## 14. Diagram Source Files

All diagrams above are **Mermaid.js source** — edit the code blocks to customize.

> **Tip:** Use [Mermaid Live Editor](https://mermaid.live/) to experiment before committing.

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*

---

