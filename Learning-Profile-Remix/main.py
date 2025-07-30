import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64
from datetime import datetime
import re
import json
import os
import pandas as pd
from utils.questions import QUESTIONS, LIKERT_SCALE, CATEGORIES
from utils.scoring import calculate_scores, generate_description, get_personality_label
from utils.visualization import create_radar_chart
from utils.database import (init_db, save_assessment_result, get_previous_assessments, get_admin_statistics,
                             create_teacher_account, get_teacher_by_email, create_assignment, 
                             get_assignment_by_token, get_teacher_assignments, complete_assignment)
from utils.teacher_insights import get_teacher_insights
from utils.helpers import title_case_name

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Begin Learning - Find Your Child's Learning Language",
    page_icon="📚",
    layout="wide"
)

# Try to initialize database but continue if it fails
try:
    init_db()
except Exception as e:
    st.error(f"Error initializing database: {str(e)}")

# Load custom CSS
css_file_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
with open(css_file_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'child_info' not in st.session_state:
    st.session_state.child_info = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'previous_assessments' not in st.session_state:
    st.session_state.previous_assessments = []
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'login_clicked' not in st.session_state:
    st.session_state.login_clicked = False
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'teacher_user' not in st.session_state:
    st.session_state.teacher_user = None
if 'assignment_token' not in st.session_state:
    st.session_state.assignment_token = None

def get_child_text(text, child_name=None):
    """Replace [name] with proper capitalization."""
    if not text:
        return text

    # Title case the child's name if provided
    display_name = title_case_name(child_name) if child_name else None

    # Check if [name] appears at the start of the sentence
    if text.startswith("[name]"):
        return text.replace("[name]", display_name if display_name else "Your child")
    else:
        return text.replace("[name]", display_name if display_name else "your child")

def validate_email(email):
    """Validate email format."""
    if not email:  # Empty email is valid (optional)
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def quiz_page():
    # Check if this is from a teacher assignment
    if st.session_state.assignment_token:
        assignment = get_assignment_by_token(st.session_state.assignment_token)
        if assignment:
            st.markdown(f"""
            <div class="assignment-banner">
                <h4>👩‍🏫 Teacher Assignment</h4>
                <p><strong>{assignment['teacher_name']}</strong> from <strong>{assignment['school']}</strong> ({assignment['grade_level']}) has requested this learning profile for <strong>{assignment['child_name']}</strong>.</p>
                <p><small>This assessment will help your child's teacher understand their learning style from Day 1!</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Pre-populate child name if provided in assignment
            if assignment['child_name'] and not st.session_state.child_info.get('name'):
                st.session_state.child_info['name'] = assignment['child_name']
    
    # Get category icons mapping
    category_icons = {
        "Communication": "📣",
        "Collaboration": "🤝",
        "Content": "📚",
        "Critical Thinking": "🧩",
        "Creative Innovation": "💡",
        "Confidence": "🌟"
    }
    
    # Get encouragement messages
    encouragement_messages = [
        "You're doing great!",
        "Keep going!",
        "Wonderful progress!",
        "You're almost there!",
        "Every answer helps us understand your child better!",
        "Fantastic job so far!",
        "You're unlocking valuable insights!",
        "Your responses are building a personalized profile!"
    ]
    
    # Create a more compact layout
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Enhanced title with progress indicator
        st.markdown('<div class="quiz-header">', unsafe_allow_html=True)
        st.title("Begin Profile")
        
        # Show progress only during questions, not during email collection
        if len(st.session_state.responses) < len(QUESTIONS):
            progress = len(st.session_state.responses) / len(QUESTIONS)
            progress_pct = int(progress * 100)
            
            # Show progress bar
            st.progress(progress)
            
            # Show encouragement message that changes based on progress
            encouragement_idx = min(int(progress * len(encouragement_messages)), len(encouragement_messages) - 1)
            st.markdown(f"""
            <div class="progress-info">
                <div class="progress-text">Question {len(st.session_state.responses) + 1} of {len(QUESTIONS)}</div>
                <div class="encouragement">{encouragement_messages[encouragement_idx]}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        child_name = st.session_state.child_info.get("name")
        child_name_display = title_case_name(child_name) if child_name else None

        # Add a more subtle back link if not on first question
        if len(st.session_state.responses) > 0:
            st.markdown('<div class="back-link-container">', unsafe_allow_html=True)
            if st.button("◂ previous", key="back_button", use_container_width=False):
                # Remove the last response
                last_question = max(st.session_state.responses.keys())
                del st.session_state.responses[last_question]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Show current question or email collection
        if len(st.session_state.responses) == len(QUESTIONS):
            # All questions completed, show email collection with enhanced design
            st.markdown('<div class="final-step-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="final-step-header">You did it! 🎉</h2>', unsafe_allow_html=True)
            st.markdown('<p class="final-step-subheader">Just one more step to unlock your child\'s Learning Profile</p>', unsafe_allow_html=True)
            
            email_prompt = f"Share your email to receive periodic helpful tips and resources for {child_name_display if child_name_display else 'your child'}"
            st.markdown(f'<p class="email-prompt">{email_prompt}</p>', unsafe_allow_html=True)
            email = st.text_input("Email (Optional)", key="email_input", placeholder="your.email@example.com")
            
            # Benefits of sharing email
            st.markdown("""
            <div class="email-benefits">
                <p>By sharing your email, you'll get:</p>
                <ul>
                    <li>Age-appropriate activity suggestions</li>
                    <li>Developmental milestone updates</li>
                    <li>Learning tips personalized to your child's profile</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Make button more prominent and fix the submission logic
            if email and not validate_email(email):
                st.error("Please enter a valid email address")
            
            # Make the button full width and more prominent
            if st.button("See My Results", key="results_button", use_container_width=True):
                # Only validate if email is provided (since it's optional)
                if email and not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    # Use a spinner while processing
                    with st.spinner("Generating your results..."):
                        try:
                            # Calculate scores first - always do this even if database fails
                            st.session_state.scores = calculate_scores(st.session_state.responses)
                            personality_label = get_personality_label(st.session_state.scores)
                            
                            # Save essential data to session state first - ensures we can show results
                            # even if database operations fail
                            st.session_state.personality_label = personality_label
                            st.session_state.assessment_date = datetime.now()
                            
                            # Ensure st.session_state.page is set to 'results' - critical step!
                            st.session_state.page = 'results'
                            
                            # Try to save to database - but don't let database issues block showing results
                            try:
                                result_id = save_assessment_result(
                                    child_name=child_name_display,
                                    age=st.session_state.child_info.get("age"),
                                    scores=st.session_state.scores,
                                    personality_label=personality_label,
                                    raw_responses=st.session_state.responses,
                                    email=email if email else None,
                                    birth_month=st.session_state.child_info.get("birth_month"),
                                    birth_year=st.session_state.child_info.get("birth_year")
                                )
                                
                                if result_id:
                                    print(f"Assessment saved with ID: {result_id}")
                                    st.session_state.assessment_id = result_id
                                    
                                    # Complete assignment if this was from a teacher assignment
                                    if st.session_state.assignment_token:
                                        assignment_completed = complete_assignment(st.session_state.assignment_token, result_id)
                                        if assignment_completed:
                                            print(f"Assignment completed for token: {st.session_state.assignment_token}")
                                        else:
                                            print(f"Failed to complete assignment for token: {st.session_state.assignment_token}")
                                else:
                                    print("Assessment will continue without saving to database")
                            except Exception as db_error:
                                print(f"Database error: {str(db_error)}")
                                # Continue to results page even if database save fails
                            
                            # Redirect to results page
                            st.query_params["page"] = "results"
                            st.rerun()
                            
                        except Exception as e:
                            print(f"Critical error processing results: {str(e)}")
                            st.error("We encountered an error processing your results. Please try again.")
                            # Continue trying to show results despite error
                            st.session_state.page = 'results'
                            st.query_params["page"] = "results"
                            st.rerun()

        else:
            # Show next question with enhanced UI - in a compact format to prevent scrolling
            for question in QUESTIONS:
                if question["id"] not in st.session_state.responses:
                    current_category = question["category"]
                    category_icon = category_icons.get(current_category, "✏️")
                    
                    # Create a more compact layout
                    st.markdown('<div class="question-layout">', unsafe_allow_html=True)
                    
                    # Category indicator
                    st.markdown(f"""
                    <div class="category-indicator {current_category.lower().replace(' ', '-')}">
                        <span class="category-icon">{category_icon}</span>
                        <span class="category-name">{current_category}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Enhanced question display
                    question_text = get_child_text(question["text"], child_name_display)
                    st.markdown(f"""
                    <div class="question-container {current_category.lower().replace(' ', '-')}">
                        <h3>{question_text}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Give each option a single character display to prevent line breaks
                    st.markdown('<div class="response-options">', unsafe_allow_html=True)
                    
                    # Create a custom scale with numbers instead of text to avoid wrapping
                    response_options = ["1", "2", "3", "4"]
                    
                    # Show a custom select widget
                    option_index = st.radio(
                        "Your response:",
                        options=range(len(response_options)),
                        format_func=lambda i: response_options[i],
                        key=f"q_{question['id']}",
                        label_visibility="collapsed",
                        horizontal=True,
                        index=None
                    )
                    
                    # Convert numeric selection back to text response
                    response = None
                    if option_index is not None:
                        full_options = ["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"]
                        response = full_options[option_index]
                    
                    # Show a legend to explain the numbers
                    st.markdown("""
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 5px;">
                        <div>1 = Strongly Disagree</div>
                        <div>2 = Disagree</div>
                        <div>3 = Agree</div>
                        <div>4 = Strongly Agree</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add response guidance
                    st.markdown("""
                    <div class="response-guide">
                        <div class="disagree">Disagree</div>
                        <div class="agree">Agree</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Fun facts displayed in a more compact way
                    if len(st.session_state.responses) > 0 and len(st.session_state.responses) % 4 == 0:
                        category_tips = {
                            "Communication": "Did you know? Children who engage in daily conversations develop 40% larger vocabularies.",
                            "Collaboration": "Quick tip: Board games are a fun way to practice taking turns and working together!",
                            "Content": "Fun fact: Children learn best when information connects to their personal interests.",
                            "Critical Thinking": "Try this: Ask 'what if' questions to spark problem-solving skills.",
                            "Creative Innovation": "Did you know? Creative thinking helps develop math and science skills too!",
                            "Confidence": "Research shows: Celebrating effort, not just results, builds lasting confidence."
                        }
                        
                        st.markdown(f"""
                        <div class="category-tip">
                            <div class="tip-icon">💡</div>
                            <div class="tip-text">{category_tips.get(current_category, "")}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # Close question-layout div

                    # Auto-advance when option is selected
                    if response:
                        st.session_state.responses[question["id"]] = LIKERT_SCALE[response]
                        st.rerun()
                    break

def results_page():
    try:
        if not st.session_state.scores:
            st.error("Please complete the assessment first.")
            st.markdown('<div class="navigation-link">', unsafe_allow_html=True)
            if st.button("Start Assessment", use_container_width=False, key="start_assessment"):
                st.session_state.page = 'welcome'
                st.session_state.responses = {}
                st.session_state.scores = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return

        # Get child info
        child_name = st.session_state.child_info.get("name")
        child_age = st.session_state.child_info.get("age")
        sentence_start_text = title_case_name(child_name) if child_name else "Your child"  # For sentence starts
        
        # Main results container
        st.markdown('<div class="results-main-container">', unsafe_allow_html=True)

        # Check if this is from a teacher assignment
        assignment_context = None
        if st.session_state.assignment_token:
            assignment_context = get_assignment_by_token(st.session_state.assignment_token)
        
        # Header section with personality label
        try:
            personality_label = get_personality_label(st.session_state.scores)
            
            header_html = f"""
            <div class="results-header">
                <h1>{sentence_start_text}'s Learning Profile</h1>
                <p class="profile-date">Completed on {datetime.now().strftime('%B %d, %Y')}</p>
            """
            
            # Add assignment context if from teacher
            if assignment_context:
                header_html += f"""
                <div class="assignment-context">
                    <p class="teacher-assignment">📚 <strong>For {assignment_context['teacher_name']}</strong> at {assignment_context['school']} ({assignment_context['grade_level']})</p>
                    <p class="assignment-note">Your child's teacher will receive classroom-focused insights to better support their learning.</p>
                </div>
                """
            
            header_html += """
            </div>
            
            <div class="personality-feature">
                <div class="personality-feature-content">
                    <span class="personality-feature-prefix">{sentence_start_text} is a</span>
                    <h2 class="personality-feature-label">{personality_label}</h2>
                    <p class="personality-feature-description">Children with this profile thrive when given opportunities to explore ideas deeply and approach learning at their own pace.</p>
                </div>
            </div>
            """.format(sentence_start_text=sentence_start_text, personality_label=personality_label)
            
            st.markdown(header_html, unsafe_allow_html=True)
            
# Sharing options moved to bottom of page
            
            # Profile visualization
            st.markdown('<div class="profile-visualization">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Radar chart with error handling
                st.markdown('<h3 class="section-title">Learning Strengths Map</h3>', unsafe_allow_html=True)
                try:
                    if st.session_state.scores and all(score is not None for score in st.session_state.scores.values()):
                        fig = create_radar_chart(st.session_state.scores)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info("Complete score data is not available for visualization.")
                except Exception as viz_error:
                    st.info("Unable to display visualization chart. Your profile data is still valid.")
                    print(f"Visualization error: {str(viz_error)}")
            
            with col2:
                # Key insights sidebar
                st.markdown('<div class="key-insights-container">', unsafe_allow_html=True)
                st.markdown('<h3 class="insights-title">Key Insights</h3>', unsafe_allow_html=True)
                
                # Get top strengths and areas for growth
                strengths = [cat for cat, score in st.session_state.scores.items() if score == "High"]
                growth_areas = [cat for cat, score in st.session_state.scores.items() if score == "Low"]
                
                if strengths:
                    strength_list = ", ".join(strengths[:2]) if len(strengths) > 1 else strengths[0]
                    st.markdown(f"""
                    <div class="insight-item strength">
                        <div class="insight-icon">🌟</div>
                        <div class="insight-content">
                            <h4>Top Strengths</h4>
                            <p>{strength_list}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if growth_areas:
                    growth_list = ", ".join(growth_areas[:2]) if len(growth_areas) > 1 else growth_areas[0]
                    st.markdown(f"""
                    <div class="insight-item growth">
                        <div class="insight-icon">🌱</div>
                        <div class="insight-content">
                            <h4>Growth Opportunities</h4>
                            <p>{growth_list}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Motivation triggers based on profile
                st.markdown(f"""
                <div class="insight-item motivation">
                    <div class="insight-icon">🔆</div>
                    <div class="insight-content">
                        <h4>Motivation Triggers</h4>
                        <p>{get_motivation_triggers(strengths)}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Answer the 4 key parent questions in tabs
            st.markdown('<div class="parent-questions">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Personalized Learning Insights</h3>', unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "Learning Style", 
                "Motivation", 
                "Key Milestones", 
                "Support Strategies"
            ])
            
            with tab1:
                st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                st.markdown('<h4>How does your child learn best?</h4>', unsafe_allow_html=True)
                
                # Learning style insights based on scores
                learning_style = get_learning_style(st.session_state.scores)
                st.markdown(f'<p class="tab-description">{learning_style}</p>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="learning-preferences">
                        <h5>Preferred Learning Environments</h5>
                        <ul class="preferences-list">
                            <li>Small group settings with peer interaction</li>
                            <li>Hands-on, tactile learning opportunities</li>
                            <li>Visual aids and demonstrations</li>
                            <li>Spaces that allow movement and exploration</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="learning-preferences">
                        <h5>Information Processing</h5>
                        <ul class="preferences-list">
                            <li>Needs time to observe before participating</li>
                            <li>Processes information through discussion</li>
                            <li>Connects new concepts to personal experiences</li>
                            <li>Benefits from multi-sensory learning approaches</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                st.markdown('<h4>What motivates your child?</h4>', unsafe_allow_html=True)
                
                # Motivation insights
                motivation_details = get_detailed_motivation(strengths)
                st.markdown(f'<p class="tab-description">{motivation_details}</p>', unsafe_allow_html=True)
                
                # Motivation strategies
                st.markdown("""
                <div class="motivation-strategies">
                    <h5>Effective Motivation Strategies</h5>
                    <div class="strategy-grid">
                        <div class="strategy-card">
                            <div class="strategy-icon">🏆</div>
                            <h6>Recognition</h6>
                            <p>Acknowledge effort and progress, not just results</p>
                        </div>
                        <div class="strategy-card">
                            <div class="strategy-icon">🎮</div>
                            <h6>Play-Based</h6>
                            <p>Incorporate games and playful elements into learning</p>
                        </div>
                        <div class="strategy-card">
                            <div class="strategy-icon">🔍</div>
                            <h6>Curiosity-Led</h6>
                            <p>Follow their questions and natural interests</p>
                        </div>
                        <div class="strategy-card">
                            <div class="strategy-icon">👨‍👩‍👧‍👦</div>
                            <h6>Social Connection</h6>
                            <p>Create opportunities for collaborative learning</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                st.markdown('<h4>What milestones matter most for your child?</h4>', unsafe_allow_html=True)
                
                # Age-appropriate milestones
                st.markdown(f'<p class="tab-description">Based on your child\'s profile, these are the developmental milestones to focus on at age {child_age}.</p>', unsafe_allow_html=True)
                
                # Milestone cards
                milestone_categories = get_milestone_focus(st.session_state.scores)
                
                for category in milestone_categories:
                    milestones = get_age_appropriate_milestones(category, child_age)
                    
                    st.markdown(f"""
                    <div class="milestone-category {category.lower().replace(' ', '-')}">
                        <h5>{category}</h5>
                        <div class="milestone-list">
                    """, unsafe_allow_html=True)
                    
                    for milestone in milestones:
                        st.markdown(f"""
                        <div class="milestone-item">
                            <span class="milestone-check">○</span>
                            <span class="milestone-text">{milestone}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab4:
                st.markdown('<div class="tab-content">', unsafe_allow_html=True)
                st.markdown('<h4>How can you support your child\'s learning journey?</h4>', unsafe_allow_html=True)
                
                # Support strategies
                st.markdown('<p class="tab-description">Try these personalized activities and resources to support your child\'s growth.</p>', unsafe_allow_html=True)
                
                # Generate description for activities
                with st.container():
                    try:
                        success = generate_description(
                            st.session_state.scores,
                            child_name,
                            child_age
                        )
                        if not success:
                            st.error("Unable to generate activities recommendations.")
                    except Exception as e:
                        st.error("Error displaying activities recommendations")
                
                # Begin Product Recommendations
                try:
                    from utils.begin_products import get_begin_recommendations, get_external_activities, get_parent_insights
                    
                    # Get personalized recommendations
                    begin_recommendations = get_begin_recommendations(st.session_state.scores, child_age)
                    external_activities = get_external_activities(st.session_state.scores, 2)
                    parent_insights = get_parent_insights(st.session_state.scores, child_name, child_age)
                    
                    # Begin Products Section
                    st.markdown('<h5>🌟 Personalized Begin Product Recommendations</h5>', unsafe_allow_html=True)
                    
                    # Create tabs for different recommendation types
                    rec_tab1, rec_tab2, rec_tab3 = st.tabs(["Build on Strengths", "Support Growth", "Daily Activities"])
                    
                    with rec_tab1:
                        if begin_recommendations["strength_builders"]:
                            col1, col2 = st.columns(2)
                            for i, product in enumerate(begin_recommendations["strength_builders"][:4]):
                                with col1 if i % 2 == 0 else col2:
                                    product_type_emoji = {"apps": "📱", "kits": "📦", "classes": "👩‍🏫", "tutoring": "🎯"}.get(product["type"], "🌟")
                                    st.markdown(f"""
                                    <div class="begin-product-card">
                                        <div class="product-header">
                                            <span class="product-emoji">{product_type_emoji}</span>
                                            <h4>{product["name"]}</h4>
                                            <span class="product-type">{product["type"].title()}</span>
                                        </div>
                                        <p class="product-description">{product["description"]}</p>
                                        <div class="product-benefits">
                                            <strong>Perfect for:</strong> {product["category_match"]}
                                        </div>
                                        <div class="product-benefits-list">
                                            {' • '.join(product["benefits"][:2])}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"Learn More About {product['name']}", key=f"strength_{i}"):
                                        st.info(f"Visit {product['url']} to explore {product['name']}")
                        else:
                            st.info("Building a personalized recommendation list based on your child's strengths...")
                    
                    with rec_tab2:
                        if begin_recommendations["growth_supporters"]:
                            col1, col2 = st.columns(2)
                            for i, product in enumerate(begin_recommendations["growth_supporters"][:4]):
                                with col1 if i % 2 == 0 else col2:
                                    product_type_emoji = {"apps": "📱", "kits": "📦", "classes": "👩‍🏫", "tutoring": "🎯"}.get(product["type"], "🌱")
                                    st.markdown(f"""
                                    <div class="begin-product-card growth-card">
                                        <div class="product-header">
                                            <span class="product-emoji">{product_type_emoji}</span>
                                            <h4>{product["name"]}</h4>
                                            <span class="product-type">{product["type"].title()}</span>
                                        </div>
                                        <p class="product-description">{product["description"]}</p>
                                        <div class="product-benefits">
                                            <strong>Helps develop:</strong> {product["category_match"]}
                                        </div>
                                        <div class="product-benefits-list">
                                            {' • '.join(product["benefits"][:2])}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"Explore {product['name']}", key=f"growth_{i}"):
                                        st.info(f"Visit {product['url']} to learn more about {product['name']}")
                        else:
                            st.info("Curating growth-focused activities based on your child's learning profile...")
                    
                    with rec_tab3:
                        st.markdown('<h6>🏠 At-Home Activities (No Purchase Needed)</h6>', unsafe_allow_html=True)
                        
                        # Show external activities by category
                        activity_count = 0
                        for category, activities in external_activities.items():
                            if activity_count < 6:  # Limit total activities shown
                                st.markdown(f"""
                                <div class="activity-category">
                                    <h6>{category}</h6>
                                    <ul class="activity-list">
                                """, unsafe_allow_html=True)
                                
                                for activity in activities[:2]:  # Show 2 per category
                                    st.markdown(f'<li class="activity-item">• {activity}</li>', unsafe_allow_html=True)
                                    activity_count += 1
                                
                                st.markdown('</ul></div>', unsafe_allow_html=True)
                        
                        # Parent insights section
                        st.markdown('<h6>💡 Parent Insights</h6>', unsafe_allow_html=True)
                        
                        insight_col1, insight_col2 = st.columns(2)
                        with insight_col1:
                            st.markdown(f"""
                            <div class="parent-insight-card">
                                <h6>🎯 Learning Style</h6>
                                <p>{parent_insights["learning_style"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="parent-insight-card">
                                <h6>🔥 Motivation Tips</h6>
                                <p>{parent_insights["motivation_tips"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with insight_col2:
                            st.markdown(f"""
                            <div class="parent-insight-card">
                                <h6>🌱 Growth Support</h6>
                                <p>{parent_insights["growth_support"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="parent-insight-card">
                                <h6>📅 Daily Integration</h6>
                                <p>{parent_insights["daily_integration"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                except ImportError:
                    # Fallback to original recommendations if import fails
                    st.markdown('<h5>Recommended Resources</h5>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        top_strength = strengths[0] if strengths else list(st.session_state.scores.keys())[0]
                        st.markdown(f"""
                        <div class="resource-card">
                            <div class="resource-icon">🎲</div>
                            <div class="resource-content">
                                <h4>Fun Family Game</h4>
                                <p>"Puzzle Discovery" - Perfect for building {top_strength}</p>
                                <a href="#" class="resource-link">Learn more →</a>
                            </div>
                        </div>
                        
                        <div class="resource-card">
                            <div class="resource-icon">📱</div>
                            <div class="resource-content">
                                <h4>Learning App</h4>
                                <p>"Begin Explorer" - Interactive activities for ages {child_age}-{child_age+2}</p>
                                <a href="#" class="resource-link">Download →</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        growth_area = growth_areas[0] if growth_areas else list(st.session_state.scores.keys())[-1]
                        st.markdown(f"""
                        <div class="resource-card">
                            <div class="resource-icon">📚</div>
                            <div class="resource-content">
                                <h4>Book Recommendation</h4>
                                <p>"Growing Minds" - Supports development in {growth_area}</p>
                                <a href="#" class="resource-link">See more →</a>
                            </div>
                        </div>
                        
                        <div class="resource-card">
                            <div class="resource-icon">👨‍👩‍👧‍👦</div>
                            <div class="resource-content">
                                <h4>Community Activity</h4>
                                <p>Local workshop on child development starting next month</p>
                                <a href="#" class="resource-link">Find events →</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error displaying results visualization: {str(e)}")
            st.markdown('<div class="navigation-link">', unsafe_allow_html=True)
            if st.button("Start Over", use_container_width=False, key="start_over"):
                st.session_state.page = 'welcome'
                st.session_state.responses = {}
                st.session_state.scores = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return

        # Share options moved to the bottom
        st.markdown("""
        <div class="share-container">
            <h4 style="margin-bottom: 15px;">Share This Profile</h4>
            <div class="share-buttons-row">
                <div class="share-button">
                    <span>📤 Share with Partner</span>
                </div>
                <div class="share-button">
                    <span>👩‍🏫 Share with Teacher</span>
                </div>
                <div class="share-button">
                    <span>🖨️ Print Profile</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer with restart option
        st.markdown("""
        <div class="results-footer">
            <p>This Learning Profile is a snapshot of your child's current development. Children grow and change rapidly, so consider reassessing in 6 months to track progress.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Updated buttons for profile management
        st.markdown('<div style="text-align: center; margin-top: 20px;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        # Use child name from session state with fallback
        child_name_display = st.session_state.child_info.get("name", "your child") if hasattr(st.session_state, "child_info") else "your child"
        
        with col1:
            if st.button(f"Update {child_name_display}'s Profile", use_container_width=True, key="update_profile"):
                # Keep child info but reset responses and scores for a new assessment
                st.session_state.responses = {}
                st.session_state.scores = None
                st.query_params["page"] = "quiz"
                st.rerun()
                
        with col2:
            if st.button("Add New Child", use_container_width=True, key="add_new_child"):
                # Reset all session state for a completely new profile
                st.session_state.child_info = None
                st.session_state.responses = {}
                st.session_state.scores = None
                st.query_params["page"] = "welcome"
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close main results container

    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
        st.markdown('<div class="navigation-link">', unsafe_allow_html=True)
        if st.button("Start Over", use_container_width=False, key="error_start_over"):
            st.session_state.page = 'welcome'
            st.session_state.responses = {}
            st.session_state.scores = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Helper functions for results page
def get_motivation_triggers(strengths):
    """Return motivation triggers based on top strengths."""
    if not strengths:
        return "Positive recognition and celebrating small wins"
    
    motivation_map = {
        "Communication": "Opportunities to share ideas and stories",
        "Collaboration": "Group activities and helping others",
        "Content": "Exploring new information and facts",
        "Critical Thinking": "Puzzles and problem-solving challenges",
        "Creative Innovation": "Open-ended creative projects",
        "Confidence": "Achieving goals and receiving recognition"
    }
    
    if len(strengths) >= 2:
        return f"{motivation_map.get(strengths[0])} and {motivation_map.get(strengths[1])}"
    return motivation_map.get(strengths[0])

def get_learning_style(scores):
    """Generate learning style description based on scores profile."""
    strengths = [cat for cat, score in scores.items() if score == "High"]
    developing = [cat for cat, score in scores.items() if score == "Medium"]
    
    if not strengths and not developing:
        return "Your child is still developing their learning preferences. They benefit from a varied approach that includes multiple ways of engaging with information."
    
    if "Communication" in strengths and "Collaboration" in strengths:
        return "Your child thrives in social learning environments where they can discuss ideas, work with others, and express their thoughts verbally. They learn best through conversation and collaborative activities."
    
    if "Content" in strengths and "Critical Thinking" in strengths:
        return "Your child has an analytical learning style. They enjoy gathering information, asking questions, and solving problems methodically. They benefit from structured learning with clear objectives."
    
    if "Creative Innovation" in strengths:
        return "Your child has a creative, imaginative learning style. They enjoy open-ended activities that allow for exploration and coming up with unique solutions. Visual and hands-on learning approaches work well."
    
    if "Confidence" in strengths:
        return "Your child learns best when they feel secure in their abilities. They're willing to take on challenges and learn from mistakes when in supportive environments that celebrate effort and progress."
    
    # Default response
    return "Your child has a balanced learning style that combines different approaches. They benefit from variety in learning methods and environments to keep them engaged and motivated."

def get_detailed_motivation(strengths):
    """Provide detailed motivation insights based on strengths."""
    if not strengths:
        return "Your child is motivated by a supportive environment that recognizes their efforts and provides clear, achievable goals. Celebrating small wins helps build their confidence and desire to learn."
    
    motivation_details = {
        "Communication": "Your child is motivated by opportunities to express themselves and be heard. They thrive when given chances to share stories, explain their thinking, and engage in meaningful conversations.",
        "Collaboration": "Your child is motivated by social connection and helping others. Working as part of a team, sharing responsibilities, and contributing to group success drives their engagement.",
        "Content": "Your child is motivated by acquiring new knowledge and understanding how things work. They enjoy learning facts, building expertise, and making connections between ideas.",
        "Critical Thinking": "Your child is motivated by solving problems and figuring things out. They enjoy challenges that make them think deeply, analyze information, and come to their own conclusions.",
        "Creative Innovation": "Your child is motivated by opportunities to create and invent. They thrive when given freedom to express their unique ideas and approach activities in their own way.",
        "Confidence": "Your child is motivated by feeling capable and independent. Successfully completing challenging tasks and receiving recognition for their efforts fuels their drive to learn more."
    }
    
    if len(strengths) >= 2:
        return f"{motivation_details.get(strengths[0])} {motivation_details.get(strengths[1])}"
    return motivation_details.get(strengths[0])

def get_milestone_focus(scores):
    """Determine which milestone categories to focus on based on scores."""
    # Return 2-3 categories to focus on - including both strengths and growth areas
    strengths = [cat for cat, score in scores.items() if score == "High"]
    growth_areas = [cat for cat, score in scores.items() if score == "Low"]
    
    focus_areas = []
    # Add 1-2 strengths to build upon
    if strengths:
        focus_areas.extend(strengths[:2])
    
    # Add 1 growth area to develop
    if growth_areas:
        focus_areas.append(growth_areas[0])
    
    # If we don't have 3 areas yet, add from medium areas
    if len(focus_areas) < 3:
        medium_areas = [cat for cat, score in scores.items() if score == "Medium"]
        focus_areas.extend(medium_areas[:3-len(focus_areas)])
    
    # If still not enough, add more from the remaining categories
    all_categories = list(scores.keys())
    while len(focus_areas) < 3 and all_categories:
        if all_categories[0] not in focus_areas:
            focus_areas.append(all_categories[0])
        all_categories.pop(0)
    
    return focus_areas[:3]  # Return up to 3 focus areas

def get_age_appropriate_milestones(category, age):
    """Get age-appropriate milestones for a category."""
    # Define milestones for different age ranges
    milestones = {
        "Communication": {
            "young": [  # Ages 2-5
                "Uses 2-3 word sentences to express needs",
                "Follows simple 2-step directions",
                "Asks questions using who, what, where, why",
                "Tells simple stories about experiences"
            ],
            "middle": [  # Ages 6-8
                "Expresses thoughts in complete sentences",
                "Follows multi-step instructions",
                "Asks clarifying questions when confused",
                "Adapts communication style based on audience"
            ],
            "older": [  # Ages 9-11
                "Participates effectively in group discussions",
                "Presents ideas logically and persuasively",
                "Uses figurative language appropriately",
                "Gives and receives constructive feedback"
            ]
        },
        "Collaboration": {
            "young": [
                "Takes turns in games and activities",
                "Shares toys with gentle reminders",
                "Shows concern when others are upset",
                "Plays cooperatively with peers for short periods"
            ],
            "middle": [
                "Works in a group toward a common goal",
                "Respects others' ideas and contributions",
                "Resolves simple conflicts with peers",
                "Takes responsibility within group settings"
            ],
            "older": [
                "Negotiates roles and responsibilities in groups",
                "Compromises to reach group consensus",
                "Recognizes and utilizes others' strengths",
                "Shows leadership in collaborative settings"
            ]
        },
        "Content": {
            "young": [
                "Recognizes and names colors and shapes",
                "Counts objects up to 10-20",
                "Identifies some letters and their sounds",
                "Shows interest in how things work"
            ],
            "middle": [
                "Reads and comprehends grade-level texts",
                "Uses basic math operations with confidence",
                "Shows curiosity about science concepts",
                "Remembers and applies learned information"
            ],
            "older": [
                "Comprehends complex reading material",
                "Applies math concepts to real-world problems",
                "Connects ideas across different subject areas",
                "Researches topics of interest independently"
            ]
        },
        "Critical Thinking": {
            "young": [
                "Sorts objects by attributes (color, size, shape)",
                "Identifies simple patterns",
                "Makes predictions based on observations",
                "Solves simple problems with adult guidance"
            ],
            "middle": [
                "Identifies cause and effect relationships",
                "Compares and contrasts ideas or objects",
                "Thinks through multiple solutions to a problem",
                "Makes logical connections between ideas"
            ],
            "older": [
                "Analyzes information from multiple sources",
                "Evaluates evidence and forms reasoned conclusions",
                "Identifies biases and considers different perspectives",
                "Develops and tests hypotheses systematically"
            ]
        },
        "Creative Innovation": {
            "young": [
                "Engages in imaginative play with various props",
                "Creates simple art using different materials",
                "Makes up stories with beginning, middle, and end",
                "Finds new uses for everyday objects"
            ],
            "middle": [
                "Generates multiple ideas for creative projects",
                "Experiments with different approaches to problems",
                "Creates original stories, art, or music",
                "Thinks outside conventional boundaries"
            ],
            "older": [
                "Develops innovative solutions to complex problems",
                "Combines ideas in unique and unexpected ways",
                "Takes creative risks and learns from failures",
                "Adds personal style to creative expressions"
            ]
        },
        "Confidence": {
            "young": [
                "Attempts new activities with encouragement",
                "Expresses pride in accomplishments",
                "Recovers quickly from minor setbacks",
                "Separates from caregivers with minimal anxiety"
            ],
            "middle": [
                "Tries challenging tasks independently",
                "Persists when facing difficulties",
                "Expresses opinions and preferences clearly",
                "Recognizes own strengths and abilities"
            ],
            "older": [
                "Takes on leadership roles when appropriate",
                "Views mistakes as learning opportunities",
                "Sets challenging but achievable goals",
                "Advocates for self when needed"
            ]
        }
    }
    
    # Determine age group
    if age <= 5:
        age_group = "young"
    elif age <= 8:
        age_group = "middle"
    else:
        age_group = "older"
    
    return milestones.get(category, {}).get(age_group, ["Milestone information not available for this age group"])

def welcome_page():
    # Main header with reduced size
    st.markdown("""
    <style>
    /* Make the welcome header smaller to save space */
    .welcome-header h1 {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    .welcome-header .tagline {
        font-size: 1rem !important;
        line-height: 1.4 !important;
    }
    
    /* Subtle login link styling */
    .subtle-login {
        display: block;
        text-align: center;
        margin: 10px auto 20px;
        color: #666;
        font-size: 0.9rem;
        padding: 5px;
        opacity: 0.8;
    }
    
    .subtle-login:hover {
        opacity: 1;
        text-decoration: underline;
    }
    
    /* Make Begin Profile button stand out */
    .begin-profile-btn {
        background-color: var(--begin-primary);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Compact header without extra margins
    st.markdown("""
    <style>
    /* Remove extra margins in the main content container */
    section.main > div.block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    </style>
    
    <div class="welcome-header">
        <h1>Help Your Child's Teacher Understand Their Unique Learning Style from Day 1</h1>
        <p class="tagline" style="text-align: center; max-width: 900px; margin: 0 auto;">Join 50,000+ families using Begin Learning Profiles to strengthen school-home connections. Get personalized insights and Begin product recommendations tailored to your child's learning strengths.</p>
        
        <!-- Teacher Access Link -->
        <div style="text-align: center; margin-top: 1rem;">
            <a href="?page=teacher_register" style="color: var(--begin-secondary); font-weight: 600; text-decoration: none; font-size: 0.9rem;">
                👩‍🏫 Are you a teacher? Click here to access the Teacher Dashboard
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show login form if requested
    if st.session_state.get('show_login', False):
        with st.expander("Log In", expanded=True):
            login_email = st.text_input("Email Address", key="login_email", 
                                      placeholder="Your email address")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Log In", key="login_button", use_container_width=True):
                    if login_email and validate_email(login_email):
                        # Retrieve previous assessments from database
                        with st.spinner("Retrieving your previous assessments..."):
                            previous_assessments = get_previous_assessments(email=login_email)
                            
                        if previous_assessments:
                            st.session_state.user_email = login_email
                            st.session_state.previous_assessments = previous_assessments
                            st.session_state.show_login = False
                            st.success(f"Found {len(previous_assessments)} previous assessment(s).")
                            st.query_params["page"] = "profile_dashboard"
                            st.rerun()
                        else:
                            st.warning("No assessments found for this email. Please create a new assessment.")
                    else:
                        st.error("Please enter a valid email address.")
                        
            with col2:
                if st.button("Cancel", key="cancel_login", use_container_width=True):
                    st.session_state.show_login = False
                    st.rerun()
    
    # REORGANIZED CONTENT - About Your Child section first as requested
    
    # Renamed section with better header - MOVED TO THE TOP
    st.markdown("""
    <div class="child-info-section">
        <h3>Help Your Child Learn Best</h3>
        <p>Please share a few details to personalize their assessment results</p>
    </div>
    """, unsafe_allow_html=True)
    
    child_name = st.text_input("Child's Name (Optional)", key="child_name", 
                            placeholder="Enter your child's name")

    col1, col2 = st.columns(2)
    with col1:
        birth_month = st.selectbox(
            "Birth Month",
            options=range(1, 13),
            format_func=lambda x: datetime(2000, x, 1).strftime('%B'),
            key="birth_month"
        )
    with col2:
        current_year = datetime.now().year
        min_year = current_year - 11  # Expanded age range to 2-11 years
        max_year = current_year - 2
        birth_year = st.selectbox(
            "Birth Year",
            options=range(max_year, min_year - 1, -1),
            key="birth_year"
        )

    # Get started button with enhanced styling - MOVED UP with the child info
    st.markdown("""
    <div class="start-button-container">
        <p class="start-note">It takes only 5 minutes to complete the assessment and unlock valuable insights!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Begin Profile", key="start_button", use_container_width=True):
        today = datetime.now()
        birth_date = datetime(birth_year, birth_month, 1)
        age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, 1))

        st.session_state.child_info = {
            "name": child_name.strip() if child_name else None,
            "age": age_years,
            "birth_month": birth_month,
            "birth_year": birth_year
        }
        # Use URL parameter for navigation
        st.query_params["page"] = "quiz"
        st.rerun()
    
    # Show login options directly below the Begin Profile button
    if st.session_state.user_email:
        # If logged in, show profile link
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"View My Profiles", key="profile_btn", type="secondary", use_container_width=False):
                st.query_params["page"] = "profile_dashboard"
                st.rerun()
    else:
        # If not logged in, show the login form directly below
        with st.expander("Already have a profile? Log In", expanded=False):
            login_email = st.text_input("Email Address", key="login_email", 
                                      placeholder="Your email address")
            
            if st.button("Log In", key="login_button", use_container_width=True):
                if login_email and validate_email(login_email):
                    # Store the email regardless of assessment history
                    st.session_state.user_email = login_email
                    
                    # Try to retrieve previous assessments from database
                    try:
                        with st.spinner("Retrieving your previous assessments..."):
                            previous_assessments = get_previous_assessments(email=login_email)
                            
                        if previous_assessments and len(previous_assessments) > 0:
                            st.session_state.previous_assessments = previous_assessments
                            st.success(f"Found {len(previous_assessments)} previous assessment(s).")
                            st.query_params["page"] = "profile_dashboard"
                            st.rerun()
                        else:
                            # Still let them in, but they'll need to create a new profile
                            st.success(f"Welcome, {login_email}! Please create your first child profile.")
                    except Exception as e:
                        print(f"Login error: {str(e)}")
                        # Still let them use the app without previous profiles
                        st.warning("We encountered an issue retrieving your profile history. You can still create a new assessment.")
                else:
                    st.error("Please enter a valid email address.")
    
    # Value proposition in columns - MOVED BELOW the CTA
    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Why Your Child's Learning Profile Matters</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="value-prop">
            <h3>Why This Matters</h3>
            <p>Understanding your child's learning profile helps you:</p>
            <ul>
                <li>Discover how they learn best (style, pace, interests)</li>
                <li>Understand what truly motivates them</li>
                <li>Focus on the milestones that matter most</li>
                <li>Find simple ways to support their development</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-prop">
            <h3>The Begin Learning Profile</h3>
            <p>This assessment helps create a personalized learning profile that:</p>
            <ul>
                <li>Captures your child's unique learning identity</li>
                <li>Evolves as they grow and develop</li>
                <li>Connects home and school learning</li>
                <li>Provides actionable recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Framework explanation
    st.markdown("""
    <div class="framework-section">
        <h3>The 6 Cs Learning Framework</h3>
        <p>This assessment measures six critical competencies for lifelong learning success:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use columns to display the framework categories with icons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="category-card communication">
            <h4>📣 Communication</h4>
            <p>Express ideas and listen effectively</p>
        </div>
        
        <div class="category-card collaboration">
            <h4>🤝 Collaboration</h4>
            <p>Work well with others</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="category-card content">
            <h4>📚 Content</h4>
            <p>Understand and retain knowledge</p>
        </div>
        
        <div class="category-card critical-thinking">
            <h4>🧩 Critical Thinking</h4>
            <p>Analyze and solve problems</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="category-card creative-innovation">
            <h4>💡 Creative Innovation</h4>
            <p>Find unique solutions</p>
        </div>
        
        <div class="category-card confidence">
            <h4>🌟 Confidence</h4>
            <p>Believe in oneself</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dashboard Preview Section
    st.markdown("""
    <div style="margin: 3rem 0 2rem 0;">
        <h3 style="text-align: center; color: var(--begin-primary); margin-bottom: 1.5rem;">See What Parents and Teachers Receive</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for dashboard preview
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["📊 Parent Dashboard", "👩‍🏫 Teacher Insights", "🌟 Success Stories"])
    
    with preview_tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="dashboard-preview">
                <h4>Your Child's Learning Profile</h4>
                <div class="preview-feature">
                    <span class="feature-icon">🎯</span>
                    <div>
                        <strong>Interactive Learning Map</strong><br>
                        <small>Visual radar chart showing your child's strengths across 6 learning dimensions</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">📱</span>
                    <div>
                        <strong>Personalized Begin Products</strong><br>
                        <small>Apps, kits, classes, and tutoring matched to your child's profile</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">🏠</span>
                    <div>
                        <strong>At-Home Activities</strong><br>
                        <small>Simple activities you can do today to support learning</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">💡</span>
                    <div>
                        <strong>Parent Insights</strong><br>
                        <small>Understanding your child's motivation, learning style, and growth areas</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Simulated dashboard screenshot
            st.markdown("""
            <div class="dashboard-mockup">
                <div class="mockup-header">
                    <div class="mockup-dots">
                        <div class="dot red"></div>
                        <div class="dot yellow"></div>
                        <div class="dot green"></div>
                    </div>
                    <div class="mockup-title">Emma's Learning Profile</div>
                </div>
                <div class="mockup-content">
                    <div class="profile-summary">
                        <div class="personality-label">🌟 Creative Collaborator</div>
                        <div class="strength-badges">
                            <span class="badge high">Communication: High</span>
                            <span class="badge high">Creative Innovation: High</span>
                            <span class="badge medium">Collaboration: Medium</span>
                        </div>
                    </div>
                    <div class="recommendations-preview">
                        <h6>Recommended for Emma:</h6>
                        <div class="rec-item">📱 Begin Creative App</div>
                        <div class="rec-item">🎨 Creative Arts Kit</div>
                        <div class="rec-item">👩‍🏫 Creative Writing Workshop</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with preview_tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="teacher-preview">
                <h4>Classroom Intelligence for Teachers</h4>
                <div class="preview-feature">
                    <span class="feature-icon">👥</span>
                    <div>
                        <strong>Individual Student Profiles</strong><br>
                        <small>Understand each student's learning preferences and motivations</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">🎯</span>
                    <div>
                        <strong>Differentiation Strategies</strong><br>
                        <small>Specific classroom techniques for each learning profile</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">📞</span>
                    <div>
                        <strong>Parent Communication Tools</strong><br>
                        <small>Talking points and collaboration suggestions</small>
                    </div>
                </div>
                <div class="preview-feature">
                    <span class="feature-icon">📈</span>
                    <div>
                        <strong>Class Overview Dashboard</strong><br>
                        <small>See learning style distribution across your classroom</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="teacher-mockup">
                <div class="mockup-header">
                    <div class="mockup-title">Ms. Johnson's 3rd Grade Class</div>
                </div>
                <div class="teacher-content">
                    <div class="class-stats">
                        <div class="stat-item">
                            <span class="stat-number">24</span>
                            <span class="stat-label">Students Profiled</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">18</span>
                            <span class="stat-label">Parent Responses</span>
                        </div>
                    </div>
                    <div class="student-highlights">
                        <h6>Today's Focus Students:</h6>
                        <div class="student-card">
                            <strong>Emma R.</strong> - Creative Collaborator<br>
                            <small>💡 Try group storytelling activities</small>
                        </div>
                        <div class="student-card">
                            <strong>Marcus J.</strong> - Analytical Explorer<br>
                            <small>🔍 Provide hands-on science experiments</small>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with preview_tab3:
        st.markdown("""
        <div class="testimonials-section">
            <div class="testimonial">
                <div class="testimonial-content">
                    "The Begin Learning Profile helped me understand why my daughter was struggling in traditional math activities. Now I know she's a kinesthetic learner, and we use Begin's hands-on math kit at home. Her confidence has soared!"
                </div>
                <div class="testimonial-author">
                    <strong>Sarah M.</strong> - Parent of 2nd grader
                </div>
            </div>
            
            <div class="testimonial">
                <div class="testimonial-content">
                    "As a kindergarten teacher, having learning profiles from Day 1 completely changed how I approach my classroom. I can differentiate instruction from the start instead of spending weeks figuring out each child's needs."
                </div>
                <div class="testimonial-author">
                    <strong>Mrs. Rodriguez</strong> - Kindergarten Teacher
                </div>
            </div>
            
            <div class="testimonial">
                <div class="testimonial-content">
                    "My son's teacher assigned this during Back to School week. Now we both understand that he's a 'Creative Innovator' and need to give him more open-ended projects. The Begin products recommended were perfect for him!"
                </div>
                <div class="testimonial-author">
                    <strong>Jennifer K.</strong> - Parent of 1st grader
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Debug mode toggle (hidden in a small expander at the bottom)
    with st.expander("Developer Options", expanded=False):
        debug_enabled = st.checkbox("Enable Debug Mode", value=st.session_state.debug_mode)
        if debug_enabled != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_enabled
            
        if debug_enabled:
            if st.button("Skip to Results (Debug)", key="debug_button"):
                # Create mock data for debugging
                st.session_state.child_info = {
                    "name": "Test Child",
                    "age": 5,
                    "birth_month": 6,
                    "birth_year": current_year - 5
                }
                
                # Generate balanced scores across categories
                categories = ["Communication", "Collaboration", "Content", 
                            "Critical Thinking", "Creative Innovation", "Confidence"]
                scores = {}
                for i, category in enumerate(categories):
                    if i < 2:  # First two are high
                        scores[category] = "High"
                    elif i < 4:  # Next two are medium
                        scores[category] = "Medium"
                    else:  # Last two are low
                        scores[category] = "Low"
                
                st.session_state.scores = scores
                # Use URL parameter for navigation
                st.query_params["page"] = "results"
                st.rerun()

# Profile dashboard page
def teacher_register_page():
    """Teacher registration and login page"""
    st.markdown("""
    <div class="teacher-auth-container">
        <h1 style="text-align: center; color: var(--begin-primary);">Welcome, Educators!</h1>
        <p style="text-align: center; font-size: 1.1rem; margin-bottom: 2rem;">
            Join the Begin Learning Profile platform to help your students from Day 1
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check URL for assignment token (parent access via teacher assignment)
    query_params = st.query_params
    assignment_token = query_params.get("token")
    
    if assignment_token:
        # Parent access via teacher assignment
        assignment = get_assignment_by_token(assignment_token)
        if assignment:
            st.session_state.assignment_token = assignment_token
            st.success(f"Welcome! {assignment['teacher_name']} from {assignment['school']} has assigned this profile for {assignment['child_name']}.")
            st.query_params["page"] = "quiz"
            st.rerun()
        else:
            st.error("Invalid assignment link. Please contact your teacher for a new link.")
            return
    
    # Teacher registration/login tabs
    tab1, tab2 = st.tabs(["👩‍🏫 Teacher Login", "📝 New Teacher Registration"])
    
    with tab1:
        st.markdown("### Teacher Login")
        login_email = st.text_input("Teacher Email", key="teacher_login_email")
        
        if st.button("Login as Teacher", key="teacher_login_btn", use_container_width=True):
            if login_email and validate_email(login_email):
                teacher = get_teacher_by_email(login_email)
                if teacher:
                    st.session_state.teacher_user = teacher
                    st.success(f"Welcome back, {teacher['name']}!")
                    st.query_params["page"] = "teacher_dashboard"
                    st.rerun()
                else:
                    st.error("Teacher account not found. Please register first.")
            else:
                st.error("Please enter a valid email address.")
    
    with tab2:
        st.markdown("### Create Teacher Account")
        
        col1, col2 = st.columns(2)
        with col1:
            teacher_name = st.text_input("Full Name", key="teacher_name")
            teacher_email = st.text_input("School Email Address", key="teacher_email")
        
        with col2:
            school_name = st.text_input("School Name", key="school_name")
            grade_level = st.selectbox("Grade Level", 
                                     ["Pre-K", "Kindergarten", "1st Grade", "2nd Grade", 
                                      "3rd Grade", "4th Grade", "5th Grade", "Mixed Grades"],
                                     key="grade_level")
        
        ambassador_program = st.checkbox("I'm interested in the Begin Teacher Ambassador program", key="ambassador_interest")
        
        if st.button("Create Teacher Account", key="create_teacher_btn", use_container_width=True):
            if teacher_name and teacher_email and validate_email(teacher_email):
                teacher_id = create_teacher_account(teacher_email, teacher_name, school_name, grade_level)
                if teacher_id:
                    # Retrieve the created teacher account
                    teacher = get_teacher_by_email(teacher_email)
                    st.session_state.teacher_user = teacher
                    st.success(f"Welcome to Begin Learning Profile, {teacher_name}! Your teacher account has been created.")
                    st.query_params["page"] = "teacher_dashboard"
                    st.rerun()
                else:
                    st.error("A teacher account with this email already exists. Please login instead.")
            else:
                st.error("Please fill in all required fields with valid information.")
    
    # Information section about the platform
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### For Teachers
        - **Understand each student from Day 1** with personalized learning profiles
        - **Save weeks of observation time** with instant insights
        - **Differentiate instruction** with specific classroom strategies
        - **Strengthen parent partnerships** through shared understanding
        """)
    
    with col2:
        st.markdown("""
        ### How It Works
        1. **Assign profiles** to parents during Back to School week
        2. **Parents complete** the 5-minute assessment at home
        3. **Receive insights** for both classroom and home learning
        4. **Collaborate** with parents using shared learning language
        """)

def teacher_dashboard_page():
    """Teacher dashboard for managing assignments and viewing results"""
    if not st.session_state.teacher_user:
        st.error("Please login as a teacher to access this page.")
        st.query_params["page"] = "teacher_register"
        st.rerun()
        return
    
    teacher = st.session_state.teacher_user
    
    # Header with teacher info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        # {teacher['name']}'s Dashboard
        **{teacher['school']} • {teacher['grade_level']}**
        """)
    
    with col2:
        if st.button("Logout", key="teacher_logout"):
            st.session_state.teacher_user = None
            st.query_params["page"] = "welcome"
            st.rerun()
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs(["📋 Assign Profiles", "📊 Student Results", "👥 Class Overview"])
    
    with tab1:
        st.markdown("### Assign Learning Profiles to Parents")
        
        # Bulk assignment form
        st.markdown("#### Add Student Assignments")
        
        col1, col2 = st.columns(2)
        with col1:
            parent_email = st.text_input("Parent Email", key="assign_parent_email")
            child_name = st.text_input("Student Name", key="assign_child_name")
        
        with col2:
            if st.button("Send Assignment", key="send_assignment_btn"):
                if parent_email and child_name and validate_email(parent_email):
                    # Generate unique assignment token
                    import secrets
                    assignment_token = secrets.token_urlsafe(32)
                    
                    assignment_id = create_assignment(teacher['id'], parent_email, child_name, assignment_token)
                    if assignment_id:
                        # Generate assignment URL
                        assignment_url = f"?token={assignment_token}"
                        
                        st.success(f"✅ Assignment sent to {parent_email} for {child_name}")
                        st.info(f"**Assignment Link:** {assignment_url}")
                        st.markdown("*Copy this link to send to the parent via email or school communication system.*")
                    else:
                        st.error("Failed to create assignment. Please try again.")
                else:
                    st.error("Please enter valid parent email and student name.")
        
        # Recent assignments
        st.markdown("#### Recent Assignments")
        assignments = get_teacher_assignments(teacher['id'], 10)
        
        if assignments:
            for assignment in assignments:
                status_emoji = "✅" if assignment['status'] == 'completed' else "⏳"
                status_color = "green" if assignment['status'] == 'completed' else "orange"
                
                with st.expander(f"{status_emoji} {assignment['child_name']} - {assignment['parent_email']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Status:** <span style='color: {status_color}'>{assignment['status'].title()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Assigned:** {assignment['assigned_at_formatted']}")
                        if assignment['completed_at']:
                            st.markdown(f"**Completed:** {assignment['completed_at_formatted']}")
                        if assignment['personality_label']:
                            st.markdown(f"**Learning Profile:** {assignment['personality_label']}")
                    
                    with col2:
                        if assignment['status'] == 'completed':
                            if st.button("View Results", key=f"view_results_{assignment['id']}"):
                                st.query_params["page"] = "teacher_results"
                                st.query_params["assignment_id"] = str(assignment['id'])
                                st.rerun()
        else:
            st.info("No assignments yet. Create your first assignment above!")
    
    with tab2:
        st.markdown("### Individual Student Results")
        
        completed_assignments = [a for a in get_teacher_assignments(teacher['id']) if a['status'] == 'completed']
        
        if completed_assignments:
            for assignment in completed_assignments:
                with st.expander(f"📊 {assignment['child_name']} - {assignment['personality_label']}", expanded=False):
                    st.markdown("*Teacher-specific insights coming soon!*")
                    st.markdown(f"**Learning Profile:** {assignment['personality_label']}")
                    st.markdown(f"**Completed:** {assignment['completed_at_formatted']}")
        else:
            st.info("No completed assessments yet. Assignments will appear here once parents complete them.")
    
    with tab3:
        st.markdown("### Class Learning Distribution")
        st.info("Class-wide analytics coming soon! This will show the distribution of learning styles across your classroom.")

def teacher_results_page():
    """Teacher-specific results view with classroom insights"""
    if not st.session_state.teacher_user:
        st.error("Please login as a teacher to access this page.")
        st.query_params["page"] = "teacher_register"
        st.rerun()
        return
    
    # Get assignment ID from URL params
    query_params = st.query_params
    assignment_id = query_params.get("assignment_id")
    
    if not assignment_id:
        st.error("No assignment specified.")
        st.query_params["page"] = "teacher_dashboard"
        st.rerun()
        return
    
    # Get the assignment and assessment data
    assignments = get_teacher_assignments(st.session_state.teacher_user['id'])
    assignment = next((a for a in assignments if str(a['id']) == assignment_id), None)
    
    if not assignment or assignment['status'] != 'completed':
        st.error("Assignment not found or not completed yet.")
        st.query_params["page"] = "teacher_dashboard"
        st.rerun()
        return
    
    # Get the assessment data
    try:
        assessment_data = get_previous_assessments(child_name=assignment['child_name'], limit=1)
        if not assessment_data:
            st.error("Assessment data not found.")
            return
        
        assessment = assessment_data[0]
        child_name = assessment['child_name']
        child_age = assessment['age']
        scores = assessment['scores']
        personality_label = assessment['personality_label']
        
        # Generate teacher insights
        teacher_insights = get_teacher_insights(scores, child_name, child_age)
        
    except Exception as e:
        st.error(f"Error loading assessment data: {str(e)}")
        return
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# {child_name}'s Classroom Learning Profile")
        st.markdown(f"**Age:** {child_age} • **Profile:** {personality_label}")
    
    with col2:
        if st.button("← Back to Dashboard", key="back_to_dashboard"):
            st.query_params["page"] = "teacher_dashboard"
            st.rerun()
    
    # Teacher-specific tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Classroom Behavior", 
        "📚 Teaching Strategies", 
        "🔄 Differentiation Plan",
        "👨‍👩‍👧‍👦 Parent Communication"
    ])
    
    with tab1:
        st.markdown("### Expected Classroom Behaviors")
        st.markdown(f"**{teacher_insights['behavior_summary']}**")
        
        # Learning profile visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Learning Strengths Map")
            try:
                fig = create_radar_chart(scores)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except:
                st.info("Chart not available")
        
        with col2:
            st.markdown("#### Focus Areas")
            
            strengths = [cat for cat, score in scores.items() if score == "High"]
            growth_areas = [cat for cat, score in scores.items() if score == "Low"]
            
            if strengths:
                st.markdown("**🌟 Strengths to Leverage:**")
                for strength in strengths:
                    st.markdown(f"• {strength}")
            
            if growth_areas:
                st.markdown("**🌱 Areas for Support:**")
                for area in growth_areas:
                    st.markdown(f"• {area}")
            
            # Seating suggestions
            st.markdown("**🪑 Seating Suggestions:**")
            for suggestion in teacher_insights['seating_suggestions']:
                st.markdown(f"• {suggestion}")
    
    with tab2:
        st.markdown("### Teaching Strategies by Learning Area")
        
        for category, level in scores.items():
            if category in teacher_insights['teaching_strategies']:
                strategies = teacher_insights['teaching_strategies'][category]
                
                with st.expander(f"{category} - {level} Level", expanded=(level == "High" or level == "Low")):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎯 Classroom Strategies:**")
                        for strategy in strategies['strategies']:
                            st.markdown(f"• {strategy}")
                        
                        st.markdown("**💡 Teaching Tips:**")
                        for tip in strategies['classroom_tips']:
                            st.markdown(f"• {tip}")
                    
                    with col2:
                        st.markdown("**🔄 Differentiation Ideas:**")
                        for diff in strategies['differentiation']:
                            st.markdown(f"• {diff}")
    
    with tab3:
        st.markdown("### Personalized Differentiation Plan")
        
        plan = teacher_insights['differentiation_plan']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌟 Leverage Strengths")
            for strategy in plan['leverage_strengths']:
                st.markdown(f"• {strategy}")
            
            st.markdown("#### 📚 Instructional Strategies")
            for strategy in plan['instructional_strategies']:
                st.markdown(f"• {strategy}")
        
        with col2:
            st.markdown("#### 🌱 Support Growth Areas")
            for strategy in plan['support_growth']:
                st.markdown(f"• {strategy}")
            
            st.markdown("#### 📋 Assessment Adaptations")
            for adaptation in teacher_insights['assessment_adaptations']:
                st.markdown(f"• {adaptation}")
        
        # Focus areas
        focus = teacher_insights['classroom_focus']
        
        st.markdown("### This Week's Focus")
        
        col1, col2 = st.columns(2)
        with col1:
            if 'primary_support_needed' in focus:
                st.markdown(f"**🎯 Primary Support:** {focus['primary_support_needed']}")
        
        with col2:
            if 'leverage_opportunity' in focus:
                st.markdown(f"**⚡ Leverage Opportunity:** {focus['leverage_opportunity']}")
        
        st.markdown(f"**📝 Weekly Goal:** {focus['weekly_goal']}")
    
    with tab4:
        st.markdown("### Parent Communication Toolkit")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 💬 Talking Points")
            st.markdown("*Use these points for parent conferences or check-ins:*")
            
            for point in teacher_insights['parent_talking_points']:
                st.markdown(f"• {point}")
        
        with col2:
            st.markdown("#### 🏠 Home-School Connection")
            st.markdown("*Suggestions for coordinated support:*")
            
            suggestions = [
                f"Share that {child_name} thrives when given opportunities to use their strengths",
                "Ask parents what learning activities work best at home",
                "Suggest family activities that align with classroom learning",
                "Coordinate on consistent approaches to building confidence",
                "Share specific examples of classroom successes to celebrate at home"
            ]
            
            for suggestion in suggestions:
                st.markdown(f"• {suggestion}")
        
        # Email template
        st.markdown("#### 📧 Parent Email Template")
        
        email_template = f"""
**Subject:** {child_name}'s Learning Profile - Great Insights to Share!

Dear {assignment['parent_email'].split('@')[0].title()},

I hope this message finds you well! I wanted to share some wonderful insights about {child_name}'s learning style based on the Begin Learning Profile you completed.

{teacher_insights['behavior_summary']}

I'm excited to use these insights to better support {child_name} in our classroom. I'd love to hear your thoughts and learn more about what you're seeing at home.

Would you be available for a brief chat this week to discuss how we can work together to support {child_name}'s continued growth?

Best regards,
{st.session_state.teacher_user['name']}
{st.session_state.teacher_user['school']}
        """
        
        st.text_area("Copy and customize this email template:", email_template.strip(), height=200)

def profile_dashboard_page():
    st.title("Your Child's Learning Profiles")
    
    # Show user email and logout option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Logged in as:** {st.session_state.user_email}")
    with col2:
        if st.button("Log Out", key="logout_button"):
            st.session_state.user_email = None
            st.session_state.previous_assessments = []
            # Use URL parameter for navigation
            st.query_params["page"] = "welcome"
            st.rerun()
            
    # Display previous assessments
    if not st.session_state.previous_assessments:
        st.warning("No assessments found. Create a new assessment to get started.")
    else:
        st.markdown("### Previous Assessments")
        
        for i, assessment in enumerate(st.session_state.previous_assessments):
            with st.expander(f"{assessment.get('child_name', 'Unnamed Child')} - {assessment.get('created_at_formatted', 'Unknown date')}", expanded=(i==0)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Age:** {assessment.get('age', 'Unknown')} years")
                    st.markdown(f"**Personality Label:** {assessment.get('personality_label', 'Unknown')}")
                    
                    # Show scores as bullet list
                    st.markdown("**Learning Profile:**")
                    scores = assessment.get('scores', {})
                    for category, level in scores.items():
                        emoji = "🌟" if level == "High" else "🌱" if level == "Medium" else "⭐"
                        st.markdown(f"- {emoji} **{category}:** {level}")
                
                with col2:
                    if st.button("View Full Report", key=f"view_report_{i}"):
                        # Load this assessment data into session state
                        st.session_state.child_info = {
                            "name": assessment.get('child_name'),
                            "age": assessment.get('age'),
                            "birth_month": assessment.get('birth_month'),
                            "birth_year": assessment.get('birth_year')
                        }
                        st.session_state.scores = assessment.get('scores')
                        # Use URL parameter for navigation
                        st.query_params["page"] = "results"
                        st.rerun()
    
    # Option to create a new assessment
    st.markdown("### Create New Assessment")
    if st.button("Start New Assessment", key="new_assessment", use_container_width=True):
        # Use URL parameter for navigation
        st.query_params["page"] = "welcome"
        st.rerun()

    # If they have assessments, show a progress chart
    if len(st.session_state.previous_assessments) >= 2:
        try:
            from utils.visualization import create_progress_chart
            st.markdown("### Learning Progress Over Time")
            progress_chart = create_progress_chart(st.session_state.previous_assessments)
            if progress_chart:
                st.plotly_chart(progress_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Could not display progress chart: {e}")

# URL-based navigation
def get_url_params():
    """Get URL parameters for navigation."""
    query_params = st.query_params
    
    # Default to welcome page if no page parameter
    page = query_params.get("page", "welcome")
    
    return page

def set_url_params(page):
    """Set URL parameters for navigation."""
    # Only update if the page has changed
    if st.query_params.get("page") != page:
        st.query_params["page"] = page
        if page != st.session_state.page:
            st.session_state.page = page

# Update session state based on URL
url_page = get_url_params()
if url_page != st.session_state.page:
    # Synchronize session state with URL
    st.session_state.page = url_page

# Check for assignment token in URL (parent access via teacher assignment)
query_params = st.query_params
assignment_token = query_params.get("token")
if assignment_token and not st.session_state.assignment_token:
    assignment = get_assignment_by_token(assignment_token)
    if assignment:
        st.session_state.assignment_token = assignment_token
        # Redirect to the appropriate page based on assignment status
        if st.session_state.page == "welcome":
            st.session_state.page = "quiz"

# Admin dashboard function
def admin_dashboard_page():
    """Admin dashboard to view usage statistics and database activity."""
    st.markdown('<div class="admin-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center;">Begin Learning Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Admin authentication - simple password protection
    if not st.session_state.get('admin_authenticated', False):
        st.markdown('<div class="admin-login">', unsafe_allow_html=True)
        st.subheader("Admin Login")
        admin_password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Simple password check - in a real app use more secure authentication
            if admin_password == "BeginAdmin2025":  # Replace with your preferred password
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Get admin statistics from database
    try:
        with st.spinner("Loading statistics..."):
            admin_stats = get_admin_statistics()
        
        if not admin_stats:
            st.error("Unable to retrieve admin statistics from the database.")
            if st.button("Return to Home"):
                st.session_state.page = 'welcome'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Dashboard layout with tabs
        tab1, tab2, tab3 = st.tabs(["Summary", "Recent Activity", "Data Export"])
        
        with tab1:
            st.subheader("Overview")
            # Key metrics in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Assessments", admin_stats['total_assessments'])
            
            with col2:
                st.metric("Unique Profiles", admin_stats['unique_children'])
            
            with col3:
                st.metric("Unique Accounts", admin_stats['unique_accounts'])
            
            # Activity chart
            st.subheader("Daily Activity (Last 14 Days)")
            if admin_stats['daily_assessments']:
                chart_data = pd.DataFrame(admin_stats['daily_assessments'])
                fig = px.bar(
                    chart_data, 
                    x='date', 
                    y='count',
                    labels={'count': 'Assessments', 'date': 'Date'},
                    title="Assessments Per Day"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent activity data available.")
        
        with tab2:
            st.subheader("Recent Assessments")
            if admin_stats['latest_assessments']:
                # Convert to DataFrame for better display
                recent_df = pd.DataFrame(admin_stats['latest_assessments'])
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("No recent assessments to display.")
        
        with tab3:
            st.subheader("Data Export")
            
            if admin_stats['all_assessments']:
                all_assessments_df = pd.DataFrame(admin_stats['all_assessments'])
                
                # Provide CSV download option
                csv = all_assessments_df.to_csv(index=False)
                current_date = datetime.now().strftime("%Y%m%d")
                
                st.download_button(
                    label="Download All Assessment Data (CSV)",
                    data=csv,
                    file_name=f"begin_learning_assessments_{current_date}.csv",
                    mime="text/csv"
                )
                
                st.dataframe(all_assessments_df, use_container_width=True)
            else:
                st.info("No assessment data available for export.")
        
        # Logout option
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
            
        # Return to home
        if st.button("Return to Home"):
            st.session_state.page = 'welcome'
            st.rerun()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
# Main app logic
if st.session_state.page == 'welcome':
    welcome_page()
    set_url_params('welcome')
elif st.session_state.page == 'quiz':
    quiz_page()
    set_url_params('quiz')
elif st.session_state.page == 'results':
    results_page()
    set_url_params('results')
elif st.session_state.page == 'profile_dashboard':
    profile_dashboard_page()
    set_url_params('profile_dashboard')
elif st.session_state.page == 'admin':
    admin_dashboard_page()
    set_url_params('admin')
elif st.session_state.page == 'teacher_register':
    teacher_register_page()
    set_url_params('teacher_register')
elif st.session_state.page == 'teacher_dashboard':
    teacher_dashboard_page()
    set_url_params('teacher_dashboard')
elif st.session_state.page == 'teacher_results':
    teacher_results_page()
    set_url_params('teacher_results')