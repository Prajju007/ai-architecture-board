"""Tests for PRD loading and validation."""

import json
import os
import sys
import unittest

# Add parent dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.prd import PRD


class TestPRDLoading(unittest.TestCase):

    def setUp(self):
        prd_path = os.path.join(os.path.dirname(__file__), "..", "sample_prd.json")
        with open(prd_path, "r") as f:
            self.prd = json.load(f)

    def test_prd_has_required_fields(self):
        """PRD should have all required fields."""
        required = ["title", "problem_statement", "goals", "non_goals",
                     "constraints", "success_criteria", "budget", "timeline"]
        for field in required:
            self.assertIn(field, self.prd, f"PRD missing required field: {field}")

    def test_prd_title_is_string(self):
        self.assertIsInstance(self.prd["title"], str)

    def test_prd_goals_is_list(self):
        self.assertIsInstance(self.prd["goals"], list)
        self.assertGreater(len(self.prd["goals"]), 0)

    def test_prd_constraints_is_list(self):
        self.assertIsInstance(self.prd["constraints"], list)


if __name__ == "__main__":
    unittest.main()