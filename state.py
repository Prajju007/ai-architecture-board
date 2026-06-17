from typing import TypedDict


class Concern(TypedDict):

    id: str

    description: str

    severity: str

    category: str

    status: str

    rationale: str


class Review(TypedDict):

    reviewer: str

    review: str


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

    concerns: list[Concern]

    approved: bool