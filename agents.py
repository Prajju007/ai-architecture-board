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

    response_text = response.choices[0].message.content.strip()

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


def gpt_initial_position(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Create an architecture proposal.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Provide your reasoning and recommendation.
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

    return {
        "gpt_initial_position":
        response.choices[0].message.content
    }


def gemini_initial_position(state):

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Create an architecture proposal.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Provide your reasoning and recommendation.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return {
        "gemini_initial_position":
        response.text
    }


def gpt_deliberation(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gpt_initial_position']}

Gemini Original Position:

{state['gemini_initial_position']}

Discussion So Far:

{json.dumps(state.get('deliberation_history', []), indent=2)}

Review the discussion.

Answer:

1. What changed your thinking?
2. What assumptions remain unvalidated?
3. What information is still missing?
4. How would you refine your recommendation?

Do not repeat earlier points unless necessary.
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

    history = state.get(
        "deliberation_history",
        []
    )

    history.append(
        {
            "author": "GPT",
            "comment":
            response.choices[0].message.content
        }
    )

    return {
        "deliberation_history": history
    }


def gemini_deliberation(state):

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gemini_initial_position']}

GPT Original Position:

{state['gpt_initial_position']}

Discussion So Far:

{json.dumps(state.get('deliberation_history', []), indent=2)}

Review the discussion.

Answer:

1. What changed your thinking?
2. What assumptions remain unvalidated?
3. What information is still missing?
4. How would you refine your recommendation?

Do not repeat earlier points unless necessary.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    history = state.get(
        "deliberation_history",
        []
    )

    history.append(
        {
            "author": "Gemini",
            "comment": response.text
        }
    )

    return {
        "deliberation_history": history
    }


def gpt_final_position(state):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gpt_initial_position']}

Gemini Original Position:

{state['gemini_initial_position']}

Discussion Transcript:

{json.dumps(state['deliberation_history'], indent=2)}

After reviewing the discussion:

1. What is your current recommendation?
2. What changed in your thinking?
3. What remains uncertain?
4. What are the most important decision drivers?

Be concise.
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

    return {
        "gpt_final_position":
        response.choices[0].message.content
    }


def gemini_final_position(state):

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    prompt = f"""
You are a Principal Software Architect.

Decision Context:

{json.dumps(state['decision_context'], indent=2)}

Your Original Position:

{state['gemini_initial_position']}

GPT Original Position:

{state['gpt_initial_position']}

Discussion Transcript:

{json.dumps(state['deliberation_history'], indent=2)}

After reviewing the discussion:

1. What is your current recommendation?
2. What changed in your thinking?
3. What remains uncertain?
4. What are the most important decision drivers?

Be concise.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return {
        "gemini_final_position":
        response.text
    }