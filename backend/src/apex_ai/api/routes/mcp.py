from fastapi import APIRouter, HTTPException, Request

from apex_ai.mcp.servers import SERVERS

router = APIRouter()


@router.get("/servers")
async def list_mcp_servers(request: Request) -> list[dict[str, object]]:
    manager = getattr(request.app.state, "mcp_manager", None)
    if manager is None:
        raise HTTPException(
            status_code=503,
            detail="MCP servers have not been initialized",
        )

    try:
        tools = await manager.get_tools()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load approved MCP tools",
        ) from exc

    tools_by_server: dict[str, list[str]] = {
        server_id: [] for server_id in SERVERS
    }
    for tool in tools:
        server_id, separator, tool_name = tool.name.partition("_")
        if separator and server_id in tools_by_server:
            tools_by_server[server_id].append(tool_name)

    return [
        {
            "id": server_id,
            "name": (
                "Expense Tracker"
                if server_id == "expense"
                else server_id.replace("_", " ").title()
            ),
            "description": (
                f"{len(server_tools)} enabled tool"
                f"{'' if len(server_tools) == 1 else 's'}"
                if server_tools
                else "No approved tools"
            ),
            "enabled": bool(server_tools),
        }
        for server_id, server_tools in tools_by_server.items()
    ]
