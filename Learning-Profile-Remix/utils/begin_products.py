"""
Begin Product Recommendation Engine
Provides personalized Begin product suggestions based on learning profiles
"""

import random
from typing import Dict, List, Any

BEGIN_PRODUCTS = {
    "apps": {
        "Begin Reading": {
            "age_range": "3-8",
            "categories": ["Communication", "Content"],
            "description": "Interactive phonics and reading app with personalized learning paths",
            "benefits": ["Builds foundational reading skills", "Develops vocabulary", "Improves comprehension"],
            "url": "https://begin.com/reading"
        },
        "Begin Math": {
            "age_range": "3-8", 
            "categories": ["Critical Thinking", "Content"],
            "description": "Math concepts through games and visual learning",
            "benefits": ["Number sense development", "Problem-solving skills", "Mathematical reasoning"],
            "url": "https://begin.com/math"
        },
        "Begin Creative": {
            "age_range": "3-10",
            "categories": ["Creative Innovation", "Communication"],
            "description": "Art, music, and storytelling activities to spark creativity",
            "benefits": ["Artistic expression", "Creative thinking", "Story creation skills"],
            "url": "https://begin.com/creative"
        },
        "Begin Social": {
            "age_range": "4-9",
            "categories": ["Collaboration", "Confidence"],
            "description": "Social-emotional learning through interactive scenarios",
            "benefits": ["Emotional intelligence", "Social skills", "Empathy development"],
            "url": "https://begin.com/social"
        }
    },
    "kits": {
        "Hands-On Science Kit": {
            "age_range": "5-10",
            "categories": ["Critical Thinking", "Creative Innovation"],
            "description": "Monthly science experiments and STEM activities",
            "benefits": ["Scientific thinking", "Hands-on exploration", "Critical analysis"],
            "url": "https://begin.com/science-kit"
        },
        "Creative Arts Kit": {
            "age_range": "3-8",
            "categories": ["Creative Innovation", "Communication"],
            "description": "Art supplies and guided projects for creative expression",
            "benefits": ["Fine motor skills", "Artistic confidence", "Creative problem-solving"],
            "url": "https://begin.com/arts-kit"
        },
        "Reading Adventure Kit": {
            "age_range": "4-9",
            "categories": ["Communication", "Content"],
            "description": "Books, reading games, and comprehension activities",
            "benefits": ["Reading fluency", "Vocabulary growth", "Story comprehension"],
            "url": "https://begin.com/reading-kit"
        },
        "Social Skills Kit": {
            "age_range": "4-8",
            "categories": ["Collaboration", "Confidence"],
            "description": "Games and activities for building social connections",
            "benefits": ["Friendship skills", "Emotional regulation", "Cooperative play"],
            "url": "https://begin.com/social-kit"
        }
    },
    "classes": {
        "Creative Writing Workshop": {
            "age_range": "6-10",
            "categories": ["Communication", "Creative Innovation"],
            "description": "Small group live classes focused on storytelling and writing",
            "benefits": ["Writing skills", "Creative expression", "Peer collaboration"],
            "url": "https://begin.com/writing-class"
        },
        "Math Explorers": {
            "age_range": "5-9",
            "categories": ["Critical Thinking", "Content"],
            "description": "Interactive math problem-solving with expert teachers",
            "benefits": ["Mathematical reasoning", "Problem-solving confidence", "Peer learning"],
            "url": "https://begin.com/math-class"
        },
        "Art & Design Studio": {
            "age_range": "4-10",
            "categories": ["Creative Innovation", "Confidence"],
            "description": "Live art classes with professional artists and designers",
            "benefits": ["Artistic techniques", "Creative confidence", "Portfolio building"],
            "url": "https://begin.com/art-class"
        },
        "Science Discovery Lab": {
            "age_range": "6-11",
            "categories": ["Critical Thinking", "Content"],
            "description": "Hands-on science experiments and investigations",
            "benefits": ["Scientific inquiry", "Experimental skills", "STEM confidence"],
            "url": "https://begin.com/science-class"
        }
    },
    "tutoring": {
        "Reading Support": {
            "age_range": "4-10",
            "categories": ["Communication", "Content"],
            "description": "1:1 reading tutoring with certified literacy specialists",
            "benefits": ["Personalized reading support", "Confidence building", "Skill acceleration"],
            "url": "https://begin.com/reading-tutor"
        },
        "Math Mastery": {
            "age_range": "5-11",
            "categories": ["Critical Thinking", "Content"],
            "description": "Individual math tutoring tailored to learning style",
            "benefits": ["Personalized math support", "Concept mastery", "Problem-solving skills"],
            "url": "https://begin.com/math-tutor"
        },
        "Social-Emotional Learning": {
            "age_range": "4-9",
            "categories": ["Collaboration", "Confidence"],
            "description": "1:1 support for social skills and emotional development",
            "benefits": ["Emotional intelligence", "Social confidence", "Behavioral strategies"],
            "url": "https://begin.com/sel-tutor"
        },
        "Creative Expression": {
            "age_range": "5-10",
            "categories": ["Creative Innovation", "Communication"],
            "description": "Individual coaching for creative writing, art, and storytelling",
            "benefits": ["Creative confidence", "Artistic skills", "Self-expression"],
            "url": "https://begin.com/creative-tutor"
        }
    }
}

