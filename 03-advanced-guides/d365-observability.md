---
name: d365-observability
description: D365 F&O observability — Application Insights, custom telemetry, performance counters, alerting rules
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Observability Guide

> **Target audience:** Developers and ops engineers implementing monitoring, alerting, and debugging for D365 F&O production environments.

---

## 1. Observability Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        D365 F&O OBSERVABILITY STACK                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  APPLICATION │    │  INFRASTRUCTURE│   │   BUSINESS   │    │  USER    │  │
│  │   METRICS    │    │   METRICS     │   │   METRICS    │    │  EXPERIENCE│  │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤    ├──────────┤  │
│  │ • X++ exec   │    │ • AOS CPU/    │    │ • Order vol  │    │ • Form   │  │
│  │   time       │    │   Memory      │    │ • Batch succ │    │   load   │  │
│  │ • SQL queries│    │ • SQL DTU     │    │   rate       │    │ • API    │  │
│  │ • Cache hit  │    │ • Storage     │    │ • Error rates│    │   latency│  │
│  │ • Batch dur  │    │ • Network     │    │ • SLA breach │    │ • Errors │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └────┬─────┘  │
│         │                   │                   │                 │         │
│         └───────────────────┼───────────────────┼─────────────────┘         │
│                             ▼                   ▼                           │
│                    ┌─────────────────────────────────────┐                  │
│                    │       APPLICATION INSIGHTS           │                  │
│                    │  (Logs, Metrics, Traces, Live Stream)│                  │
│                    └─────────────────────────────────────┘                  │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   ALERTS    │    │  DASHBOARDS │    │  WORKBOOKS  │                    │
│  │  (Action    │    │  (Grafana/  │    │  (Azure     │                    │
│  │   Groups)   │    │   Azure)    │    │   Monitor)  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Application Insights Integration

### 2.1 Setup Application Insights Resource

```bash
# Azure CLI
az monitor app-insights component create \
  --app d365fo-prod-insights \
  --location eastus \
  --resource-group d365fo-monitoring \
  --kind web \
  --application-type web
```

### 2.2 Instrumentation Key Configuration

Store in **Key Vault** (not in code):

```xpp
/// <summary>
/// Telemetry client for D365 F&O
/// </summary>
class TelemetryClient
{
    private static TelemetryClient instance;
    private Microsoft.ApplicationInsights.TelemetryClient client;
    private str instrumentationKey;
    
    private void new()
    {
        // Get from Key Vault at runtime
        this.instrumentationKey = KeyVaultClient::getSecret("AppInsights-InstrumentationKey");
        
        if (this.instrumentationKey)
        {
            Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration config;
            config = Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration::CreateDefault();
            config.InstrumentationKey = this.instrumentationKey;
            this.client = new Microsoft.ApplicationInsights.TelemetryClient(config);
            
            // Set common properties
            this.client.Context.Cloud.RoleName = "D365FO-AOS";
            this.client.Context.Cloud.RoleInstance = System.Environment::MachineName;
            this.client.Context.Session.Id = System.Guid::NewGuid().ToString();
        }
    }
    
    public static TelemetryClient getInstance()
    {
        if (!instance)
            instance = new TelemetryClient();
        return instance;
    }
    
    // ... tracking methods below
}
```

### 2.3 Custom Telemetry Tracking

