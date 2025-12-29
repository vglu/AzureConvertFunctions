# How I Solved the Data Conversion Problem in Serverless Architecture: From Idea to Production

## The Problem Every Developer Has Faced

Recently, I had to solve a classic problem: I needed to convert data between various formats (CSV, JSON, HTML, PDF) across multiple projects. Each time, I wrote the same code, configured servers, and thought about scaling and security.

Then I thought: what if I do it right once and use it everywhere?

## Solution: Serverless Microservices on Azure Functions

I created a set of Azure Functions for data conversion — a universal solution that can be used in any project through a simple HTTP API. Here's what came out:

### What the system can do:

✅ **CSV ↔ JSON** — fast conversion of tabular data  
✅ **Markdown → HTML** — generation of beautiful HTML documents  
✅ **HTML → PDF** — PDF creation with Unicode support  
✅ **URL → PDF** — convert web pages to PDF with JavaScript rendering  
✅ **URL → JPG** — web page screenshots  
✅ **DBF → JSON** — working with legacy formats  

## Technical Challenges and Solutions

### 1. JavaScript Content Rendering

**Problem:** Many modern websites load data via JavaScript. A simple HTTP request returns an empty page.

**Solution:** Used Playwright for headless browser. Now the system:
- Waits for dynamic content to load
- Scrolls the page to trigger lazy loading
- Takes screenshots and converts to PDF

```python
# Smart content waiting
page.wait_for_selector('table tbody tr', timeout=10000)
page.wait_for_load_state('networkidle')
```

### 2. Security: SSRF Protection

**Problem:** If accepting URLs from users, an attacker could gain access to internal resources (localhost, Azure metadata, etc.).

**Solution:** Implemented multi-level validation:
- URL scheme check (only http/https)
- Blocking localhost and internal IPs
- Private IP range checks
- Azure metadata service blocking

```python
# Check for private IPs
if ip.is_private or ip.is_loopback:
    raise SecurityError("Private IP addresses are not allowed")
```

### 3. Complex CSS Handling

**Problem:** xhtml2pdf (library for PDF generation) doesn't support modern CSS (calc(), var(), @keyframes, etc.).

**Solution:** Created an aggressive CSS cleaning system using regular expressions. Now the system:
- Removes unsupported CSS functions
- Normalizes CSS syntax
- Handles multi-line values

### 4. Modular Architecture

**Problem:** Code was duplicated between functions (font registration, validation, logging).

**Solution:** Created a modular structure with shared utilities:
- `utils/validation.py` — input validation
- `utils/fonts.py` — font registration
- `utils/exceptions.py` — specific exceptions
- `utils/config.py` — centralized configuration

Result: code became 3 times shorter and easier to maintain.

## Architectural Decisions

### Serverless Microservices

Each conversion function is an independent microservice:
- Runs on demand (from 0 to millions of requests)
- Automatically scales
- Isolated from other functions

### Caching

Implemented simple in-memory caching for URL content:
- Reduces load on external resources
- Speeds up repeated requests
- Configurable TTL via environment variables

### Structured Logging

Every request is logged with context:
- Request ID for tracing
- Function, method, URL
- Execution time
- Errors with full stack

This is critical for a production system.

## Results

### Performance
- CSV ↔ JSON: up to 10,000 rows/sec
- URL → PDF: 5-10 seconds (depends on complexity)
- Automatic scaling without configuration

### Cost-Effectiveness
- Pay-per-use model
- Free tier: 1M requests/month
- No infrastructure costs

### Security
- Validation of all input data
- SSRF protection
- Request size limits
- Authorization support

## Lessons I Learned

### 1. Serverless is Not Just About Cost Savings

Serverless architecture provides not only savings but also:
- Automatic scaling
- No need to manage infrastructure
- Focus on business logic, not DevOps

### 2. Security Must Be Built In From the Start

Input validation and attack protection are not optional, but a mandatory part of any system that accepts data from users.

### 3. Modularity is Key to Maintainability

Extracting common code into utilities not only reduces duplication but also simplifies testing and maintenance.

### 4. Documentation is an Investment

Detailed documentation (Swagger, examples, troubleshooting) saves time in the future and makes the product accessible to other developers.

## What's Next?

Planning to add:
- Support for more formats (Excel, XML)
- Parallel processing of multiple files
- Azure Storage integration for large files
- Metrics and monitoring via Application Insights

## Conclusions

Creating a universal solution for data conversion taught me:
- How to properly design serverless architecture
- To think about security from the start
- To write modular and maintainable code
- To document solutions for future me and others

If you've also faced similar challenges — share your experience in the comments! What approaches did you use? What problems did you encounter?

---

**Technologies:** Python 3.11, Azure Functions, Playwright, xhtml2pdf, pandas  
**Architecture:** Serverless microservices  
**Security:** SSRF protection, input validation  
**Performance:** Caching, CSS processing optimization  

#Serverless #AzureFunctions #Python #DevOps #CloudComputing #SoftwareArchitecture #BackendDevelopment #APIDevelopment
