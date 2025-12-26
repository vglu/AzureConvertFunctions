"""
HTML to PDF conversion Azure Function
"""
import logging
import azure.functions as func
from utils.exceptions import ValidationError, ProcessingError
from utils.validation import validate_request_size, validate_html_content
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from .converter import convert_html_to_pdf


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert HTML data to PDF format.
    
    Args:
        req: Azure Function HTTP request containing HTML data in body
        
    Returns:
        HTTP response with PDF file (200) or error message (400/500)
        
    Example:
        Request body: "<h1>Hello</h1><p>World</p>"
        Response: PDF file bytes
    """
    context = create_logger_context(req, 'html2pdf')
    log_function_start(logging, context, 'HTML2PDF function processing request.')
    
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
        
        # Get HTML data from request body
        req_body = req.get_body()
        validate_request_size(len(req_body))
        
        html_content = decode_request_body(req_body)
        
        # Validate HTML content
        try:
            validate_html_content(html_content)
        except ValidationError as e:
            log_function_error(logging, context, e, 'HTML validation failed')
            return func.HttpResponse(
                f"Validation error: {str(e)}",
                status_code=400
            )
        
        # Convert HTML to PDF
        try:
            pdf_bytes = convert_html_to_pdf(html_content)
        except ProcessingError as e:
            log_function_error(logging, context, e, 'HTML to PDF conversion failed')
            return func.HttpResponse(
                f"Conversion error: {str(e)}",
                status_code=500
            )
        
        log_function_success(logging, context, 'HTML2PDF function completed successfully')
        
        return func.HttpResponse(
            pdf_bytes,
            mimetype="application/pdf",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=converted.pdf"
            }
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
