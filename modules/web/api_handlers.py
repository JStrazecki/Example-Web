"""
API Handlers for Power BI MCP Web Application
"""

import json
import logging
from typing import Dict, Any
from aiohttp.web import Request, Response, json_response

from .mcp_connector import MCPConnector

logger = logging.getLogger(__name__)

class APIHandlers:
    """HTTP API handlers for Power BI MCP operations"""
    
    def __init__(self, mcp_connector: MCPConnector):
        self.mcp_connector = mcp_connector
    
    async def mcp_status(self, request: Request) -> Response:
        """Get MCP server connection status"""
        try:
            async with self.mcp_connector:
                status = await self.mcp_connector.validate_connection()
                return json_response(status)
        except Exception as e:
            logger.error(f"Error checking MCP status: {e}")
            return json_response({
                "status": "error",
                "error": str(e)
            }, status=500)
    
    async def list_mcp_tools(self, request: Request) -> Response:
        """List available MCP tools"""
        try:
            async with self.mcp_connector:
                tools = await self.mcp_connector.list_available_tools()
                return json_response(tools)
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def call_mcp_tool(self, request: Request) -> Response:
        """Call a specific MCP tool"""
        tool_name = request.match_info['tool_name']
        
        try:
            # Get request body
            if request.content_type == 'application/json':
                body = await request.json()
                arguments = body.get('arguments', {})
            else:
                arguments = {}
            
            async with self.mcp_connector:
                result = await self.mcp_connector.call_mcp_tool(tool_name, arguments)
                
                if result["success"]:
                    return json_response(result)
                else:
                    return json_response(result, status=400)
                    
        except json.JSONDecodeError as e:
            return json_response({
                "success": False,
                "error": f"Invalid JSON in request body: {str(e)}"
            }, status=400)
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return json_response({
                "success": False,
                "error": str(e),
                "tool": tool_name
            }, status=500)
    
    async def list_workspaces(self, request: Request) -> Response:
        """List Power BI workspaces via MCP"""
        try:
            async with self.mcp_connector:
                result = await self.mcp_connector.list_powerbi_workspaces()
                
                if result["success"]:
                    # Parse the JSON result from MCP
                    mcp_result = result["result"]
                    if isinstance(mcp_result, str):
                        workspace_data = json.loads(mcp_result)
                    else:
                        workspace_data = mcp_result
                    
                    return json_response({
                        "success": True,
                        "workspaces": workspace_data.get("workspaces", []),
                        "count": len(workspace_data.get("workspaces", [])),
                        "execution_time": result.get("execution_time"),
                        "timestamp": result.get("timestamp")
                    })
                else:
                    return json_response({
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                        "workspaces": []
                    }, status=400)
                    
        except Exception as e:
            logger.error(f"Error listing workspaces: {e}")
            return json_response({
                "success": False,
                "error": str(e),
                "workspaces": []
            }, status=500)
    
    async def list_datasets(self, request: Request) -> Response:
        """List datasets in a Power BI workspace via MCP"""
        workspace_name = request.match_info['workspace_name']
        
        try:
            async with self.mcp_connector:
                result = await self.mcp_connector.list_powerbi_datasets(workspace_name)
                
                if result["success"]:
                    # Parse the JSON result from MCP
                    mcp_result = result["result"]
                    if isinstance(mcp_result, str):
                        dataset_data = json.loads(mcp_result)
                    else:
                        dataset_data = mcp_result
                    
                    return json_response({
                        "success": True,
                        "workspace": workspace_name,
                        "datasets": dataset_data.get("datasets", []),
                        "count": len(dataset_data.get("datasets", [])),
                        "execution_time": result.get("execution_time"),
                        "timestamp": result.get("timestamp")
                    })
                else:
                    return json_response({
                        "success": False,
                        "workspace": workspace_name,
                        "error": result.get("error", "Unknown error"),
                        "datasets": []
                    }, status=400)
                    
        except Exception as e:
            logger.error(f"Error listing datasets for workspace {workspace_name}: {e}")
            return json_response({
                "success": False,
                "workspace": workspace_name,
                "error": str(e),
                "datasets": []
            }, status=500)
    
    async def execute_dax_query(self, request: Request) -> Response:
        """Execute DAX query via MCP"""
        try:
            # Get request body
            if request.content_type != 'application/json':
                return json_response({
                    "success": False,
                    "error": "Content-Type must be application/json"
                }, status=400)
            
            body = await request.json()
            
            # Validate required parameters
            required_params = ['workspace_name', 'dataset_name', 'dax_query']
            missing_params = [param for param in required_params if param not in body]
            
            if missing_params:
                return json_response({
                    "success": False,
                    "error": f"Missing required parameters: {', '.join(missing_params)}"
                }, status=400)
            
            workspace_name = body['workspace_name']
            dataset_name = body['dataset_name']
            dax_query = body['dax_query']
            
            # Validate DAX query is not empty
            if not dax_query.strip():
                return json_response({
                    "success": False,
                    "error": "DAX query cannot be empty"
                }, status=400)
            
            async with self.mcp_connector:
                result = await self.mcp_connector.execute_dax_query(
                    workspace_name, 
                    dataset_name, 
                    dax_query
                )
                
                if result["success"]:
                    # Parse the JSON result from MCP
                    mcp_result = result["result"]
                    if isinstance(mcp_result, str):
                        try:
                            query_data = json.loads(mcp_result)
                        except json.JSONDecodeError:
                            # If it's not JSON, treat as plain text result
                            query_data = {"raw_result": mcp_result}
                    else:
                        query_data = mcp_result
                    
                    return json_response({
                        "success": True,
                        "workspace": workspace_name,
                        "dataset": dataset_name,
                        "dax_query": dax_query,
                        "result": query_data,
                        "row_count": len(query_data) if isinstance(query_data, list) else None,
                        "execution_time": result.get("execution_time"),
                        "timestamp": result.get("timestamp")
                    })
                else:
                    return json_response({
                        "success": False,
                        "workspace": workspace_name,
                        "dataset": dataset_name,
                        "dax_query": dax_query,
                        "error": result.get("error", "Unknown error")
                    }, status=400)
                    
        except json.JSONDecodeError as e:
            return json_response({
                "success": False,
                "error": f"Invalid JSON in request body: {str(e)}"
            }, status=400)
        except Exception as e:
            logger.error(f"Error executing DAX query: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def format_teams_message(self, request: Request) -> Response:
        """Format content for Teams message display via MCP"""
        try:
            # Get request body
            if request.content_type != 'application/json':
                return json_response({
                    "success": False,
                    "error": "Content-Type must be application/json"
                }, status=400)
            
            body = await request.json()
            
            # Validate required parameters
            if 'content' not in body:
                return json_response({
                    "success": False,
                    "error": "Missing required parameter: content"
                }, status=400)
            
            content = body['content']
            message_type = body.get('message_type', 'text')
            
            async with self.mcp_connector:
                result = await self.mcp_connector.format_teams_message(content, message_type)
                
                if result["success"]:
                    # Parse the JSON result from MCP
                    mcp_result = result["result"]
                    if isinstance(mcp_result, str):
                        try:
                            formatted_data = json.loads(mcp_result)
                        except json.JSONDecodeError:
                            formatted_data = {"formatted_content": mcp_result}
                    else:
                        formatted_data = mcp_result
                    
                    return json_response({
                        "success": True,
                        "original_content": content,
                        "message_type": message_type,
                        "formatted": formatted_data,
                        "execution_time": result.get("execution_time"),
                        "timestamp": result.get("timestamp")
                    })
                else:
                    return json_response({
                        "success": False,
                        "original_content": content,
                        "message_type": message_type,
                        "error": result.get("error", "Unknown error")
                    }, status=400)
                    
        except json.JSONDecodeError as e:
            return json_response({
                "success": False,
                "error": f"Invalid JSON in request body: {str(e)}"
            }, status=400)
        except Exception as e:
            logger.error(f"Error formatting Teams message: {e}")
            return json_response({
                "success": False,
                "error": str(e)
            }, status=500)