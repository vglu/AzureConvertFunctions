# API Specification

## Base URL

```
Development: http://localhost:7071/api
Production: https://<function-app-name>.azurewebsites.net/api
```

## Authentication

All endpoints support function-level authentication. Configure authentication level in `function.json`:
- `anonymous` - No authentication required
- `function` - Function key required
- `admin` - Master key required

## Endpoints

### 1. CSV to JSON

**Endpoint**: `POST /api/csv2json`

**Description**: Converts CSV data to JSON format

**Request**:
```http
POST /api/csv2json HTTP/1.1
Content-Type: text/csv
Content-Length: <length>

name,age,city
John,25,New York
Jane,30,London
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "name": "John",
    "age": "25",
    "city": "New York"
  },
  {
    "name": "Jane",
    "age": "30",
    "city": "London"
  }
]
```

**Response** (Error):
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "CSV content not provided"
}
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (empty or invalid input)
- `500` - Internal Server Error

---

### 2. JSON to CSV

**Endpoint**: `POST /api/json2csv`

**Description**: Converts JSON data to CSV format

**Request**:
```http
POST /api/json2csv HTTP/1.1
Content-Type: application/json

[
  {"name": "John", "age": 25, "city": "New York"},
  {"name": "Jane", "age": 30, "city": "London"}
]
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename=converted.csv

name,age,city
John,25,New York
Jane,30,London
```

**Response** (Error):
```http
HTTP/1.1 400 Bad Request
Content-Type: text/plain

JSON parsing error: Expecting value: line 1 column 1 (char 0)
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (invalid JSON)
- `500` - Internal Server Error

---

### 3. DBF to JSON

**Endpoint**: `POST /api/dbf2json`

**Description**: Converts DBF (dBase) file to JSON format

**Request**:
```http
POST /api/dbf2json HTTP/1.1
Content-Type: application/x-dbf
Content-Length: <length>

<DBF binary data>
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "NAME": "John",
    "AGE": 25,
    "CITY": "New York"
  },
  {
    "NAME": "Jane",
    "AGE": 30,
    "CITY": "London"
  }
]
```

**Response** (Error):
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "DBF file not provided"
}
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (empty or invalid input)
- `500` - Internal Server Error (invalid DBF format)

**Features**:
- Supports dBASE III, dBASE IV, FoxPro formats
- UTF-8 encoding support
- Handles various field types (Character, Numeric, Date, Logical)
- Automatic type conversion

**Example**:
```bash
# Upload DBF file
curl -X POST https://func-convert-app.azurewebsites.net/api/dbf2json \
  -H "Content-Type: application/x-dbf" \
  --data-binary "@data.dbf"
```

---

### 4. Markdown to HTML

**Endpoint**: `POST /api/md2html`

**Description**: Converts Markdown text to HTML

**Request**:
```http
POST /api/md2html HTTP/1.1
Content-Type: text/markdown

# Hello World

This is a **markdown** document.
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Converted Markdown</title>
    <style>...</style>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a <strong>markdown</strong> document.</p>
</body>
</html>
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (empty input)
- `500` - Internal Server Error

---

### 5. HTML to PDF

**Endpoint**: `POST /api/html2pdf`

**Description**: Converts HTML content to PDF document

**Request**:
```http
POST /api/html2pdf HTTP/1.1
Content-Type: text/html

<html>
<body>
    <h1>Hello World</h1>
    <p>This is a PDF document.</p>
</body>
</html>
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename=converted.pdf

<PDF binary data>
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (empty input)
- `500` - Internal Server Error (PDF generation failed)

**Features**:
- Unicode and Cyrillic character support
- Custom fonts (Arial, Calibri, Verdana on Windows)
- Page margins: 2cm

---

### 6. URL to PDF

**Endpoint**: `POST /api/url2pdf`

**Description**: Converts web page URL to PDF document

**Request**:
```http
POST /api/url2pdf HTTP/1.1
Content-Type: text/plain

https://example.com
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename=converted.pdf

<PDF binary data>
```

**Response** (Error):
```http
HTTP/1.1 400 Bad Request
Content-Type: text/plain

Error fetching URL: Connection timeout
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (invalid URL or fetch failed)
- `500` - Internal Server Error (PDF generation failed)

**Features**:
- JavaScript rendering via Playwright
- Dynamic content loading
- Image embedding
- CSS normalization
- Unicode support

**Performance**:
- Timeout: 60 seconds
- Additional wait for dynamic content: 5-10 seconds

---

### 7. URL to JPG

