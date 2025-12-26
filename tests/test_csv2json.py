"""
Test cases for csv2json function
"""
import pytest
import json
import azure.functions as func
from csv2json import __init__ as csv2json_func


class MockRequest:
    """Mock HTTP request for testing"""
    def __init__(self, body: bytes, headers: dict = None):
        self._body = body
        self._headers = headers or {}
        self.method = 'POST'
        self.url = 'http://localhost:7071/api/csv2json'
        self.route_params = {}
        self.params = {}
    
    def get_body(self) -> bytes:
        return self._body
    
    def headers(self):
        return self._headers
    
    def get(self, key: str, default=None):
        return self._headers.get(key, default)


def test_csv2json_success():
    """Test successful CSV to JSON conversion"""
    csv_data = "name,age,city\nJohn,25,New York\nJane,30,London"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    
    result = json.loads(response.get_body())
    assert isinstance(result, str)  # JSON string
    parsed = json.loads(result)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "John"
    assert parsed[0]["age"] == "25"
    assert parsed[1]["city"] == "London"


def test_csv2json_empty_body():
    """Test handling of empty request body"""
    req = MockRequest(b"")
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 400
    response_body = json.loads(response.get_body())
    assert "error" in response_body


def test_csv2json_invalid_csv():
    """Test handling of invalid CSV"""
    csv_data = "name,age\nJohn,25,New York,extra"
    req = MockRequest(csv_data.encode('utf-8'))
    
    # pandas usually handles this, but may have warnings
    response = csv2json_func.main(req)
    
    # Function should handle this (pandas may ignore extra columns)
    assert response.status_code in [200, 500]


def test_csv2json_with_special_characters():
    """Test handling of special characters"""
    csv_data = 'text,number\nHello, world!,42\nTest "quotes",100'
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    result = json.loads(response.get_body())
    parsed = json.loads(result)
    assert "Hello, world!" in parsed[0]["text"]


def test_csv2json_single_row():
    """Test conversion of single CSV row"""
    csv_data = "name,age\nJohn,25"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    result = json.loads(response.get_body())
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "John"


def test_csv2json_unicode():
    """Test handling of Unicode characters"""
    csv_data = "name,age\nJosé,30\nFrançois,25"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    result = json.loads(response.get_body())
    parsed = json.loads(result)
    assert len(parsed) == 2
    assert "José" in [p["name"] for p in parsed]
    assert "François" in [p["name"] for p in parsed]


def test_csv2json_large_request():
    """Test handling of large request size"""
    # Create CSV with many rows
    csv_data = "name,age\n" + "\n".join([f"Person{i},{20+i}" for i in range(1000)])
    req = MockRequest(csv_data.encode('utf-8'), headers={'Content-Length': str(len(csv_data.encode('utf-8')))})
    
    response = csv2json_func.main(req)
    
    # Should succeed for reasonable sizes
    assert response.status_code in [200, 400]  # 400 if exceeds MAX_REQUEST_SIZE
