"""
Encoding detection and handling utilities
"""
from typing import Optional
import chardet


def detect_encoding(data: bytes) -> str:
    """
    Detect encoding of byte data
    
    Args:
        data: Byte data to analyze
        
    Returns:
        Detected encoding name
    """
    try:
        result = chardet.detect(data)
        encoding = result.get('encoding')
        if encoding and encoding.lower() != 'ascii':
            return encoding
    except Exception:
        pass
    
    return 'utf-8'


def decode_request_body(req_body: bytes, encoding: Optional[str] = None) -> str:
    """
    Decode request body with automatic encoding detection
    
    Args:
        req_body: Request body as bytes
        encoding: Optional encoding to use (if None, will auto-detect)
        
    Returns:
        Decoded string
    """
    # Try specified encoding first
    if encoding:
        try:
            return req_body.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    
    # Try UTF-8 first (most common)
    try:
        return req_body.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # Try to detect encoding
    detected_encoding = detect_encoding(req_body)
    try:
        return req_body.decode(detected_encoding)
    except (UnicodeDecodeError, LookupError):
        # Fallback to UTF-8 with error handling
        return req_body.decode('utf-8', errors='replace')

