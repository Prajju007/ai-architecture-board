"""Decision context model extracted by the problem framer."""

from typing import TypedDict


class DecisionContext(TypedDict):
    """Structured problem analysis extracted from the PRD.

    Captures the engineering context that all agents reason about:
    facts, constraints, assumptions, unknowns, risks, trade-offs,
    success criteria, and open questions.
    """

    facts: list[str]
    constraints: list[str]
    assumptions: list[str]
    unknowns: list[str]
    risks: list[str]
    tradeoffs: list[str]
    success_criteria: list[str]
    open_questions: list[str]