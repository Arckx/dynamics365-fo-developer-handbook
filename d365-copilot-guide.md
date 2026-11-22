---
name: d365-copilot-guide
description: D365 F&O Copilot extensibility — plugins, actions, prompt engineering, custom skills
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Copilot Extensibility Guide

> **Target audience:** Developers extending Copilot in D365 F&O. Requires Power Platform environment with Copilot Studio access.

---

## 1. Copilot Architecture in D365 F&O

```
┌─────────────────────────────────────────────────────────────────┐
│                      COPILOT ORCHESTRATOR                        │
│  (Natural Language → Intent → Action Planning → Execution)      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  PLUGINS    │ │  ACTIONS    │ │   SKILLS    │
       │ (Read-only) │ │ (Write/Exec)│ │ (Multi-step)│
       └─────────────┘ └─────────────┘ └─────────────┘
              │               │               │
              ▼               ▼               ▼
       ┌─────────────────────────────────────────┐
       │      DATVERSE / D365 F&O BACKEND        │
       │  Tables, Data Entities, Custom APIs,    │
       │  SysOperation, Power Automate Flows     │
       └─────────────────────────────────────────┘
```

### 1.1 Extension Points

| Extension Type | Capability | Use Case | Deployment |
|----------------|------------|----------|------------|
| **Plugin** | Read data, answer questions | "Show me open orders for Contoso" | Copilot Studio |
| **Action** | Execute write operations | "Create a purchase order for item X" | Copilot Studio + Power Automate |
| **Skill** | Multi-step orchestration | "Reconcile this bank statement" | Copilot Studio + Custom API |
| **Prompt** | Guide LLM behavior | Domain-specific instructions | Copilot Studio |

---

## 2. Building a Copilot Plugin (Read-Only)

### 2.1 Plugin Manifest (JSON)

```json
{
  "schema_version": "v1",
  "name_for_human": "D365 F&O Customer Insights",
  "name_for_model": "d365_customer_insights",
  "description_for_human": "Query customer data, orders, and credit status from D365 F&O",
  "description_for_model": "Use this plugin to retrieve customer information from Dynamics 365 Finance & Operations. Supports querying by account number, name, or credit status. Returns customer details, open orders, and credit limits.",
  "auth": {
    "type": "oauth",
    "client_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
    "token_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
    "scope": "https://api.businesscentral.dynamics.com/.default"
  },
  "api": {
    "type": "openapi",
    "url": "https://your-env.operations.dynamics.com/data/$metadata",
    "has_user_authentication": true
  },
  "logo_url": "https://your-cdn.com/d365-logo.png",
  "contact_email": "dev@yourcompany.com",
  "legal_info_url": "https://yourcompany.com/legal"
}
```

### 2.2 Custom API for Plugin (Preferred over raw OData)

```csharp
// Custom API: GetCustomerInsights
// File: GetCustomerInsights.cs (C# in Custom API project)

[CustomAPI]
public class GetCustomerInsights : ICustomAPI
{
    public GetCustomerInsightsResponse Execute(GetCustomerInsightsRequest request)
    {
        var response = new GetCustomerInsightsResponse();
        
        using (var ctx = new DataEntitiesContext(request.EnvironmentUrl))
        {
            ctx.Credentials = new OAuthCredentials(request.AccessToken);
            
            var customer = ctx.CustCustomerV3Entities
                .Where(c => c.AccountNum == request.AccountNumber)
                .Select(c => new {
                    c.AccountNum,
                    c.Name,
                    c.CustGroup,
                    c.CreditLimit,
                    c.Currency,
                    c.PaymentTerms
                })
                .FirstOrDefault();

            if (customer == null)
            {
                response.Success = false;
                response.ErrorMessage = $"Customer {request.AccountNumber} not found";
                return response;
            }

            // Get open orders
            var openOrders = ctx.SalesOrderHeadersV2Entities
                .Where(o => o.CustAccount == request.AccountNumber 
                         && o.DocumentStatus == "OpenOrder")
                .Select(o => new {
                    o.SalesOrderNumber,
                    o.OrderDate,
                    o.SalesAmount,
                    o.DeliveryDate
                })
                .Take(10)
                .ToList();

            response.Customer = new CustomerInfo
            {
                AccountNumber = customer.AccountNum,
                Name = customer.Name,
                CustomerGroup = customer.CustGroup,
                CreditLimit = customer.CreditLimit,
                Currency = customer.Currency,
                PaymentTerms = customer.PaymentTerms,
                OpenOrdersCount = openOrders.Count,
                TotalOpenAmount = openOrders.Sum(o => o.SalesAmount)
            };
            response.Success = true;
        }
        
        return response;
    }
}

// Request/Response DTOs
public class GetCustomerInsightsRequest
{
    public string AccountNumber { get; set; }
    public string EnvironmentUrl { get; set; }
    public string AccessToken { get; set; }
}

public class GetCustomerInsightsResponse
{
    public bool Success { get; set; }
    public string ErrorMessage { get; set; }
    public CustomerInfo Customer { get; set; }
}

public class CustomerInfo
{
    public string AccountNumber { get; set; }
    public string Name { get; set; }
    public string CustomerGroup { get; set; }
    public decimal CreditLimit { get; set; }
    public string Currency { get; set; }
    public string PaymentTerms { get; set; }
    public int OpenOrdersCount { get; set; }
    public decimal TotalOpenAmount { get; set; }
}
```

### 2.3 Register Custom API in D365 F&O

```xpp
// X++: Register Custom API (run once via job)
static void RegisterCustomAPI(Args _args)
{
    CustomAPI customAPI;
    ;
    
    customAPI = CustomAPI::construct();
    customAPI.parmName("GetCustomerInsights");
    customAPI.parmDisplayName("Get Customer Insights");
    customAPI.parmDescription("Retrieves customer details and open orders");
    customAPI.parmPluginType(CustomAPIPluginType::CustomBusinessLogic);
    customAPI.parmBindingType(CustomAPIBindingType::Global);
    customAPI.parmExecuteMethod("GetCustomerInsights.execute");
    customAPI.parmAllowedCustomProcessingStepType(AllowedCustomProcessingStepType::SyncOnly);
    
    // Input parameters
    customAPI.addParameter("AccountNumber", "Customer Account Number", 
                           ExtendedTypeStr(CustAccount), true);
    customAPI.addParameter("EnvironmentUrl", "Environment URL", 
                           ExtendedTypeStr(Url), false);
    
    // Output parameters
    customAPI.addOutputParameter("Success", "Success Flag", 
                                 ExtendedTypeStr(NoYes));
    customAPI.addOutputParameter("Customer", "Customer Info", 
                                 ExtendedTypeStr(Json));
    
    customAPI.save();
    info("Custom API registered");
}
```

---

## 3. Building a Copilot Action (Write/Execute)

### 3.1 Action via Power Automate Flow

```
Trigger: Copilot Action (Manual trigger with inputs)
    │
    ├─ Input: PurchaseOrderRequest (JSON)
    │         { vendorAccount, items[], deliveryDate, ... }
    │
    ├─ Step 1: Validate Vendor (D365 F&O OData)
    │         GET /data/VendorsV2?$filter=AccountNum eq 'VEND-001'
    │
    ├─ Step 2: Validate Items (D365 F&O OData)
    │         GET /data/ProductsV2?$filter=ProductNumber in (...)
    │
    ├─ Step 3: Create Purchase Order (Custom API)
    │         POST /api/CreatePurchaseOrder
    │
    ├─ Step 4: Return Confirmation
    │         { poNumber, status, message }
    │
    └─ Output: PurchaseOrderResponse
```

### 3.2 Custom API for Action (Write Operation)

