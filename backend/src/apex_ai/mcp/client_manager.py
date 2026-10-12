
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

from apex_ai.mcp.servers import SERVERS
from apex_ai.mcp.registry import filter_allowed_tools


class MCPClientManager:
    def __init__(self):
        self.client = MultiServerMCPClient(
            SERVERS,
            tool_name_prefix=True,
            handle_tool_errors=True,
        )
        self._tools: list[BaseTool] | None = None

    async def get_tools(
        self,
        refresh: bool = False,
    ) -> list[BaseTool]:
        if self._tools is None or refresh:
            discovered_tools = await self.client.get_tools()

            print(
             "Discovered MCP tools:",
                  [tool.name for tool in discovered_tools],
              )

            self._tools = filter_allowed_tools(discovered_tools)

            print(
                   "Approved MCP tools:",
            [tool.name for tool in self._tools],
            ) 

            if not self._tools:
                raise RuntimeError(
                    "No approved MCP tools were discovered"
                )

        return list(self._tools)
