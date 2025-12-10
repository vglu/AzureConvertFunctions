import logging
import azure.functions as func
from io import BytesIO
import base64

# Try to import playwright for screenshot
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, url2jpg requires Playwright")


def capture_screenshot(url: str, width: int = 1920, height: int = 1080) -> bytes:
    """Captures screenshot of URL using Playwright"""
    if not PLAYWRIGHT_AVAILABLE:
        raise Exception("Playwright is required for url2jpg. Install with: playwright install chromium")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set viewport size
        page.set_viewport_size({"width": width, "height": height})
        
        # Navigate to URL
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Wait for network to be idle
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass  # Continue even if networkidle timeout
        
        # Wait for tables to be populated if any
        try:
            page.wait_for_selector('table tbody tr, table tr:not(:first-child)', timeout=10000)
            logging.info("Table data rows detected")
        except:
            logging.warning("No table data rows found, waiting additional time")
            page.wait_for_timeout(5000)
        
        # Additional wait for any remaining async operations
        page.wait_for_timeout(2000)
        
        # Scroll to bottom to trigger lazy loading if any
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        
        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        
        # Take screenshot
        screenshot_bytes = page.screenshot(type='jpeg', quality=90, full_page=True)
        
        browser.close()
        logging.info("Successfully captured screenshot using Playwright")
        return screenshot_bytes


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('URL2JPG function processing request.')

    try:
        if not PLAYWRIGHT_AVAILABLE:
            return func.HttpResponse(
                "Playwright is required for url2jpg. Install with: playwright install chromium",
                status_code=500
            )
        
        # Get URL from request body
        url_content = req.get_body().decode('utf-8').strip()
        
        if not url_content:
            return func.HttpResponse(
                "URL not provided",
                status_code=400
            )

        # Get optional parameters from query string
        width = int(req.params.get('width', 1920))
        height = int(req.params.get('height', 1080))
        
        # Validate URL
        from urllib.parse import urlparse
        parsed = urlparse(url_content)
        if not parsed.scheme or not parsed.netloc:
            return func.HttpResponse(
                "Invalid URL format",
                status_code=400
            )

        # Capture screenshot
        try:
            jpg_bytes = capture_screenshot(url_content, width, height)
        except Exception as e:
            logging.error(f"Error capturing screenshot: {str(e)}")
            return func.HttpResponse(
                f"Error capturing screenshot: {str(e)}",
                status_code=500
            )

        if not jpg_bytes:
            return func.HttpResponse(
                "Failed to capture screenshot",
                status_code=500
            )

        return func.HttpResponse(
            jpg_bytes,
            mimetype="image/jpeg",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=screenshot.jpg"
            }
        )
    
    except Exception as e:
        logging.error(f'Error converting URL to JPG: {str(e)}')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )



