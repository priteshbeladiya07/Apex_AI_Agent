from typing import Literal

from apex_ai.agents.state import AgentState


def route_after_model(state: AgentState) -> Literal["tools", "end"]:
    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    tool_calls = getattr(last_message, "tool_calls", [])

    if tool_calls:
        return "tools"

    return "end"