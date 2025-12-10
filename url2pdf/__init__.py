import logging
import azure.functions as func
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os
import requests
from urllib.parse import urlparse, urljoin
import re
import base64
import tempfile

# Try to import playwright for JavaScript rendering
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, falling back to basic HTML fetching")

# Flag for one-time font registration
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


def download_image_to_base64(image_url: str, base_url: str = None) -> bytes:
    """Downloads an image and returns its bytes"""
    try:
        # Handle relative URLs
        if base_url and not image_url.startswith(('http://', 'https://')):
            image_url = urljoin(base_url, image_url)
        
        # Validate URL
        parsed = urlparse(image_url)
        if not parsed.scheme or not parsed.netloc:
            logging.warning(f'Invalid image URL: {image_url}')
            return None
        
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10, verify=True)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
            logging.warning(f'URL does not point to an image: {image_url} (Content-Type: {content_type})')
            return None
        
        # Return image bytes
        image_data = response.content
        logging.info(f'Successfully downloaded image: {image_url} ({len(image_data)} bytes)')
        return image_data
        
    except Exception as e:
        logging.warning(f'Failed to download image {image_url}: {e}')
        return None


def replace_images_with_absolute_urls(html_content: str, base_url: str) -> str:
    """Converts relative image URLs to absolute URLs"""
    # Find all img tags with relative src
    img_pattern = r'<img([^>]*?)src=["\']([^"\']+)["\']([^>]*?)>'
    
    def replace_img(match):
        img_attrs_before = match.group(1)
        img_src = match.group(2)
        img_attrs_after = match.group(3)
        
        # Skip if already absolute URL, data URI, or empty
        if img_src.startswith(('http://', 'https://', 'data:')) or not img_src or img_src.startswith('#'):
            return match.group(0)
        
        # Convert relative URL to absolute
        if base_url:
            img_src = urljoin(base_url, img_src)
            return f'<img{img_attrs_before}src="{img_src}"{img_attrs_after}>'
        else:
            return match.group(0)  # Keep as is if no base URL
    
    html_content = re.sub(img_pattern, replace_img, html_content, flags=re.IGNORECASE | re.DOTALL)
    return html_content


