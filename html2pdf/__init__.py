import logging
import azure.functions as func
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os

# Флаг для регистрации шрифтов один раз
_fonts_registered = False


def register_fonts():
    """Registers fonts for Unicode and Cyrillic support"""
    global _fonts_registered
    
    if _fonts_registered:
        return 'Arial'  # Return font name for CSS
    
    try:
        # Try to use system fonts with Unicode support (cross-platform)
        font_configs = []
        
        # Windows fonts
        if os.name == 'nt':
            font_configs = [
                (r'C:\Windows\Fonts\arial.ttf', 'Arial', 'Arial'),
                (r'C:\Windows\Fonts\arialuni.ttf', 'ArialUnicode', 'Arial'),  # Arial Unicode MS
                (r'C:\Windows\Fonts\calibri.ttf', 'Calibri', 'Calibri'),
                (r'C:\Windows\Fonts\verdana.ttf', 'Verdana', 'Verdana'),
            ]
        # Linux fonts
        elif os.name == 'posix':
            font_configs = [
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans', 'DejaVu Sans'),
                ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans', 'Liberation Sans'),
                ('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', 'NotoSans', 'Noto Sans'),
                ('/usr/share/fonts/truetype/arial.ttf', 'Arial', 'Arial'),
                ('/usr/share/fonts/TTF/DejaVuSans.ttf', 'DejaVuSans', 'DejaVu Sans'),  # Alternative path
            ]
        
        font_registered = False
        registered_font_name = None
        css_font_name = None
        
        for font_path, internal_name, css_name in font_configs:
            if os.path.exists(font_path):
                try:
                    # Register font in ReportLab
                    pdfmetrics.registerFont(TTFont(internal_name, font_path))
                    
                    # Register mapping for all variants
                    addMapping(internal_name, 0, 0, internal_name)  # normal
                    addMapping(internal_name, 0, 1, internal_name)  # italic
                    addMapping(internal_name, 1, 0, internal_name)  # bold
                    addMapping(internal_name, 1, 1, internal_name)  # bold italic
                    
                    # Mapping for CSS names and standard ReportLab fonts
                    addMapping(css_name, 0, 0, internal_name)
                    addMapping('sans-serif', 0, 0, internal_name)
                    addMapping('Helvetica', 0, 0, internal_name)  # Important: map Helvetica to our font
                    addMapping('Helvetica', 0, 1, internal_name)  # italic
                    addMapping('Helvetica', 1, 0, internal_name)  # bold
                    addMapping('Helvetica', 1, 1, internal_name)  # bold italic
                    
                    if not font_registered:
                        registered_font_name = internal_name
                        css_font_name = css_name
                        font_registered = True
                    
                    logging.info(f'Font registered: {internal_name} (CSS: {css_name}) from {font_path}')
                    
                    # Use first found font
                    break
                except Exception as e:
                    logging.warning(f'Failed to register font {font_path}: {e}')
                    continue
        
        if not font_registered:
            logging.warning('System fonts not found, using Helvetica (may not support Cyrillic)')
        
        _fonts_registered = True
        return css_font_name if font_registered else 'Helvetica'
    except Exception as e:
        logging.warning(f'Error registering fonts: {e}')
        return 'Helvetica'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTML2PDF function processing request.')

    try:
        # Register fonts for Unicode support and get font name for CSS
        css_font_name = register_fonts()
        if css_font_name is None:
            css_font_name = 'Arial'
        
        # Get HTML data from request body
        html_content = req.get_body().decode('utf-8')
        
        if not html_content:
            return func.HttpResponse(
                "HTML content not provided",
                status_code=400
            )

        # Check if HTML already has full structure
        html_lower = html_content.lower().strip()
        has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
        
        # Use registered font - important to use exact name
        # xhtml2pdf uses font mapping through ReportLab
        font_family = "Helvetica, Arial, sans-serif"  # Helvetica will be mapped to registered font
        
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
        # Use show_error_as_pdf=False to see errors in logs
        pisa_status = pisa.CreatePDF(
            src=full_html,
            dest=pdf_buffer,
            encoding='utf-8',
            link_callback=None,
            show_error_as_pdf=False
        )
        
        # Log warnings
        if pisa_status.warn:
            for warning in pisa_status.warn:
                logging.warning(f'PISA warning: {warning}')
        
        # Check for errors
        if pisa_status.err:
            logging.error(f'Error creating PDF: {pisa_status.err}')
            return func.HttpResponse(
                f"Error converting HTML to PDF: {pisa_status.err}",
                status_code=500
            )
        
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        
        return func.HttpResponse(
            pdf_bytes,
            mimetype="application/pdf",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=converted.pdf"
            }
        )
    
    except Exception as e:
        logging.error(f'Error converting HTML to PDF: {str(e)}')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )

