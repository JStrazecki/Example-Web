# Power BI MCP Teams Bot

A Microsoft Teams bot that provides Power BI data access and DAX query execution using the Model Context Protocol (MCP).

## Features

- 🤖 **Teams Bot Integration**: Natural language chat interface in Microsoft Teams
- 📊 **Power BI Integration**: Query Power BI datasets with DAX queries
- 🏢 **Workspace Management**: Browse workspaces, datasets, and data models
- 🔧 **MCP Protocol**: Extensible tool system for Claude integration
- ⚡ **Real-time Processing**: Async processing for fast responses

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Teams Client  │────│   Teams Bot     │────│   MCP Server    │
│                 │    │   Framework     │    │   (FastMCP)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Bot Handler    │    │   MCP Tools     │
                       │  (teams_bot.py) │    │   - SQL Tools   │
                       │                 │    │   - PowerBI     │
                       └─────────────────┘    │   - Teams Utils │
                                              └─────────────────┘
```

## Setup

### 1. Environment Variables

Create a `.env` file with the following variables:

#### Required (Power BI integration)
```bash
# Power BI Authentication
POWERBI_TENANT_ID=your-tenant-id
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
```

#### Optional (Teams Bot)
```bash
# Teams Bot Framework
MICROSOFT_APP_ID=your-teams-app-id
MICROSOFT_APP_PASSWORD=your-teams-app-password
```

#### Optional (Configuration)
```bash
# Server ports
MCP_PORT=3000
BOT_PORT=3978

# Logging
LOG_LEVEL=INFO
```

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Check configuration
python app_config.py
```

### 3. Running the Application

#### Option 1: All Services (Recommended)
```bash
python startup.py
```

#### Option 2: Individual Services
```bash
# MCP Server only
python main.py

# Teams Bot only  
python teams_app.py
```

## Usage

### Teams Bot Commands

Once deployed to Teams, you can interact with the bot using:

#### Power BI Commands
```
"list workspaces"
"list datasets in Finance Workspace"
"dax: EVALUATE VALUES(Sales[Product])"
```

#### System Commands
```
"help" - Show available commands
"status" - Check system status
```

### MCP Integration

The MCP server exposes tools that can be used by Claude or other MCP clients:

- `list_powerbi_workspaces()`
- `list_powerbi_datasets(workspace_name)`
- `execute_dax_query(workspace_name, dataset_name, dax_query)`
- `format_teams_message(content, message_type)`

## Teams App Configuration

### 1. Create Teams App

1. Go to [Microsoft Teams Developer Portal](https://dev.teams.microsoft.com/)
2. Create a new app
3. Configure bot settings:
   - Bot endpoint: `https://your-domain.com/api/messages`
   - App ID: Use `MICROSOFT_APP_ID` from environment

### 2. Bot Framework Registration

1. Go to [Azure Bot Service](https://portal.azure.com)
2. Create a new Bot Channels Registration
3. Configure Microsoft Teams channel
4. Note the App ID and generate App Password

### 3. Deployment

#### Azure App Service
```bash
# Deploy to Azure
az webapp up --name your-app-name --resource-group your-rg
```

#### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3978

CMD ["python", "startup.py"]
```

## Configuration Check

Run the configuration checker to verify setup:

```bash
python app_config.py
```

Expected output:
```
============================================================
POWER BI MCP TEAMS BOT - CONFIGURATION STATUS
============================================================
🔧 Configuration Status:
  Power BI: ✅
  Teams Bot: ✅

🚀 Available Features:
  Power BI Integration: ✅
  Teams Bot: ✅

🌐 Server Ports:
  MCP Server: 3000
  Teams Bot: 3978

✅ All configuration complete!
============================================================
```

## Troubleshooting

### Common Issues

1. **Teams Bot not responding**
   - Check bot endpoint URL in Teams Developer Portal
   - Verify `MICROSOFT_APP_ID` and `MICROSOFT_APP_PASSWORD`
   - Check firewall/network access to bot endpoint

2. **Power BI integration failing**
   - Confirm Power BI service principal has proper permissions
   - Verify tenant ID and client credentials
   - Check Power BI workspace access

### Logs

Application logs are written to console. For production, configure log aggregation:

```bash
# View logs during development
python startup.py

# Production logging (example)
export LOG_LEVEL=INFO
python startup.py >> app.log 2>&1
```

### Health Checks

```bash
# Teams Bot health
curl http://localhost:3978/health

# MCP Server status  
# Connect MCP client to localhost:3000
```

## Development

### Project Structure

```
.
├── main.py              # MCP server entry point
├── teams_bot.py         # Teams bot handler
├── teams_app.py         # Teams web server
├── startup.py           # Unified startup script
├── app_config.py        # Configuration management
├── requirements.txt     # Dependencies
├── powerbi_client.py    # Power BI client (from existing)
├── sql_translator.py    # SQL translator (from existing)
└── README.md           # This file
```

### Adding MCP Tools

Add new tools to `main.py`:

```python
@mcp.tool()
def my_new_tool(param: str) -> str:
    """Description of the tool"""
    # Implementation
    return json.dumps(result)

# Register in main()
register_my_tools()
```

### Extending Teams Bot

Add new commands to `teams_bot.py`:

```python
async def _handle_my_command(self, turn_context: TurnContext, message: str):
    """Handle custom command"""
    # Implementation
    await turn_context.send_activity(MessageFactory.text(response))
```

## License

This project provides Power BI integration with MCP and Teams. Ensure compliance with:
- Microsoft Teams Terms of Service
- Power BI Licensing Requirements
- Azure Service Terms

## Support

For issues and questions:
1. Check configuration with `python app_config.py`
2. Review logs for error details
3. Verify all environment variables are set correctly
4. Test individual components (MCP server, Teams bot) separately