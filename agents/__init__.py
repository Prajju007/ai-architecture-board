"""Agents package for the AI Architecture Board."""

from agents.prd_generator import generate_prd
from agents.problem_framer import problem_framer
from agents.gpt_agent import gpt_initial_position, gpt_deliberation, gpt_final_position
from agents.gemini_agent import gemini_initial_position, gemini_deliberation, gemini_final_position
from agents.synthesis import synthesis

__all__ = [
    "generate_prd",
    "problem_framer",
    "gpt_initial_position",
    "gpt_deliberation",
    "gpt_final_position",
    "gemini_initial_position",
    "gemini_deliberation",
    "gemini_final_position",
    "synthesis",
]