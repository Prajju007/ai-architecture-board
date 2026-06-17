from typing import TypedDict


class PRD(TypedDict):

    title: str

    problem_statement: str

    goals: list[str]

    non_goals: list[str]

    constraints: list[str]

    success_criteria: list[str]

    budget: str

    timeline: str
