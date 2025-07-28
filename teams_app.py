#!/usr/bin/env python3
"""
Teams Bot Application Server
Runs the Teams Bot Framework server for SQL Assistant MCP integration
"""

import os
import sys
import asyncio
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity

from teams_bot import SQLAssistantBot
from app_config import get_config, print_config_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TeamsApp:
    """Teams Bot Framework Application"""
    
    def __init__(self):
        self.config = get_config()
        
        # Validate configuration
        validation = self.config.validate()
        if validation["critical"]:
            logger.critical("❌ Missing critical configuration!")
            for var in validation["critical"]:
                logger.critical(f"  - {var}")
            sys.exit(1)
        
        # Create bot adapter
        if not self.config.teams:
            logger.error("❌ Teams configuration not available")
            sys.exit(1)
        
        settings = BotFrameworkAdapterSettings(
            app_id=self.config.teams.app_id,
            app_password=self.config.teams.app_password
        )
        
        self.adapter = BotFrameworkAdapter(settings)
        self.bot = SQLAssistantBot()
        
        # Error handler
        async def on_error(context, error):
            logger.error(f"Bot error: {error}", exc_info=True)
            await context.send_activity("❌ Sorry, an error occurred processing your request.")
        
        self.adapter.on_turn_error = on_error
    
    async def messages_handler(self, req: Request) -> Response:
        """Handle incoming Teams messages"""
        if "application/json" in req.headers.get("Content-Type", ""):
            body = await req.json()
        else:
            return Response(status=415)
        
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            response = await self.adapter.process_activity(
                activity, 
                auth_header,
                self.bot.on_message_activity
            )
            
            if response:
                return Response(
                    text=response.body, 
                    status=response.status,
                    headers={"Content-Type": "application/json"}
                )
            else:
                return Response(status=200)
                
        except Exception as e:
            logger.error(f"Error processing activity: {e}", exc_info=True)
            return Response(status=500)
    
    async def health_handler(self, req: Request) -> Response:
        """Health check endpoint"""
        status = self.config.get_status()
        
        health_data = {
            "status": "healthy",
            "service": "Power BI Teams Bot",
            "timestamp": "2025-01-28T00:00:00Z",  # Would use real timestamp
            "configuration": status,
            "bot": {
                "app_id": self.config.teams.app_id[:8] + "***" if self.config.teams else None,
                "adapter_ready": self.adapter is not None
            }
        }
        
        return web.json_response(health_data)
    
    async def info_handler(self, req: Request) -> Response:
        """Information endpoint"""
        return web.json_response({
            "name": "Power BI MCP Teams Bot",
            "version": "1.0.0",
            "description": "Teams bot with MCP integration for Power BI queries",
            "endpoints": {
                "/api/messages": "Teams Bot Framework endpoint",
                "/health": "Health check",
                "/info": "Service information"
            },
            "features": {
                "powerbi_integration": self.config.enable_powerbi_integration,
                "mcp_server": True
            }
        })
    
    def create_app(self) -> web.Application:
        """Create aiohttp web application"""
        app = web.Application()
        
        # Add routes
        app.router.add_post("/api/messages", self.messages_handler)
        app.router.add_get("/health", self.health_handler)
        app.router.add_get("/info", self.info_handler)
        
        # Add CORS if needed
        from aiohttp_cors import setup as cors_setup, ResourceOptions
        cors = cors_setup(app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Apply CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
        
        return app

def main():
    """Main entry point"""
    print_config_status()
    
    logger.info("Starting Power BI Teams Bot")
    
    try:
        teams_app = TeamsApp()
        app = teams_app.create_app()
        
        # Start server
        host = teams_app.config.bot_host
        port = teams_app.config.bot_port
        
        logger.info(f"🤖 Teams Bot starting on {host}:{port}")
        logger.info(f"📡 Bot endpoint: http://{host}:{port}/api/messages")
        logger.info(f"🔍 Health check: http://{host}:{port}/health")
        
        web.run_app(
            app,
            host=host,
            port=port,
            access_log_format='%a %t "%r" %s %b'
        )
        
    except KeyboardInterrupt:
        logger.info("Teams Bot shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start Teams Bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()