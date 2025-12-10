# Architecture Specification

## 1. System Overview

Azure Convert Functions is a serverless microservices architecture built on Azure Functions. The system provides stateless, on-demand data conversion services through HTTP-triggered functions.

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                      │
│  (Web Apps, Mobile Apps, API Clients, Command Line Tools)   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Azure Functions Runtime                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              HTTP Trigger Functions                   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │  │
│  │  │ csv2json │ │ json2csv │ │ dbf2json │ │ md2html │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │  │
│  │  │ html2pdf │ │ url2pdf  │ │ url2jpg  │            │  │
│  │  └──────────┘ └──────────┘ └──────────┘            │  │
│  │  ┌──────────┐                                       │  │
│  │  │ swagger  │                                       │  │
│  │  └──────────┘                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Python Runtime (3.10+)                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │  │
│  │  │ pandas   │ │ markdown │ │ xhtml2pdf│ │requests │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │  │
│  │  ┌──────────┐ ┌──────────┐                          │  │
│  │  │ playwright│ │ bleach   │                          │  │
│  │  └──────────┘ └──────────┘                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ External│    │ System  │    │ Temp    │
    │ URLs    │    │ Fonts   │    │ Files   │
    └─────────┘    └─────────┘    └─────────┘
```

## 3. Component Architecture

### 3.1 Function Components

Each function follows a consistent structure:

```
function_name/
├── __init__.py          # Main function code
├── function.json        # Function configuration
└── (dependencies)      # Shared utilities
```

**Function Structure**:
1. **Input Handler**: Receives HTTP request, validates input
2. **Processor**: Performs conversion logic
3. **Output Handler**: Formats and returns HTTP response
4. **Error Handler**: Catches and handles exceptions

### 3.2 Shared Components

#### 3.2.1 Font Registration Module
- **Location**: `html2pdf/__init__.py`, `url2pdf/__init__.py`
- **Purpose**: Register system fonts for Unicode/Cyrillic support
- **Platform Support**: Windows and Linux
- **Fonts**: Arial, Calibri, Verdana (Windows); DejaVu, Liberation, Noto (Linux)

#### 3.2.2 URL Content Fetcher
- **Location**: `url2pdf/__init__.py`
- **Purpose**: Fetch HTML content from URLs
- **Features**:
  - Playwright for JavaScript rendering
  - Fallback to requests library
  - CSS/JS cleanup
  - Image URL normalization

#### 3.2.3 Image Handler
- **Location**: `url2pdf/__init__.py`
- **Purpose**: Download and embed images in PDF
- **Features**:
  - Image downloading
  - Temporary file management
  - Base64 conversion (alternative approach)

## 4. Data Flow

### 4.1 CSV to JSON Flow

```
Client Request
    │
    ▼
HTTP Trigger (csv2json)
    │
    ▼
Input Validation
    │
    ▼
pandas.read_csv()
    │
    ▼
DataFrame.to_json()
    │
    ▼
HTTP Response (JSON)
```

### 4.1.1 DBF to JSON Flow

```
Client Request (DBF binary)
    │
    ▼
HTTP Trigger (dbf2json)
    │
    ▼
Input Validation
    │
    ▼
Save to Temporary File
    │
    ▼
dbfread.DBF()
    │
    ▼
Convert Records to Dict
    │
    ▼
json.dumps()
    │
    ▼
Cleanup Temp File
    │
    ▼
HTTP Response (JSON)
```

### 4.2 URL to PDF Flow

```
Client Request (URL)
    │
    ▼
HTTP Trigger (url2pdf)
    │
    ▼
URL Validation
    │
    ▼
Playwright Browser Launch
    │
    ▼
Page Navigation & Rendering
    │
    ├─► Wait for Dynamic Content
    ├─► Scroll to Trigger Lazy Loading
    └─► Extract HTML
    │
    ▼
HTML Cleanup
    ├─► Remove CSS/JS
    ├─► Normalize CSS
    └─► Convert Image URLs
    │
    ▼
Image Download & Temp Files
    │
    ▼
PDF Generation (xhtml2pdf)
    ├─► Font Registration
    ├─► CSS Injection
    └─► Image Embedding
    │
    ▼
Temp File Cleanup
    │
    ▼
HTTP Response (PDF)
```

### 4.3 URL to JPG Flow

```
Client Request (URL + params)
    │
    ▼
HTTP Trigger (url2jpg)
    │
    ▼
URL Validation
    │
    ▼
Playwright Browser Launch
    │
    ▼
Page Navigation
    │
    ▼
Wait for Content Load
    │
    ▼
Screenshot Capture
    │
    ▼
JPEG Encoding
    │
    ▼
