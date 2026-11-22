---
name: d365-perf-benchmark
description: D365 F&O performance benchmarking — scripts, queries, cache hit ratios, batch throughput
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Performance Benchmarking Guide

> **Target audience:** Developers and performance engineers measuring, tuning, and validating D365 F&O performance.

---

## 1. Benchmarking Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PERFORMANCE TESTING PYRAMID                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     ┌─────────────────────┐                                                  │
│     │   PRODUCTION-LIKE   │  ← Full load test (monthly)                     │
│     │   LOAD TEST         │     Real data volumes, real integrations        │
│     └─────────────────────┘                                                  │
│         ┌─────────────────────┐                                              │
│         │   INTEGRATION       │  ← Scenario tests (weekly)                  │
│         │   PERFORMANCE       │     Key business flows end-to-end           │
│         └─────────────────────┘                                              │
│             ┌─────────────────────┐                                          │
│             │   UNIT PERFORMANCE  │  ← Microbenchmarks (every build)        │
│             │   (Microbenchmarks) │     Single method, query, batch         │
│             └─────────────────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Microbenchmarks (Unit Level)

### 2.1 X++ Benchmark Harness

```xpp
/// <summary>
/// Lightweight benchmark runner for X++ code
/// </summary>
class Benchmark
{
    struct Result
    {
        str name;
        int iterations;
        real avgMs;
        real minMs;
        real maxMs;
        real p50Ms;
        real p95Ms;
        real p99Ms;
        int64 totalTicks;
    }
    
    /// <summary>
    /// Run a benchmark with statistical analysis
    /// </summary>
    public static Result run(
        str _name,
        int _iterations,
        delegate void _action(),
        delegate void _setup() = null,
        delegate void _teardown() = null)
    {
        List durations = new List(Types::Real);
        int i;
        UTCDateTime start;
        TimeSpan duration;
        real ms;
        ;
        
        // Warmup (not measured)
        for (i = 1; i <= 5; i++)
        {
            if (_setup) _setup();
            _action();
            if (_teardown) _teardown();
        }
        
        // Measured runs
        for (i = 1; i <= _iterations; i++)
        {
            if (_setup) _setup();
            
            start = DateTimeUtil::utcNow();
            _action();
            duration = DateTimeUtil::utcNow() - start;
            
            if (_teardown) _teardown();
            
            ms = duration.TotalMilliseconds;
            durations.addEnd(ms);
        }
        
        return Benchmark::calculateStats(_name, _iterations, durations);
    }
    
    private static Result calculateStats(str _name, int _iterations, List _durations)
    {
        Result result;
        real sum = 0;
        real min = 999999;
        real max = 0;
        List sorted = new List(Types::Real);
        int i;
        ;
        
        // Sort for percentiles
        for (i = 1; i <= _durations.elements(); i++)
        {
            real d = _durations.item(i);
            sorted.addEnd(d);
            sum += d;
            if (d < min) min = d;
            if (d > max) max = d;
        }
        
        // Simple sort (bubble - fine for small arrays)
        sorted = Benchmark::sortList(sorted);
        
        result.name = _name;
        result.iterations = _iterations;
        result.avgMs = sum / _iterations;
        result.minMs = min;
        result.maxMs = max;
        result.p50Ms = sorted.item((_iterations * 50) / 100);
        result.p95Ms = sorted.item((_iterations * 95) / 100);
        result.p99Ms = sorted.item((_iterations * 99) / 100);
        result.totalTicks = 0; // Would need high-res timer
        
        return result;
    }
    
    private static List sortList(List _list)
    {
        // Quick sort implementation
        // Simplified - use .NET List.Sort in real implementation
        return _list;
    }
    
    public static void printResult(Result _result)
    {
        info(strFmt("%1: avg=%.2fms min=%.2fms max=%.2fms p50=%.2fms p95=%.2fms p99=%.2fms (%2 iterations)",
            _result.name, _result.avgMs, _result.minMs, _result.maxMs,
            _result.p50Ms, _result.p95Ms, _result.p99Ms, _result.iterations));
    }
    
    public static void compareResults(Result _baseline, Result _candidate)
    {
        real speedup = _baseline.avgMs / _candidate.avgMs;
        str verdict = speedup > 1.0 ? "FASTER" : "SLOWER";
        
        info(strFmt("COMPARISON: %1 vs %2", _baseline.name, _candidate.name));
        info(strFmt("  Baseline:  %.2fms avg", _baseline.avgMs));
        info(strFmt("  Candidate: %.2fms avg", _candidate.avgMs));
        info(strFmt("  Speedup:   %.2fx %3", speedup, verdict));
    }
}
```

