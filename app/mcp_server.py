# app/mcp_server.py
"""
MCP Server — Model Context Protocol endpoint for AI agents.
This exposes read/write tools to authorized agents.
"""
from fastapi import APIRouter
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
import asyncio, json

# NOTE: python-mcp package needed:
# pip install mcp
# See https://modelcontextprotocol.io for MCP spec.

MCP_SERVER_NAME = "525600-calendar-mcp"

router = APIRouter()


def create_mcp_router() -> APIRouter:
    """
    Returns a FastAPI router that wraps the MCP stdio server.
    Agents connect via stdio transport (local process) or HTTP.
    """
    router = APIRouter()

    @router.post("/mcp/tools/call")
    async def call_mcp_tool(payload: dict):
        """
        Generic MCP tool call endpoint.
        Agents send: {"tool": "list_calendars", "arguments": {...}}
        """
        tool_name = payload.get("tool")
        arguments = payload.get("arguments", {})

        # Dispatch to handler
        if tool_name == "list_calendars":
            return {"result": await list_calendars_handler(arguments)}
        elif tool_name == "get_events":
            return {"result": await get_events_handler(arguments)}
        elif tool_name == "create_event":
            return {"result": await create_event_handler(arguments)}
        elif tool_name == "get_upcoming_events":
            return {"result": await get_upcoming_handler(arguments)}
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    return router


# ─── MCP Tool Handlers ──────────────────────────────────────────────────────

async def list_calendars_handler(args: dict):
    """List calendars for authenticated user. Agent passes JWT in Authorization header."""
    # Implementation hooks into get_db / auth
    # Return: [{id, name, description, color, calendar_type}]
    return [{"id": 1, "name": "Personal", "description": "Default calendar", "color": "#3B82F6"}]


async def get_events_handler(args: dict):
    """
    Get events from a calendar.
    Args: calendar_id, start_date?, end_date?
    Returns: [{id, title, start_time, end_time, location, cost, joy_score}]
    """
    # TODO: integrate with get_db + JWT auth
    return []


async def create_event_handler(args: dict):
    """
    Create a calendar event.
    Args: calendar_id, title, start_time, end_time, location?, cost?, joy_score?
    Returns: {id, title, ...}
    """
    # TODO: integrate with get_db + JWT auth
    return {"id": None, "status": "not_implemented"}


async def get_upcoming_handler(args: dict):
    """
    Get upcoming events for scanning agents to evaluate re-optimization.
    Args: calendar_id, days_ahead (default 90)
    Returns: [{event_with_cost_joy_metadata}]
    """
    # TODO: integrate with get_db + JWT auth
    return []


# ─── MCP Tool Definitions (for agent discovery) ────────────────────────────

MCP_TOOLS = [
    Tool(
        name="list_calendars",
        description="List all calendars belonging to the authenticated user.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_events",
        description="Get events from a calendar within a date range.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "integer"},
                "start_date": {"type": "string", "description": "ISO date"},
                "end_date": {"type": "string", "description": "ISO date"},
            },
            "required": ["calendar_id"],
        },
    ),
    Tool(
        name="create_event",
        description="Create a new event on a calendar.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "integer"},
                "title": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"},
                "location": {"type": "string"},
                "cost": {"type": "number"},
                "joy_score": {"type": "number"},
            },
            "required": ["calendar_id", "title", "start_time", "end_time"],
        },
    ),
    Tool(
        name="get_upcoming_events",
        description="Get upcoming events for re-optimization scanning. Returns cost and joy_score for each event.",
        inputSchema={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "integer"},
                "days_ahead": {"type": "integer", "default": 90},
            },
            "required": ["calendar_id"],
        },
    ),
]


# ─── Standalone MCP Stdio Server (optional alternative) ───────────────────

async def run_mcp_stdio():
    """
    Run MCP server over stdio (for AI agents that connect via stdio transport).
    Entry point: python -m app.mcp_server
    """
    server = Server(MCP_SERVER_NAME)

    @server.list_tools()
    async def list_tools():
        return MCP_TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        handlers = {
            "list_calendars": list_calendars_handler,
            "get_events": get_events_handler,
            "create_event": create_event_handler,
            "get_upcoming_events": get_upcoming_handler,
        }
        handler = handlers.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
        result = await handler(arguments)
        return [TextContent(type="text", text=json.dumps(result))]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def mount_mcp(app):
    """Attach MCP router to FastAPI app."""
    mcp_router = create_mcp_router()
    app.include_router(mcp_router)