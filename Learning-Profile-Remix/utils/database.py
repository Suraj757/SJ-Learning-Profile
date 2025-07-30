import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Create a database connection using environment variables."""
    if 'DATABASE_URL' not in os.environ:
        print("DATABASE_URL not found in environment")
        return None
    try:
        return psycopg2.connect(os.environ['DATABASE_URL'])
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    if not conn:
        print("No database connection available, skipping initialization")
        return False

    cur = conn.cursor()
    try:
        # Check if table exists first
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'assessment_results'
            );
        """)
        result = cur.fetchone()
        table_exists = result[0] if result else False
        
        if not table_exists:
            # Create assessment_results table with version tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS assessment_results (
                    id SERIAL PRIMARY KEY,
                    child_name VARCHAR(100),
                    age INTEGER,
                    birth_month INTEGER,
                    birth_year INTEGER,
                    email VARCHAR(255),
                    scores JSONB,
                    personality_label VARCHAR(100),
                    raw_responses JSONB,
                    version INTEGER DEFAULT 1,
                    source VARCHAR(50) DEFAULT 'parent',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Database table created successfully")
        else:
            # Check if version and source columns exist
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'assessment_results' AND column_name = 'version'
                );
            """)
            result = cur.fetchone()
            has_version = result[0] if result else False
            
            if not has_version:
                # Add version column
                cur.execute("""
                    ALTER TABLE assessment_results 
                    ADD COLUMN version INTEGER DEFAULT 1,
                    ADD COLUMN source VARCHAR(50) DEFAULT 'parent'
                """)
                conn.commit()
                print("Database schema updated with version tracking")
        
        # Create teachers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                school VARCHAR(100),
                grade_level VARCHAR(50),
                ambassador_status BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create profile assignments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profile_assignments (
                id SERIAL PRIMARY KEY,
                teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
                parent_email VARCHAR(255) NOT NULL,
                child_name VARCHAR(100),
                assignment_token VARCHAR(255) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'sent',
                assessment_id INTEGER REFERENCES assessment_results(id) ON DELETE SET NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Create indexes for profile assignments
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_assignments_token 
            ON profile_assignments(assignment_token)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_assignments_parent_email 
            ON profile_assignments(parent_email)
        """)
        
        conn.commit()
            
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def save_assessment_result(child_name, age, scores, personality_label, raw_responses, email=None, birth_month=None, birth_year=None, source="parent"):
    """Save assessment results to database and return result ID if successful."""
    conn = get_db_connection()
    if not conn:
        print("No database connection available, skipping result save")
        return None

    cur = conn.cursor()
    try:
        # Check if a previous assessment exists for this child
        version = 1
        if child_name:
            cur.execute("""
                SELECT MAX(version) FROM assessment_results WHERE child_name = %s
            """, (child_name,))
            result = cur.fetchone()
            if result and result[0]:
                version = result[0] + 1
        
        # Insert new assessment with version
        cur.execute("""
            INSERT INTO assessment_results 
            (child_name, age, birth_month, birth_year, email, scores, personality_label, raw_responses, version, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            child_name,
            age,
            birth_month,
            birth_year,
            email,
            json.dumps(scores),
            personality_label,
            json.dumps(raw_responses),
            version,
            source
        ))
        result = cur.fetchone()
        result_id = result[0] if result else None
        conn.commit()
        print(f"Successfully saved assessment result with ID: {result_id}, version: {version}")
        return result_id
    except Exception as e:
        print(f"Error saving assessment result: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def get_previous_assessments(child_name=None, email=None, limit=5):
    """Get previous assessments for a child or email."""
    try:
        conn = get_db_connection()
        if not conn:
            print("No database connection available, skipping retrieval")
            return []

        cur = conn.cursor()
        try:
            # Check if table exists first
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'assessment_results'
                );
            """)
            result = cur.fetchone()
            if not result or not result[0]:
                print("Assessment table does not exist")
                return []
            
            # Simple query that works with any schema version
            query = """
                SELECT id, child_name, age, birth_month, birth_year, email,
                    scores, personality_label, created_at
                FROM assessment_results
                WHERE 1=1
            """
            
            params = []
            
            if child_name:
                query += " AND child_name = %s"
                params.append(child_name)
                
            if email:
                query += " AND email = %s"
                params.append(email)
                
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cur.execute(query, params)
            rows = cur.fetchall()
            
            # Convert results to list of dictionaries
            assessments = []
            for row in rows:
                # Create a dictionary from row data
                assessment = {
                    "id": row[0],
                    "child_name": row[1],
                    "age": row[2],
                    "birth_month": row[3],
                    "birth_year": row[4],
                    "email": row[5],
                    "scores": json.loads(row[6]) if isinstance(row[6], str) else row[6] if row[6] else {},
                    "personality_label": row[7],
                    "created_at": row[8],
                    # Default values for backward compatibility
                    "version": 1,
                    "source": "parent"
                }
                
                # Format date for display
                if assessment["created_at"]:
                    assessment["created_at_formatted"] = assessment["created_at"].strftime('%B %d, %Y')
                
                assessments.append(assessment)
                
            return assessments
        except Exception as e:
            print(f"Error retrieving assessment history: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    except Exception as e:
        print(f"Database connection error in get_previous_assessments: {e}")
        return []

def get_admin_statistics():
    """Get statistics for admin dashboard."""
    try:
        conn = get_db_connection()
        if not conn:
            print("No database connection available, skipping statistics retrieval")
            return None

        cur = conn.cursor()
        try:
            stats = {}
            
            # Total number of assessments
            cur.execute("SELECT COUNT(*) FROM assessment_results")
            result = cur.fetchone()
            stats['total_assessments'] = result[0] if result else 0
            
            # Unique children
            cur.execute("SELECT COUNT(DISTINCT child_name) FROM assessment_results WHERE child_name IS NOT NULL")
            result = cur.fetchone()
            stats['unique_children'] = result[0] if result else 0
            
            # Unique emails (accounts)
            cur.execute("SELECT COUNT(DISTINCT email) FROM assessment_results WHERE email IS NOT NULL")
            result = cur.fetchone()
            stats['unique_accounts'] = result[0] if result else 0
            
            # Assessments per day (last 14 days)
            cur.execute("""
                SELECT 
                    DATE(created_at) as date, 
                    COUNT(*) as count
                FROM 
                    assessment_results
                WHERE 
                    created_at >= NOW() - INTERVAL '14 days'
                GROUP BY 
                    DATE(created_at)
                ORDER BY 
                    date ASC
            """)
            rows = cur.fetchall()
            stats['daily_assessments'] = [{'date': row[0].strftime('%Y-%m-%d'), 'count': row[1]} for row in rows]
            
            # Latest assessments
            cur.execute("""
                SELECT 
                    id, child_name, email, created_at
                FROM 
                    assessment_results
                ORDER BY 
                    created_at DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
            stats['latest_assessments'] = [
                {
                    'id': row[0],
                    'child_name': row[1] if row[1] else 'Unnamed',
                    'email': row[2] if row[2] else 'No Email',
                    'created_at': row[3].strftime('%Y-%m-%d %H:%M:%S')
                } 
                for row in rows
            ]
            
            # Get all assessments data for download
            cur.execute("""
                SELECT 
                    id, child_name, age, email, personality_label, 
                    version, source, created_at
                FROM 
                    assessment_results
                ORDER BY 
                    created_at DESC
            """)
            rows = cur.fetchall()
            stats['all_assessments'] = [
                {
                    'id': row[0],
                    'child_name': row[1] if row[1] else 'Unnamed',
                    'age': row[2],
                    'email': row[3] if row[3] else 'No Email',
                    'personality_label': row[4],
                    'version': row[5] if row[5] else 1,
                    'source': row[6] if row[6] else 'parent',
                    'created_at': row[7].strftime('%Y-%m-%d %H:%M:%S')
                } 
                for row in rows
            ]
            
            return stats
        except Exception as e:
            print(f"Error retrieving admin statistics: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    except Exception as e:
        print(f"Database connection error in get_admin_statistics: {e}")
        return None

# Teacher management functions
def create_teacher_account(email, name, school=None, grade_level=None):
    """Create a new teacher account."""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO teachers (email, name, school, grade_level)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, name, school, grade_level))
        result = cur.fetchone()
        teacher_id = result[0] if result else None
        conn.commit()
        return teacher_id
    except psycopg2.IntegrityError:
        conn.rollback()
        return None  # Teacher already exists
    except Exception as e:
        print(f"Error creating teacher account: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def get_teacher_by_email(email):
    """Get teacher information by email."""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, email, name, school, grade_level, ambassador_status, created_at
            FROM teachers
            WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'school': row[3],
                'grade_level': row[4],
                'ambassador_status': row[5],
                'created_at': row[6]
            }
        return None
    except Exception as e:
        print(f"Error retrieving teacher: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def create_assignment(teacher_id, parent_email, child_name, assignment_token):
    """Create a new profile assignment."""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO profile_assignments (teacher_id, parent_email, child_name, assignment_token)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (teacher_id, parent_email, child_name, assignment_token))
        result = cur.fetchone()
        assignment_id = result[0] if result else None
        conn.commit()
        return assignment_id
    except Exception as e:
        print(f"Error creating assignment: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def get_assignment_by_token(assignment_token):
    """Get assignment information by token."""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT pa.id, pa.teacher_id, pa.parent_email, pa.child_name, 
                   pa.status, pa.assessment_id, pa.assigned_at, pa.completed_at,
                   t.name as teacher_name, t.school, t.grade_level
            FROM profile_assignments pa
            JOIN teachers t ON pa.teacher_id = t.id
            WHERE pa.assignment_token = %s
        """, (assignment_token,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'teacher_id': row[1],
                'parent_email': row[2],
                'child_name': row[3],
                'status': row[4],
                'assessment_id': row[5],
                'assigned_at': row[6],
                'completed_at': row[7],
                'teacher_name': row[8],
                'school': row[9],
                'grade_level': row[10]
            }
        return None
    except Exception as e:
        print(f"Error retrieving assignment: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def get_teacher_assignments(teacher_id, limit=50):
    """Get all assignments for a teacher."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT pa.id, pa.parent_email, pa.child_name, pa.status, 
                   pa.assigned_at, pa.completed_at, ar.personality_label
            FROM profile_assignments pa
            LEFT JOIN assessment_results ar ON pa.assessment_id = ar.id
            WHERE pa.teacher_id = %s
            ORDER BY pa.assigned_at DESC
            LIMIT %s
        """, (teacher_id, limit))
        rows = cur.fetchall()
        assignments = []
        for row in rows:
            assignment = {
                'id': row[0],
                'parent_email': row[1],
                'child_name': row[2],
                'status': row[3],
                'assigned_at': row[4],
                'completed_at': row[5],
                'personality_label': row[6]
            }
            if assignment['assigned_at']:
                assignment['assigned_at_formatted'] = assignment['assigned_at'].strftime('%B %d, %Y')
            if assignment['completed_at']:
                assignment['completed_at_formatted'] = assignment['completed_at'].strftime('%B %d, %Y')
            assignments.append(assignment)
        return assignments
    except Exception as e:
        print(f"Error retrieving teacher assignments: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def complete_assignment(assignment_token, assessment_id):
    """Mark an assignment as completed."""
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE profile_assignments 
            SET status = 'completed', assessment_id = %s, completed_at = CURRENT_TIMESTAMP
            WHERE assignment_token = %s
        """, (assessment_id, assignment_token))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"Error completing assignment: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()