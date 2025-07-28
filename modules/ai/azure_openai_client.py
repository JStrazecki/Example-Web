"""
Azure OpenAI Client for Power BI Analysis
Handles intelligent communication with Azure OpenAI for reasoning and insights
"""

import logging
import json
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ThinkingProcess:
    """Represents the AI's internal thinking process"""
    user_intent: str
    analysis_plan: List[str]
    context_summary: str
    reasoning_steps: List[str]
    dax_queries: List[str]
    confidence_score: float
    timestamp: datetime

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration"""
    endpoint: str
    api_key: str
    deployment_name: str
    api_version: str = "2024-02-15-preview"
    max_tokens: int = 4000
    temperature: float = 0.3

class AzureOpenAIClient:
    """Enhanced Azure OpenAI client for Power BI analysis"""
    
    def __init__(self, config: AzureOpenAIConfig):
        self.config = config
        self.base_url = f"{config.endpoint.rstrip('/')}/openai/deployments/{config.deployment_name}"
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for Azure OpenAI"""
        return {
            "Content-Type": "application/json",
            "api-key": self.config.api_key
        }
    
    async def reasoning_analysis(self, 
                               user_query: str, 
                               context: Dict[str, Any]) -> ThinkingProcess:
        """
        Perform multi-step reasoning analysis with thinking process
        """
        reasoning_prompt = self._build_reasoning_prompt(user_query, context)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": reasoning_prompt
                        }
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "response_format": {"type": "json_object"}
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions?api-version={self.config.api_version}",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        thinking_data = json.loads(content)
                        
                        return ThinkingProcess(
                            user_intent=thinking_data.get("user_intent", ""),
                            analysis_plan=thinking_data.get("analysis_plan", []),
                            context_summary=thinking_data.get("context_summary", ""),
                            reasoning_steps=thinking_data.get("reasoning_steps", []),
                            dax_queries=thinking_data.get("dax_queries", []),
                            confidence_score=thinking_data.get("confidence_score", 0.5),
                            timestamp=datetime.now()
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Azure OpenAI reasoning failed: {response.status} - {error_text}")
                        return self._create_fallback_thinking(user_query)
                        
        except Exception as e:
            logger.error(f"Error in reasoning analysis: {e}", exc_info=True)
            return self._create_fallback_thinking(user_query)
    
    async def generate_dax_query(self, 
                               intent: str, 
                               schema_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized DAX queries based on user intent and schema
        """
        dax_prompt = self._build_dax_generation_prompt(intent, schema_context)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_dax_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": dax_prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions?api-version={self.config.api_version}",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
                    else:
                        error_text = await response.text()
                        logger.error(f"DAX generation failed: {response.status} - {error_text}")
                        return {"error": f"DAX generation failed: {error_text}"}
                        
        except Exception as e:
            logger.error(f"Error generating DAX query: {e}", exc_info=True)
            return {"error": f"DAX generation error: {str(e)}"}
    
    async def analyze_results(self, 
                            data: List[Dict[str, Any]], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query results and extract business insights
        """
        analysis_prompt = self._build_analysis_prompt(data, context)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_analysis_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"}
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions?api-version={self.config.api_version}",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
                    else:
                        error_text = await response.text()
                        logger.error(f"Results analysis failed: {response.status} - {error_text}")
                        return {"error": f"Analysis failed: {error_text}"}
                        
        except Exception as e:
            logger.error(f"Error analyzing results: {e}", exc_info=True)
            return {"error": f"Analysis error: {str(e)}"}
    
    async def format_business_response(self, 
                                     analysis: Dict[str, Any],
                                     thinking: ThinkingProcess) -> str:
        """
        Create clean, professional responses for Teams
        """
        formatting_prompt = self._build_formatting_prompt(analysis, thinking)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_formatting_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": formatting_prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.2
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions?api-version={self.config.api_version}",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Response formatting failed: {response.status} - {error_text}")
                        return self._create_fallback_response(analysis)
                        
        except Exception as e:
            logger.error(f"Error formatting response: {e}", exc_info=True)
            return self._create_fallback_response(analysis)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for reasoning analysis"""
        return """You are a Power BI business intelligence expert performing multi-step reasoning analysis.

Your task is to analyze user queries and create a structured thinking process. You must respond with valid JSON containing:

{
  "user_intent": "Clear description of what the user wants to accomplish",
  "analysis_plan": ["Step 1", "Step 2", "Step 3"],
  "context_summary": "Summary of available data and constraints",
  "reasoning_steps": ["Logical step 1", "Logical step 2", "Logical step 3"],
  "dax_queries": ["DAX query 1", "DAX query 2"],
  "confidence_score": 0.85
}

Focus on:
- Understanding business intent behind technical requests
- Creating logical analysis sequences
- Generating efficient DAX queries
- Providing confidence in your analysis approach"""
    
    def _get_dax_system_prompt(self) -> str:
        """Get system prompt for DAX generation"""
        return """You are a DAX expert for Power BI. Generate optimized DAX queries based on user requirements.

Respond with valid JSON:
{
  "primary_query": "Main DAX query",
  "alternative_queries": ["Alternative approach 1", "Alternative approach 2"],
  "explanation": "Why this approach is optimal",
  "estimated_performance": "Fast/Medium/Slow",
  "required_tables": ["Table1", "Table2"],
  "confidence": 0.9
}

Best practices:
- Use SUMMARIZE, CALCULATE, and FILTER efficiently
- Minimize table scans
- Consider date context and filters
- Optimize for performance"""
    
    def _get_analysis_system_prompt(self) -> str:
        """Get system prompt for results analysis"""
        return """You are a business intelligence analyst extracting insights from Power BI query results.

Respond with valid JSON:
{
  "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
  "trends_identified": ["Trend 1", "Trend 2"],
  "recommendations": ["Action 1", "Action 2"],
  "data_quality_notes": ["Note 1", "Note 2"],
  "confidence_level": "High/Medium/Low",
  "executive_summary": "Brief summary for leadership"
}

Focus on:
- Business-relevant insights, not just data description
- Actionable recommendations
- Trend identification and pattern recognition
- Executive-level communication"""
    
    def _get_formatting_system_prompt(self) -> str:
        """Get system prompt for response formatting"""
        return """You are a professional business communication specialist. Create clean, well-formatted responses for Microsoft Teams.

Guidelines:
- Use emojis strategically for visual appeal (📊 📈 📉 💡 ⚠️)
- Structure with clear headings and bullet points
- Lead with executive summary
- Include actionable insights
- Maintain professional tone
- Keep responses concise but comprehensive
- Use **bold** and *italics* for emphasis

Format for business stakeholders, not technical users."""
    
    def _build_reasoning_prompt(self, user_query: str, context: Dict[str, Any]) -> str:
        """Build reasoning analysis prompt"""
        return f"""Analyze this Power BI user query and create a structured thinking process:

USER QUERY: "{user_query}"

AVAILABLE CONTEXT:
- Workspaces: {context.get('workspaces', [])}
- Datasets: {context.get('datasets', [])}
- Time context: {context.get('time_context', 'Current period')}
- Business domain: {context.get('business_domain', 'General business')}

Create a comprehensive analysis plan with reasoning steps and potential DAX queries."""
    
    def _build_dax_generation_prompt(self, intent: str, schema_context: Dict[str, Any]) -> str:
        """Build DAX generation prompt"""
        return f"""Generate optimized DAX query for this business requirement:

INTENT: {intent}

SCHEMA CONTEXT:
Tables: {schema_context.get('tables', [])}
Key measures: {schema_context.get('measures', [])}
Date columns: {schema_context.get('date_columns', [])}
Relationships: {schema_context.get('relationships', [])}

Create efficient DAX that follows best practices and optimizes performance."""
    
    def _build_analysis_prompt(self, data: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Build results analysis prompt"""
        data_sample = data[:10] if len(data) > 10 else data
        return f"""Analyze these Power BI query results and extract business insights:

QUERY RESULTS (sample):
{json.dumps(data_sample, indent=2)}

TOTAL ROWS: {len(data)}

BUSINESS CONTEXT:
Query intent: {context.get('user_intent', 'Data analysis')}
Domain: {context.get('business_domain', 'General')}
Time period: {context.get('time_context', 'Current')}

Provide actionable business insights and recommendations."""
    
    def _build_formatting_prompt(self, analysis: Dict[str, Any], thinking: ThinkingProcess) -> str:
        """Build response formatting prompt"""
        return f"""Format this analysis into a professional Teams response:

ANALYSIS RESULTS:
{json.dumps(analysis, indent=2)}

USER INTENT: {thinking.user_intent}
CONFIDENCE: {thinking.confidence_score}

Create an engaging, professional response suitable for business stakeholders in Microsoft Teams."""
    
    def _create_fallback_thinking(self, user_query: str) -> ThinkingProcess:
        """Create fallback thinking process when AI fails"""
        return ThinkingProcess(
            user_intent=f"Analyze: {user_query}",
            analysis_plan=["Retrieve data", "Analyze results", "Generate insights"],
            context_summary="Limited context available",
            reasoning_steps=["Process user request", "Execute queries", "Format response"],
            dax_queries=[],
            confidence_score=0.3,
            timestamp=datetime.now()
        )
    
    def _create_fallback_response(self, analysis: Dict[str, Any]) -> str:
        """Create fallback response when formatting fails"""
        return f"📊 **Analysis Results**\n\nData retrieved successfully with {len(analysis.get('data', []))} records.\n\n💡 **Note**: Detailed analysis formatting unavailable - please review raw results."