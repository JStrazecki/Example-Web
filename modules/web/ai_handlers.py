"""
AI-Enhanced Web API Handlers
Web API endpoints that integrate with the AI reasoning system
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

from aiohttp import web, ClientSession
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from ..config import ConfigManager
from ..mcp import IntelligentPowerBIAnalyzer

logger = logging.getLogger(__name__)

class AIWebHandlers:
    """
    Web handlers for AI-powered Power BI analysis
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.analyzer = IntelligentPowerBIAnalyzer(config_manager)
    
    async def intelligent_analysis_handler(self, request: Request) -> Response:
        """
        Handle intelligent Power BI analysis requests
        """
        try:
            # Parse request data
            data = await request.json()
            
            user_question = data.get("question", "")
            analysis_depth = data.get("depth", "standard")
            
            if not user_question:
                return web.json_response({
                    "success": False,
                    "error": "Question parameter is required"
                }, status=400)
            
            logger.info(f"AI analysis request: {user_question[:50]}...")
            
            # Perform intelligent analysis
            result = await self.analyzer.intelligent_analysis(
                user_question=user_question,
                analysis_depth=analysis_depth
            )
            
            # Add request metadata
            result["request_metadata"] = {
                "question": user_question,
                "depth": analysis_depth,
                "timestamp": datetime.now().isoformat(),
                "client_ip": request.remote,
                "user_agent": request.headers.get("User-Agent", "Unknown")
            }
            
            status_code = 200 if result.get("success") else 500
            return web.json_response(result, status=status_code)
            
        except json.JSONDecodeError:
            return web.json_response({
                "success": False,
                "error": "Invalid JSON in request body"
            }, status=400)
        except Exception as e:
            logger.error(f"AI analysis handler error: {e}", exc_info=True)
            return web.json_response({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status=500)
    
    async def smart_dax_handler(self, request: Request) -> Response:
        """
        Handle smart DAX query generation requests
        """
        try:
            data = await request.json()
            
            natural_request = data.get("request", "")
            dataset_context = data.get("dataset_context", "auto")
            
            if not natural_request:
                return web.json_response({
                    "success": False,
                    "error": "Request parameter is required"
                }, status=400)
            
            logger.info(f"Smart DAX request: {natural_request[:50]}...")
            
            # Generate smart DAX
            result = await self.analyzer.smart_dax_generation(
                natural_language_request=natural_request,
                dataset_context=dataset_context
            )
            
            # Add metadata
            result["request_metadata"] = {
                "natural_request": natural_request,
                "dataset_context": dataset_context,
                "timestamp": datetime.now().isoformat()
            }
            
            status_code = 200 if result.get("success") else 500
            return web.json_response(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Smart DAX handler error: {e}", exc_info=True)
            return web.json_response({
                "success": False,
                "error": f"DAX generation error: {str(e)}"
            }, status=500)
    
    async def business_insights_handler(self, request: Request) -> Response:
        """
        Handle business insights analysis requests
        """
        try:
            data = await request.json()
            
            question = data.get("question", "")
            depth = data.get("depth", "standard")
            
            if not question:
                return web.json_response({
                    "success": False,
                    "error": "Question parameter is required"
                }, status=400)
            
            logger.info(f"Business insights request: {question[:50]}...")
            
            # Perform business analysis
            result = await self.analyzer.business_insights_analysis(
                data_question=question,
                analysis_depth=depth
            )
            
            # Enhance with business-specific metadata
            result["business_metadata"] = {
                "analysis_focus": "Business Insights",
                "decision_support": True,
                "executive_summary": True,
                "recommendations_included": True
            }
            
            status_code = 200 if result.get("success") else 500
            return web.json_response(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Business insights handler error: {e}", exc_info=True)
            return web.json_response({
                "success": False,
                "error": f"Business analysis error: {str(e)}"
            }, status=500)
    
    async def ai_status_handler(self, request: Request) -> Response:
        """
        Handle AI system status requests
        """
        try:
            status = self.analyzer.get_analyzer_status()
            
            # Add system information
            status["system_info"] = {
                "timestamp": datetime.now().isoformat(),
                "configuration_loaded": bool(self.config),
                "web_server_active": True
            }
            
            return web.json_response(status)
            
        except Exception as e:
            logger.error(f"AI status handler error: {e}", exc_info=True)
            return web.json_response({
                "success": False,
                "error": f"Status check error: {str(e)}"
            }, status=500)
    
    async def ai_health_check(self, request: Request) -> Response:
        """
        Health check endpoint for AI services
        """
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "ai_analyzer": "healthy" if self.analyzer else "unavailable",
                    "azure_openai": "configured" if self.config.azure_openai else "not_configured",
                    "powerbi": "configured" if self.config.powerbi else "not_configured"
                },
                "version": "1.0.0"
            }
            
            # Check component health
            if not self.analyzer.reasoning_engine:
                health_status["status"] = "degraded"
                health_status["warnings"] = ["AI reasoning engine not available"]
            
            if not self.config.azure_openai:
                health_status["status"] = "limited"
                health_status["limitations"] = ["Azure OpenAI not configured - using fallback mode"]
            
            return web.json_response(health_status)
            
        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=500)

def create_ai_routes(config_manager: ConfigManager) -> list:
    """
    Create AI-enhanced web routes
    """
    handlers = AIWebHandlers(config_manager)
    
    routes = [
        # AI Analysis Routes
        web.post('/ai/analyze', handlers.intelligent_analysis_handler),
        web.post('/ai/dax', handlers.smart_dax_handler),  
        web.post('/ai/insights', handlers.business_insights_handler),
        
        # AI System Routes
        web.get('/ai/status', handlers.ai_status_handler),
        web.get('/ai/health', handlers.ai_health_check),
        
        # Alternative endpoint names for compatibility
        web.post('/api/ai/analysis', handlers.intelligent_analysis_handler),
        web.post('/api/ai/smart-dax', handlers.smart_dax_handler),
        web.post('/api/ai/business-insights', handlers.business_insights_handler)
    ]
    
    return routes

def create_ai_documentation() -> Dict[str, Any]:
    """
    Create API documentation for AI endpoints
    """
    return {
        "ai_endpoints": {
            "/ai/analyze": {
                "method": "POST",
                "description": "Perform intelligent Power BI analysis with AI reasoning",
                "parameters": {
                    "question": "Your business question in natural language",
                    "depth": "Analysis depth: standard, deep, or extensive"
                },
                "example": {
                    "question": "What were our top performing products last quarter?",
                    "depth": "standard"
                }
            },
            "/ai/dax": {
                "method": "POST",
                "description": "Generate smart DAX queries from natural language",
                "parameters": {
                    "request": "Natural language description of what to calculate",
                    "dataset_context": "Dataset context (auto-detected if not specified)"
                },
                "example": {
                    "request": "Calculate total sales by product category for this year",
                    "dataset_context": "auto"
                }
            },
            "/ai/insights": {
                "method": "POST", 
                "description": "Perform business intelligence analysis with insights",
                "parameters": {
                    "question": "Business question focusing on insights",
                    "depth": "Analysis depth level"
                },
                "example": {
                    "question": "What trends should we focus on for Q4 planning?",
                    "depth": "deep"
                }
            },
            "/ai/status": {
                "method": "GET",
                "description": "Get AI system status and statistics",
                "parameters": {},
                "example": {}
            },
            "/ai/health": {
                "method": "GET",
                "description": "Health check for AI services",
                "parameters": {},
                "example": {}
            }
        },
        "authentication": "Inherits from main application authentication",
        "rate_limits": "Standard application rate limits apply",
        "response_format": "JSON with success flag, data, and metadata"
    }