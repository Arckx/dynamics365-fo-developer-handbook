# Data Management Basics for Dynamics 365 Finance & Operations

This guide introduces the core concepts of **Data Management Framework (DMF)**, **Data Entities**, and **import/export** processes for new developers.

---
## 1. What is the Data Management Framework?

The DMF provides a **declarative, metadata‑driven** way to move data in and out of D365 FO. It powers the **Data Import/Export** workspace in LCS and the **Data Entity** APIs.

- **Data Entity** – a logical representation of one or more tables, exposing a flat view for import/export.
- **Staging tables** – temporary tables used during import to validate and transform data before it reaches the target tables.
- **Mapping** – defines how source columns map to target entity fields.

---
## 2. Creating a Data Entity

1. In **Visual Studio**, create a new **Data Entity** project item.
2. Set the **Root Data Source** to the primary table (e.g., `VendTable`).
3. Add **Fields** you want to expose – you can include fields from related tables via **Relations**.
4. Set **`IsPublic = Yes`** to expose the entity via OData.
5. Build and synchronize the project.

> **Tip:** Use the **Entity Wizard** (`File → New → Data Entity`) to scaffold the entity quickly.

---
## 3. Importing Data

1. Open the **Data Management** workspace in the web client.
2. Click **Import** → **Add file** (CSV, Excel, XML).
3. Choose the **Data Entity** you created.
4. Map source columns to entity fields (auto‑mapping works for matching names).
5. Run the import – the system validates data in staging tables, then applies it to the target tables.

### Common Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid data type` | Source column type mismatches target field type | Adjust source file or modify entity field type. |
| `Duplicate key` | Primary key already exists in target table | Use **Update** mode or clean target data before import. |

---
## 4. Exporting Data

1. In **Data Management**, click **Export**.
2. Select the **Data Entity** you want to export.
3. Choose the **Target format** (CSV, Excel, XML).
4. Run the export – the system generates a file with the entity’s data.

---
## 5. Using Data Entities via OData

When `IsPublic = Yes`, the entity is exposed through the **OData endpoint**:

```
https://<environment>.cloudax.dynamics.com/data/<EntityName>
```

You can query, filter, and paginate using standard OData query options (`$filter`, `$select`, `$top`).

---
## 6. Best Practices

- **Keep entities small** – expose only the fields needed for the integration.
- **Use staging tables** for heavy transformations; avoid complex logic in the entity itself.
- **Version entities** – when changing fields, create a new version to avoid breaking existing integrations.
- **Document mappings** – maintain a CSV of source → target column mappings for each integration.

---
## 7. Further Reading (Microsoft Docs)

- [Data entities in D365 FO](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/data-entities)
- [Import and export data](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/import-export-data)
- [OData services](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata-services)

---
*Part of the foundational improvements to give new developers a clear entry point into data management.*