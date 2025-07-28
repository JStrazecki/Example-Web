"""
Centralized Configuration Manager for Modular Application
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class PowerBIConfig:
    """Power BI configuration settings"""
    tenant_id: str
    client_id: str
    client_secret: str
    scope: str = "https://analysis.windows.net/powerbi/api/.default"
    authority_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.authority_url:
            self.authority_url = f"https://login.microsoftonline.com/{self.tenant_id}"

@dataclass  
class TeamsConfig:
    """Teams Bot configuration settings"""
    app_id: str
    app_password: str
    bot_port: int = 3978
    bot_host: str = "0.0.0.0"

@dataclass
class MCPConfig:
    """MCP server configuration settings"""
    server_url: str
    api_key: Optional[str] = None
    timeout: int = 60
    retry_attempts: int = 3

@dataclass
class WebConfig:
    """Web server configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8080
    enable_cors: bool = True
    static_path: Optional[str] = None

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_dir: Optional[str] = None
    enable_file_logging: bool = False

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration settings"""
    endpoint: str
    api_key: str
    deployment_name: str
    api_version: str = "2024-02-15-preview"
    max_tokens: int = 4000
    temperature: float = 0.3
    thinking_enabled: bool = True
    analysis_depth: str = "standard"  # standard, deep, extensive
    response_style: str = "business"  # technical, business, executive

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config_data = {}
        
        # Initialize configurations
        self.powerbi: Optional[PowerBIConfig] = None
        self.teams: Optional[TeamsConfig] = None
        self.mcp: Optional[MCPConfig] = None
        self.azure_openai: Optional[AzureOpenAIConfig] = None
        self.web: WebConfig = WebConfig()
        self.logging: LoggingConfig = LoggingConfig()
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment and optional file"""
        # Load from file if specified
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self._config_data = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")
        
        # Load Power BI configuration
        self._load_powerbi_config()
        
        # Load Teams configuration
        self._load_teams_config()
        
        # Load MCP configuration
        self._load_mcp_config()
        
        # Load Azure OpenAI configuration
        self._load_azure_openai_config()
        
        # Load Web configuration
        self._load_web_config()
        
        # Load Logging configuration
        self._load_logging_config()
    
    def _load_powerbi_config(self):
        """Load Power BI configuration from environment"""
        tenant_id = os.environ.get("POWERBI_TENANT_ID") or self._config_data.get("powerbi", {}).get("tenant_id")
        client_id = os.environ.get("POWERBI_CLIENT_ID") or self._config_data.get("powerbi", {}).get("client_id")
        client_secret = os.environ.get("POWERBI_CLIENT_SECRET") or self._config_data.get("powerbi", {}).get("client_secret")
        
        if all([tenant_id, client_id, client_secret]):
            self.powerbi = PowerBIConfig(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                scope=os.environ.get("POWERBI_SCOPE", self._config_data.get("powerbi", {}).get("scope", "https://analysis.windows.net/powerbi/api/.default"))
            )
            logger.info("Power BI configuration loaded successfully")
        else:
            logger.warning("Power BI configuration incomplete")
    
    def _load_teams_config(self):
        """Load Teams configuration from environment"""
        app_id = os.environ.get("MICROSOFT_APP_ID") or self._config_data.get("teams", {}).get("app_id")
        app_password = os.environ.get("MICROSOFT_APP_PASSWORD") or self._config_data.get("teams", {}).get("app_password")
        
        if all([app_id, app_password]):
            self.teams = TeamsConfig(
                app_id=app_id,
                app_password=app_password,
                bot_port=int(os.environ.get("BOT_PORT", self._config_data.get("teams", {}).get("bot_port", 3978))),
                bot_host=os.environ.get("BOT_HOST", self._config_data.get("teams", {}).get("bot_host", "0.0.0.0"))
            )
            logger.info("Teams configuration loaded successfully")
        else:
            logger.warning("Teams configuration incomplete")
    
    def _load_mcp_config(self):
        """Load MCP configuration from environment"""
        server_url = os.environ.get("MCP_SERVER_URL") or self._config_data.get("mcp", {}).get("server_url")
        
        if server_url:
            self.mcp = MCPConfig(
                server_url=server_url,
                api_key=os.environ.get("MCP_API_KEY") or self._config_data.get("mcp", {}).get("api_key"),
                timeout=int(os.environ.get("MCP_TIMEOUT", self._config_data.get("mcp", {}).get("timeout", 60))),
                retry_attempts=int(os.environ.get("MCP_RETRY_ATTEMPTS", self._config_data.get("mcp", {}).get("retry_attempts", 3)))
            )
            logger.info("MCP configuration loaded successfully")
        else:
            logger.warning("MCP server URL not configured")
    
    def _load_azure_openai_config(self):
        """Load Azure OpenAI configuration from environment"""
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT") or self._config_data.get("azure_openai", {}).get("endpoint")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY") or self._config_data.get("azure_openai", {}).get("api_key")
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME") or self._config_data.get("azure_openai", {}).get("deployment_name")
        
        if all([endpoint, api_key, deployment_name]):
            self.azure_openai = AzureOpenAIConfig(
                endpoint=endpoint,
                api_key=api_key,
                deployment_name=deployment_name,
                api_version=os.environ.get("AZURE_OPENAI_VERSION", self._config_data.get("azure_openai", {}).get("api_version", "2024-02-15-preview")),
                max_tokens=int(os.environ.get("AZURE_OPENAI_MAX_TOKENS", self._config_data.get("azure_openai", {}).get("max_tokens", 4000))),
                temperature=float(os.environ.get("AZURE_OPENAI_TEMPERATURE", self._config_data.get("azure_openai", {}).get("temperature", 0.3))),
                thinking_enabled=os.environ.get("AI_THINKING_ENABLED", str(self._config_data.get("azure_openai", {}).get("thinking_enabled", True))).lower() == "true",
                analysis_depth=os.environ.get("AI_ANALYSIS_DEPTH", self._config_data.get("azure_openai", {}).get("analysis_depth", "standard")),
                response_style=os.environ.get("AI_RESPONSE_STYLE", self._config_data.get("azure_openai", {}).get("response_style", "business"))
            )
            logger.info("Azure OpenAI configuration loaded successfully")
        else:
            logger.warning("Azure OpenAI configuration incomplete")
    
    def _load_web_config(self):
        """Load Web server configuration"""
        self.web = WebConfig(
            host=os.environ.get("WEB_HOST", self._config_data.get("web", {}).get("host", "0.0.0.0")),
            port=int(os.environ.get("WEB_PORT", self._config_data.get("web", {}).get("port", 8080))),
            enable_cors=os.environ.get("WEB_ENABLE_CORS", str(self._config_data.get("web", {}).get("enable_cors", True))).lower() == "true",
            static_path=os.environ.get("WEB_STATIC_PATH") or self._config_data.get("web", {}).get("static_path")
        )
        logger.info("Web server configuration loaded")
    
    def _load_logging_config(self):
        """Load Logging configuration"""
        self.logging = LoggingConfig(
            level=os.environ.get("LOG_LEVEL", self._config_data.get("logging", {}).get("level", "INFO")),
            format=os.environ.get("LOG_FORMAT", self._config_data.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")),
            log_dir=os.environ.get("LOG_DIR") or self._config_data.get("logging", {}).get("log_dir"),
            enable_file_logging=os.environ.get("ENABLE_FILE_LOGGING", str(self._config_data.get("logging", {}).get("enable_file_logging", False))).lower() == "true"
        )
        logger.info("Logging configuration loaded")
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration status"""
        return {
            "configurations": {
                "powerbi": bool(self.powerbi),
                "teams": bool(self.teams),
                "mcp": bool(self.mcp),
                "azure_openai": bool(self.azure_openai),
                "web": True,
                "logging": True
            },
            "powerbi_configured": bool(self.powerbi),
            "teams_configured": bool(self.teams),
            "mcp_configured": bool(self.mcp),
            "azure_openai_configured": bool(self.azure_openai),
            "config_file_used": bool(self.config_file and os.path.exists(self.config_file)),
            "endpoints": {
                "web_server": f"http://{self.web.host}:{self.web.port}" if self.web else None,
                "teams_bot": f"http://{self.teams.bot_host}:{self.teams.bot_port}/api/messages" if self.teams else None,
                "mcp_server": self.mcp.server_url if self.mcp else None,
                "azure_openai": self.azure_openai.endpoint if self.azure_openai else None
            }
        }
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate configuration and return missing requirements"""
        validation_result = {
            "critical": [],
            "optional": [],
            "recommendations": []
        }
        
        # Power BI validation (critical for core functionality)
        if not self.powerbi:
            validation_result["critical"].extend([
                "POWERBI_TENANT_ID",
                "POWERBI_CLIENT_ID", 
                "POWERBI_CLIENT_SECRET"
            ])
        
        # MCP server validation (critical for web app functionality)
        if not self.mcp or not self.mcp.server_url:
            validation_result["critical"].append("MCP_SERVER_URL")
        
        # Azure OpenAI validation (optional but recommended for AI features)
        if not self.azure_openai:
            validation_result["optional"].extend([
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_DEPLOYMENT_NAME"
            ])
        
        # Teams validation (optional)
        if not self.teams:
            validation_result["optional"].extend([
                "MICROSOFT_APP_ID",
                "MICROSOFT_APP_PASSWORD"
            ])
        
        # Recommendations
        if self.mcp and not self.mcp.api_key:
            validation_result["recommendations"].append("Consider setting MCP_API_KEY for secure communication")
        
        if not self.logging.enable_file_logging:
            validation_result["recommendations"].append("Consider enabling file logging for production deployments")
        
        if self.azure_openai and not self.azure_openai.thinking_enabled:
            validation_result["recommendations"].append("Consider enabling AI thinking process for better analysis quality")
        
        return validation_result
    
    def print_configuration_status(self):
        """Print detailed configuration status"""
        status = self.get_status()
        validation = self.validate()
        
        print("=" * 70)
        print("🔧 MODULAR POWER BI MCP APPLICATION - CONFIGURATION STATUS")
        print("=" * 70)
        
        print("\n📊 Configuration Modules:")
        for module, configured in status["configurations"].items():
            print(f"  {module.upper()}: {'✅ Configured' if configured else '❌ Not Configured'}")
        
        print(f"\n🌐 Service Endpoints:")
        for service, endpoint in status["endpoints"].items():
            if endpoint:
                print(f"  {service.replace('_', ' ').title()}: {endpoint}")
            else:
                print(f"  {service.replace('_', ' ').title()}: ❌ Not configured")
        
        # Show validation results
        if validation["critical"]:
            print(f"\n❌ Missing Critical Configuration:")
            for var in validation["critical"]:
                print(f"  - {var}")
        
        if validation["optional"]:
            print(f"\n⚠️ Missing Optional Configuration:")
            for var in validation["optional"]:
                print(f"  - {var}")
        
        if validation["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in validation["recommendations"]:
                print(f"  - {rec}")
        
        if not validation["critical"]:
            print(f"\n✅ Core configuration complete!")
        
        print("=" * 70)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)"""
        result = {
            "powerbi": {
                "configured": bool(self.powerbi),
                "tenant_id": self.powerbi.tenant_id[:8] + "***" if self.powerbi else None,
                "client_id": self.powerbi.client_id[:8] + "***" if self.powerbi else None
            } if self.powerbi else {"configured": False},
            
            "teams": {
                "configured": bool(self.teams),
                "app_id": self.teams.app_id[:8] + "***" if self.teams else None,
                "bot_port": self.teams.bot_port if self.teams else None,
                "bot_host": self.teams.bot_host if self.teams else None
            } if self.teams else {"configured": False},
            
            "mcp": {
                "configured": bool(self.mcp),
                "server_url": self.mcp.server_url if self.mcp else None,
                "has_api_key": bool(self.mcp and self.mcp.api_key) if self.mcp else False,
                "timeout": self.mcp.timeout if self.mcp else None
            } if self.mcp else {"configured": False},
            
            "azure_openai": {
                "configured": bool(self.azure_openai),
                "endpoint": self.azure_openai.endpoint if self.azure_openai else None,
                "deployment_name": self.azure_openai.deployment_name if self.azure_openai else None,
                "thinking_enabled": self.azure_openai.thinking_enabled if self.azure_openai else False,
                "analysis_depth": self.azure_openai.analysis_depth if self.azure_openai else None,
                "response_style": self.azure_openai.response_style if self.azure_openai else None
            } if self.azure_openai else {"configured": False},
            
            "web": {
                "host": self.web.host,
                "port": self.web.port,
                "enable_cors": self.web.enable_cors
            },
            
            "logging": {
                "level": self.logging.level,
                "enable_file_logging": self.logging.enable_file_logging
            }
        }
        
        return result

# Global configuration manager instance
_config_manager = None

def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    
    return _config_manager

def reload_configuration(config_file: Optional[str] = None):
    """Reload the global configuration"""
    global _config_manager
    _config_manager = ConfigManager(config_file)