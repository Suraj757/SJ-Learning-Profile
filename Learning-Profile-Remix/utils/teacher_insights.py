"""
Teacher-Specific Insights and Classroom Strategies
Provides classroom-focused recommendations based on learning profiles
"""

from typing import Dict, List, Any

CLASSROOM_STRATEGIES = {
    "Communication": {
        "high": {
            "strategies": [
                "Provide opportunities for verbal presentations and storytelling",
                "Use think-pair-share activities to leverage discussion skills",
                "Assign peer tutoring or explanation roles",
                "Include dramatic play and role-playing activities"
            ],
            "classroom_tips": [
                "This student thrives when they can verbally process information",
                "Give them time to explain their thinking out loud",
                "Use them as a classroom helper to explain concepts to peers",
                "Provide multiple opportunities for oral participation"
            ],
            "differentiation": [
                "Offer choice between written or oral responses",
                "Use audio recording tools for assignments",
                "Incorporate group discussions before independent work",
                "Provide sentence starters and discussion frameworks"
            ]
        },
        "medium": {
            "strategies": [
                "Gradually increase speaking opportunities with support",
                "Use partner work before whole-class sharing",
                "Provide visual aids and prompts for communication",
                "Practice active listening skills through structured activities"
            ],
            "classroom_tips": [
                "This student needs scaffolding to build communication confidence",
                "Start with low-pressure sharing opportunities",
                "Use visual supports to aid verbal expression",
                "Celebrate attempts at communication, not just accuracy"
            ],
            "differentiation": [
                "Provide communication sentence frames",
                "Use picture cards or visual prompts",
                "Allow processing time before expecting responses",
                "Create safe spaces for practice with trusted peers"
            ]
        },
        "low": {
            "strategies": [
                "Start with non-verbal communication methods",
                "Use drawing, gestures, or movement to express ideas",
                "Build confidence through one-on-one interactions",
                "Incorporate art and creative expression as communication tools"
            ],
            "classroom_tips": [
                "This student may prefer alternative ways to communicate",
                "Don't force verbal participation - honor diverse communication styles",
                "Look for non-verbal signs of understanding and engagement",
                "Build trust through individual connections before group activities"
            ],
            "differentiation": [
                "Accept drawings, charts, or models as valid responses",
                "Use technology tools for alternative communication",
                "Provide extra wait time for verbal responses",
                "Create opportunities for success in non-verbal activities first"
            ]
        }
    },
    "Collaboration": {
        "high": {
            "strategies": [
                "Assign group project leadership roles",
                "Use cooperative learning structures regularly",
                "Create peer mentoring opportunities",
                "Implement collaborative problem-solving activities"
            ],
            "classroom_tips": [
                "This student energizes and excels in group settings",
                "Use their collaborative skills to support classroom community",
                "They can help shy students feel included in activities",
                "Balance group work with some independent challenges"
            ],
            "differentiation": [
                "Provide complex group projects with multiple roles",
                "Allow them to facilitate small group discussions",
                "Create mixed-ability groups where they can support others",
                "Teach conflict resolution and group management skills"
            ]
        },
        "medium": {
            "strategies": [
                "Provide structured group work with clear roles",
                "Practice collaboration skills through guided activities",
                "Use partner work before larger group activities",
                "Teach specific social and teamwork skills"
            ],
            "classroom_tips": [
                "This student benefits from explicit collaboration instruction",
                "Provide clear expectations and procedures for group work",
                "Mix collaborative activities with individual work",
                "Model and practice turn-taking and active listening"
            ],
            "differentiation": [
                "Assign specific roles within group work",
                "Provide collaboration rubrics and checklists",
                "Use structured protocols for group discussions",
                "Allow choice between individual and group options when possible"
            ]
        },
        "low": {
            "strategies": [
                "Start with parallel work before true collaboration",
                "Use one-on-one partnerships before group work",
                "Provide individual space and choice when possible",
                "Build social skills through structured, low-pressure activities"
            ],
            "classroom_tips": [
                "This student may find group work overwhelming or draining",
                "Respect their need for individual work space and time",
                "Gradually introduce collaborative elements with support",
                "Don't mistake preference for individual work as lack of ability"
            ],
            "differentiation": [
                "Offer individual alternatives to group projects",
                "Provide quiet spaces for independent work",
                "Use structured turn-taking to manage group interactions",
                "Build confidence through successful individual achievements first"
            ]
        }
    },
    "Content": {
        "high": {
            "strategies": [
                "Provide enrichment and extension activities",
                "Use this student as a peer resource for content questions",
                "Offer independent research projects",
                "Connect new learning to their existing knowledge base"
            ],
            "classroom_tips": [
                "This student absorbs and retains information quickly",
                "They may need additional challenges to stay engaged",
                "Use their knowledge to support other students' learning",
                "Provide depth rather than just breadth in content coverage"
            ],
            "differentiation": [
                "Offer advanced materials and resources",
                "Allow them to explore topics of interest independently",
                "Use their expertise in peer teaching opportunities",
                "Provide choice in how they demonstrate knowledge"
            ]
        },
        "medium": {
            "strategies": [
                "Use multiple modalities to present content",
                "Provide graphic organizers and visual aids",
                "Connect new information to familiar concepts",
                "Use repetition and practice in engaging ways"
            ],
            "classroom_tips": [
                "This student learns content well with appropriate support",
                "Break complex information into manageable chunks",
                "Use concrete examples and hands-on experiences",
                "Provide multiple opportunities to practice and apply learning"
            ],
            "differentiation": [
                "Offer content in multiple formats (visual, auditory, kinesthetic)",
                "Use scaffolding tools like graphic organizers",
                "Provide just-right level materials",
                "Allow extra time for processing and understanding"
            ]
        },
        "low": {
            "strategies": [
                "Focus on foundational concepts and skills",
                "Use concrete, hands-on approaches to abstract concepts",
                "Provide intensive support and repetition",
                "Break learning into very small, achievable steps"
            ],
            "classroom_tips": [
                "This student needs explicit, systematic content instruction",
                "Celebrate small wins and incremental progress",
                "Use multi-sensory approaches to support understanding",
                "Don't assume prior knowledge - build from the ground up"
            ],
            "differentiation": [
                "Provide intensive, small-group instruction",
                "Use manipulatives and concrete materials",
                "Offer modified assignments that focus on key concepts",
                "Allow alternative ways to demonstrate understanding"
            ]
        }
    },
    "Critical Thinking": {
        "high": {
            "strategies": [
                "Provide open-ended problems and investigations",
                "Use Socratic questioning to deepen thinking",
                "Offer choice in problem-solving approaches",
                "Create opportunities for analysis and evaluation"
            ],
            "classroom_tips": [
                "This student thrives on intellectual challenges",
                "They enjoy analyzing 'why' and 'how' questions",
                "Use their thinking skills to benefit the whole class",
                "Provide complex, multi-step problems to solve"
            ],
            "differentiation": [
                "Offer advanced problem-solving opportunities",
                "Allow them to create their own investigation questions",
                "Use them as thinking partners for other students",
                "Provide choice in how they approach and solve problems"
            ]
        },
        "medium": {
            "strategies": [
                "Provide structured thinking routines and frameworks",
                "Use graphic organizers for analysis activities",
                "Model thinking processes explicitly",
                "Gradually increase complexity of problems"
            ],
            "classroom_tips": [
                "This student benefits from explicit thinking instruction",
                "Provide scaffolding for complex reasoning tasks",
                "Make thinking processes visible through modeling",
                "Give them time to process before expecting responses"
            ],
            "differentiation": [
                "Use thinking maps and organizational tools",
                "Provide step-by-step problem-solving guides",
                "Offer multiple examples before independent practice",
                "Allow collaboration during complex thinking tasks"
            ]
        },
        "low": {
            "strategies": [
                "Start with concrete, familiar problems",
                "Provide extensive modeling and guided practice",
                "Use hands-on materials to support abstract thinking",
                "Break complex problems into smaller parts"
            ],
            "classroom_tips": [
                "This student needs concrete supports for abstract thinking",
                "Start with what they know and build gradually",
                "Use manipulatives and visual supports",
                "Celebrate logical thinking, even in simple contexts"
            ],
            "differentiation": [
                "Provide concrete materials for abstract concepts",
                "Use simple, familiar contexts for problem-solving",
                "Offer extensive guided practice before independence",
                "Focus on one thinking skill at a time"
            ]
        }
    },
    "Creative Innovation": {
        "high": {
            "strategies": [
                "Provide open-ended creative projects",
                "Allow multiple solutions to problems",
                "Use brainstorming and idea generation activities",
                "Incorporate arts integration across subjects"
            ],
            "classroom_tips": [
                "This student generates original ideas and solutions",
                "They may approach tasks in unexpected ways",
                "Value process over product in creative work",
                "Use their creativity to inspire other students"
            ],
            "differentiation": [
                "Offer choice in creative expression methods",
                "Allow them to design their own projects",
                "Provide time for exploration and experimentation",
                "Use their creative work as inspiration for others"
            ]
        },
        "medium": {
            "strategies": [
                "Provide structured creative activities",
                "Offer choice within parameters",
                "Use creative warm-ups and brain breaks",
                "Model creative thinking processes"
            ],
            "classroom_tips": [
                "This student shows creative potential with support",
                "Provide structure to help channel creative energy",
                "Celebrate unique approaches and ideas",
                "Build creative confidence through successful experiences"
            ],
            "differentiation": [
                "Provide creative frameworks and templates",
                "Offer choice in materials and methods",
                "Use guided creative activities before open-ended ones",
                "Celebrate effort and originality over technical perfection"
            ]
        },
        "low": {
            "strategies": [
                "Start with structured creative activities",
                "Provide examples and models for inspiration",
                "Focus on personal expression over originality",
                "Use familiar materials and contexts"
            ],
            "classroom_tips": [
                "This student may need permission to be creative",
                "Start with low-risk creative opportunities",
                "Focus on personal meaning over innovation",
                "Build creative confidence gradually"
            ],
            "differentiation": [
                "Provide step-by-step creative activities",
                "Use familiar contexts for creative expression",
                "Offer multiple examples and inspiration",
                "Focus on personal connection rather than originality"
            ]
        }
    },
    "Confidence": {
        "high": {
            "strategies": [
                "Provide leadership opportunities",
                "Use their confidence to support other students",
                "Offer challenging tasks that match their self-belief",
                "Channel confidence into positive classroom contributions"
            ],
            "classroom_tips": [
                "This student believes in their abilities and takes on challenges",
                "They can be a positive influence on hesitant classmates",
                "Help them balance confidence with humility",
                "Use their willingness to try as a classroom asset"
            ],
            "differentiation": [
                "Provide advanced challenges that match their confidence",
                "Allow them to model risk-taking for other students",
                "Use their confidence in peer support roles",
                "Help them develop realistic self-assessment skills"
            ]
        },
        "medium": {
            "strategies": [
                "Build on successful experiences",
                "Provide encouragement and specific feedback",
                "Create safe spaces for risk-taking",
                "Gradually increase challenge levels"
            ],
            "classroom_tips": [
                "This student's confidence grows with success and support",
                "Provide specific, constructive feedback",
                "Create opportunities for them to shine",
                "Balance challenge with achievable goals"
            ],
            "differentiation": [
                "Provide scaffolding for challenging tasks",
                "Celebrate effort and improvement over perfection",
                "Offer choices to build sense of control",
                "Use peer partnerships for support"
            ]
        },
        "low": {
            "strategies": [
                "Start with guaranteed success experiences",
                "Provide extensive encouragement and support",
                "Focus on effort and growth over outcomes",
                "Create a safe, non-judgmental environment"
            ],
            "classroom_tips": [
                "This student needs confidence-building experiences",
                "Avoid putting them on the spot unexpectedly",
                "Celebrate small wins and incremental progress",
                "Create predictable, safe learning environments"
            ],
            "differentiation": [
                "Provide tasks slightly below current ability level initially",
                "Use private feedback rather than public correction",
                "Allow choice in when and how to participate",
                "Focus on personal growth rather than comparison to others"
            ]
        }
    }
}

