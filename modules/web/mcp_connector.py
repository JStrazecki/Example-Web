"""
MCP Connector for communicating with deployed MCP server
"""

import json
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPConnector:
    """Connects to deployed MCP server on the web"""
    
    def __init__(self, mcp_base_url: str, api_key: Optional[str] = None):
        self.mcp_base_url = mcp_base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self._connection_validated = False
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional API key"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PowerBI-MCP-WebClient/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate connection to MCP server"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.mcp_base_url}/health",
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self._connection_validated = True
                    
                    return {
                        "status": "connected",
                        "server_info": data,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "connection_failed",
                        "error": f"HTTP {response.status}: {error_text}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error connecting to MCP server: {e}")
            return {
                "status": "network_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error validating MCP connection: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """Get list of available MCP tools"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.mcp_base_url}/tools",
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "tools": data.get("tools", []),
                        "count": len(data.get("tools", []))
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_mcp_tool(self, 
                           tool_name: str, 
                           arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool on the deployed server"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            payload = {
                "tool": tool_name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Calling MCP tool: {tool_name}")
            
            async with self.session.post(
                f"{self.mcp_base_url}/tools/{tool_name}",
                headers=self._get_headers(),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"MCP tool {tool_name} executed successfully")
                    
                    return {
                        "success": True,
                        "result": result,
                        "tool": tool_name,
                        "execution_time": result.get("execution_time"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"MCP tool {tool_name} failed: {response.status}")
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "tool": tool_name,
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling MCP tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def list_powerbi_workspaces(self) -> Dict[str, Any]:
        """Call the list_powerbi_workspaces MCP tool"""
        return await self.call_mcp_tool("list_powerbi_workspaces", {})
    
    async def list_powerbi_datasets(self, workspace_name: str) -> Dict[str, Any]:
        """Call the list_powerbi_datasets MCP tool"""
        return await self.call_mcp_tool("list_powerbi_datasets", {
            "workspace_name": workspace_name
        })
    
    async def execute_dax_query(self, 
                               workspace_name: str,
                               dataset_name: str, 
                               dax_query: str) -> Dict[str, Any]:
        """Call the execute_dax_query MCP tool"""
        return await self.call_mcp_tool("execute_dax_query", {
            "workspace_name": workspace_name,
            "dataset_name": dataset_name,
            "dax_query": dax_query
        })
    
    async def format_teams_message(self, 
                                  content: str,
                                  message_type: str = "text") -> Dict[str, Any]:
        """Call the format_teams_message MCP tool"""
        return await self.call_mcp_tool("format_teams_message", {
            "content": content,
            "message_type": message_type
        })
    
    def is_connected(self) -> bool:
        """Check if connection has been validated"""
        return self._connection_validated
    
    async def close(self):
        """Close the connector and cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("MCP connector closed")

# Utility function to create MCP connector
def create_mcp_connector(mcp_url: str, api_key: Optional[str] = None) -> MCPConnector:
    """Create and return an MCP connector instance"""
    return MCPConnector(mcp_url, api_key)