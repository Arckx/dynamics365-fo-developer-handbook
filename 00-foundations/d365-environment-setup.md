---
name: d365-environment-setup
description: Step-by-step Tier-1 VM provisioning, VS + D365 extension install, first project, Git setup
metadata:
  type: reference
  last-verified: 2026-11-22
---

# D365 F&O Environment Setup Guide

> **Follow this BEFORE Chapter 1** to get your development environment ready. Estimated time: 2-4 hours.

---

## 1. Prerequisites Checklist

| Requirement | Minimum | Recommended | Verify |
|-------------|---------|-------------|--------|
| **Azure Subscription** | Pay-as-you-go | Enterprise Agreement | `az account show` |
| **LCS Access** | Project Owner | Project Owner | lcs.dynamics.com |
| **Visual Studio** | 2022 Community | 2022 Enterprise | VS Installer |
| **Windows** | 10/11 Pro | 11 Pro | `winver` |
| **RAM** | 16 GB | 32 GB+ | Task Manager |
| **Disk** | 128 GB free | 256 GB+ SSD | Explorer |
| **Admin Rights** | Local admin | Domain admin | Required for VS |

---

## 2. Get a Tier-1 Development VM

### Option A: LCS Cloud-Hosted (Recommended)

1. **Login to LCS** → https://lcs.dynamics.com
2. **Select your project** (or create one)
3. **Go to "Environments"** → **Add**
4. **Choose:**
   - **Topology:** Development (Tier-1)
   - **Version:** Latest 10.0.x (e.g., 10.0.40)
   - **Size:** D13 v2 (8 vCPU, 56 GB RAM) or D14 v2 (16 vCPU, 112 GB)
5. **Deploy** — takes 30-60 minutes
6. **RDP** to VM when ready (credentials in LCS)

### Option B: Local VM (Advanced)

> Only if you have Windows Server 2019/2022 license and 64+ GB RAM

1. **Download VHD** from LCS → Shared Asset Library → "D365 F&O Development VM"
2. **Create Hyper-V VM** (Gen 2, 64 GB RAM, 256 GB dynamic disk)
3. **Run setup scripts** — complex, not recommended for beginners

---

## 3. Visual Studio 2022 Installation

### 3.1 Install VS 2022

```bash
# Option 1: Visual Studio Installer (GUI)
# Download from: https://visualstudio.microsoft.com/downloads/
# Choose: Community (free) or Professional/Enterprise

# Option 2: Command line (for automation)
winget install Microsoft.VisualStudio.2022.Community
```

### 3.2 Required Workloads

In **Visual Studio Installer** → **Modify** → **Workloads** tab:

| Workload | Required? |
|----------|-----------|
| **.NET desktop development** | ✅ Yes |
| **ASP.NET and web development** | ✅ Yes |
| **Azure development** | ✅ Yes |
| **Data storage and processing** | ✅ Yes |
| **Universal Windows Platform** | ❌ No |

### 3.3 Individual Components (Verify These Are Checked)

| Component | Why |
|-----------|-----|
| **.NET 6.0/7.0/8.0 Runtime** | X++ compiles to .NET |
| **NuGet Package Manager** | Packages |
| **Git for Windows** | Source control |
| **Azure CLI** | LCS automation |
| **PowerShell 7+** | Scripts |

---

## 4. Dynamics 365 Development Tools

### 4.1 Install via VS Marketplace

1. **Open VS 2022** → **Extensions** → **Manage Extensions**
2. **Search:** "Dynamics 365"
3. **Install:**
   - **Dynamics 365 Development Tools** (Microsoft)
   - **Dynamics 365 Unified Operations Tools** (if separate)
4. **Restart VS** when prompted

### 4.2 Verify Installation

1. **File** → **New** → **Project**
2. **Search:** "Dynamics 365"
3. **Should see:**
   - Dynamics 365 Package
   - Dynamics 365 Project
   - Dynamics 365 Model

