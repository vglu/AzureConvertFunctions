"""
CSV to JSON conversion Azure Function
"""
import logging
import json
import azure.functions as func
from typing import Optional
from utils.exceptions import ValidationError, ProcessingError
from utils.validation import validate_request_size, validate_csv_content
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from .converter import convert_csv_to_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert CSV data to JSON format.
    
    Args:
        req: Azure Function HTTP request containing CSV data in body
        
    Returns:
        HTTP response with JSON data (200) or error message (400/500)
        
    Example:
        Request body: "name,age\\nJohn,25"
        Response: [{"name": "John", "age": "25"}]
    """
    context = create_logger_context(req, 'csv2json')
    log_function_start(logging, context, 'CSV2JSON function processing request.')
    
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
        
        # Get CSV data from request body
        req_body = req.get_body()
        validate_request_size(len(req_body))
        
        csv_content = decode_request_body(req_body)
        
        # Validate CSV content
        try:
            validate_csv_content(csv_content)
        except ValidationError as e:
            log_function_error(logging, context, e, 'CSV validation failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        
        # Convert CSV to JSON
        try:
            json_result = convert_csv_to_json(csv_content)
        except ProcessingError as e:
            log_function_error(logging, context, e, 'CSV to JSON conversion failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
        
        log_function_success(logging, context, 'CSV2JSON function completed successfully')
        
        return func.HttpResponse(
            json_result,
            mimetype="application/json",
            status_code=200
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
