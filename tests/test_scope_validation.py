"""
Test scope validation functionality
"""

import unittest
from agents.ResearchAgent import ResearchAgent


class TestScopeValidation(unittest.TestCase):

    def test_out_of_scope_restaurant_query(self):
        """Test that restaurant recommendation queries are marked as out of scope"""
        agent = ResearchAgent()
        result = agent.research("What is the best restaurant in New York City?")

        self.assertIn("Out of Scope", result["result"])
        self.assertEqual(result["scope_check"], "out_of_scope")


if __name__ == "__main__":
    unittest.main()