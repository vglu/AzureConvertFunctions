"""
URL content fetcher with Playwright support
"""
import logging
import re
import requests
from typing import Optional
from urllib.parse import urlparse, urljoin
from utils.exceptions import ExternalServiceError, TimeoutError
from utils.config import Config
from utils.cache import get_cached_url_content, set_cached_url_content

# Try to import playwright for JavaScript rendering
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available, falling back to basic HTML fetching")


def clean_html_css(html_content: str) -> str:
    """
    Clean HTML from problematic CSS that xhtml2pdf cannot handle
    
    Args:
        html_content: Raw HTML content
        
    Returns:
        Cleaned HTML content
    """
    # Remove ALL <link> tags (including multiline) to prevent xhtml2pdf from trying to load external resources
    html_content = re.sub(r'<link[^>]*>', '', html_content, flags=re.IGNORECASE | re.MULTILINE)
    html_content = re.sub(r'<link[^>]*?\/?>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove <script> tags (both external and inline)
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove <style> tags completely - they often contain problematic CSS
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all CSS @ rules
    html_content = re.sub(r'@keyframes\s+\w+\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'@[a-z-]+\s*[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'@import[^;]+;', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'@media[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'@[a-z-]+\s*[^;{]*[;{]?', '', html_content, flags=re.IGNORECASE)
    
    # Remove modern CSS functions
    html_content = re.sub(r'var\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'calc\([^)]+\)', '0', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'rgba?\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'hsla?\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'url\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'--[a-z0-9-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE)
    
    # Remove complex CSS selectors
    html_content = re.sub(r':not\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r':nth-[a-z]+\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r':[a-z-]+\([^)]+\)', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'\[[^\]]*\]', '', html_content, flags=re.IGNORECASE)
    
    # Remove CSS animation properties
    html_content = re.sub(r'-webkit-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-moz-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-o-animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'animation\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-webkit-transition\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'transition\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'transform\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'content\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-webkit-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-moz-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-o-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'-ms-[a-z-]+\s*:[^;]+;', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Normalize CSS: aggressively remove newlines and normalize whitespace
    html_content = re.sub(r'([:;{])\s*[\n\r\t]+', r'\1 ', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'[\n\r\t]+\s*([;}])', r'\1', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r':([^;{}]*?)[\n\r\t]+([^;{}]*?)([;}])', r':\1 \2\3', html_content, flags=re.IGNORECASE | re.DOTALL)
    html_content = re.sub(r'([:;{])\s+', r'\1 ', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'\s+([;}])', r'\1', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'([:;{])\s*[\n\r]+\s*', r'\1 ', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'\s*[\n\r]+\s*([;}])', r'\1', html_content, flags=re.IGNORECASE)
    
    # Remove all href attributes pointing to external URLs
    html_content = re.sub(r'href=["\']https?://[^"\']+["\']', 'href=""', html_content, flags=re.IGNORECASE)
    
    # Remove all inline style attributes completely
    html_content = re.sub(r'\s+style=["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
    
    # Final pass: remove any remaining link tags
    html_content = re.sub(r'<link.*?>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    return html_content


def fetch_url_content(url: str, use_playwright: bool = True) -> str:
    """
    Fetches HTML content from URL, optionally using Playwright for JavaScript rendering
    
    Args:
        url: URL to fetch
        use_playwright: Whether to use Playwright for JS rendering
        
    Returns:
        HTML content as string
        
    Raises:
        ExternalServiceError: If fetching fails
        TimeoutError: If operation times out
    """
    # Check cache first
    cached_content = get_cached_url_content(url)
    if cached_content:
        logging.info(f"Using cached content for URL: {url}")
        return cached_content
    
    try:
        # Try to use Playwright for JavaScript rendering if available
        if use_playwright and PLAYWRIGHT_AVAILABLE:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    # Navigate to URL
                    page.goto(url, wait_until='domcontentloaded', timeout=Config.PLAYWRIGHT_TIMEOUT)
                    
                    # Wait for network to be idle
                    try:
                        page.wait_for_load_state('networkidle', timeout=Config.PLAYWRIGHT_NETWORK_IDLE_TIMEOUT)
                    except Exception:
                        pass  # Continue even if networkidle timeout
                    
                    # Wait for tables to be populated
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
                    
                    html_content = page.content()
                    browser.close()
                    logging.info("Successfully fetched HTML using Playwright")
                    
                    # Clean HTML and cache
                    cleaned_content = clean_html_css(html_content)
                    set_cached_url_content(url, cleaned_content)
                    return cleaned_content
            except Exception as e:
                logging.warning(f"Playwright failed, falling back to requests: {e}")
                # Fall back to requests
        
        # Fallback to requests for basic HTML fetching
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=Config.MAX_URL_FETCH_TIMEOUT, verify=True)
        response.raise_for_status()
        
        # Try to detect encoding
        if response.encoding:
            html_content = response.text
        else:
            # Fallback to UTF-8
            html_content = response.content.decode('utf-8', errors='replace')
        
        # Clean HTML and cache
        cleaned_content = clean_html_css(html_content)
        set_cached_url_content(url, cleaned_content)
        return cleaned_content
    
    except requests.exceptions.Timeout as e:
        raise TimeoutError(f"Request to {url} timed out: {str(e)}") from e
    except requests.exceptions.RequestException as e:
        raise ExternalServiceError(f"Failed to fetch URL {url}: {str(e)}") from e
    except Exception as e:
        raise ExternalServiceError(f"Unexpected error fetching URL {url}: {str(e)}") from e

