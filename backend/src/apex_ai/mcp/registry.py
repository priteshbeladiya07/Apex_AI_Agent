
import os
from langchain_core.tools import BaseTool


def filter_allowed_tools(
    tools: list[BaseTool],
) -> list[BaseTool]:
    configured = os.getenv("MCP_ALLOWED_TOOLS", "")

    # Accept exact tool names and unambiguous unprefixed names.
    allowed_names = {
        name.strip()
        for name in configured.split(",")
        if name.strip()
    }

    registered = []
    seen_names = set()
    tool_names = {tool.name for tool in tools}
    unprefixed_allowed_names = set()

    for name in allowed_names - tool_names:
        matches = [
            tool
            for tool in tools
            if tool.name.endswith(f"_{name}")
        ]
        if len(matches) == 1:
            unprefixed_allowed_names.add(matches[0].name)

    for tool in tools:
        if tool.name in seen_names:
            raise ValueError(
                f"Duplicate MCP tool name: {tool.name}"
            )

        seen_names.add(tool.name)

        if (
            tool.name in allowed_names
            or tool.name in unprefixed_allowed_names
        ):
            registered.append(tool)

    return registered