def fetch_url_content(url: str, use_playwright: bool = True) -> str:
    """Fetches HTML content from URL, optionally using Playwright for JavaScript rendering"""
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Try to use Playwright for JavaScript rendering if available
        if use_playwright and PLAYWRIGHT_AVAILABLE:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    # Navigate to URL
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    
                    # Wait for network to be idle (all requests finished)
                    try:
                        page.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        pass  # Continue even if networkidle timeout
                    
                    # Wait for tables to be populated
                    # Try to wait for table rows (more than just header)
                    try:
                        # Wait for at least one data row in table (not just th)
                        page.wait_for_selector('table tbody tr, table tr:not(:first-child)', timeout=10000)
                        logging.info("Table data rows detected")
                    except:
                        logging.warning("No table data rows found, waiting additional time")
                        # Wait longer for dynamic content
                        page.wait_for_timeout(5000)
                    
                    # Additional wait for any remaining async operations
                    page.wait_for_timeout(2000)
                    
                    # Scroll to bottom to trigger lazy loading if any
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                    
                    html_content = page.content()
                    browser.close()
                    logging.info("Successfully fetched HTML using Playwright")
                    return html_content
            except Exception as e:
                logging.warning(f"Playwright failed, falling back to requests: {e}")
                # Fall back to requests
        
        # Fallback to requests for basic HTML fetching
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, verify=True)
        response.raise_for_status()
        
        # Try to detect encoding
        if response.encoding:
            html_content = response.text
        else:
            # Fallback to UTF-8
            html_content = response.content.decode('utf-8', errors='replace')
        
        # Remove all CSS and JavaScript to avoid parsing errors
        # We'll add our own clean styles later
        # Remove ALL <link> tags (including multiline) to prevent xhtml2pdf from trying to load external resources
        html_content = re.sub(r'<link[^>]*>', '', html_content, flags=re.IGNORECASE | re.MULTILINE)
        # Also remove link tags that might span multiple lines
        html_content = re.sub(r'<link[^>]*?\/?>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove <script> tags (both external and inline)
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove <style> tags completely - they often contain problematic CSS
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all CSS @ rules that might be in text or attributes
        # @keyframes can be complex with nested braces, need to match them properly
        # Match @keyframes with nested braces
        html_content = re.sub(r'@keyframes\s+\w+\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Match other @ rules with nested braces (more aggressive)
        html_content = re.sub(r'@[a-z-]+\s*[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove @import statements
        html_content = re.sub(r'@import[^;]+;', '', html_content, flags=re.IGNORECASE)
        # Remove @media queries (can be complex with nested rules)
        html_content = re.sub(r'@media[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove any remaining @ rules (catch-all)
        html_content = re.sub(r'@[a-z-]+\s*[^;{]*[;{]?', '', html_content, flags=re.IGNORECASE)
        
        # Remove modern CSS functions that xhtml2pdf doesn't support
        # Remove CSS variables var(--variable-name)
        html_content = re.sub(r'var\([^)]+\)', '', html_content, flags=re.IGNORECASE)
        # Remove calc() functions (can contain var() and complex expressions)
        html_content = re.sub(r'calc\([^)]+\)', '0', html_content, flags=re.IGNORECASE)
        # Remove other CSS functions that might cause issues
        html_content = re.sub(r'rgba?\([^)]+\)', '', html_content, flags=re.IGNORECASE)  # Keep basic colors, but remove rgba
        html_content = re.sub(r'hsla?\([^)]+\)', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'url\([^)]+\)', '', html_content, flags=re.IGNORECASE)  # Remove url() in CSS
        # Remove CSS custom properties (--variable-name: value;)
        html_content = re.sub(r'--[a-z0-9-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE)
        
        # Remove complex CSS selectors that xhtml2pdf doesn't support
        # Remove :not() pseudo-class selectors
        html_content = re.sub(r':not\([^)]+\)', '', html_content, flags=re.IGNORECASE)
        # Remove other complex pseudo-classes that might cause issues
        html_content = re.sub(r':nth-[a-z]+\([^)]+\)', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r':[a-z-]+\([^)]+\)', '', html_content, flags=re.IGNORECASE)  # Remove any pseudo-class with parentheses
        # Remove attribute selectors with complex patterns
        html_content = re.sub(r'\[[^\]]*\]', '', html_content, flags=re.IGNORECASE)  # Remove all attribute selectors
        # Remove complex combinators (>, +, ~) that might cause issues
        # But keep basic selectors like .class and #id
        
        # Remove CSS animation properties that xhtml2pdf doesn't support
        html_content = re.sub(r'-webkit-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-moz-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-o-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-webkit-transition\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'transition\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'transform\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove content property with complex values
        html_content = re.sub(r'content\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Remove vendor prefixes that might cause issues
        html_content = re.sub(r'-webkit-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-moz-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-o-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'-ms-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Normalize CSS: aggressively remove newlines and normalize whitespace
        # This is critical for xhtml2pdf to parse CSS correctly
        # First, replace all newlines and tabs with spaces in CSS contexts
        # Match CSS property:value pairs and normalize them
        html_content = re.sub(r'([:;{])\s*[\n\r\t]+', r'\1 ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'[\n\r\t]+\s*([;}])', r'\1', html_content, flags=re.IGNORECASE)
        # Replace newlines within CSS values (between : and ; or })
        html_content = re.sub(r':([^;{}]*?)[\n\r\t]+([^;{}]*?)([;}])', r':\1 \2\3', html_content, flags=re.IGNORECASE | re.DOTALL)
        # Collapse multiple whitespace characters to single space
        html_content = re.sub(r'([:;{])\s+', r'\1 ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s+([;}])', r'\1', html_content, flags=re.IGNORECASE)
        # Remove any remaining newlines in CSS blocks
        html_content = re.sub(r'([:;{])\s*[\n\r]+\s*', r'\1 ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*[\n\r]+\s*([;}])', r'\1', html_content, flags=re.IGNORECASE)
        
        # Images will be handled separately - convert to base64 instead of removing
        # Don't remove image sources here, we'll convert them to base64 later
        # Remove all href attributes pointing to external URLs (CSS, JS, etc.)
        html_content = re.sub(r'href=["\']https?://[^"\']+["\']', 'href=""', html_content, flags=re.IGNORECASE)
        # Remove all inline style attributes completely - they often contain problematic CSS
        html_content = re.sub(r'\s+style=["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        # Final pass: remove any remaining link tags that might have been missed
        html_content = re.sub(r'<link.*?>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        return html_content
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching URL: {str(e)}')
        raise Exception(f"Failed to fetch URL: {str(e)}")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('URL2PDF function processing request.')

    try:
        # Register fonts for Unicode support
        register_fonts()
        
        # Get URL from request body
        url_content = req.get_body().decode('utf-8').strip()
        
        if not url_content:
            return func.HttpResponse(
                "URL not provided",
                status_code=400
            )

        # Fetch HTML content from URL (try Playwright first for JS rendering)
        try:
            html_content = fetch_url_content(url_content, use_playwright=True)
        except Exception as e:
            logging.error(f"Error fetching URL: {str(e)}")
            return func.HttpResponse(
                f"Error fetching URL: {str(e)}",
                status_code=400
            )

        if not html_content:
            return func.HttpResponse(
                "No content retrieved from URL",
                status_code=400
            )
        
        # Convert relative image URLs to absolute URLs
        # Images will be loaded via link_callback
        html_content = replace_images_with_absolute_urls(html_content, url_content)

        # Check if HTML already has full structure
        html_lower = html_content.lower().strip()
        has_html_tag = '<html' in html_lower or '<!doctype' in html_lower
        
        # Use registered font
        font_family = "Helvetica, Arial, sans-serif"  # Helvetica will be mapped to registered font
        
        if has_html_tag:
            # HTML is already complete, but we need to completely remove all existing styles
            # and replace with our own clean, minimal styles to avoid parsing errors
            # Remove ALL <style> blocks completely - they often contain problematic CSS
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            # Remove all inline style attributes - they often contain problematic CSS
            html_content = re.sub(r'\s+style=["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
            # Remove all <link> tags
            html_content = re.sub(r'<link[^>]*>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
            html_content = re.sub(r'href=["\']https?://[^"\']+["\']', 'href=""', html_content, flags=re.IGNORECASE)
            
            # Add minimal, clean style block that xhtml2pdf can definitely parse
            # Use only simple CSS properties without any complex features
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
                # If no head tag, add it
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

        # Convert HTML to PDF using xhtml2pdf
        pdf_buffer = BytesIO()
        
        # Final safety check: remove any remaining problematic elements that might cause parsing errors
        # Remove link tags
        full_html = re.sub(r'<link[^>]*>', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        # Remove any remaining @ rules (especially @keyframes which can cause parsing errors)
        full_html = re.sub(r'@keyframes\s+\w+\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'@[a-z-]+\s*[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        # Remove any @ rules that might be incomplete or malformed
        full_html = re.sub(r'@[a-z-]+\s*[^;{]*[;{]?', '', full_html, flags=re.IGNORECASE)
        # Remove modern CSS functions and variables that xhtml2pdf doesn't support
        full_html = re.sub(r'var\([^)]+\)', '', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'calc\([^)]+\)', '0', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'--[a-z0-9-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE)
        # Remove complex CSS selectors that xhtml2pdf doesn't support
        full_html = re.sub(r':not\([^)]+\)', '', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r':[a-z-]+\([^)]+\)', '', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'\[[^\]]*\]', '', full_html, flags=re.IGNORECASE)
        # Remove animation and transition properties
        full_html = re.sub(r'-webkit-animation\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'animation\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'transition\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'content\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'-webkit-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'-moz-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'-o-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        full_html = re.sub(r'-ms-[a-z-]+\s*:[^;]+;', '', full_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Normalize CSS: aggressively remove newlines within CSS property values
        # This is critical for xhtml2pdf to parse CSS correctly
        # Replace all newlines, carriage returns, and tabs with spaces in CSS contexts
        full_html = re.sub(r'([:;{])\s*[\n\r\t]+', r'\1 ', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'[\n\r\t]+\s*([;}])', r'\1', full_html, flags=re.IGNORECASE)
        # Replace newlines within CSS values (between : and ; or })
        full_html = re.sub(r':([^;{}]*?)[\n\r\t]+([^;{}]*?)([;}])', r':\1 \2\3', full_html, flags=re.IGNORECASE | re.DOTALL)
        # Collapse multiple whitespace characters to single space
        full_html = re.sub(r'([:;{])\s+', r'\1 ', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'\s+([;}])', r'\1', full_html, flags=re.IGNORECASE)
        # Remove any remaining newlines in CSS blocks
        full_html = re.sub(r'([:;{])\s*[\n\r]+\s*', r'\1 ', full_html, flags=re.IGNORECASE)
        full_html = re.sub(r'\s*[\n\r]+\s*([;}])', r'\1', full_html, flags=re.IGNORECASE)
        
        # Link callback to handle external resources
        # xhtml2pdf will try to load external CSS/JS/images, we need to handle them appropriately
        # Store downloaded images in temporary files for link_callback
        image_cache = {}
        temp_files = []  # Keep track of temp files to clean up
        
        def link_callback(uri, rel):
            # Skip CSS and JS files - we've already removed them
            if rel == 'stylesheet' or uri.endswith(('.css', '.js')):
                logging.debug(f'Skipping CSS/JS resource: {uri}')
                return None
            
            # Skip data URI - xhtml2pdf has issues with them
            if uri.startswith('data:'):
                logging.debug(f'Skipping data URI in link_callback')
                return None
            
            # Try to load images from external URLs
            if uri.startswith(('http://', 'https://')):
                # Check cache first
                if uri in image_cache:
                    logging.debug(f'Using cached image: {uri}')
                    return image_cache[uri]
                
                # Download image
                image_data = download_image_to_base64(uri, url_content)
                if image_data:
                    try:
                        # Create temporary file for image
                        # Determine file extension from URL
                        parsed = urlparse(uri)
                        ext = parsed.path.lower().split('.')[-1] if '.' in parsed.path else 'jpg'
                        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            ext = 'jpg'
                        
                        # Create temp file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
                        temp_file.write(image_data)
                        temp_file.close()
                        temp_files.append(temp_file.name)
                        
                        # Store in cache and return file path
                        image_cache[uri] = temp_file.name
                        logging.info(f'Downloaded and cached image: {uri} ({len(image_data)} bytes) -> {temp_file.name}')
                        return temp_file.name
                    except Exception as e:
                        logging.warning(f'Failed to create temp file for image {uri}: {e}')
                        return None
                else:
                    logging.warning(f'Failed to load image resource: {uri}')
                    return None
            
            # For other resources, skip
            logging.debug(f'Skipping resource: {uri} (rel: {rel})')
            return None
        
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
            # pisa_status.warn might be a list or other iterable
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
        logging.error(f'Error converting URL to PDF: {str(e)}')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )

