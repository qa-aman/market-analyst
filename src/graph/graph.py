from langgraph.graph import StateGraph, START, END

from src.graph.state import MarketAnalystState
from src.graph.nodes import (
    orchestrator_node,
    fundamental_agent_node,
    technical_agent_node,
    sentiment_agent_node,
    compile_node,
    fan_out_agents,
)
from src.config import MAX_CONCURRENCY


def build_graph() -> StateGraph:
    graph = StateGraph(MarketAnalystState)

    graph.add_node("orchestrator_node", orchestrator_node)
    graph.add_node("fundamental_agent", fundamental_agent_node)
    graph.add_node("technical_agent", technical_agent_node)
    graph.add_node("sentiment_agent", sentiment_agent_node)
    graph.add_node("compile_node", compile_node)

    graph.add_edge(START, "orchestrator_node")
    graph.add_conditional_edges(
        "orchestrator_node",
        fan_out_agents,
        ["fundamental_agent", "technical_agent", "sentiment_agent"],
    )
    graph.add_edge("fundamental_agent", "compile_node")
    graph.add_edge("technical_agent", "compile_node")
    graph.add_edge("sentiment_agent", "compile_node")
    graph.add_edge("compile_node", END)

    return graph.compile()


app = build_graph()
