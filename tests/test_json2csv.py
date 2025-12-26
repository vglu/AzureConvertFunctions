"""
Test cases for json2csv function
"""
import pytest
import json
from json2csv import __init__ as json2csv_func


class MockRequest:
    """Mock HTTP request for testing"""
    def __init__(self, body: bytes, headers: dict = None):
        self._body = body
        self._headers = headers or {}
        self.method = 'POST'
        self.url = 'http://localhost:7071/api/json2csv'
        self.route_params = {}
        self.params = {}
    
    def get_body(self) -> bytes:
        return self._body
    
    def headers(self):
        return self._headers
    
    def get(self, key: str, default=None):
        return self._headers.get(key, default)


def test_json2csv_success():
    """Test successful JSON to CSV conversion"""
    json_data = [{"name": "John", "age": 25, "city": "New York"}, {"name": "Jane", "age": 30, "city": "London"}]
    req = MockRequest(json.dumps(json_data).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    csv_content = response.get_body().decode('utf-8')
    assert "name,age,city" in csv_content
    assert "John,25,New York" in csv_content


def test_json2csv_empty_body():
    """Test handling of empty request body"""
    req = MockRequest(b"")
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 400
    response_body = json.loads(response.get_body())
    assert "error" in response_body


def test_json2csv_invalid_json():
    """Test handling of invalid JSON"""
    req = MockRequest(b"{invalid json}")
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 400
    response_body = json.loads(response.get_body())
    assert "error" in response_body


def test_json2csv_single_object():
    """Test conversion of single JSON object"""
    json_data = {"name": "John", "age": 25}
    req = MockRequest(json.dumps(json_data).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 200
    csv_content = response.get_body().decode('utf-8')
    assert "name,age" in csv_content
    assert "John,25" in csv_content


def test_json2csv_empty_array():
    """Test handling of empty JSON array"""
    req = MockRequest(json.dumps([]).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    # Should return error for empty array
    assert response.status_code in [400, 500]
