"""Token and cost tracking for all LLM calls.

Every LLM call should be recorded here so the final session
report includes total tokens used and estimated cost.
"""

from __future__ import annotations

# Rough per-1K-token pricing in USD (update as providers change).
# These are approximate; adjust in config if you need precision.
PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gemini-3.1-pro-preview": {"input": 0.00125, "output": 0.005},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate the cost of a single LLM call.

    Args:
        model: The model identifier (e.g. "gpt-4o").
        prompt_tokens: Number of input tokens used.
        completion_tokens: Number of output tokens used.

    Returns:
        Estimated cost in USD.
    """
    rates = PRICING.get(model, {"input": 0.001, "output": 0.003})
    cost = (prompt_tokens / 1000) * rates["input"] + (completion_tokens / 1000) * rates["output"]
    return round(cost, 6)


def extract_openai_tokens(response) -> tuple:
    """Extract prompt and completion token counts from an OpenAI response."""
    usage = getattr(response, "usage", None)
    if usage:
        return usage.prompt_tokens, usage.completion_tokens
    return 0, 0


def extract_gemini_tokens(response) -> tuple:
    """Extract prompt and completion token counts from a Gemini response.

    Gemini's usage metadata field name varies across SDK versions.
    """
    usage = getattr(response, "usage_metadata", None)
    if usage:
        prompt = getattr(usage, "prompt_token_count", 0) or getattr(usage, "prompt_tokens", 0) or 0
        completion = getattr(usage, "candidates_token_count", 0) or getattr(usage, "completion_tokens", 0) or 0
        return prompt, completion
    return 0, 0