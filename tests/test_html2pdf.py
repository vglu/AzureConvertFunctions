"""
Test cases for html2pdf function
"""
import pytest
from html2pdf import __init__ as html2pdf_func


class MockRequest:
    """Mock HTTP request for testing"""
    def __init__(self, body: bytes, headers: dict = None):
        self._body = body
        self._headers = headers or {}
        self.method = 'POST'
        self.url = 'http://localhost:7071/api/html2pdf'
        self.route_params = {}
        self.params = {}
    
    def get_body(self) -> bytes:
        return self._body
    
    def headers(self):
        return self._headers
    
    def get(self, key: str, default=None):
        return self._headers.get(key, default)


def test_html2pdf_success():
    """Test successful HTML to PDF conversion"""
    html_data = "<html><body><h1>Test</h1><p>Hello, world!</p></body></html>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    
    # Check that response contains valid PDF (starts with %PDF)
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_empty_body():
    """Test handling of empty request body"""
    req = MockRequest(b"")
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 400
    assert "error" in response.get_body().decode('utf-8').lower()


def test_html2pdf_simple_html():
    """Test conversion of simple HTML"""
    html_data = "<h1>Title</h1><p>Paragraph with <strong>bold</strong> text.</p>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_with_styles():
    """Test conversion of HTML with styles"""
    html_data = """
    <html>
    <head>
        <style>
            body { font-family: Arial; }
            h1 { color: blue; }
        </style>
    </head>
    <body>
        <h1>Title</h1>
        <p>Text</p>
    </body>
    </html>
    """
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_with_unicode():
    """Test conversion of HTML with Unicode characters"""
    html_data = "<html><body><p>Hello, world! 🌍</p></body></html>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_invalid_html():
    """Test handling of invalid HTML (xhtml2pdf may handle it)"""
    html_data = "<html><body><p>Unclosed tag"
    req = MockRequest(html_data.encode('utf-8'))
    
    # xhtml2pdf may handle invalid HTML
    response = html2pdf_func.main(req)
    
    # May be successful (xhtml2pdf fixes) or error
    assert response.status_code in [200, 500]
