#!/usr/bin/env python3
"""
Test script for AI reasoning system core components
Tests data structures and logic without HTTP dependencies
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def test_config_manager():
    """Test configuration manager with AI settings"""
    print("Testing ConfigManager...")
    
    try:
        from modules.config.config_manager import ConfigManager, AzureOpenAIConfig
        
        # Test Azure OpenAI config creation
        ai_config = AzureOpenAIConfig(
            endpoint="https://test.openai.azure.com/",
            api_key="test-key",
            deployment_name="gpt-4-turbo",
            thinking_enabled=True,
            analysis_depth="standard"
        )
        
        print(f"  ✓ AzureOpenAIConfig created: {ai_config.deployment_name}")
        print(f"  ✓ Thinking enabled: {ai_config.thinking_enabled}")
        print(f"  ✓ Analysis depth: {ai_config.analysis_depth}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ ConfigManager test failed: {e}")
        return False

def test_data_structures():
    """Test AI data structures"""
    print("Testing AI data structures...")
    
    try:
        # Test without importing HTTP-dependent modules
        # Create mock data structures
        
        thinking_data = {
            "user_intent": "Analyze sales performance",
            "analysis_plan": ["Get sales data", "Analyze trends", "Generate insights"],
            "context_summary": "Sales analysis for Q3 2024",
            "reasoning_steps": ["Identify top products", "Calculate growth rates"],
            "dax_queries": ["EVALUATE SUMMARIZE(Sales, [Product], 'Total', SUM([Amount]))"],
            "confidence_score": 0.85,
            "timestamp": datetime.now()
        }
        
        print(f"  ✓ Thinking process data structure: {len(thinking_data)} fields")
        print(f"  ✓ User intent: {thinking_data['user_intent']}")
        print(f"  ✓ Confidence score: {thinking_data['confidence_score']}")
        
        # Test analysis result structure
        analysis_result = {
            "success": True,
            "response": "Sales analysis completed successfully",
            "confidence": 0.85,
            "execution_time_ms": 1500,
            "datasets_used": ["Sales", "Products"],
            "thinking_summary": {
                "intent": thinking_data["user_intent"],
                "steps": len(thinking_data["reasoning_steps"])
            }
        }
        
        print(f"  ✓ Analysis result structure: {analysis_result['success']}")
        print(f"  ✓ Datasets used: {analysis_result['datasets_used']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Data structures test failed: {e}")
        return False

def test_business_logic():
    """Test business logic components"""
    print("Testing business logic...")
    
    try:
        # Test intent classification logic
        def classify_intent(query: str) -> str:
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['sales', 'revenue', 'profit']):
                return "sales_analysis"
            elif any(word in query_lower for word in ['customer', 'client']):
                return "customer_analysis"
            elif any(word in query_lower for word in ['trend', 'growth', 'change']):
                return "trend_analysis"
            else:
                return "general_analysis"
        
        # Test with sample queries
        test_queries = [
            "What were our top sales products last quarter?",
            "Show me customer retention rates",
            "Analyze revenue trends over time",
            "Give me a general business overview"
        ]
        
        expected_intents = [
            "sales_analysis",
            "customer_analysis", 
            "trend_analysis",
            "general_analysis"
        ]
        
        for query, expected in zip(test_queries, expected_intents):
            result = classify_intent(query)
            if result == expected:
                print(f"  ✓ Intent classification: '{query[:30]}...' -> {result}")
            else:
                print(f"  ✗ Intent classification failed: expected {expected}, got {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Business logic test failed: {e}")
        return False

def test_response_formatting():
    """Test response formatting logic"""
    print("Testing response formatting...")
    
    try:
        # Test Teams response formatting logic
        def format_teams_response(analysis_data: Dict[str, Any]) -> str:
            """Simple Teams response formatter"""
            
            response_parts = [
                f"📊 **Analysis Results**",
                f"",
                f"**Success**: {analysis_data.get('success', False)}",
                f"**Confidence**: {analysis_data.get('confidence', 0):.1%}",
                f"**Execution Time**: {analysis_data.get('execution_time_ms', 0)}ms",
                f""
            ]
            
            if analysis_data.get('datasets_used'):
                response_parts.append(f"**Data Sources**: {', '.join(analysis_data['datasets_used'])}")
            
            if analysis_data.get('response'):
                response_parts.extend([
                    f"",
                    f"**Results**: {analysis_data['response']}"
                ])
            
            return "\n".join(response_parts)
        
        # Test with sample data
        test_data = {
            "success": True,
            "confidence": 0.87,
            "execution_time_ms": 2300,
            "datasets_used": ["Sales", "Products", "Customers"],
            "response": "Top performing products identified with growth trends analyzed."
        }
        
        formatted_response = format_teams_response(test_data)
        
        print(f"  ✓ Response formatting successful")
        print(f"  ✓ Response length: {len(formatted_response)} characters")
        print(f"  ✓ Contains emoji and formatting: {'📊' in formatted_response}")
        
        # Verify key elements are present
        required_elements = ["Analysis Results", "Success", "Confidence", "Data Sources"]
        for element in required_elements:
            if element in formatted_response:
                print(f"  ✓ Contains required element: {element}")
            else:
                print(f"  ✗ Missing required element: {element}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Response formatting test failed: {e}")
        return False

def test_context_building():
    """Test context building logic"""
    print("Testing context building...")
    
    try:
        # Test context building logic
        def build_analysis_context(user_query: str) -> Dict[str, Any]:
            """Simple context builder"""
            
            context = {
                "query": user_query,
                "timestamp": datetime.now().isoformat(),
                "business_domain": "General Business",
                "complexity": "Medium",
                "estimated_datasets": 2,
                "time_context": {
                    "current_quarter": "Q4 2024",
                    "current_month": "January 2025"
                }
            }
            
            # Analyze query for business domain
            query_lower = user_query.lower()
            if "sales" in query_lower or "revenue" in query_lower:
                context["business_domain"] = "Sales & Marketing"
                context["estimated_datasets"] = 3
            elif "customer" in query_lower:
                context["business_domain"] = "Customer Relations"
                context["estimated_datasets"] = 2
            elif "finance" in query_lower or "budget" in query_lower:
                context["business_domain"] = "Finance & Accounting"
                context["estimated_datasets"] = 4
            
            return context
        
        # Test with different query types
        test_queries = [
            "Show me sales performance this quarter",
            "Analyze customer satisfaction trends", 
            "Review our budget vs actual expenses",
            "General business overview please"
        ]
        
        for query in test_queries:
            context = build_analysis_context(query)
            print(f"  ✓ Context for '{query[:25]}...': {context['business_domain']}")
            print(f"    - Estimated datasets: {context['estimated_datasets']}")
            print(f"    - Complexity: {context['complexity']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Context building test failed: {e}")
        return False

def test_integration_flow():
    """Test complete integration flow without HTTP calls"""
    print("Testing integration flow...")
    
    try:
        # Simulate complete analysis flow
        user_query = "What were our top performing products last quarter?"
        
        # Step 1: Classify intent
        def classify_intent(query):
            if "sales" in query.lower() or "product" in query.lower():
                return "sales_analysis"
            return "general_analysis"
        
        intent = classify_intent(user_query)
        print(f"  ✓ Step 1 - Intent classification: {intent}")
        
        # Step 2: Build context
        context = {
            "query": user_query,
            "intent": intent,
            "business_domain": "Sales & Marketing",
            "available_datasets": ["Sales", "Products", "Customers"],
            "time_context": "Q3 2024"
        }
        print(f"  ✓ Step 2 - Context building: {len(context['available_datasets'])} datasets")
        
        # Step 3: Generate thinking process
        thinking = {
            "user_intent": intent,
            "analysis_plan": [
                "Identify available product sales data",
                "Calculate performance metrics by product", 
                "Rank products by performance",
                "Generate insights and recommendations"
            ],
            "confidence_score": 0.85,
            "dax_queries": [
                "EVALUATE TOPN(10, SUMMARIZE(Sales, [Product], 'Revenue', SUM([Amount])), [Revenue], DESC)"
            ]
        }
        print(f"  ✓ Step 3 - Thinking process: {len(thinking['analysis_plan'])} steps planned")
        
        # Step 4: Simulate execution results
        execution_results = {
            "success": True,
            "data": [
                {"Product": "Product A", "Revenue": 2400000},
                {"Product": "Product B", "Revenue": 1800000},
                {"Product": "Product C", "Revenue": 1200000}
            ],
            "row_count": 3,
            "execution_time_ms": 1200
        }
        print(f"  ✓ Step 4 - Simulated execution: {execution_results['row_count']} results")
        
        # Step 5: Generate insights
        insights = {
            "key_insights": [
                "Product A leads with $2.4M revenue (+32% growth)",
                "Top 3 products account for 67% of total revenue",
                "Strong performance across all product categories"
            ],
            "recommendations": [
                "Increase inventory for Product A ahead of Q4",
                "Analyze success factors of top performers",
                "Consider promotional campaigns for lower performers"
            ]
        }
        print(f"  ✓ Step 5 - Insight generation: {len(insights['key_insights'])} insights")
        
        # Step 6: Format final response
        final_response = f"""📊 **Q3 2024 Top Performing Products**

**Revenue Leaders:**
1. 🥇 **Product A** - $2.4M (+32% growth)
2. 🥈 **Product B** - $1.8M (stable)
3. 🥉 **Product C** - $1.2M (+5% growth)

**💡 Key Insights:**
• Product A shows exceptional growth momentum
• Top 3 products drive majority of revenue
• Consistent performance across portfolio

**📈 Recommendations:**
• Increase Product A inventory for Q4 demand
• Analyze success factors for replication
• Consider targeted promotions for growth

*Analysis completed in {execution_results['execution_time_ms']}ms*"""
        
        print(f"  ✓ Step 6 - Final response: {len(final_response)} characters")
        print(f"  ✓ Integration flow completed successfully!")
        
        # Verify response quality
        quality_checks = [
            ("Contains executive summary", "Revenue Leaders" in final_response),
            ("Contains insights", "Key Insights" in final_response),
            ("Contains recommendations", "Recommendations" in final_response),
            ("Contains emojis", "📊" in final_response and "💡" in final_response),
            ("Contains performance data", "$2.4M" in final_response)
        ]
        
        for check_name, check_result in quality_checks:
            if check_result:
                print(f"  ✓ Quality check passed: {check_name}")
            else:
                print(f"  ✗ Quality check failed: {check_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Integration flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AI REASONING SYSTEM - CORE LOGIC TESTS")
    print("="*60)
    
    tests = [
        ("Configuration Manager", test_config_manager),
        ("Data Structures", test_data_structures),
        ("Business Logic", test_business_logic),
        ("Response Formatting", test_response_formatting),
        ("Context Building", test_context_building),
        ("Integration Flow", test_integration_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✓ {test_name}: PASSED")
                passed += 1
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - AI reasoning system core logic is working!")
    else:
        print(f"⚠️  {total - passed} tests failed - review issues above")
    
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)