```xpp
/// <summary>
/// Track custom events, metrics, and dependencies
/// </summary>
class TelemetryClient
{
    // ... constructor and getInstance from above
    
    /// <summary>Track a business event</summary>
    public void trackEvent(str _eventName, Map _properties = null, Map _metrics = null)
    {
        if (!this.client) return;
        
        Microsoft.ApplicationInsights.DataContracts.EventTelemetry telemetry;
        telemetry = new Microsoft.ApplicationInsights.DataContracts.EventTelemetry(_eventName);
        
        if (_properties)
        {
            MapEnumerator enum = _properties.getEnumerator();
            while (enum.moveNext())
            {
                telemetry.Properties.Add(enum.currentKey(), enum.currentValue());
            }
        }
        
        if (_metrics)
        {
            MapEnumerator enum = _metrics.getEnumerator();
            while (enum.moveNext())
            {
                telemetry.Metrics.Add(enum.currentKey(), anytype2real(enum.currentValue()));
            }
        }
        
        // Add correlation context
        telemetry.Context.Operation.Id = this.getOperationId();
        telemetry.Context.Operation.ParentId = this.getParentOperationId();
        
        this.client.TrackEvent(telemetry);
        this.client.Flush();
    }
    
    /// <summary>Track a metric value</summary>
    public void trackMetric(str _name, real _value, Map _properties = null)
    {
        if (!this.client) return;
        
        Microsoft.ApplicationInsights.DataContracts.MetricTelemetry telemetry;
        telemetry = new Microsoft.ApplicationInsights.DataContracts.MetricTelemetry(_name, _value);
        
        if (_properties)
        {
            MapEnumerator enum = _properties.getEnumerator();
            while (enum.moveNext())
            {
                telemetry.Properties.Add(enum.currentKey(), enum.currentValue());
            }
        }
        
        this.client.TrackMetric(telemetry);
    }
    
    /// <summary>Track a dependency call (SQL, HTTP, external service)</summary>
    public void trackDependency(str _dependencyName, str _command, 
                                UTCDateTime _startTime, TimeSpan _duration,
                                boolean _success, str _resultCode = "", str _target = "")
    {
        if (!this.client) return;
        
        Microsoft.ApplicationInsights.DataContracts.DependencyTelemetry telemetry;
        telemetry = new Microsoft.ApplicationInsights.DataContracts.DependencyTelemetry();
        telemetry.Name = _dependencyName;
        telemetry.Data = _command;
        telemetry.Timestamp = _startTime;
        telemetry.Duration = _duration;
        telemetry.Success = _success;
        telemetry.ResultCode = _resultCode;
        telemetry.Target = _target;
        telemetry.Type = "SQL"; // or "HTTP", "Azure Service Bus", etc.
        
        this.client.TrackDependency(telemetry);
    }
    
    /// <summary>Track an exception</summary>
    public void trackException(Exception _ex, Map _properties = null)
    {
        if (!this.client) return;
        
        Microsoft.ApplicationInsights.DataContracts.ExceptionTelemetry telemetry;
        telemetry = new Microsoft.ApplicationInsights.DataContracts.ExceptionTelemetry(_ex);
        
        if (_properties)
        {
            MapEnumerator enum = _properties.getEnumerator();
            while (enum.moveNext())
            {
                telemetry.Properties.Add(enum.currentKey(), enum.currentValue());
            }
        }
        
        this.client.TrackException(telemetry);
    }
    
    /// <summary>Track a request (form load, API call)</summary>
    public void trackRequest(str _name, UTCDateTime _startTime, TimeSpan _duration,
                             str _responseCode, boolean _success)
    {
        if (!this.client) return;
        
        Microsoft.ApplicationInsights.DataContracts.RequestTelemetry telemetry;
        telemetry = new Microsoft.ApplicationInsights.DataContracts.RequestTelemetry();
        telemetry.Name = _name;
        telemetry.Timestamp = _startTime;
        telemetry.Duration = _duration;
        telemetry.ResponseCode = _responseCode;
        telemetry.Success = _success;
        
        this.client.TrackRequest(telemetry);
    }
    
    // Helper methods for correlation
    private str getOperationId()
    {
        // Use existing correlation ID from context or create new
        return SysCorrelationContext::getCurrentCorrelationId();
    }
    
    private str getParentOperationId()
    {
        return SysCorrelationContext::getCurrentParentCorrelationId();
    }
}
```

---

## 3. X++ Instrumentation Patterns

### 3.1 Method Execution Timing

