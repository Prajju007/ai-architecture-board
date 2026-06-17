from langgraph.graph import (
    StateGraph,
    END
)

from state import AgentState

from agents import (
    problem_framer,
    gpt_initial_position,
    gemini_initial_position,
    gpt_deliberation,
    gemini_deliberation,
    gpt_final_position,
    gemini_final_position
)

builder = StateGraph(
    AgentState
)

builder.add_node(
    "problem_framer",
    problem_framer
)

builder.add_node(
    "gpt_initial_position",
    gpt_initial_position
)

builder.add_node(
    "gemini_initial_position",
    gemini_initial_position
)

builder.add_node(
    "gpt_deliberation_r1",
    gpt_deliberation
)

builder.add_node(
    "gemini_deliberation_r1",
    gemini_deliberation
)

builder.add_node(
    "gpt_deliberation_r2",
    gpt_deliberation
)

builder.add_node(
    "gemini_deliberation_r2",
    gemini_deliberation
)

builder.add_node(
    "gpt_final_position",
    gpt_final_position
)

builder.add_node(
    "gemini_final_position",
    gemini_final_position
)

builder.set_entry_point(
    "problem_framer"
)

builder.add_edge(
    "problem_framer",
    "gpt_initial_position"
)

builder.add_edge(
    "gpt_initial_position",
    "gemini_initial_position"
)

builder.add_edge(
    "gemini_initial_position",
    "gpt_deliberation_r1"
)

builder.add_edge(
    "gpt_deliberation_r1",
    "gemini_deliberation_r1"
)

builder.add_edge(
    "gemini_deliberation_r1",
    "gpt_deliberation_r2"
)

builder.add_edge(
    "gpt_deliberation_r2",
    "gemini_deliberation_r2"
)

builder.add_edge(
    "gemini_deliberation_r2",
    "gpt_final_position"
)

builder.add_edge(
    "gpt_final_position",
    "gemini_final_position"
)

builder.add_edge(
    "gemini_final_position",
    END
)

graph = builder.compile()