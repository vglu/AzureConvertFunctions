# Azure Convert Functions

A set of Azure Functions for converting various data formats, implemented in Python.

## Quick Start

- [Installation and Setup](INSTALL.md)
- [Azure Deployment](AZURE_DEPLOYMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Project Specification](spec/README.md)

## Functions

### 1. CSV2JSON
Converts CSV data to JSON format.

**Endpoint:** `POST /api/csv2json`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** CSV data as string

**Response:** JSON array of objects

**Example:**
```bash
curl -X POST "http://localhost:7071/api/csv2json?code=your-code" \
  -H "Content-Type: text/csv" \
  -d "name,age,city
John,25,New York
Jane,30,London"
```

### 2. HTML2PDF
Converts HTML to PDF document.

**Endpoint:** `POST /api/html2pdf`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** HTML data as string

**Response:** PDF file in binary format

**Example:**
```bash
curl -X POST "http://localhost:7071/api/html2pdf?code=your-code" \
  -H "Content-Type: text/html" \
  -d "<html><body><h1>Hello</h1></body></html>"
```

### 3. DBF2JSON
Converts DBF (dBase) file to JSON format.

**Endpoint:** `POST /api/dbf2json`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** DBF file in binary format

**Content-Type:** `application/x-dbf` or `application/octet-stream`

**Response:** JSON array of objects

**Example:**
```bash
# Upload DBF file
curl -X POST "http://localhost:7071/api/dbf2json?code=your-code" \
  -H "Content-Type: application/x-dbf" \
  --data-binary "@data.dbf"
```

**Note:** The function accepts DBF file in binary format. Supports dBASE III, dBASE IV, FoxPro formats.

### 4. JSON2CSV
Converts JSON data to CSV format.

**Endpoint:** `POST /api/json2csv`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** JSON object or array of objects

**Response:** CSV data

**Example:**
```bash
curl -X POST "http://localhost:7071/api/json2csv?code=your-code" \
  -H "Content-Type: application/json" \
  -d '[{"name":"John","age":25},{"name":"Jane","age":30}]'
```

### 5. MD2HTML
Converts Markdown to HTML.

**Endpoint:** `POST /api/md2html`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** Markdown data as string

**Response:** Full HTML document with styles

**Example:**
```bash
curl -X POST "http://localhost:7071/api/md2html?code=your-code" \
  -H "Content-Type: text/markdown" \
  -d "# Heading\n\nThis is **bold** text."
```

### 6. URL2PDF
Converts a web page by URL to PDF document. Supports JavaScript rendering via Playwright.

**Endpoint:** `POST /api/url2pdf`

**Query Parameters:**
- `code` (optional) - Azure Function authorization code

**Request Body:** URL as string

**Response:** PDF file in binary format

**Example:**
```bash
curl -X POST "http://localhost:7071/api/url2pdf?code=your-code" \
  -H "Content-Type: text/plain" \
  -d "https://example.com"
```

**Note:** For pages with dynamic content (JavaScript), Playwright and browsers installation is required:
```powershell
playwright install chromium
```

### 7. URL2JPG
Creates a screenshot of a web page by URL and returns JPG image. Uses Playwright for JavaScript rendering.

**Endpoint:** `POST /api/url2jpg`

**Request Body:** URL as string

**Query Parameters:**
- `code` (optional) - Azure Function authorization code
- `width` (optional) - screenshot width in pixels (default: 1920)
- `height` (optional) - screenshot height in pixels (default: 1080)

**Response:** JPG image in binary format

**Example:**
```bash
curl -X POST "http://localhost:7071/api/url2jpg?code=your-code&width=1920&height=1080" \
  -H "Content-Type: text/plain" \
  -d "https://example.com"
```

**Note:** Playwright and browsers installation is required:
```powershell
playwright install chromium
```

## Swagger/OpenAPI Documentation

API documentation is available through Swagger UI:

**Endpoint:** `GET /api/swagger`

Open in browser: `http://localhost:7071/api/swagger` to view interactive API documentation.

Swagger JSON specification is available at: `GET /api/swagger/swagger.json`

## Installation and Running

### Requirements
- Python 3.10+ (3.11 recommended, Python 3.9 reached EOL)
- Azure Functions Core Tools

