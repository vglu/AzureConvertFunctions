"""
Markdown to HTML conversion Azure Function
"""
import logging
import azure.functions as func
from utils.exceptions import ValidationError, ProcessingError
from utils.validation import validate_request_size, validate_markdown_content
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from .converter import convert_markdown_to_html


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert Markdown data to HTML format.
    
    Args:
        req: Azure Function HTTP request containing Markdown data in body
        
    Returns:
        HTTP response with HTML document (200) or error message (400/500)
        
    Example:
        Request body: "# Hello\\n\\nThis is **bold** text"
        Response: Full HTML document with converted Markdown
    """
    context = create_logger_context(req, 'md2html')
    log_function_start(logging, context, 'MD2HTML function processing request.')
    
    try:
        # Get and validate request size
        content_length = req.headers.get('Content-Length')
        if content_length:
            try:
                validate_request_size(int(content_length))
            except ValidationError as e:
                log_function_error(logging, context, e, 'Request size validation failed')
                return func.HttpResponse(
                    f"Validation error: {str(e)}",
                    status_code=400
                )
        
        # Get Markdown data from request body
        req_body = req.get_body()
        validate_request_size(len(req_body))
        
        md_content = decode_request_body(req_body)
        
        # Validate Markdown content
        try:
            validate_markdown_content(md_content)
        except ValidationError as e:
            log_function_error(logging, context, e, 'Markdown validation failed')
            return func.HttpResponse(
                f"Validation error: {str(e)}",
                status_code=400
            )
        
        # Convert Markdown to HTML
        try:
            # Check if sanitization is requested via query parameter
            sanitize = req.params.get('sanitize', 'false').lower() == 'true'
            full_html = convert_markdown_to_html(md_content, sanitize=sanitize)
        except ProcessingError as e:
            log_function_error(logging, context, e, 'Markdown to HTML conversion failed')
            return func.HttpResponse(
                f"Conversion error: {str(e)}",
                status_code=500
            )
        
        log_function_success(logging, context, 'MD2HTML function completed successfully')
        
        return func.HttpResponse(
            full_html,
            mimetype="text/html",
            status_code=200
        )
    
    except ValidationError as e:
        log_function_error(logging, context, e, 'Validation error')
        return func.HttpResponse(
            f"Validation error: {str(e)}",
            status_code=400
        )
    except ProcessingError as e:
        log_function_error(logging, context, e, 'Processing error')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )
    except Exception as e:
        log_function_error(logging, context, e, 'Unexpected error')
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )
