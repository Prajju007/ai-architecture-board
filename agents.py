import json

from openai import OpenAI
from google import genai

from config import (
    GPT_MODEL,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    GOOGLE_API_KEY
)


def problem_framer(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prd = state["prd"]

    prompt = f"""
You are a Principal Engineer.

Analyze the following PRD.

PRD:

{json.dumps(prd, indent=2)}

Return ONLY valid JSON.

Format:

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

    result = json.loads(
        response_text.strip()
    )

    return {
        "decision_context": result
    }


def architect(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    context = state["decision_context"]

    prompt = f"""
You are a Principal Software Architect.

Create an architecture proposal.

Decision Context:

{json.dumps(context, indent=2)}

The architecture must respect:

- Constraints
- Non-goals
- Success Criteria

Avoid unnecessary complexity.
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

    architecture = (
        response
        .choices[0]
        .message
        .content
    )

    return {
        "architecture_v1": architecture
    }


def reviewer(state):

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    prompt = f"""
You are a Principal Architecture Reviewer.

Decision Context:

{json.dumps(state["decision_context"], indent=2)}

Architecture:

{state["architecture_v1"]}

Review the architecture.

Return ONLY JSON.

Format:

{{
  "review": "",
  "concerns": [
    {{
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "category": "",
      "description": ""
    }}
  ]
}}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace(
            "```json",
            "",
            1
        )

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    result = json.loads(
        response_text.strip()
    )

    reviews = state.get(
        "reviews",
        []
    )

    concerns = state.get(
        "concerns",
        []
    )

    review_record = {
        "reviewer": "Gemini 3.1 Pro",
        "review": result["review"]
    }

    reviews.append(
        review_record
    )

    existing_count = len(
        concerns
    )

    for index, concern in enumerate(
        result["concerns"],
        start=1
    ):

        concern_record = {

            "id":
            f"C{existing_count + index:03d}",

            "description":
            concern["description"],

            "severity":
            concern["severity"],

            "category":
            concern["category"],

            "status":
            "OPEN",

            "rationale":
            ""
        }

        concerns.append(
            concern_record
        )

    return {

        "reviews": reviews,

        "concerns": concerns
    }


def consensus(state):

    concerns = state.get(
        "concerns",
        []
    )

    open_concerns = [

        concern

        for concern in concerns

        if concern["status"] == "OPEN"
    ]

    approved = (
        len(open_concerns) == 0
    )

    return {
        "approved": approved
    }