### 2.2 Benchmark Examples

```xpp
[SysTestCase]
class Microbenchmarks extends SysTestCase
{
    [SysTestMethod]
    public void benchmark_InsertMethods()
    {
        int recordCount = 1000;
        
        // Benchmark 1: Loop insert
        Benchmark.Result loopResult = Benchmark::run(
            "Loop Insert",
            10,
            delegate void()
            {
                int i;
                MyTestTable table;
                for (i = 1; i <= recordCount; i++)
                {
                    table.clear();
                    table.Field1 = int2str(i);
                    table.Field2 = "Test";
                    table.insert();
                }
            },
            delegate void() { delete_from MyTestTable; }
        );
        
        // Benchmark 2: insert_recordset
        Benchmark.Result recordsetResult = Benchmark::run(
            "insert_recordset",
            10,
            delegate void()
            {
                MyTempTable temp;
                int i;
                for (i = 1; i <= recordCount; i++)
                {
                    temp.clear();
                    temp.Field1 = int2str(i);
                    temp.Field2 = "Test";
                    temp.insert();
                }
                insert_recordset MyTestTable (Field1, Field2)
                    select Field1, Field2 from temp;
            },
            delegate void() 
            { 
                delete_from MyTestTable; 
                delete_from MyTempTable; 
            }
        );
        
        Benchmark::printResult(loopResult);
        Benchmark::printResult(recordsetResult);
        Benchmark::compareResults(loopResult, recordsetResult);
        
        // Assert: insert_recordset should be at least 5x faster
        this.assertTrue(recordsetResult.avgMs * 5 < loopResult.avgMs);
    }
    
    [SysTestMethod]
    public void benchmark_QueryPatterns()
    {
        // Setup: Create test data
        this.createTestCustomers(10000);
        
        // Pattern 1: while select with where
        Benchmark.Result whileSelect = Benchmark::run(
            "while select where",
            20,
            delegate void()
            {
                CustTable cust;
                while select cust
                    where cust.CustGroup == "10"
                {
                    // Process
                }
            }
        );
        
        // Pattern 2: exists join
        Benchmark.Result existsJoin = Benchmark::run(
            "exists join",
            20,
            delegate void()
            {
                CustTable cust;
                SalesTable sales;
                while select cust
                    exists join sales
                        where sales.CustAccount == cust.AccountNum
                           && sales.SalesStatus == SalesStatus::OpenOrder
                {
                    // Process
                }
            }
        );
        
        Benchmark::printResult(whileSelect);
        Benchmark::printResult(existsJoin);
    }
}
```

---

## 3. SQL Query Analysis

### 3.1 Key DMV Queries