EXTERNAL_ACTIVITIES = {
    "Communication": [
        "Family storytelling time with picture books",
        "Recording daily video journals together",
        "Playing charades and acting games",
        "Having 'interview' conversations about their day",
        "Creating puppet shows with different characters"
    ],
    "Collaboration": [
        "Cooking simple recipes together",
        "Building puzzles as a team",
        "Playing cooperative board games",
        "Organizing neighborhood scavenger hunts",
        "Doing family art projects with shared goals"
    ],
    "Content": [
        "Nature walks with observation journals",
        "Library visits with book selection time",
        "Educational museum or zoo trips",
        "Gardening and plant observation",
        "Simple science experiments at home"
    ],
    "Critical Thinking": [
        "Brain teaser puzzles and riddles",
        "Strategy games like chess or checkers",
        "Mystery-solving activities and treasure hunts",
        "Building challenges with blocks or LEGOs",
        "Comparing and sorting household objects"
    ],
    "Creative Innovation": [
        "Open-ended art projects with recycled materials",
        "Making up songs and dance routines",
        "Building forts and imaginary spaces",
        "Creating comic strips or storybooks",
        "Inventing new games with household items"
    ],
    "Confidence": [
        "Setting and celebrating small daily goals",
        "Teaching them to teach you something new",
        "Encouraging presentation of their creations",
        "Practicing positive self-talk activities",
        "Trying new activities in low-pressure settings"
    ]
}

