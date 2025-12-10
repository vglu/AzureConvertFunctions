# Deployment Specification

## 1. Prerequisites

### 1.1 Development Environment

**Required Software**:
- Python 3.10 or higher (recommended 3.11, Python 3.9 reached EOL)
- Azure Functions Core Tools v4.x
- Git (for version control)
- Code editor (VS Code recommended)

**Optional**:
- Azure CLI
- Azure subscription
- VS Code with Azure Functions extension

### 1.2 Azure Resources

**Required**:
- Azure subscription
- Azure Function App (Consumption, Premium, or Dedicated plan)
- Storage account (for Function App)

**Optional**:
- Application Insights (for monitoring)
- Key Vault (for secrets management)

## 2. Local Development Setup

### 2.1 Initial Setup

**Step 1: Clone Repository**
```bash
git clone <repository-url>
cd AzureConvertFunctions
```

**Step 2: Install Python Dependencies**
```bash
# Install in system Python (Azure Functions uses system Python)
python -m pip install -r requirements.txt
```

**Step 3: Install Playwright Browsers**
```bash
playwright install chromium
```

**Step 4: Configure Local Settings**
```bash
# Copy example settings
cp local.settings.json.example local.settings.json

# Edit local.settings.json if needed
```

### 2.2 Running Locally

**Start Azure Functions Core Tools**:
```bash
func start
```

**Verify Functions**:
- Functions should be available at `http://localhost:7071/api`
- Swagger UI: `http://localhost:7071/api/swagger/ui`

**Test Endpoint**:
```bash
curl -X POST http://localhost:7071/api/csv2json \
  -H "Content-Type: text/csv" \
  -d "name,age\nJohn,25"
```

## 3. Production Deployment

### 3.1 Azure Function App Creation

**Using Azure CLI**:
```bash
# Create resource group
az group create --name rg-convert-functions --location eastus

# Create storage account
az storage account create \
  --name stconvertfuncs \
  --resource-group rg-convert-functions \
  --location eastus \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group rg-convert-functions \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-convert-app \
  --storage-account stconvertfuncs
```

**Using Azure Portal**:
1. Navigate to Azure Portal
2. Create Resource → Function App
3. Configure:
   - Runtime stack: Python
   - Version: 3.11 (recommended) or 3.10
   - Plan: Consumption
4. Create

### 3.2 Deployment Methods

#### Method 1: Azure Functions Core Tools

```bash
# Login to Azure
az login

# Deploy
func azure functionapp publish func-convert-app
```

#### Method 2: VS Code

1. Install Azure Functions extension
2. Sign in to Azure
3. Right-click function app folder
4. Select "Deploy to Function App"

#### Method 3: GitHub Actions

**Workflow File** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Azure Functions

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium
    
    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: func-convert-app
        package: '.'
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

#### Method 4: Azure DevOps

1. Create build pipeline
2. Add Python task
3. Install dependencies
4. Install Playwright browsers
5. Publish artifacts
6. Deploy to Function App

### 3.3 Post-Deployment Configuration

**Application Settings**:
```bash
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    FUNCTIONS_WORKER_RUNTIME=python \
    PYTHON_ENABLE_WORKER_EXTENSIONS=1
```

**Function App Settings**:
- Python version: 3.11 (recommended) or 3.10
- Always On: Disabled (Consumption plan)
- HTTP 2.0: Enabled
- Minimum TLS version: 1.2

## 4. Linux Deployment

### 4.1 System Dependencies

**Install Playwright Dependencies**:
```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

**Install Fonts**:
```bash
sudo apt-get install -y \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-liberation \
    fonts-noto-core
```

### 4.2 Custom Docker Image (Optional)

**Dockerfile**:
```dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy function code
COPY . /home/site/wwwroot
```

**Build and Deploy**:
```bash
# Build image
docker build -t func-convert-app .

# Tag for Azure Container Registry
docker tag func-convert-app <acr-name>.azurecr.io/func-convert-app:latest

# Push to ACR
docker push <acr-name>.azurecr.io/func-convert-app:latest

# Update Function App to use custom image
az functionapp config container set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --docker-custom-image-name <acr-name>.azurecr.io/func-convert-app:latest
```

## 5. Configuration Management

### 5.1 Environment Variables

**Development** (`local.settings.json`):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PYTHON_ENABLE_WORKER_EXTENSIONS": "1"
  }
}
```

**Production** (Azure Portal or CLI):
```bash
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    FUNCTIONS_WORKER_RUNTIME=python \
    PYTHON_ENABLE_WORKER_EXTENSIONS=1 \
    WEBSITE_TIME_ZONE=UTC
```

### 5.2 Connection Strings

**Storage Account Connection**:
- Automatically configured during Function App creation
- Stored in `AzureWebJobsStorage` setting

**Key Vault Integration** (Optional):
```bash
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    @Microsoft.KeyVault(SecretUri=https://<vault-name>.vault.azure.net/secrets/<secret-name>/)
```

