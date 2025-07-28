#!/usr/bin/env python3
"""
Power BI MCP Server with Teams Integration
Teams bot integration for Power BI queries and workspace management
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logs
logging.getLogger('msal').setLevel(logging.WARNING)

# Initialize MCP server
mcp = FastMCP("powerbi-teams-server")

class EnvironmentConfig:
    """Environment configuration manager"""
    
    def __init__(self):
        self.powerbi_vars = {
            "POWERBI_TENANT_ID": "Power BI Tenant ID",
            "POWERBI_CLIENT_ID": "Power BI Client ID",
            "POWERBI_CLIENT_SECRET": "Power BI Client Secret"
        }
        
        self.teams_vars = {
            "MICROSOFT_APP_ID": "Teams Bot App ID",
            "MICROSOFT_APP_PASSWORD": "Teams Bot App Password"
        }
    
    def check_environment(self) -> Dict[str, Any]:
        """Check and validate environment variables"""
        logger.info("=== Power BI Configuration Check ===")
        
        missing_vars = []
        status = {
            "powerbi": True, 
            "teams": True
        }
        
        # Check Power BI variables
        logger.info("=== Power BI Configuration ===")
        for var, description in self.powerbi_vars.items():
            value = os.environ.get(var)
            if not value:
                logger.error(f"❌ {var}: NOT SET ({description})")
                missing_vars.append(var)
                status["powerbi"] = False
            else:
                if "SECRET" in var:
                    masked = value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
                    logger.info(f"✓ {var}: {masked}")
                else:
                    logger.info(f"✓ {var}: {value[:30]}...")
        
        # Check Teams variables
        logger.info("\n=== Teams Bot Configuration ===")
        for var, description in self.teams_vars.items():
            value = os.environ.get(var)
            if not value:
                logger.info(f"ℹ️ {var}: NOT SET ({description})")
                status["teams"] = False
            else:
                if "PASSWORD" in var or "SECRET" in var:
                    masked = value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
                    logger.info(f"✓ {var}: {masked}")
                else:
                    logger.info(f"✓ {var}: {value[:30]}...")
        
        return {
            "missing_vars": missing_vars,
            "status": status
        }

# Initialize configuration
config = EnvironmentConfig()
env_status = config.check_environment()

# Initialize Power BI client if available
POWERBI_CLIENT = None
if env_status["status"]["powerbi"]:
    try:
        from powerbi_client import PowerBIClient
        POWERBI_CLIENT = PowerBIClient()
        logger.info("✓ Power BI client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Power BI client: {e}")

def register_powerbi_tools():
    """Register Power BI-related MCP tools"""
    
    @mcp.tool()
    def list_powerbi_workspaces() -> str:
        """List available Power BI workspaces."""
        if not POWERBI_CLIENT:
            return json.dumps({
                "error": "Power BI client not available",
                "message": "Missing Power BI configuration"
            })
        
        try:
            workspaces = POWERBI_CLIENT.get_workspaces()
            return json.dumps({
                "workspaces": [
                    {
                        "id": ws.get("id"),
                        "name": ws.get("name"),
                        "type": ws.get("type", "Unknown")
                    }
                    for ws in workspaces
                ]
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
            return json.dumps({
                "error": "Failed to list workspaces",
                "message": str(e)
            })

    @mcp.tool()
    def list_powerbi_datasets(workspace_name: str) -> str:
        """
        List datasets in a Power BI workspace.
        
        Args:
            workspace_name: Name of the Power BI workspace
        """
        if not POWERBI_CLIENT:
            return json.dumps({
                "error": "Power BI client not available"
            })
        
        try:
            workspace = POWERBI_CLIENT.get_workspace_by_name(workspace_name)
            datasets = POWERBI_CLIENT.get_datasets(workspace["id"])
            
            return json.dumps({
                "workspace": workspace_name,
                "datasets": [
                    {
                        "id": ds.get("id"),
                        "name": ds.get("name"),
                        "configuredBy": ds.get("configuredBy", "Unknown")
                    }
                    for ds in datasets
                ]
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return json.dumps({
                "error": "Failed to list datasets",
                "message": str(e)
            })

    @mcp.tool()
    def execute_dax_query(
        workspace_name: str,
        dataset_name: str,
        dax_query: str
    ) -> str:
        """
        Execute a DAX query against a Power BI dataset.
        
        Args:
            workspace_name: Name of the Power BI workspace
            dataset_name: Name of the dataset
            dax_query: DAX query to execute
        """
        if not POWERBI_CLIENT:
            return json.dumps({
                "error": "Power BI client not available"
            })
        
        try:
            workspace = POWERBI_CLIENT.get_workspace_by_name(workspace_name)
            dataset = POWERBI_CLIENT.get_dataset_by_name(workspace["id"], dataset_name)
            
            result = POWERBI_CLIENT.execute_dax_query(
                workspace["id"], 
                dataset["id"], 
                dax_query
            )
            
            # Extract table data from result
            results = result.get("results", [])
            if results and "tables" in results[0]:
                return json.dumps(results[0]["tables"], indent=2)
            else:
                return json.dumps({"message": "No data returned"})
                
        except Exception as e:
            logger.error(f"Failed to execute DAX query: {e}")
            return json.dumps({
                "error": "Failed to execute DAX query",
                "message": str(e)
            })

def register_teams_tools():
    """Register Teams-specific MCP tools"""
    
    @mcp.tool()
    def format_teams_message(
        content: str,
        message_type: str = "text"
    ) -> str:
        """
        Format content for Teams message display.
        
        Args:
            content: Content to format
            message_type: Type of message (text, card, table)
        """
        try:
            if message_type == "table" and isinstance(content, str):
                # Try to parse as JSON and format as table
                try:
                    data = json.loads(content)
                    if isinstance(data, list) and len(data) > 0:
                        # Convert to adaptive card table format
                        headers = list(data[0].keys()) if data else []
                        rows = []
                        
                        for item in data[:10]:  # Limit to 10 rows for Teams
                            row = [str(item.get(header, "")) for header in headers]
                            rows.append(row)
                        
                        table_markdown = "| " + " | ".join(headers) + " |\n"
                        table_markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                        
                        for row in rows:
                            table_markdown += "| " + " | ".join(row) + " |\n"
                        
                        return json.dumps({
                            "type": "markdown",
                            "content": table_markdown
                        })
                        
                except json.JSONDecodeError:
                    pass
            
            # Default text formatting
            return json.dumps({
                "type": "text",
                "content": content
            })
            
        except Exception as e:
            logger.error(f"Failed to format Teams message: {e}")
            return json.dumps({
                "type": "text", 
                "content": str(content)
            })

def main():
    """Main entry point"""
    logger.info("Starting Power BI MCP Server with Teams Integration")
    
    # Check environment status
    if not env_status["status"]["powerbi"]:
        logger.critical("❌ Missing required Power BI environment variables!")
        logger.info("Required variables:")
        for var in env_status["missing_vars"]:
            logger.info(f"  - {var}")
        sys.exit(1)
    
    # Register all tools
    logger.info("Registering MCP tools...")
    
    if env_status["status"]["powerbi"]:
        register_powerbi_tools()
        logger.info("✓ Power BI tools registered")
    else:
        logger.error("❌ Power BI tools not available")
        sys.exit(1)
    
    register_teams_tools()
    logger.info("✓ Teams tools registered")
    
    # Start MCP server
    logger.info("Starting MCP server...")
    logger.info(f"Server capabilities: PowerBI={bool(POWERBI_CLIENT)}")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.critical(f"Server startup failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()