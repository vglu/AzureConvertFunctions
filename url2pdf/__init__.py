"""
URL to PDF conversion Azure Function
"""
import logging
import os
import re
import azure.functions as func
from xhtml2pdf import pisa
from utils.exceptions import ValidationError, ProcessingError, ExternalServiceError, SecurityError
from utils.validation import validate_url, validate_request_size
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from utils.fonts import register_fonts
from utils.config import Config
from .fetcher import fetch_url_content
from .image_handler import replace_images_with_absolute_urls, create_link_callback


def prepare_html_for_pdf(html_content: str, font_family: str) -> str:
    """
    Prepare HTML content for PDF conversion
    
    Args:
        html_content: Raw HTML content
        font_family: Font family to use
        
    Returns:
        Prepared HTML content
    """
    # Check if HTML already has full structure
    html_lower = html_content.lower().strip()
    has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
    
    if has_html_tag:
        # HTML is already complete, but we need to completely remove all existing styles
        # and replace with our own clean, minimal styles to avoid parsing errors
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'\s+style=["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<link[^>]*>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'href=["\']https?://[^"\']+["\']', 'href=""', html_content, flags=re.IGNORECASE)
        
        # Add minimal, clean style block that xhtml2pdf can definitely parse
        clean_styles = f"""<style>
* {{ font-family: {font_family} !important; }}
body {{ font-family: {font_family}; font-size: 12pt; line-height: 1.6; margin: 0; padding: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #f2f2f2; font-weight: bold; }}
</style>"""
        
        if '<head>' in html_lower:
            html_content = html_content.replace('</head>', f'{clean_styles}</head>', 1)
        else:
            html_content = html_content.replace('<html>', f'<html><head>{clean_styles}</head>', 1)
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
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # Final safety check: remove any remaining problematic elements
    full_html = re.sub(r'<link[^>]*>', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'@keyframes\s+\w+\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'@[a-z-]+\s*[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'@[a-z-]+\s*[^;{]*[;{]?', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'var\([^)]+\)', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'calc\([^)]+\)', '0', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'--[a-z0-9-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r':not\([^)]+\)', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r':[a-z-]+\([^)]+\)', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'\[[^\]]*\]', '', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'-webkit-animation\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'animation\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'transition\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'content\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'-webkit-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'-moz-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'-o-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'-ms-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
    
    # Normalize CSS
    full_html = re.sub(r'([:;{])\s*[\n\r\t]+', r'\1 ', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'[\n\r\t]+\s*([;}])', r'\1', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r':([^;{}]*?)[\n\r\t]+([^;{}]*?)([;}])', r':\1 \2\3', full_html, flags=re.IGNORECASE | re.DOTALL)
    full_html = re.sub(r'([:;{])\s+', r'\1 ', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'\s+([;}])', r'\1', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'([:;{])\s*[\n\r]+\s*', r'\1 ', full_html, flags=re.IGNORECASE)
    full_html = re.sub(r'\s*[\n\r]+\s*([;}])', r'\1', full_html, flags=re.IGNORECASE)
    
    return full_html


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert URL to PDF format.
    
    Args:
        req: Azure Function HTTP request containing URL in body
        
    Returns:
        HTTP response with PDF file (200) or error message (400/500)
        
    Example:
        Request body: "https://example.com"
        Response: PDF file bytes
    """
    context = create_logger_context(req, 'url2pdf')
    log_function_start(logging, context, 'URL2PDF function processing request.')
    
    try:
        # Register fonts for Unicode support
        register_fonts()
        
        # Get URL from request body
        req_body = req.get_body()
        url_content = decode_request_body(req_body).strip()
        
        if not url_content:
            raise ValidationError("URL not provided")
        
        # Validate URL (including SSRF protection)
        is_valid, error_msg = validate_url(url_content)
        if not is_valid:
            raise SecurityError(f"Invalid or unsafe URL: {error_msg}")
        
        # Fetch HTML content from URL (try Playwright first for JS rendering)
        try:
            html_content = fetch_url_content(url_content, use_playwright=True)
        except ExternalServiceError as e:
            log_function_error(logging, context, e, 'Error fetching URL')
            return func.HttpResponse(
                f"Error fetching URL: {str(e)}",
                status_code=400
            )
        except Exception as e:
            log_function_error(logging, context, e, 'Unexpected error fetching URL')
            return func.HttpResponse(
                f"Error fetching URL: {str(e)}",
                status_code=400
            )
        
        if not html_content:
            raise ValidationError("No content retrieved from URL")
        
        # Convert relative image URLs to absolute URLs
        html_content = replace_images_with_absolute_urls(html_content, url_content)
        
        # Use registered font
        font_family = "Helvetica, Arial, sans-serif"  # Helvetica will be mapped to registered font
        
        # Prepare HTML for PDF conversion
        full_html = prepare_html_for_pdf(html_content, font_family)
        
        # Convert HTML to PDF using xhtml2pdf
        from io import BytesIO
        pdf_buffer = BytesIO()
        
        # Link callback to handle external resources
        link_callback, temp_files = create_link_callback(url_content)
        
        try:
            # Create PDF from HTML with correct encoding and settings
            pisa_status = pisa.CreatePDF(
                src=full_html,
                dest=pdf_buffer,
                encoding='utf-8',
                link_callback=link_callback,
                show_error_as_pdf=False
            )
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logging.debug(f'Cleaned up temp file: {temp_file}')
                except Exception as e:
                    logging.warning(f'Failed to clean up temp file {temp_file}: {e}')
        
        # Log warnings
        if pisa_status.warn:
            try:
                if hasattr(pisa_status.warn, '__iter__') and not isinstance(pisa_status.warn, (str, bytes)):
                    for warning in pisa_status.warn:
                        logging.warning(f'PISA warning: {warning}')
                else:
                    logging.warning(f'PISA warning: {pisa_status.warn}')
            except (TypeError, AttributeError) as warn_err:
                logging.warning(f'Error logging PISA warnings: {warn_err}')
        
        # Check for errors
        if pisa_status.err:
            error_msg = str(pisa_status.err)
            logging.error(f'Error creating PDF: {error_msg}')
            raise ProcessingError(f"Error converting HTML to PDF: {error_msg}")
        
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        
        log_function_success(logging, context, 'URL2PDF function completed successfully')
        
        return func.HttpResponse(
            pdf_bytes,
            mimetype="application/pdf",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=converted.pdf"
            }
        )
    
    except ValidationError as e:
        log_function_error(logging, context, e, 'Validation error')
        return func.HttpResponse(
            f"Validation error: {str(e)}",
            status_code=400
        )
    except SecurityError as e:
        log_function_error(logging, context, e, 'Security error')
        return func.HttpResponse(
            f"Security error: {str(e)}",
            status_code=400
        )
    except ProcessingError as e:
        log_function_error(logging, context, e, 'Processing error')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )
    except Exception as e:
        log_function_error(logging, context, e, 'Unexpected error')
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )
