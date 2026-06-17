from typing import TypedDict


class Review(TypedDict):
    reviewer: str
    review: str
    concerns: list[str]


class AgentState(TypedDict):
    requirement: str

    architecture_v1: str

    reviews: list[Review]

    approved: bool