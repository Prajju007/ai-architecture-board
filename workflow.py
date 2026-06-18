"""LangGraph workflow for the AI Architecture Board.

Builds a deliberation graph with configurable rounds:
  PRD → Problem Framer → GPT Initial → Gemini Initial
  → [Deliberation Round 1..N: GPT then Gemini]
  → GPT Final → Gemini Final → Synthesis → END

The number of deliberation rounds is configurable (default: 2).
"""

from langgraph.graph import StateGraph, END

from models.state import AgentState
from agents import (
    problem_framer,
    gpt_initial_position,
    gemini_initial_position,
    gpt_deliberation,
    gemini_deliberation,
    gpt_final_position,
    gemini_final_position,
    synthesis,
)


def build_graph(rounds: int = 2):
    """Build and compile the deliberation graph.

    Args:
        rounds: Number of deliberation rounds (each round = GPT turn + Gemini turn).

    Returns:
        A compiled LangGraph ready for .invoke().
    """
    builder = StateGraph(AgentState)

    # --- Register nodes ---

    builder.add_node("problem_framer", problem_framer)
    builder.add_node("gpt_initial_position", gpt_initial_position)
    builder.add_node("gemini_initial_position", gemini_initial_position)

    # Register deliberation round nodes dynamically
    for r in range(1, rounds + 1):
        builder.add_node(f"gpt_deliberation_r{r}", gpt_deliberation)
        builder.add_node(f"gemini_deliberation_r{r}", gemini_deliberation)

    builder.add_node("gpt_final_position", gpt_final_position)
    builder.add_node("gemini_final_position", gemini_final_position)
    builder.add_node("synthesis", synthesis)

    # --- Wire edges ---

    builder.set_entry_point("problem_framer")

    builder.add_edge("problem_framer", "gpt_initial_position")
    builder.add_edge("gpt_initial_position", "gemini_initial_position")

    # First deliberation round comes after initial positions
    builder.add_edge("gemini_initial_position", f"gpt_deliberation_r1")
    builder.add_edge(f"gpt_deliberation_r1", f"gemini_deliberation_r1")

    # Chain remaining rounds
    for r in range(1, rounds):
        builder.add_edge(
            f"gemini_deliberation_r{r}",
            f"gpt_deliberation_r{r + 1}",
        )
        builder.add_edge(
            f"gpt_deliberation_r{r + 1}",
            f"gemini_deliberation_r{r + 1}",
        )

    # After last round → final positions → synthesis → END
    builder.add_edge(f"gemini_deliberation_r{rounds}", "gpt_final_position")
    builder.add_edge("gpt_final_position", "gemini_final_position")
    builder.add_edge("gemini_final_position", "synthesis")
    builder.add_edge("synthesis", END)

    return builder.compile()


# Default graph with 2 rounds (backward compatible)
graph = build_graph(rounds=2)