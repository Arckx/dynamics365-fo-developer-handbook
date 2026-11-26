---
name: d365-foundations
description: Chapter 0 — ERP concepts, D365 F&O modules, business processes, Azure basics for absolute beginners
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Foundations — Chapter 0

> **Glossary:** See the [Business Glossary](d365-business-glossary.md) for term definitions.

> **Read this BEFORE Chapter 1** if you're new to ERP, enterprise software, or cloud platforms. This chapter assumes zero prior knowledge.

---

## 1. What Is an ERP?

### 1.1 The Problem ERP Solves

Imagine a company with **separate systems** for each department:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    FINANCE      │  │    SALES        │  │  INVENTORY      │  │     HR          │
│  (QuickBooks)   │  │  (Salesforce)   │  │  (Spreadsheet)  │  │  (BambooHR)     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Invoices      │  │ • Orders        │  │ • Stock levels  │  │ • Employees     │
│ • Payments      │  │ • Quotes        │  │ • Warehouses    │  │ • Payroll       │
│ • GL            │  │ • Customers     │  │ • Purchase orders│ │ • Benefits      │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │                    │
         └────────────────────┼────────────────────┼────────────────────┘
                              ▼
                    **DATA SILOS PROBLEM**
         • Finance doesn't know real-time inventory
         • Sales sells items not in stock
         • HR pays people who left (no link to Finance)
         • Monthly close takes 2 weeks of manual reconciliation
```

**ERP (Enterprise Resource Planning)** = **One integrated system** sharing a **single database** across all departments.

### 1.2 ERP Core Principle

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   One Database  →  One Customer Record  →  All Departments     │
│                                                                  │
│   Sales creates Customer  →  Finance sees it instantly         │
│   Warehouse ships order  →  Finance invoices automatically     │
│   HR hires employee    →  Payroll, Security, Badge access auto │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Key ERP Modules

| Module | Business Function | Key Entities |
|--------|-------------------|--------------|
| **Finance (GL/AP/AR)** | General ledger, payables, receivables, fixed assets, budgeting | Journal, Invoice, Vendor, Customer, Asset |
| **Supply Chain (SCM)** | Procurement, inventory, warehouse, production, planning | Purchase Order, Item, Warehouse, BOM, Route |
| **Human Resources** | Personnel, payroll, benefits, recruitment, training | Worker, Position, Benefit, Leave |
| **Commerce** | Retail, e-commerce, POS, call center | Store, Channel, Catalog, Loyalty |
| **Project Operations** | Project management, resource scheduling, billing | Project, Work Breakdown, Timesheet |

---

## 2. What Is Dynamics 365 Finance & Operations?

### 2.1 The Product Family

```
Microsoft Dynamics 365
├── Customer Engagement (CE) Apps — CRM-style
│   ├── Sales
│   ├── Customer Service
│   ├── Marketing
│   └── Field Service
│
└── Finance & Operations (F&O) Apps — ERP-style
    ├── Finance          ← Core financials
    ├── Supply Chain     ← SCM, Manufacturing, Retail
    ├── Commerce         ← Retail, E-commerce
    ├── Human Resources  ← HR, Payroll
    └── Project Operations ← Project-based services
```

> **This handbook covers D365 F&O** (the ERP side), not CE (the CRM side).

### 2.2 D365 F&O at a Glance

| Attribute | Detail |
|-----------|--------|
| **Type** | Cloud SaaS (Software as a Service) |
| **Hosting** | Microsoft Azure (you don't manage servers) |
| **Architecture** | Multi-tenant with data isolation |
| **Updates** | Continuous (monthly quality updates, biannual feature updates) |
| **Language** | X++ (C#-like, runs on .NET CLR) |
| **Database** | Azure SQL Database (shared instance, your schema) |
| **UI** | Browser-based (HTML5), no thick client |
| **Extensibility** | Metadata-driven, no over-layering (Chain of Command) |

### 2.3 Who Uses D365 F&O?

| Role | What They Do in F&O |
|------|---------------------|
| **CFO/Controller** | Financial reporting, close, compliance |
| **AP/AR Clerk** | Process invoices, payments, collections |
| **Buyer/Planner** | Purchase orders, requisitions, MRP |
| **Warehouse Worker** | Receive, pick, pack, ship, cycle count |
| **Production Supervisor** | Release orders, report progress, scrap |
| **Project Manager** | Track costs, bill clients, resource allocation |
| **HR Specialist** | Onboard, benefits, leave, compensation |
| **IT/Developer** | **YOU** — customize, integrate, extend |

---

## 3. Business Processes You'll Automate

### 3.1 Procure-to-Pay (P2P)

```
Vendor Quote → Purchase Requisition → Purchase Order → Goods Receipt → Vendor Invoice → Payment
     │              │                    │               │               │             │
     ▼              ▼                    ▼               ▼               ▼             ▼
  (External)   (Internal approval)   (Legal commit)  (Warehouse)   (AP matching)  (Bank)