```csharp
// Custom API: CreatePurchaseOrder
[CustomAPI]
public class CreatePurchaseOrder : ICustomAPI
{
    public CreatePurchaseOrderResponse Execute(CreatePurchaseOrderRequest request)
    {
        var response = new CreatePurchaseOrderResponse();
        
        // Validate inputs
        if (request.VendorAccount == null || request.Items.Count == 0)
        {
            response.Success = false;
            response.ErrorMessage = "Vendor and items required";
            return response;
        }

        // Call SysOperation service (server-side)
        using (var client = new HttpClient())
        {
            client.BaseAddress = new Uri(request.EnvironmentUrl);
            client.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", request.AccessToken);

            var payload = new
            {
                _contract = new
                {
                    VendorAccount = request.VendorAccount,
                    Items = request.Items.Select(i => new
                    {
                        ItemId = i.ItemId,
                        Qty = i.Qty,
                        Price = i.Price,
                        DeliveryDate = i.DeliveryDate
                    }).ToArray()
                }
            };

            var json = JsonSerializer.Serialize(payload);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // Call custom service endpoint
            var result = client.PostAsync("/api/CreatePurchaseOrderService", content).Result;
            
            if (result.IsSuccessStatusCode)
            {
                var responseJson = result.Content.ReadAsStringAsync().Result;
                var poResult = JsonSerializer.Deserialize<PoCreationResult>(responseJson);
                
                response.Success = true;
                response.PurchaseOrderNumber = poResult.PurchaseOrderNumber;
                response.Message = $"PO {poResult.PurchaseOrderNumber} created successfully";
            }
            else
            {
                response.Success = false;
                response.ErrorMessage = $"Service error: {result.StatusCode}";
            }
        }

        return response;
    }
}
```

### 3.3 SysOperation Service (Server-Side)

```xpp
// Service: CreatePurchaseOrderService
class CreatePurchaseOrderService extends SysOperationServiceBase
{
    [DataMemberAttribute]
    PurchTableDataContract contract;

    public void run()
    {
        PurchTable purchTable;
        PurchLine purchLine;
        NumberSeq numberSeq;
        ;
        
        ttsBegin;
        try
        {
            // Create header
            purchTable.clear();
            purchTable.PurchId = NumberSeq::newGetNum(PurchParameters::numRefPurchId()).num();
            purchTable.OrderAccount = contract.VendorAccount;
            purchTable.PurchStatus = PurchStatus::Backorder;
            purchTable.DeliveryDate = contract.DeliveryDate;
            purchTable.insert();

            // Create lines
            foreach (PurchLineDataContract lineContract in contract.Items)
            {
                purchLine.clear();
                purchLine.PurchId = purchTable.PurchId;
                purchLine.ItemId = lineContract.ItemId;
                purchLine.PurchQty = lineContract.Qty;
                purchLine.PurchPrice = lineContract.Price;
                purchLine.DeliveryDate = lineContract.DeliveryDate;
                purchLine.insert();
            }

            // Store result for return
            this.parmResult(purchTable.PurchId);
            
            ttsCommit;
        }
        catch
        {
            ttsAbort;
            throw Exception::Error;
        }
    }
}

[DataContractAttribute]
class PurchTableDataContract
{
    VendAccount vendorAccount;
    List(PurchLineDataContract) items;
    Date deliveryDate;
    
    [DataMemberAttribute('VendorAccount')]
    public VendAccount parmVendorAccount(VendAccount _v = vendorAccount) { vendorAccount = _v; return vendorAccount; }
    
    [DataMemberAttribute('Items')]
    public List(PurchLineDataContract) parmItems(List(PurchLineDataContract) _i = items) { items = _i; return items; }
    
    [DataMemberAttribute('DeliveryDate')]
    public Date parmDeliveryDate(Date _d = deliveryDate) { deliveryDate = _d; return deliveryDate; }
}

[DataContractAttribute]
class PurchLineDataContract
{
    ItemId itemId;
    Qty qty;
    Price price;
    Date deliveryDate;
    // ... DataMember attributes
}
```

---

## 4. Building a Copilot Skill (Multi-Step Orchestration)

### 4.1 Skill Definition (YAML)