```xpp
/// <summary>
/// Aspect-oriented timing for any method
/// </summary>
class MethodTimer
{
    public static void timeMethod(str _className, str _methodName, 
                                  delegate void _action())
    {
        UTCDateTime start = DateTimeUtil::utcNow();
        Exception lastException;
        boolean success = true;
        ;
        
        try
        {
            _action();
        }
        catch
        {
            success = false;
            throw;
        }
        finally
        {
            TimeSpan duration = DateTimeUtil::utcNow() - start;
            real durationMs = duration.TotalMilliseconds;
            
            TelemetryClient::getInstance().trackMetric(
                strFmt("MethodDuration.%1.%2", _className, _methodName),
                durationMs,
                new Map(Types::String, Types::AnyType).fromArray([
                    ["class", _className],
                    ["method", _methodName],
                    ["success", success]
                ])
            );
            
            // Alert if slow
            if (durationMs > 5000) // 5 seconds
            {
                TelemetryClient::getInstance().trackEvent(
                    "SlowMethodDetected",
                    new Map(Types::String, Types::AnyType).fromArray([
                        ["class", _className],
                        ["method", _methodName],
                        ["durationMs", durationMs]
                    ])
                );
            }
        }
    }
}

// Usage in any class:
public void myBusinessMethod()
{
    MethodTimer::timeMethod(className(this), "myBusinessMethod", delegate void() {
        // Original method body
        this.doWork();
    });
}
```

### 3.2 SQL Query Tracking

```xpp
/// <summary>
/// Track all SQL queries (wrap select statements)
/// </summary>
class SqlTracker
{
    public static void trackQuery(str _queryType, str _tableName, 
                                  delegate Common _query())
    {
        UTCDateTime start = DateTimeUtil::utcNow();
        Common result;
        int recordCount = 0;
        ;
        
        try
        {
            result = _query();
            
            // Count records if it's a query result
            if (result)
            {
                // For while select, count iterations
                // This is simplified - real implementation would wrap QueryRun
            }
        }
        catch
        {
            throw;
        }
        finally
        {
            TimeSpan duration = DateTimeUtil::utcNow() - start;
            
            TelemetryClient::getInstance().trackDependency(
                strFmt("SQL.%1", _queryType),
                _tableName,
                start,
                duration,
                true,
                "200",
                "Azure SQL Database"
            );
            
            // Track slow queries
            if (duration.TotalMilliseconds > 1000)
            {
                TelemetryClient::getInstance().trackEvent("SlowQuery", 
                    new Map(Types::String, Types::AnyType).fromArray([
                        ["queryType", _queryType],
                        ["table", _tableName],
                        ["durationMs", duration.TotalMilliseconds]
                    ]));
            }
        }
    }
}

// Usage:
SqlTracker::trackQuery("Select", "CustTable", delegate Common() {
    select firstOnly custTable where custTable.AccountNum == "CUST-001";
    return custTable;
});
```

### 3.3 Batch Job Instrumentation

```xpp
/// <summary>
/// Base class for instrumented batch jobs
/// </summary>
abstract class InstrumentedBatchJob extends SysOperationServiceBase
{
    protected str telemetryOperationName;
    
    protected void new()
    {
        super();
        this.telemetryOperationName = className(this);
    }
    
    public void run()
    {
        UTCDateTime start = DateTimeUtil::utcNow();
        boolean success = true;
        str errorMessage = "";
        int recordsProcessed = 0;
        ;
        
        TelemetryClient::getInstance().trackEvent("BatchJobStarted",
            new Map(Types::String, Types::AnyType).fromArray([
                ["jobName", this.telemetryOperationName]
            ]));
        
        try
        {
            recordsProcessed = this.executeBatch();
            success = true;
        }
        catch (Exception::Error)
        {
            success = false;
            errorMessage = "Batch execution failed";
            throw;
        }
        finally
        {
            TimeSpan duration = DateTimeUtil::utcNow() - start;
            
            TelemetryClient::getInstance().trackMetric("BatchJob.Duration",
                duration.TotalMilliseconds,
                new Map(Types::String, Types::AnyType).fromArray([
                    ["jobName", this.telemetryOperationName],
                    ["success", success]
                ]));
            
            TelemetryClient::getInstance().trackMetric("BatchJob.RecordsProcessed",
                recordsProcessed,
                new Map(Types::String, Types::AnyType).fromArray([
                    ["jobName", this.telemetryOperationName]
                ]));
            
            TelemetryClient::getInstance().trackEvent("BatchJobCompleted",
                new Map(Types::String, Types::AnyType).fromArray([
                    ["jobName", this.telemetryOperationName],
                    ["durationMs", duration.TotalMilliseconds],
                    ["recordsProcessed", recordsProcessed],
                    ["success", success],
                    ["errorMessage", errorMessage]
                ]));
        }
    }
    
    abstract int executeBatch();
}
```

### 3.4 Form Load Tracking

```xpp
/// <summary>
/// Form extension to track load performance
/// </summary>
[ExtensionOf(formStr(CustTable))]
final class CustTable_FormTelemetry_Ext
{
    UTCDateTime formInitStart;
    
    public void init()
    {
        this.formInitStart = DateTimeUtil::utcNow();
        next init();
    }
    
    public void run()
    {
        next run();
        
        TimeSpan duration = DateTimeUtil::utcNow() - this.formInitStart;
        
        TelemetryClient::getInstance().trackRequest(
            "FormLoad.CustTable",
            this.formInitStart,
            duration,
            "200",
            true
        );
        
        // Track form-specific metrics
        TelemetryClient::getInstance().trackMetric("FormLoad.DataSourcesCount",
            this.dataSourceCount(),
            new Map(Types::String, Types::AnyType).fromArray([
                ["form", "CustTable"]
            ]));
    }
}
```

---

## 4. Performance Counters & System Metrics

### 4.1 Key Metrics to Collect

| Category | Metric | Source | Alert Threshold |
|----------|--------|--------|-----------------|
| **AOS** | Request Duration (p50, p95, p99) | App Insights | p99 > 5s |
| **AOS** | Request Rate (req/sec) | App Insights | Drop > 50% |
| **AOS** | Error Rate | App Insights | > 1% |
| **AOS** | Active Sessions | Perf Counter | > 80% license limit |
| **SQL** | DTU Utilization | Azure Monitor | > 80% sustained |
| **SQL** | Query Duration (p95) | Query Store | > 2s |
| **SQL** | Deadlocks/sec | Perf Counter | > 0 |
| **SQL** | Cache Hit Ratio | Perf Counter | < 90% |
| **Batch** | Job Duration | Custom | > SLA |
| **Batch** | Failure Rate | Custom | > 5% |
| **Batch** | Queue Depth | Custom | > 1000 |
| **Cache** | Hit Ratio | App Insights | < 80% |
| **Cache** | Eviction Rate | App Insights | Increasing |
| **Integration** | OData Latency | App Insights | p95 > 3s |
| **Integration** | Message Queue Lag | Service Bus | > 1000 messages |

### 4.2 Collecting AOS Performance Counters

```xpp
/// <summary>
/// Collect and send AOS performance counters
/// </summary>
class AosPerformanceCollector
{
    public static void collectAndSend()
    {
        // These require .NET interop to read Windows Performance Counters
        // Run as a scheduled batch job every 1-5 minutes
        
        Map counters = new Map(Types::String, Types::Real);
        
        // Using System.Diagnostics.PerformanceCounter
        using System.Diagnostics;
        
        PerformanceCounter cpuCounter = new PerformanceCounter("Process", "% Processor Time", "Ax32Serv");
        PerformanceCounter memCounter = new PerformanceCounter("Process", "Working Set - Private Bytes", "Ax32Serv");
        PerformanceCounter threadCounter = new PerformanceCounter("Process", "Thread Count", "Ax32Serv");
        PerformanceCounter handleCounter = new PerformanceCounter("Process", "Handle Count", "Ax32Serv");
        
        counters.insert("AOS.CPU.Percent", cpuCounter.NextValue());
        counters.insert("AOS.Memory.PrivateBytes", memCounter.NextValue() / (1024*1024)); // MB
        counters.insert("AOS.Threads", threadCounter.NextValue());
        counters.insert("AOS.Handles", handleCounter.NextValue());
        
        // Send to App Insights
        MapEnumerator enum = counters.getEnumerator();
        while (enum.moveNext())
        {
            TelemetryClient::getInstance().trackMetric(enum.currentKey(), enum.currentValue());
        }
    }
}
```