## 6. Monitoring and Logging

### 6.1 Application Insights

**Enable Application Insights**:
```bash
az monitor app-insights component create \
  --app ai-convert-functions \
  --location eastus \
  --resource-group rg-convert-functions

az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY=<instrumentation-key>
```

**Metrics to Monitor**:
- Function execution count
- Function execution duration
- Error rate
- Memory usage
- HTTP response codes

### 6.2 Logging

**Log Levels**:
- Production: INFO, WARNING, ERROR
- Development: DEBUG, INFO, WARNING, ERROR

**Log Destinations**:
- Application Insights
- Azure Monitor Logs
- Function App logs (for debugging)

## 7. Scaling Configuration

### 7.1 Consumption Plan

**Auto-scaling**:
- Automatic based on load
- Scale to zero when idle
- Pay per execution

**Limits**:
- 10-minute timeout
- 1.5 GB memory per instance
- Unlimited scale-out

### 7.2 Premium Plan

**Features**:
- Always-on instances
- VNet integration
- Unlimited execution duration
- Pre-warmed instances

**Configuration**:
```bash
az functionapp plan create \
  --name plan-convert-functions \
  --resource-group rg-convert-functions \
  --location eastus \
  --sku EP1

az functionapp update \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --plan plan-convert-functions
```

### 7.3 Dedicated Plan

**Features**:
- Full control over scaling
- Reserved capacity
- Better for high-volume usage

## 8. Security Configuration

### 8.1 Authentication

**Function-Level Authentication**:
- Configure in `function.json`: `"authLevel": "function"`
- Use function keys for authentication

**Azure AD Integration**:
```bash
az functionapp auth update \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id <client-id> \
  --aad-token-issuer-url https://sts.windows.net/<tenant-id>/
```

### 8.2 Network Security

**Private Endpoints** (Premium/Dedicated):
- VNet integration
- Private endpoints for storage
- Network isolation

**IP Restrictions**:
```bash
az functionapp config access-restriction add \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --rule-name "AllowSpecificIP" \
  --action Allow \
  --ip-address <ip-address>
```

### 8.3 HTTPS Configuration

**TLS/SSL**:
- HTTPS enforced by default
- Minimum TLS version: 1.2
- Custom domains with SSL certificates

## 9. Backup and Recovery

### 9.1 Backup Strategy

**Function App Backup**:
- Enable backup in Azure Portal
- Configure backup schedule
- Store backups in separate storage account

**Code Backup**:
- Version control (Git)
- Regular commits
- Tagged releases

### 9.2 Recovery Procedures

**Function App Restore**:
1. Navigate to Function App → Backup
2. Select backup to restore
3. Restore to new or existing Function App

**Code Rollback**:
```bash
# Revert to previous version
git checkout <previous-tag>
func azure functionapp publish func-convert-app
```

## 10. Troubleshooting Deployment

### 10.1 Common Issues

**Issue: Dependencies not installed**
```bash
# Verify requirements.txt is included
# Check deployment logs
az functionapp log tail --name func-convert-app --resource-group rg-convert-functions
```

**Issue: Playwright browsers missing**
```bash
# Install browsers in deployment script
playwright install chromium
```

**Issue: Fonts not found (Linux)**
```bash
# Install system fonts
sudo apt-get install fonts-dejavu-core fonts-dejavu-extra
```

### 10.2 Deployment Validation

**Checklist**:
- [ ] All functions deployed
- [ ] Dependencies installed
- [ ] Playwright browsers installed
- [ ] Environment variables configured
- [ ] Authentication configured
- [ ] Monitoring enabled
- [ ] Tests passing

**Validation Script**:
```bash
# Test each endpoint
curl -X POST https://func-convert-app.azurewebsites.net/api/csv2json \
  -H "Content-Type: text/csv" \
  -d "name,age\nJohn,25"
```

## 11. CI/CD Pipeline

### 11.1 GitHub Actions Example

See section 3.2 Method 3 for complete workflow.

### 11.2 Azure DevOps Pipeline

**azure-pipelines.yml**:
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    pip install -r requirements.txt
    playwright install chromium
  displayName: 'Install dependencies'

- script: |
    pytest
  displayName: 'Run tests'

- task: AzureFunctionApp@1
  inputs:
    azureSubscription: '<subscription>'
    appName: 'func-convert-app'
    package: '.'
```

## 12. Maintenance

### 12.1 Regular Updates

**Dependencies**:
- Review and update `requirements.txt` monthly
- Test updates in development first
- Update Playwright browsers as needed

**Runtime**:
- Monitor Python version support
- Update Azure Functions runtime as available

### 12.2 Monitoring

**Key Metrics**:
- Function execution count
- Average execution time
- Error rate
- Memory usage
- Cost

**Alerts**:
- High error rate (>5%)
- Long execution times (>30s)
- High memory usage (>80%)
- Cost threshold exceeded

