# Azure Convert Functions
## Universal API for Data Conversion

**Convert any data formats in seconds with a serverless solution built on Azure Functions**

---

## 🚀 What is it?

Azure Convert Functions is a set of ready-to-use services for converting between various data formats. Simply send an HTTP request and get the result in the format you need. No servers, no infrastructure setup — just an API.

---

## ✨ Key Features

### 📊 Data Conversion

**CSV ↔ JSON**
- Fast conversion of tabular data
- Unicode and special character support
- Automatic structure detection

**Markdown → HTML**
- Full-featured HTML documents with CSS
- Support for tables, code, lists
- Optional content sanitization

**DBF → JSON**
- Conversion of legacy dBase files
- Support for dBASE III, dBASE IV, FoxPro
- Automatic encoding handling

### 📄 Document Generation

**HTML → PDF**
- Professional PDF documents
- Unicode and Cyrillic support
- Customizable styles and fonts

**URL → PDF**
- Convert web pages to PDF
- JavaScript content rendering
- Automatic image loading
- Dynamic table support

**URL → JPG**
- Web page screenshots
- Customizable resolution
- Full-page captures

---

## 🎯 Who is it for?

### Developers
- Integrate conversion into your applications
- REST API without infrastructure deployment
- Simple integration via HTTP requests

### Business Analysts
- Quick processing of data from various sources
- Convert reports to required formats
- Automate routine tasks

### DevOps Engineers
- Serverless architecture — pay only for usage
- Automatic scaling
- Minimal maintenance costs

### Enterprises
- Processing legacy formats (DBF)
- Data migration between systems
- Document generation from web content

---

## 💡 Advantages

### ⚡ Performance
- **Instant startup** — no cold start thanks to caching
- **Parallel processing** — automatic scaling with Azure Functions
- **Optimized algorithms** — fast processing of large data volumes

### 🔒 Security
- **Input validation** — protection against incorrect requests
- **SSRF protection** — blocking access to internal resources
- **Size limits** — protection against DoS attacks
- **Authorization** — Azure Function Keys support

### 💰 Cost-Effectiveness
- **Pay-per-use** — pay only for actual usage
- **No infrastructure costs** — Azure manages everything
- **Automatic scaling** — from 0 to millions of requests

### 🛠️ Ease of Use
- **REST API** — standard HTTP requests
- **JSON responses** — clear format for integration
- **Swagger documentation** — interactive API testing
- **Code examples** — ready-made examples for popular languages

### 🌍 Reliability
- **99.95% SLA** — Azure Functions availability guarantee
- **Automatic updates** — always up-to-date version
- **Monitoring and logging** — full transparency
- **Error handling** — clear error messages

---

## 📋 Usage Examples

### Converting CSV to JSON

```bash
curl -X POST "https://your-function.azurewebsites.net/api/csv2json" \
  -H "Content-Type: text/csv" \
  -d "name,age,city
John,25,New York
Jane,30,London"
```

**Result:**
```json
[
  {"name": "John", "age": "25", "city": "New York"},
  {"name": "Jane", "age": "30", "city": "London"}
]
```

### Generating PDF from Web Page

```bash
curl -X POST "https://your-function.azurewebsites.net/api/url2pdf" \
  -H "Content-Type: text/plain" \
  -d "https://example.com/report"
```

**Result:** PDF file with full page content

### Web Page Screenshot

```bash
curl -X POST "https://your-function.azurewebsites.net/api/url2jpg?width=1920&height=1080" \
  -H "Content-Type: text/plain" \
  -d "https://example.com/dashboard"
```

**Result:** JPEG image with specified resolution

---

## 🏗️ Architecture

### Serverless Microservices
Each conversion function is an independent microservice that:
- Runs on demand
- Automatically scales
- Is isolated from other functions

### Technology Stack
- **Python 3.11** — modern and performant
- **Azure Functions** — Microsoft's serverless platform
- **Playwright** — JavaScript content rendering
- **xhtml2pdf** — PDF generation from HTML
- **pandas** — tabular data processing

### Security
- Validation of all input data
- SSRF attack protection
- Request size limits
- Authorization support via Function Keys

---

## 📊 API Endpoints

| Endpoint | Method | Description | Input Format | Output Format |
|----------|-------|-------------|--------------|---------------|
| `/api/csv2json` | POST | CSV → JSON | CSV string | JSON array |
| `/api/json2csv` | POST | JSON → CSV | JSON object/array | CSV string |
| `/api/md2html` | POST | Markdown → HTML | Markdown string | HTML document |
| `/api/html2pdf` | POST | HTML → PDF | HTML string | PDF file |
| `/api/url2pdf` | POST | URL → PDF | URL string | PDF file |
| `/api/url2jpg` | POST | URL → JPG | URL string | JPEG image |
| `/api/dbf2json` | POST | DBF → JSON | DBF file (binary) | JSON array |

All endpoints support optional `code` parameter for authorization.

---

## 🚀 Quick Start

### 1. Deploy to Azure

```bash
# Create Function App
az functionapp create \
  --resource-group rg-convert-functions \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-convert-app \
  --storage-account stconvertfuncs \
  --os-type Linux

# Deploy functions
func azure functionapp publish func-convert-app
```

### 2. Using the API

```python
import requests

# Convert CSV to JSON
response = requests.post(
    'https://func-convert-app.azurewebsites.net/api/csv2json',
    data='name,age\nJohn,25',
    headers={'Content-Type': 'text/csv'}
)
json_data = response.json()
```

---

## 📈 Performance

- **CSV ↔ JSON**: up to 10,000 rows/sec
- **HTML → PDF**: ~2-5 seconds per document
- **URL → PDF**: ~5-10 seconds (depends on page complexity)
- **URL → JPG**: ~3-7 seconds

*Results may vary depending on data size and content complexity*

---

## 🔧 Configuration

All parameters are configured via environment variables:

- `MAX_REQUEST_SIZE` — maximum request size (default: 10 MB)
- `PLAYWRIGHT_TIMEOUT` — rendering timeout (default: 30 sec)
- `CACHE_TTL` — cache lifetime (default: 1 hour)
- `DEFAULT_SCREENSHOT_WIDTH/HEIGHT` — screenshot dimensions

---

## 📚 Documentation

- [Full API Documentation](spec/api.md)
- [Deployment Guide](AZURE_DEPLOYMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Swagger UI](swagger.json) — interactive documentation

---

## 💬 Support

- **GitHub Issues** — bug reports and suggestions
- **Documentation** — detailed guides and examples
- **Swagger** — interactive API testing

---

## 🎁 Features

### Smart Content Processing
- Automatic encoding detection
- Unicode and Cyrillic handling
- Support for complex CSS and JavaScript

### Performance Optimization
- URL content caching
- Parallel image loading
- Optimized CSS cleaning

### Reliability
- Handling of all error types
- Structured logging
- Automatic temporary file cleanup

---

## 🌟 Why Choose Us?

✅ **Ready Solution** — deploy in 5 minutes  
✅ **No Infrastructure** — Azure manages everything  
✅ **Scalability** — from 0 to millions of requests  
✅ **Security** — built-in attack protection  
✅ **Cost-Effective** — pay only for usage  
✅ **Support** — detailed documentation and examples  

---

## 🚀 Get Started Now

Deploy Azure Convert Functions on your Azure subscription and get access to all data conversion capabilities through a simple REST API.

**Azure Functions free tier includes:**
- 1,000,000 free requests per month
- 400,000 GB-seconds of execution per month

---

*Azure Convert Functions — your universal tool for working with data in the cloud*
