"""Consensus artifact model produced by the synthesis agent."""

from typing import TypedDict


class Disagreement(TypedDict):
    """A point where GPT and Gemini hold different positions."""

    topic: str
    gpt_position: str
    gemini_position: str


class ConsensusArtifact(TypedDict):
    """Synthesized output after deliberation completes.

    Produced by the synthesis agent from the full deliberation
    transcript. This is NOT a judge's verdict — it is a faithful
    summary of what the models agreed on, disagreed on, and what
    remains open, plus a synthesized recommendation.
    """

    agreements: list[str]
    disagreements: list[Disagreement]
    open_questions: list[str]
    decision_drivers: list[str]
    recommendation: str
    confidence: str  # "high" | "medium" | "low"