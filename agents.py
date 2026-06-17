import json

from openai import OpenAI
from google import genai

from config import (
    GPT_MODEL,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    GOOGLE_API_KEY
)


def architect(state):
    """
    GPT-4o generates Architecture V1
    """

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
You are a Principal Software Architect.

Your task is to propose a robust architecture.

Focus on:
- Scalability
- Maintainability
- Cost Optimization
- Simplicity
"""
            },
            {
                "role": "user",
                "content": state["requirement"]
            }
        ]
    )

    architecture = response.choices[0].message.content

    return {
        "architecture_v1": architecture
    }


def reviewer(state):
    """
    Gemini reviews Architecture V1
    """

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    prompt = f"""
You are a Principal Architecture Reviewer.

Review the architecture.

Requirement:

{state["requirement"]}

Architecture:

{state["architecture_v1"]}

Return ONLY valid JSON.

Format:

{{
    "review": "Overall assessment",
    "concerns": [
        "Concern 1",
        "Concern 2"
    ]
}}

Do NOT wrap the JSON inside markdown.
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

    response_text = response_text.strip()

    result = json.loads(response_text)

    review_record = {
        "reviewer": "Gemini 3.1 Pro",
        "review": result["review"],
        "concerns": result["concerns"]
    }

    reviews = state.get(
        "reviews",
        []
    )

    reviews.append(
        review_record
    )

    return {
        "reviews": reviews
    }


def consensus(state):
    """
    Determine consensus.
    """

    reviews = state.get(
        "reviews",
        []
    )

    if not reviews:
        return {
            "approved": False
        }

    latest_review = reviews[-1]

    approved = (
        len(
            latest_review["concerns"]
        ) == 0
    )

    return {
        "approved": approved
    }