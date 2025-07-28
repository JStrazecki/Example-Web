#!/usr/bin/env python3
"""
Unified startup script for SQL Assistant MCP Teams Bot
Starts both MCP server and Teams bot in parallel
"""

import os
import sys
import asyncio
import logging
import threading
import signal
from concurrent.futures import ThreadPoolExecutor
import time

from app_config import get_config, print_config_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StartupManager:
    """Manages startup of both MCP server and Teams bot"""
    
    def __init__(self):
        self.config = get_config()
        self.running = True
        self.threads = []
        
        # Validate configuration
        validation = self.config.validate()
        if validation["critical"]:
            logger.critical("❌ Missing critical configuration!")
            for var in validation["critical"]:
                logger.critical(f"  - {var}")
            sys.exit(1)
    
    def start_mcp_server(self):
        """Start MCP server in separate thread"""
        logger.info("🔧 Starting MCP Server...")
        
        try:
            # Import and run MCP server
            from main import main as mcp_main
            mcp_main()
        except Exception as e:
            logger.error(f"❌ MCP Server failed: {e}", exc_info=True)
    
    def start_teams_bot(self):
        """Start Teams bot in separate thread"""
        logger.info("🤖 Starting Teams Bot...")
        
        try:
            # Import and run Teams app
            from teams_app import main as teams_main
            teams_main()
        except Exception as e:
            logger.error(f"❌ Teams Bot failed: {e}", exc_info=True)
    
    def start_services(self):
        """Start both services concurrently"""
        logger.info("🚀 Starting Power BI MCP Teams Bot System")
        print_config_status()
        
        # Create thread pool
        executor = ThreadPoolExecutor(max_workers=2)
        
        # Start MCP server
        if self.config.enable_powerbi_integration:
            logger.info(f"📡 MCP Server will run on port {self.config.mcp_port}")
            mcp_future = executor.submit(self.start_mcp_server)
            self.threads.append(('MCP Server', mcp_future))
        else:
            logger.warning("⚠️ MCP Server disabled - no Power BI configuration")
        
        # Start Teams bot  
        if self.config.enable_teams_bot:
            logger.info(f"🤖 Teams Bot will run on port {self.config.bot_port}")
            # Small delay to let MCP server start first
            time.sleep(2)
            teams_future = executor.submit(self.start_teams_bot)
            self.threads.append(('Teams Bot', teams_future))
        else:
            logger.warning("⚠️ Teams Bot disabled - no Teams configuration")
        
        if not self.threads:
            logger.error("❌ No services to start - check configuration")
            sys.exit(1)
        
        logger.info("✅ All services started")
        logger.info("")
        logger.info("📋 Service Endpoints:")
        if self.config.enable_powerbi_integration:
            logger.info(f"  🔧 MCP Server: Running on port {self.config.mcp_port}")
        if self.config.enable_teams_bot:
            logger.info(f"  🤖 Teams Bot: http://{self.config.bot_host}:{self.config.bot_port}/api/messages")
            logger.info(f"  🔍 Health Check: http://{self.config.bot_host}:{self.config.bot_port}/health")
        logger.info("")
        logger.info("💡 Integration Instructions:")
        logger.info("  1. Configure your Teams app to point to the bot endpoint")
        logger.info("  2. Set up Claude to connect to the MCP server")
        logger.info("  3. Test with 'list workspaces' or DAX queries")
        logger.info("")
        logger.info("🛑 Press Ctrl+C to stop all services")
        
        # Wait for threads and handle shutdown
        try:
            while self.running:
                time.sleep(1)
                
                # Check if any threads have died
                for name, future in self.threads:
                    if future.done():
                        try:
                            future.result()  # This will raise any exception
                        except Exception as e:
                            logger.error(f"❌ {name} stopped unexpectedly: {e}")
                            self.running = False
                            break
                            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested...")
            self.running = False
        
        # Cleanup
        logger.info("🔄 Stopping services...")
        executor.shutdown(wait=False)
        
        # Force kill any remaining threads
        for name, future in self.threads:
            if not future.done():
                logger.info(f"⏹️ Stopping {name}...")
                future.cancel()
        
        logger.info("✅ All services stopped")

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

def main():
    """Main entry point"""
    # Handle system signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    startup_manager = StartupManager()
    startup_manager.start_services()

if __name__ == "__main__":
    main()