**Endpoint**: `POST /api/url2jpg`

**Description**: Generates screenshot of web page as JPG image

**Request**:
```http
POST /api/url2jpg?width=1920&height=1080 HTTP/1.1
Content-Type: text/plain

https://example.com
```

**Query Parameters**:
- `width` (optional): Screenshot width in pixels (default: 1920)
- `height` (optional): Screenshot height in pixels (default: 1080)

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Disposition: attachment; filename=screenshot.jpg

<JPG binary data>
```

**Response** (Error):
```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/plain

Playwright is required for url2jpg. Install with: playwright install chromium
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request (invalid URL)
- `500` - Internal Server Error (Playwright not available or screenshot failed)

**Features**:
- Full-page screenshots
- JavaScript rendering
- Custom viewport size
- JPEG quality: 90%

---

### 8. Swagger Documentation

**Endpoint**: `GET /api/swagger` or `GET /api/swagger/ui`

**Description**: Returns Swagger UI for interactive API documentation

**Request**:
```http
GET /api/swagger/ui HTTP/1.1
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: text/html

<Swagger UI HTML page>
```

**Features**:
- Interactive API testing
- Complete endpoint documentation
- Request/response examples
- Try it out functionality

---

## Error Responses

All endpoints follow consistent error response format:

**Format**:
```json
{
  "error": "Error message description"
}
```

Or plain text for some endpoints:
```
Error message description
```

**Common Error Codes**:
- `400 Bad Request` - Invalid input, missing required data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

Azure Functions automatically handles rate limiting based on:
- Function app plan (Consumption, Premium, Dedicated)
- Concurrent execution limits
- Timeout limits

## CORS

CORS can be configured in `host.json`:
```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[2.*, 3.0.0)"
  },
  "customHandler": {
    "enableForwardingHttpRequest": true
  }
}
```

## Content Types

Supported content types for each endpoint:

| Endpoint | Request Content-Type | Response Content-Type |
|----------|---------------------|----------------------|
| `/api/csv2json` | `text/csv`, `text/plain` | `application/json` |
| `/api/json2csv` | `application/json`, `text/plain` | `text/csv` |
| `/api/dbf2json` | `application/x-dbf`, `application/octet-stream` | `application/json` |
| `/api/md2html` | `text/markdown`, `text/plain` | `text/html` |
| `/api/html2pdf` | `text/html`, `text/plain` | `application/pdf` |
| `/api/url2pdf` | `text/plain` | `application/pdf` |
| `/api/url2jpg` | `text/plain` | `image/jpeg` |
| `/api/swagger` | N/A | `text/html` |

## Examples

### cURL Examples

**CSV to JSON**:
```bash
curl -X POST http://localhost:7071/api/csv2json \
  -H "Content-Type: text/csv" \
  -d "name,age\nJohn,25\nJane,30"
```

**JSON to CSV**:
```bash
curl -X POST http://localhost:7071/api/json2csv \
  -H "Content-Type: application/json" \
  -d '[{"name":"John","age":25},{"name":"Jane","age":30}]'
```

**URL to PDF**:
```bash
curl -X POST http://localhost:7071/api/url2pdf \
  -H "Content-Type: text/plain" \
  -d "https://example.com" \
  --output result.pdf
```

**URL to JPG**:
```bash
curl -X POST "http://localhost:7071/api/url2jpg?width=1920&height=1080" \
  -H "Content-Type: text/plain" \
  -d "https://example.com" \
  --output screenshot.jpg
```

### Python Examples

```python
import requests

# CSV to JSON
response = requests.post(
    'http://localhost:7071/api/csv2json',
    data='name,age\nJohn,25',
    headers={'Content-Type': 'text/csv'}
)
print(response.json())

# URL to PDF
response = requests.post(
    'http://localhost:7071/api/url2pdf',
    data='https://example.com',
    headers={'Content-Type': 'text/plain'}
)
with open('output.pdf', 'wb') as f:
    f.write(response.content)
```

### JavaScript Examples

```javascript
// CSV to JSON
fetch('http://localhost:7071/api/csv2json', {
  method: 'POST',
  headers: { 'Content-Type': 'text/csv' },
  body: 'name,age\nJohn,25'
})
.then(res => res.json())
.then(data => console.log(data));

// URL to PDF
fetch('http://localhost:7071/api/url2pdf', {
  method: 'POST',
  headers: { 'Content-Type': 'text/plain' },
  body: 'https://example.com'
})
.then(res => res.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  window.open(url);
});
```