```sql
-- 1. Top 20 most expensive queries (by total CPU)
SELECT TOP 20
    qs.total_worker_time / qs.execution_count AS avg_cpu_ms,
    qs.total_elapsed_time / qs.execution_count AS avg_duration_ms,
    qs.execution_count,
    qs.total_logical_reads / qs.execution_count AS avg_logical_reads,
    SUBSTRING(qt.text, (qs.statement_start_offset/2) + 1,
        ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(qt.text)
         ELSE qs.statement_end_offset END - qs.statement_start_offset)/2) + 1) AS query_text,
    qp.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
CROSS APPLY sys.dm_exec_query_plan(qs.plan_handle) qp
WHERE qt.dbid = DB_ID()
ORDER BY avg_cpu_ms DESC;

-- 2. Queries with missing indexes
SELECT TOP 20
    migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans) AS improvement_measure,
    'CREATE INDEX [IX_' + OBJECT_NAME(mid.object_id) + '_' + 
     REPLACE(REPLACE(REPLACE(mid.equality_columns, ', ', '_'), '[', ''), ']', '') + ']' +
     ' ON ' + OBJECT_SCHEMA_NAME(mid.object_id) + '.' + OBJECT_NAME(mid.object_id) +
     ' (' + ISNULL(mid.equality_columns, '') + 
     CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ',' ELSE '' END +
     ISNULL(mid.inequality_columns, '') + ')' +
     ISNULL(' INCLUDE (' + mid.included_columns + ')', '') AS create_index_statement,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_groups mig
JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
JOIN sys.dm_db_missing_index_details mid ON mid.index_handle = mig.index_handle
WHERE mid.database_id = DB_ID()
ORDER BY improvement_measure DESC;

-- 3. Cache hit ratio
SELECT 
    (1.0 - (CAST(cntr_value AS FLOAT) / 
     CASE WHEN (SELECT cntr_value FROM sys.dm_os_performance_counters 
                WHERE counter_name = 'Page reads/sec' AND instance_name = '_Total') > 0
          THEN (SELECT cntr_value FROM sys.dm_os_performance_counters 
                WHERE counter_name = 'Page reads/sec' AND instance_name = '_Total')
          ELSE 1 END)) * 100.0 AS cache_hit_ratio_percent
FROM sys.dm_os_performance_counters
WHERE counter_name = 'Buffer cache hit ratio';

-- 4. Deadlock graph (run during deadlock)
SELECT 
    xed.value('@timestamp', 'datetime') AS deadlock_time,
    xed.query('.') AS deadlock_graph
FROM (
    SELECT CAST(target_data AS XML) AS target_data
    FROM sys.dm_xe_session_targets st
    JOIN sys.dm_xe_sessions s ON s.address = st.event_session_address
    WHERE s.name = 'system_health'
      AND st.target_name = 'ring_buffer'
) AS src
CROSS APPLY target_data.nodes('//event[@name="xml_deadlock_report"]') AS x(xed);

-- 5. Table fragmentation
SELECT 
    OBJECT_NAME(ips.object_id) AS table_name,
    i.name AS index_name,
    ips.index_type_desc,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
JOIN sys.indexes i ON i.object_id = ips.object_id AND i.index_id = ips.index_id
WHERE ips.avg_fragmentation_in_percent > 10
  AND ips.page_count > 1000
ORDER BY ips.avg_fragmentation_in_percent DESC;

-- 6. Blocking queries
SELECT 
    r.session_id,
    r.blocking_session_id,
    r.wait_type,
    r.wait_time,
    r.cpu_time,
    r.total_elapsed_time,
    st.text AS sql_text,
    qp.query_plan
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
CROSS APPLY sys.dm_exec_query_plan(r.plan_handle) qp
WHERE r.blocking_session_id > 0;
```

### 3.2 D365 F&O Specific Queries

