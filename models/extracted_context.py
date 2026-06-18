from typing import TypedDict


class ExtractedContext(TypedDict):

    facts: list[str]

    constraints: list[str]

    assumptions: list[str]

    decisions_made: list[str]

    alternatives_considered: list[str]

    arguments_for: list[str]

    arguments_against: list[str]

    risks: list[str]

    unknowns: list[str]

    open_questions: list[str]

    unresolved_questions: list[str]
