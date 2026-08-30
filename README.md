# Dynamics 365 Finance & Operations (D365 F&O) Developer Handbook

## Project Overview

This project is a comprehensive learning guide for a Technical Microsoft Dynamics 365 Finance & Operations developer/technical intern. It spans a **4–12 month learning journey** designed to take you from foundational concepts through advanced enterprise development patterns.

The handbook covers the complete technical stack of D365 F&O, including X++ programming, system architecture, data modeling, form development, business logic, extensibility patterns, security, integration, reporting, testing, DevOps, and performance optimization.

## Project Goals

- **Master Core Concepts:** Learn the four pillars of D365 F&O architecture, data layer design, and the X++ programming language
- **Build Real Solutions:** Create custom tables, forms, business logic classes, and extensions following Microsoft best practices
- **Understand Extensibility:** Master Chain of Custody (CoC), Event Handlers, and Delegates for non-invasive customizations
- **Implement Enterprise Patterns:** Learn RunBase, SysOperation, batch processing, SSRS reporting, and integration patterns
- **Deploy with Confidence:** Understand security, testing, DevOps pipelines, and performance optimization
- **Achieve Certification:** Prepare for Microsoft MB-310 or MB-330 certifications

## Curriculum Structure — 12-Month Roadmap

### Phase 1: Foundations (Month 1)
- **Theme:** Understand the platform and write your first X++ code
- **Topics:** Core concepts, first X++ job, data queries using `select` and `while select`
- **Deliverable:** A working X++ job reading from `CustTable` with infolog output
- **Checkpoint:** Explain differences between `select` and `while select`; describe the four pillars of D365 F&O architecture

### Phase 2: Data Layer Deep Dive (Month 2)
- **Theme:** Master tables, EDTs, and data integrity
- **Topics:** Table design, Extended Data Types (EDTs), field groups, alternate indexes, table validation
- **Deliverable:** Custom table with 8+ fields, 2 EDTs, 1 field group, 1 alternate index, and `validateWrite()` override
- **Checkpoint:** Explain EDT importance and impacts of changing `StringSize`; describe alternate vs. hash indexes

### Phase 3: UI & Business Logic (Month 3)
- **Theme:** Build forms and write business logic classes
- **Topics:** Form controls, parent-child data sources, form queries, RunBase pattern, business orchestration
- **Deliverable:** Form with 2 data sources (parent-child), 3 action pane actions, and orchestrating business logic class
- **Checkpoint:** Explain `Inner Join`, `Outer Join`, `Exists Join` differences; describe the RunBase pattern

### Phase 4: Extensibility Patterns (Month 4)
- **Theme:** Master CoC, Event Handlers, and Delegates
- **Topics:** Chain of Custody, event subscription, delegate patterns, non-invasive customization
- **Deliverable:** Extension using CoC, Event Handler, and Delegate with proper execution order
- **Checkpoint:** Determine when to use CoC vs. Event Handlers vs. Delegates; explain execution order

### Phase 5: Security & Integration (Month 5)
- **Theme:** Understand D365 F&O security and build integrations
- **Topics:** Security roles, duties, privileges, data entities, OData endpoints, integration patterns
- **Deliverable:** Custom security role with 2 duties and 4 privileges; data entity exposing custom table to external systems
- **Checkpoint:** Trace privilege → duty → role → user path; explain Data Entity vs. Data Project

### Phase 6: Reporting & Batch Processing (Month 6)
- **Theme:** Build reports and batch jobs
- **Topics:** SSRS reports, `SrsReportDataProvider`, `RunBaseBatch`, background processing
- **Deliverable:** SSRS report with custom data provider + `RunBaseBatch` job for background processing
- **Checkpoint:** Explain `SrsReportDataProvider` vs. standard `ReportRun`; describe `BatchHeader` class purpose

### Phase 7: Testing & Quality (Month 7)
- **Theme:** Write tests and establish QA practices
- **Topics:** SysTest framework, unit testing, acceptance test library (ATL), RSAT
- **Deliverable:** 5 unit tests covering table validation, class logic, and form behavior
- **Checkpoint:** Differentiate between SysTest and ATL; explain when to use RSAT

### Phase 8: DevOps & Deployment (Month 8)
- **Theme:** Automate builds and manage deployments
- **Topics:** Azure DevOps pipelines, build automation, `.axmodel` artifacts, configuration keys
- **Deliverable:** Azure DevOps build pipeline with X++ compilation, unit tests, and artifact generation
- **Checkpoint:** Differentiate build vs. release pipelines in LCS; explain configuration keys

