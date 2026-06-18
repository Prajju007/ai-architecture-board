"""GPT agent: initial position, structured deliberation, final position.

The deliberation function produces structured JSON turns (claims,
criticisms, resolutions) instead of free-text blobs, making the
reasoning trail machine-readable and auditable.
"""

import json
import logging

from config import GPT_MODEL
from core.llm_client import get_openai_client, call_with_retry
from core.token_tracker import extract_openai_tokens, estimate_cost

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    """Remove markdown JSON code fences from a response string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "", 1)
    elif text.startswith("```"):
        text = text.replace("```", "", 1)
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _record_call(state: dict, agent_name: str, prompt_tokens: int, completion_tokens: int) -> dict:
    """Append an LLM call record and update cumulative token/cost totals."""
    llm_calls = state.get("llm_calls", [])
    llm_calls.append({
        "agent": agent_name,
        "model": GPT_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": 0,
        "success": True,
        "error": None,
    })
    cost = estimate_cost(GPT_MODEL, prompt_tokens, completion_tokens)
    return {
        "llm_calls": llm_calls,
        "total_prompt_tokens": state.get("total_prompt_tokens", 0) + prompt_tokens,
        "total_completion_tokens": state.get("total_completion_tokens", 0) + completion_tokens,
        "estimated_cost": state.get("estimated_cost", 0.0) + cost,
    }


def gpt_initial_position(state: dict) -> dict:
    """Generate GPT's independent initial architecture proposal."""
    client = get_openai_client()

    prompt = f"""You are a Principal Software Architect.

Create an architecture proposal.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Provide your reasoning and recommendation.
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name="gpt_initial_position")
    content = response.choices[0].message.content

    prompt_tokens, completion_tokens = extract_openai_tokens(response)
    tracking = _record_call(state, "gpt_initial_position", prompt_tokens, completion_tokens)

    return {"gpt_initial_position": content, **tracking}


def gpt_deliberation(state: dict) -> dict:
    """One structured deliberation turn from GPT.

    Produces a DeliberationTurn dict with claims, criticisms,
    resolutions, open questions, and an outcome summary.
    """
    client = get_openai_client()

    turns = state.get("deliberation_turns", [])
    current_round = len([t for t in turns if t["author"] == "GPT"]) + 1

    prompt = f"""You are a Principal Software Architect participating in a structured deliberation.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gpt_initial_position']}

Gemini Original Position:

{state['gemini_initial_position']}

Discussion So Far (Structured):

{json.dumps(turns, indent=2)}

Review the discussion so far. Respond ONLY with valid JSON in this exact format:

{{
    "claims": [
        {{
            "claim": "your assertion",
            "evidence": "supporting reasoning or evidence",
            "confidence": "high"
        }}
    ],
    "criticisms": [
        {{
            "target_claim": "the claim from Gemini you are challenging",
            "criticism": "your counterargument",
            "severity": "blocking"
        }}
    ],
    "resolutions": [
        {{
            "original_position": "what you previously thought",
            "updated_position": "your refined view",
            "reason": "why you changed"
        }}
    ],
    "open_questions": [
        "what remains unresolved"
    ],
    "outcome_summary": "net effect of this round on your thinking"
}}

Rules:
- Confidence must be one of: high, medium, low
- Severity must be one of: blocking, major, minor
- Only include resolutions if you actually changed your position
- Be specific and concise — do not repeat earlier points
- Focus on architectural trade-offs, not style preferences
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name=f"gpt_deliberation_r{current_round}")
    response_text = _strip_fences(response.choices[0].message.content)
    turn_data = json.loads(response_text)

    turn = {
        "author": "GPT",
        "round": current_round,
        "claims": turn_data.get("claims", []),
        "criticisms": turn_data.get("criticisms", []),
        "resolutions": turn_data.get("resolutions", []),
        "open_questions": turn_data.get("open_questions", []),
        "outcome_summary": turn_data.get("outcome_summary", ""),
    }

    turns.append(turn)

    prompt_tokens, completion_tokens = extract_openai_tokens(response)
    tracking = _record_call(state, f"gpt_deliberation_r{current_round}", prompt_tokens, completion_tokens)

    return {"deliberation_turns": turns, **tracking}


def gpt_final_position(state: dict) -> dict:
    """Generate GPT's final position after all deliberation rounds."""
    client = get_openai_client()

    prompt = f"""You are a Principal Software Architect.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gpt_initial_position']}

Gemini Original Position:

{state['gemini_initial_position']}

Discussion Transcript (Structured):

{json.dumps(state['deliberation_turns'], indent=2)}

After reviewing the discussion:

1. What is your current recommendation?
2. What changed in your thinking?
3. What remains uncertain?
4. What are the most important decision drivers?

Be concise.
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name="gpt_final_position")
    content = response.choices[0].message.content

    prompt_tokens, completion_tokens = extract_openai_tokens(response)
    tracking = _record_call(state, "gpt_final_position", prompt_tokens, completion_tokens)

    return {"gpt_final_position": content, **tracking}