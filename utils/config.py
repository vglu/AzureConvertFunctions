"""
Configuration module for Azure Convert Functions
Loads configuration from environment variables with sensible defaults
"""
import os
from typing import List


class Config:
    """Application configuration"""
    
    # Request limits
    MAX_REQUEST_SIZE = int(os.getenv('MAX_REQUEST_SIZE', '10485760'))  # 10 MB
    MAX_URL_FETCH_TIMEOUT = int(os.getenv('MAX_URL_FETCH_TIMEOUT', '30'))
    
    # Playwright settings
    PLAYWRIGHT_TIMEOUT = int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000'))
    PLAYWRIGHT_NETWORK_IDLE_TIMEOUT = int(os.getenv('PLAYWRIGHT_NETWORK_IDLE_TIMEOUT', '10000'))
    PLAYWRIGHT_WAIT_FOR_TABLE_TIMEOUT = int(os.getenv('PLAYWRIGHT_WAIT_FOR_TABLE_TIMEOUT', '10000'))
    PLAYWRIGHT_ADDITIONAL_WAIT = int(os.getenv('PLAYWRIGHT_ADDITIONAL_WAIT', '2000'))
    PLAYWRIGHT_SCROLL_WAIT = int(os.getenv('PLAYWRIGHT_SCROLL_WAIT', '1000'))
    
    # Screenshot settings
    DEFAULT_SCREENSHOT_WIDTH = int(os.getenv('DEFAULT_SCREENSHOT_WIDTH', '1920'))
    DEFAULT_SCREENSHOT_HEIGHT = int(os.getenv('DEFAULT_SCREENSHOT_HEIGHT', '1080'))
    DEFAULT_SCREENSHOT_QUALITY = int(os.getenv('DEFAULT_SCREENSHOT_QUALITY', '90'))
    
    # Allowed URL schemes
    ALLOWED_URL_SCHEMES = ['http', 'https']
    
    # Blocked hosts/IPs for SSRF protection
    BLOCKED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '169.254.169.254',  # Azure metadata service
    ]
    
    # Private IP ranges (CIDR notation)
    PRIVATE_IP_RANGES = [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        'fc00::/7',  # IPv6 private
    ]
    
    # Font paths (can be overridden via environment)
    @staticmethod
    def get_font_paths_windows() -> List[tuple]:
        """Get Windows font paths"""
        paths_str = os.getenv(
            'FONT_PATHS_WINDOWS',
            'C:\\Windows\\Fonts\\arial.ttf|Arial|Arial;C:\\Windows\\Fonts\\arialuni.ttf|ArialUnicode|Arial;C:\\Windows\\Fonts\\calibri.ttf|Calibri|Calibri;C:\\Windows\\Fonts\\verdana.ttf|Verdana|Verdana'
        )
        fonts = []
        for font_str in paths_str.split(';'):
            if '|' in font_str:
                parts = font_str.split('|')
                if len(parts) == 3:
                    fonts.append((parts[0], parts[1], parts[2]))
        return fonts if fonts else [
            (r'C:\Windows\Fonts\arial.ttf', 'Arial', 'Arial'),
            (r'C:\Windows\Fonts\arialuni.ttf', 'ArialUnicode', 'Arial'),
            (r'C:\Windows\Fonts\calibri.ttf', 'Calibri', 'Calibri'),
            (r'C:\Windows\Fonts\verdana.ttf', 'Verdana', 'Verdana'),
        ]
    
    @staticmethod
    def get_font_paths_linux() -> List[tuple]:
        """Get Linux font paths"""
        paths_str = os.getenv(
            'FONT_PATHS_LINUX',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf|DejaVuSans|DejaVu Sans;/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf|LiberationSans|Liberation Sans;/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf|NotoSans|Noto Sans'
        )
        fonts = []
        for font_str in paths_str.split(';'):
            if '|' in font_str:
                parts = font_str.split('|')
                if len(parts) == 3:
                    fonts.append((parts[0], parts[1], parts[2]))
        return fonts if fonts else [
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans', 'DejaVu Sans'),
            ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'LiberationSans', 'Liberation Sans'),
            ('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf', 'NotoSans', 'Noto Sans'),
            ('/usr/share/fonts/truetype/arial.ttf', 'Arial', 'Arial'),
            ('/usr/share/fonts/TTF/DejaVuSans.ttf', 'DejaVuSans', 'DejaVu Sans'),
        ]
    
    # Cache settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    
    # Image download settings
    IMAGE_DOWNLOAD_TIMEOUT = int(os.getenv('IMAGE_DOWNLOAD_TIMEOUT', '10'))
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', '5242880'))  # 5 MB
    
    # PDF generation settings
    PDF_PAGE_MARGIN = os.getenv('PDF_PAGE_MARGIN', '2cm')
    PDF_FONT_SIZE = os.getenv('PDF_FONT_SIZE', '12pt')
    PDF_LINE_HEIGHT = os.getenv('PDF_LINE_HEIGHT', '1.6')