def get_begin_recommendations(scores: Dict[str, str], child_age: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate personalized Begin product recommendations based on learning profile
    """
    recommendations = {
        "strength_builders": [],
        "growth_supporters": [],
        "balanced_development": []
    }
    
    # Identify strengths and growth areas
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    medium_areas = [cat for cat, score in scores.items() if score == "Medium"]
    
    # Recommend products for strength building
    for strength in strengths[:2]:  # Top 2 strengths
        strength_products = find_products_for_category(strength, child_age)
        recommendations["strength_builders"].extend(strength_products[:2])
    
    # Recommend products for growth areas
    for growth_area in growth_areas[:2]:  # Top 2 growth areas
        growth_products = find_products_for_category(growth_area, child_age)
        recommendations["growth_supporters"].extend(growth_products[:2])
    
    # Recommend balanced products for medium areas
    for medium_area in medium_areas[:1]:  # Top medium area
        balanced_products = find_products_for_category(medium_area, child_age)
        recommendations["balanced_development"].extend(balanced_products[:1])
    
    return recommendations

def find_products_for_category(category: str, child_age: int) -> List[Dict[str, Any]]:
    """
    Find Begin products that support a specific learning category
    """
    matching_products = []
    
    for product_type, products in BEGIN_PRODUCTS.items():
        for name, details in products.items():
            # Check if product supports this category
            if category in details["categories"]:
                # Check if age-appropriate
                if is_age_appropriate(details["age_range"], child_age):
                    product_info = {
                        "name": name,
                        "type": product_type,
                        "description": details["description"],
                        "benefits": details["benefits"],
                        "url": details["url"],
                        "category_match": category
                    }
                    matching_products.append(product_info)
    
    return matching_products

def is_age_appropriate(age_range: str, child_age: int) -> bool:
    """
    Check if a product is appropriate for the child's age
    """
    try:
        min_age, max_age = map(int, age_range.split("-"))
        return min_age <= child_age <= max_age
    except:
        return True  # If age range parsing fails, include the product

def get_external_activities(scores: Dict[str, str], num_per_category: int = 3) -> Dict[str, List[str]]:
    """
    Get external activity recommendations based on learning profile
    """
    activity_recommendations = {}
    
    for category, score in scores.items():
        if category in EXTERNAL_ACTIVITIES:
            # Get activities for this category
            available_activities = EXTERNAL_ACTIVITIES[category]
            # Randomly select activities to provide variety
            selected_activities = random.sample(
                available_activities, 
                min(num_per_category, len(available_activities))
            )
            activity_recommendations[category] = selected_activities
    
    return activity_recommendations

def get_parent_insights(scores: Dict[str, str], child_name: str, child_age: int) -> Dict[str, str]:
    """
    Generate parent-specific insights based on learning profile
    """
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    
    insights = {
        "learning_style": generate_learning_style_insight(scores, child_name),
        "motivation_tips": generate_motivation_insight(strengths, child_name),
        "growth_support": generate_growth_support_insight(growth_areas, child_name),
        "daily_integration": generate_daily_integration_tips(scores, child_age)
    }
    
    return insights

def generate_learning_style_insight(scores: Dict[str, str], child_name: str) -> str:
    """Generate personalized learning style insight"""
    strengths = [cat for cat, score in scores.items() if score == "High"]
    
    if "Creative Innovation" in strengths and "Communication" in strengths:
        return f"{child_name} is a natural storyteller who learns best through creative expression and imaginative play. They thrive when given opportunities to create their own narratives and share their ideas."
    elif "Critical Thinking" in strengths and "Content" in strengths:
        return f"{child_name} is an analytical learner who enjoys exploring how things work. They learn best through hands-on investigation and asking 'why' questions."
    elif "Collaboration" in strengths and "Communication" in strengths:
        return f"{child_name} is a social learner who benefits from group activities and discussion. They process information best when they can talk through ideas with others."
    else:
        return f"{child_name} has a unique learning style that combines multiple approaches. They benefit from varied learning experiences that engage different skills."

def generate_motivation_insight(strengths: List[str], child_name: str) -> str:
    """Generate motivation tips based on strengths"""
    if "Confidence" in strengths:
        return f"{child_name} is motivated by opportunities to take on challenges and show independence. Encourage them to set their own goals and celebrate their problem-solving process."
    elif "Collaboration" in strengths:
        return f"{child_name} is energized by working with others. They're motivated by team projects, helping friends, and contributing to group success."
    elif "Creative Innovation" in strengths:
        return f"{child_name} is motivated by creative freedom and original thinking. Give them open-ended projects and celebrate their unique approaches to problems."
    else:
        return f"{child_name} is motivated by variety and new experiences. Keep learning fresh by rotating between different types of activities and approaches."

def generate_growth_support_insight(growth_areas: List[str], child_name: str) -> str:
    """Generate growth support suggestions"""
    if not growth_areas:
        return f"{child_name} shows balanced development across all areas. Continue providing diverse learning experiences to maintain this strong foundation."
    
    area = growth_areas[0] if growth_areas else "overall development"
    
    if area == "Confidence":
        return f"To support {child_name}'s confidence, start with small, achievable challenges and celebrate effort over results. Build their sense of capability gradually."
    elif area == "Collaboration":
        return f"Help {child_name} develop collaboration skills through low-pressure group activities and one-on-one partnerships before larger group settings."
    elif area == "Communication":
        return f"Support {child_name}'s communication development through active listening, encouraging questions, and providing rich vocabulary experiences."
    else:
        return f"Support {child_name}'s growth in {area} through patient practice, breaking skills into smaller steps, and connecting to their existing interests."

def generate_daily_integration_tips(scores: Dict[str, str], child_age: int) -> str:
    """Generate tips for integrating learning into daily routines"""
    if child_age <= 5:
        return "Integrate learning through daily routines: count toys during cleanup, practice letters in their name, and have conversations during meals about their favorite parts of the day."
    elif child_age <= 8:
        return "Build learning into everyday activities: cooking together teaches math and following directions, nature walks develop observation skills, and bedtime stories expand vocabulary and imagination."
    else:
        return "Encourage independent learning habits: set up a dedicated learning space, involve them in planning family activities, and connect their interests to learning opportunities in the community."