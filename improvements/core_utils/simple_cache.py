"""
Simple Cache - Refactored from RedisCache
Simplified caching mechanism without deep scraping dependencies.
"""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Simple in-memory cache for storing data.
    Can be easily replaced with Redis or other cache backends.
    """

    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 24):
        self.cache = {}
        self.max_size = max_size
        self.default_ttl_hours = default_ttl_hours
        self.access_times = {}  # For LRU eviction

    def _make_key(self, key: str) -> str:
        """Generate a standardized cache key."""
        return f"cache:{hashlib.md5(key.encode()).hexdigest()}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache."""
        cache_key = self._make_key(key)
        
        if cache_key not in self.cache:
            return None
            
        # Check if expired
        if self._is_expired(cache_key):
            self.delete(key)
            return None
            
        # Update access time for LRU
        self.access_times[cache_key] = datetime.now()
        
        return self.cache[cache_key]

    def set(self, key: str, data: Dict[str, Any], ttl_hours: Optional[int] = None) -> bool:
        """Set data in cache."""
        try:
            cache_key = self._make_key(key)
            
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Prepare data with metadata
            cache_data = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "ttl_hours": ttl_hours or self.default_ttl_hours
            }
            
            self.cache[cache_key] = cache_data
            self.access_times[cache_key] = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete data from cache."""
        try:
            cache_key = self._make_key(key)
            
            if cache_key in self.cache:
                del self.cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache data."""
        try:
            self.cache.clear()
            self.access_times.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def _is_expired(self, cache_key: str) -> bool:
        """Check if cache entry is expired."""
        if cache_key not in self.cache:
            return True
            
        cache_data = self.cache[cache_key]
        timestamp_str = cache_data.get("timestamp")
        ttl_hours = cache_data.get("ttl_hours", self.default_ttl_hours)
        
        if not timestamp_str:
            return True
            
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            age = now - timestamp
            return age > timedelta(hours=ttl_hours)
        except Exception:
            return True

    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.access_times:
            return
            
        # Find least recently used item
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove from both dictionaries
        if lru_key in self.cache:
            del self.cache[lru_key]
        if lru_key in self.access_times:
            del self.access_times[lru_key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size,
            "keys": list(self.cache.keys())
        }

    def is_cached(self, key: str) -> bool:
        """Check if key exists in cache and is not expired."""
        return self.get(key) is not None


