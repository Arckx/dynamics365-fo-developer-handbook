# Dynamics 365 Finance & Operations (D365 F&O) Developer Handbook

> A production-grade technical handbook, 30-chapter desktop guide, and 12-month learning journey designed for Microsoft D365 F&O developers, technical interns, and enterprise engineers.

---

## 🚀 Quick Start — Where Should You Go?

Depending on what you are looking for, jump straight to the right file:
- **If you are starting your learning journey:** Read [`d365-fao-learning-journey.md`](d365-fao-learning-journey.md) and [`d365-guide-cross-reference.md`](d365-guide-cross-reference.md).
- **If you want the complete 30-chapter technical desktop guide:** Open [`d365-learning-guide.md`](d365-learning-guide.md) (covers X++, architecture, tables, forms, workflows, services, and VSI enterprise patterns).
- **If you are reviewing real-world VSI codebase patterns & architecture gaps:** Read [`VSI_GAP_ANALYSIS.md`](VSI_GAP_ANALYSIS.md).
- **If you need quick X++ syntax lookups:** Keep [`d365-xpp-quick-reference.md`](d365-xpp-quick-reference.md) open.
- **If you need to master batch processing architecture:** Read [`BatchProcessinginD365F&ORunBaseBatchvsSysOperation.md`](BatchProcessinginD365F&ORunBaseBatchvsSysOperation.md).

---

## 📂 Repository Structure & Key Files

| File | Description | Best For |
|---|---|---|
| [`d365-learning-guide.md`](d365-learning-guide.md) | **30-Chapter Desktop Guide** with full code examples, tables, and activities. Includes VSI enterprise patterns (`VSIAssetServiceHelper`, `VSIAssetNotificationHelper`, `SysQueryRangeUtil`, etc.). | In-depth technical study & code reference |
| [`d365-fao-learning-journey.md`](d365-fao-learning-journey.md) | **12-Month Structured Study Plan** with milestones and deliverables. | Structuring an internship or training program |
| [`d365-guide-cross-reference.md`](d365-guide-cross-reference.md) | **Master Index & Mapping Table** linking curriculum phases to desktop guide chapters. | Navigating between concepts |
| [`d365-xpp-quick-reference.md`](d365-xpp-quick-reference.md) | **X++ Syntax Cheat Sheet** (CRUD, CoC, LINQ-style queries, exception handling). | Quick syntax checks while coding |
| [`d365-xpp-exercises.md`](d365-xpp-exercises.md) | **Hands-On Coding Exercises** mapped to each learning phase. | Practicing core concepts |
| [`d365-glossary.md`](d365-glossary.md) | **D365 F&O Glossary** of terms (AOT, EDTs, CoC, XDS, etc.). | Terminology lookups |
| [`VSI_GAP_ANALYSIS.md`](VSI_GAP_ANALYSIS.md) | **VSI Enterprise Codebase Gap Analysis** and architectural enhancement roadmap. | Advanced architectural review |
| [`BatchProcessinginD365F&ORunBaseBatchvsSysOperation.md`](BatchProcessinginD365F&ORunBaseBatchvsSysOperation.md) | **Batch Processing Comparison** (`RunBaseBatch` vs. `SysOperationServiceController`). | Designing background jobs |

---

## 📚 Curriculum At-a-Glance (12-Month Roadmap)

The curriculum is structured into 4 foundational quarters and 12 progressive phases:

- **Quarter 1 (Months 1–3): Foundations & Data Layer**
  - *Phase 1:* Platform Architecture & First X++ Job
  - *Phase 2:* Tables, EDTs, Alternate Indexes & Data Integrity
  - *Phase 3:* Forms, Parent-Child Data Sources & Business Logic Classes
- **Quarter 2 (Months 4–6): Extensibility & Backend Architecture**
  - *Phase 4:* Chain of Command (CoC) & Event Handlers (No base code edits!)
  - *Phase 5:* Security Hierarchies (Roles/Duties/Privileges) & Data Entities
  - *Phase 6:* SSRS Reporting & Batch Processing (`RunBaseBatch` / `SysOperation`)
- **Quarter 3 (Months 7–9): Quality, DevOps & Advanced Performance**
  - *Phase 7:* Unit Testing (`SysTest`), ATL & RSAT
  - *Phase 8:* Azure DevOps Build Pipelines, LCS & Release Management
  - *Phase 9:* SQL Performance Tuning, Caching Strategies & Deadlock Handling
- **Quarter 4 (Months 10–12): Enterprise Solutions & Module Specialization**
  - *Phase 10:* End-to-End Capstone Project Solution Architecture
  - *Phase 11:* Module Specialization Deep Dive (Finance, SCM, HR, Retail, or Project Operations + Capstones A–E)
  - *Phase 12:* Advanced Patterns (Workflows, Number Sequences, Custom JSON Services) & Certification Prep (MB-310 / MB-330)

---

## ✨ Key Learning Outcomes

Upon completing this handbook, developers will be able to:
✅ Write production-grade, maintainable X++ following Microsoft best practices  
✅ Implement non-invasive customizations using Chain of Command (CoC)  
✅ Design secure tables, EDTs, forms, and custom data entities  
✅ Build asynchronous background batch jobs and custom SSRS reports  
✅ Configure automated Azure DevOps CI/CD pipelines and unit tests  
✅ Troubleshoot and optimize complex SQL queries and memory caching  
✅ Specialize in core D365 F&O enterprise modules (Finance, SCM, HR, Retail, Project Operations)  
✅ Prepare for Microsoft certifications **MB-310** (Finance) and **MB-330** (Supply Chain)

---

## 🛠️ Prerequisites & Environment Setup

- **Development Environment:** Access to a D365 F&O Development VM or Tier-1 Cloud Hosted Environment with Visual Studio.
- **Skills:** Basic object-oriented programming experience and relational database fundamentals (SQL).
- **Recommended Tools:** Visual Studio with Dynamics 365 Add-in, Azure DevOps, LCS (Lifecycle Services).

---

**Last Updated:** November 13, 2026  
**Target Audience:** Technical Interns, Junior-to-Senior X++ Developers, Enterprise Solution Architects.