### Phase 9: Performance & Troubleshooting (Month 9)
- **Theme:** Optimize code and diagnose issues
- **Topics:** SQL performance anti-patterns, `CacheLookup`, query optimization, bottleneck identification
- **Deliverable:** Performance audit identifying 3+ bottlenecks with rewrites
- **Checkpoint:** List top 5 SQL anti-patterns in X++; explain `CacheLookup` performance impact

### Phase 10: Capstone Project (Month 10)
- **Theme:** End-to-end production scenario
- **Topics:** Full solution architecture and deployment
- **Deliverable:** Complete solution: table + EDT + form + business logic + security role + data entity + SSRS report + batch job, deployed to test environment
- **Checkpoint:** Walk through entire solution explaining design decisions

### Phase 11: Module Specialization (Month 11)
- **Theme:** Go deep in your chosen module (Finance, SCM, or HR)
- **Topics:** Module-specific tables, workflows, business processes
- **Deliverable:** Module-specific deep-dive document with code samples and end-to-end data flow analysis
- **Checkpoint:** Explain end-to-end business process; identify key tables, EDTs, and logic classes

### Phase 12: Advanced Patterns & Certification Prep (Month 12)
- **Theme:** Master advanced patterns and prepare for certification
- **Topics:** Workflow extensibility, E-Signature, BI/Power BI integration, certification exam prep
- **Deliverable:** Certification study guide with annotated code samples and mock exam self-assessment
- **Checkpoint:** Demonstrate mastery of all previous concepts; walk through complete end-to-end solutions

## Key Files in This Repository

- **d365-learning-guide.md** — Condensed learning guide with key concepts and quick references
- **d365-fao-learning-journey.md** — Detailed month-by-month study plan and milestones
- **d365-xpp-quick-reference.md** — Quick reference for X++ syntax and common patterns
- **d365-xpp-exercises.md** — Hands-on coding exercises for each phase
- **d365-glossary.md** — Comprehensive glossary of D365 F&O terminology
- **d365-guide-cross-reference.md** — Index linking all guides and resources

## How to Use This Handbook

1. **Start with Phase 1:** Begin with foundational concepts in `D365_Combined_Guide.md`
2. **Follow the Study Plan:** Work through each month's theme, chapters, and deliverable
3. **Reference the Quick Guides:** Use `d365-xpp-quick-reference.md` for syntax lookups
4. **Complete Exercises:** Work through `d365-xpp-exercises.md` for hands-on practice
5. **Track Progress:** Mark off milestones as you complete each month
6. **Review Checkpoints:** Answer checkpoint questions before moving to the next phase

## Learning Outcomes

Upon completion of this 12-month journey, you will be able to:

✅ Write production-grade X++ code following D365 F&O best practices  
✅ Design and implement custom tables, EDTs, forms, and business logic  
✅ Apply extensibility patterns without modifying base code  
✅ Implement security models, roles, and privileges  
✅ Build integrations using data entities and APIs  
✅ Create SSRS reports and batch processing jobs  
✅ Write comprehensive unit tests  
✅ Set up CI/CD pipelines for automated deployments  
✅ Optimize code for performance and diagnose issues  
✅ Deploy complete end-to-end solutions  
✅ Specialize in Finance, SCM, or HR modules  
✅ Prepare for Microsoft D365 F&O certifications (MB-310, MB-330)

## Prerequisites

- Basic programming knowledge (any language)
- Understanding of relational databases
- Familiarity with cloud platforms (Azure) is helpful
- Access to a D365 F&O development environment or sandbox

## Additional Resources

- Microsoft Learn: [Dynamics 365 Finance & Operations](https://learn.microsoft.com/en-us/dynamics365/finance-operations/)
- Microsoft Docs: [X++ Language Reference](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-language-reference)
- **Certifications:** [Microsoft Learn Certification Path](https://learn.microsoft.com/en-us/credentials/browse/?roles=developer&products=dynamics-365)

## About This Project

This is a **Technical Developer Handbook** designed for interns and junior developers aiming to master D365 Finance & Operations development. It combines conceptual learning with hands-on coding exercises, real-world patterns, and a structured progression from basics to advanced topics.

---

**Last Updated:** August 31, 2026  
**Format:** Comprehensive learning guide with 12-phase curriculum, code examples, and practical exercises
