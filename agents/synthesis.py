"""Synthesis agent (GPT-based, anti-hallucination).

Produces the ConsensusArtifact after deliberation completes. The
prompt is carefully designed to prevent hallucination: the model is
instructed to synthesize ONLY from the provided transcript and to
explicitly mark anything not supported by the discussion as an open
question rather than inventing an answer.
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


def synthesis(state: dict) -> dict:
    """Synthesize a consensus artifact from the full deliberation transcript.

    Anti-hallucination safeguards in the prompt:
    1. Model is told it is a synthesizer, not a decision-maker.
    2. Model is told to ONLY use information present in the transcript.
    3. Model is told to mark unsupported claims as open questions.
    4. Model is told NOT to introduce new architectural ideas.
    5. Recommendation must be traceable to positions in the transcript.
    """
    client = get_openai_client()

    prompt = f"""You are a Synthesis Agent for an engineering deliberation board.

Your job is to summarize what happened — NOT to make the decision.

You will receive:
1. The Decision Context
2. GPT's initial and final positions
3. Gemini's initial and final positions
4. The structured deliberation transcript

CRITICAL RULES (to prevent hallucination):
- You may ONLY reference information that appears in the inputs above.
- You may NOT introduce new architectural ideas, technologies, or approaches.
- If something is not discussed, do NOT invent it — mark it as an open question.
- Your recommendation must be traceable to the positions taken by GPT and Gemini.
- If GPT and Gemini genuinely disagree on something and neither concedes, that is a disagreement — do NOT force agreement.
- You are a synthesizer, not an arbitrator. The human makes the final decision.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

GPT Initial Position:

{state['gpt_initial_position']}

Gemini Initial Position:

{state['gemini_initial_position']}

GPT Final Position:

{state['gpt_final_position']}

Gemini Final Position:

{state['gemini_final_position']}

Deliberation Transcript (Structured):

{json.dumps(state['deliberation_turns'], indent=2)}

Respond ONLY with valid JSON in this exact format:

{{
    "agreements": [
        "points where GPT and Gemini explicitly agree"
    ],
    "disagreements": [
        {{
            "topic": "the subject of disagreement",
            "gpt_position": "what GPT says",
            "gemini_position": "what Gemini says"
        }}
    ],
    "open_questions": [
        "things that remain unresolved or were never discussed"
    ],
    "decision_drivers": [
        "the most important factors that should drive the final decision"
    ],
    "recommendation": "a synthesized recommendation based ONLY on the above",
    "confidence": "high"
}}

Rules:
- Confidence must be one of: high, medium, low
- Every agreement and disagreement must be traceable to the transcript
- If you cannot find evidence for something in the transcript, it goes in open_questions
- The recommendation should reflect what the deliberation supports, not your own opinion
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name="synthesis")
    response_text = _strip_fences(response.choices[0].message.content)
    result = json.loads(response_text)

    prompt_tokens, completion_tokens = extract_openai_tokens(response)
    cost = estimate_cost(GPT_MODEL, prompt_tokens, completion_tokens)

    llm_calls = state.get("llm_calls", [])
    llm_calls.append({
        "agent": "synthesis",
        "model": GPT_MODEL,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": 0,
        "success": True,
        "error": None,
    })

    return {
        "consensus_artifact": result,
        "llm_calls": llm_calls,
        "total_prompt_tokens": state.get("total_prompt_tokens", 0) + prompt_tokens,
        "total_completion_tokens": state.get("total_completion_tokens", 0) + completion_tokens,
        "estimated_cost": state.get("estimated_cost", 0.0) + cost,
    }