---

## 5. Connect VS to Tier-1 VM

### 5.1 Get Connection Info from LCS

In LCS → Environment → **Details**:
- **VM Name:** `usnconeboxabc123`
- **Admin User:** `Admin`
- **Password:** (shown once, save it!)
- **URL:** `https://usnconeboxabc123.cloud.dynamics.com`

### 5.2 Configure VS Connection

1. **VS** → **Dynamics 365** → **Options**
2. **Add New Connection:**
   - **Name:** `My Tier-1`
   - **Server:** `usnconeboxabc123.cloud.dynamics.com` (or IP)
   - **Authentication:** Windows (if domain) or Basic
   - **User:** `Admin`
   - **Password:** (from LCS)
3. **Test Connection** → Should succeed
4. **Set as Default**

### 5.3 Synchronize Metadata

1. **Dynamics 365** → **Model Management** → **Refresh Models**
2. Wait for "Refresh completed"
3. **Dynamics 365** → **Model Management** → **Synchronize Database**
   - **Wait 10-20 minutes** — this creates SQL tables from AOT!

---

## 6. Create Your First Model & Project

### 6.1 Create a Model

1. **Dynamics 365** → **Model Management** → **Create Model**
2. **Fill in:**
   - **Model Name:** `MyFirstModel`
   - **Model Publisher:** `MyCompany`
   - **Version:** `1.0.0`
   - **Layer:** `CUS` (Customer layer)
   - **Description:** `My first D365 F&O model`
3. **Create** → Wait for completion

### 6.2 Create a Project

1. **File** → **New** → **Project**
2. **Search:** "Dynamics 365 Project"
3. **Name:** `MyFirstProject`
4. **Location:** `C:\Source\MyFirstProject`
5. **Solution:** Create new solution
6. **Add to Source Control:** ✅ Git

### 6.3 Add Elements to Project

1. **Right-click Project** → **Add** → **New Item**
2. **Try each type:**
   - **Runnable Class (Job)** → `MyFirstJob`
   - **Table** → `MyTable`
   - **Form** → `MyForm`
   - **Class** → `MyClass`

---

## 7. Write & Run Your First X++ Job

### 7.1 Create a Job

```xpp
// MyFirstJob
internal final class MyFirstJob
{
    public static void main(Args _args)
    {
        // Select customers
        CustTable cust;
        int count = 0;
        
        while select cust
            where cust.CustGroup == '10'
        {
            count++;
            info(strFmt("%1: %2 (%3)", count, cust.AccountNum, cust.Name));
        }
        
        info(strFmt("Total customers in group 10: %1", count));
    }
}
```

### 7.2 Run It

1. **Right-click `MyFirstJob`** in Solution Explorer
2. **Set as Startup Object**
3. **Press F5** (or **Debug** → **Start Debugging**)
4. **Watch Output Window** and **Infolog** (View → Infolog)

### 7.3 Debug It

1. **Set breakpoint** (F9) on `info(...)` line
2. **F5** → Execution pauses
3. **Hover variables** to see values
4. **F10** (Step Over), **F11** (Step Into)
5. **Debug** → **Windows** → **Watch** / **Locals** / **Call Stack**

---

## 8. Git Setup

### 8.1 Initialize Repository

```bash
# In your project folder (C:\Source\MyFirstProject)
git init

# Create .gitignore for D365
cat > .gitignore << 'EOF'
# D365 F&O
*.axmodel
*.dll
*.pdb
bin/
obj/
*.user
*.suo
.vs/
*.log
*.cache
Descriptor/ModuleDescriptor.xml  # Generated
*.xml~
EOF

# First commit
git add .
git commit -m "Initial commit: MyFirstModel project structure"
```

### 8.2 Connect to Azure DevOps / GitHub

```bash
# Azure DevOps
git remote add origin https://dev.azure.com/{org}/{project}/_git/{repo}

# GitHub
git remote add origin https://github.com/{user}/{repo}.git

# Push
git push -u origin main
```

### 8.3 Branch Strategy

```
main (protected)
  ├── release/10.0.40
  ├── feature/add-customer-validation
  ├── bugfix/credit-limit-calculation
  └── hotfix/prod-deadlock-issue
```

---

## 9. Essential VS Settings

### 9.1 X++ Editor Settings

**Tools** → **Options** → **Text Editor** → **X++**:

| Setting | Value |
|---------|-------|
| **Tab size** | 4 |
| **Indent** | Spaces |
| **Line numbers** | ✅ On |
| **Word wrap** | ✅ On |
| **Show whitespace** | ✅ On |

### 9.2 Build Settings

**Tools** → **Options** → **Projects and Solutions** → **Build and Run**:

| Setting | Value |
|---------|-------|
| **Maximum parallel builds** | 4 (or CPU cores) |
| **Build log verbosity** | Normal |
| **Always show Error List** | ✅ On |

### 9.3 Debugging Settings

**Tools** → **Options** → **Debugging** → **General**:

| Setting | Value |
|---------|-------|
| **Enable Just My Code** | ❌ Off (debug standard code too) |
| **Show disassembly** | ✅ On |
| **Break all processes on breakpoint** | ✅ On |

---

## 10. Useful Extensions (Optional but Recommended)

| Extension | Purpose |
|-----------|---------|
| **GitLens** | Git blame, history inline |
| **Markdown All in One** | Edit README.md, docs |
| **SQL Server (mssql)** | Query Azure SQL directly |
| **Azure Account** | Manage Azure resources in VS |
| **REST Client** | Test OData endpoints (.http files) |

---

## 11. Verification Checklist

Before moving to Chapter 1, verify:

- [ ] **Tier-1 VM** accessible via RDP
- [ ] **VS 2022** with D365 tools installed
- [ ] **VS connected** to Tier-1 (Test Connection passes)
- [ ] **Database synchronized** (no "table not found" errors)
- [ ] **Model created** in CUS layer
- [ ] **Project created** and added to Git
- [ ] **First job runs** and shows Infolog output
- [ ] **Breakpoints work** in debugger
- [ ] **Git remote** configured and push works

---

## 12. Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| **"Cannot connect to server"** | Check VPN, firewall, VM running in LCS |
| **"Model not found"** | Refresh Models (Dynamics 365 → Model Management) |
| **"Table doesn't exist"** | Synchronize Database (takes 10-20 min) |
| **"Access denied"** | Run VS as Administrator |
| **"Build fails: metadata"** | Clean (Build → Clean), Rebuild |
| **"Debug doesn't hit breakpoint"** | Check "Enable Just My Code" = Off |
| **"Infolog not showing"** | View → Infolog, or Ctrl+Alt+I |

---

## 13. Next Steps

1. **Complete Exercise 1** → `d365-xpp-exercises.md` → Exercise 1
2. **Read Chapter 1** → `d365-learning-guide.md` → Chapter 1
3. **Bookmark these URLs:**
   - X++ Reference: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-programming-language
   - Tables: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/tables/tables
   - Best Practices: https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-best-practices

---

## 14. Cost Management (Important!)

| Resource | Cost | Management |
|----------|------|------------|
| **Tier-1 VM** | ~$2-4/hour (D13/D14) | **Deallocate when not coding!** |
| **Azure SQL** | Included in VM | Auto-pauses after 1hr idle |
| **LCS** | Free | No cost |
| **VS Community** | Free | Individual use |

**Set up Auto-Shutdown in Azure Portal:**
1. Go to VM resource
2. **Operations** → **Auto-shutdown**
3. **Enable** → 6:00 PM (or your end of day)
4. **Notification email** → Your email

---

*Last verified: 2026-11-22 | Part of 35-Chapter Handbook*