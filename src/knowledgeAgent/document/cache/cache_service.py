from typing import Optional, Any, Dict
from dataclasses import dataclass
import logging
from .sqllite import SqlLite

@dataclass
class CacheConfig:
    """Configuration for cache service"""
    enabled: bool = True
    location: Optional[str] = None
    cache_type: str = "sqlite"

class SQLiteCacheService:
    """SQLite implementation of cache service"""
    
    def __init__(self):
        self.db = None
        self.logger = logging.getLogger("knowledgeAgent.cache")
    
    def initialize(self, config: CacheConfig) -> None:
        """Initialize SQLite cache"""
        if not config.enabled:
            self.logger.info("Cache disabled")
            return
            
        if not config.location:
            self.logger.warning("No cache location provided")
            return
            
        self.logger.info(f"Initializing SQLite cache at {config.location}")
        self.db = SqlLite(db_path=config.location)
    
    def set(self, key: str, value: Any) -> bool:
        """Save document and its chunks to cache"""
        if not self.db:
            self.logger.warning("Cache not initialized, skipping save")
            return False
        try:
            return self.db.save_document(value)
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Dict]:
        """Get document and its chunks from cache"""
        if not self.db:
            self.logger.warning("Cache not initialized, skipping get")
            return None
        try:
            return self.db.get_document_with_chunks(key)
        except Exception as e:
            self.logger.error(f"Error getting from cache: {e}")
            return None
