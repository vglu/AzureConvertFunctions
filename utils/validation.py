"""
Input validation utilities
"""
import json
import re
import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse
from .exceptions import ValidationError, SecurityError
from .config import Config


def validate_request_size(req_size: int) -> None:
    """
    Validate request size
    
    Args:
        req_size: Size of request in bytes
        
    Raises:
        ValidationError: If request size exceeds limit
    """
    if req_size > Config.MAX_REQUEST_SIZE:
        raise ValidationError(
            f"Request size ({req_size} bytes) exceeds maximum allowed size "
            f"({Config.MAX_REQUEST_SIZE} bytes)"
        )


def validate_csv_content(content: str) -> None:
    """
    Validate CSV content
    
    Args:
        content: CSV content string
        
    Raises:
        ValidationError: If CSV content is invalid
    """
    if not content:
        raise ValidationError("CSV content is empty")
    
    if len(content.encode('utf-8')) > Config.MAX_REQUEST_SIZE:
        raise ValidationError("CSV content exceeds maximum size")
    
    # Basic CSV validation - should have at least one line
    lines = content.strip().split('\n')
    if not lines or not lines[0]:
        raise ValidationError("CSV content must contain at least a header row")


def validate_json_content(content: str) -> None:
    """
    Validate JSON content
    
    Args:
        content: JSON content string
        
    Raises:
        ValidationError: If JSON content is invalid
    """
    if not content:
        raise ValidationError("JSON content is empty")
    
    if len(content.encode('utf-8')) > Config.MAX_REQUEST_SIZE:
        raise ValidationError("JSON content exceeds maximum size")
    
    try:
        data = json.loads(content)
        # Check for reasonable depth to prevent stack overflow
        _check_json_depth(data, max_depth=100)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")


def _check_json_depth(obj: any, max_depth: int, current_depth: int = 0) -> None:
    """Recursively check JSON depth"""
    if current_depth > max_depth:
        raise ValidationError("JSON structure is too deeply nested")
    
    if isinstance(obj, dict):
        for value in obj.values():
            _check_json_depth(value, max_depth, current_depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _check_json_depth(item, max_depth, current_depth + 1)


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL and check for SSRF vulnerabilities
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if not parsed.scheme:
            return False, "Missing URL scheme"
        
        if parsed.scheme not in Config.ALLOWED_URL_SCHEMES:
            return False, f"URL scheme '{parsed.scheme}' is not allowed. Only {Config.ALLOWED_URL_SCHEMES} are allowed"
        
        # Check hostname
        if not parsed.netloc:
            return False, "Missing URL host"
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Check for blocked hosts
        if hostname.lower() in [h.lower() for h in Config.BLOCKED_HOSTS]:
            return False, f"Host '{hostname}' is blocked for security reasons"
        
        # Check for private IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False, f"IP address '{hostname}' is private/local and not allowed"
            
            # Check against private IP ranges
            for ip_range in Config.PRIVATE_IP_RANGES:
                if ip in ipaddress.ip_network(ip_range, strict=False):
                    return False, f"IP address '{hostname}' is in blocked range '{ip_range}'"
        except ValueError:
            # Not an IP address, check if it's a blocked hostname pattern
            if any(blocked in hostname.lower() for blocked in ['localhost', '127.', '192.168.', '10.', '172.']):
                return False, f"Hostname '{hostname}' matches blocked pattern"
        
        # Check for Azure metadata service
        if '169.254.169.254' in hostname:
            return False, "Azure metadata service access is blocked"
        
        return True, None
        
    except Exception as e:
        return False, f"URL validation error: {str(e)}"


def validate_file_size(data: bytes) -> None:
    """
    Validate file size
    
    Args:
        data: File data in bytes
        
    Raises:
        ValidationError: If file size exceeds limit
    """
    if len(data) > Config.MAX_REQUEST_SIZE:
        raise ValidationError(
            f"File size ({len(data)} bytes) exceeds maximum allowed size "
            f"({Config.MAX_REQUEST_SIZE} bytes)"
        )


def validate_image_size(data: bytes) -> None:
    """
    Validate image size
    
    Args:
        data: Image data in bytes
        
    Raises:
        ValidationError: If image size exceeds limit
    """
    if len(data) > Config.MAX_IMAGE_SIZE:
        raise ValidationError(
            f"Image size ({len(data)} bytes) exceeds maximum allowed size "
            f"({Config.MAX_IMAGE_SIZE} bytes)"
        )


def validate_markdown_content(content: str) -> None:
    """
    Validate Markdown content
    
    Args:
        content: Markdown content string
        
    Raises:
        ValidationError: If Markdown content is invalid
    """
    if not content:
        raise ValidationError("Markdown content is empty")
    
    if len(content.encode('utf-8')) > Config.MAX_REQUEST_SIZE:
        raise ValidationError("Markdown content exceeds maximum size")


def validate_html_content(content: str) -> None:
    """
    Validate HTML content
    
    Args:
        content: HTML content string
        
    Raises:
        ValidationError: If HTML content is invalid
    """
    if not content:
        raise ValidationError("HTML content is empty")
    
    if len(content.encode('utf-8')) > Config.MAX_REQUEST_SIZE:
        raise ValidationError("HTML content exceeds maximum size")

