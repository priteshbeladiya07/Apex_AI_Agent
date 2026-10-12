
from typing import Any

from apex_ai.mcp.client_manager import MCPClientManager
from apex_ai.mcp.permissions import (
    require_tool_permission,
    requires_confirmation,
)


class ExpenseService:
    def __init__(self, client_manager: MCPClientManager | None = None):
        self.client_manager = client_manager or MCPClientManager()

    async def list_tools(self) -> list[dict[str, str]]:
        tools = await self.client_manager.get_tools()

        expense_tools = [
            tool for tool in tools
            if tool.name.startswith("expense_")
        ]

        return [
            {
                "name": tool.name,
                "description": tool.description or "",
            }
            for tool in expense_tools
        ]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_permissions: set[str],
        confirmed: bool = False,
    ) -> Any:
        tools = await self.client_manager.get_tools()

        tool = next(
            (
                item for item in tools
                if item.name == tool_name
                and item.name.startswith("expense_")
            ),
            None,
        )

        if tool is None:
            raise ValueError(
                f"Approved expense tool not found: {tool_name}"
            )

        # Reject unknown tools or tools the current user cannot use.
        require_tool_permission(tool_name, user_permissions)

        if requires_confirmation(tool_name) and not confirmed:
            raise PermissionError(
                f"Explicit user confirmation is required for {tool_name}"
            )

        return await tool.ainvoke(arguments)
