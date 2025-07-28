"""
Power BI Authentication Manager
Handles OAuth2 authentication with Power BI services
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from msal import ConfidentialClientApplication
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    ConfidentialClientApplication = None

logger = logging.getLogger(__name__)

@dataclass
class PowerBICredentials:
    """Power BI authentication credentials"""
    tenant_id: str
    client_id: str
    client_secret: str
    authority_url: str
    scope: str = "https://analysis.windows.net/powerbi/api/.default"

class PowerBIAuthManager:
    """Manages Power BI authentication and token lifecycle"""
    
    def __init__(self, 
                 tenant_id: str,
                 client_id: str, 
                 client_secret: str):
        
        if not MSAL_AVAILABLE:
            raise ImportError("MSAL library required. Install with: pip install msal")
        
        self.credentials = PowerBICredentials(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            authority_url=f"https://login.microsoftonline.com/{tenant_id}"
        )
        
        self._msal_app = None
        self._token_cache = {}
        self._initialize_msal_client()
    
    def _initialize_msal_client(self):
        """Initialize MSAL confidential client application"""
        try:
            self._msal_app = ConfidentialClientApplication(
                client_id=self.credentials.client_id,
                authority=self.credentials.authority_url,
                client_credential=self.credentials.client_secret
            )
            logger.info("Power BI MSAL client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MSAL client: {e}")
            raise
    
    async def get_access_token(self) -> Optional[str]:
        """Get valid access token for Power BI API"""
        if not self._msal_app:
            logger.error("MSAL client not initialized")
            return None
        
        # Check cache first
        cache_key = "powerbi_token"
        if cache_key in self._token_cache:
            cached_token = self._token_cache[cache_key]
            if cached_token["expires_at"] > datetime.now() + timedelta(minutes=5):
                logger.debug("Using cached Power BI access token")
                return cached_token["access_token"]
        
        try:
            logger.info("Acquiring new Power BI access token...")
            result = self._msal_app.acquire_token_for_client(
                scopes=[self.credentials.scope]
            )
            
            if "access_token" in result:
                # Cache the token
                expires_in = result.get("expires_in", 3600)
                self._token_cache[cache_key] = {
                    "access_token": result["access_token"],
                    "expires_at": datetime.now() + timedelta(seconds=expires_in)
                }
                
                logger.info("Successfully acquired Power BI access token")
                return result["access_token"]
            else:
                error_msg = result.get('error_description', result.get('error', 'Unknown error'))
                logger.error(f"Failed to acquire token: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Exception while getting access token: {e}", exc_info=True)
            return None
    
    def is_configured(self) -> bool:
        """Check if authentication is properly configured"""
        return (
            MSAL_AVAILABLE and
            self.credentials.tenant_id and 
            self.credentials.client_id and 
            self.credentials.client_secret and
            self._msal_app is not None
        )
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get detailed configuration status"""
        return {
            "configured": self.is_configured(),
            "msal_available": MSAL_AVAILABLE,
            "credentials_present": {
                "tenant_id": bool(self.credentials.tenant_id),
                "client_id": bool(self.credentials.client_id),
                "client_secret": bool(self.credentials.client_secret)
            },
            "token_cached": bool(self._token_cache.get("powerbi_token")),
            "authority_url": self.credentials.authority_url
        }
    
    @classmethod
    def from_environment(cls) -> Optional['PowerBIAuthManager']:
        """Create PowerBIAuthManager from environment variables"""
        tenant_id = os.environ.get("POWERBI_TENANT_ID")
        client_id = os.environ.get("POWERBI_CLIENT_ID")
        client_secret = os.environ.get("POWERBI_CLIENT_SECRET")
        
        if not all([tenant_id, client_id, client_secret]):
            logger.warning("Power BI credentials not found in environment")
            return None
        
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )