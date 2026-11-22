---
name: d365-role-day-in-life
description: Day-in-the-life scenarios for key D365 F&O roles — AP Clerk, Warehouse Worker, Controller, Buyer, Developer
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Role Day-in-Life

> **Understand your users** — What they do, what screens they use, what pain points they have. This makes you a better developer.

---

## 👩‍💼 Accounts Payable Clerk — "Maria"

### Profile
- **Experience:** 3 years AP, 1 year D365 F&O
- **Volume:** 50-80 invoices/day
- **Pain Points:** Matching exceptions, vendor calls, duplicate invoices

### Daily Flow

| Time | Activity | D365 F&O Forms | Pain Points |
|------|----------|----------------|-------------|
| 8:00 | Open email, download vendor PDFs | — | Manual download |
| 8:30 | **Vendor Invoice Register** — header entry | `VendInvoiceRegister` | Repetitive header fields |
| 9:00 | **Invoice Approval Journal** — line entry + matching | `VendInvoiceApprovalJournal` | 3-way match failures |
| 10:30 | **Exceptions** — resolve qty/price mismatches | `VendInvoiceMatch` | No vendor portal access |
| 12:00 | Lunch | — | — |
| 13:00 | **Payment Proposal** — select invoices to pay | `VendPaymProposal` | Manual vendor selection |
| 14:00 | **Payment Journal** — post payments | `VendPaymentJournal` | Bank file format issues |
| 15:00 | **Vendor Inquiries** — answer "where's my payment?" | `VendTransOpen` / `VendInvoiceJour` | Slow search |
| 16:00 | **Monthly Close** — accruals, cut-off | `VendInvoiceJournal` | Manual cut-off entries |

### What She Wishes Developers Knew
- "Default the **Invoice Date** to today — I forget to change it"
- "Show **PO Number** on the invoice line grid — I keep switching tabs"
- "Let me **filter vendors by 'Active' only** — inactive ones clutter search"
- "**Keyboard shortcuts** for Approve/Reject — mouse kills my wrist"

---

## 📦 Warehouse Worker — "James"

### Profile
- **Experience:** 5 years warehouse, 6 months D365 (mobile app)
- **Role:** Picker/Packer on RF gun
- **Volume:** 200+ picks/day

### Daily Flow

| Time | Activity | D365 F&O Mobile App | Pain Points |
|------|----------|---------------------|-------------|
| 6:30 | Login, select **Wave** | Wave List | Wave assignment unclear |
| 6:45 | **Pick Work** — scan LP, location, item | Pick Work | Small buttons on gun |
| 9:00 | **Replenishment** — move bulk to pick face | Replenishment | Location suggestions wrong |
| 10:30 | **Pack** — scan items into shipping box | Pack | Box size suggestions off |
| 12:00 | Lunch | — | — |
| 12:30 | **Load** — scan boxes to trailer | Load | Trailer assignment manual |
| 14:00 | **Cycle Count** — count random locations | Cycle Count | No offline mode |
| 15:30 | **Returns** — receive, inspect, put away | Returns | Damage codes confusing |

### What He Wishes Developers Knew
- "**Bigger scan targets** — gloves + small buttons = errors"
- "**Offline mode** — warehouse has dead zones"
- "**Voice-directed picking** — hands-free would be huge"
- "**Show item image** on pick screen — reduces wrong picks"

---

## 💰 Controller — "David"

### Profile
- **Experience:** 15 years finance, CPA, 2 years D365
- **Focus:** Month-end close, reporting, compliance
- **Team:** 6 accountants

### Daily Flow

| Time | Activity | D365 F&O / Power BI | Pain Points |
|------|----------|---------------------|-------------|
| 7:30 | Review **Trial Balance** | `LedgerTrialBalance` | Slow for 5000 accounts |
| 8:30 | **Journal Review** — approve team entries | `LedgerJournalTable` | No bulk approve |
| 10:00 | **Reconciliations** — bank, intercompany | `BankReconciliation` / `Intercompany` | Manual matching |
| 12:00 | Lunch | — | — |
| 13:00 | **Financial Reports** — P&L, Balance Sheet | Power BI / `FinancialReports` | Report refresh slow |
| 15:00 | **Variance Analysis** — actual vs budget | `BudgetPlan` / Power BI | Drill-through limited |
| 16:30 | **Compliance** — SOX, audit requests | `AuditTrail` / `Security` | Audit trail incomplete |

### What He Wishes Developers Knew
- "**Drill from P&L to voucher in 2 clicks** — not 10"
- "**Lock periods automatically** on close date — human error"
- "**Audit trail on EVERY field change** — not just postings"
- "**Export to Excel with formatting preserved** — re-formatting wastes hours"

---

## 🛒 Buyer / Planner — "Priya"

### Profile
- **Experience:** 4 years procurement, CIPS certified
- **Focus:** PO management, vendor performance, inventory optimization
- **Category:** Raw materials (500+ SKUs)

### Daily Flow

| Time | Activity | D365 F&O Forms | Pain Points |
|------|----------|----------------|-------------|
| 8:00 | **MRP Review** — planned purchase orders | `ReqTrans` / `ReqPlanSched` | Too many false signals |
| 9:30 | **Firm Planned Orders** → PO | `PurchTable` | Manual one-by-one |
| 11:00 | **Vendor Scorecards** — OTIF, quality | Custom / Power BI | Data not in F&O |
| 12:00 | Lunch | — | — |
| 13:00 | **Expedite** — call vendors on late POs | `PurchTable` (Delivery Date) | No vendor portal |
| 14:30 | **Inventory Analysis** — excess, obsolete | `InventSum` / `InventAging` | No predictive insights |
| 16:00 | **New Vendor Setup** — RFQ, evaluation | `VendTable` / `PurchRFQ` | Manual process |

### What She Wishes Developers Knew
- "**Auto-firm POs** when demand is stable — save 2 hrs/day"
- "**Vendor portal** for ASN/acknowledgment — email is broken"
- "**Predictive reorder points** — not just min/max"
- "**Show supplier lead time trend** on PO line — I calculate manually"

---

## 👨‍💻 D365 F&O Developer — "Alex" (You!)

### Profile
- **Experience:** 2 years .NET, 6 months D365
- **Focus:** Customizations, integrations, performance
- **Environment:** Tier-1 dev, VS, Git, Azure DevOps

### Daily Flow

| Time | Activity | Tools | Pain Points |
|------|----------|-------|-------------|
| 8:30 | **Sync** — pull latest, build | VS, Git | Build fails on BP errors |
| 9:00 | **Code Review** — PR comments | Azure DevOps | Reviewers miss perf issues |
| 10:00 | **Feature Work** — CoC extension | VS, X++ | Debugging standard code |
| 12:00 | Lunch | — | — |
| 13:00 | **Integration** — OData / Logic Apps | Postman, Azure | Token expiry, throttling |
| 15:00 | **Performance** — Trace Parser | Trace Parser, SQL | Interpreting plans |
| 16:30 | **Deploy** — create package, LCS | LCS, DevOps | Sync DB takes 20 min |

### What You Should Know About Your Users
- **They don't know X++** — they know business process
- **They measure in minutes saved** — not lines of code
- **They fear upgrades** — "will my customization break?"
- **They want consistency** — same patterns everywhere

---

## 🎭 Role Empathy Exercise

**Do this once per sprint:**

1. **Pick a role** (not your own)
2. **Shadow for 30 minutes** — watch them work
3. **Note 3 friction points** — where they struggle
4. **Build one small fix** — keyboard shortcut, default value, filter
5. **Watch them use it** — did it help?

---

## 📋 Developer Checklist per Role

| Role | Must-Test Scenarios |
|------|---------------------|
| **AP Clerk** | High-volume entry, matching exceptions, payment runs |
| **Warehouse** | Mobile app offline, glove-friendly UI, scan speed |
| **Controller** | Month-end close, drill-through, audit trail |
| **Buyer** | MRP noise, vendor communication, inventory visibility |
| **Developer** | Build pipeline, debug standard code, deploy speed |

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*