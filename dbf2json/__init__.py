"""
DBF to JSON conversion Azure Function
"""
import logging
import json
import azure.functions as func
from dbfread import DBF
from utils.exceptions import ValidationError, ProcessingError
from utils.validation import validate_file_size
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.file_utils import temporary_file


def convert_dbf_to_json(dbf_data: bytes) -> str:
    """
    Convert DBF file data to JSON string
    
    Args:
        dbf_data: DBF file data as bytes
        
    Returns:
        JSON string with records
        
    Raises:
        ProcessingError: If conversion fails
    """
    with temporary_file(suffix='.dbf') as temp_path:
        try:
            # Write DBF data to temporary file
            with open(temp_path, 'wb') as f:
                f.write(dbf_data)
            
            # Read DBF file
            table = DBF(temp_path, encoding='utf-8', load=True)
            
            # Convert to list of dictionaries
            records = []
            for record in table:
                # Convert record to dictionary, handling different data types
                record_dict = {}
                for field_name in record.keys():
                    value = record[field_name]
                    # Convert None to null for JSON
                    if value is None:
                        record_dict[field_name] = None
                    # Keep other types as is (strings, numbers, dates)
                    else:
                        record_dict[field_name] = value
                records.append(record_dict)
            
            # Convert to JSON
            json_result = json.dumps(records, ensure_ascii=False, indent=2, default=str)
            
            return json_result
        except Exception as e:
            raise ProcessingError(f"Failed to convert DBF to JSON: {str(e)}") from e


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert DBF file data to JSON format.
    
    Args:
        req: Azure Function HTTP request containing DBF file data in body
        
    Returns:
        HTTP response with JSON data (200) or error message (400/500)
        
    Example:
        Request body: Binary DBF file data
        Response: [{"field1": "value1", "field2": 123}, ...]
    """
    context = create_logger_context(req, 'dbf2json')
    log_function_start(logging, context, 'DBF2JSON function processing request.')
    
    try:
        # Get DBF file data from request body
        dbf_data = req.get_body()
        
        if not dbf_data:
            raise ValidationError("DBF file not provided")
        
        # Validate file size
        try:
            validate_file_size(dbf_data)
        except ValidationError as e:
            log_function_error(logging, context, e, 'File size validation failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        
        # Convert DBF to JSON
        try:
            json_result = convert_dbf_to_json(dbf_data)
        except ProcessingError as e:
            log_function_error(logging, context, e, 'DBF to JSON conversion failed')
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=500
            )
        
        log_function_success(logging, context, 'DBF2JSON function completed successfully')
        
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
