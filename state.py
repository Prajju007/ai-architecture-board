from typing import TypedDict


class DecisionContext(TypedDict):

    facts: list[str]

    constraints: list[str]

    assumptions: list[str]

    unknowns: list[str]

    risks: list[str]

    tradeoffs: list[str]

    success_criteria: list[str]

    open_questions: list[str]


class DeliberationComment(TypedDict):

    author: str

    comment: str


class AgentState(TypedDict):

    prd: dict

    decision_context: DecisionContext

    gpt_initial_position: str

    gemini_initial_position: str

    deliberation_history: list[DeliberationComment]

    gpt_final_position: str

    gemini_final_position: str

    consensus_artifact: str

    total_prompt_tokens: int

    total_completion_tokens: int

    estimated_cost: float

    llm_calls: int