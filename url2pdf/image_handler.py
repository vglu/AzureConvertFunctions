"""
Image handling utilities for PDF generation
"""
import logging
import tempfile
import os
from typing import Optional, Dict, List
from urllib.parse import urlparse, urljoin
import requests
from utils.exceptions import ExternalServiceError
from utils.validation import validate_image_size
from utils.config import Config


def download_image_bytes(image_url: str, base_url: str = None) -> Optional[bytes]:
    """
    Downloads an image and returns its bytes
    
    Args:
        image_url: Image URL (can be relative)
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Image bytes or None if download fails
        
    Raises:
        ExternalServiceError: If download fails
    """
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
        response = requests.get(image_url, headers=headers, timeout=Config.IMAGE_DOWNLOAD_TIMEOUT, verify=True)
        response.raise_for_status()
        
        # Check if it's actually an image
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
            logging.warning(f'URL does not point to an image: {image_url} (Content-Type: {content_type})')
            return None
        
        # Validate image size
        image_data = response.content
        try:
            validate_image_size(image_data)
        except Exception as e:
            logging.warning(f'Image size validation failed for {image_url}: {e}')
            return None
        
        logging.info(f'Successfully downloaded image: {image_url} ({len(image_data)} bytes)')
        return image_data
        
    except requests.exceptions.RequestException as e:
        logging.warning(f'Failed to download image {image_url}: {e}')
        return None
    except Exception as e:
        logging.warning(f'Unexpected error downloading image {image_url}: {e}')
        return None


def replace_images_with_absolute_urls(html_content: str, base_url: str) -> str:
    """
    Converts relative image URLs to absolute URLs
    
    Args:
        html_content: HTML content
        base_url: Base URL for resolving relative URLs
        
    Returns:
        HTML content with absolute image URLs
    """
    import re
    
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


def create_link_callback(base_url: str) -> tuple:
    """
    Create link_callback function for xhtml2pdf
    
    Args:
        base_url: Base URL for resolving relative image URLs
        
    Returns:
        Tuple of (link_callback_function, temp_files_list)
    """
    image_cache: Dict[str, str] = {}
    temp_files: List[str] = []
    
    def link_callback(uri: str, rel: str) -> Optional[str]:
        """
        Callback function for xhtml2pdf to handle external resources
        
        Args:
            uri: Resource URI
            rel: Resource relationship type
            
        Returns:
            File path for images, None for other resources
        """
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
            image_data = download_image_bytes(uri, base_url)
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
    
    return link_callback, temp_files

