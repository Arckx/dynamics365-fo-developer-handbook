# Dynamics 365 Finance & Operations (D365 F&O) Developer Handbook

> The definitive technical handbook, 30-chapter desktop guide, and 12-month learning journey designed for Microsoft D365 F&O developers, technical interns, and enterprise engineers.

---

## The Language Mindset

This handbook is built around a fundamental engineering shift. Developers transitioning from languages like C# or Java must adopt a specific mindset for Dynamics 365:
* **Relational-First, Not Object-First:** The database is the primary focus; data access and movement drive the application architecture.
* **Metadata over Code:** Business logic and configurations are defined in the Application Object Tree (AOT) rather than hardcoded.
* **Extensibility as a Constraint:** Customizations must be non-invasive, relying on Chain of Command (CoC) and Event Handlers to protect the evergreen Microsoft core.

---

## Repository Structure

| File | Description | Recommended Use |
|---|---|---|
| `d365-learning-guide.md` | 30-chapter technical desktop guide with full code examples, tables, and exercises. Covers X++, architecture, tables, forms, workflows, services, and VSI patterns. | In-depth technical study and daily code reference. |
| `d365-fao-learning-journey.md` | 12-month structured study plan with quarterly milestones and deliverables. | Structuring internship programs and training paths. |
| `d365-guide-cross-reference.md` | Master index mapping curriculum phases to desktop guide chapters. | Navigating between study phases and reference chapters. |
| `d365-xpp-quick-reference.md` | X++ syntax cheat sheet covering CRUD operations, CoC, LINQ-style queries, and exception handling. | Quick syntax checks while writing code. |
| `d365-xpp-exercises.md` | Hands-on coding exercises aligned with each learning phase. | Practical application of core concepts. |
| `d365-glossary.md` | Glossary of core D365 terms (AOT, EDTs, CoC, XDS, etc.). | Terminology lookups. |
| `VSI_GAP_ANALYSIS.md` | Analysis of real-world VSI codebase patterns and architectural enhancement roadmap. | Advanced architectural review. |
| `BatchProcessinginD365F&ORunBaseBatchvsSysOperation.md` | Technical comparison of `RunBaseBatch` versus `SysOperationServiceController`. | Designing asynchronous background jobs. |

---

## Curriculum Overview

The curriculum spans four foundational quarters and twelve progressive phases:

* **Quarter 1 (Months 1–3): Foundations and Data Layer**
  - Phase 1: Platform Architecture and First X++ Job
  - Phase 2: Tables, Extended Data Types (EDTs), Alternate Indexes, and Data Integrity
  - Phase 3: Forms, Parent-Child Data Sources, and Business Logic Classes

* **Quarter 2 (Months 4–6): Extensibility and Backend Architecture**
  - Phase 4: Chain of Command (CoC) and Event Handlers
  - Phase 5: Security Hierarchies and Data Entities
  - Phase 6: SSRS Reporting and Batch Processing

* **Quarter 3 (Months 7–9): Quality, DevOps, and Advanced Performance**
  - Phase 7: Unit Testing (`SysTest`), ATL, and RSAT
  - Phase 8: Azure DevOps Build Pipelines, LCS, and Release Management
  - Phase 9: SQL Performance Tuning, Caching Strategies, and Deadlock Handling

* **Quarter 4 (Months 10–12): Enterprise Solutions and Module Specialization**
  - Phase 10: End-to-End Capstone Project Solution Architecture
  - Phase 11: Module Specialization Deep Dive (Finance, SCM, HR, Retail, Project Operations)
  - Phase 12: Advanced Patterns (Workflows, Number Sequences, Custom Services) and Certification Prep (MB-310 / MB-330)

---

## Core Learning Outcomes

Upon completing this handbook, developers will be able to:
* Write production-grade, maintainable X++ following Microsoft best practices.
* Implement non-invasive customizations using Chain of Command.
* Design secure tables, EDTs, forms, and custom data entities.
* Build asynchronous background batch jobs and custom SSRS reports.
* Configure automated Azure DevOps CI/CD pipelines and unit tests.
* Troubleshoot and optimize complex SQL queries and memory caching.
* Specialize in core D365 F&O enterprise modules and prepare for Microsoft certifications MB-310 and MB-330.

---

## Prerequisites and Environment Setup

* **Development Environment:** Access to a D365 F&O Development VM or Tier-1 Cloud Hosted Environment with Visual Studio.
* **Prerequisites:** Basic object-oriented programming experience and relational database fundamentals (SQL).
* **Tooling:** Visual Studio with Dynamics 365 Add-in, Azure DevOps, Lifecycle Services (LCS).

---

**Last Updated:** November 14, 2026  
**Target Audience:** Technical Interns, Junior-to-Senior X++ Developers, Enterprise Solution Architects.
