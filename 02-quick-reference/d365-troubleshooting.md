---
name: d365-troubleshooting
description: Common D365 F&O errors, causes, and fixes
metadata:
  type: reference
---

# D365 F&O — Troubleshooting Guide

> **Quick diagnosis** — Search for your error message or symptom. Each entry: Error → Root Cause → Fix.

---

## Runtime Errors

| Error / Symptom | Root Cause | Fix |
|-----------------|------------|-----|
| **"Object reference not set to an instance of an object"** | Table buffer not initialized (null) | Call `.clear()` or `.initValue()` before use |
| **"Record has been deleted" / `Exception::Broken`** | Buffer refers to deleted record | Re-fetch with `select`; check `RecId` validity |
| **"Deadlock" (`Exception::Deadlock`)** | Two processes hold locks the other needs | 1. Keep transactions short<br>2. Consistent table access order<br>3. Implement retry (max 3) with `sleep(100)` |
| **"Duplicate key"** (`Exception::DuplicateKey`) | Unique index violation on insert | Check `AllowDuplicates = No` on index; use `find()` before `insert()` |
| **"Update conflict" / `RecVersion` mismatch** | Optimistic concurrency — record changed by another process | Re-read record (`reread()`), reapply changes, retry |
| **"Stack overflow" / "Recursion limit"** | Infinite recursion in CoC/event handler | Ensure `next`/`super()` called; check for circular extensions |
| **"License error" / "Configuration key not enabled"** | Required config key disabled | Enable in **License configuration** form |

---

## Compilation / Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| **"The model 'X' cannot be installed because it depends on 'Y'"** | Missing model reference in `ModelManifest.xml` | Add `<ModelReference><Name>Y</Name></ModelReference>` |
| **"Field 'X' does not exist on table 'Y'"** | EDT/field name mismatch or case sensitivity | Verify exact field name in AOT; use `fieldNum()` |
| **"Method 'X' does not exist on class 'Y'"** | Wrong class or method renamed | Check class name; use cross-references (Alt+F12) |
| **"Cannot create a record in 'X'. The record already exists."** | `RecId` collision or duplicate alternate key | Let system generate `RecId`; check alternate index |

---

## Deployment / Sync Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Table not syncing / "Table not found in database"** | Model not deployed or sync skipped | 1. Build → Deploy model<br>2. Run **Database synchronization** in VS<br>3. Check `SysSyncLog` for errors |
| **Form changes not visible** | Form extension not compiled/deployed | Rebuild model; verify extension class is `final` and has `[ExtensionOf]` |
| **Data Entity not in OData** | `IsPublic = No` or missing `Public Collection Name` | Set `IsPublic = Yes`; define `Public Entity Name` & `Public Collection Name` |
| **Batch job stuck "Waiting"** | No batch server for batch group | Configure batch server in **System admin > Server config**; assign batch group |

---

## Performance Issues

| Symptom | Likely Cause | Investigation |
|---------|--------------|---------------|
| **Form loads slowly** | Too many data sources / complex joins / missing indexes | Check `executeQuery()` overrides; run Trace Parser |
| **Report times out** | Large dataset without query optimization | Add ranges; use `SrsReportDataProviderPreProcessTempDB` |
| **Batch job runs for hours** | Row-by-row processing (`while select` + `update()`) | Convert to `update_recordset` / `insert_recordset` |
| **High SQL CPU** | Missing indexes / table scans | Capture query plan in SSMS; add covering indexes |
| **AOS memory pressure** | `InMemory` tables with large datasets | Switch to `TempDB` table type |

---

## Debugging Tips

| Problem | Solution |
|---------|----------|
| **Breakpoint not hitting** | 1. Build/Deploy succeeded?<br>2. Attached to correct process (`w3wp.exe` for web, `Microsoft.Dynamics.AX.Batch.Service.exe` for batch)<br>3. PDBs loaded?<br>4. Code runs on server, not client |
| **Infolog empty in batch** | Check **Batch job history > Log** (not client Infolog) |
| **Need to trace SQL** | Use **Trace Parser** or SQL Profiler on Azure SQL |
| **Inspect query at runtime** | `queryRun.query().dataSourceTable(tableNum(X)).toString()` in debugger |

---

## Common "Why Isn't This Working?" Scenarios

| Scenario | Check |
|----------|-------|
| **CoC extension not executing** | 1. Class is `final`?<br>2. `[ExtensionOf]` attribute correct?<br>3. Model deployed?<br>4. Layer order (CUS > VAR > ISV > SYS) |
| **Event handler not firing** | 1. `[SubscribesTo]` attribute correct table/method?<br>2. Handler is `static`?<br>3. Model deployed? |
| **`validateWrite()` not called** | Using `doInsert()`/`doUpdate()`? Those bypass validation |
| **Number sequence gaps** | Normal behavior — sequences reserve blocks; gaps = rolled-back transactions |
| **Cross-company query returns nothing** | `crossCompany` without container → scans all companies. Use `crossCompany:['USMF']` |

---

## Quick Fixes Checklist

- [ ] **Always** `ttsBegin` / `ttsCommit` / `ttsAbort` for multi-table ops
- [ ] **Never** `select` inside a loop — use `join` / `exists join`
- [ ] **Never** `update()` / `delete()` in loop — use `update_recordset` / `delete_from`
- [ ] **Always** `checkFailed()` not `error()` in `validateWrite()` / `validateField()`
- [ ] **Always** call `super()` FIRST in base override; `next` in CoC
- [ ] **Always** specify fields in `select` — avoid `select *`
- [ ] **Use** `TempDB` not `InMemory` for >1000 rows
- [ ] **Set** `CacheLookup` on lookup/reference tables
- [ ] **Use** EDTs everywhere — never base types in tables/forms
- [ ] **Test** deadlock retry logic (3 attempts, `sleep(100)`)

---

*Part of D365 F&O Developer Handbook • Updated Nov 2026*