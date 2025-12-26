"""
Simple in-memory cache for URL content
"""
import hashlib
import time
from typing import Optional, Any, Dict
from .config import Config


class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl: int = None):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (defaults to Config.CACHE_TTL)
        """
        self._cache: Dict[str, tuple] = {}
        self.ttl = ttl or Config.CACHE_TTL
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)


# Global cache instance
_url_cache = SimpleCache(ttl=Config.CACHE_TTL) if Config.ENABLE_CACHE else None


def get_cached_url_content(url: str) -> Optional[str]:
    """
    Get cached URL content
    
    Args:
        url: URL to look up
        
    Returns:
        Cached content or None
    """
    if not _url_cache:
        return None
    
    cache_key = hashlib.md5(url.encode()).hexdigest()
    return _url_cache.get(cache_key)


def set_cached_url_content(url: str, content: str) -> None:
    """
    Cache URL content
    
    Args:
        url: URL
        content: Content to cache
    """
    if not _url_cache:
        return
    
    cache_key = hashlib.md5(url.encode()).hexdigest()
    _url_cache.set(cache_key, content)

