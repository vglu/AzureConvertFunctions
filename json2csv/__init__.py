"""
JSON to CSV conversion Azure Function
"""
import logging
import json
import azure.functions as func
from utils.exceptions import ValidationError, ProcessingError
from utils.validation import validate_request_size, validate_json_content
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from .converter import convert_json_to_csv


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert JSON data to CSV format.
    
    Args:
        req: Azure Function HTTP request containing JSON data in body
        
    Returns:
        HTTP response with CSV data (200) or error message (400/500)
        
    Example:
        Request body: [{"name": "John", "age": 25}]
        Response: "name,age\\nJohn,25"
    """
    context = create_logger_context(req, 'json2csv')
    log_function_start(logging, context, 'JSON2CSV function processing request.')
    
    try:
        # Get and validate request size
        content_length = req.headers.get('Content-Length')
        if content_length:
            try:
                validate_request_size(int(content_length))
            except ValidationError as e:
                log_function_error(logging, context, e, 'Request size validation failed')
                return func.HttpResponse(
                    json.dumps({"error": str(e)}),
                    mimetype="application/json",
                    status_code=400
                )
        
        # Get JSON data from request body
        req_body = req.get_body()
        validate_request_size(len(req_body))
        
        json_content = decode_request_body(req_body)
        
        # Validate JSON content
        try:
            validate_json_content(json_content)
        except ValidationError as e:
            log_function_error(logging, context, e, 'JSON validation failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        
        # Convert JSON to CSV
        try:
            csv_result = convert_json_to_csv(json_content)
        except ValidationError as e:
            log_function_error(logging, context, e, 'JSON format validation failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        except ProcessingError as e:
            log_function_error(logging, context, e, 'JSON to CSV conversion failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
        
        log_function_success(logging, context, 'JSON2CSV function completed successfully')
        
        return func.HttpResponse(
            csv_result,
            mimetype="text/csv",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=converted.csv"
            }
        )
    
    except ValidationError as e:
        log_function_error(logging, context, e, 'Validation error')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
    except ProcessingError as e:
        log_function_error(logging, context, e, 'Processing error')
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
    except Exception as e:
        log_function_error(logging, context, e, 'Unexpected error')
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            mimetype="application/json",
            status_code=500
        )
