---
name: d365-business-glossary
description: Business terminology for D365 F&O — P2P, O2C, MRP, BOM, financial terms, supply chain terms
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Business Glossary

> **Non-technical business terms** you'll hear daily. Technical terms are in `d365-glossary.md`.

---

## 📦 Procure-to-Pay (P2P) — Buying Stuff

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **Purchase Requisition (PR)** | Internal request to buy something | `PurchReqTable` |
| **Request for Quotation (RFQ)** | Asking vendors for prices | `PurchRFQTable` |
| **Purchase Order (PO)** | Legal commitment to buy | `PurchTable` / `PurchLine` |
| **Goods Receipt / Product Receipt** | Recording what arrived at warehouse | `PurchParmTable` |
| **Vendor Invoice** | Bill from supplier | `VendInvoiceJour` / `VendInvoiceTrans` |
| **Invoice Matching** | 2-way (PO=Invoice) or 3-way (PO=Receipt=Invoice) | `VendInvoiceMatch` |
| **Payment Journal** | Paying vendors | `VendPaymMode` / `LedgerJournalTable` |
| **Three-Way Match** | PO quantity = Receipt quantity = Invoice quantity | AP Parameter |
| **Landed Cost** | Purchase price + freight + duties + insurance | `InventTrans` + `Costing` |
| **Blanket PO** | Agreement for multiple deliveries over time | `PurchTable` (type=Blanket) |

---

## 💰 Order-to-Cash (O2C) — Selling Stuff

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **Sales Quotation** | Price offer to customer | `SalesQuotationTable` |
| **Sales Order (SO)** | Customer's purchase commitment | `SalesTable` / `SalesLine` |
| **Credit Check** | Verify customer can pay | `CustCreditMaxCheck` |
| **Reservation** | Allocating inventory to order | `InventTrans` (Status=Reserved) |
| **Pick / Pack** | Warehouse: gather items, put in boxes | `WMSPickingRoute` / `WHSPack` |
| **Ship / Dispatch** | Hand to carrier, print labels | `CustPackingSlipJour` |
| **Customer Invoice** | Bill sent to customer | `CustInvoiceJour` / `CustInvoiceTrans` |
| **Payment Collection** | Receiving money from customer | `CustTrans` / `LedgerJournalTable` |
| **Cash Application** | Matching payment to invoice | `CustOpenTrans` |
| **Credit Memo / Return** | Refund or return processing | `SalesTable` (type=Return) |
| **Backorder** | Order placed but stock not available | `SalesLine` (Backorder qty) |

---

## 🏭 Manufacturing & Planning

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **Bill of Materials (BOM)** | Recipe: what components make a product | `BOMTable` / `BOMVersion` |
| **Route / Routing** | Steps: work centers, times, sequence | `RouteTable` / `RouteVersion` |
| **Work Center** | Machine or labor group where work happens | `WrkCtrTable` / `WrkCtrGroup` |
| **Production Order** | Work order to manufacture | `ProdTable` |
| **Production BOM** | Components for specific production order | `ProdBOM` |
| **Production Route** | Operations for specific production order | `ProdRoute` / `ProdRouteTrans` |
| **Job Scheduling** | Detailed: specific machine, person, time | `ProdRouteJob` |
| **Operations Scheduling** | Rough: work center, day level | `ProdRouteTrans` |
| **Material Requirements Planning (MRP)** | Calculate what to buy/make based on demand | `ReqPlanSched` / `ReqTrans` |
| **Master Planning** | MRP + capacity + scheduling | `ReqPlanSched` |
| **Planned Order** | System suggestion: buy or make | `ReqTrans` (Action=Buy/Make) |
| **Firming** | Convert planned order → actual PO/Production | `ReqTransFirm` |
| **Kanban** | Visual pull system for lean manufacturing | `KanbanRule` / `Kanban` |
| **Co-product / By-product** | Multiple outputs from one production | `BOMTable` (CoProduct) |

---

## 📊 Inventory & Warehouse

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **On-Hand** | Quantity physically in warehouse | `InventSum` / `InventOnHand` |
| **Available** | On-Hand − Reserved − Quarantine | `InventSum` (AvailPhysical) |
| **Reserved** | Allocated to sales/production | `InventSum` (ReservPhysical) |
| **Quarantine** | Quality hold — not available | `InventQuarantine` |
| **Location** | Specific spot: Aisle-Rack-Shelf-Bin | `InventLocation` / `WMSLocation` |
| **License Plate (LP)** | Container ID (pallet, box, tote) | `WMSLicensePlateTable` |
| **Wave** | Group of work released together | `WMSWaveTable` |
| **Work** | Individual task: pick, put, count | `WMSWorkTable` |
| **Cycle Count** | Periodic inventory audit | `InventCountTable` |
| **ABC Classification** | A=high value, B=medium, C=low | `InventABC` |
| **Safety Stock** | Minimum buffer quantity | `InventMinMax` |
| **Reorder Point** | Trigger for replenishment | `InventMinMax` |
| **Transfer Order** | Move stock between warehouses | `InventTransferTable` |

---

## 💵 Financial Terms

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **Chart of Accounts** | List of all GL accounts | `LedgerChartOfAccounts` |
| **Main Account** | Individual GL account (P&L or Balance Sheet) | `MainAccount` |
| **Dimension** | Tag for reporting: Department, CostCenter, Project | `DimensionAttribute` |
| **Dimension Value** | Specific value: "IT Dept", "Project Alpha" | `DimensionAttributeValue` |
| **Journal** | Batch of accounting entries | `LedgerJournalTable` |
| **Journal Line** | One debit/credit entry | `LedgerJournalTrans` |
| **Voucher** | Unique ID for a balanced journal | `LedgerJournalTrans` (Voucher) |
| **Posting** | Making entries permanent in GL | `LedgerPosting` |
| **Trial Balance** | List all accounts with debit/credit totals | `LedgerTrialBalance` |
| **Period Close** | Lock period, run adjustments, report | `LedgerPeriod` / `LedgerClosing` |
| **Year-End Close** | Reset P&L to Retained Earnings | `LedgerFiscalCalendar` |
| **Fixed Asset** | Long-term tangible asset | `AssetTable` |
| **Depreciation** | Allocate asset cost over life | `AssetBook` / `AssetDepreciation` |
| **Budget** | Planned financial targets | `BudgetPlan` / `BudgetRegister` |
| **Cash Flow** | In/out of cash forecasting | `CashFlowForecast` |

---

## 👥 HR & Payroll

| Term | Definition | D365 F&O Area |
|------|------------|---------------|
| **Worker** | Person employed (employee or contractor) | `HcmWorker` |
| **Position** | Job slot: "Senior Developer" (can be vacant) | `HcmPosition` |
| **Job** | Role definition: duties, competencies | `HcmJob` |
| **Employment** | Worker + Position + Dates | `HcmEmployment` |
| **Compensation** | Salary, bonus, benefits | `HcmCompensation` |
| **Benefit** | Health, 401k, PTO | `HcmBenefit` |
| **Leave / Absence** | Vacation, sick, FMLA | `HcmLeave` |
| **Time & Attendance** | Clock in/out, overtime | `JmgRegistration` |
| **Payroll** | Calculate gross → net → pay | `PaymPayroll` |
| **Tax Region** | Jurisdiction for payroll taxes | `PaymTaxRegion` |

---

## 🔧 Common Acronyms

| Acronym | Full Form |
|---------|-----------|
| **P2P** | Procure-to-Pay |
| **O2C** | Order-to-Cash |
| **MRP** | Material Requirements Planning |
| **BOM** | Bill of Materials |
| **SKU** | Stock Keeping Unit (Item) |
| **LP** | License Plate |
| **WMS** | Warehouse Management System |
| **GL** | General Ledger |
| **AP** | Accounts Payable |
| **AR** | Accounts Receivable |
| **COGS** | Cost of Goods Sold |
| **PO** | Purchase Order |
| **SO** | Sales Order |
| **PR** | Purchase Requisition |
| **RFQ** | Request for Quotation |
| **GRN** | Goods Receipt Note |
| **ETA** | Estimated Time of Arrival |
| **SLA** | Service Level Agreement |
| **RMA** | Return Merchandise Authorization |
| **EOL** | End of Life (product) |
| **MOQ** | Minimum Order Quantity |
| **LT** | Lead Time |

---

## 🎯 How to Use This

1. **When you hear a term in meetings** → Look it up here
2. **Before each module chapter** → Review relevant section
3. **Create flashcards** for terms you forget
4. **Ask business users** to explain their process using these terms

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*