import logging
import json
import azure.functions as func
from io import BytesIO
from dbfread import DBF


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DBF2JSON function processing request.')

    try:
        # Get DBF file data from request body
        dbf_data = req.get_body()

        if not dbf_data:
            return func.HttpResponse(
                "DBF file not provided",
                status_code=400
            )

        # Create BytesIO object from binary data
        dbf_buffer = BytesIO(dbf_data)

        # Save to temporary file (DBF library requires file path)
        import tempfile
        import os
        
        temp_file = None
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dbf')
            temp_file.write(dbf_data)
            temp_file.close()

            # Read DBF file
            table = DBF(temp_file.name, encoding='utf-8', load=True)

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

            return func.HttpResponse(
                json_result,
                mimetype="application/json",
                status_code=200
            )

        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logging.warning(f'Failed to delete temp file: {e}')

    except Exception as e:
        logging.error(f'Error converting DBF to JSON: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": f"Conversion error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )



