"""
Power BI AI Reasoning Engine
Core intelligence system with multi-step thinking process
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

from .azure_openai_client import AzureOpenAIClient, ThinkingProcess
from .context_builder import PowerBIContextBuilder, PowerBIContext
from ..powerbi import PowerBIClient
from ..powerbi.models import QueryResult

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Complete analysis result with thinking process and formatted response"""
    # Internal thinking (not shown to user)
    thinking: ThinkingProcess
    
    # Clean response for Teams/UI
    response: str
    
    # Query results and data
    query_results: List[QueryResult] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Analysis metadata
    confidence: float = 0.0
    execution_time_ms: int = 0
    datasets_used: List[str] = field(default_factory=list)
    
    # Error handling
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "response": self.response,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
            "datasets_used": self.datasets_used,
            "row_count": len(self.data),
            "warnings": self.warnings,
            "error": self.error_message,
            "thinking_summary": {
                "intent": self.thinking.user_intent,
                "confidence": self.thinking.confidence_score,
                "steps_completed": len(self.thinking.reasoning_steps)
            }
        }

class PowerBIReasoningEngine:
    """
    AI-powered analysis engine with internal thinking process
    """
    
    def __init__(self, 
                 openai_client: AzureOpenAIClient,
                 context_builder: PowerBIContextBuilder,
                 powerbi_client: PowerBIClient):
        self.openai_client = openai_client
        self.context_builder = context_builder
        self.powerbi_client = powerbi_client
        
        # Analysis statistics
        self._analysis_count = 0
        self._success_count = 0
        self._total_execution_time = 0
    
    async def analyze_request(self, 
                            user_query: str, 
                            analysis_depth: str = "standard") -> AnalysisResult:
        """
        Main analysis method with complete thinking process
        """
        start_time = datetime.now()
        self._analysis_count += 1
        
        logger.info(f"Starting AI analysis for query: {user_query[:50]}...")
        
        try:
            # STEP 1: Build comprehensive context
            logger.debug("Building analysis context...")
            context = await self.context_builder.build_context(user_query)
            
            # STEP 2: Internal reasoning (Hidden from user)
            logger.debug("Performing internal reasoning...")
            thinking_process = await self._internal_reasoning(user_query, context)
            
            # STEP 3: Execute planned analysis
            logger.debug("Executing analysis plan...")
            results = await self._execute_analysis_plan(thinking_process, context)
            
            # STEP 4: Generate insights from results
            logger.debug("Generating insights...")
            insights = await self._generate_insights(results, context, thinking_process)
            
            # STEP 5: Format clean response for Teams
            logger.debug("Formatting response...")
            clean_response = await self._format_teams_response(insights, thinking_process)
            
            # Calculate execution time
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._total_execution_time += execution_time
            self._success_count += 1
            
            # Build final result
            result = AnalysisResult(
                thinking=thinking_process,
                response=clean_response,
                query_results=results.get("query_results", []),
                data=results.get("data", []),
                confidence=thinking_process.confidence_score,
                execution_time_ms=execution_time,
                datasets_used=[ds.name for ds in context.relevant_datasets],
                success=True
            )
            
            logger.info(f"Analysis completed successfully in {execution_time}ms")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            
            # Create error result
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AnalysisResult(
                thinking=ThinkingProcess(
                    user_intent=user_query,
                    analysis_plan=["Error occurred during analysis"],
                    context_summary="Analysis failed",
                    reasoning_steps=[f"Error: {str(e)}"],
                    dax_queries=[],
                    confidence_score=0.0,
                    timestamp=datetime.now()
                ),
                response=self._create_error_response(str(e)),
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time
            )
    
    async def _internal_reasoning(self, 
                                user_query: str, 
                                context: PowerBIContext) -> ThinkingProcess:
        """
        Internal AI reasoning process (hidden from user)
        """
        logger.debug("Starting internal reasoning process...")
        
        try:
            # Use Azure OpenAI for structured thinking
            thinking = await self.openai_client.reasoning_analysis(
                user_query, 
                context.to_dict()
            )
            
            # Enhance thinking with context-specific improvements
            await self._enhance_thinking_with_context(thinking, context)
            
            logger.debug(f"Reasoning complete - Intent: {thinking.user_intent}, Confidence: {thinking.confidence_score}")
            return thinking
            
        except Exception as e:
            logger.error(f"Internal reasoning failed: {e}")
            # Return fallback thinking
            return ThinkingProcess(
                user_intent=f"Analyze: {user_query}",
                analysis_plan=["Retrieve available data", "Process results", "Generate response"],
                context_summary=f"Available datasets: {len(context.relevant_datasets)}",
                reasoning_steps=["Basic analysis due to reasoning error"],
                dax_queries=[],
                confidence_score=0.4,
                timestamp=datetime.now()
            )
    
    async def _enhance_thinking_with_context(self, 
                                           thinking: ThinkingProcess, 
                                           context: PowerBIContext):
        """Enhance AI thinking with Power BI specific context"""
        
        # Add context-aware DAX queries if none were generated
        if not thinking.dax_queries and context.relevant_datasets:
            thinking.dax_queries = await self._generate_fallback_queries(thinking, context)
        
        # Adjust confidence based on available context
        context_quality_score = self._assess_context_quality(context)
        thinking.confidence_score = min(
            thinking.confidence_score * context_quality_score, 
            1.0
        )
        
        # Add performance considerations to reasoning
        if context.estimated_complexity == "High":
            thinking.reasoning_steps.append(
                "Consider query optimization due to high complexity"
            )
    
    async def _generate_fallback_queries(self, 
                                       thinking: ThinkingProcess, 
                                       context: PowerBIContext) -> List[str]:
        """Generate basic DAX queries when AI doesn't provide them"""
        
        fallback_queries = []
        
        if context.relevant_datasets:
            dataset = context.relevant_datasets[0]  # Use most relevant dataset
            
            # Basic exploratory queries based on intent
            if context.intent == "sales_analysis":
                fallback_queries.append(
                    f"EVALUATE TOPN(10, SUMMARIZE({dataset.name}, [Product], \"Total Sales\", SUM([Sales Amount])), [Total Sales], DESC)"
                )
            elif context.intent == "trend_analysis":
                fallback_queries.append(
                    f"EVALUATE SUMMARIZE({dataset.name}, [Date], \"Value\", SUM([Amount]))"
                )
            else:
                # Generic summary query
                fallback_queries.append(
                    f"EVALUATE SUMMARIZE({dataset.name}, \"Row Count\", COUNTROWS({dataset.name}))"
                )
        
        return fallback_queries
    
    def _assess_context_quality(self, context: PowerBIContext) -> float:
        """Assess the quality of available context"""
        quality_score = 0.5  # Base score
        
        # Dataset availability bonus
        if context.relevant_datasets:
            quality_score += 0.2
            
        # Multiple datasets bonus
        if len(context.relevant_datasets) > 1:
            quality_score += 0.1
            
        # Schema information bonus
        if context.schema_info.get("tables"):
            quality_score += 0.1
            
        # Business context bonus
        if context.business_context.business_rules:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    async def _execute_analysis_plan(self, 
                                   thinking: ThinkingProcess, 
                                   context: PowerBIContext) -> Dict[str, Any]:
        """
        Execute the planned analysis steps
        """
        logger.debug("executing analysis plan...")
        
        results = {
            "query_results": [],
            "data": [],
            "execution_summary": []
        }
        
        # Execute DAX queries from thinking process
        for i, dax_query in enumerate(thinking.dax_queries):
            if context.relevant_datasets:
                dataset = context.relevant_datasets[0]  # Use primary dataset
                
                logger.debug(f"Executing query {i+1}/{len(thinking.dax_queries)}...")
                
                query_result = await self.powerbi_client.execute_dax_query(
                    dataset_id=dataset.id,
                    dax_query=dax_query,
                    context=context
                )
                
                results["query_results"].append(query_result)
                
                if query_result.success and query_result.data:
                    results["data"].extend(query_result.data)
                    results["execution_summary"].append(
                        f"Query {i+1}: {query_result.row_count} rows retrieved"
                    )
                else:
                    results["execution_summary"].append(
                        f"Query {i+1}: Failed - {query_result.error or 'Unknown error'}"
                    )
        
        # If no queries were executed, try basic data retrieval
        if not results["query_results"] and context.relevant_datasets:
            await self._execute_fallback_analysis(results, context)
        
        logger.debug(f"Analysis execution complete: {len(results['data'])} total rows")
        return results
    
    async def _execute_fallback_analysis(self, 
                                       results: Dict[str, Any], 
                                       context: PowerBIContext):
        """Execute basic analysis when specific queries fail"""
        
        if context.relevant_datasets:
            dataset = context.relevant_datasets[0]
            
            # Try a simple row count query
            basic_query = f"EVALUATE ROW(\"Dataset\", \"{dataset.name}\", \"Workspace\", \"{dataset.workspace_name}\")"
            
            query_result = await self.powerbi_client.execute_dax_query(
                dataset_id=dataset.id,
                dax_query=basic_query
            )
            
            results["query_results"].append(query_result)
            
            if query_result.success:
                results["data"] = query_result.data or []
                results["execution_summary"].append("Fallback analysis: Basic dataset info retrieved")
            else:
                results["execution_summary"].append("Fallback analysis also failed")
    
    async def _generate_insights(self, 
                               results: Dict[str, Any], 
                               context: PowerBIContext,
                               thinking: ThinkingProcess) -> Dict[str, Any]:
        """
        Generate business insights from query results
        """
        logger.debug("Generating business insights...")
        
        if not results["data"]:
            return {
                "insights": ["No data available for analysis"],
                "recommendations": ["Check data availability and query validity"],
                "summary": "Analysis could not be completed due to lack of data"
            }
        
        try:
            # Use AI to analyze results and generate insights
            analysis_context = {
                "user_intent": thinking.user_intent,
                "business_domain": context.business_context.domain,
                "time_context": context.time_context.get("current_quarter", "Current period")
            }
            
            insights = await self.openai_client.analyze_results(
                results["data"], 
                analysis_context
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            
            # Fallback insights
            return {
                "insights": [
                    f"Retrieved {len(results['data'])} records from Power BI",
                    f"Data sourced from {len(context.relevant_datasets)} dataset(s)"
                ],
                "recommendations": [
                    "Review the data for patterns and trends",
                    "Consider additional filters or time periods"
                ],
                "summary": f"Basic analysis completed with {len(results['data'])} data points"
            }
    
    async def _format_teams_response(self, 
                                   insights: Dict[str, Any], 
                                   thinking: ThinkingProcess) -> str:
        """
        Generate clean, professional response for Teams
        """
        logger.debug("Formatting Teams response...")
        
        try:
            # Use AI to format professional response
            response = await self.openai_client.format_business_response(
                insights, 
                thinking
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            
            # Fallback formatting
            return self._create_fallback_response(insights, thinking)
    
    def _create_fallback_response(self, 
                                insights: Dict[str, Any], 
                                thinking: ThinkingProcess) -> str:
        """Create fallback response when AI formatting fails"""
        
        response_parts = [
            f"📊 **Analysis Results**",
            f"",
            f"**Intent**: {thinking.user_intent}",
            f"**Confidence**: {thinking.confidence_score:.1%}",
            f""
        ]
        
        # Add insights
        if insights.get("insights"):
            response_parts.append("**💡 Key Insights:**")
            for insight in insights["insights"][:3]:  # Limit to top 3
                response_parts.append(f"• {insight}")
            response_parts.append("")
        
        # Add recommendations
        if insights.get("recommendations"):
            response_parts.append("**📈 Recommendations:**")
            for rec in insights["recommendations"][:2]:  # Limit to top 2
                response_parts.append(f"• {rec}")
            response_parts.append("")
        
        # Add summary
        if insights.get("summary"):
            response_parts.append(f"**Summary**: {insights['summary']}")
        
        return "\n".join(response_parts)
    
    def _create_error_response(self, error_message: str) -> str:
        """Create user-friendly error response"""
        return f"""⚠️ **Analysis Error**

I encountered an issue while analyzing your Power BI data:

**Error**: {error_message}

**💡 Suggestions**:
• Check your Power BI data connections
• Verify dataset permissions
• Try rephrasing your question
• Contact your administrator if the issue persists

I'm ready to help once the issue is resolved!"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""
        avg_execution_time = (
            self._total_execution_time / self._analysis_count 
            if self._analysis_count > 0 else 0
        )
        
        success_rate = (
            self._success_count / self._analysis_count 
            if self._analysis_count > 0 else 0
        )
        
        return {
            "total_analyses": self._analysis_count,
            "successful_analyses": self._success_count,
            "success_rate": success_rate,
            "average_execution_time_ms": int(avg_execution_time),
            "total_execution_time_ms": self._total_execution_time
        }
    
    def reset_statistics(self):
        """Reset analysis statistics"""
        self._analysis_count = 0
        self._success_count = 0
        self._total_execution_time = 0
        logger.info("Reasoning engine statistics reset")