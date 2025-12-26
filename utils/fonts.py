"""
Font registration utilities for PDF generation
"""
import logging
import os
from typing import Optional
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from .config import Config

# Flag for one-time font registration
_fonts_registered = False


def register_fonts() -> Optional[str]:
    """
    Registers fonts for Unicode and Cyrillic support
    
    Returns:
        CSS font name to use, or None if registration failed
    """
    global _fonts_registered
    
    if _fonts_registered:
        return 'Arial'  # Return font name for CSS
    
    try:
        # Try to use system fonts with Unicode support (cross-platform)
        font_configs = []
        
        # Windows fonts
        if os.name == 'nt':
            font_configs = Config.get_font_paths_windows()
        # Linux fonts
        elif os.name == 'posix':
            font_configs = Config.get_font_paths_linux()
        
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

