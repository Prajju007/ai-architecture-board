from typing import TypedDict


class Review(TypedDict):
    reviewer: str
    review: str
    concerns: list[str]


class DecisionContext(TypedDict):
    facts: list[str]
    constraints: list[str]
    assumptions: list[str]
    unknowns: list[str]
    risks: list[str]
    tradeoffs: list[str]
    success_criteria: list[str]
    open_questions: list[str]


class AgentState(TypedDict):

    prd: dict

    decision_context: DecisionContext

    architecture_v1: str

    reviews: list[Review]

    approved: bool