"""
HTML to PDF converter
"""
from typing import Optional
from io import BytesIO
from xhtml2pdf import pisa
import logging
from utils.exceptions import ProcessingError
from utils.fonts import register_fonts


def convert_html_to_pdf(html_content: str, font_family: Optional[str] = None) -> bytes:
    """
    Convert HTML string to PDF bytes
    
    Args:
        html_content: HTML content as string
        font_family: Optional font family to use (if None, will register fonts)
        
    Returns:
        PDF file as bytes
        
    Raises:
        ProcessingError: If conversion fails
    """
    try:
        # Register fonts if not already registered
        if font_family is None:
            css_font_name = register_fonts()
            if css_font_name is None:
                css_font_name = 'Arial'
            font_family = "Helvetica, Arial, sans-serif"  # Helvetica will be mapped to registered font
        else:
            font_family = font_family
        
        # Check if HTML already has full structure
        html_lower = html_content.lower().strip()
        has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
        
        if has_html_tag:
            # If HTML is already complete, add or update styles
            if '<head>' not in html_lower:
                # Insert head with styles after opening html tag
                html_content = html_content.replace('<html>', f'''<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ margin: 2cm; }}
        * {{ font-family: {font_family} !important; }}
        body {{ font-family: {font_family}; font-size: 12pt; line-height: 1.6; }}
        h1 {{ font-family: {font_family}; font-size: 24pt; margin-bottom: 10pt; }}
        p {{ font-family: {font_family}; margin-bottom: 8pt; }}
    </style>
</head>''', 1)
            elif '<style>' in html_lower:
                # If styles already exist, add font-family everywhere
                html_content = html_content.replace(
                    'body {', f'body {{ font-family: {font_family} !important;'
                )
            full_html = html_content
        else:
            # Wrap HTML in basic structure with Unicode support
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            margin: 2cm;
        }}
        * {{
            font-family: {font_family} !important;
        }}
        body {{
            font-family: {font_family};
            font-size: 12pt;
            line-height: 1.6;
        }}
        h1 {{
            font-family: {font_family};
            font-size: 24pt;
            margin-bottom: 10pt;
        }}
        p {{
            font-family: {font_family};
            margin-bottom: 8pt;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # Convert HTML to PDF using xhtml2pdf
        pdf_buffer = BytesIO()
        
        # Create PDF from HTML with correct encoding and settings
        pisa_status = pisa.CreatePDF(
            src=full_html,
            dest=pdf_buffer,
            encoding='utf-8',
            link_callback=None,
            show_error_as_pdf=False
        )
        
        # Log warnings
        if pisa_status.warn:
            try:
                if hasattr(pisa_status.warn, '__iter__') and not isinstance(pisa_status.warn, (str, bytes)):
                    for warning in pisa_status.warn:
                        logging.warning(f'PISA warning: {warning}')
                else:
                    logging.warning(f'PISA warning: {pisa_status.warn}')
            except (TypeError, AttributeError):
                pass
        
        # Check for errors
        if pisa_status.err:
            error_msg = str(pisa_status.err)
            logging.error(f'Error creating PDF: {error_msg}')
            raise ProcessingError(f"Error converting HTML to PDF: {error_msg}")
        
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        
        return pdf_bytes
    except ProcessingError:
        raise
    except Exception as e:
        raise ProcessingError(f"Failed to convert HTML to PDF: {str(e)}") from e