```sql
-- 1. Find queries hitting specific tables (e.g., InventTrans)
SELECT TOP 50
    qs.execution_count,
    qs.total_elapsed_time / qs.execution_count AS avg_duration_ms,
    qs.total_logical_reads / qs.execution_count AS avg_reads,
    SUBSTRING(qt.text, (qs.statement_start_offset/2) + 1, 200) AS query_preview
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
WHERE qt.text LIKE '%INVENTTRANS%'
   OR qt.text LIKE '%CUSTTRANS%'
   OR qt.text LIKE '%VENDTRANS%'
ORDER BY qs.total_elapsed_time DESC;

-- 2. Check for missing CacheLookup on lookup tables
-- Run in D365 F&O: Check table properties
SELECT 
    t.name AS table_name,
    t.CacheLookup,
    CASE t.CacheLookup 
        WHEN 0 THEN 'None'
        WHEN 1 THEN 'NotInTTS'
        WHEN 2 THEN 'Found'
        WHEN 3 THEN 'FoundAndEmpty'
        WHEN 4 THEN 'EntireTable'
    END AS cache_lookup_desc,
    p.rows AS row_count
FROM ModelElement t
JOIN sys.partitions p ON p.object_id = OBJECT_ID(t.name)
WHERE t.ElementType = 40  -- Table
  AND t.CacheLookup = 0   -- None
  AND p.rows > 1000       -- Large enough to benefit
  AND t.name IN ('CustTable', 'VendTable', 'InventTable', 'EcoResProduct', 
                 'CustGroup', 'VendGroup', 'InventItemGroup', 'UnitOfMeasure');

-- 3. Batch job performance
SELECT 
    bj.Caption,
    bjh.Status,
    bjh.StartDateTime,
    bjh.EndDateTime,
    DATEDIFF(SECOND, bjh.StartDateTime, bjh.EndDateTime) AS duration_seconds,
    bjh.ErrorMessage
FROM BatchJob bj
JOIN BatchJobHistory bjh ON bjh.RecId = bj.RecId
WHERE bjh.Status IN (3, 4) -- Executed, Error
  AND bjh.StartDateTime > DATEADD(DAY, -7, GETDATE())
ORDER BY duration_seconds DESC;
```

---

## 4. Load Testing with RSAT

### 4.1 RSAT Test Case Design

```xml
<!-- RSAT Test Case: Sales Order Create-Post -->
<TestCase>
  <Name>SalesOrder_CreatePost_FullFlow</Name>
  <Description>End-to-end sales order creation and posting</Description>
  <Steps>
    <Step>
      <Action>Navigate</Action>
      <Target>SalesTableListPage</Target>
    </Step>
    <Step>
      <Action>Click</Action>
      <Target>NewButton</Target>
    </Step>
    <Step>
      <Action>SetValue</Action>
      <Target>CustAccount</Target>
      <Data>US-001</Data>
    </Step>
    <Step>
      <Action>SetValue</Action>
      <Target>SalesLine.ItemId</Target>
      <Data>ITEM-001</Data>
    </Step>
    <Step>
      <Action>SetValue</Action>
      <Target>SalesLine.SalesQty</Target>
      <Data>10</Data>
    </Step>
    <Step>
      <Action>Click</Action>
      <Target>SaveButton</Target>
    </Step>
    <Step>
      <Action>Click</Action>
      <Target>PostButton</Target>
    </Step>
    <Step>
      <Action>Verify</Action>
      <Target>Infolog</Target>
      <Expected>Posted</Expected>
    </Step>
  </Steps>
  <Parameters>
    <Parameter Name="Iterations" Value="100" />
    <Parameter Name="ConcurrentUsers" Value="10" />
    <Parameter Name="RampUpSeconds" Value="30" />
  </Parameters>
</TestCase>
```

### 4.2 RSAT Load Test Execution

```powershell
# Run RSAT load test via command line
# Requires RSAT installed and configured

$rsatPath = "C:\Program Files (x86)\Microsoft Dynamics 365\RSAT\Microsoft.Dynamics.RegressionSuite.ConsoleApp.exe"
$testCase = "SalesOrder_CreatePost_FullFlow"
$iterations = 100
$users = 10
$envUrl = "https://perf-env.sandbox.operations.dynamics.com"

& $rsatPath `
    -testcase $testCase `
    -iterations $iterations `
    -users $users `
    -url $envUrl `
    -output "C:\RSATResults\LoadTest_$(Get-Date -Format 'yyyyMMdd_HHmmss').trx"

# Parse results
$results = Import-Clixml "C:\RSATResults\LoadTest_*.trx"
$avgDuration = ($results | Measure-Object -Property Duration -Average).Average
$p95Duration = $results | Sort-Object Duration | Select-Object -Skip ([math]::Floor($results.Count * 0.95)) -First 1
$errorRate = ($results | Where-Object { $_.Outcome -eq 'Failed' }).Count / $results.Count * 100