```

**Your code touches:** `PurchTable`, `PurchLine`, `PurchParmTable`, `VendInvoiceJour`, `LedgerJournalTrans`

### 3.2 Order-to-Cash (O2C)

```
Sales Quotation → Sales Order → Pick/Pack/Ship → Customer Invoice → Payment Collection
      │               │              │                 │                  │
      ▼               ▼              ▼                 ▼                  ▼
   (CRM/External)  (Credit check)  (Warehouse)     (AR posting)       (Bank rec)
```

**Your code touches:** `SalesTable`, `SalesLine`, `CustPackingSlipJour`, `CustInvoiceJour`, `CustTrans`

### 3.3 Record-to-Report (R2R)

```
Journal Entry → Approval → Post → Trial Balance → Financial Statements → Close
     │            │         │        │                 │                 │
     ▼            ▼         ▼        ▼                 ▼                 ▼
  (Manual/      (Workflow)  (GL)    (Dimension       (SSRS/ER)        (Period
   Auto)                                            balancing)            close)
```

**Your code touches:** `LedgerJournalTable`, `LedgerJournalTrans`, `DimensionAttributeValue`, `FinancialReport`

---

## 4. Cloud & Azure Basics

### 4.1 Cloud Service Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOU MANAGE LESS →                            │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  On-Prem    │    IaaS     │    PaaS     │       SaaS          │
│  (Your DC)  │  (Azure VM) │ (Azure SQL) │  (D365 F&O)         │
├─────────────┼─────────────┼─────────────┼─────────────────────┤
│ Hardware    │ ✓ You       │ ✓ MS        │ ✓ MS                │
│ OS          │ ✓ You       │ ✓ MS        │ ✓ MS                │
│ Runtime     │ ✓ You       │ ✓ You       │ ✓ MS                │
│ App         │ ✓ You       │ ✓ You       │ ✓ You (config)      │
│ Data        │ ✓ You       │ ✓ You       │ ✓ You (your data)   │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

**D365 F&O = SaaS** — Microsoft manages everything up to the application. You configure and extend.

### 4.2 Azure Resources You'll Encounter

| Resource | Purpose | Developer Interaction |
|----------|---------|----------------------|
| **Azure SQL Database** | Your business data | Query via X++, DMF, OData |
| **Azure App Service** | AOS workers | Deploy models via LCS |
| **Azure DevOps** | CI/CD pipelines | Build, test, release |
| **Azure Key Vault** | Secrets, certificates | Reference in code via config keys |
| **Azure Storage** | File shares, blobs | Model store, DMF staging |
| **Azure AD / Entra ID** | Authentication | Users, groups, service principals |
| **Azure Service Bus** | Async messaging | Integration patterns |
| **Application Insights** | Monitoring | Custom telemetry (see observability guide) |

### 4.3 Environments in D365 F&O

| Environment | Purpose | Access |
|-------------|---------|--------|
| **Tier-1 (Dev)** | Your personal sandbox, full admin | VS, SQL, AOS, LCS |
| **Tier-2 (Build)** | Automated build agent | Azure DevOps only |
| **Tier-3/4 (UAT/Prod)** | Microsoft-managed, no admin | LCS, browser only |
| **Sandbox** | Copy of prod for testing | LCS deploy |

---

## 5. How D365 F&O Differs from Traditional Development

### 5.1 Traditional App vs D365 F&O

| Aspect | Traditional (C#/Java) | D365 F&O (X++) |
|--------|----------------------|----------------|
| **Data Access** | ORM (EF, Hibernate) | Direct `select` / Data Entities |
| **Schema Changes** | Migrations (code-first) | AOT metadata → sync |
| **Deployment** | Docker/K8s/IIS | LCS deployable packages |
| **UI** | React/Angular/Blazor | Metadata forms (AOT) |
| **Business Logic** | Domain models | Tables + Classes + Services |
| **Customization** | Fork/override | Extensions only (CoC) |
| **Upgrades** | Your problem | Microsoft handles platform |

### 5.2 The "Metadata-First" Mindset

```
Traditional:        Code defines structure → Database created
                    class Customer { string Name; }

D365 F&O:           Metadata defines structure → Code generated
                    Table: CustTable
                      Field: Name (String 60, EDT: CustName)
                    → SQL CREATE TABLE
                    → X++ class with .Name property
                    → Form auto-generates field
