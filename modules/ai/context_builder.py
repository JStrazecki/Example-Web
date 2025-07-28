"""
Power BI Context Builder for AI Analysis
Builds comprehensive context for intelligent Power BI analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..powerbi import PowerBIClient
from ..powerbi.models import WorkspaceInfo, DatasetInfo

logger = logging.getLogger(__name__)

@dataclass
class BusinessContext:
    """Business context information"""
    domain: str = "General Business"
    time_period: str = "Current"
    key_metrics: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)

@dataclass
class PowerBIContext:
    """Comprehensive Power BI context for AI analysis"""
    # User context
    query: str
    intent: str
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Power BI context
    available_workspaces: List[WorkspaceInfo] = field(default_factory=list)
    relevant_datasets: List[DatasetInfo] = field(default_factory=list)
    schema_info: Dict[str, Any] = field(default_factory=dict)
    
    # Historical context
    recent_queries: List[str] = field(default_factory=list)
    query_patterns: Dict[str, int] = field(default_factory=dict)
    
    # Business context
    business_context: BusinessContext = field(default_factory=BusinessContext)
    time_context: Dict[str, Any] = field(default_factory=dict)
    
    # Technical context
    performance_hints: List[str] = field(default_factory=list)
    estimated_complexity: str = "Medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for AI processing"""
        return {
            "query": self.query,
            "intent": self.intent,
            "workspaces": [ws.name for ws in self.available_workspaces],
            "datasets": [ds.name for ds in self.relevant_datasets],
            "schema_summary": self.schema_info,
            "time_context": self.time_context,
            "business_domain": self.business_context.domain,
            "complexity": self.estimated_complexity,
            "performance_hints": self.performance_hints
        }

class PowerBIContextBuilder:
    """Builds comprehensive context for AI analysis"""
    
    def __init__(self, powerbi_client: PowerBIClient):
        self.powerbi_client = powerbi_client
        self._query_history = []
        self._user_preferences = {}
        
    async def build_context(self, user_query: str) -> PowerBIContext:
        """Build comprehensive context for AI analysis"""
        logger.info(f"Building context for query: {user_query[:50]}...")
        
        # Initialize context
        context = PowerBIContext(
            query=user_query,
            intent=await self._classify_intent(user_query)
        )
        
        # Build context components in parallel where possible
        await self._build_powerbi_context(context)
        await self._build_business_context(context)
        self._build_time_context(context)
        self._build_historical_context(context)
        self._estimate_complexity(context)
        
        logger.info(f"Context built with {len(context.available_workspaces)} workspaces and {len(context.relevant_datasets)} datasets")
        return context
    
    async def _classify_intent(self, user_query: str) -> str:
        """Classify user intent from query"""
        query_lower = user_query.lower()
        
        # Sales and revenue analysis
        if any(word in query_lower for word in ['sales', 'revenue', 'profit', 'income']):
            return "sales_analysis"
        
        # Performance and metrics
        elif any(word in query_lower for word in ['performance', 'kpi', 'metric', 'target']):
            return "performance_analysis"
        
        # Trend and time-based analysis
        elif any(word in query_lower for word in ['trend', 'growth', 'change', 'over time', 'quarterly', 'monthly']):
            return "trend_analysis"
        
        # Comparison analysis
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference', 'better', 'worse']):
            return "comparison_analysis"
        
        # Top/bottom analysis
        elif any(word in query_lower for word in ['top', 'bottom', 'best', 'worst', 'highest', 'lowest']):
            return "ranking_analysis"
        
        # Customer analysis
        elif any(word in query_lower for word in ['customer', 'client', 'account', 'segment']):
            return "customer_analysis"
        
        # Product analysis
        elif any(word in query_lower for word in ['product', 'item', 'category', 'inventory']):
            return "product_analysis"
        
        # Regional/geographic analysis
        elif any(word in query_lower for word in ['region', 'country', 'state', 'city', 'location', 'geographic']):
            return "geographic_analysis"
        
        # Financial analysis
        elif any(word in query_lower for word in ['budget', 'cost', 'expense', 'margin', 'roi', 'financial']):
            return "financial_analysis"
        
        else:
            return "general_analysis"
    
    async def _build_powerbi_context(self, context: PowerBIContext):
        """Build Power BI specific context"""
        try:
            # Get available workspaces
            context.available_workspaces = await self.powerbi_client.get_workspaces()
            
            # Find relevant datasets based on intent
            await self._find_relevant_datasets(context)
            
            # Build schema context for relevant datasets
            await self._build_schema_context(context)
            
        except Exception as e:
            logger.error(f"Error building Power BI context: {e}")
            context.performance_hints.append("Limited Power BI context due to connection issues")
    
    async def _find_relevant_datasets(self, context: PowerBIContext):
        """Find datasets relevant to the user query"""
        relevant_datasets = []
        
        # Keywords for different types of analysis
        intent_keywords = {
            "sales_analysis": ["sales", "revenue", "order", "transaction"],
            "customer_analysis": ["customer", "client", "account", "crm"],
            "product_analysis": ["product", "inventory", "item", "catalog"],
            "financial_analysis": ["finance", "budget", "accounting", "expense"],
            "performance_analysis": ["performance", "kpi", "metric", "dashboard"]
        }
        
        search_keywords = intent_keywords.get(context.intent, [])
        query_words = context.query.lower().split()
        search_terms = search_keywords + query_words
        
        # Search through workspaces for relevant datasets
        for workspace in context.available_workspaces:
            try:
                datasets = await self.powerbi_client.get_datasets(workspace.id)
                
                for dataset in datasets:
                    # Score dataset relevance
                    relevance_score = self._calculate_dataset_relevance(
                        dataset, search_terms, context.intent
                    )
                    
                    if relevance_score > 0.3:  # Threshold for relevance
                        dataset.relevance_score = relevance_score
                        relevant_datasets.append(dataset)
                        
            except Exception as e:
                logger.warning(f"Error accessing datasets in workspace {workspace.name}: {e}")
        
        # Sort by relevance and limit to top 5
        context.relevant_datasets = sorted(
            relevant_datasets, 
            key=lambda ds: getattr(ds, 'relevance_score', 0), 
            reverse=True
        )[:5]
    
    def _calculate_dataset_relevance(self, 
                                   dataset: DatasetInfo, 
                                   search_terms: List[str], 
                                   intent: str) -> float:
        """Calculate how relevant a dataset is to the query"""
        score = 0.0
        dataset_name_lower = dataset.name.lower()
        
        # Exact keyword matches in dataset name
        for term in search_terms:
            if term in dataset_name_lower:
                score += 0.3
        
        # Intent-based scoring
        intent_weights = {
            "sales_analysis": {"sales": 0.5, "revenue": 0.5, "order": 0.4},
            "customer_analysis": {"customer": 0.5, "client": 0.4, "crm": 0.6},
            "financial_analysis": {"finance": 0.5, "budget": 0.4, "accounting": 0.5}
        }
        
        if intent in intent_weights:
            for keyword, weight in intent_weights[intent].items():
                if keyword in dataset_name_lower:
                    score += weight
        
        # Workspace context bonus
        workspace_name_lower = dataset.workspace_name.lower()
        if any(term in workspace_name_lower for term in search_terms):
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _build_schema_context(self, context: PowerBIContext):
        """Build schema information for relevant datasets"""
        schema_info = {
            "tables": [],
            "measures": [],
            "date_columns": [],
            "relationships": [],
            "estimated_size": "Unknown"
        }
        
        # For now, we'll build basic schema context
        # In a full implementation, you'd call Power BI REST API to get detailed schema
        for dataset in context.relevant_datasets:
            schema_info["tables"].append({
                "dataset": dataset.name,
                "workspace": dataset.workspace_name,
                "estimated_tables": self._estimate_table_count(dataset)
            })
        
        context.schema_info = schema_info
    
    def _estimate_table_count(self, dataset: DatasetInfo) -> int:
        """Estimate number of tables in dataset based on name patterns"""
        # Simple heuristic based on dataset naming patterns
        name_lower = dataset.name.lower()
        
        if "warehouse" in name_lower or "dwh" in name_lower:
            return 15  # Data warehouse typically has many tables
        elif "cube" in name_lower or "olap" in name_lower:
            return 8   # OLAP cubes typically have fewer but richer tables
        elif "report" in name_lower:
            return 5   # Report datasets typically have fewer tables
        else:
            return 10  # Default estimate
    
    async def _build_business_context(self, context: PowerBIContext):
        """Build business context based on intent and available data"""
        business_context = BusinessContext()
        
        # Map intent to business domain
        intent_domains = {
            "sales_analysis": "Sales & Marketing",
            "customer_analysis": "Customer Relations", 
            "financial_analysis": "Finance & Accounting",
            "product_analysis": "Product Management",
            "performance_analysis": "Business Intelligence"
        }
        
        business_context.domain = intent_domains.get(context.intent, "General Business")
        
        # Add relevant business rules based on intent
        business_rules = {
            "sales_analysis": [
                "Focus on revenue trends and growth",
                "Consider seasonality in retail data",
                "Analyze by product, region, and time period"
            ],
            "customer_analysis": [
                "Prioritize customer lifetime value",
                "Consider customer segmentation",
                "Analyze retention and churn patterns"
            ],
            "financial_analysis": [
                "Ensure data accuracy for financial reporting",
                "Consider fiscal year vs calendar year",
                "Include budget vs actual comparisons"
            ]
        }
        
        business_context.business_rules = business_rules.get(context.intent, [])
        context.business_context = business_context
    
    def _build_time_context(self, context: PowerBIContext):
        """Build time-related context"""
        now = datetime.now()
        
        time_context = {
            "current_date": now.isoformat(),
            "current_quarter": f"Q{((now.month - 1) // 3) + 1} {now.year}",
            "current_month": now.strftime("%B %Y"),
            "current_year": str(now.year),
            "last_quarter": self._get_last_quarter(now),
            "last_month": (now.replace(day=1) - timedelta(days=1)).strftime("%B %Y"),
            "ytd_start": f"{now.year}-01-01",
            "suggested_periods": self._get_suggested_time_periods(context.intent)
        }
        
        context.time_context = time_context
    
    def _get_last_quarter(self, date: datetime) -> str:
        """Get last quarter string"""
        current_quarter = ((date.month - 1) // 3) + 1
        if current_quarter == 1:
            return f"Q4 {date.year - 1}"
        else:
            return f"Q{current_quarter - 1} {date.year}"
    
    def _get_suggested_time_periods(self, intent: str) -> List[str]:
        """Get suggested time periods based on analysis intent"""
        period_suggestions = {
            "trend_analysis": ["Last 12 months", "Quarter over quarter", "Year over year"],
            "sales_analysis": ["Monthly trends", "Quarterly performance", "YTD vs last year"],
            "performance_analysis": ["Current vs target", "Monthly variance", "Quarterly trends"],
            "comparison_analysis": ["Period over period", "Same period last year", "Benchmark comparison"]
        }
        
        return period_suggestions.get(intent, ["Current period", "Historical trend", "Comparative analysis"])
    
    def _build_historical_context(self, context: PowerBIContext):
        """Build historical query context"""
        # Add current query to history
        self._query_history.append({
            "query": context.query,
            "intent": context.intent,
            "timestamp": datetime.now()
        })
        
        # Keep only last 10 queries
        if len(self._query_history) > 10:
            self._query_history = self._query_history[-10:]
        
        # Extract recent query patterns
        context.recent_queries = [q["query"] for q in self._query_history[-5:]]
        
        # Build query pattern analysis
        intent_counts = {}
        for query in self._query_history:
            intent = query["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        context.query_patterns = intent_counts
    
    def _estimate_complexity(self, context: PowerBIContext):
        """Estimate query complexity and add performance hints"""
        complexity_score = 0
        
        # Dataset count factor
        complexity_score += len(context.relevant_datasets) * 0.2
        
        # Schema complexity factor  
        estimated_tables = sum(
            table.get("estimated_tables", 0) 
            for table in context.schema_info.get("tables", [])
        )
        complexity_score += min(estimated_tables * 0.1, 2.0)
        
        # Intent complexity factor
        intent_complexity = {
            "general_analysis": 0.3,
            "sales_analysis": 0.5,
            "trend_analysis": 0.7,
            "comparison_analysis": 0.8,
            "performance_analysis": 0.6
        }
        complexity_score += intent_complexity.get(context.intent, 0.5)
        
        # Determine complexity level
        if complexity_score < 1.0:
            context.estimated_complexity = "Low"
            context.performance_hints = ["Simple query expected", "Fast execution likely"]
        elif complexity_score < 2.0:
            context.estimated_complexity = "Medium"
            context.performance_hints = ["Moderate complexity", "Consider data volume"]
        else:
            context.estimated_complexity = "High"
            context.performance_hints = [
                "Complex analysis detected", 
                "May require multiple queries",
                "Consider breaking into smaller parts"
            ]
    
    def get_context_summary(self, context: PowerBIContext) -> str:
        """Get a human-readable context summary"""
        summary_parts = [
            f"Intent: {context.intent}",
            f"Workspaces: {len(context.available_workspaces)}",
            f"Relevant datasets: {len(context.relevant_datasets)}",
            f"Complexity: {context.estimated_complexity}",
            f"Domain: {context.business_context.domain}"
        ]
        
        return " | ".join(summary_parts)
    
    def clear_history(self):
        """Clear query history"""
        self._query_history.clear()
        logger.info("Query history cleared")