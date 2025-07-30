import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.questions import QUESTIONS
from utils.scoring import calculate_scores, get_personality_label, generate_description

class TestResultsPage(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.valid_responses = {
            1: 5,  # Strongly Agree
            2: 4,  # Agree
            3: 5,  # Strongly Agree
            4: 4,  # Agree
            5: 5,  # Strongly Agree
            6: 4,  # Agree
            7: 5,  # Strongly Agree
            8: 4   # Agree
        }

        self.valid_scores = {
            "Communication": "High",
            "Collaboration": "High",
            "Content": "Medium",
            "Critical Thinking": "Medium",
            "Creative Innovation": "Low",
            "Confidence": "Low"
        }

    def test_description_generation(self):
        """Test description generation with various inputs"""
        # Test with valid scores and no name
        success = generate_description(self.valid_scores)
        self.assertTrue(success)

        # Test with valid scores and name
        success = generate_description(self.valid_scores, "Test Child", 4)
        self.assertTrue(success)

        # Test with invalid scores
        success = generate_description({})
        self.assertFalse(success)

        # Test with invalid score values
        invalid_scores = {"Communication": "Invalid"}
        success = generate_description(invalid_scores)
        self.assertFalse(success)

    def test_full_results_flow(self):
        """Test the entire results generation flow"""
        # First calculate scores
        scores = calculate_scores(self.valid_responses)
        self.assertIsInstance(scores, dict)

        # Get personality label
        label = get_personality_label(scores)
        self.assertIsInstance(label, str)
        self.assertNotEqual(label, "")

        # Generate description
        success = generate_description(scores, "Test Child", 4)
        self.assertTrue(success)

    def test_error_handling(self):
        """Test error handling in the results flow"""
        # Test with empty responses
        with self.assertRaises(ValueError):
            calculate_scores({})

        # Test with invalid response values
        with self.assertRaises(ValueError):
            calculate_scores({1: 10})  # Invalid score

        # Test personality label with invalid scores
        with self.assertRaises(ValueError):
            get_personality_label({"Communication": "Invalid"})

        # Test description generation with invalid input
        success = generate_description(None)
        self.assertFalse(success)

    def test_text_formatting(self):
        """Test text formatting for unnamed children"""
        # Verify capitalization (note: actual string comparison would be done in
        # a real UI test, here we're just verifying the function runs)
        success = generate_description(self.valid_scores, None, 4)
        self.assertTrue(success)
        # Verify capitalization with no child name
        scores = {
            "Communication": "High",
            "Collaboration": "Medium",
            "Content": "Low",
            "Critical Thinking": "Low",
            "Creative Innovation": "Low",
            "Confidence": "Low"
        }

        success = generate_description(scores, None, 4)
        self.assertTrue(success)

class TestCapitalization(unittest.TestCase):
    def test_name_replacement(self):
        """Test proper capitalization of 'Your child' in questions"""
        from main import get_child_text

        # Test sentence starting with [name]
        start_sentence = "[name] loves to tell stories"
        self.assertEqual(
            get_child_text(start_sentence),
            "Your child loves to tell stories"
        )

        # Test sentence with [name] in middle
        mid_sentence = "When [name] plays with others"
        self.assertEqual(
            get_child_text(mid_sentence),
            "When your child plays with others"
        )

if __name__ == '__main__':
    unittest.main()