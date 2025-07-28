"""
Teams Response Formatter for Power BI Analysis
Creates beautiful, professional responses for Microsoft Teams
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .reasoning_engine import AnalysisResult
from .azure_openai_client import ThinkingProcess

logger = logging.getLogger(__name__)

@dataclass
class BusinessInsight:
    """Represents a business insight with metadata"""
    title: str
    description: str
    impact: str  # "High", "Medium", "Low"
    confidence: float
    recommendation: Optional[str] = None
    metric_value: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable"

@dataclass
class FormattingOptions:
    """Options for response formatting"""
    use_emojis: bool = True
    include_executive_summary: bool = True
    include_recommendations: bool = True
    include_data_summary: bool = True
    max_insights: int = 5
    business_tone: bool = True
    include_confidence: bool = False

class TeamsResponseFormatter:
    """
    Format AI analysis results for Teams display
    """
    
    def __init__(self, formatting_options: Optional[FormattingOptions] = None):
        self.options = formatting_options or FormattingOptions()
        
        # Emoji mappings for different contexts
        self.emoji_map = {
            "success": "✅",
            "analysis": "📊",
            "insight": "💡",
            "recommendation": "📈",
            "warning": "⚠️",
            "error": "❌",
            "trend_up": "📈",
            "trend_down": "📉", 
            "trend_stable": "➡️",
            "money": "💰",
            "customer": "👥",
            "product": "📦",
            "time": "⏰",
            "target": "🎯",
            "performance": "📊"
        }
    
    def format_analysis_result(self, analysis_result: AnalysisResult) -> str:
        """
        Main method to format complete analysis result
        """
        logger.debug("Formatting analysis result for Teams...")
        
        if not analysis_result.success:
            return self._format_error_response(analysis_result)
        
        try:
            # Build formatted response sections
            sections = []
            
            # Header section
            if self.options.use_emojis:
                sections.append(self._create_header_section(analysis_result))
            
            # Executive summary
            if self.options.include_executive_summary:
                summary_section = self._create_executive_summary(analysis_result)
                if summary_section:
                    sections.append(summary_section)
            
            # Key insights section
            insights_section = self._create_insights_section(analysis_result)
            if insights_section:
                sections.append(insights_section)
            
            # Recommendations section
            if self.options.include_recommendations:
                recommendations_section = self._create_recommendations_section(analysis_result)
                if recommendations_section:
                    sections.append(recommendations_section)
            
            # Data summary section
            if self.options.include_data_summary:
                data_section = self._create_data_summary_section(analysis_result)
                if data_section:
                    sections.append(data_section)
            
            # Footer with metadata
            footer_section = self._create_footer_section(analysis_result)
            if footer_section:
                sections.append(footer_section)
            
            # Join all sections
            response = "\n\n".join(sections)
            
            logger.debug("Response formatting completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}", exc_info=True)
            return self._create_fallback_response(analysis_result)
    
    def _create_header_section(self, analysis_result: AnalysisResult) -> str:
        """Create formatted header section"""
        emoji = self.emoji_map.get("analysis", "📊")
        intent_title = self._format_intent_title(analysis_result.thinking.user_intent)
        
        header_parts = [
            f"{emoji} **{intent_title}**"
        ]
        
        # Add confidence indicator if enabled
        if self.options.include_confidence and analysis_result.confidence > 0:
            confidence_emoji = self._get_confidence_emoji(analysis_result.confidence)
            header_parts.append(f"*{confidence_emoji} Confidence: {analysis_result.confidence:.0%}*")
        
        return "\n".join(header_parts)
    
    def _create_executive_summary(self, analysis_result: AnalysisResult) -> Optional[str]:
        """Create executive summary section"""
        if not analysis_result.data:
            return None
        
        summary_parts = [
            f"**{self.emoji_map.get('insight', '💡')} Executive Summary**"
        ]
        
        # Data volume summary
        data_count = len(analysis_result.data)
        datasets_used = len(analysis_result.datasets_used)
        
        summary_parts.append(
            f"Analyzed **{data_count:,} records** from **{datasets_used} dataset(s)** "
            f"in {analysis_result.execution_time_ms:,}ms."
        )
        
        # Add key finding if available
        if hasattr(analysis_result, 'key_finding'):
            summary_parts.append(f"**Key Finding**: {analysis_result.key_finding}")
        
        return "\n".join(summary_parts)
    
    def _create_insights_section(self, analysis_result: AnalysisResult) -> Optional[str]:
        """Create insights section from analysis"""
        # This would typically extract insights from the analysis_result.response
        # For now, we'll return the main response content
        
        if not analysis_result.response or analysis_result.response.strip() == "":
            return None
        
        # If the response is already well-formatted, return it
        if "**" in analysis_result.response or "*" in analysis_result.response:
            return analysis_result.response
        
        # Otherwise, format it as insights
        insights_parts = [
            f"**{self.emoji_map.get('insight', '💡')} Key Insights**",
            "",
            analysis_result.response
        ]
        
        return "\n".join(insights_parts)
    
    def _create_recommendations_section(self, analysis_result: AnalysisResult) -> Optional[str]:
        """Create recommendations section"""
        # Extract recommendations from thinking process or response
        recommendations = self._extract_recommendations(analysis_result)
        
        if not recommendations:
            return None
        
        rec_parts = [
            f"**{self.emoji_map.get('recommendation', '📈')} Recommendations**"
        ]
        
        for i, rec in enumerate(recommendations[:3], 1):  # Limit to top 3
            rec_parts.append(f"{i}. {rec}")
        
        return "\n".join(rec_parts)
    
    def _create_data_summary_section(self, analysis_result: AnalysisResult) -> Optional[str]:
        """Create data summary section"""
        if not analysis_result.datasets_used:
            return None
        
        summary_parts = [
            f"**📋 Data Summary**"
        ]
        
        # Dataset information
        if analysis_result.datasets_used:
            datasets_text = ", ".join(analysis_result.datasets_used)
            summary_parts.append(f"**Sources**: {datasets_text}")
        
        # Data volume
        if analysis_result.data:
            summary_parts.append(f"**Records**: {len(analysis_result.data):,}")
        
        # Execution performance
        if analysis_result.execution_time_ms > 0:
            summary_parts.append(f"**Response Time**: {analysis_result.execution_time_ms:,}ms")
        
        return "\n".join(summary_parts)
    
    def _create_footer_section(self, analysis_result: AnalysisResult) -> Optional[str]:
        """Create footer with metadata"""
        footer_parts = []
        
        # Warnings
        if analysis_result.warnings:
            warning_emoji = self.emoji_map.get("warning", "⚠️")
            footer_parts.append(f"{warning_emoji} *{'; '.join(analysis_result.warnings)}*")
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        footer_parts.append(f"*Analysis completed at {timestamp}*")
        
        return "\n".join(footer_parts) if footer_parts else None
    
    def _format_error_response(self, analysis_result: AnalysisResult) -> str:
        """Format error response for Teams"""
        error_emoji = self.emoji_map.get("error", "❌")
        
        error_parts = [
            f"{error_emoji} **Analysis Error**",
            "",
            f"I encountered an issue while analyzing your Power BI data.",
            ""
        ]
        
        if analysis_result.error_message:
            error_parts.extend([
                f"**Error Details**: {analysis_result.error_message}",
                ""
            ])
        
        # Add helpful suggestions
        suggestions_emoji = self.emoji_map.get("insight", "💡")
        error_parts.extend([
            f"{suggestions_emoji} **Suggestions**:",
            "• Check your Power BI data connections",
            "• Verify dataset permissions", 
            "• Try rephrasing your question",
            "• Contact your administrator if the issue persists",
            "",
            "I'm ready to help once the issue is resolved!"
        ])
        
        return "\n".join(error_parts)
    
    def _create_fallback_response(self, analysis_result: AnalysisResult) -> str:
        """Create simple fallback response"""
        fallback_parts = [
            f"{self.emoji_map.get('analysis', '📊')} **Power BI Analysis**",
            "",
            "Analysis completed successfully.",
            ""
        ]
        
        if analysis_result.data:
            fallback_parts.append(f"Retrieved {len(analysis_result.data):,} records from your Power BI data.")
        
        if analysis_result.datasets_used:
            datasets = ", ".join(analysis_result.datasets_used)
            fallback_parts.append(f"Data sources: {datasets}")
        
        return "\n".join(fallback_parts)
    
    def format_quick_response(self, 
                            message: str, 
                            response_type: str = "info") -> str:
        """Format quick response with appropriate emoji and styling"""
        
        emoji_mapping = {
            "info": self.emoji_map.get("analysis", "ℹ️"),
            "success": self.emoji_map.get("success", "✅"),
            "warning": self.emoji_map.get("warning", "⚠️"),
            "error": self.emoji_map.get("error", "❌"),
            "thinking": "🧠"
        }
        
        emoji = emoji_mapping.get(response_type, "ℹ️")
        return f"{emoji} {message}"
    
    def format_data_table(self, 
                         data: List[Dict[str, Any]], 
                         max_rows: int = 10) -> str:
        """Format data as a simple table for Teams"""
        if not data:
            return "No data available."
        
        # Limit data
        display_data = data[:max_rows]
        
        # Get column headers
        headers = list(display_data[0].keys()) if display_data else []
        
        if not headers:
            return "No data structure available."
        
        # Limit columns for readability
        if len(headers) > 4:
            headers = headers[:4]
        
        # Create simple table
        table_parts = [
            "```",
            " | ".join(headers),
            " | ".join(["---"] * len(headers))
        ]
        
        for row in display_data:
            row_values = []
            for header in headers:
                value = str(row.get(header, ""))
                # Truncate long values
                if len(value) > 15:
                    value = value[:12] + "..."
                row_values.append(value)
            
            table_parts.append(" | ".join(row_values))
        
        table_parts.append("```")
        
        if len(data) > max_rows:
            table_parts.append(f"*Showing {max_rows} of {len(data)} total records*")
        
        return "\n".join(table_parts)
    
    def _format_intent_title(self, user_intent: str) -> str:
        """Format user intent into a proper title"""
        # Convert snake_case to Title Case
        title = user_intent.replace("_", " ").title()
        
        # Special formatting for common intents
        title_mapping = {
            "Sales Analysis": "Sales Performance Analysis",
            "Customer Analysis": "Customer Insights Analysis", 
            "Product Analysis": "Product Performance Analysis",
            "Financial Analysis": "Financial Performance Analysis",
            "Trend Analysis": "Trend & Growth Analysis",
            "General Analysis": "Business Intelligence Analysis"
        }
        
        return title_mapping.get(title, title)
    
    def _get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        if confidence >= 0.8:
            return "🟢"  # High confidence
        elif confidence >= 0.6:
            return "🟡"  # Medium confidence
        else:
            return "🟠"  # Low confidence
    
    def _extract_recommendations(self, analysis_result: AnalysisResult) -> List[str]:
        """Extract recommendations from analysis result"""
        recommendations = []
        
        # Look for recommendations in the response
        response = analysis_result.response.lower()
        
        if "recommend" in response:
            # Extract sentences containing recommendations
            sentences = analysis_result.response.split(".")
            for sentence in sentences:
                if "recommend" in sentence.lower() or "suggest" in sentence.lower():
                    clean_sentence = sentence.strip()
                    if clean_sentence and len(clean_sentence) > 10:
                        recommendations.append(clean_sentence)
        
        # Add default recommendations based on intent
        if not recommendations:
            intent = analysis_result.thinking.user_intent.lower()
            
            if "sales" in intent:
                recommendations = [
                    "Focus on top-performing products and regions",
                    "Investigate declining trends for improvement opportunities"
                ]
            elif "customer" in intent:
                recommendations = [
                    "Enhance engagement with high-value customer segments",
                    "Develop retention strategies for at-risk customers"
                ]
            else:
                recommendations = [
                    "Continue monitoring key performance indicators",
                    "Schedule regular analysis updates"
                ]
        
        return recommendations[:3]  # Limit to top 3