```

**You design in the AOT (Visual Studio), not in code files.**

---

## 6. Key Terminology Cheat Sheet

| Term | Simple Definition |
|------|-------------------|
| **AOT** | Application Object Tree — where all metadata lives (tables, forms, classes) |
| **Model** | A container for your customizations (like a VS project) |
| **Package** | Compiled model (.axmodel file) ready for deployment |
| **Layer** | Isolation level (SYS, ISV, VAR, CUS, USR) — higher wins |
| **Extension** | Adding to standard objects without modifying them |
| **CoC** | Chain of Command — call `next` to run base logic |
| **Data Entity** | Business document view (header+lines) for import/export/OData |
| **DMF** | Data Management Framework — bulk data import/export |
| **LCS** | Lifecycle Services — deployment, monitoring, support portal |
| **Legal Entity** | A company with its own chart of accounts, tax, reporting |
| **Partition** | Physical data separation (rarely used, mostly for hosting) |
| **Number Sequence** | Automatic ID generation (invoice numbers, customer IDs) |

---

## 7. Your First Week Checklist

Before writing code, complete these:

- [ ] **Get a Tier-1 VM** — Ask your admin or provision via LCS
- [ ] **Install Visual Studio 2022** + **Dynamics 365 Development Tools**
- [ ] **Clone this handbook repo** — `git clone <url>`
- [ ] **Open `d365-learning-guide.md`** — Start at Chapter 1
- [ ] **Run Exercise 1** — `d365-xpp-exercises.md` → Exercise 1
- [ ] **Join the D365 community** — #d365fo on Twitter, Dynamics 365 Community forums

---

## 8. Learning Path Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR 12-MONTH JOURNEY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MONTH 1-3: FOUNDATIONS          MONTH 4-6: EXTENSIBILITY       │
│  ┌─────────────────────────┐     ┌─────────────────────────┐    │
│  │ Ch 1: Architecture      │     │ Ch 9: Tables, EDTs      │    │
│  │ Ch 2: Models, Layers    │     │ Ch 10: Forms, CoC       │    │
│  │ Ch 3: VS, Mindset       │     │ Ch 11: Views, Lookups   │    │
│  │ Ch 4: LCS, DevOps       │     │ Ch 12: Classes, RunBase │    │
│  │ Ch 5: X++ Types         │     │ Ch 13: Events           │    │
│  │ Ch 6: CRUD, Transactions│     │ Ch 14: Extensibility    │    │
│  │ Ch 7: Methods, Classes  │     │ Ch 15: Security         │    │
│  │ Ch 8: Debugging         │     │                          │    │
│  └─────────────────────────┘     └─────────────────────────┘    │
│                                                                  │
│  MONTH 7-9: QUALITY & PERF        MONTH 10-12: ENTERPRISE       │
│  ┌─────────────────────────┐     ┌─────────────────────────┐    │
│  │ Ch 16: Data Entities    │     │ Ch 22: Capstone         │    │
│  │ Ch 17: SSRS, ER         │     │ Ch 23: Advanced X++     │    │
│  │ Ch 18: Batch            │     │ Ch 24: Prod Debugging   │    │
│  │ Ch 19: SysTest          │     │ Ch 25: Power Platform   │    │
│  │ Ch 20: CI/CD            │     │ Ch 26: Module Deep Dive │    │
│  │ Ch 21: SQL Tuning       │     │ Ch 27: Advanced DevOps  │    │
│  │                          │     │ Ch 28: Compliance       │    │
│  └─────────────────────────┘     └─────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Resources for Deeper Understanding

| Resource | Link | Best For |
|----------|------|----------|
| **D365 F&O Architecture** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/architecture/ | Platform internals |
| **ERP Fundamentals** | https://www.microsoft.com/en-us/dynamics-365/erp | Business context |
| **Azure Fundamentals** | https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/ | Cloud basics |
| **X++ Language Reference** | https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language | Syntax deep dive |

---

## Official Microsoft Documentation
- [Dynamics 365 Finance & Operations docs](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/)
- [X++ programming guide](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language)
- [Data entities overview](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities)
## 10. Quick Self-Test

Before moving to Chapter 1, answer these:

1. **What does ERP stand for?** Enterprise Resource Planning
2. **What problem does ERP solve?** Data silos — integrates all departments into one system
3. **What is D365 F&O?** Microsoft's cloud ERP (SaaS) for finance, supply chain, HR, projects
4. **What language does D365 F&O use?** X++ (runs on .NET CLR)
5. **What is the AOT?** Application Object Tree — metadata repository for all objects
6. **What is a Model?** Container for your customizations (like a project)
7. **What is a Layer?** Isolation level — SYS (Microsoft) → ISV → VAR → CUS → USR
8. **What is CoC?** Chain of Command — extension pattern using `next` keyword
9. **What is a Data Entity?** Business document view for import/export/OData
10. **What is LCS?** Lifecycle Services — deployment and monitoring portal

> **If you got 8+ correct:** You're ready for Chapter 1!  
> **If less:** Re-read sections 1-6, then try again.

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*