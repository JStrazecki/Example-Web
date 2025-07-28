#!/usr/bin/env python3
"""
Configuration settings for SQL Assistant MCP Teams Bot
Centralized configuration management
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass 
class PowerBIConfig:
    """Power BI configuration"""
    tenant_id: str
    client_id: str
    client_secret: str
    authority_url: Optional[str] = None
    scope: str = "https://analysis.windows.net/powerbi/api/.default"
    
    @classmethod
    def from_env(cls) -> Optional['PowerBIConfig']:
        """Create config from environment variables"""
        tenant_id = os.environ.get("POWERBI_TENANT_ID")
        client_id = os.environ.get("POWERBI_CLIENT_ID") 
        client_secret = os.environ.get("POWERBI_CLIENT_SECRET")
        
        if not all([tenant_id, client_id, client_secret]):
            return None
        
        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            authority_url=authority_url,
            scope=os.environ.get("POWERBI_SCOPE", "https://analysis.windows.net/powerbi/api/.default")
        )

@dataclass
class TeamsConfig:
    """Teams Bot configuration"""
    app_id: str
    app_password: str
    
    @classmethod
    def from_env(cls) -> Optional['TeamsConfig']:
        """Create config from environment variables"""
        app_id = os.environ.get("MICROSOFT_APP_ID")
        app_password = os.environ.get("MICROSOFT_APP_PASSWORD")
        
        if not all([app_id, app_password]):
            return None
        
        return cls(
            app_id=app_id,
            app_password=app_password
        )


class AppConfig:
    """Main application configuration"""
    
    def __init__(self):
        self.powerbi = PowerBIConfig.from_env()
        self.teams = TeamsConfig.from_env()
        
        # MCP server settings
        self.mcp_port = int(os.environ.get("MCP_PORT", "3000"))
        self.mcp_host = os.environ.get("MCP_HOST", "localhost")
        
        # Teams bot settings
        self.bot_port = int(os.environ.get("BOT_PORT", "3978"))
        self.bot_host = os.environ.get("BOT_HOST", "0.0.0.0")
        
        # Logging settings
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.log_dir = os.environ.get("LOG_DIR", "./logs")
        
        # Feature flags
        self.enable_powerbi_integration = bool(self.powerbi)
        self.enable_teams_bot = bool(self.teams)
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration status"""
        return {
            "powerbi_configured": self.powerbi is not None,
            "teams_configured": self.teams is not None,
            "features": {
                "powerbi_integration": self.enable_powerbi_integration,
                "teams_bot": self.enable_teams_bot
            },
            "ports": {
                "mcp_server": self.mcp_port,
                "teams_bot": self.bot_port
            }
        }
    
    def validate(self) -> Dict[str, list]:
        """Validate configuration and return missing requirements"""
        missing = {
            "critical": [],
            "optional": []
        }
        
        # Critical requirements - Power BI is now required
        if not self.powerbi:
            missing["critical"].extend([
                "POWERBI_TENANT_ID",
                "POWERBI_CLIENT_ID",
                "POWERBI_CLIENT_SECRET"
            ])
        
        # Optional features
        if not self.teams:
            missing["optional"].extend([
                "MICROSOFT_APP_ID",
                "MICROSOFT_APP_PASSWORD"
            ])
        
        return missing

# Global configuration instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config

def print_config_status():
    """Print configuration status to console"""
    status = config.get_status()
    validation = config.validate()
    
    print("=" * 60)
    print("POWER BI MCP TEAMS BOT - CONFIGURATION STATUS")
    print("=" * 60)
    
    print(f"🔧 Configuration Status:")
    print(f"  Power BI: {'✅' if status['powerbi_configured'] else '❌'}")
    print(f"  Teams Bot: {'✅' if status['teams_configured'] else '❌'}")
    
    print(f"\n🚀 Available Features:")
    print(f"  Power BI Integration: {'✅' if status['features']['powerbi_integration'] else '❌'}")
    print(f"  Teams Bot: {'✅' if status['features']['teams_bot'] else '❌'}")
    
    print(f"\n🌐 Server Ports:")
    print(f"  MCP Server: {status['ports']['mcp_server']}")
    print(f"  Teams Bot: {status['ports']['teams_bot']}")
    
    if validation["critical"]:
        print(f"\n❌ Missing Critical Configuration:")
        for var in validation["critical"]:
            print(f"  - {var}")
    
    if validation["optional"]:
        print(f"\n⚠️ Missing Optional Configuration:")
        for var in validation["optional"]:
            print(f"  - {var}")
    
    if not validation["critical"] and not validation["optional"]:
        print(f"\n✅ All configuration complete!")
    
    print("=" * 60)

if __name__ == "__main__":
    print_config_status()