"""Tests for structured deliberation models and persistence."""

import json
import os
import sys
import tempfile
import unittest

# Add parent dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.deliberation import DeliberationTurn
from models.consensus import ConsensusArtifact
from core.persistence import generate_session_id, get_output_dir, save_session, load_session, generate_transcript


class TestSessionIDGeneration(unittest.TestCase):

    def test_session_id_has_date_prefix(self):
        """Session ID should start with a date (YYYY-MM-DD)."""
        sid = generate_session_id("My Test Project")
        self.assertRegex(sid, r"^\d{4}-\d{2}-\d{2}_")

    def test_session_id_is_filesystem_safe(self):
        """Session ID should not contain spaces or special chars."""
        sid = generate_session_id("Project With Spaces & Special!Chars")
        self.assertNotIn(" ", sid)
        self.assertNotIn("!", sid)
        self.assertNotIn("&", sid)

    def test_session_id_preserves_title(self):
        """Session ID should contain a slugified version of the title."""
        sid = generate_session_id("My Architecture Board")
        self.assertIn("my-architecture-board", sid)


class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state = {
            "prd": {
                "title": "Test Project",
                "problem_statement": "Test problem",
                "goals": ["goal1"],
                "constraints": ["constraint1"],
            },
            "session_id": "test_session",
            "decision_context": {
                "facts": ["fact1"],
                "constraints": ["c1"],
                "assumptions": [],
                "unknowns": [],
                "risks": ["r1"],
                "tradeoffs": [],
                "success_criteria": [],
                "open_questions": [],
            },
            "gpt_initial_position": "GPT says X",
            "gemini_initial_position": "Gemini says Y",
            "deliberation_turns": [
                {
                    "author": "GPT",
                    "round": 1,
                    "claims": [{"claim": "test claim", "evidence": "evidence", "confidence": "high"}],
                    "criticisms": [],
                    "resolutions": [],
                    "open_questions": ["unresolved?"],
                    "outcome_summary": "GPT refined position",
                }
            ],
            "gpt_final_position": "GPT final",
            "gemini_final_position": "Gemini final",
            "consensus_artifact": {
                "agreements": ["agree on X"],
                "disagreements": [],
                "open_questions": ["what about Z?"],
                "decision_drivers": ["cost"],
                "recommendation": "do X",
                "confidence": "medium",
            },
            "llm_calls": [
                {"agent": "problem_framer", "model": "gpt-4o", "prompt_tokens": 100,
                 "completion_tokens": 50, "latency_ms": 500, "success": True, "error": None}
            ],
            "total_prompt_tokens": 100,
            "total_completion_tokens": 50,
            "estimated_cost": 0.005,
            "output_dir": os.path.join(self.tmpdir, "test_session"),
        }

    def test_save_session_creates_files(self):
        """save_session should create session.json, transcript.md, and decision_context.json."""
        saved_dir = save_session(self.state)
        self.assertTrue(os.path.isfile(os.path.join(saved_dir, "session.json")))
        self.assertTrue(os.path.isfile(os.path.join(saved_dir, "transcript.md")))
        self.assertTrue(os.path.isfile(os.path.join(saved_dir, "decision_context.json")))

    def test_load_session_roundtrip(self):
        """Loaded session should match the original state."""
        saved_dir = save_session(self.state)
        loaded = load_session(saved_dir)
        self.assertEqual(loaded["session_id"], "test_session")
        self.assertEqual(loaded["prd"]["title"], "Test Project")
        self.assertEqual(loaded["gpt_initial_position"], "GPT says X")
        self.assertEqual(len(loaded["deliberation_turns"]), 1)

    def test_transcript_contains_key_sections(self):
        """Generated transcript should contain all major sections."""
        transcript = generate_transcript(self.state)
        self.assertIn("# Deliberation Session: Test Project", transcript)
        self.assertIn("## Decision Context", transcript)
        self.assertIn("## Initial Positions", transcript)
        self.assertIn("## Deliberation", transcript)
        self.assertIn("## Final Positions", transcript)
        self.assertIn("## Synthesis", transcript)
        self.assertIn("## Run Metadata", transcript)

    def test_transcript_contains_structured_claims(self):
        """Transcript should render structured claims with confidence."""
        transcript = generate_transcript(self.state)
        self.assertIn("[HIGH]", transcript)
        self.assertIn("test claim", transcript)


class TestDeliberationModel(unittest.TestCase):

    def test_deliberation_turn_structure(self):
        """A DeliberationTurn should have all required fields."""
        turn = DeliberationTurn(
            author="GPT",
            round=1,
            claims=[{"claim": "c1", "evidence": "e1", "confidence": "high"}],
            criticisms=[{"target_claim": "tc1", "criticism": "crit1", "severity": "major"}],
            resolutions=[{"original_position": "old", "updated_position": "new", "reason": "r"}],
            open_questions=["q1"],
            outcome_summary="summary",
        )
        self.assertEqual(turn["author"], "GPT")
        self.assertEqual(turn["round"], 1)
        self.assertEqual(len(turn["claims"]), 1)
        self.assertEqual(len(turn["criticisms"]), 1)
        self.assertEqual(len(turn["resolutions"]), 1)


if __name__ == "__main__":
    unittest.main()