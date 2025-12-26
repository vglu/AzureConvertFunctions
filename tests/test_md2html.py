"""
Test cases for md2html function
"""
import pytest
from md2html import __init__ as md2html_func


class MockRequest:
    """Mock HTTP request for testing"""
    def __init__(self, body: bytes, headers: dict = None, params: dict = None):
        self._body = body
        self._headers = headers or {}
        self._params = params or {}
        self.method = 'POST'
        self.url = 'http://localhost:7071/api/md2html'
        self.route_params = {}
    
    def get_body(self) -> bytes:
        return self._body
    
    def headers(self):
        return self._headers
    
    def headers(self):
        return self._headers
    
    def get(self, key: str, default=None):
        return self._headers.get(key, default)
    
    def params(self):
        return self._params


def test_md2html_success():
    """Test successful Markdown to HTML conversion"""
    md_data = "# Hello\n\nThis is **bold** text"
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    html_content = response.get_body().decode('utf-8')
    assert "<h1>Hello</h1>" in html_content
    assert "<strong>bold</strong>" in html_content


def test_md2html_empty_body():
    """Test handling of empty request body"""
    req = MockRequest(b"")
    
    response = md2html_func.main(req)
    
    assert response.status_code == 400


def test_md2html_with_tables():
    """Test Markdown with tables"""
    md_data = "| Name | Age |\n|------|-----|\n| John | 25  |"
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    assert "<table>" in html_content