```yaml
# skill-bank-reconciliation.yaml
name: "BankReconciliationSkill"
description: "Reconcile bank statements with D365 F&O transactions"
version: "1.0"

inputs:
  - name: bankAccountId
    type: string
    description: "Bank account ID in D365 F&O"
    required: true
  - name: statementDate
    type: date
    description: "Statement date to reconcile"
    required: true
  - name: statementFile
    type: file
    description: "Bank statement file (CSV/MT940)"
    required: false

steps:
  - id: parseStatement
    type: "custom_api"
    api: "ParseBankStatement"
    inputs:
      file: "{{inputs.statementFile}}"
      format: "auto"
    outputs:
      transactions: "parsedTransactions"

  - id: fetchD365Transactions
    type: "custom_api"
    api: "GetBankTransactions"
    inputs:
      bankAccountId: "{{inputs.bankAccountId}}"
      fromDate: "{{subtract_days(inputs.statementDate, 30)}}"
      toDate: "{{inputs.statementDate}}"
    outputs:
      d365Transactions: "transactions"

  - id: matchTransactions
    type: "custom_api"
    api: "MatchBankTransactions"
    inputs:
      bankTransactions: "{{steps.parseStatement.outputs.transactions}}"
      d365Transactions: "{{steps.fetchD365Transactions.outputs.d365Transactions}}"
      tolerance: 0.01
    outputs:
      matches: "matched"
      unmatchedBank: "unmatchedBank"
      unmatchedD365: "unmatchedD365"

  - id: createReconciliation
    type: "custom_api"
    api: "CreateBankReconciliation"
    inputs:
      bankAccountId: "{{inputs.bankAccountId}}"
      statementDate: "{{inputs.statementDate}}"
      matches: "{{steps.matchTransactions.outputs.matches}}"
    outputs:
      reconciliationId: "reconciliationId"

  - id: reportResults
    type: "message"
    template: |
      Bank reconciliation completed for account {{inputs.bankAccountId}}.
      
      **Matched:** {{steps.matchTransactions.outputs.matches.length}} transactions
      **Unmatched (Bank):** {{steps.matchTransactions.outputs.unmatchedBank.length}}
      **Unmatched (D365):** {{steps.matchTransactions.outputs.unmatchedD365.length}}
      **Reconciliation ID:** {{steps.createReconciliation.outputs.reconciliationId}}
      
      {{#if steps.matchTransactions.outputs.unmatchedBank.length}}
      ⚠️ Review unmatched bank transactions manually.
      {{/if}}

outputs:
  - name: reconciliationId
    type: string
    source: "steps.createReconciliation.outputs.reconciliationId"
  - name: summary
    type: object
    source: "steps.reportResults"
```

### 4.2 Skill Registration in Copilot Studio

1. Open **Copilot Studio** → **Skills** → **New Skill**
2. Upload the YAML file
3. Configure **Custom API connections** for each step
4. Test with sample utterances:
   - "Reconcile bank account BK001 for January 15th"
   - "Match my bank statement for USMF checking account"

---

## 5. Prompt Engineering for D365 F&O

### 5.1 System Prompt Template

```
You are a Dynamics 365 Finance & Operations expert assistant. 
You help users navigate, query, and perform actions in D365 F&O.

CONTEXT:
- Environment: {{environment_name}} ({{environment_url}})
- Company: {{default_company}} ({{default_company_name}})
- User Role: {{user_security_roles}}
- Available Modules: {{enabled_modules}}

RULES:
1. Always use Data Entities (OData) for queries — never suggest direct SQL
2. For write operations, use Custom APIs or SysOperation services
3. Respect security roles — only suggest actions user can perform
4. Use D365 terminology: "Legal Entity" not "Company", "Data Entity" not "Table"
5. For batch jobs, suggest SysOperation framework
6. For reports, suggest SSRS or Electronic Reporting

EXAMPLES:
User: "Show me customer CUST-001"
→ Call GetCustomerInsights plugin with AccountNumber=CUST-001

User: "Create a purchase order for vendor VEND-001"
→ Call CreatePurchaseOrder action with vendor details

User: "Reconcile bank statement"
→ Invoke BankReconciliationSkill

ERROR HANDLING:
- If plugin fails, explain in business terms, not technical
- Suggest alternatives (e.g., "You can also check this in the All Customers form")
- Never expose stack traces or internal errors
```

### 5.2 Few-Shot Examples for Training

```json
{
  "examples": [
    {
      "user": "What's the credit limit for customer US-001?",
      "assistant": "I'll check the credit limit for customer US-001.",
      "tool_call": {
        "name": "d365_customer_insights",
        "arguments": { "AccountNumber": "US-001" }
      }
    },
    {
      "user": "Create a PO for vendor 1001 with item ITEM-001, qty 10",
      "assistant": "I'll create a purchase order for vendor 1001.",
      "tool_call": {
        "name": "create_purchase_order",
        "arguments": { 
          "vendorAccount": "1001",
          "items": [{ "itemId": "ITEM-001", "qty": 10, "price": 25.00 }]
        }
      }
    },
    {
      "user": "Why did the batch job fail?",
      "assistant": "Let me check the batch job history for failures.",
      "tool_call": {
        "name": "get_batch_job_history",
        "arguments": { "jobName": "SalesOrderProcessing" }
      }
    }
  ]
}
```

---

## 6. Deployment & Governance

### 6.1 ALM for Copilot Extensions

| Artifact | Source Control | Deployment |
|----------|----------------|------------|
| Plugin Manifest | JSON in `/copilot/plugins/` | Copilot Studio import |
| Custom APIs | C# project in `/src/CustomAPIs/` | NuGet package → D365 F&O |
| Power Automate Flows | `.msflow` in `/copilot/flows/` | Power Platform CLI (`pac`) |
| Skills | YAML in `/copilot/skills/` | Copilot Studio import |
| Prompts | Markdown in `/copilot/prompts/` | Copilot Studio configuration |

### 6.2 CI/CD Pipeline Snippet

```yaml
# Deploy Copilot extensions
- stage: DeployCopilot
  displayName: 'Deploy Copilot Extensions'
  jobs:
  - job: DeployPlugins
    steps:
    - task: PowerShell@2
      displayName: 'Import Plugin to Copilot Studio'
      inputs:
        targetType: 'inline'
        script: |
          # Use Power Platform CLI
          pac plugin import --path $(Build.SourcesDirectory)/copilot/plugins/d365_customer_insights.json --environment $(PowerPlatformEnvironmentId)

    - task: PowerShell@2
      displayName: 'Deploy Custom APIs'
      inputs:
        targetType: 'inline'
        script: |
          # Deploy via LCS or direct to environment
          # Custom APIs deployed as part of model package

    - task: PowerShell@2
      displayName: 'Deploy Power Automate Flows'
      inputs:
        targetType: 'inline'
        script: |
          pac solution import --path $(Build.SourcesDirectory)/copilot/flows/CopilotActions.zip --environment $(PowerPlatformEnvironmentId) --activate

    - task: PowerShell@2
      displayName: 'Import Skills'
      inputs:
        targetType: 'inline'
        script: |
          # Skills imported via Copilot Studio API
          # Requires manual step or custom automation
```

---

## 7. Testing Copilot Extensions

### 7.1 Unit Test for Custom API

```csharp
[TestClass]
public class GetCustomerInsightsTests
{
    [TestMethod]
    public void Execute_ValidCustomer_ReturnsCustomerInfo()
    {
        // Arrange
        var request = new GetCustomerInsightsRequest
        {
            AccountNumber = "CUST-001",
            EnvironmentUrl = "https://test.operations.dynamics.com",
            AccessToken = "mock-token"
        };
        
        var mockContext = new Mock<IDataEntitiesContext>();
        mockContext.Setup(c => c.CustCustomerV3Entities
            .Where(It.IsAny<Expression<Func<CustCustomerV3Entity, bool>>>())
            .Select(It.IsAny<Expression<Func<CustCustomerV3Entity, object>>>())
            .FirstOrDefault())
            .Returns(new CustCustomerV3Entity { AccountNum = "CUST-001", Name = "Test Customer", CreditLimit = 10000 });

        var api = new GetCustomerInsights(mockContext.Object);

        // Act
        var response = api.Execute(request);

        // Assert
        Assert.IsTrue(response.Success);
        Assert.AreEqual("CUST-001", response.Customer.AccountNumber);
        Assert.AreEqual("Test Customer", response.Customer.Name);
    }

    [TestMethod]
    public void Execute_InvalidCustomer_ReturnsError()
    {
        // Arrange
        var request = new GetCustomerInsightsRequest { AccountNumber = "INVALID" };
        var mockContext = new Mock<IDataEntitiesContext>();
        mockContext.Setup(c => c.CustCustomerV3Entities
            .Where(It.IsAny<Expression<Func<CustCustomerV3Entity, bool>>>())
            .FirstOrDefault())
            .Returns((CustCustomerV3Entity)null);

        var api = new GetCustomerInsights(mockContext.Object);

        // Act
        var response = api.Execute(request);

        // Assert
        Assert.IsFalse(response.Success);
        Assert.IsTrue(response.ErrorMessage.Contains("not found"));
    }
}
```

### 7.2 Integration Test (End-to-End)

```powershell
# Test script: Test-CopilotPlugin.ps1
param(
    [string]$EnvironmentUrl,
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$TenantId
)

# Get token
$token = Get-MsalToken -ClientId $ClientId -ClientSecret $ClientSecret -TenantId $TenantId -Scope "https://api.businesscentral.dynamics.com/.default"

# Test plugin via Copilot API
$pluginUrl = "$EnvironmentUrl/api/plugins/d365_customer_insights/execute"
$body = @{ AccountNumber = "CUST-001" } | ConvertTo-Json

$response = Invoke-RestMethod -Uri $pluginUrl -Method Post -Body $body -Headers @{ Authorization = "Bearer $token.AccessToken" } -ContentType "application/json"

if ($response.Success) {
    Write-Host "✅ Plugin test PASSED" -ForegroundColor Green
    Write-Host "Customer: $($response.Customer.Name)"
    Write-Host "Credit Limit: $($response.Customer.CreditLimit)"
} else {
    Write-Host "❌ Plugin test FAILED: $($response.ErrorMessage)" -ForegroundColor Red
    exit 1
}
```

---

## 8. Security & Compliance

| Concern | Mitigation |
|---------|------------|
| **Data Leakage** | Plugins respect D365 security roles; use XDS for row-level filtering |
| **Unauthorized Actions** | Actions require explicit user confirmation; audit logged |
| **PII Exposure** | Custom APIs should filter sensitive fields (SSN, bank details) |
| **Rate Limiting** | Implement circuit breaker; cache read-only plugin results |
| **Audit Trail** | All Copilot interactions logged in Dataverse audit log |

---

## 9. Microsoft Resources

- **Copilot Studio Docs**: https://learn.microsoft.com/en-us/microsoft-copilot-studio/
- **Custom APIs**: https://learn.microsoft.com/en-us/powerapps/developer/data-platform/custom-api
- **D365 F&O OData**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/odata
- **SysOperation Services**: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/sysoperation-framework
- **Power Platform ALM**: https://learn.microsoft.com/en-us/power-platform/alm/

---

## 10. Quick Start Checklist

- [ ] Provision Power Platform environment with Copilot Studio
- [ ] Create Custom API project (C#) for read/write operations
- [ ] Deploy Custom APIs to D365 F&O via model package
- [ ] Build Plugin manifest (JSON) for read-only queries
- [ ] Build Power Automate flows for write actions
- [ ] Define Skills (YAML) for multi-step processes
- [ ] Write system prompt with D365 F&O context
- [ ] Add few-shot examples for common utterances
- [ ] Configure CI/CD for all artifacts
- [ ] Test with real users; iterate on prompts

---

*Last verified: 2026-11-22 | Handbook: 35 Chapters*