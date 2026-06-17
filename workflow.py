from langgraph.graph import (
    StateGraph,
    END
)

from state import AgentState

from agents import (
    problem_framer,
    architect,
    reviewer,
    consensus
)

builder = StateGraph(
    AgentState
)

builder.add_node(
    "problem_framer",
    problem_framer
)

builder.add_node(
    "architect",
    architect
)

builder.add_node(
    "reviewer",
    reviewer
)

builder.add_node(
    "consensus",
    consensus
)

builder.set_entry_point(
    "problem_framer"
)

builder.add_edge(
    "problem_framer",
    "architect"
)

builder.add_edge(
    "architect",
    "reviewer"
)

builder.add_edge(
    "reviewer",
    "consensus"
)

builder.add_edge(
    "consensus",
    END
)

graph = builder.compile()