def get_teacher_insights(scores: Dict[str, str], child_name: str, child_age: int) -> Dict[str, Any]:
    """Generate teacher-specific insights for classroom use"""
    
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    developing_areas = [cat for cat, score in scores.items() if score == "Medium"]
    
    # Generate classroom behavior summary
    behavior_summary = generate_classroom_behavior_summary(scores, child_name)
    
    # Get specific strategies for each area
    teaching_strategies = {}
    for category, level in scores.items():
        level_key = level.lower()
        if category in CLASSROOM_STRATEGIES and level_key in CLASSROOM_STRATEGIES[category]:
            teaching_strategies[category] = CLASSROOM_STRATEGIES[category][level_key]
    
    # Generate differentiation recommendations
    differentiation_plan = generate_differentiation_plan(strengths, growth_areas, child_age)
    
    # Create parent communication talking points
    parent_talking_points = generate_parent_talking_points(scores, child_name)
    
    return {
        "behavior_summary": behavior_summary,
        "teaching_strategies": teaching_strategies,
        "differentiation_plan": differentiation_plan,
        "parent_talking_points": parent_talking_points,
        "classroom_focus": generate_classroom_focus_areas(strengths, growth_areas),
        "seating_suggestions": generate_seating_suggestions(scores),
        "assessment_adaptations": generate_assessment_adaptations(scores)
    }

