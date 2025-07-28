"""
Web Server for Power BI MCP Web Application
Provides HTTP API and web interface
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from aiohttp import web, ClientError
from aiohttp.web import Request, Response, RouteTableDef
import aiohttp_cors

from .mcp_connector import MCPConnector
from .api_handlers import APIHandlers
from .ai_handlers import create_ai_routes, create_ai_documentation
from ..config import ConfigManager

logger = logging.getLogger(__name__)

class WebServer:
    """Web server for Power BI MCP application"""
    
    def __init__(self, 
                 mcp_url: str, 
                 mcp_api_key: Optional[str] = None,
                 host: str = "0.0.0.0",
                 port: int = 8080,
                 config_manager: Optional[ConfigManager] = None):
        
        self.mcp_url = mcp_url
        self.mcp_api_key = mcp_api_key
        self.host = host
        self.port = port
        self.config_manager = config_manager
        
        # Initialize MCP connector
        self.mcp_connector = MCPConnector(mcp_url, mcp_api_key)
        
        # Initialize API handlers
        self.api_handlers = APIHandlers(self.mcp_connector)
        
        # Create web application
        self.app = self._create_app()
    
    def _create_app(self) -> web.Application:
        """Create and configure the web application"""
        app = web.Application()
        
        # Add routes
        self._add_routes(app)
        
        # Add CORS support
        self._add_cors(app)
        
        # Add error handling middleware
        app.middlewares.append(self._error_middleware)
        
        # Add request logging middleware
        app.middlewares.append(self._logging_middleware)
        
        return app
    
    def _add_routes(self, app: web.Application):
        """Add all routes to the application"""
        routes = web.RouteTableDef()
        
        # Health and info endpoints
        routes.get('/health', self._health_handler)
        routes.get('/info', self._info_handler)
        routes.get('/status', self._status_handler)
        
        # MCP connection endpoints
        routes.get('/mcp/status', self.api_handlers.mcp_status)
        routes.get('/mcp/tools', self.api_handlers.list_mcp_tools)
        routes.post('/mcp/tools/{tool_name}', self.api_handlers.call_mcp_tool)
        
        # Power BI endpoints (proxied through MCP)
        routes.get('/api/powerbi/workspaces', self.api_handlers.list_workspaces)
        routes.get('/api/powerbi/workspaces/{workspace_name}/datasets', self.api_handlers.list_datasets)
        routes.post('/api/powerbi/query', self.api_handlers.execute_dax_query)
        
        # Teams integration endpoints
        routes.post('/api/teams/format', self.api_handlers.format_teams_message)
        
        # Static file serving for web interface
        routes.get('/', self._web_interface_handler)
        routes.get('/dashboard', self._dashboard_handler)
        
        app.add_routes(routes)
        
        # Add AI-enhanced routes if config manager is available
        if self.config_manager:
            ai_routes = create_ai_routes(self.config_manager)
            app.add_routes(ai_routes)
            logger.info("AI-enhanced routes added to web server")
    
    def _add_cors(self, app: web.Application):
        """Add CORS support"""
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
    
    @web.middleware
    async def _error_middleware(self, request: Request, handler):
        """Global error handling middleware"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error in {request.method} {request.path}: {e}", exc_info=True)
            return web.json_response({
                "error": "Internal server error",
                "message": str(e),
                "path": request.path,
                "method": request.method
            }, status=500)
    
    @web.middleware
    async def _logging_middleware(self, request: Request, handler):
        """Request logging middleware"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await handler(request)
            
            # Log successful requests
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.info(f"{request.method} {request.path} - {response.status} - {duration:.2f}ms")
            
            return response
        except Exception as e:
            # Log errors
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"{request.method} {request.path} - ERROR - {duration:.2f}ms: {e}")
            raise
    
    async def _health_handler(self, request: Request) -> Response:
        """Health check endpoint"""
        # Check MCP connection
        mcp_status = await self.mcp_connector.validate_connection()
        
        health_data = {
            "status": "healthy" if mcp_status["status"] == "connected" else "unhealthy",
            "service": "Power BI MCP Web Application",
            "version": "1.0.0",
            "timestamp": "2025-01-28T00:00:00Z",  # Would use real timestamp
            "components": {
                "web_server": "healthy",
                "mcp_connection": mcp_status["status"]
            },
            "mcp_server": mcp_status
        }
        
        status_code = 200 if health_data["status"] == "healthy" else 503
        return web.json_response(health_data, status=status_code)
    
    async def _info_handler(self, request: Request) -> Response:
        """Service information endpoint"""
        info_data = {
            "name": "Power BI MCP Web Application",
            "version": "1.0.0",
            "description": "Web interface for Power BI MCP server integration with AI capabilities",
            "mcp_server": self.mcp_url,
            "endpoints": {
                "/health": "Health check",
                "/info": "Service information",
                "/status": "Detailed status",
                "/mcp/status": "MCP server status",
                "/mcp/tools": "List available MCP tools",
                "/api/powerbi/workspaces": "List Power BI workspaces",
                "/api/powerbi/query": "Execute DAX queries",
                "/dashboard": "Web dashboard"
            },
            "features": {
                "mcp_integration": True,
                "powerbi_proxy": True,
                "teams_formatting": True,
                "web_dashboard": True,
                "ai_reasoning": bool(self.config_manager and self.config_manager.azure_openai)
            }
        }
        
        # Add AI endpoints if available
        if self.config_manager and self.config_manager.azure_openai:
            ai_endpoints = {
                "/ai/analyze": "Intelligent Power BI analysis",
                "/ai/dax": "Smart DAX query generation", 
                "/ai/insights": "Business insights analysis",
                "/ai/status": "AI system status",
                "/ai/health": "AI health check"
            }
            info_data["endpoints"].update(ai_endpoints)
            info_data["ai_documentation"] = create_ai_documentation()
        
        return web.json_response(info_data)
    
    async def _status_handler(self, request: Request) -> Response:
        \"\"\"Detailed status endpoint\"\"\"
        # Validate MCP connection
        mcp_status = await self.mcp_connector.validate_connection()
        
        # Get available tools if connected
        tools_info = {"available": False, "count": 0, "tools": []}
        if mcp_status["status"] == "connected":
            tools_result = await self.mcp_connector.list_available_tools()
            if tools_result["success"]:
                tools_info = {
                    "available": True,
                    "count": tools_result["count"],
                    "tools": [tool["name"] for tool in tools_result["tools"]]
                }
        
        return web.json_response({
            "service": {
                "name": "Power BI MCP Web Application",
                "version": "1.0.0",
                "status": "running",
                "uptime": "N/A"  # Would calculate actual uptime
            },
            "mcp_connection": mcp_status,
            "mcp_tools": tools_info,
            "configuration": {
                "mcp_url": self.mcp_url,
                "has_api_key": bool(self.mcp_api_key),
                "host": self.host,
                "port": self.port
            }
        })
    
    async def _web_interface_handler(self, request: Request) -> Response:
        \"\"\"Serve the main web interface\"\"\"
        html_content = \"\"\"
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Power BI MCP Web Application</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; border-bottom: 3px solid #0078d4; padding-bottom: 10px; }
                .status-card { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #0078d4; }
                .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
                .endpoint-card { background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 6px; }
                .endpoint-card h3 { margin-top: 0; color: #0078d4; }
                button { background: #0078d4; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
                button:hover { background: #106ebe; }
                .json-result { background: #f8f9fa; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Power BI MCP Web Application</h1>
                
                <div class="status-card">
                    <h2>📊 Service Status</h2>
                    <p>This web application provides a modular interface to your deployed Power BI MCP server.</p>
                    <button onclick="checkStatus()">Check Status</button>
                    <div id="status-result" class="json-result" style="display:none;"></div>
                </div>
                
                <div class="endpoints">
                    <div class="endpoint-card">
                        <h3>🏢 Workspaces</h3>
                        <p>List all accessible Power BI workspaces</p>
                        <button onclick="listWorkspaces()">List Workspaces</button>
                        <div id="workspaces-result" class="json-result" style="display:none;"></div>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>🔧 MCP Tools</h3>
                        <p>View available MCP tools on the server</p>
                        <button onclick="listTools()">List Tools</button>
                        <div id="tools-result" class="json-result" style="display:none;"></div>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>⚡ DAX Query</h3>
                        <p>Execute DAX queries against datasets</p>
                        <input type="text" id="workspace-input" placeholder="Workspace name" style="width:100%; margin:5px 0; padding:8px;">
                        <input type="text" id="dataset-input" placeholder="Dataset name" style="width:100%; margin:5px 0; padding:8px;">
                        <textarea id="dax-input" placeholder="DAX Query" style="width:100%; height:60px; margin:5px 0; padding:8px;"></textarea>
                        <button onclick="executeDax()">Execute Query</button>
                        <div id="dax-result" class="json-result" style="display:none;"></div>
                    </div>
                </div>
                
                <div class="status-card">
                    <h2>🔗 API Endpoints</h2>
                    <ul>
                        <li><strong>GET /health</strong> - Health check</li>
                        <li><strong>GET /status</strong> - Detailed status</li>
                        <li><strong>GET /api/powerbi/workspaces</strong> - List workspaces</li>
                        <li><strong>POST /api/powerbi/query</strong> - Execute DAX query</li>
                        <li><strong>GET /mcp/tools</strong> - List MCP tools</li>
                    </ul>
                </div>
            </div>
            
            <script>
                async function checkStatus() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        document.getElementById('status-result').style.display = 'block';
                        document.getElementById('status-result').textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        document.getElementById('status-result').style.display = 'block';
                        document.getElementById('status-result').textContent = 'Error: ' + error.message;
                    }
                }
                
                async function listWorkspaces() {
                    try {
                        const response = await fetch('/api/powerbi/workspaces');
                        const data = await response.json();
                        document.getElementById('workspaces-result').style.display = 'block';
                        document.getElementById('workspaces-result').textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        document.getElementById('workspaces-result').style.display = 'block';
                        document.getElementById('workspaces-result').textContent = 'Error: ' + error.message;
                    }
                }
                
                async function listTools() {
                    try {
                        const response = await fetch('/mcp/tools');
                        const data = await response.json();
                        document.getElementById('tools-result').style.display = 'block';
                        document.getElementById('tools-result').textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        document.getElementById('tools-result').style.display = 'block';
                        document.getElementById('tools-result').textContent = 'Error: ' + error.message;
                    }
                }
                
                async function executeDax() {
                    const workspace = document.getElementById('workspace-input').value;
                    const dataset = document.getElementById('dataset-input').value; 
                    const dax = document.getElementById('dax-input').value;
                    
                    if (!workspace || !dataset || !dax) {
                        alert('Please fill in all fields');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/powerbi/query', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                workspace_name: workspace,
                                dataset_name: dataset,
                                dax_query: dax
                            })
                        });
                        const data = await response.json();
                        document.getElementById('dax-result').style.display = 'block';
                        document.getElementById('dax-result').textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                        document.getElementById('dax-result').style.display = 'block';
                        document.getElementById('dax-result').textContent = 'Error: ' + error.message;
                    }
                }
            </script>
        </body>
        </html>
        \"\"\"
        
        return web.Response(text=html_content, content_type='text/html')
    
    async def _dashboard_handler(self, request: Request) -> Response:
        \"\"\"Serve the dashboard interface\"\"\"
        return await self._web_interface_handler(request)
    
    async def start(self):
        \"\"\"Start the web server\"\"\"
        logger.info(f"Starting Power BI MCP Web Server on {self.host}:{self.port}")
        logger.info(f"MCP Server: {self.mcp_url}")
        logger.info(f"Web Interface: http://{self.host}:{self.port}")
        logger.info(f"API Documentation: http://{self.host}:{self.port}/info")
        
        # Validate MCP connection
        async with self.mcp_connector:
            connection_status = await self.mcp_connector.validate_connection()
            if connection_status["status"] == "connected":
                logger.info("✅ MCP server connection validated")
            else:
                logger.warning(f"⚠️ MCP server connection issue: {connection_status['error']}")
        
        # Start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info("✅ Web server started successfully")
        
        return runner
    
    async def cleanup(self):
        \"\"\"Cleanup resources\"\"\"
        await self.mcp_connector.close()
        logger.info("Web server cleanup complete")