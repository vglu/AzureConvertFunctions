"""
Markdown to HTML converter
"""
import markdown
import bleach
from typing import List
from utils.exceptions import ProcessingError

# Allowed HTML tags for sanitization
ALLOWED_HTML_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'ul', 'ol', 'li', 'a',
    'code', 'pre', 'table', 'thead', 'tbody',
    'tr', 'td', 'th', 'blockquote', 'img'
]

# Allowed attributes for sanitization
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title']
}


def convert_markdown_to_html(md_content: str, sanitize: bool = False) -> str:
    """
    Convert Markdown string to HTML string
    
    Args:
        md_content: Markdown content as string
        sanitize: Whether to sanitize HTML output (default: False)
        
    Returns:
        Full HTML document as string
        
    Raises:
        ProcessingError: If conversion fails
    """
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables']
        )
        
        # Sanitize HTML if requested
        if sanitize:
            html_content = bleach.clean(
                html_content,
                tags=ALLOWED_HTML_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True
            )
        
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
        
        return full_html
    except Exception as e:
        raise ProcessingError(f"Failed to convert Markdown to HTML: {str(e)}") from e