---

## 5. Alerting Rules

### 5.1 Azure Monitor Alert Rules (ARM Template)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "appInsightsName": { "type": "string" },
    "actionGroupId": { "type": "string" }
  },
  "resources": [
    {
      "type": "Microsoft.Insights/metricAlerts",
      "apiVersion": "2018-03-01",
      "name": "D365FO-HighErrorRate",
      "properties": {
        "description": "Alert when error rate exceeds 1%",
        "severity": 2,
        "enabled": true,
        "scopes": ["[resourceId('Microsoft.Insights/components', parameters('appInsightsName'))]"],
        "evaluationFrequency": "PT1M",
        "windowSize": "PT5M",
        "criteria": {
          "odata.type": "Microsoft.Azure.Monitor.MetricCriteria",
          "metricName": "exceptions/count",
          "metricNamespace": "Microsoft.Insights/components",
          "operator": "GreaterThan",
          "threshold": 10,
          "timeAggregation": "Count",
          "dimensions": [
            { "name": "cloud_RoleName", "operator": "Include", "values": ["D365FO-AOS"] }
          ]
        },
        "actions": [
          { "actionGroupId": "[parameters('actionGroupId')]" }
        ]
      }
    },
    {
      "type": "Microsoft.Insights/metricAlerts",
      "apiVersion": "2018-03-01",
      "name": "D365FO-HighResponseTime",
      "properties": {
        "description": "Alert when p95 response time exceeds 5 seconds",
        "severity": 2,
        "enabled": true,
        "scopes": ["[resourceId('Microsoft.Insights/components', parameters('appInsightsName'))]"],
        "evaluationFrequency": "PT1M",
        "windowSize": "PT5M",
        "criteria": {
          "odata.type": "Microsoft.Azure.Monitor.MetricCriteria",
          "metricName": "requests/duration",
          "metricNamespace": "Microsoft.Insights/components",
          "operator": "GreaterThan",
          "threshold": 5000,
          "timeAggregation": "Percentile95",
          "dimensions": [
            { "name": "cloud_RoleName", "operator": "Include", "values": ["D365FO-AOS"] }
          ]
        },
        "actions": [
          { "actionGroupId": "[parameters('actionGroupId')]" }
        ]
      }
    },
    {
      "type": "Microsoft.Insights/metricAlerts",
      "apiVersion": "2018-03-01",
      "name": "D365FO-SQL-HighDTU",
      "properties": {
        "description": "SQL DTU utilization above 80%",
        "severity": 3,
        "enabled": true,
        "scopes": ["[resourceId('Microsoft.Sql/servers/databases', 'd365fo-sql', 'd365fo-db')]"],
        "evaluationFrequency": "PT5M",
        "windowSize": "PT15M",
        "criteria": {
          "odata.type": "Microsoft.Azure.Monitor.MetricCriteria",
          "metricName": "dtu_consumption_percent",
          "operator": "GreaterThan",
          "threshold": 80,
          "timeAggregation": "Average"
        },
        "actions": [
          { "actionGroupId": "[parameters('actionGroupId')]" }
        ]
      }
    }
  ]
}
```

### 5.2 Custom Log-Based Alerts

```kusto
// KQL queries for Log Analytics alerts

// 1. Slow form loads
requests
| where cloud_RoleName == "D365FO-AOS"
| where name startswith "FormLoad."
| where duration > 10000 // 10 seconds
| summarize count() by name, bin(timestamp, 5m)
| where count_ > 5
| project timestamp, name, count_

// 2. Batch job failures
customEvents
| where name == "BatchJobCompleted"
| where customDimensions.success == "False"
| summarize count() by tostring(customDimensions.jobName), bin(timestamp, 15m)
| where count_ > 0

// 3. Deadlock detection
customEvents
| where name == "DeadlockDetected"
| summarize count() by bin(timestamp, 5m)
| where count_ > 0