**Supported platforms:**
- Windows
- Linux (Ubuntu/Debian)
- macOS

### Installing Dependencies

**IMPORTANT:** Azure Functions Core Tools uses system Python, not virtual environment!

**If virtual environment is activated, deactivate it first:**

```powershell
deactivate
```

**Then install dependencies in system Python:**

```powershell
# Install all dependencies
python -m pip install -r requirements.txt

# Install browsers for Playwright (for url2pdf and url2jpg with JavaScript support)
playwright install chromium

# On Linux, system dependencies are also required:
# Ubuntu/Debian:
# sudo apt-get update
# sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

**Verification:**

```powershell
# Check that system Python is being used
python -c "import sys; print(sys.executable)"

# Check module installation
python -c "import pandas, markdown, xhtml2pdf, requests; print('All modules installed!')"

# Check Playwright (optional)
python -c "from playwright.sync_api import sync_playwright; print('Playwright available!')"
```

**Alternative - virtual environment:**

If you want to use a virtual environment, activate it and run `func start` from the same terminal:

```powershell
.venv\Scripts\Activate.ps1
func start
```

### Local Run

**Before running, create `local.settings.json`:**

```powershell
# Copy example
Copy-Item local.settings.json.example local.settings.json
```

Then start the functions:

```bash
func start
```

**If you encounter a grpc error**, see the [Troubleshooting](#troubleshooting) section below or run:

```powershell
.\fix-grpc-issue.ps1
```

### Running Tests

```bash
pip install pytest
pytest
```

## Dependencies

- `azure-functions` - SDK for Azure Functions
- `pandas` - for working with CSV and data
- `markdown` - for converting Markdown to HTML
- `xhtml2pdf` - for converting HTML to PDF (cross-platform)
- `bleach` - for HTML sanitization (optional)
- `requests` - for loading HTML from URL
- `playwright` - for rendering JavaScript on web pages (for url2pdf and url2jpg)
- `dbfread` - for reading DBF (dBase) files

**Note for Linux:**
- For PDF work, system fonts are needed (usually already installed: DejaVu Sans, Liberation Sans)
- For Playwright, system dependencies are required (see instructions above)

## Project Structure

```
.
├── csv2json/
│   ├── __init__.py
│   └── function.json
├── html2pdf/
│   ├── __init__.py
│   └── function.json
├── json2csv/
│   ├── __init__.py
│   └── function.json
├── md2html/
│   ├── __init__.py
│   └── function.json
├── swagger/
│   ├── __init__.py
│   └── function.json
├── tests/
│   ├── test_csv2json.py
│   ├── test_html2pdf.py
│   ├── test_json2csv.py
│   ├── test_md2html.py
│   └── test_swagger.py
├── host.json
├── swagger.json
├── requirements.txt
└── README.md
```

## Testing

All functions are covered with test cases:

- **test_csv2json.py** - tests for CSV2JSON conversion
- **test_json2csv.py** - tests for JSON2CSV conversion
- **test_md2html.py** - tests for MD2HTML conversion
- **test_html2pdf.py** - tests for HTML2PDF conversion
- **test_swagger.py** - tests for Swagger UI function
- **test_url2pdf.py** - tests for URL2PDF conversion (if created)
- **test_url2jpg.py** - tests for URL2JPG conversion (if created)

Each test file contains:
- Successful conversion tests
- Error handling tests
- Edge case tests
- Special character tests

## Troubleshooting

### Error: cannot import name 'cygrpc' from 'grpc._cython'

This is a known issue with Azure Functions Core Tools on Windows. Solutions:

1. **Update Azure Functions Core Tools:**
   ```powershell
   choco upgrade azure-functions-core-tools
   # or
   npm install -g azure-functions-core-tools@latest
   ```

2. **Use virtual environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   func start
   ```

3. **Run diagnostic script:**
   ```powershell
   .\fix-grpc-issue.ps1
   ```

For detailed instructions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Azure Deployment

1. Create Azure Function App
2. Install dependencies via Kudu or SSH
3. Deploy functions via Azure CLI or Visual Studio Code

```bash
func azure functionapp publish <your-function-app-name>
```

For detailed deployment instructions, see [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
