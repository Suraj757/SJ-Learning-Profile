"""
Conference Intelligence Agent Prototype
Transforms parent-teacher conferences into strategic planning sessions
Part of Begin Learning Profile Strategy
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from utils.questions import QUESTIONS, CATEGORIES
from utils.scoring import calculate_scores, get_personality_label, generate_description

@dataclass
class ConferenceContext:
    child_name: str
    age: str
    grade_level: str
    conference_type: str  # "quarterly", "annual", "concern", "transition"
    previous_conferences: List[Dict] = None
    learning_profile: Dict = None
    parent_concerns: List[str] = None
    teacher_observations: str = ""

@dataclass
class ConferenceOutcome:
    action_items: List[Dict[str, str]]
    next_conference_date: str
    profile_updates: Dict
    recommended_activities: List[Dict]
    follow_up_needed: List[str]

class ConferenceIntelligenceAgent:
    def __init__(self):
        self.conversation_templates = self._load_conversation_templates()
        self.milestone_frameworks = self._load_milestone_frameworks()
    
    def _load_conversation_templates(self) -> Dict[str, Dict]:
        """Load age-appropriate conversation templates"""
        return {
            "prek": {
                "focus_areas": ["Social-emotional development", "Communication skills", "Physical development", "Independence"],
                "key_questions": [
                    "How does [child] interact with peers during play?",
                    "What activities does [child] gravitate toward?",
                    "How does [child] handle transitions and new situations?",
                    "What motivates [child] to try new things?"
                ],
                "parent_concerns": ["Separation anxiety", "Potty training", "Sharing/cooperation", "Following directions"],
                "discussion_structure": [
                    "Celebrate Growth Moments",
                    "Discuss Current Interests & Motivations", 
                    "Address Any Concerns Together",
                    "Plan Home-School Coordination",
                    "Set Goals for Next Quarter"
                ]
            },
            "k2": {
                "focus_areas": ["Academic readiness", "Social skills", "Self-regulation", "Learning preferences"],
                "key_questions": [
                    "How does [child] approach learning challenges?",
                    "What subjects or activities energize [child]?",
                    "How does [child] work in group settings?",
                    "What support does [child] need to stay focused?"
                ],
                "parent_concerns": ["Reading readiness", "Math concepts", "Attention span", "Peer relationships"],
                "discussion_structure": [
                    "Review Academic Progress & Learning Style",
                    "Celebrate Strengths & Interests",
                    "Address Learning Challenges Together",
                    "Align Home & School Strategies",
                    "Plan Enrichment & Support"
                ]
            },
            "35": {
                "focus_areas": ["Academic achievement", "Critical thinking", "Independence", "Leadership potential"],
                "key_questions": [
                    "How does [child] tackle complex problems?",
                    "What subjects spark [child]'s curiosity?",
                    "How does [child] collaborate and lead with peers?",
                    "What goals is [child] setting for themselves?"
                ],
                "parent_concerns": ["Academic performance", "Homework habits", "Social dynamics", "Future preparation"],
                "discussion_structure": [
                    "Review Academic Performance & Growth",
                    "Explore Interests & Passion Projects",
                    "Discuss Character Development",
                    "Plan Advanced Opportunities",
                    "Prepare for Next Grade Transition"
                ]
            }
        }
    
    def _load_milestone_frameworks(self) -> Dict[str, Dict]:
        """Load developmental milestone frameworks by age"""
        return {
            "prek": {
                "social_emotional": [
                    "Separates from parents without distress",
                    "Plays cooperatively with others", 
                    "Expresses emotions appropriately",
                    "Shows empathy for others"
                ],
                "cognitive": [
                    "Follows 2-3 step directions",
                    "Asks questions to learn",
                    "Shows curiosity about world",
                    "Remembers and retells events"
                ],
                "physical": [
                    "Uses bathroom independently",
                    "Dresses self with minimal help",
                    "Uses utensils and writing tools",
                    "Runs, jumps, climbs safely"
                ]
            },
            "k2": {
                "academic": [
                    "Recognizes letters and sounds",
                    "Counts and recognizes numbers 1-20",
                    "Follows classroom routines",
                    "Sits and attends for 15-20 minutes"
                ],
                "social": [
                    "Takes turns and shares materials",
                    "Resolves simple conflicts with words",
                    "Includes others in play",
                    "Follows classroom rules"
                ],
                "independence": [
                    "Manages personal belongings",
                    "Asks for help when needed",
                    "Completes tasks with minimal support",
                    "Makes appropriate choices"
                ]
            },
            "35": {
                "academic": [
                    "Reads at grade level with comprehension",
                    "Solves multi-step math problems",
                    "Writes organized paragraphs",
                    "Conducts simple research"
                ],
                "leadership": [
                    "Takes initiative in group projects",
                    "Helps and mentors younger students",
                    "Advocates for self and others",
                    "Shows responsibility for actions"
                ],
                "critical_thinking": [
                    "Analyzes problems from multiple angles",
                    "Makes connections across subjects",
                    "Questions assumptions respectfully",
                    "Proposes creative solutions"
                ]
            }
        }
    
    def prepare_conference(self, context: ConferenceContext) -> Dict[str, any]:
        """Generate pre-conference preparation materials"""
        age_group = self._determine_age_group(context.age, context.grade_level)
        template = self.conversation_templates[age_group]
        milestones = self.milestone_frameworks[age_group]
        
        # Generate personalized talking points
        talking_points = self._generate_talking_points(context, template)
        
        # Create milestone checklist
        milestone_checklist = self._create_milestone_checklist(context, milestones)
        
        # Suggest questions based on learning profile
        suggested_questions = self._generate_profile_based_questions(context, template)
        
        # Prepare discussion structure
        discussion_agenda = self._create_discussion_agenda(context, template)
        
        return {
            "conference_type": context.conference_type,
            "child_name": context.child_name,
            "age_group": age_group,
            "preparation_materials": {
                "talking_points": talking_points,
                "milestone_checklist": milestone_checklist,
                "suggested_questions": suggested_questions,
                "discussion_agenda": discussion_agenda,
                "previous_action_items": self._review_previous_actions(context)
            },
            "estimated_duration": "30-45 minutes",
            "materials_needed": ["Learning profile", "Recent work samples", "Assessment data"]
        }
    
    def facilitate_conference(self, context: ConferenceContext, live_notes: str) -> Dict[str, any]:
        """Real-time conference facilitation and note-taking"""
        
        # Extract key insights from live notes
        insights = self._extract_conference_insights(live_notes, context)
        
        # Generate real-time suggestions
        suggestions = self._generate_realtime_suggestions(insights, context)
        
        # Track discussion coverage
        coverage = self._assess_discussion_coverage(live_notes, context)
        
        return {
            "live_insights": insights,
            "suggested_followups": suggestions,
            "discussion_coverage": coverage,
            "time_management": self._assess_time_allocation(live_notes),
            "action_item_candidates": self._identify_action_items(live_notes)
        }
    
    def generate_conference_summary(self, context: ConferenceContext, conference_notes: str) -> ConferenceOutcome:
        """Generate comprehensive conference summary and action plan"""
        
        # Extract key themes and decisions
        key_themes = self._extract_key_themes(conference_notes)
        
        # Generate specific action items
        action_items = self._generate_action_items(conference_notes, context)
        
        # Update learning profile based on insights
        profile_updates = self._generate_profile_updates(conference_notes, context)
        
        # Recommend specific activities
        recommended_activities = self._recommend_activities(profile_updates, context)
        
        # Identify follow-up needs
        follow_up_needed = self._identify_followup_needs(conference_notes, context)
        
        # Schedule next conference
        next_conference = self._suggest_next_conference_date(context, action_items)
        
        return ConferenceOutcome(
            action_items=action_items,
            next_conference_date=next_conference,
            profile_updates=profile_updates,
            recommended_activities=recommended_activities,
            follow_up_needed=follow_up_needed
        )
    
    def _determine_age_group(self, age: str, grade: str) -> str:
        """Determine appropriate template group"""
        if "prek" in grade.lower() or "pre-k" in grade.lower():
            return "prek"
        elif grade.lower() in ["k", "kindergarten", "1st", "2nd", "first", "second"]:
            return "k2"
        else:
            return "35"
    
    def _generate_talking_points(self, context: ConferenceContext, template: Dict) -> List[str]:
        """Generate personalized talking points"""
        talking_points = []
        
        # Add profile-specific strengths
        if context.learning_profile:
            profile = context.learning_profile
            strengths = [cat for cat, score in profile.items() if score == "High"]
            if strengths:
                talking_points.append(f"Celebrate {context.child_name}'s strengths in {', '.join(strengths)}")
        
        # Add teacher observations
        if context.teacher_observations:
            talking_points.append(f"Discuss recent observations: {context.teacher_observations[:100]}...")
        
        # Add parent concerns
        if context.parent_concerns:
            for concern in context.parent_concerns:
                talking_points.append(f"Address parent concern: {concern}")
        
        # Add template-based points
        for area in template["focus_areas"]:
            talking_points.append(f"Review progress in {area}")
        
        return talking_points
    
    def _create_milestone_checklist(self, context: ConferenceContext, milestones: Dict) -> Dict[str, List[Dict]]:
        """Create interactive milestone checklist"""
        checklist = {}
        for category, items in milestones.items():
            checklist[category] = [
                {"milestone": item, "status": "to_discuss", "notes": ""} 
                for item in items
            ]
        return checklist
    
    def _generate_profile_based_questions(self, context: ConferenceContext, template: Dict) -> List[str]:
        """Generate questions based on child's learning profile"""
        questions = []
        
        # Start with template questions
        for q in template["key_questions"]:
            questions.append(q.replace("[child]", context.child_name))
        
        # Add profile-specific questions
        if context.learning_profile:
            profile = context.learning_profile
            
            # Questions for high areas (celebration)
            high_areas = [cat for cat, score in profile.items() if score == "High"]
            for area in high_areas:
                if area == "Communication":
                    questions.append(f"How can we further develop {context.child_name}'s excellent communication skills?")
                elif area == "Creative Innovation":
                    questions.append(f"What creative projects might challenge {context.child_name}?")
            
            # Questions for growth areas (development)
            low_areas = [cat for cat, score in profile.items() if score == "Low"]
            for area in low_areas:
                if area == "Collaboration":
                    questions.append(f"What strategies can help {context.child_name} with collaborative activities?")
                elif area == "Confidence":
                    questions.append(f"How can we build {context.child_name}'s confidence in new situations?")
        
        return questions
    
    def _create_discussion_agenda(self, context: ConferenceContext, template: Dict) -> List[Dict]:
        """Create time-boxed discussion agenda"""
        agenda = []
        structure = template["discussion_structure"]
        
        total_time = 40  # minutes
        time_per_section = total_time // len(structure)
        
        for i, section in enumerate(structure):
            agenda.append({
                "section": section,
                "duration_minutes": time_per_section,
                "key_points": [],
                "questions_to_ask": [],
                "outcomes_needed": []
            })
        
        return agenda
    
    def _extract_conference_insights(self, notes: str, context: ConferenceContext) -> List[Dict]:
        """Extract key insights from live conference notes"""
        insights = []
        
        # Simple keyword-based insight extraction (would be AI-powered in production)
        if "strength" in notes.lower():
            insights.append({"type": "strength", "content": "Strength identified in discussion"})
        if "concern" in notes.lower() or "challenge" in notes.lower():
            insights.append({"type": "concern", "content": "Area of concern discussed"})
        if "goal" in notes.lower() or "plan" in notes.lower():
            insights.append({"type": "action", "content": "Action item or goal mentioned"})
        
        return insights
    
    def _generate_action_items(self, notes: str, context: ConferenceContext) -> List[Dict[str, str]]:
        """Generate specific, actionable items from conference"""
        action_items = []
        
        # Template action items based on common conference outcomes
        action_items.extend([
            {
                "owner": "teacher",
                "action": f"Continue monitoring {context.child_name}'s progress in identified growth areas",
                "deadline": "ongoing",
                "success_metric": "Weekly observation notes"
            },
            {
                "owner": "parent", 
                "action": "Implement recommended home activities for 15 minutes daily",
                "deadline": "next 4 weeks",
                "success_metric": "Activity completion log"
            },
            {
                "owner": "both",
                "action": "Schedule follow-up check-in to review progress",
                "deadline": "4 weeks",
                "success_metric": "Meeting scheduled and completed"
            }
        ])
        
        return action_items
    
    def _generate_profile_updates(self, notes: str, context: ConferenceContext) -> Dict:
        """Generate updates to child's learning profile"""
        updates = {
            "conference_date": datetime.now().isoformat(),
            "conference_type": context.conference_type,
            "key_insights": [],
            "updated_strengths": [],
            "updated_growth_areas": [],
            "motivational_triggers": [],
            "learning_preferences": []
        }
        
        # Extract insights from notes (simplified for demo)
        if "loves" in notes.lower():
            updates["motivational_triggers"].append("Shows enthusiasm for discussed activities")
        if "struggles" in notes.lower():
            updates["updated_growth_areas"].append("Area needing additional support identified")
        
        return updates
    
    def _recommend_activities(self, profile_updates: Dict, context: ConferenceContext) -> List[Dict]:
        """Recommend specific activities based on conference insights"""
        activities = []
        
        # Begin product recommendations based on profile
        if context.learning_profile:
            profile = context.learning_profile
            
            if profile.get("Creative Innovation") == "High":
                activities.append({
                    "product": "codeSpark",
                    "activity": "Creative coding challenges", 
                    "duration": "15-20 minutes",
                    "frequency": "3x per week",
                    "rationale": "Builds on creative innovation strength"
                })
            
            if profile.get("Content") in ["Medium", "Low"]:
                activities.append({
                    "product": "HOMER",
                    "activity": "Personalized reading pathway",
                    "duration": "15 minutes", 
                    "frequency": "daily",
                    "rationale": "Supports content knowledge development"
                })
        
        return activities
    
    def _identify_followup_needs(self, notes: str, context: ConferenceContext) -> List[str]:
        """Identify what follow-up is needed"""
        followup = []
        
        if "assessment" in notes.lower():
            followup.append("Schedule additional assessment")
        if "specialist" in notes.lower():
            followup.append("Consider specialist consultation")
        if "support" in notes.lower():
            followup.append("Explore additional support services")
        
        return followup
    
    def _suggest_next_conference_date(self, context: ConferenceContext, action_items: List[Dict]) -> str:
        """Suggest optimal next conference timing"""
        if context.conference_type == "concern":
            return "4 weeks (follow-up on concerns)"
        elif context.conference_type == "quarterly":
            return "12 weeks (next quarterly check-in)"
        else:
            return "8 weeks (standard follow-up)"
    
    def _review_previous_actions(self, context: ConferenceContext) -> List[Dict]:
        """Review outcomes from previous conferences"""
        if not context.previous_conferences:
            return []
        
        # Would analyze previous action items and outcomes
        return [{"item": "Review progress on previous goals", "status": "to_discuss"}]
    
    def _generate_realtime_suggestions(self, insights: List[Dict], context: ConferenceContext) -> List[str]:
        """Generate real-time suggestions during conference"""
        suggestions = []
        
        concern_count = sum(1 for i in insights if i["type"] == "concern")
        if concern_count > 2:
            suggestions.append("Consider scheduling follow-up conference to address multiple concerns")
        
        return suggestions
    
    def _assess_discussion_coverage(self, notes: str, context: ConferenceContext) -> Dict[str, bool]:
        """Assess whether key topics were covered"""
        age_group = self._determine_age_group(context.age, context.grade_level)
        template = self.conversation_templates[age_group]
        
        coverage = {}
        for area in template["focus_areas"]:
            coverage[area] = area.lower() in notes.lower()
        
        return coverage
    
    def _assess_time_allocation(self, notes: str) -> Dict[str, str]:
        """Assess how time was spent in conference"""
        return {
            "total_duration": "estimated from note length",
            "balance": "good coverage of topics" if len(notes) > 200 else "may need more discussion time"
        }
    
    def _identify_action_items(self, notes: str) -> List[str]:
        """Identify potential action items from live notes"""
        action_candidates = []
        
        if "will" in notes.lower():
            action_candidates.append("Commitment identified - create action item")
        if "should" in notes.lower() or "need to" in notes.lower():
            action_candidates.append("Need identified - create action item")
        
        return action_candidates
    
    def _extract_key_themes(self, notes: str) -> List[str]:
        """Extract major themes from conference"""
        themes = []
        
        # Simple theme extraction (would use NLP in production)
        if len(notes) > 100:
            themes.append("Comprehensive discussion of child's development")
        if "strength" in notes.lower():
            themes.append("Celebration of child's strengths")
        if "goal" in notes.lower():
            themes.append("Goal setting and planning")
        
        return themes

