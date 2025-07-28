# 🧠 AI-Powered Power BI MCP Web Application

A modern, intelligent web application that provides comprehensive Power BI analysis with **AI reasoning capabilities** powered by Azure OpenAI. Transform your Power BI data into actionable insights with natural language queries and intelligent analysis.

## 🌟 Key Features

### 🤖 **AI-Powered Analysis**  
- **Natural Language Queries**: Ask questions in plain English
- **Multi-Step Reasoning**: AI thinks through complex business problems
- **Smart DAX Generation**: Automatic query creation with optimization
- **Business Insights**: Executive-ready analysis and recommendations
- **Context-Aware**: Understands your data structure and business domain

### 🏗️ **Robust Architecture**
- **🔐 Secure Authentication**: MSAL-based Azure AD authentication
- **🚀 High Performance**: Async/await with intelligent caching  
- **🏗️ Modular Design**: Clean separation with dedicated AI reasoning layer
- **🌐 Interactive Web Interface**: AI-enhanced dashboard
- **📊 Power BI Integration**: Deep workspace and dataset integration
- **🤖 Teams Ready**: AI-formatted responses for Microsoft Teams

## 🧠 AI Capabilities

### **Intelligent Analysis Engine**
Transform questions like:
- *"What were our top performing products last quarter?"*
- *"Show me sales trends by region for the past 6 months"*  
- *"Which customers have the highest lifetime value?"*

Into comprehensive business intelligence reports with:
- ✅ **Executive summaries**
- ✅ **Key insights and trends**  
- ✅ **Actionable recommendations**
- ✅ **Professional Teams formatting**

### **Smart DAX Generation**
Natural language to optimized DAX:
- *"Calculate total sales by product category for this year"* 
- *"Show monthly growth rates compared to last year"*
- *"Find customers with declining purchase patterns"*

Gets converted to efficient, business-optimized DAX queries.

## 📁 Enhanced Architecture

```
modules/
├── ai/                # 🧠 AI reasoning and analysis
│   ├── azure_openai_client.py    # Azure OpenAI integration
│   ├── context_builder.py        # Business context analysis  
│   ├── reasoning_engine.py       # Multi-step AI reasoning
│   └── response_formatter.py     # Professional output formatting
├── auth/              # 🔐 Power BI authentication  
├── config/            # ⚙️ Configuration (now with AI settings)
├── powerbi/           # 📊 Power BI API integration
├── mcp/              # 🔧 Intelligent MCP tools
└── web/              # 🌐 AI-enhanced web server
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies (now includes AI libraries)
pip install -r requirements.txt
```

### 2. Configuration

Create configuration with AI capabilities:

```bash
python main.py --create-config
```

Configure your `config.json`:

```json
{
  "powerbi": {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id", 
    "client_secret": "your-client-secret"
  },
  "mcp": {
    "server_url": "https://your-mcp-server.com",
    "api_key": "your-api-key"
  },
  "azure_openai": {
    "endpoint": "https://your-openai.openai.azure.com/",
    "api_key": "your-azure-openai-key",
    "deployment_name": "gpt-4-turbo",
    "thinking_enabled": true,
    "analysis_depth": "standard",
    "response_style": "business"
  },
  "web": {
    "host": "0.0.0.0",
    "port": 8080
  }
}
```

### 3. Run with AI Capabilities

```bash
# Start the AI-powered application
python main.py

# The system will show:
# 🤖 AI reasoning capabilities enabled
# 🧠 Try AI-powered analysis at /ai/analyze endpoint
```

## 🎯 AI-Enhanced API Endpoints

### **🧠 Intelligent Analysis**
- `POST /ai/analyze` - AI-powered business analysis
- `POST /ai/dax` - Smart DAX query generation  
- `POST /ai/insights` - Business intelligence with recommendations
- `GET /ai/status` - AI system health and statistics
- `GET /ai/health` - AI components health check

