# Technical Specification

## 1. Technology Stack

### 1.1 Runtime Environment

- **Platform**: Azure Functions
- **Runtime**: Python 3.10 or higher (recommended 3.11, Python 3.9 reached EOL on 2025-10-31)
- **Worker Runtime**: Azure Functions Python Worker 4.x
- **OS**: Windows (development), Linux (production)

### 1.2 Core Dependencies

```txt
azure-functions          # Azure Functions SDK
pandas==2.1.4           # Data manipulation (CSV/JSON)
markdown==3.5.1         # Markdown to HTML conversion
xhtml2pdf==0.2.15       # HTML to PDF conversion
bleach==6.1.0           # HTML sanitization
requests==2.31.0        # HTTP client
playwright==1.57.0      # Headless browser
dbfread==2.0.7          # DBF (dBase) file reading
pytest==7.4.3           # Testing framework
```

### 1.3 System Dependencies

**Windows**:
- System fonts in `C:\Windows\Fonts\`
- No additional system libraries required

**Linux**:
- System fonts: `/usr/share/fonts/truetype/`
- Playwright dependencies:
  ```bash
  libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2
  libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3
  libxrandr2 libgbm1 libasound2
  ```

## 2. Implementation Details

### 2.1 CSV to JSON Conversion

**Library**: `pandas`

**Implementation**:
```python
import pandas as pd
from io import StringIO

csv_buffer = StringIO(csv_content)
df = pd.read_csv(csv_buffer)
json_result = df.to_json(orient='records', force_ascii=False, indent=2)
```

**Features**:
- Automatic type detection
- Unicode support (`force_ascii=False`)
- Records-oriented JSON output

**Limitations**:
- Large files may cause memory issues
- Complex CSV formats may require additional configuration

### 2.2 JSON to CSV Conversion

**Library**: `pandas`

**Implementation**:
```python
import pandas as pd
from io import StringIO

data = json.loads(json_content)
df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False, encoding='utf-8')
```

**Features**:
- Handles both objects and arrays
- UTF-8 encoding
- No index column

### 2.3 DBF to JSON Conversion

**Library**: `dbfread`

**Implementation**:
```python
from dbfread import DBF
import tempfile
import os

# Save binary data to temporary file
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dbf')
temp_file.write(dbf_data)
temp_file.close()

# Read DBF file
table = DBF(temp_file.name, encoding='utf-8', load=True)

# Convert to list of dictionaries
records = []
for record in table:
    record_dict = {}
    for field_name in record.keys():
        value = record[field_name]
        if value is None:
            record_dict[field_name] = None
        else:
            record_dict[field_name] = value
    records.append(record_dict)

# Clean up temp file
os.unlink(temp_file.name)
```

**Features**:
- Supports dBASE III, dBASE IV, FoxPro formats
- UTF-8 encoding
- Handles various field types
- Automatic type conversion

**Limitations**:
- Requires temporary file (DBF library needs file path)
- Large files may cause memory issues
- Some legacy DBF formats may not be fully supported

### 2.4 Markdown to HTML Conversion

**Library**: `markdown`

**Implementation**:
```python
import markdown

html_content = markdown.markdown(
    md_content,
    extensions=['extra', 'codehilite', 'tables']
)
```

**Extensions**:
- `extra`: Extended syntax (tables, fenced code)
- `codehilite`: Syntax highlighting
- `tables`: Table support

**Output**: Complete HTML document with embedded CSS

### 2.5 HTML to PDF Conversion

**Library**: `xhtml2pdf` (pisa)

**Implementation**:
```python
from xhtml2pdf import pisa
from io import BytesIO

