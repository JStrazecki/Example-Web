"""
Token Manager for caching and refreshing authentication tokens
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class TokenInfo:
    """Information about a cached token"""
    access_token: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class TokenManager:
    """Manages token caching, validation, and refresh"""
    
    def __init__(self):
        self._token_cache: Dict[str, TokenInfo] = {}
        self._refresh_callbacks: Dict[str, Callable] = {}
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def store_token(self, 
                   cache_key: str, 
                   token_info: TokenInfo,
                   refresh_callback: Optional[Callable] = None):
        """Store token in cache with optional refresh callback"""
        self._token_cache[cache_key] = token_info
        
        if refresh_callback:
            self._refresh_callbacks[cache_key] = refresh_callback
        
        logger.debug(f"Token stored for key: {cache_key}")
    
    def get_token(self, cache_key: str, min_validity_minutes: int = 5) -> Optional[TokenInfo]:
        """Get token from cache if valid"""
        if cache_key not in self._token_cache:
            return None
        
        token_info = self._token_cache[cache_key]
        min_expiry = datetime.now() + timedelta(minutes=min_validity_minutes)
        
        if token_info.expires_at > min_expiry:
            logger.debug(f"Valid token found for key: {cache_key}")
            return token_info
        else:
            logger.debug(f"Token expired or expiring soon for key: {cache_key}")
            return None
    
    async def get_or_refresh_token(self, 
                                  cache_key: str, 
                                  min_validity_minutes: int = 5) -> Optional[TokenInfo]:
        """Get token from cache or refresh if expired"""
        token_info = self.get_token(cache_key, min_validity_minutes)
        
        if token_info:
            return token_info
        
        # Try to refresh if callback available
        if cache_key in self._refresh_callbacks:
            logger.info(f"Attempting to refresh token for key: {cache_key}")
            refresh_callback = self._refresh_callbacks[cache_key]
            
            try:
                new_token = await refresh_callback()
                if new_token:
                    return new_token
            except Exception as e:
                logger.error(f"Token refresh failed for key {cache_key}: {e}")
        
        return None
    
    def remove_token(self, cache_key: str):
        """Remove token from cache"""
        if cache_key in self._token_cache:
            del self._token_cache[cache_key]
        
        if cache_key in self._refresh_callbacks:
            del self._refresh_callbacks[cache_key]
        
        logger.debug(f"Token removed for key: {cache_key}")
    
    def clear_all_tokens(self):
        """Clear all cached tokens"""
        self._token_cache.clear()
        self._refresh_callbacks.clear()
        logger.info("All tokens cleared from cache")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of token cache"""
        now = datetime.now()
        status = {
            "total_tokens": len(self._token_cache),
            "tokens": {}
        }
        
        for key, token_info in self._token_cache.items():
            time_until_expiry = token_info.expires_at - now
            status["tokens"][key] = {
                "expires_at": token_info.expires_at.isoformat(),
                "time_until_expiry_seconds": int(time_until_expiry.total_seconds()),
                "is_valid": time_until_expiry.total_seconds() > 300,  # 5 minutes
                "token_type": token_info.token_type,
                "has_refresh_callback": key in self._refresh_callbacks
            }
        
        return status
    
    def _start_cleanup_task(self):
        """Start background task to clean up expired tokens"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_tokens())
    
    async def _cleanup_expired_tokens(self):
        """Background task to periodically clean up expired tokens"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                now = datetime.now()
                expired_keys = []
                
                for key, token_info in self._token_cache.items():
                    if token_info.expires_at <= now:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    logger.debug(f"Cleaning up expired token: {key}")
                    self.remove_token(key)
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired tokens")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in token cleanup task: {e}")
    
    def shutdown(self):
        """Shutdown token manager and cleanup tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        self.clear_all_tokens()
        logger.info("Token manager shutdown complete")

# Global token manager instance
_token_manager = TokenManager()

def get_token_manager() -> TokenManager:
    """Get the global token manager instance"""
    return _token_manager