Write-Host "Avg Duration: $avgDuration ms"
Write-Host "P95 Duration: $($p95Duration.Duration) ms"
Write-Host "Error Rate: $errorRate%"
```

---

## 5. Batch Performance Benchmarking

### 5.1 Batch Throughput Measurement

```xpp
/// <summary>
/// Measure batch job throughput
/// </summary>
class BatchBenchmark
{
    public static void measureThroughput(str _batchJobName, int _testRecords)
    {
        BatchJob batchJob = BatchJob::find(_batchJobName);
        if (!batchJob)
            throw error(strFmt("Batch job %1 not found", _batchJobName));
        
        // Create test data
        BatchBenchmark::createTestData(_testRecords);
        
        // Reset batch
        BatchBenchmark::resetBatchJob(batchJob);
        
        // Start timing
        UTCDateTime start = DateTimeUtil::utcNow();
        
        // Run batch synchronously
        batchJob.runBatchJob();
        
        // Wait for completion
        while (batchJob.status() != BatchStatus::Finished)
        {
            sleep(1000);
        }
        
        TimeSpan duration = DateTimeUtil::utcNow() - start;
        
        real recordsPerSecond = _testRecords / duration.TotalSeconds;
        
        info(strFmt("Batch: %1 | Records: %2 | Duration: %3 sec | Throughput: %.2f rec/sec",
            _batchJobName, _testRecords, duration.TotalSeconds, recordsPerSecond));
        
        // Log to App Insights
        TelemetryClient::getInstance().trackMetric("Batch.Throughput", recordsPerSecond,
            new Map(Types::String, Types::AnyType).fromArray([
                ["jobName", _batchJobName],
                ["recordCount", _testRecords]
            ]));
    }
    
    private static void createTestData(int _count)
    {
        // Override in derived class
    }
    
    private static void resetBatchJob(BatchJob _job)
    {
        // Clear history, reset status
    }
}
```

### 5.2 Batch Concurrency Testing

```xpp
/// <summary>
/// Test batch performance under concurrent load
/// </summary>
class BatchConcurrencyTest
{
    public static void runConcurrencyTest(str _batchJobName, int _concurrentThreads, int _recordsPerThread)
    {
        Thread[] threads = new Thread[_concurrentThreads];
        ManualResetEvent[] events = new ManualResetEvent[_concurrentThreads];
        real[] durations = new real[_concurrentThreads];
        int i;
        ;
        
        for (i = 0; i < _concurrentThreads; i++)
        {
            events[i] = new ManualResetEvent(false);
            int threadIndex = i; // Capture for closure
            
            threads[i] = new Thread(delegate void()
            {
                UTCDateTime start = DateTimeUtil::utcNow();
                
                // Each thread runs its own batch instance
                BatchJob batchJob = BatchJob::createNew(_batchJobName);
                BatchBenchmark::createTestDataForThread(_recordsPerThread, threadIndex);
                batchJob.runBatchJob();
                
                while (batchJob.status() != BatchStatus::Finished)
                {
                    sleep(1000);
                }
                
                durations[threadIndex] = (DateTimeUtil::utcNow() - start).TotalSeconds;
                events[threadIndex].Set();
            });
            
            threads[i].Start();
        }
        
        // Wait for all
        WaitHandle.WaitAll(events);
        
        // Results
        real totalDuration = 0;
        for (i = 0; i < _concurrentThreads; i++)
        {
            totalDuration += durations[i];
            info(strFmt("Thread %1: %.2f sec", i, durations[i]));
        }
        
        real avgDuration = totalDuration / _concurrentThreads;
        real totalRecords = _concurrentThreads * _recordsPerThread;
        real throughput = totalRecords / avgDuration;
        
        info(strFmt("Concurrency: %1 | Avg Duration: %.2f sec | Total Throughput: %.2f rec/sec",
            _concurrentThreads, avgDuration, throughput));
    }
}
```

---

## 6. Form Load Performance

### 6.1 Form Load Measurement

```xpp
/// <summary>
/// Measure form load time with data source counts
/// </summary>
class FormLoadBenchmark
{
    public static void measureFormLoad(str _formName, Map _filters = null)
    {
        // Use FormRun to measure
        Args args = new Args();
        args.name(_formName);
        
        if (_filters)
        {
            MapEnumerator enum = _filters.getEnumerator();
            while (enum.moveNext())
            {
                args.parm(enum.currentKey(), enum.currentValue());
            }
        }
        
        UTCDateTime start = DateTimeUtil::utcNow();
        
        FormRun formRun = ClassFactory.formRunClass(args);
        formRun.init();
        formRun.run();
        
        TimeSpan duration = DateTimeUtil::utcNow() - start;
        
        // Collect data source stats
        Map dsStats = new Map(Types::String, Types::Container);
        FormDataSource ds;
        int i;
        for (i = 1; i <= formRun.dataSourceCount(); i++)
        {
            ds = formRun.dataSource(i);
            dsStats.insert(ds.name(), 
                [ds.query().dataSourceCount(), ds.cursor().rowCount()]);
        }
        
        info(strFmt("Form: %1 | Load Time: %.2f ms | DataSources: %2",
            _formName, duration.TotalMilliseconds, dsStats.elements()));
        
        // Log
        TelemetryClient::getInstance().trackRequest(
            "FormLoad." + _formName, start, duration, "200", true);
    }
}
```

---

## 7. Memory & Cache Analysis

### 7.1 Cache Hit Ratio Monitoring

```xpp
/// <summary>
/// Monitor kernel cache performance
/// </summary>
class CacheMonitor
{
    public static void reportCacheStats()
    {
        // These require kernel API access
        // Run as batch job periodically
        
        Map stats = new Map(Types::String, Types::Real);
        
        // Record cache
        stats.insert("RecordCache.HitRatio", CacheMonitor::getRecordCacheHitRatio());
        stats.insert("RecordCache.Size", CacheMonitor::getRecordCacheSize());
        
        // Session cache
        stats.insert("SessionCache.HitRatio", CacheMonitor::getSessionCacheHitRatio());
        
        // Table cache (EntireTable/Found)
        stats.insert("TableCache.HitRatio", CacheMonitor::getTableCacheHitRatio());
        
        // Log all
        MapEnumerator enum = stats.getEnumerator();
        while (enum.moveNext())
        {
            TelemetryClient::getInstance().trackMetric(enum.currentKey(), enum.currentValue());
            
            // Alert if low
            if (strFind(enum.currentKey(), "HitRatio") && enum.currentValue() < 80)
            {
                TelemetryClient::getInstance().trackEvent("LowCacheHitRatio",
                    new Map(Types::String, Types::AnyType).fromArray([
                        ["metric", enum.currentKey()],
                        ["value", enum.currentValue()]
                    ]));
            }
        }
    }
    