pdf_buffer = BytesIO()
pisa_status = pisa.CreatePDF(
    src=html_content,
    dest=pdf_buffer,
    encoding='utf-8',
    link_callback=None,
    show_error_as_pdf=False
)
```

**Font Registration**:
- Windows: Arial, Calibri, Verdana from `C:\Windows\Fonts\`
- Linux: DejaVu Sans, Liberation Sans, Noto Sans
- Registration via ReportLab's `pdfmetrics.registerFont()`

**CSS Limitations**:
- No support for `calc()`, `var()`, `@keyframes`
- Limited pseudo-class support (`:not()`, `:nth-child()`)
- No vendor prefixes (`-webkit-`, `-moz-`)
- Requires CSS normalization

### 2.5 URL to PDF Conversion

**Components**:
1. **URL Fetching**: Playwright (primary) or requests (fallback)
2. **HTML Cleanup**: Aggressive CSS/JS removal
3. **Image Handling**: Temporary files via link_callback
4. **PDF Generation**: xhtml2pdf

**Playwright Configuration**:
```python
browser = p.chromium.launch(headless=True)
page = browser.new_page()
page.goto(url, wait_until='domcontentloaded', timeout=30000)
page.wait_for_load_state('networkidle', timeout=10000)
```

**HTML Cleanup Process**:
1. Remove all `<link>` tags
2. Remove all `<script>` tags
3. Remove all `<style>` tags
4. Remove CSS @ rules (`@keyframes`, `@media`, etc.)
5. Remove modern CSS functions (`calc()`, `var()`)
6. Remove complex selectors (`:not()`, attribute selectors)
7. Normalize CSS (remove newlines, collapse whitespace)
8. Remove inline `style` attributes

**Image Handling**:
- Convert relative URLs to absolute
- Download images via link_callback
- Store in temporary files
- Clean up after PDF generation

### 2.6 URL to JPG Conversion

**Library**: `playwright`

**Implementation**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({"width": width, "height": height})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(2000)  # Wait for dynamic content
    screenshot_bytes = page.screenshot(type="jpeg", quality=90, full_page=True)
    browser.close()
```

**Features**:
- Full-page screenshots
- Custom viewport size
- JPEG quality: 90%
- JavaScript rendering support

## 3. Font Management

### 3.1 Font Registration

**Windows Fonts**:
```python
font_configs = [
    (r'C:\Windows\Fonts\arial.ttf', 'Arial', 'Arial'),
    (r'C:\Windows\Fonts\arialuni.ttf', 'ArialUnicode', 'Arial'),
    (r'C:\Windows\Fonts\calibri.ttf', 'Calibri', 'Calibri'),
    (r'C:\Windows\Fonts\verdana.ttf', 'Verdana', 'Verdana'),
]
```

**Linux Fonts**:
```python
font_configs = [
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans', 'DejaVu Sans'),
    ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans', 'Liberation Sans'),
    ('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', 'NotoSans', 'Noto Sans'),
]
```

**Registration Process**:
1. Check if fonts already registered (global flag)
2. Iterate through font configs
3. Check if font file exists
4. Register with ReportLab: `pdfmetrics.registerFont(TTFont(...))`
5. Map CSS names to registered fonts: `addMapping(...)`

### 3.2 Font Mapping

**CSS to ReportLab Mapping**:
- `Helvetica` → Registered font (Arial/DejaVu)
- `Arial` → Registered font
- `sans-serif` → Registered font

**Font Variants**:
- Normal, Italic, Bold, Bold Italic
- All variants mapped to registered font

## 4. CSS Processing

### 4.1 CSS Cleanup Rules

**Removed Elements**:
- All `<link>` tags (external stylesheets)
- All `<script>` tags (JavaScript)
- All `<style>` tags (embedded CSS)
- Inline `style` attributes

**Removed CSS Features**:
- `@keyframes` animations
- `@media` queries
- `@import` statements
- `@` rules in general
- `calc()` functions
- `var()` CSS variables
- `:not()` pseudo-classes
- `:nth-child()` and similar
- Attribute selectors `[attr]`
- Vendor prefixes (`-webkit-`, `-moz-`, etc.)
- `animation` and `transition` properties
- `content` property
- `transform` property

**Normalization**:
- Remove newlines within CSS values
- Collapse multiple whitespace
- Normalize spacing around `:`, `;`, `{`, `}`

### 4.2 Injected CSS

**Base Styles**:
```css
@page {
    margin: 2cm;
}
* {
    font-family: Helvetica, Arial, sans-serif !important;
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 12pt;
    line-height: 1.6;
}
```

**Table Styles**:
```css
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
```

## 5. Image Processing

### 5.1 Image Download

**Process**:
1. Extract image URLs from HTML
2. Convert relative URLs to absolute
3. Download via `requests`
4. Validate Content-Type
5. Store in temporary file
6. Return file path to xhtml2pdf

**Temporary File Management**:
```python
import tempfile

temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
temp_file.write(image_data)
temp_file.close()
temp_files.append(temp_file.name)
```

**Cleanup**:
```python
finally:
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
```

