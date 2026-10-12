from collections.abc import Sequence
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_mistralai import ChatMistralAI
from langgraph.prebuilt import ToolNode

from apex_ai.agents.state import AgentState
from apex_ai.agents.prompts import SYSTEM_PROMPT
from apex_ai.core.config import settings


_tools: list[BaseTool] = []
_tool_node: ToolNode | None = None
_model: ChatMistralAI | None = None


def configure_tools(tools: Sequence[BaseTool]) -> None:
    global _tools, _tool_node

    tool_list = list(tools)
    tool_names = [tool.name for tool in tool_list]

    if len(tool_names) != len(set(tool_names)):
        raise ValueError(
            "Duplicate tool names detected. "
            "Use unique names for tools from different MCP servers."
        )

    _tools = tool_list
    _tool_node = ToolNode(_tools) if _tools else None


def get_model() -> ChatMistralAI:
    global _model

    if _model is None:
        if settings.mistral_api_key is None:
            raise RuntimeError("MISTRAL_API_KEY is not configured")

        _model = ChatMistralAI(
            model=settings.mistral_model,
            api_key=settings.mistral_api_key,
            temperature=0,
        )

    return _model


async def call_model(state: AgentState) -> dict[str, Any]:
    messages = state.get("messages", [])

    if not messages:
        raise ValueError("No messages found in agent state")

    model = get_model()

    if _tools:
        model = model.bind_tools(_tools)

    response = await model.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *messages,
        ]
    )

    return {"messages": [response]}


async def run_tools(
    state: AgentState,
    config: RunnableConfig,
) -> dict[str, Any]:
    if _tool_node is None:
        raise RuntimeError(
            "No MCP tools configured. Load tools before invoking the graph."
        )

    return await _tool_node.ainvoke(state, config)