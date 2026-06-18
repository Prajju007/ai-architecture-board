import json

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    GPT_MODEL
)


def context_extractor(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    context_input = state["context_input"]

    prompt = f"""
You are an expert Staff Engineer.

Your job is NOT to summarize.

Your job is to extract engineering reasoning.

Source Type:

{context_input["source_type"]}

Content:

{context_input["raw_content"]}

Return ONLY valid JSON.

Format:

{{
    "facts": [],
    "constraints": [],
    "assumptions": [],
    "decisions_made": [],
    "alternatives_considered": [],
    "arguments_for": [],
    "arguments_against": [],
    "risks": [],
    "unknowns": [],
    "open_questions": [],
    "unresolved_questions": []
}}

Rules:

- Extract decisions that were actually made.
- Extract alternatives that were discussed.
- Extract arguments supporting decisions.
- Extract arguments opposing decisions.
- Extract unresolved engineering questions.
- Prefer engineering intent over summarization.
- Ignore conversational filler.
"""

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    if response_text.startswith("```json"):
        response_text = response_text.replace(
            "```json",
            "",
            1
        )

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    extracted_context = json.loads(
        response_text.strip()
    )

    return {
        "extracted_context":
        extracted_context
    }