import logging
import markdown
import bleach
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MD2HTML function processing request.')

    try:
        # Get Markdown data from request body
        md_content = req.get_body().decode('utf-8')
        
        if not md_content:
            return func.HttpResponse(
                "Markdown content not provided",
                status_code=400
            )

        # Convert Markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables']
        )
        
        # Clean HTML from potentially dangerous tags (optional, for security)
        # Can be commented out if all HTML tags are needed
        # html_content = bleach.clean(html_content, tags=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        #                                                  'strong', 'em', 'ul', 'ol', 'li', 'a', 
        #                                                  'code', 'pre', 'table', 'thead', 'tbody', 
        #                                                  'tr', 'td', 'th', 'blockquote'])
        
        # Wrap in basic HTML structure
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Markdown</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        return func.HttpResponse(
            full_html,
            mimetype="text/html",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f'Error converting Markdown to HTML: {str(e)}')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )

