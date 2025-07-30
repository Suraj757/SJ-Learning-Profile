"""
Assessment Assistant Agent Prototype
Converts natural teacher observations into Learning Profile assessment scores
"""

import re
from typing import Dict, List, Tuple, Optional
from utils.questions import QUESTIONS, LIKERT_SCALE, CATEGORIES

class AssessmentAssistant:
    def __init__(self):
        self.questions = QUESTIONS
        self.categories = CATEGORIES
        self.keyword_patterns = self._build_keyword_patterns()
    
    def _build_keyword_patterns(self) -> Dict[int, Dict[str, List[str]]]:
        """Build keyword patterns for each question to match observations"""
        patterns = {
            # Communication (Questions 1-4)
            1: {
                "strong_agree": ["detailed story", "tells stories", "elaborate", "narrative", "explains everything"],
                "agree": ["talks about day", "shares", "describes", "tells about"],
                "disagree": ["short answers", "doesn't share", "quiet about"],
                "strong_disagree": ["refuses to talk", "silent", "won't share"]
            },
            2: {
                "strong_agree": ["asks many questions", "makes comments", "interactive", "engages with stories"],
                "agree": ["asks questions", "comments", "participates in story time"],
                "disagree": ["listens quietly", "doesn't participate"],
                "strong_disagree": ["ignores stories", "disruptive", "uninterested"]
            },
            3: {
                "strong_agree": ["loves silly voices", "character voices", "dramatic play", "voice acting"],
                "agree": ["uses different voices", "pretend voices", "silly sounds"],
                "disagree": ["plays quietly", "normal voice"],
                "strong_disagree": ["doesn't do pretend", "avoids roleplay"]
            },
            4: {
                "strong_agree": ["expressive face", "shows emotions clearly", "empathetic reactions"],
                "agree": ["facial expressions", "shows feelings", "reacts to others"],
                "disagree": ["less expressive", "mild reactions"],
                "strong_disagree": ["flat affect", "doesn't react", "no expression"]
            },
            
            # Collaboration (Questions 5-8)
            5: {
                "strong_agree": ["loves taking turns", "waits patiently", "shares easily", "fair play"],
                "agree": ["takes turns", "shares toys", "waits turn"],
                "disagree": ["reluctant to share", "impatient", "needs reminders"],
                "strong_disagree": ["refuses to share", "grabs toys", "won't take turns"]
            },
            6: {
                "strong_agree": ["eager to help", "volunteers", "helpful", "wants to assist"],
                "agree": ["helps with tasks", "assists", "participates in chores"],
                "disagree": ["helps when asked", "sometimes helps"],
                "strong_disagree": ["avoids helping", "refuses tasks", "uncooperative"]
            },
            7: {
                "strong_agree": ["comforts friends", "very caring", "tries to help upset friends"],
                "agree": ["notices when friends sad", "shows concern", "caring"],
                "disagree": ["aware but doesn't act", "mild concern"],
                "strong_disagree": ["ignores upset friends", "unconcerned", "self-focused"]
            },
            8: {
                "strong_agree": ["loves group projects", "team player", "collaborative", "builds together"],
                "agree": ["enjoys group games", "works with others", "cooperative play"],
                "disagree": ["prefers solo", "joins reluctantly"],
                "strong_disagree": ["avoids group activities", "won't collaborate"]
            },
            
            # Content (Questions 9-12)
            9: {
                "strong_agree": ["sings constantly", "knows all words", "loves songs", "musical"],
                "agree": ["sings along", "remembers songs", "enjoys music"],
                "disagree": ["sometimes sings", "knows some songs"],
                "strong_disagree": ["doesn't sing", "uninterested in songs"]
            },
            10: {
                "strong_agree": ["asks about everything outside", "nature lover", "curious about plants/animals"],
                "agree": ["notices nature", "asks questions outside", "observant"],
                "disagree": ["mild interest", "notices sometimes"],
                "strong_disagree": ["uninterested in nature", "doesn't notice outdoors"]
            },
            11: {
                "strong_agree": ["vocabulary explosion", "loves new words", "repeats everything"],
                "agree": ["learns new words", "repeats words", "expanding vocabulary"],
                "disagree": ["learns some words", "gradual growth"],
                "strong_disagree": ["limited vocabulary", "doesn't repeat words"]
            },
            12: {
                "strong_agree": ["counts everything", "loves numbers", "math enthusiasm"],
                "agree": ["enjoys counting", "notices numbers", "counts objects"],
                "disagree": ["counts when prompted", "mild interest"],
                "strong_disagree": ["avoids counting", "no interest in numbers"]
            },
            
            # Critical Thinking (Questions 13-16)
            13: {
                "strong_agree": ["persistent problem solver", "tries many approaches", "creative building"],
                "agree": ["tries different ways", "problem solves", "experiments"],
                "disagree": ["tries a few ways", "gives up easily"],
                "strong_disagree": ["gives up immediately", "doesn't experiment"]
            },
            14: {
                "strong_agree": ["constant why questions", "investigative", "deep curiosity"],
                "agree": ["asks why", "curious", "questions things"],
                "disagree": ["occasional questions", "mild curiosity"],
                "strong_disagree": ["doesn't ask questions", "accepts without questioning"]
            },
            15: {
                "strong_agree": ["excellent organizer", "loves sorting", "systematic cleanup"],
                "agree": ["sorts toys", "organizes", "puts things away"],
                "disagree": ["sorts sometimes", "needs help organizing"],
                "strong_disagree": ["doesn't sort", "messy", "avoids cleanup"]
            },
            16: {
                "strong_agree": ["notices every change", "very aware", "asks about differences"],
                "agree": ["notices changes", "observant", "comments on differences"],
                "disagree": ["sometimes notices", "needs pointing out"],
                "strong_disagree": ["doesn't notice changes", "unaware"]
            },
            
            # Creative Innovation (Questions 17-20)
            17: {
                "strong_agree": ["incredibly creative", "transforms everything", "imaginative use"],
                "agree": ["creative play", "uses objects differently", "imaginative"],
                "disagree": ["some creativity", "occasional creative play"],
                "strong_disagree": ["uses toys traditionally", "not creative"]
            },
            18: {
                "strong_agree": ["elaborate pretend scenarios", "detailed imagination", "complex roleplay"],
                "agree": ["pretend play", "make-believe", "creates scenarios"],
                "disagree": ["simple pretend", "basic roleplay"],
                "strong_disagree": ["doesn't pretend", "avoids make-believe"]
            },
            19: {
                "strong_agree": ["art experimenter", "loves mixing", "creative expression"],
                "agree": ["enjoys art", "tries new techniques", "creative with materials"],
                "disagree": ["does art activities", "follows instructions"],
                "strong_disagree": ["avoids art", "doesn't experiment"]
            },
            20: {
                "strong_agree": ["constantly creating music/dance", "performer", "loves entertaining"],
                "agree": ["makes up songs", "dances", "creates"],
                "disagree": ["occasional creativity", "sometimes makes up things"],
                "strong_disagree": ["doesn't create", "follows only existing songs/dances"]
            },
            
            # Confidence (Questions 21-24)
            21: {
                "strong_agree": ["extremely persistent", "never gives up", "determined"],
                "agree": ["keeps trying", "perseveres", "positive attitude"],
                "disagree": ["tries a few times", "needs encouragement"],
                "strong_disagree": ["gives up quickly", "says can't do it"]
            },
            22: {
                "strong_agree": ["proudly shows everything", "seeks attention for work", "excited to share"],
                "agree": ["shows creations", "proud of work", "wants to share"],
                "disagree": ["sometimes shows work", "modest"],
                "strong_disagree": ["hides work", "shy about creations"]
            },
            23: {
                "strong_agree": ["bounces back immediately", "resilient", "learns from mistakes"],
                "agree": ["tries again", "recovers from mistakes", "persistent"],
                "disagree": ["needs encouragement", "recovers slowly"],
                "strong_disagree": ["gets very upset", "won't try again"]
            },
            24: {
                "strong_agree": ["thrills at new activities", "adventurous", "first to try"],
                "agree": ["likes new things", "willing to try", "open to new"],
                "disagree": ["cautious but willing", "needs encouragement"],
                "strong_disagree": ["avoids new activities", "very cautious", "prefers familiar"]
            }
        }
        return patterns
    
    def analyze_observation(self, observation: str, child_name: str = "child") -> Dict[int, Tuple[int, str, float]]:
        """
        Analyze a natural language observation and suggest scores for relevant questions
        
        Returns: Dict[question_id, (suggested_score, explanation, confidence)]
        """
        observation = observation.lower()
        results = {}
        
        for question_id, patterns in self.keyword_patterns.items():
            score, explanation, confidence = self._match_patterns(observation, question_id, patterns, child_name)
            if score > 0:  # Only include if there's a match
                results[question_id] = (score, explanation, confidence)
        
        return results
    
    def _match_patterns(self, observation: str, question_id: int, patterns: Dict[str, List[str]], child_name: str) -> Tuple[int, str, float]:
        """Match observation against patterns for a specific question"""
        question_text = next(q["text"] for q in self.questions if q["id"] == question_id)
        
        # Check each confidence level (highest to lowest)
        for level in ["strong_agree", "agree", "disagree", "strong_disagree"]:
            for pattern in patterns[level]:
                if pattern in observation:
                    score = LIKERT_SCALE["Strongly Agree"] if level == "strong_agree" else \
                           LIKERT_SCALE["Agree"] if level == "agree" else \
                           LIKERT_SCALE["Disagree"] if level == "disagree" else \
                           LIKERT_SCALE["Strongly Disagree"]
                    
                    confidence = 0.9 if "strong_" in level else 0.7
                    explanation = f"Matched '{pattern}' in observation, suggesting {level.replace('_', ' ')} for: {question_text}"
                    
                    return score, explanation, confidence
        
        return 0, "", 0.0
    
    def process_bulk_observations(self, observations: List[Dict[str, str]]) -> Dict[str, Dict[int, Tuple[int, str, float]]]:
        """
        Process multiple children's observations at once
        
        observations: List of {"child_name": str, "observation": str}
        Returns: Dict[child_name, assessment_results]
        """
        results = {}
        for obs in observations:
            child_name = obs["child_name"]
            observation = obs["observation"]
            results[child_name] = self.analyze_observation(observation, child_name)
        
        return results
    
    def generate_assessment_draft(self, child_name: str, observations: str) -> Dict[str, any]:
        """Generate a complete assessment draft for review"""
        analysis = self.analyze_observation(observations, child_name)
        
        # Create response dict for all questions
        responses = {}
        explanations = {}
        confidence_scores = {}
        
        for question in self.questions:
            q_id = question["id"]
            if q_id in analysis:
                score, explanation, confidence = analysis[q_id]
                responses[q_id] = score
                explanations[q_id] = explanation
                confidence_scores[q_id] = confidence
            else:
                # Default neutral score for unmatched questions
                responses[q_id] = 3  # Neutral
                explanations[q_id] = "No specific observation found - please review and adjust"
                confidence_scores[q_id] = 0.1
        
        return {
            "child_name": child_name,
            "responses": responses,
            "explanations": explanations,
            "confidence_scores": confidence_scores,
            "questions_matched": len(analysis),
            "total_questions": len(self.questions)
        }

