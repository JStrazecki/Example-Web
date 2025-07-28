"""
Intelligent MCP Tools with AI-Powered Analysis
Enhanced Power BI MCP tools with Azure OpenAI reasoning capabilities
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..config import ConfigManager
from ..powerbi import PowerBIClient
from ..auth import PowerBIAuthManager
from ..ai import (
    AzureOpenAIClient, 
    PowerBIContextBuilder, 
    PowerBIReasoningEngine,
    TeamsResponseFormatter
)
from ..ai.azure_openai_client import AzureOpenAIConfig

logger = logging.getLogger(__name__)

class IntelligentPowerBIAnalyzer:
    """
    AI-powered Power BI analyzer with reasoning capabilities
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        
        # Initialize components
        self.powerbi_client = None
        self.reasoning_engine = None
        self.response_formatter = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize AI and Power BI components"""
        try:
            # Initialize Power BI client
            if self.config.powerbi:
                auth_manager = PowerBIAuthManager(
                    tenant_id=self.config.powerbi.tenant_id,
                    client_id=self.config.powerbi.client_id,
                    client_secret=self.config.powerbi.client_secret
                )
                self.powerbi_client = PowerBIClient(auth_manager)
                logger.info("Power BI client initialized for AI analysis")
            
            # Initialize AI components if configured
            if self.config.azure_openai and self.powerbi_client:
                # Azure OpenAI client
                openai_config = AzureOpenAIConfig(
                    endpoint=self.config.azure_openai.endpoint,
                    api_key=self.config.azure_openai.api_key,
                    deployment_name=self.config.azure_openai.deployment_name,
                    api_version=self.config.azure_openai.api_version,
                    max_tokens=self.config.azure_openai.max_tokens,
                    temperature=self.config.azure_openai.temperature
                )
                openai_client = AzureOpenAIClient(openai_config)
                
                # Context builder
                context_builder = PowerBIContextBuilder(self.powerbi_client)
                
                # Reasoning engine
                self.reasoning_engine = PowerBIReasoningEngine(
                    openai_client=openai_client,
                    context_builder=context_builder,
                    powerbi_client=self.powerbi_client
                )
                
                # Response formatter
                self.response_formatter = TeamsResponseFormatter()
                
                logger.info("AI reasoning components initialized successfully")
            else:
                logger.warning("AI components not initialized - missing Azure OpenAI or Power BI configuration")
                
        except Exception as e:
            logger.error(f"Error initializing intelligent analyzer: {e}", exc_info=True)
    
    async def intelligent_analysis(self, user_question: str, analysis_depth: str = "standard") -> Dict[str, Any]:
        """
        Perform intelligent Power BI analysis with AI reasoning
        """
        if not self.reasoning_engine:
            return {
                "success": False,
                "error": "AI reasoning engine not available",
                "fallback": True,
                "message": "Please configure Azure OpenAI settings to enable intelligent analysis"
            }
        
        try:
            logger.info(f"Starting intelligent analysis: {user_question[:50]}...")
            
            # Perform AI-powered analysis
            result = await self.reasoning_engine.analyze_request(
                user_query=user_question,
                analysis_depth=analysis_depth
            )
            
            # Format response for MCP
            response_data = {
                "success": result.success,
                "response": result.response,
                "thinking_summary": {
                    "intent": result.thinking.user_intent,
                    "confidence": result.thinking.confidence_score,
                    "analysis_steps": len(result.thinking.reasoning_steps),
                    "queries_executed": len(result.thinking.dax_queries)
                },
                "data_summary": {
                    "rows_analyzed": len(result.data),
                    "datasets_used": result.datasets_used,
                    "execution_time_ms": result.execution_time_ms
                },
                "metadata": {
                    "analysis_type": "intelligent_ai_powered",
                    "timestamp": datetime.now().isoformat(),
                    "ai_enabled": True
                }
            }
            
            if not result.success:
                response_data["error"] = result.error_message
                response_data["warnings"] = result.warnings
            
            logger.info(f"Intelligent analysis completed: {result.success}")
            return response_data
            
        except Exception as e:
            logger.error(f"Intelligent analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Analysis error: {str(e)}",
                "fallback": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def smart_dax_generation(self, natural_language_request: str, dataset_context: str = "auto") -> Dict[str, Any]:
        """
        Generate smart DAX queries with business context
        """
        if not self.reasoning_engine:
            return {
                "success": False,
                "error": "AI reasoning not available for DAX generation"
            }
        
        try:
            # Build context for DAX generation
            context = await self.reasoning_engine.context_builder.build_context(natural_language_request)
            
            # Generate DAX with AI
            if self.reasoning_engine.openai_client:
                schema_context = {
                    "tables": [ds.name for ds in context.relevant_datasets],
                    "workspace_names": [ds.workspace_name for ds in context.relevant_datasets],
                    "intent": context.intent,
                    "business_domain": context.business_context.domain
                }
                
                dax_result = await self.reasoning_engine.openai_client.generate_dax_query(
                    intent=natural_language_request,
                    schema_context=schema_context
                )
                
                return {
                    "success": True,
                    "dax_query": dax_result.get("primary_query", ""),
                    "alternatives": dax_result.get("alternative_queries", []),
                    "explanation": dax_result.get("explanation", ""),
                    "confidence": dax_result.get("confidence", 0.5),
                    "context_used": {
                        "datasets": len(context.relevant_datasets),
                        "intent": context.intent,
                        "complexity": context.estimated_complexity
                    }
                }
            else:
                return {"success": False, "error": "OpenAI client not available"}
                
        except Exception as e:
            logger.error(f"Smart DAX generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"DAX generation error: {str(e)}"
            }
    
    async def business_insights_analysis(self, data_question: str, analysis_depth: str = "standard") -> Dict[str, Any]:
        """
        Perform business intelligence analysis with insights and recommendations
        """
        # This delegates to intelligent_analysis with specific formatting for business insights
        result = await self.intelligent_analysis(data_question, analysis_depth)
        
        if result.get("success"):
            # Enhance with business-specific formatting
            result["analysis_type"] = "business_insights"
            result["insights_focused"] = True
            
            # Add business context
            if "thinking_summary" in result:
                result["business_context"] = {
                    "domain": "Business Intelligence",
                    "focus": "Insights and Recommendations",
                    "decision_support": True
                }
        
        return result
    
    def get_analyzer_status(self) -> Dict[str, Any]:
        """Get status of the intelligent analyzer"""
        return {
            "ai_enabled": bool(self.reasoning_engine),
            "powerbi_connected": bool(self.powerbi_client),
            "azure_openai_configured": bool(self.config.azure_openai),
            "reasoning_engine_ready": bool(self.reasoning_engine),
            "components": {
                "powerbi_client": bool(self.powerbi_client),
                "reasoning_engine": bool(self.reasoning_engine),
                "response_formatter": bool(self.response_formatter)
            },
            "configuration": {
                "thinking_enabled": self.config.azure_openai.thinking_enabled if self.config.azure_openai else False,
                "analysis_depth": self.config.azure_openai.analysis_depth if self.config.azure_openai else "standard",
                "response_style": self.config.azure_openai.response_style if self.config.azure_openai else "business"
            },
            "statistics": self.reasoning_engine.get_statistics() if self.reasoning_engine else {}
        }

def create_intelligent_mcp_tools(config_manager: ConfigManager) -> List[Dict[str, Any]]:
    """
    Create intelligent MCP tools with AI capabilities
    """
    # Initialize the intelligent analyzer
    analyzer = IntelligentPowerBIAnalyzer(config_manager)
    
    # Define intelligent MCP tools
    tools = [
        {
            "name": "intelligent_powerbi_analysis",
            "description": """
            Perform intelligent Power BI analysis with AI reasoning.
            
            This tool uses Azure OpenAI to understand your business questions,
            analyze Power BI data with context awareness, and provide insights
            with professional formatting suitable for Teams or executive reporting.
            
            Examples:
            - "What were our top performing products last quarter?"
            - "Show me sales trends by region for the past 6 months"
            - "Which customers have the highest lifetime value?"
            - "Analyze our Q3 performance against targets"
            """,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_question": {
                        "type": "string",
                        "description": "Your business question or analysis request in natural language"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["standard", "deep", "extensive"],
                        "default": "standard",
                        "description": "Depth of analysis: standard (quick insights), deep (detailed analysis), extensive (comprehensive report)"
                    }
                },
                "required": ["user_question"]
            },
            "handler": analyzer.intelligent_analysis
        },
        
        {
            "name": "smart_dax_query",
            "description": """
            Generate and execute smart DAX queries with business context.
            
            Uses AI to understand your natural language request and generate
            optimized DAX queries with business logic and best practices.
            """,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "natural_language_request": {
                        "type": "string",
                        "description": "Describe what you want to calculate or analyze in natural language"
                    },
                    "dataset_context": {
                        "type": "string",
                        "default": "auto",
                        "description": "Dataset context (auto-detected if not specified)"
                    }
                },
                "required": ["natural_language_request"]
            },
            "handler": analyzer.smart_dax_generation
        },
        
        {
            "name": "business_insights_analysis",
            "description": """
            Perform business intelligence analysis with insights and recommendations.
            
            Focused on extracting actionable business insights, trends, and
            strategic recommendations from your Power BI data.
            """,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data_question": {
                        "type": "string",
                        "description": "Your business question focusing on insights and strategy"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["standard", "deep", "extensive"],
                        "default": "standard",
                        "description": "Depth of business analysis"
                    }
                },
                "required": ["data_question"]
            },
            "handler": analyzer.business_insights_analysis
        },
        
        {
            "name": "ai_analyzer_status",
            "description": """
            Get status and statistics of the AI-powered analysis system.
            
            Shows configuration, component health, and usage statistics.
            """,
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            },
            "handler": lambda: analyzer.get_analyzer_status()
        }
    ]
    
    # Add traditional tools as fallbacks if AI is not configured
    if not analyzer.reasoning_engine:
        logger.warning("AI reasoning not available - adding fallback tools")
        tools.extend(_create_fallback_tools(config_manager))
    
    return tools

def _create_fallback_tools(config_manager: ConfigManager) -> List[Dict[str, Any]]:
    """Create fallback tools when AI is not available"""
    
    async def fallback_analysis(user_question: str, **kwargs) -> Dict[str, Any]:
        return {
            "success": False,
            "error": "AI analysis not available",
            "fallback_message": "Please configure Azure OpenAI settings to enable intelligent analysis",
            "suggestion": "Use basic Power BI tools for now: list_powerbi_workspaces, execute_dax_query"
        }
    
    return [
        {
            "name": "powerbi_analysis_fallback",
            "description": "Fallback analysis when AI is not configured",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_question": {"type": "string"}
                },
                "required": ["user_question"]
            },
            "handler": fallback_analysis
        }
    ]