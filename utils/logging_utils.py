"""
Logging utilities for structured logging
"""
import logging
import uuid
from typing import Dict, Any, Optional
import azure.functions as func


def create_logger_context(req: func.HttpRequest, function_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create logging context from request
    
    Args:
        req: Azure Function HTTP request
        function_name: Optional function name override
        
    Returns:
        Dictionary with logging context
    """
    context = {
        'request_id': str(uuid.uuid4()),
        'function_name': function_name or req.route_params.get('function_name', 'unknown'),
        'method': req.method,
        'url': req.url,
    }
    
    # Add user agent if available
    user_agent = req.headers.get('User-Agent')
    if user_agent:
        context['user_agent'] = user_agent
    
    # Add content length if available
    content_length = req.headers.get('Content-Length')
    if content_length:
        try:
            context['content_length'] = int(content_length)
        except ValueError:
            pass
    
    return context


def log_function_start(logger: logging.Logger, context: Dict[str, Any], message: str = "Function started"):
    """Log function start with context"""
    logger.info(message, extra=context)


def log_function_success(logger: logging.Logger, context: Dict[str, Any], message: str = "Function completed successfully"):
    """Log function success with context"""
    logger.info(message, extra=context)


def log_function_error(logger: logging.Logger, context: Dict[str, Any], error: Exception, message: str = "Function failed"):
    """Log function error with context"""
    logger.error(message, extra={**context, 'error': str(error), 'error_type': type(error).__name__}, exc_info=True)

