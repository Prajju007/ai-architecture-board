"""Structured deliberation models.

Each deliberation turn is broken into structured units:
  Claim -> Criticism -> Resolution -> Outcome

This makes the reasoning trail machine-readable and auditable,
instead of a free-text blob.
"""

from typing import TypedDict


class Claim(TypedDict):
    """An assertion made by a model during deliberation."""

    claim: str
    evidence: str
    confidence: str  # "high" | "medium" | "low"


class Criticism(TypedDict):
    """A challenge raised against a claim from the opposing model."""

    target_claim: str
    criticism: str
    severity: str  # "blocking" | "major" | "minor"


class Resolution(TypedDict):
    """How a model updates its position based on deliberation."""

    original_position: str
    updated_position: str
    reason: str


class DeliberationTurn(TypedDict):
    """One structured turn in the deliberation process.

    Replaces the old free-text DeliberationComment. Each turn
    captures claims, criticisms, resolutions, open questions,
    and a summary of the net effect.
    """

    author: str  # "GPT" | "Gemini"
    round: int  # 1, 2, 3...
    claims: list[Claim]
    criticisms: list[Criticism]
    resolutions: list[Resolution]
    open_questions: list[str]
    outcome_summary: str