def generate_classroom_behavior_summary(scores: Dict[str, str], child_name: str) -> str:
    """Generate a summary of expected classroom behaviors"""
    
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    
    summary_parts = []
    
    if "Communication" in strengths:
        summary_parts.append(f"{child_name} is likely to be verbally expressive and enjoy sharing ideas in class discussions")
    
    if "Collaboration" in strengths:
        summary_parts.append("thrives in group work and can help facilitate peer interactions")
    
    if "Critical Thinking" in strengths:
        summary_parts.append("asks thoughtful questions and enjoys problem-solving challenges")
    
    if "Creative Innovation" in strengths:
        summary_parts.append("approaches tasks with original thinking and creative solutions")
    
    if "Confidence" in strengths:
        summary_parts.append("shows willingness to take on challenges and share their work")
    
    if "Content" in strengths:
        summary_parts.append("demonstrates strong knowledge retention and academic curiosity")
    
    # Add growth area considerations
    if "Collaboration" in growth_areas:
        summary_parts.append("may prefer individual work and need support in group settings")
    
    if "Confidence" in growth_areas:
        summary_parts.append("may need encouragement and confidence-building opportunities")
    
    if "Communication" in growth_areas:
        summary_parts.append("may benefit from alternative ways to express ideas beyond verbal communication")
    
    if len(summary_parts) == 0:
        return f"{child_name} shows balanced development across learning areas and will benefit from varied instructional approaches."
    
    if len(summary_parts) == 1:
        return f"{child_name} {summary_parts[0]}."
    else:
        return f"{child_name} {', '.join(summary_parts[:-1])}, and {summary_parts[-1]}."

def generate_differentiation_plan(strengths: List[str], growth_areas: List[str], age: int) -> Dict[str, List[str]]:
    """Generate specific differentiation strategies"""
    
    plan = {
        "leverage_strengths": [],
        "support_growth": [],
        "instructional_strategies": []
    }
    
    # Leverage strengths
    if "Communication" in strengths:
        plan["leverage_strengths"].append("Use verbal processing and discussion as learning tools")
        plan["leverage_strengths"].append("Provide opportunities for peer teaching and explanation")
    
    if "Collaboration" in strengths:
        plan["leverage_strengths"].append("Assign group leadership roles and cooperative projects")
        plan["leverage_strengths"].append("Use their social skills to support classroom community")
    
    if "Critical Thinking" in strengths:
        plan["leverage_strengths"].append("Provide complex, open-ended problems to solve")
        plan["leverage_strengths"].append("Use Socratic questioning to deepen their analysis")
    
    # Support growth areas
    if "Confidence" in growth_areas:
        plan["support_growth"].append("Start with tasks slightly below ability level to build success")
        plan["support_growth"].append("Provide private feedback and avoid unexpected public participation")
    
    if "Communication" in growth_areas:
        plan["support_growth"].append("Accept non-verbal responses and alternative communication methods")
        plan["support_growth"].append("Provide wait time and visual supports for verbal expression")
    
    if "Collaboration" in growth_areas:
        plan["support_growth"].append("Start with partner work before group activities")
        plan["support_growth"].append("Provide individual alternatives when needed")
    
    # Age-appropriate strategies
    if age <= 6:
        plan["instructional_strategies"].append("Use hands-on materials and concrete examples")
        plan["instructional_strategies"].append("Keep activities short and include movement breaks")
    elif age <= 8:
        plan["instructional_strategies"].append("Balance structured and open-ended activities")
        plan["instructional_strategies"].append("Incorporate choice and student interests")
    else:
        plan["instructional_strategies"].append("Provide opportunities for independent learning")
        plan["instructional_strategies"].append("Use project-based and inquiry learning approaches")
    
    return plan

def generate_parent_talking_points(scores: Dict[str, str], child_name: str) -> List[str]:
    """Generate talking points for parent communication"""
    
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    
    talking_points = []
    
    # Positive strengths to share
    if strengths:
        strength_descriptions = {
            "Communication": "excellent verbal expression and listening skills",
            "Collaboration": "natural ability to work well with others",
            "Content": "strong knowledge retention and academic curiosity", 
            "Critical Thinking": "thoughtful problem-solving and analytical skills",
            "Creative Innovation": "original thinking and creative approaches to tasks",
            "Confidence": "willingness to take on challenges and share ideas"
        }
        
        strength_list = [strength_descriptions.get(s, s) for s in strengths[:2]]
        talking_points.append(f"{child_name} shows particular strength in {' and '.join(strength_list)}")
    
    # Growth opportunities
    if growth_areas:
        talking_points.append(f"Areas where {child_name} would benefit from continued support include {' and '.join(growth_areas[:2])}")
        talking_points.append("These are normal developmental areas that we can work on together")
    
    # Home-school collaboration
    talking_points.append(f"I'd love to hear about what you're seeing at home with {child_name}'s learning")
    talking_points.append("Let's work together to support their growth in both classroom and home settings")
    
    return talking_points

def generate_classroom_focus_areas(strengths: List[str], growth_areas: List[str]) -> Dict[str, str]:
    """Generate immediate classroom focus recommendations"""
    
    focus = {}
    
    if growth_areas:
        primary_growth = growth_areas[0]
        focus["primary_support_needed"] = f"Building {primary_growth.lower()} through scaffolded activities and encouragement"
    
    if strengths:
        primary_strength = strengths[0]
        focus["leverage_opportunity"] = f"Use {primary_strength.lower()} as a pathway to support other learning areas"
    
    focus["weekly_goal"] = "Observe and document specific examples of learning preferences in action"
    
    return focus

def generate_seating_suggestions(scores: Dict[str, str]) -> List[str]:
    """Generate classroom seating and environment suggestions"""
    
    suggestions = []
    
    if scores.get("Collaboration") == "High":
        suggestions.append("Place near students who might benefit from peer support")
        suggestions.append("Consider for group table or collaborative seating arrangement")
    elif scores.get("Collaboration") == "Low":
        suggestions.append("Provide individual workspace with option to join groups")
        suggestions.append("Consider quieter area of classroom away from high-traffic zones")
    
    if scores.get("Confidence") == "Low":
        suggestions.append("Seat near teacher for easy encouragement and support")
        suggestions.append("Avoid high-visibility locations that might increase anxiety")
    
    if scores.get("Communication") == "High":
        suggestions.append("Position where they can easily participate in discussions")
        suggestions.append("Consider as discussion leader or class helper")
    
    if not suggestions:
        suggestions.append("Flexible seating based on activity and daily needs")
    
    return suggestions

def generate_assessment_adaptations(scores: Dict[str, str]) -> List[str]:
    """Generate assessment accommodation suggestions"""
    
    adaptations = []
    
    if scores.get("Communication") == "Low":
        adaptations.append("Allow drawings, charts, or demonstrations instead of verbal responses")
        adaptations.append("Provide extra wait time for verbal questions")
    
    if scores.get("Confidence") == "Low":
        adaptations.append("Use private assessment methods when possible")
        adaptations.append("Focus on effort and growth rather than comparison to peers")
    
    if scores.get("Creative Innovation") == "High":
        adaptations.append("Allow creative expression in assessment responses")
        adaptations.append("Accept alternative methods of showing understanding")
    
    if scores.get("Critical Thinking") == "High":
        adaptations.append("Provide open-ended questions that allow for deeper analysis")
        adaptations.append("Allow them to explain their reasoning process")
    
    if not adaptations:
        adaptations.append("Use variety of assessment methods to capture full picture of learning")
    
    return adaptations