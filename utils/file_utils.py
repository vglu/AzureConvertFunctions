"""
File utilities for temporary file handling
"""
import tempfile
import os
from contextlib import contextmanager
from typing import Generator


@contextmanager
def temporary_file(suffix: str = '', prefix: str = 'tmp', delete: bool = True) -> Generator[str, None, None]:
    """
    Context manager for temporary files
    
    Args:
        suffix: File suffix (e.g., '.dbf', '.jpg')
        prefix: File prefix
        delete: Whether to delete file on exit
        
    Yields:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        prefix=prefix
    )
    temp_file.close()
    try:
        yield temp_file.name
    finally:
        if delete and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass  # Ignore cleanup errors

