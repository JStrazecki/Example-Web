#!/usr/bin/env python3
"""
Teams Bot integration for SQL Assistant MCP Server
Handles Teams Bot Framework messaging and connects to MCP tools
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from botbuilder.core import (
    ActivityHandler, 
    TurnContext, 
    MessageFactory, 
    CardFactory
)
from botbuilder.schema import (
    Activity, 
    ActivityTypes, 
    ChannelAccount,
    CardAction,
    ActionTypes,
    SuggestedActions
)

# Configure logging
logger = logging.getLogger(__name__)

class SQLAssistantBot(ActivityHandler):
    """Teams bot for SQL Assistant MCP integration"""
    
    def __init__(self):
        super().__init__()
        self.conversation_history = {}
        
        # Check if MCP tools are available
        self.mcp_available = self._check_mcp_availability()
        
        # Welcome message and help text
        self.welcome_message = """
🤖 **Power BI Teams Bot**

I can help you with:
• 📊 **Power BI Queries** - Execute DAX queries and explore datasets
• 🏢 **Workspace Management** - List workspaces and datasets
• 📈 **Data Exploration** - Discover tables, measures, and relationships

**Examples:**
- "List all Power BI workspaces"
- "Show datasets in Finance workspace"
- "Execute DAX query: EVALUATE VALUES(Sales[Product])"
- "Find all measures in the Sales table"