HTTP Response (JPG)
```

## 5. Technology Stack

### 5.1 Runtime
- **Platform**: Azure Functions
- **Language**: Python 3.10+ (recommended 3.11)
- **Runtime Version**: Azure Functions Python Worker 4.x

### 5.2 Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| pandas | 2.1.4 | CSV/JSON data manipulation |
| markdown | 3.5.1 | Markdown to HTML conversion |
| xhtml2pdf | 0.2.15 | HTML to PDF conversion |
| bleach | 6.1.0 | HTML sanitization |
| requests | 2.31.0 | HTTP client for URL fetching |
| playwright | 1.57.0 | Headless browser for JS rendering |

### 5.3 System Dependencies

**Windows**:
- System fonts: Arial, Calibri, Verdana (in `C:\Windows\Fonts\`)

**Linux**:
- System fonts: DejaVu Sans, Liberation Sans, Noto Sans
- Playwright system dependencies (libnss3, libatk, etc.)

## 6. Deployment Architecture

### 6.1 Azure Functions Deployment

```
┌─────────────────────────────────────┐
│      Azure Function App             │
│  ┌───────────────────────────────┐  │
│  │   Consumption Plan            │  │
│  │   (or Premium/Dedicated)      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Function App Settings       │  │
│  │   - Python 3.11                │  │
│  │   - Auto-scaling             │  │
│  │   - Timeout: 10 min          │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Application Settings        │  │
│  │   - Environment variables     │  │
│  │   - Connection strings       │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 6.2 Local Development

```
┌─────────────────────────────────────┐
│   Azure Functions Core Tools        │
│   (func start)                      │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Local Python Environment    │  │
│  │   - System Python 3.10+       │  │
│  │   - Virtual env (optional)    │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Playwright Browsers         │  │
│  │   - Chromium (local install) │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 7. Security Architecture

### 7.1 Authentication Layers

1. **Function Level**: Configurable in `function.json`
   - `anonymous`: No authentication
   - `function`: Function key required
   - `admin`: Master key required

2. **Azure AD**: Optional integration
3. **API Keys**: Custom authentication (optional)

### 7.2 Input Validation

- URL validation (scheme, netloc)
- Content type validation
- Size limits (implicit via Azure Functions)
- Sanitization (HTML via bleach, optional)

### 7.3 Data Privacy

- No persistent storage
- Temporary files cleaned up
- No logging of sensitive data
- Stateless design

## 8. Scalability

### 8.1 Auto-scaling

Azure Functions automatically scales based on:
- Request volume
- Function app plan limits
- Resource availability

### 8.2 Stateless Design

- No shared state between invocations
- Each request is independent
- No session management required

### 8.3 Resource Management

- Memory: Efficient handling of large files
- CPU: Optimized conversion operations
- Storage: Temporary files with automatic cleanup
- Network: Efficient HTTP client usage

## 9. Error Handling Architecture

### 9.1 Error Categories

1. **Input Errors** (400): Invalid input, missing data
2. **Authentication Errors** (401/403): Auth failures
3. **Processing Errors** (500): Conversion failures
4. **Timeout Errors** (504): Execution timeout

### 9.2 Error Flow

```
Exception Occurred
    │
    ▼
Exception Handler
    │
    ├─► Log Error (with context)
    ├─► Determine Error Type
    └─► Format Error Response
    │
    ▼
HTTP Error Response
```

### 9.3 Logging

- All errors logged with context
- Warning logs for non-critical issues
- Info logs for successful operations
- Debug logs for development

## 10. Performance Considerations

### 10.1 Optimization Strategies

1. **Caching**: Font registration cached (one-time)
2. **Lazy Loading**: Playwright only when needed
3. **Resource Cleanup**: Automatic temp file cleanup
4. **Efficient Libraries**: pandas for data operations

### 10.2 Bottlenecks

1. **PDF Generation**: xhtml2pdf can be slow for complex HTML
2. **URL Fetching**: Network latency
3. **JavaScript Rendering**: Playwright overhead
4. **Image Processing**: Download and embedding time

### 10.3 Mitigation

- Timeout configuration
- Efficient CSS cleanup
- Image caching in link_callback
- Parallel processing where possible

## 11. Future Architecture Considerations

### 11.1 Potential Improvements

1. **Playwright PDF**: Replace xhtml2pdf with Playwright PDF generation
   - Better CSS support
   - Native image handling
   - Simpler code

2. **Caching Layer**: Add Redis for frequently accessed URLs
3. **Queue Processing**: For long-running conversions
4. **Monitoring**: Application Insights integration
5. **CDN**: For static assets (Swagger UI)

### 11.2 Scalability Enhancements

- Function app scaling configuration
- Premium plan for better performance
- Dedicated plan for high-volume usage
- Multi-region deployment

