import logging
import json
import pandas as pd
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('CSV2JSON function processing request.')

    try:
        # Get CSV data from request body
        csv_content = req.get_body().decode('utf-8')
        
        if not csv_content:
            return func.HttpResponse(
                "CSV content not provided",
                status_code=400
            )

        # Use StringIO to read CSV from string
        from io import StringIO
        csv_buffer = StringIO(csv_content)
        
        # Read CSV into DataFrame
        df = pd.read_csv(csv_buffer)
        
        # Convert to JSON (records-oriented)
        json_result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        return func.HttpResponse(
            json_result,
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f'Error converting CSV to JSON: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Conversion error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )

