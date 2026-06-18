"""LLM client singletons with retry logic.

Instantiates OpenAI and Gemini clients ONCE and reuses them
across all agent calls. Includes retry with exponential backoff
for transient failures.
"""

from __future__ import annotations

import time
import logging
from typing import Optional

from openai import OpenAI
from google import genai

from config import OPENAI_API_KEY, GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# --- Singleton clients -------------------------------------------------

_openai_client: Optional[OpenAI] = None
_gemini_client: Optional[genai.Client] = None


def get_openai_client() -> OpenAI:
    """Return a shared OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def get_gemini_client() -> genai.Client:
    """Return a shared Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    return _gemini_client


# --- Retry helper -------------------------------------------------------

MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds


def call_with_retry(fn, agent_name: str = "unknown"):
    """Call a function with exponential-backoff retry.

    Args:
        fn: A callable that performs the LLM call and returns the response.
        agent_name: Name of the agent for logging.

    Returns:
        The response object from the LLM call.

    Raises:
        The last exception if all retries fail.
    """
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            wait = INITIAL_BACKOFF ** attempt
            logger.warning(
                "Attempt %d/%d for '%s' failed: %s. Retrying in %ds...",
                attempt, MAX_RETRIES, agent_name, exc, wait,
            )
            time.sleep(wait)

    logger.error("All %d retries exhausted for '%s': %s", MAX_RETRIES, agent_name, last_exc)
    raise last_exc