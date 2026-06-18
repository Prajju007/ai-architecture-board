"""PRD Generator agent.

Takes any free-form text (Markdown, plain text, README, etc.) and
converts it into a structured PRD JSON using GPT. This lets users
pass any document format — not just hand-crafted JSON.
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


def generate_prd(raw_content: str, source_name: str = "input") -> dict:
    """Convert free-form text into a structured PRD dict.

    Args:
        raw_content: The raw text/Markdown content to convert.
        source_name: Name of the source file (for logging).

    Returns:
        A PRD dict with title, problem_statement, goals, non_goals,
        constraints, success_criteria, budget, timeline.
    """
    client = get_openai_client()

    prompt = f"""You are a Principal Engineer.

A user has provided a document. Your job is to extract or infer a structured Product Requirements Document (PRD) from it.

Source document ({source_name}):

---
{raw_content}
---

Return ONLY valid JSON in this exact format:

{{
    "title": "concise project title",
    "problem_statement": "what problem needs to be solved",
    "goals": ["goal 1", "goal 2"],
    "non_goals": ["explicitly out of scope"],
    "constraints": ["constraint 1", "constraint 2"],
    "success_criteria": ["how to measure success"],
    "budget": "Low / Medium / High",
    "timeline": "Prototype / Weeks / Months / Quarters"
}}

Rules:
- Infer fields that aren't explicitly stated based on context
- If the document is not a PRD, extract the engineering problem it describes
- Keep goals and constraints as concise bullet points
- Budget and timeline should be short labels, not paragraphs
- Return ONLY the JSON, no explanation
"""

    def _call():
        return client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

    response = call_with_retry(_call, agent_name="prd_generator")
    response_text = _strip_fences(response.choices[0].message.content)
    prd = json.loads(response_text)

    logger.info("PRD generated from %s: %s", source_name, prd.get("title", "Unknown"))
    return prd