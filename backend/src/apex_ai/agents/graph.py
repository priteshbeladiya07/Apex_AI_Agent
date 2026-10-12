from langgraph.graph import StateGraph, START, END

from apex_ai.agents.state import AgentState
from apex_ai.agents.nodes import call_model, run_tools
from apex_ai.agents.routing import route_after_model


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("call_model", call_model)
    builder.add_node("run_tools", run_tools)

    builder.add_edge(START, "call_model")

    builder.add_conditional_edges(
        "call_model",
        route_after_model,
        {
            "tools": "run_tools",
            "end": END,
        },
    )

    builder.add_edge("run_tools", "call_model")

    return builder.compile()


graph = build_graph()