def demo_conference_intelligence():
    """Demo the Conference Intelligence Agent"""
    print("🎯 Conference Intelligence Agent Demo")
    print("=" * 60)
    
    # Sample conference context
    context = ConferenceContext(
        child_name="Emma",
        age="5",
        grade_level="PreK",
        conference_type="quarterly",
        learning_profile={
            "Communication": "High",
            "Collaboration": "Medium", 
            "Content": "Medium",
            "Critical Thinking": "High",
            "Creative Innovation": "High",
            "Confidence": "Medium"
        },
        parent_concerns=["Wants help with reading readiness", "Social skills with new friends"],
        teacher_observations="Emma shows exceptional creativity and asks thoughtful questions. Sometimes hesitant in large group activities."
    )
    
    agent = ConferenceIntelligenceAgent()
    
    # Demo conference preparation
    print("\n📋 PRE-CONFERENCE PREPARATION")
    print("-" * 40)
    
    prep = agent.prepare_conference(context)
    print(f"Conference Type: {prep['conference_type']}")
    print(f"Child: {prep['child_name']} (Age Group: {prep['age_group']})")
    print(f"Estimated Duration: {prep['estimated_duration']}")
    
    print("\n🎯 Key Talking Points:")
    for point in prep['preparation_materials']['talking_points'][:3]:
        print(f"  • {point}")
    
    print("\n❓ Suggested Questions:")
    for question in prep['preparation_materials']['suggested_questions'][:3]:
        print(f"  • {question}")
    
    # Demo conference summary
    print("\n📝 POST-CONFERENCE SUMMARY")
    print("-" * 40)
    
    sample_notes = """
    Emma's creativity really shone through when we discussed her art projects. 
    She's been creating elaborate stories to go with her drawings. Parents mentioned 
    she's been asking lots of questions about letters and wants to write her own books.
    
    She's still a bit shy in large group settings but does well in small groups. 
    We agreed to work on building her confidence during class presentations.
    Teacher will provide more opportunities for Emma to share her creative work.
    Parents will continue reading together daily and let Emma 'read' by telling 
    stories from pictures.
    """
    
    outcome = agent.generate_conference_summary(context, sample_notes)
    
    print("📋 Action Items:")
    for item in outcome.action_items[:2]:
        print(f"  • {item['owner'].title()}: {item['action']}")
        print(f"    Deadline: {item['deadline']} | Success Metric: {item['success_metric']}")
    
    print(f"\n📅 Next Conference: {outcome.next_conference_date}")
    
    print("\n🎯 Recommended Begin Products:")
    for activity in outcome.recommended_activities:
        print(f"  • {activity['product']}: {activity['activity']}")
        print(f"    {activity['frequency']} for {activity['duration']}")
        print(f"    Rationale: {activity['rationale']}")

if __name__ == "__main__":
    demo_conference_intelligence()