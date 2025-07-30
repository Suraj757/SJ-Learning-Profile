import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.scoring import calculate_scores, get_personality_label
from utils.questions import QUESTIONS

class TestScoring(unittest.TestCase):
    def setUp(self):
        # Sample responses for testing
        self.sample_responses = {
            1: 5,  # Strongly Agree
            2: 4,  # Agree
            3: 5,  # Strongly Agree
            4: 4,  # Agree
            5: 2,  # Disagree
            6: 1,  # Strongly Disagree
            7: 2,  # Disagree
            8: 1   # Strongly Disagree
        }

    def test_calculate_scores(self):
        """Test score calculation logic"""
        scores = calculate_scores(self.sample_responses)

        # Verify scores is a dictionary
        self.assertIsInstance(scores, dict)

        # Verify all categories are present
        expected_categories = {"Communication", "Collaboration", "Content", 
                             "Critical Thinking", "Creative Innovation", "Confidence"}
        self.assertEqual(set(scores.keys()), expected_categories)

        # Verify score values are valid
        valid_scores = {"High", "Medium", "Low"}
        for score in scores.values():
            self.assertIn(score, valid_scores)

        # Test specific score calculation
        # Communication should be High (avg > 3.75)
        self.assertEqual(scores["Communication"], "High")
        # Collaboration should be Low (avg <= 2.5)
        self.assertEqual(scores["Collaboration"], "Low")

    def test_personality_label(self):
        """Test personality label generation"""
        # Test case for all low scores
        all_low = {cat: "Low" for cat in ["Communication", "Collaboration", "Content", 
                                       "Critical Thinking", "Creative Innovation", "Confidence"]}
        label = get_personality_label(all_low)
        self.assertEqual(label, "Learning Explorer")

        # Test case for high communication and creativity
        high_comm_creative = {
            "Communication": "High",
            "Creative Innovation": "High",
            "Collaboration": "Medium",
            "Content": "Medium",
            "Critical Thinking": "Low",
            "Confidence": "Low"
        }
        label = get_personality_label(high_comm_creative)
        self.assertEqual(label, "Creative Storyteller")

        # Test empty scores
        label = get_personality_label({})
        self.assertEqual(label, "Learning Explorer")

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Empty responses
        empty_scores = calculate_scores({})
        self.assertIsInstance(empty_scores, dict)

        # Partial responses
        partial_responses = {1: 5}  # Only one response
        partial_scores = calculate_scores(partial_responses)
        self.assertIsInstance(partial_scores, dict)

        # Invalid response values
        with self.assertRaises(ValueError):
            calculate_scores({1: 10})  # Invalid score

        # Invalid scores for personality label
        with self.assertRaises(ValueError):
            get_personality_label({"Communication": "Invalid"})

if __name__ == '__main__':
    unittest.main()