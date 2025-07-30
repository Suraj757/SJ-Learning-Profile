import streamlit as st
import json
from datetime import datetime

@st.cache_resource
def get_db_connection():
    """Get a connection to the SQLite database using st.connection."""
    try:
        return st.connection('learningprofile', type='sql', url='sqlite:///learning_profiles.db')
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize the SQLite database schema."""
    conn = get_db_connection()
    if not conn:
        st.warning("No database connection available, skipping initialization.")
        return False
    
    try:
        # Create assessment results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assessment_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_name TEXT,
                age INTEGER,
                scores TEXT,
                personality_label TEXT,
                raw_responses TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                birth_month INTEGER,
                birth_year INTEGER
            )
        """)

        # Create teachers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                school TEXT,
                grade_level TEXT,
                ambassador_status BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create profile assignments table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
                parent_email TEXT NOT NULL,
                child_name TEXT,
                assignment_token TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'sent',
                assessment_id INTEGER REFERENCES assessment_results(id) ON DELETE SET NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Create indexes for profile assignments
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_token ON profile_assignments(assignment_token)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_parent_email ON profile_assignments(parent_email)")
        
        return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

def save_assessment_result(child_name, age, scores, personality_label, raw_responses, email, birth_month, birth_year):
    """Save an assessment result to the database."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        result = conn.execute("""
            INSERT INTO assessment_results 
            (child_name, age, scores, personality_label, raw_responses, email, birth_month, birth_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [child_name, age, json.dumps(scores), personality_label, json.dumps(raw_responses), email, birth_month, birth_year])
        
        return result.lastrowid
    except Exception as e:
        st.error(f"Error saving assessment result: {e}")
        return None

def get_previous_assessments(email=None, child_name=None, limit=50):
    """Get previous assessments by email or child name."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        if email:
            df = conn.query("SELECT *, datetime(created_at) as created_at_formatted FROM assessment_results WHERE email = ? ORDER BY created_at DESC LIMIT ?", params=[email, limit])
        elif child_name:
            df = conn.query("SELECT *, datetime(created_at) as created_at_formatted FROM assessment_results WHERE child_name = ? ORDER BY created_at DESC LIMIT ?", params=[child_name, limit])
        else:
            return []
        
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error retrieving assessments: {e}")
        return []

def create_teacher_account(email, name, school=None, grade_level=None):
    """Create a new teacher account."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        result = conn.execute("INSERT INTO teachers (email, name, school, grade_level) VALUES (?, ?, ?, ?)",
                    [email, name, school, grade_level])
        return result.lastrowid
    except Exception as e:
        # Teacher already exists or other error
        st.error(f"Error creating teacher account: {e}")
        return None

def get_teacher_by_email(email):
    """Get teacher information by email."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        df = conn.query("SELECT * FROM teachers WHERE email = ?", params=[email])
        return df.iloc[0].to_dict() if len(df) > 0 else None
    except Exception as e:
        st.error(f"Error retrieving teacher: {e}")
        return None

def create_assignment(teacher_id, parent_email, child_name, assignment_token):
    """Create a new profile assignment."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        result = conn.execute("INSERT INTO profile_assignments (teacher_id, parent_email, child_name, assignment_token) VALUES (?, ?, ?, ?)",
                    [teacher_id, parent_email, child_name, assignment_token])
        return result.lastrowid
    except Exception as e:
        st.error(f"Error creating assignment: {e}")
        return None

def get_assignment_by_token(assignment_token):
    """Get assignment information by token."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        df = conn.query("""
            SELECT pa.*, t.name as teacher_name, t.school, t.grade_level
            FROM profile_assignments pa
            JOIN teachers t ON pa.teacher_id = t.id
            WHERE pa.assignment_token = ?
        """, params=[assignment_token])
        return df.iloc[0].to_dict() if len(df) > 0 else None
    except Exception as e:
        st.error(f"Error retrieving assignment: {e}")
        return None

def get_teacher_assignments(teacher_id, limit=50):
    """Get all assignments for a teacher."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        df = conn.query("""
            SELECT pa.*, ar.personality_label,
                   datetime(pa.assigned_at) as assigned_at_formatted,
                   datetime(pa.completed_at) as completed_at_formatted
            FROM profile_assignments pa
            LEFT JOIN assessment_results ar ON pa.assessment_id = ar.id
            WHERE pa.teacher_id = ?
            ORDER BY pa.assigned_at DESC
            LIMIT ?
        """, params=[teacher_id, limit])
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error retrieving teacher assignments: {e}")
        return []

def complete_assignment(assignment_token, assessment_id):
    """Mark an assignment as completed."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        result = conn.execute("""
            UPDATE profile_assignments 
            SET status = 'completed', assessment_id = ?, completed_at = CURRENT_TIMESTAMP
            WHERE assignment_token = ?
        """, [assessment_id, assignment_token])
        return result.rowcount > 0
    except Exception as e:
        st.error(f"Error completing assignment: {e}")
        return False
            
def get_admin_statistics():
    """Get basic admin statistics."""
    conn = get_db_connection()
    if not conn:
        return {
            'total_assessments': 0,
            'total_teachers': 0,
            'total_assignments': 0,
            'daily_activity': []
        }
    
    try:
        total_assessments = conn.query("SELECT COUNT(*) as count FROM assessment_results").iloc[0]['count']
        total_teachers = conn.query("SELECT COUNT(*) as count FROM teachers").iloc[0]['count']
        total_assignments = conn.query("SELECT COUNT(*) as count FROM profile_assignments").iloc[0]['count']
        
        return {
            'total_assessments': total_assessments,
            'total_teachers': total_teachers,
            'total_assignments': total_assignments,
            'daily_activity': []  # Simplified for now
        }
    except Exception as e:
        st.error(f"Error getting admin statistics: {e}")
        return {
            'total_assessments': 0,
            'total_teachers': 0,
            'total_assignments': 0,
            'daily_activity': []
        }