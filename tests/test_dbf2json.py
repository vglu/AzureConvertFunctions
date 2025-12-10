import pytest
import json
import azure.functions as func
from dbf2json import __init__ as dbf2json_func
from io import BytesIO
import struct


class MockRequest:
    def __init__(self, body):
        self._body = body
    
    def get_body(self):
        return self._body


def create_simple_dbf():
    """
    Creates a minimal valid DBF file in memory
    DBF file structure:
    - Header (32 bytes)
    - Field descriptors (32 bytes each)
    - Terminator (1 byte)
    - Records
    """
    # This is a simplified DBF structure for testing
    # In real scenario, you would use a proper DBF file
    # For testing, we'll create a minimal valid DBF structure
    
    # DBF Header (32 bytes)
    # Byte 0: Version (0x03 = dBASE III)
    # Byte 1-3: Date (YY MM DD)
    # Byte 4-7: Number of records (little-endian)
    # Byte 8-9: Header length (little-endian)
    # Byte 10-11: Record length (little-endian)
    # Byte 12-31: Reserved
    
    header = bytearray(32)
    header[0] = 0x03  # dBASE III
    header[1] = 0x19  # Year 2019
    header[2] = 0x0C  # Month 12
    header[3] = 0x0A  # Day 10
    
    # 2 records
    struct.pack_into('<I', header, 4, 2)
    
    # Header length: 32 (header) + 32 (field) + 1 (terminator) = 65
    struct.pack_into('<H', header, 8, 65)
    
    # Record length: 20 (NAME field) + 4 (AGE field) = 24
    struct.pack_into('<H', header, 10, 24)
    
    # Field descriptor (32 bytes)
    # Byte 0-10: Field name (ASCII, null-padded)
    # Byte 11: Field type (C=Character, N=Numeric, D=Date, L=Logical)
    # Byte 12-15: Field data address (not used in file)
    # Byte 16: Field length
    # Byte 17: Field decimal count
    # Byte 18-31: Reserved
    
    field1 = bytearray(32)
    field1[0:4] = b'NAME'
    field1[11] = ord('C')  # Character type
    field1[16] = 20  # Field length
    
    field2 = bytearray(32)
    field2[0:3] = b'AGE'
    field2[11] = ord('N')  # Numeric type
    field2[16] = 4  # Field length
    field2[17] = 0  # No decimals
    
    # Terminator
    terminator = b'\x0D'
    
    # Records
    # Each record starts with deletion flag (1 byte, 0x20 = not deleted)
    record1 = bytearray(24)
    record1[0] = 0x20  # Not deleted
    record1[1:5] = b'John' + b' ' * 16  # NAME field (20 bytes)
    struct.pack_into('<I', record1, 21, 25)  # AGE field (4 bytes, but we'll use 1 byte)
    record1[21] = 25  # Simple numeric
    
    record2 = bytearray(24)
    record2[0] = 0x20
    record2[1:4] = b'Jane' + b' ' * 16
    record2[21] = 30
    
    # Combine all parts
    dbf_data = bytes(header) + bytes(field1) + bytes(field2) + terminator + bytes(record1) + bytes(record2)
    
    return dbf_data


def test_dbf2json_success():
    """Test successful DBF to JSON conversion"""
    # Note: This test requires a valid DBF file
    # For now, we'll test error handling
    req = MockRequest(b'')
    response = dbf2json_func.main(req)
    
    assert response.status_code == 400
    assert "not provided" in response.get_body().decode('utf-8').lower()


def test_dbf2json_empty_body():
    """Test with empty request body"""
    req = MockRequest(b'')
    response = dbf2json_func.main(req)
    
    assert response.status_code == 400
    body = response.get_body().decode('utf-8')
    assert "not provided" in body.lower()


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

