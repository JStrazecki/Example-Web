#!/usr/bin/env python3
"""
Modular Power BI MCP Web Application
Main entry point for the modular architecture
"""

import os
import sys
import asyncio
import logging
from typing import Optional

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.config import get_config_manager
from modules.web import WebServer
from modules.auth import PowerBIAuthManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModularPowerBIApp:
    """Main application class for modular Power BI MCP web app"""
    
    def __init__(self, config_file: Optional[str] = None):
        # Load configuration
        self.config = get_config_manager(config_file)
        
        # Validate critical configuration
        validation = self.config.validate()
        if validation["critical"]:
            logger.critical("❌ Missing critical configuration!")
            for var in validation["critical"]:
                logger.critical(f"  - {var}")
            self.config.print_configuration_status()
            sys.exit(1)
        
        # Initialize components
        self.auth_manager = None
        self.web_server = None
        self._setup_components()
    
    def _setup_components(self):
        """Initialize application components"""
        # Initialize Power BI authentication if configured
        if self.config.powerbi:
            try:
                self.auth_manager = PowerBIAuthManager(
                    tenant_id=self.config.powerbi.tenant_id,
                    client_id=self.config.powerbi.client_id,
                    client_secret=self.config.powerbi.client_secret
                )
                logger.info("✅ Power BI authentication manager initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Power BI auth: {e}")
                sys.exit(1)
        
        # Initialize web server if MCP is configured
        if self.config.mcp:
            try:
                self.web_server = WebServer(
                    mcp_url=self.config.mcp.server_url,
                    mcp_api_key=self.config.mcp.api_key,
                    host=self.config.web.host,
                    port=self.config.web.port,
                    config_manager=self.config
                )
                logger.info("✅ Web server initialized")
                
                # Log AI capabilities
                if self.config.azure_openai:
                    logger.info("🤖 AI reasoning capabilities enabled")
                else:
                    logger.info("ℹ️ AI reasoning not configured - using standard mode")
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize web server: {e}")
                sys.exit(1)
    
    async def start(self):
        """Start the modular application"""
        logger.info("🚀 Starting Modular Power BI MCP Web Application")
        
        # Print configuration status
        self.config.print_configuration_status()
        
        # Start web server
        if self.web_server:
            try:
                runner = await self.web_server.start()
                logger.info("✅ All services started successfully")
                
                # Print service information
                print("\n" + "="*60)
                print("🌐 SERVICE ENDPOINTS")
                print("="*60)
                print(f"📱 Web Interface: http://{self.config.web.host}:{self.config.web.port}")
                print(f"🔍 Health Check: http://{self.config.web.host}:{self.config.web.port}/health")
                print(f"📊 API Documentation: http://{self.config.web.host}:{self.config.web.port}/info")
                print(f"🔧 MCP Server: {self.config.mcp.server_url}")
                
                if self.config.teams:
                    print(f"🤖 Teams Bot: http://{self.config.teams.bot_host}:{self.config.teams.bot_port}/api/messages")
                
                print("\n💡 USAGE INSTRUCTIONS:")
                print("1. Open the web interface to interact with Power BI data")
                print("2. Use the API endpoints for programmatic access")
                if self.config.azure_openai:
                    print("3. 🤖 Try AI-powered analysis at /ai/analyze endpoint")
                    print("4. 🧠 Use smart DAX generation at /ai/dax endpoint")
                    print("5. Configure Teams bot if needed for Teams integration")
                    print("6. All requests are proxied through your deployed MCP server")
                else:
                    print("3. Configure Azure OpenAI for intelligent analysis features")
                    print("4. Configure Teams bot if needed for Teams integration")
                    print("5. All requests are proxied through your deployed MCP server")
                print("\n🛑 Press Ctrl+C to stop all services")
                print("="*60)
                
                # Keep the application running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("🛑 Shutdown requested...")
                finally:
                    await self.cleanup(runner)
                    
            except Exception as e:
                logger.error(f"❌ Failed to start web server: {e}")
                sys.exit(1)
        else:
            logger.error("❌ No services configured to start")
            sys.exit(1)
    
    async def cleanup(self, runner=None):
        """Cleanup application resources"""
        logger.info("🔄 Cleaning up application resources...")
        
        if self.web_server:
            await self.web_server.cleanup()
        
        if runner:
            await runner.cleanup()
        
        logger.info("✅ Application cleanup complete")

def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "powerbi": {
            "tenant_id": "your-tenant-id-here",
            "client_id": "your-client-id-here", 
            "client_secret": "your-client-secret-here",
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        },
        "teams": {
            "app_id": "your-teams-app-id-here",
            "app_password": "your-teams-app-password-here",
            "bot_port": 3978,
            "bot_host": "0.0.0.0"
        },
        "mcp": {
            "server_url": "https://your-mcp-server.com",
            "api_key": "your-mcp-api-key-here",
            "timeout": 60,
            "retry_attempts": 3
        },
        "azure_openai": {
            "endpoint": "https://your-openai.openai.azure.com/",
            "api_key": "your-azure-openai-api-key-here",
            "deployment_name": "gpt-4-turbo",
            "api_version": "2024-02-15-preview",
            "max_tokens": 4000,
            "temperature": 0.3,
            "thinking_enabled": True,
            "analysis_depth": "standard",
            "response_style": "business"
        },
        "web": {
            "host": "0.0.0.0",
            "port": 8080,
            "enable_cors": True
        },
        "logging": {
            "level": "INFO",
            "enable_file_logging": False,
            "log_dir": "./logs"
        }
    }
    
    config_file = "config.json"
    try:
        import json
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✅ Sample configuration created: {config_file}")
        print("📝 Please update the configuration with your actual values")
        return config_file
    except Exception as e:
        print(f"❌ Failed to create sample config: {e}")
        return None

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Modular Power BI MCP Web Application")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--validate-config", action="store_true", help="Validate configuration and exit")
    
    args = parser.parse_args()
    
    # Create sample configuration if requested
    if args.create_config:
        create_sample_config()
        return
    
    # Validate configuration if requested
    if args.validate_config:
        config = get_config_manager(args.config)
        config.print_configuration_status()
        return
    
    # Start the application
    try:
        app = ModularPowerBIApp(args.config)
        await app.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())