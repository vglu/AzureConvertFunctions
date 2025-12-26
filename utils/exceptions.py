"""
Custom exceptions for Azure Convert Functions
"""


class ConversionError(Exception):
    """Base exception for conversion errors"""
    pass


class ValidationError(ConversionError):
    """Input validation error"""
    pass


class ProcessingError(ConversionError):
    """Processing/conversion error"""
    pass


class ExternalServiceError(ConversionError):
    """External service (Playwright, requests) error"""
    pass


class TimeoutError(ConversionError):
    """Operation timeout error"""
    pass


class SecurityError(ConversionError):
    """Security-related error (SSRF, invalid input, etc.)"""
    pass

