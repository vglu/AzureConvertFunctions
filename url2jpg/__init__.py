"""
URL to JPG conversion Azure Function
"""
import logging
import azure.functions as func
from urllib.parse import urlparse
from utils.exceptions import ValidationError, ExternalServiceError, SecurityError, ProcessingError
from utils.validation import validate_url
from utils.logging_utils import create_logger_context, log_function_start, log_function_success, log_function_error
from utils.encoding import decode_request_body
from utils.config import Config

# Try to import playwright for screenshot
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, url2jpg requires Playwright")


def capture_screenshot(url: str, width: int = None, height: int = None) -> bytes:
    """
    Captures screenshot of URL using Playwright
    
    Args:
        url: URL to capture
        width: Screenshot width (defaults to Config.DEFAULT_SCREENSHOT_WIDTH)
        height: Screenshot height (defaults to Config.DEFAULT_SCREENSHOT_HEIGHT)
        
    Returns:
        JPEG image bytes
        
    Raises:
        ExternalServiceError: If Playwright is not available or capture fails
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise ExternalServiceError("Playwright is required for url2jpg. Install with: playwright install chromium")
    
    width = width or Config.DEFAULT_SCREENSHOT_WIDTH
    height = height or Config.DEFAULT_SCREENSHOT_HEIGHT
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set viewport size
        page.set_viewport_size({"width": width, "height": height})
        
        # Navigate to URL
        page.goto(url, wait_until='domcontentloaded', timeout=Config.PLAYWRIGHT_TIMEOUT)
        
        # Wait for network to be idle
        try:
            page.wait_for_load_state('networkidle', timeout=Config.PLAYWRIGHT_NETWORK_IDLE_TIMEOUT)
        except Exception:
            pass  # Continue even if networkidle timeout
        
        # Wait for tables to be populated if any
        try:
            page.wait_for_selector('table tbody tr, table tr:not(:first-child)', timeout=Config.PLAYWRIGHT_WAIT_FOR_TABLE_TIMEOUT)
            logging.info("Table data rows detected")
        except Exception:
            logging.warning("No table data rows found, waiting additional time")
            page.wait_for_timeout(5000)
        
        # Additional wait for any remaining async operations
        page.wait_for_timeout(Config.PLAYWRIGHT_ADDITIONAL_WAIT)
        
        # Scroll to bottom to trigger lazy loading if any
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(Config.PLAYWRIGHT_SCROLL_WAIT)
        
        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        
        # Take screenshot
        screenshot_bytes = page.screenshot(
            type='jpeg',
            quality=Config.DEFAULT_SCREENSHOT_QUALITY,
            full_page=True
        )
        
        browser.close()
        logging.info("Successfully captured screenshot using Playwright")
        return screenshot_bytes


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert URL to JPG format (screenshot).
    
    Args:
        req: Azure Function HTTP request containing URL in body
        
    Returns:
        HTTP response with JPEG image (200) or error message (400/500)
        
    Example:
        Request body: "https://example.com"
        Query params: ?width=1920&height=1080
        Response: JPEG image bytes
    """
    context = create_logger_context(req, 'url2jpg')
    log_function_start(logging, context, 'URL2JPG function processing request.')
    
    try:
        if not PLAYWRIGHT_AVAILABLE:
            return func.HttpResponse(
                "Playwright is required for url2jpg. Install with: playwright install chromium",
                status_code=500
            )
        
        # Get URL from request body
        req_body = req.get_body()
        url_content = decode_request_body(req_body).strip()
        
        if not url_content:
            raise ValidationError("URL not provided")
        
        # Validate URL (including SSRF protection)
        is_valid, error_msg = validate_url(url_content)
        if not is_valid:
            raise SecurityError(f"Invalid or unsafe URL: {error_msg}")
        
        # Get optional parameters from query string
        try:
            width = int(req.params.get('width', Config.DEFAULT_SCREENSHOT_WIDTH))
            height = int(req.params.get('height', Config.DEFAULT_SCREENSHOT_HEIGHT))
        except ValueError:
            width = Config.DEFAULT_SCREENSHOT_WIDTH
            height = Config.DEFAULT_SCREENSHOT_HEIGHT
        
        # Capture screenshot
        try:
            jpg_bytes = capture_screenshot(url_content, width, height)
        except ExternalServiceError as e:
            log_function_error(logging, context, e, 'Error capturing screenshot')
            return func.HttpResponse(
                f"Error capturing screenshot: {str(e)}",
                status_code=500
            )
        except Exception as e:
            log_function_error(logging, context, e, 'Unexpected error capturing screenshot')
            return func.HttpResponse(
                f"Error capturing screenshot: {str(e)}",
                status_code=500
            )
        
        if not jpg_bytes:
            raise ProcessingError("Failed to capture screenshot")
        
        log_function_success(logging, context, 'URL2JPG function completed successfully')
        
        return func.HttpResponse(
            jpg_bytes,
            mimetype="image/jpeg",
            status_code=200,
            headers={
                "Content-Disposition": "attachment; filename=screenshot.jpg"
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
    except Exception as e:
        log_function_error(logging, context, e, 'Unexpected error')
        return func.HttpResponse(
            f"Conversion error: {str(e)}",
            status_code=500
        )