Type **help** for more commands or just ask me a question!
        """
    
    def _check_mcp_availability(self) -> Dict[str, bool]:
        """Check which MCP capabilities are available"""
        return {
            "powerbi": all([
                os.environ.get("POWERBI_TENANT_ID"),
                os.environ.get("POWERBI_CLIENT_ID"), 
                os.environ.get("POWERBI_CLIENT_SECRET")
            ])
        }
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_message = turn_context.activity.text.strip()
        user_id = turn_context.activity.from_property.id
        
        # Initialize conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        logger.info(f"Received message from {user_id}: {user_message}")
        
        # Handle special commands
        if user_message.lower() in ["help", "/help", "?"]:
            await self._send_help_message(turn_context)
            return
        
        if user_message.lower() in ["status", "/status"]:
            await self._send_status_message(turn_context)
            return
            
        if user_message.lower().startswith("list workspaces"):
            await self._handle_list_workspaces(turn_context)
            return
        
        if user_message.lower().startswith("list datasets"):
            await self._handle_list_datasets(turn_context, user_message)
            return
        
        if user_message.lower().startswith("dax:") or user_message.lower().startswith("execute dax"):
            await self._handle_dax_query(turn_context, user_message)
            return
        
        # Handle general Power BI questions
        await self._handle_powerbi_question(turn_context, user_message)
    
    async def on_members_added_activity(
        self, 
        members_added: List[ChannelAccount], 
        turn_context: TurnContext
    ):
        """Handle new members joining the conversation"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(self.welcome_message)
                )
                await self._send_suggested_actions(turn_context)
    
    async def _send_help_message(self, turn_context: TurnContext):
        """Send detailed help message"""
        help_text = f"""
🔧 **Power BI Bot Commands**

**Power BI Commands:** {'✅ Available' if self.mcp_available['powerbi'] else '❌ Not configured'}
- "list workspaces" - Show all Power BI workspaces
- "list datasets in [workspace_name]" - Show datasets
- "dax: EVALUATE VALUES(Table[Column])" - Execute DAX query

**Data Exploration:**
- "Show me the Sales workspace"
- "What tables are in [dataset_name]?"
- "Execute: EVALUATE TOPN(10, Sales)"

**System Commands:**
- "status" - Check system status
- "help" - Show this help message

**Current Capabilities:**
- Power BI Integration: {'✅' if self.mcp_available['powerbi'] else '❌'}
- DAX Query Execution: {'✅' if self.mcp_available['powerbi'] else '❌'}
- Workspace Management: {'✅' if self.mcp_available['powerbi'] else '❌'}

Just ask me about your Power BI data!
        """
        
        await turn_context.send_activity(MessageFactory.text(help_text))
        await self._send_suggested_actions(turn_context)
    
    async def _send_status_message(self, turn_context: TurnContext):
        """Send system status information"""
        status_info = {
            "timestamp": datetime.now().isoformat(),
            "capabilities": self.mcp_available,
            "environment_check": {
                "powerbi_tenant": bool(os.environ.get("POWERBI_TENANT_ID")),
                "powerbi_client": bool(os.environ.get("POWERBI_CLIENT_ID")),
                "powerbi_secret": bool(os.environ.get("POWERBI_CLIENT_SECRET"))
            }
        }
        
        status_text = f"""
📊 **System Status**

**Core Services:**
- Power BI Integration: {'🟢 Online' if status_info['capabilities']['powerbi'] else '🔴 Offline'}

**Environment Variables:**
- Power BI Tenant: {'✅' if status_info['environment_check']['powerbi_tenant'] else '❌'}
- Power BI Client: {'✅' if status_info['environment_check']['powerbi_client'] else '❌'}
- Power BI Secret: {'✅' if status_info['environment_check']['powerbi_secret'] else '❌'}

**Last Updated:** {status_info['timestamp'][:19]}
        """
        
        await turn_context.send_activity(MessageFactory.text(status_text))
    
    async def _send_suggested_actions(self, turn_context: TurnContext):
        """Send suggested action buttons"""
        suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="📊 List Workspaces", 
                    type=ActionTypes.im_back,
                    value="list workspaces"
                ),
                CardAction(
                    title="📈 DAX Query",
                    type=ActionTypes.im_back,
                    value="dax: EVALUATE VALUES(Sales[Product])"
                ),
                CardAction(
                    title="❓ Help",
                    type=ActionTypes.im_back,
                    value="help"
                ),
                CardAction(
                    title="📈 Status",
                    type=ActionTypes.im_back,
                    value="status"
                )
            ]
        )
        
        message = MessageFactory.text("What would you like to do?")
        message.suggested_actions = suggested_actions
        await turn_context.send_activity(message)
    
    async def _handle_powerbi_question(self, turn_context: TurnContext, user_message: str):
        """Handle general Power BI questions"""
        if not self.mcp_available["powerbi"]:
            await turn_context.send_activity(
                MessageFactory.text("❌ Power BI integration not available. Missing Power BI configuration.")
            )
            return
        
        try:
            # Send typing indicator
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )
            
            # Here you would call your MCP tools
            # For now, we'll simulate the response
            response_text = f"""
🔍 **Analyzing your Power BI question:** "{user_message}"

⚠️ **Note:** This is a demonstration response. In a full implementation, this would:
1. Call the appropriate MCP Power BI tools
2. Process your question about Power BI data
3. Execute DAX queries or retrieve workspace information
4. Provide formatted results

**Available Commands:**
- `list workspaces` - See all your Power BI workspaces
- `list datasets in [workspace]` - View datasets in a workspace
- `dax: [your query]` - Execute DAX queries

**Try asking:**
- "list workspaces"
- "dax: EVALUATE VALUES(Sales[Product])"

To complete the integration, connect this bot to your MCP server running on port 3000.
            """
            
            await turn_context.send_activity(MessageFactory.text(response_text))
            
        except Exception as e:
            logger.error(f"Error handling Power BI question: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"❌ Error processing request: {str(e)}")
            )
    
    async def _handle_list_workspaces(self, turn_context: TurnContext):
        """Handle Power BI workspace listing"""
        if not self.mcp_available["powerbi"]:
            await turn_context.send_activity(
                MessageFactory.text("❌ Power BI integration not available. Missing Power BI configuration.")
            )
            return
        
        try:
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )
            
            # Simulate Power BI workspace response
            response_text = """
📊 **Power BI Workspaces**

⚠️ **Demo Response** - In full implementation, this would call `list_powerbi_workspaces` MCP tool.

**Available Workspaces:**
1. 🏢 **Finance Workspace** (Premium)
2. 📈 **Sales Analytics** (Pro)  
3. 🔍 **Operations Dashboard** (Premium)
4. 👥 **HR Metrics** (Pro)

**Usage:**
- Type: `list datasets in Finance Workspace` to see datasets
- Type: `dax: EVALUATE VALUES(Sales[Product])` to run DAX queries

*To enable live data, ensure Power BI credentials are configured in environment variables.*
            """
            
            await turn_context.send_activity(MessageFactory.text(response_text))
            
        except Exception as e:
            logger.error(f"Error listing workspaces: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"❌ Error listing workspaces: {str(e)}")
            )
    
    async def _handle_list_datasets(self, turn_context: TurnContext, user_message: str):
        """Handle dataset listing for a workspace"""
        # Extract workspace name from message
        parts = user_message.lower().split("in ", 1)
        if len(parts) < 2:
            await turn_context.send_activity(
                MessageFactory.text("❌ Please specify workspace name: `list datasets in [workspace_name]`")
            )
            return
        
        workspace_name = parts[1].strip()
        
        response_text = f"""
📊 **Datasets in "{workspace_name}"**

⚠️ **Demo Response** - In full implementation, this would call `list_powerbi_datasets` MCP tool.

**Available Datasets:**
1. 📈 **Sales Data** (Last refreshed: 2 hours ago)
2. 💰 **Financial Reports** (Last refreshed: 1 day ago)
3. 👥 **Customer Analytics** (Last refreshed: 6 hours ago)

**Next Steps:**
- Run DAX queries: `dax: EVALUATE TOPN(10, Sales, Sales[Revenue], DESC)`
- Ask questions: "Show me top customers by revenue"

*Actual datasets would be retrieved from Power BI Service API.*
        """
        
        await turn_context.send_activity(MessageFactory.text(response_text))
    
    async def _handle_dax_query(self, turn_context: TurnContext, user_message: str):
        """Handle DAX query execution"""
        if not self.mcp_available["powerbi"]:
            await turn_context.send_activity(
                MessageFactory.text("❌ Power BI integration not available.")
            )
            return
        
        # Extract DAX query
        if user_message.lower().startswith("dax:"):
            dax_query = user_message[4:].strip()
        elif user_message.lower().startswith("execute dax"):
            dax_query = user_message.split(":", 1)[1].strip() if ":" in user_message else ""
        else:
            dax_query = user_message
        
        if not dax_query:
            await turn_context.send_activity(
                MessageFactory.text("❌ Please provide a DAX query after the colon")
            )
            return
        
        try:
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )
            
            response_text = f"""
🔍 **Executing DAX Query**

**Query:** `{dax_query}`

⚠️ **Demo Response** - In full implementation, this would:
1. Call `execute_dax_query` MCP tool
2. Connect to specified workspace and dataset
3. Execute the DAX query
4. Return formatted results

**Sample Result:**
| Product | Revenue |
|---------|---------|
| Product A | $15,000 |
| Product B | $12,500 |
| Product C | $10,200 |

**Status:** Query executed successfully (3 rows returned)

*To enable live queries, ensure workspace and dataset names are specified.*
            """
            
            await turn_context.send_activity(MessageFactory.text(response_text))
            
        except Exception as e:
            logger.error(f"Error executing DAX query: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"❌ Error executing DAX query: {str(e)}")
            )