def demo_assessment_assistant():
    """Demo the Assessment Assistant with sample observations"""
    assistant = AssessmentAssistant()
    
    # Sample teacher observation
    sample_observation = """
    Sarah had an amazing day today! During circle time, she told us a very detailed story 
    about her weekend trip to the zoo, describing all the animals she saw and even doing 
    voices for them. She was so expressive and got excited when talking about the elephants.
    
    During free play, she built an elaborate block castle and kept trying different ways 
    to make the tower taller when it kept falling down. She said "I can do it!" and 
    didn't give up. When Maria was upset about her drawing, Sarah went over and tried 
    to cheer her up.
    
    She loves helping during snack time and always volunteers to pass out napkins. 
    During art time, she mixed colors to make new shades and was so proud to show 
    everyone her painting. She also made up a silly song while working.
    """
    
    print("🤖 Assessment Assistant Demo")
    print("=" * 50)
    print(f"Teacher Observation:\n{sample_observation}")
    print("\n" + "=" * 50)
    
    # Generate assessment draft
    draft = assistant.generate_assessment_draft("Sarah", sample_observation)
    
    print(f"\nAssessment Draft for {draft['child_name']}:")
    print(f"Questions Matched: {draft['questions_matched']}/{draft['total_questions']}")
    print("\nHigh Confidence Matches:")
    
    high_confidence = [(q_id, data) for q_id, data in draft['explanations'].items() 
                      if draft['confidence_scores'][q_id] > 0.5]
    
    for q_id, explanation in high_confidence:
        question = next(q for q in assistant.questions if q["id"] == q_id)
        score = draft['responses'][q_id]
        confidence = draft['confidence_scores'][q_id]
        
        score_text = {5: "Strongly Agree", 4: "Agree", 3: "Neutral", 2: "Disagree", 1: "Strongly Disagree"}[score]
        
        print(f"\nQ{q_id} ({question['category']}): {question['text']}")
        print(f"Suggested Score: {score_text} (Confidence: {confidence:.1%})")
        print(f"Reasoning: {explanation}")

if __name__ == "__main__":
    demo_assessment_assistant()