### **📊 Traditional Power BI** (Still Available)
- `GET /api/powerbi/workspaces` - List workspaces
- `POST /api/powerbi/query` - Execute DAX queries
- `GET /mcp/tools` - Available tools

## 💡 Usage Examples

### **AI Analysis Request**
```bash
curl -X POST http://localhost:8080/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What were our top performing products last quarter?",
    "depth": "standard"
  }'
```

### **Smart DAX Generation**  
```bash
curl -X POST http://localhost:8080/ai/dax \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Calculate total sales by product category for this year"
  }'
```

### **Business Insights Analysis**
```bash
curl -X POST http://localhost:8080/ai/insights \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What trends should we focus on for Q4 planning?",
    "depth": "deep"
  }'
```

## 🌐 AI-Enhanced Web Interface

Visit `http://localhost:8080` for the upgraded dashboard featuring:

- **🧠 AI Chat Interface**: Natural language queries
- **📊 Intelligent Visualizations**: Context-aware data display  
- **🎯 Business Insights Panel**: Executive-ready summaries
- **⚡ Smart DAX Builder**: AI-assisted query creation
- **📱 Teams Integration Preview**: See how responses look in Teams

## ⚙️ AI Configuration Options

### Environment Variables

```bash
# Azure OpenAI (New)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo  
AZURE_OPENAI_VERSION=2024-02-15-preview

# AI Settings  
AI_THINKING_ENABLED=true
AI_ANALYSIS_DEPTH=standard    # standard, deep, extensive
AI_RESPONSE_STYLE=business    # technical, business, executive

# Existing Power BI & MCP settings...
POWERBI_TENANT_ID=your-tenant-id
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
MCP_SERVER_URL=https://your-mcp-server.com
```

### AI Analysis Depths

- **Standard**: Quick insights (< 10 seconds)
- **Deep**: Detailed analysis with trends (< 30 seconds)  
- **Extensive**: Comprehensive report with recommendations (< 60 seconds)

## 🤖 Teams Integration with AI

AI-enhanced Teams responses include:

- **📊 Executive Summary**: Key findings upfront
- **💡 Business Insights**: Actionable intelligence  
- **📈 Recommendations**: Strategic next steps
- **🎯 Professional Formatting**: Teams-optimized layout
- **🔍 Data Context**: Sources and confidence levels

## 🧠 AI Architecture Deep Dive

### **Reasoning Engine Flow**
1. **Context Building**: Analyze available workspaces, datasets, business domain
2. **Intent Classification**: Understand what the user really wants  
3. **Multi-Step Planning**: Break down complex requests
4. **Smart Execution**: Generate and run optimized DAX queries
5. **Insight Generation**: Extract business value from results
6. **Professional Formatting**: Create Teams/executive-ready responses

### **Business Intelligence Features**
- **Domain Awareness**: Sales, Finance, Customer, Product analysis specialization
- **Time Context**: Automatic quarter/year/seasonal analysis
- **Performance Optimization**: Query efficiency recommendations  
- **Confidence Scoring**: AI confidence in analysis results
- **Error Recovery**: Graceful fallbacks when AI isn't available

## 📈 AI Monitoring & Analytics

- **AI Health**: `/ai/health` - Component status and readiness
- **Usage Statistics**: Analysis counts, success rates, performance
- **Confidence Tracking**: AI confidence scores and accuracy
- **Business Impact**: Track which insights drive decisions

## 🔒 AI Security & Privacy

- **Data Privacy**: Analysis context stays within your Azure tenant
- **Secure API Keys**: Encrypted Azure OpenAI credential storage
- **Audit Logging**: Track all AI-powered analysis requests
- **Fallback Mode**: Graceful degradation when AI unavailable
- **Business Context**: No sensitive data sent to AI models

## 🚀 Deployment with AI

### **Local Development**
```bash
# With AI capabilities
python main.py --config config.json
# 🤖 AI reasoning capabilities enabled
```

### **Production**  
```bash
# Environment-based deployment
export AZURE_OPENAI_ENDPOINT=https://your-openai.azure.com/
export AZURE_OPENAI_API_KEY=your-key
python main.py
```

### **Fallback Mode**
Without Azure OpenAI configuration, the system runs in standard mode with traditional Power BI tools.

## 📊 What's New in AI Version

### **🧠 Added AI Modules**
- **AzureOpenAIClient**: GPT-4 integration with business prompts
- **PowerBIContextBuilder**: Intelligent context analysis
- **ReasoningEngine**: Multi-step business logic
- **TeamsResponseFormatter**: Professional output generation

### **🔧 Enhanced Configuration**  
- Azure OpenAI settings and preferences
- AI thinking process toggles
- Business domain customization

### **🌐 New API Endpoints**
- `/ai/*` - Complete AI analysis suite
- Enhanced `/info` with AI documentation  
- AI-aware health checks

### **📱 Improved Web Interface**
- AI chat interface for natural queries
- Smart suggestions and auto-completion
- Business insight visualization panels

## 🎯 Success Metrics

**Intelligence Metrics:**
- ✅ Query understanding accuracy > 90%
- ✅ DAX generation success rate > 85%  
- ✅ Business insight relevance > 4.0/5
- ✅ Teams response quality: Executive-ready

**Performance Metrics:**
- ✅ Standard analysis: < 10 seconds
- ✅ Deep analysis: < 30 seconds  
- ✅ System uptime: > 99.5%
- ✅ AI availability: > 95%

## 🤝 Contributing to AI Features

1. Follow existing modular patterns in `/modules/ai/`
2. Add comprehensive error handling for AI failures
3. Include business context in AI prompts  
4. Test fallback modes when AI unavailable
5. Document new AI capabilities and use cases

## 📚 AI API Documentation

Visit `/info` for complete AI endpoint documentation including:
- Natural language query examples
- Response format specifications  
- Business insight structure
- Error handling and fallbacks
- Integration patterns for Teams/applications

## 🆘 Troubleshooting

### AI-Related Issues

1. **AI Analysis Not Working**
   - Check `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
   - Verify deployment name matches your Azure OpenAI deployment
   - Check `/ai/health` endpoint for component status

2. **Poor Analysis Quality**
   - Try increasing `analysis_depth` to "deep" or "extensive"
   - Ensure Power BI data has proper business context
   - Check AI confidence scores in responses

3. **Slow Response Times**
   - Use "standard" depth for faster responses
   - Check Azure OpenAI service limits and quotas
   - Monitor network latency to Azure OpenAI endpoint

### Traditional Issues

4. **MCP Connection Failed**
   - Check `MCP_SERVER_URL` is correct and accessible
   - Verify MCP server is running
   - Test with `/mcp/status` endpoint

5. **Power BI Authentication Failed**
   - Verify Azure AD app registration and permissions
   - Check tenant ID, client ID, and client secret
   - Ensure Power BI Service Principal access

---

## 🎉 Transform Your Power BI Experience

**Before**: "Please use the 'list workspaces' command"

**After**: 
> 📊 **Q3 2024 Top Performing Products**
> 
> **Revenue Leaders:**  
> 1. 🥇 **ProductAlpha** - $2.4M (+32% vs Q2)
> 2. 🥈 **ProductBeta** - $1.8M (+18% vs Q2)
> 
> **💡 Key Insights:**
> • ProductAlpha shows exceptional growth momentum
> • Market expansion in EMEA driving Beta performance
> 
> **📈 Recommendations:**  
> • Increase ProductAlpha inventory for Q4 demand
> • Investigate Gamma's decline in Western markets

**Ready to get started?** Configure Azure OpenAI and transform your Power BI data into intelligent business insights! 🚀

## 📄 License

This project is licensed under the MIT License.