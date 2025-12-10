import logging
import json
import os
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Swagger UI function processing request.')

    try:
        # Get path from request
        path = req.route_params.get('restOfPath', '')
        
        # If swagger.json is requested
        if path == 'swagger.json':
            # Read swagger.json file
            swagger_path = os.path.join(os.path.dirname(__file__), '..', 'swagger.json')
            
            with open(swagger_path, 'r', encoding='utf-8') as f:
                swagger_content = json.load(f)
            
            # Update server URL based on request
            host = req.headers.get('Host', 'localhost:7071')
            scheme = 'https' if 'azurewebsites.net' in host else 'http'
            swagger_content['servers'] = [
                {
                    "url": f"{scheme}://{host}/api",
                    "description": "Current server"
                }
            ]
            
            return func.HttpResponse(
                json.dumps(swagger_content, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=200
            )
        
        # For all other paths return Swagger UI HTML
        return get_swagger_ui_html()
    
    except FileNotFoundError:
        logging.error('swagger.json file not found')
        return func.HttpResponse(
            "Swagger specification not found",
            status_code=404
        )
    except Exception as e:
        logging.error(f'Error processing Swagger request: {str(e)}')
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )


def get_swagger_ui_html():
    """Generates HTML page with Swagger UI"""
    
    # Determine URL for swagger.json
    swagger_json_url = "/api/swagger/swagger.json"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure Convert Functions API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "{swagger_json_url}",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                tryItOutEnabled: true
            }});
        }};
    </script>
</body>
</html>"""
    
    return func.HttpResponse(
        html_content,
        mimetype="text/html",
        status_code=200
    )

