"""
Test cases for dbf2json function
"""
import pytest
import json
from dbf2json import __init__ as dbf2json_func


class MockRequest:
    """Mock HTTP request for testing"""
    def __init__(self, body: bytes, headers: dict = None):
        self._body = body
        self._headers = headers or {}
        self.method = 'POST'
        self.url = 'http://localhost:7071/api/dbf2json'
        self.route_params = {}
        self.params = {}
    
    def get_body(self) -> bytes:
        return self._body
    
    def headers(self):
        return self._headers
    
    def get(self, key: str, default=None):
        return self._headers.get(key, default)


def test_dbf2json_empty_body():
    """Test with empty request body"""
    req = MockRequest(b'')
    response = dbf2json_func.main(req)
    
    assert response.status_code == 400
    body = json.loads(response.get_body().decode('utf-8'))
    assert "error" in body
    assert "not provided" in body["error"].lower()


def test_dbf2json_invalid_dbf():
    """Test with invalid DBF data"""
    req = MockRequest(b'Invalid DBF data')
    response = dbf2json_func.main(req)
    
    # Should return 500 error for invalid DBF
    assert response.status_code == 500
    body = json.loads(response.get_body().decode('utf-8'))
    assert "error" in body


def test_dbf2json_binary_data():
    """Test that function accepts binary data"""
    # Create minimal binary data (not valid DBF, but tests binary handling)
    binary_data = b'\x00' * 100
    req = MockRequest(binary_data)
    response = dbf2json_func.main(req)
    
    # Should attempt to process and fail with invalid format
    assert response.status_code in [400, 500]


def test_dbf2json_large_file():
    """Test handling of large file size"""
    # Create large binary data
    binary_data = b'\x00' * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
    req = MockRequest(binary_data, headers={'Content-Length': str(len(binary_data))})
    response = dbf2json_func.main(req)
    
    # Should return 400 if exceeds MAX_REQUEST_SIZE
    assert response.status_code == 400
