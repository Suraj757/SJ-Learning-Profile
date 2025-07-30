import streamlit as st
import pandas as pd
import numpy as np
from utils.questions import QUESTIONS, LIKERT_SCALE, CATEGORIES

def get_personality_label(scores):
    """Generate a fun personality label based on top scoring categories."""
    if not isinstance(scores, dict) or not scores:
        return "Learning Explorer"

    # Validate scores
    valid_scores = {"High", "Medium", "Low"}
    if not all(score in valid_scores for score in scores.values()):
        raise ValueError("Invalid score values detected")

    # Check if all scores are low
    if all(score == "Low" for score in scores.values()):
        return "Learning Explorer"

    # Get top 2 categories with scores better than "Low"
    top_categories = [cat for cat, score in sorted(scores.items(), 
                     key=lambda x: 3 if x[1] == "High" else 2 if x[1] == "Medium" else 1, 
                     reverse=True) if score != "Low"][:2]

    # If we don't have at least 2 categories above "Low", return default
    if len(top_categories) < 2:
        return "Learning Explorer"

    personality_labels = {
        ("Communication", "Creative Innovation"): "Creative Storyteller",
        ("Communication", "Collaboration"): "Team Motivator",
        ("Communication", "Confidence"): "Confident Speaker",
        ("Creative Innovation", "Critical Thinking"): "Curious Inventor",
        ("Creative Innovation", "Content"): "Knowledge Explorer",
        ("Collaboration", "Confidence"): "Inspiring Leader",
        ("Critical Thinking", "Content"): "Deep Thinker",
        ("Critical Thinking", "Collaboration"): "Problem-Solving Partner",
        ("Content", "Communication"): "Knowledge Sharer",
        ("Confidence", "Creative Innovation"): "Bold Creator"
    }

    # Try both orders of the top categories
    label = personality_labels.get(tuple(top_categories)) or \
            personality_labels.get(tuple(reversed(top_categories))) or \
            "Learning Explorer"  # Default label

    return label

def calculate_scores(responses):
    """Calculate category scores from responses."""
    if not isinstance(responses, dict):
        raise ValueError("Responses must be a dictionary")

    # Validate response values
    valid_values = set(LIKERT_SCALE.values())
    if not all(response in valid_values for response in responses.values()):
        raise ValueError("Invalid response values detected")

    category_scores = {category: 0 for category in CATEGORIES}
    category_counts = {category: 0 for category in CATEGORIES}

    # Calculate total scores per category
    for q_id, response in responses.items():
        question = next((q for q in QUESTIONS if q["id"] == q_id), None)
        if question is None:
            continue
        category = question["category"]
        category_scores[category] += response
        category_counts[category] += 1

    # Calculate final scores
    final_scores = {}
    for category in category_scores:
        if category_counts[category] > 0:
            avg_score = category_scores[category] / category_counts[category]
            if avg_score <= 2.5:
                final_scores[category] = "Low"
            elif avg_score <= 3.75:
                final_scores[category] = "Medium"
            else:
                final_scores[category] = "High"
        else:
            final_scores[category] = "Low"  # Default to low if no responses

    return final_scores

def get_category_description(category):
    """Get the description for a category."""
    descriptions = {
        "Communication": "the ability to express ideas clearly and listen effectively",
        "Collaboration": "working well with others and contributing to group success",
        "Content": "understanding and retaining subject matter knowledge",
        "Critical Thinking": "analyzing information and solving problems logically",
        "Creative Innovation": "finding unique solutions and thinking outside the box",
        "Confidence": "believing in oneself and taking on new challenges"
    }
    return descriptions.get(category, "")

def generate_description(scores, child_name=None, age=None):
    """Generate a written description of the results."""
    try:
        # Validate inputs
        if not isinstance(scores, dict) or not scores:
            raise ValueError("Invalid scores provided")

        # Convert individual ratings into a narrative
        strengths = [cat for cat, score in scores.items() if score == "High"]
        developing = [cat for cat, score in scores.items() if score == "Medium"]
        growth_areas = [cat for cat, score in scores.items() if score == "Low"]

        # Format name properly for sentence starts
        child_text = child_name if child_name else "your child"  # lowercase for mid-sentence
        sentence_start_text = child_name if child_name else "Your child"  # Capitalized for sentence starts

        # Display results sections
        if strengths:
            strength_list = []
            for cat in strengths:
                desc = get_category_description(cat)
                strength_list.append(f"**{cat}** ({desc})")

            strength_text = " and ".join(strength_list) if len(strength_list) == 2 else \
                          ", ".join(strength_list[:-1]) + ", and " + strength_list[-1] if len(strength_list) > 2 else \
                          strength_list[0]

            st.subheader(f"{sentence_start_text}'s Superpowers!")
            st.write(f"Wow! {sentence_start_text} shows amazing abilities in {strength_text}! These natural talents make them truly special and can help them soar in their learning journey! 🌟")

            if age:
                st.write("Here are some fun ways to celebrate these superpowers:")
                for category in strengths:
                    activities = get_age_appropriate_activities(category, age)
                    st.write(f"\n**{category}:**")
                    for activity in activities:
                        st.write(f"• {activity}")

        if developing:
            developing_list = []
            for cat in developing:
                desc = get_category_description(cat)
                developing_list.append(f"**{cat}** ({desc})")

            developing_text = " and ".join(developing_list) if len(developing_list) == 2 else \
                            ", ".join(developing_list[:-1]) + ", and " + developing_list[-1] if len(developing_list) > 2 else \
                            developing_list[0]

            st.subheader("Growing Strengths")
            st.write(f"{sentence_start_text} is making great progress in {developing_text}. These skills are like seeds that are starting to sprout! With a little care and practice, they'll grow into new superpowers! 🌱")

            if age:
                st.write("Try these fun activities to help these skills grow:")
                for category in developing:
                    activities = get_age_appropriate_activities(category, age)
                    st.write(f"\n**{category}:**")
                    for activity in activities:
                        st.write(f"• {activity}")

        if growth_areas:
            growth_list = []
            for cat in growth_areas:
                desc = get_category_description(cat)
                growth_list.append(f"**{cat}** ({desc})")

            growth_text = " and ".join(growth_list) if len(growth_list) == 2 else \
                         ", ".join(growth_list[:-1]) + ", and " + growth_list[-1] if len(growth_list) > 2 else \
                         growth_list[0]

            st.subheader("Adventure Areas")
            st.write(f"Every superhero has new powers to discover! Let's explore how {child_text} can grow in {growth_text} through these fun activities:")

            if age:
                for category in growth_areas:
                    activities = get_age_appropriate_activities(category, age)
                    st.write(f"\n**{category}:**")
                    for activity in activities:
                        st.write(f"• {activity}")

        return True

    except Exception as e:
        st.error(f"An error occurred while generating the description: {str(e)}")
        return False

def get_age_appropriate_activities(category, age):
    """Get age-appropriate activities for a category."""
    activities = {
        "Communication": {
            "young": [  # Ages 4-5
                "Play 'show and tell' with favorite toys",
                "Take turns telling parts of a bedtime story",
                "Practice using kind words in everyday situations"
            ]
        },
        "Collaboration": {
            "young": [
                "Play simple board games that require taking turns",
                "Work together to build a block tower",
                "Help prepare a snack with a family member"
            ]
        },
        "Content": {
            "young": [
                "Count objects during daily activities",
                "Name colors and shapes in the environment",
                "Learn simple songs about numbers and letters"
            ]
        },
        "Critical Thinking": {
            "young": [
                "Sort toys by color, size, or type",
                "Complete age-appropriate puzzles",
                "Play 'I Spy' with descriptions"
            ]
        },
        "Creative Innovation": {
            "young": [
                "Create art with different materials",
                "Make up new endings to familiar stories",
                "Build imaginary worlds with blocks or boxes"
            ]
        },
        "Confidence": {
            "young": [
                "Practice new physical skills like hopping or skipping",
                "Help with simple household tasks",
                "Choose their own outfit for the day"
            ]
        }
    }

    return activities[category]["young"]  # Always return young activities for ages 4-5