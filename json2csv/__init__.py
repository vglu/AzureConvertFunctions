import logging
import json
import pandas as pd
import azure.functions as func
from io import StringIO


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('JSON2CSV function processing request.')

    try:
        # Get JSON data from request body
        json_content = req.get_body().decode('utf-8')
        
        if not json_content:
            return func.HttpResponse(
                "JSON content not provided",
                status_code=400
            )

        # Parse JSON
        data = json.loads(json_content)
        
        # Create DataFrame from JSON
        # If it's a list of dictionaries (array of objects)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        # If it's a single object
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            return func.HttpResponse(
                "Invalid JSON format. Expected object or array of objects.",
                status_code=400
            )
        
        # Convert to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_result = csv_buffer.getvalue()
        
        return func.HttpResponse(
            csv_result,
            mimetype="text/csv",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=converted.csv"
            }
        )
    
    except json.JSONDecodeError as e:
        logging.error(f'JSON parsing error: {str(e)}')
        return func.HttpResponse(
            f"JSON parsing error: {str(e)}",
            status_code=400
        )
    except Exception as e:
        logging.error(f'Error converting JSON to CSV: {str(e)}')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )

