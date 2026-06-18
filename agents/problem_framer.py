"""Problem Framer agent.

Extracts a structured Decision Context from the PRD using GPT.
"""

import json
import logging

from config import GPT_MODEL
from core.llm_client import get_openai_client, call_with_retry
from core.token_tracker import extract_openai_tokens, estimate_cost

logger = logging.getLogger(__name__)


def problem_framer(state: dict) -> dict:
    """Analyze the PRD and produce a structured decision context.

    Extracts facts, constraints, assumptions, unknowns, risks,
    trade-offs, success criteria, and open questions.
    """
    client = get_openai_client()
    prd = state["prd"]

    prompt = f"""You are a Principal Engineer.

Analyze the following PRD.

PRD:

{json.dumps(prd, indent=2)}

Return ONLY valid JSON in this exact format:

{{
    "facts": [],
    "constraints": [],
    "assumptions": [],
    "unknowns": [],
    "risks": [],
    "tradeoffs": [],
    "success_criteria": [],
    "open_questions": []
}}
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name="problem_framer")
    response_text = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)
    elif response_text.startswith("```"):
        response_text = response_text.replace("```", "", 1)
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    result = json.loads(response_text.strip())

    # Track tokens
    prompt_tokens, completion_tokens = extract_openai_tokens(response)
    cost = estimate_cost(GPT_MODEL, prompt_tokens, completion_tokens)

    llm_calls = state.get("llm_calls", [])
    llm_calls.append({
        "agent": "problem_framer",
        "model": GPT_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": 0,
        "success": True,
        "error": None,
    })

    return {
        "decision_context": result,
        "llm_calls": llm_calls,
        "total_prompt_tokens": state.get("total_prompt_tokens", 0) + prompt_tokens,
        "total_completion_tokens": state.get("total_completion_tokens", 0) + completion_tokens,
        "estimated_cost": state.get("estimated_cost", 0.0) + cost,
    }