    // These would use kernel APIs
    private static real getRecordCacheHitRatio() { return 0; }
    private static real getRecordCacheSize() { return 0; }
    private static real getSessionCacheHitRatio() { return 0; }
    private static real getTableCacheHitRatio() { return 0; }
}
```

---

## 8. Continuous Performance Validation

### 8.1 Performance Gate in CI/CD

```yaml
# azure-pipelines-perf-gate.yml
- stage: PerformanceGate
  displayName: 'Performance Validation'
  dependsOn: DeployToTest
  condition: succeeded()
  jobs:
  - job: PerfTests
    displayName: 'Run Performance Tests'
    pool:
      vmImage: 'windows-latest'
    timeoutInMinutes: 60
    steps:
    - task: PowerShell@2
      displayName: 'Run Microbenchmarks'
      inputs:
        targetType: 'inline'
        script: |
          # Run unit performance tests
          $testRunner = "C:\AOSService\PackagesLocalDirectory\Bin\Microsoft.Dynamics.AX.Xpp.SysTestRunner.exe"
          & $testRunner -model $(ModelName) -testSuite "Microbenchmarks" -output "$(Build.SourcesDirectory)/PerfResults.trx"
          
          # Parse results and check thresholds
          $results = Import-Clixml "$(Build.SourcesDirectory)/PerfResults.trx"
          
          # Check each benchmark against baseline
          $baselines = @{
              "Loop Insert" = 5000      # ms for 1000 records
              "insert_recordset" = 500  # ms for 1000 records
              "while select where" = 200
              "exists join" = 150
          }
          
          $failed = @()
          foreach ($test in $results) {
              if ($baselines.ContainsKey($test.Name)) {
                  if ($test.AvgMs -gt $baselines[$test.Name] * 1.5) {  # 50% regression threshold
                      $failed += "$($test.Name): $($test.AvgMs)ms (baseline: $($baselines[$test.Name])ms)"
                  }
              }
          }
          
          if ($failed.Count -gt 0) {
              Write-Error "Performance regression detected:`n$($failed -join "`n")"
              exit 1
          }
          
          Write-Host "All performance tests within thresholds"

    - task: PowerShell@2
      displayName: 'Run RSAT Load Test (Sample)'
      inputs:
        targetType: 'inline'
        script: |
          # Run subset of RSAT tests for performance
          # Only critical paths: Sales order, Purchase order, Invoice posting
          $rsatTests = @("SalesOrder_CreatePost", "PurchOrder_CreatePost", "VendInvoice_Post")
          
          foreach ($test in $rsatTests) {
              # Run with 5 iterations, measure avg
              # Compare to baseline
          }
```

### 8.2 Performance Baseline Storage

```xpp
/// <summary>
/// Store and retrieve performance baselines
/// </summary>
class PerfBaseline
{
    public static void saveBaseline(str _testName, real _avgMs, int _iterations)
    {
        PerfBaselineTable baseline;
        ;
        ttsBegin;
        baseline.clear();
        baseline.TestName = _testName;
        baseline.AvgMs = _avgMs;
        baseline.Iterations = _iterations;
        baseline.Environment = SysGlobalConfiguration::getCurrentEnvironment();
        baseline.RecordedDateTime = DateTimeUtil::utcNow();
        baseline.GitCommit = PerfBaseline::getGitCommit();
        baseline.insert();
        ttsCommit;
    }
    
    public static real getBaseline(str _testName)
    {
        PerfBaselineTable baseline;
        ;
        select firstOnly baseline
            order by RecordedDateTime desc
            where baseline.TestName == _testName
               && baseline.Environment == SysGlobalConfiguration::getCurrentEnvironment();
        
        return baseline ? baseline.AvgMs : 0;
    }
    
    public static boolean isRegression(str _testName, real _currentAvgMs, real _threshold = 1.5)
    {
        real baseline = PerfBaseline::getBaseline(_testName);
        if (baseline == 0) return false; // No baseline yet
        
        return _currentAvgMs > baseline * _threshold;
    }
}
```

---

## 9. Microsoft Resources

- **Performance Testing**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/performance-testing
- **SQL Performance**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/sql-performance
- **Trace Parser**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/trace-parser
- **RSAT**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/rsat
- **Perf SDK**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/performance-sdk

---

## 10. Quick Reference Commands

```bash
# Run microbenchmarks
# In X++: Benchmark::run("Name", 10, delegate void() { ... })

# Check SQL cache hit ratio
# SELECT * FROM sys.dm_os_performance_counters WHERE counter_name = 'Buffer cache hit ratio'

# Find slow queries
# sys.dm_exec_query_stats + sys.dm_exec_sql_text

# Run RSAT load test
# Microsoft.Dynamics.RegressionSuite.ConsoleApp.exe -testcase "Name" -iterations 100 -users 10

# Check batch job history
# SELECT * FROM BatchJobHistory WHERE StartDateTime > DATEADD(DAY, -1, GETDATE())

# Monitor cache
# CacheMonitor::reportCacheStats()  # Run as recurring batch
```

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*