### 5.2 Image Format Support

**Supported Formats**:
- JPEG/JPG
- PNG
- GIF
- WebP
- SVG (limited support in PDF)

**MIME Type Detection**:
- From HTTP response headers
- From file extension fallback
- Default: `image/jpeg`

## 6. Error Handling

### 6.1 Exception Types

**Input Validation Errors**:
- Empty input → HTTP 400
- Invalid format → HTTP 400
- Invalid URL → HTTP 400

**Processing Errors**:
- Conversion failure → HTTP 500
- PDF generation error → HTTP 500
- Network timeout → HTTP 400/500

**System Errors**:
- Missing dependencies → HTTP 500
- Font registration failure → Warning (fallback to default)
- Playwright unavailable → HTTP 500 (for url2jpg)

### 6.2 Error Logging

**Log Levels**:
- `ERROR`: Critical failures
- `WARNING`: Non-critical issues (font registration, fallbacks)
- `INFO`: Successful operations
- `DEBUG`: Detailed debugging information

**Log Format**:
```
[timestamp] [level] [function_name] message
```

## 7. Performance Optimization

### 7.1 Caching

**Font Registration**:
- Global flag `_fonts_registered`
- One-time registration per function instance
- Persists for function lifetime

**Image Caching**:
- Cache downloaded images in `link_callback`
- Reuse for multiple references
- Clean up after PDF generation

### 7.2 Resource Management

**Memory**:
- Use streaming for large files where possible
- Clean up temporary objects
- Efficient pandas operations

**CPU**:
- Optimize regex operations
- Minimize CSS processing
- Efficient HTML parsing

**Storage**:
- Temporary files with automatic cleanup
- No persistent storage

## 8. Testing

### 8.1 Unit Tests

**Framework**: `pytest`

**Test Files**:
- `tests/test_csv2json.py`
- `tests/test_json2csv.py`
- `tests/test_md2html.py`
- `tests/test_html2pdf.py`
- `tests/test_swagger.py`

**Test Structure**:
```python
def test_function_success():
    # Arrange
    mock_request = MockRequest(b"input data")
    
    # Act
    response = main(mock_request)
    
    # Assert
    assert response.status_code == 200
    assert response.get_body() is not None
```

### 8.2 Test Coverage

**Target**: >80% code coverage

**Coverage Areas**:
- Happy path scenarios
- Error handling
- Edge cases
- Input validation

## 9. Configuration

### 9.1 Function Configuration

**function.json**:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

### 9.2 Host Configuration

**host.json**:
```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[2.*, 3.0.0)"
  },
  "functionTimeout": "00:10:00"
}
```

### 9.3 Environment Variables

**local.settings.json** (development):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

## 10. Deployment

### 10.1 Build Process

1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright browsers: `playwright install chromium`
3. Run tests: `pytest`
4. Package function app
5. Deploy to Azure

### 10.2 Deployment Methods

- **Azure CLI**: `az functionapp deployment source config-zip`
- **VS Code**: Azure Functions extension
- **GitHub Actions**: CI/CD pipeline
- **Azure DevOps**: Build and release pipeline

### 10.3 Post-Deployment

1. Verify function app is running
2. Test endpoints
3. Configure authentication
4. Set up monitoring
5. Configure scaling (if needed)

## 11. Known Limitations

### 11.1 xhtml2pdf Limitations

- Limited CSS support
- Complex CSS may cause parsing errors
- Image handling requires temporary files
- Performance issues with large documents

### 11.2 Playwright Limitations

- Requires system dependencies on Linux
- High memory usage
- Slower than static HTML parsing
- Browser binary size

### 11.3 Azure Functions Limitations

- Execution timeout (10 minutes default)
- Memory limits per execution
- Cold start latency
- Concurrent execution limits

## 12. Future Improvements

### 12.1 Technical Improvements

1. **Replace xhtml2pdf with Playwright PDF**:
   - Better CSS support
   - Native image handling
   - Simpler code

2. **Optimize CSS Processing**:
   - More selective cleanup
   - Preserve more CSS features
   - Better error handling

3. **Image Optimization**:
   - Compression
   - Format conversion
   - Caching strategy

### 12.2 Architecture Improvements

1. **Caching Layer**: Redis for URL content
2. **Queue Processing**: For long-running operations
3. **Monitoring**: Application Insights integration
4. **CDN**: For static assets

