# database.py
import sqlite3
from datetime import datetime

# --- Your existing init_db() ---
def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')

    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY, title TEXT, company TEXT, department TEXT, 
                 requirements TEXT, description TEXT, created_at TIMESTAMP)''')

    # Applications table (status column may not exist yet)
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY, user_id INTEGER, job_id INTEGER, 
                 resume_data BLOB, applied_at TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(id),
                 FOREIGN KEY(job_id) REFERENCES jobs(id))''')

    conn.commit()
    conn.close()


# --- ADD THIS FUNCTION AFTER init_db() ---
def add_status_column_if_missing():
    """Add 'status' column to applications if it doesn't exist yet"""
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    
    # Check if 'status' column exists
    c.execute("PRAGMA table_info(applications)")
    columns = [col[1] for col in c.fetchall()]
    if "status" not in columns:
        c.execute("ALTER TABLE applications ADD COLUMN status TEXT DEFAULT 'Pending'")
        conn.commit()
    
    conn.close()


# --- Call it once after initializing DB ---
init_db()
add_status_column_if_missing()


# --- Your existing functions below ---
def create_job_posting(title, company, department, requirements, description):
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("INSERT INTO jobs (title, company, department, requirements, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                 (title, company, department, requirements, description, datetime.now()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error creating job posting: {e}")
        return False


def get_job_postings():
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        jobs = c.fetchall()
        conn.close()
        return jobs
    except sqlite3.Error as e:
        print(f"Error fetching job postings: {e}")
        return []


def submit_application(user_id, job_id, resume_file):
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("INSERT INTO applications (user_id, job_id, resume_data, applied_at) VALUES (?, ?, ?, ?)",
                 (user_id, job_id, resume_file.read(), datetime.now()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error submitting application: {e}")
        return False


def get_applications():
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute('''SELECT applications.id, users.username, jobs.title, applications.applied_at, 
                     applications.resume_data, jobs.company, jobs.requirements, applications.status
                     FROM applications 
                     JOIN users ON applications.user_id = users.id
                     JOIN jobs ON applications.job_id = jobs.id
                     ORDER BY applications.applied_at DESC''')
        applications = c.fetchall()
        conn.close()
        return applications
    except sqlite3.Error as e:
        print(f"Error fetching applications: {e}")
        return []


def update_application_status(application_id, status):
    """Mark an application as Hired or Not Hired"""
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        c.execute("UPDATE applications SET status=? WHERE id=?", (status, application_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error updating status: {e}")
        return False
