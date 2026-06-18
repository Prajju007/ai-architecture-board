"""Updated AgentState with structured deliberation, observability, and persistence fields."""

from __future__ import annotations

from typing import TypedDict, Optional

from models.decision_context import DecisionContext
from models.deliberation import DeliberationTurn
from models.consensus import ConsensusArtifact


class LLMCallRecord(TypedDict):
    """A single LLM API call record for observability."""

    agent: str  # e.g. "problem_framer", "gpt_initial_position"
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    success: bool
    error: Optional[str]


class AgentState(TypedDict):
    """Full state for the deliberation board workflow.

    Carries everything from PRD input through structured deliberation
    turns to final synthesis, plus observability metadata.
    """

    # Input
    prd: dict
    session_id: str
    rounds: int  # number of deliberation rounds

    # Problem framing
    decision_context: DecisionContext

    # Initial positions
    gpt_initial_position: str
    gemini_initial_position: str

    # Structured deliberation (replaces free-text history)
    deliberation_turns: list[DeliberationTurn]

    # Final positions
    gpt_final_position: str
    gemini_final_position: str

    # Synthesis
    consensus_artifact: ConsensusArtifact

    # Observability
    llm_calls: list[LLMCallRecord]
    total_prompt_tokens: int
    total_completion_tokens: int
    estimated_cost: float

    # Persistence
    output_dir: str