// 4. Number sequence exhaustion
customEvents
| where name == "NumberSequenceLow"
| summarize count() by tostring(customDimensions.sequenceName), bin(timestamp, 1h)

// 5. Integration failures
customEvents
| where name == "IntegrationError"
| summarize count() by tostring(customDimensions.integrationName), bin(timestamp, 5m)
| where count_ > 10
```

---

## 6. Distributed Tracing

### 6.1 Correlation ID Propagation

```xpp
/// <summary>
/// Correlation context for distributed tracing
/// </summary>
class SysCorrelationContext
{
    private static ThreadLocal correlationId;
    private static ThreadLocal parentCorrelationId;
    
    public static str getCurrentCorrelationId()
    {
        if (!correlationId)
        {
            correlationId = new ThreadLocal();
            correlationId.Value = System.Guid::NewGuid().ToString();
        }
        return correlationId.Value;
    }
    
    public static void setCurrentCorrelationId(str _id)
    {
        if (!correlationId) correlationId = new ThreadLocal();
        correlationId.Value = _id;
    }
    
    public static str getCurrentParentCorrelationId()
    {
        return parentCorrelationId.Value;
    }
    
    public static void setParentCorrelationId(str _id)
    {
        if (!parentCorrelationId) parentCorrelationId = new ThreadLocal();
        parentCorrelationId.Value = _id;
    }
    
    public static void clear()
    {
        correlationId.Value = "";
        parentCorrelationId.Value = "";
    }
}

/// <summary>
/// HTTP Client with correlation headers
/// </summary>
class TracedHttpClient
{
    public static System.Net.Http.HttpResponseMessage sendRequest(
        str _url, 
        str _method, 
        str _content = "")
    {
        using System.Net.Http;
        
        HttpClient client = new HttpClient();
        HttpRequestMessage request = new HttpRequestMessage(
            _method == "POST" ? HttpMethod::Post : HttpMethod::Get,
            _url
        );
        
        // Add correlation headers
        request.Headers.Add("X-Correlation-ID", SysCorrelationContext::getCurrentCorrelationId());
        request.Headers.Add("X-Parent-Correlation-ID", SysCorrelationContext::getCurrentParentCorrelationId());
        
        if (_content)
        {
            request.Content = new StringContent(_content, System.Text.Encoding::UTF8, "application/json");
        }
        
        UTCDateTime start = DateTimeUtil::utcNow();
        HttpResponseMessage response = client.SendAsync(request).Result;
        TimeSpan duration = DateTimeUtil::utcNow() - start;
        
        // Track dependency
        TelemetryClient::getInstance().trackDependency(
            "HTTP." + _method,
            _url,
            start,
            duration,
            response.IsSuccessStatusCode,
            response.StatusCode.ToString(),
            new System.Uri(_url).Host
        );
        
        return response;
    }
}
```

---

## 7. Dashboards & Workbooks

### 7.1 Azure Monitor Workbook (JSON)

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": 1,
      "content": {
        "json": "# D365 F&O Production Dashboard\n\n**Environment:** Production | **Last Updated:** {{now()}}"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "requests\n| where cloud_RoleName == \"D365FO-AOS\"\n| summarize Requests = count(), AvgDuration = avg(duration), P95Duration = percentile(duration, 95), ErrorRate = sum(toint(success == false)) * 100.0 / count()\n| by bin(timestamp, 5m)\n| render timechart",
        "title": "Request Volume & Latency (5m)",
        "visualization": "area"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "customEvents\n| where name == \"BatchJobCompleted\"\n| summarize Total = count(), Success = sum(toint(customDimensions.success == \"True\")), Failed = sum(toint(customDimensions.success == \"False\"))\n| by tostring(customDimensions.jobName), bin(timestamp, 1h)\n| render barchart",
        "title": "Batch Job Success/Failure Rate (1h)",
        "visualization": "bar"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "dependencies\n| where cloud_RoleName == \"D365FO-AOS\"\n| where type == \"SQL\"\n| summarize Calls = count(), AvgDuration = avg(duration), P95Duration = percentile(duration, 95), Failures = sum(toint(success == false))\n| by target, bin(timestamp, 5m)\n| top 20 by Calls desc\n| render table",
        "title": "Top SQL Dependencies (5m)",
        "visualization": "table"
      }
    },
    {
      "type": 3,
      "content": {
        "version": "KqlItem/1.0",
        "query": "customEvents\n| where name == \"SlowQuery\"\n| summarize count() by tostring(customDimensions.table), tostring(customDimensions.queryType), bin(timestamp, 1h)\n| render timechart",
        "title": "Slow Queries by Table (1h)",
        "visualization": "timechart"
      }
    }
  ]
}
```

---

## 8. Debugging with Live Metrics

### 8.1 Enable Live Metrics Stream

```xpp
/// <summary>
/// Configure live metrics for real-time debugging
/// </summary>
class LiveMetricsConfig
{
    public static void enableLiveMetrics()
    {
        // In TelemetryClient constructor, add:
        /*
        Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration config = 
            Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration::CreateDefault();
        
        // Enable live metrics
        config.TelemetryChannel = new Microsoft.ApplicationInsights.Channel.InMemoryChannel();
        config.TelemetryChannel.DeveloperMode = true;
        
        // Add live metrics processor
        var liveMetrics = new Microsoft.ApplicationInsights.Extensibility.PerfCounterCollector.QuickPulse.QuickPulseTelemetryProcessor();
        config.TelemetryProcessors.Add(liveMetrics);
        */
    }
}
```

---

## 9. Cost Optimization

### 9.1 Sampling Configuration

```xpp
/// <summary>
/// Configure adaptive sampling to control costs
/// </summary>
class SamplingConfig
{
    public static void configureSampling()
    {
        /*
        // In TelemetryClient constructor:
        Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration config = 
            Microsoft.ApplicationInsights.Extensibility.TelemetryConfiguration::CreateDefault();
        
        // Adaptive sampling (keeps 1 in N events, preserves metrics accuracy)
        var sampling = new Microsoft.ApplicationInsights.WindowsServer.TelemetryChannel.AdaptiveSamplingTelemetryProcessor();
        sampling.IncludedTypes = "Request;Dependency;Event;Metric";
        sampling.ExcludedTypes = "Exception"; // Never sample exceptions
        sampling.MaxTelemetryItemsPerSecond = 1000;
        config.TelemetryProcessors.Add(sampling);
        
        // Fixed rate sampling for high-volume events
        var fixedSampling = new Microsoft.ApplicationInsights.Extensibility.SamplingPercentageEstimatorSettings();
        fixedSampling.SamplingPercentage = 10; // 10% of events
        */
    }
}
```

### 9.2 Data Retention Policy

```bash
# Set retention via Azure CLI
az monitor app-insights component update \
  --app d365fo-prod-insights \
  --resource-group d365fo-monitoring \
  --retention-time 90  # days (default 90, max 730)

# Archive to storage account for long-term retention
az monitor app-insights component continue-export \
  --app d365fo-prod-insights \
  --resource-group d365fo-monitoring \
  --storage-account d365foarchive \
  --container insights-logs \
  --record-types Requests Dependencies Exceptions Events Metrics
```

---

## 10. Microsoft Resources

- **Application Insights**: https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview
- **D365 F&O Monitoring**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/perf-test/performance-testing
- **Azure Monitor Alerts**: https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview
- **Distributed Tracing**: https://learn.microsoft.com/en-us/azure/azure-monitor/app/distributed-tracing
- **KQL Reference**: https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/

---

## 11. Quick Start Checklist

- [ ] Create Application Insights resource
- [ ] Store instrumentation key in Key Vault
- [ ] Implement TelemetryClient wrapper
- [ ] Instrument critical paths (batch, forms, services)
- [ ] Add SQL query tracking
- [ ] Configure custom metrics for business KPIs
- [ ] Set up alert rules (error rate, latency, DTU, batch failures)
- [ ] Create dashboard workbook
- [ ] Enable live metrics for debugging
- [ ] Configure sampling for cost control
- [ ] Set up log analytics workspace for KQL queries
- [ ] Document runbooks for common alerts

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*