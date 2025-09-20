# auth.py
import sqlite3
import hashlib

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    
    # Users table without 'name'
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY, title TEXT, company TEXT, department TEXT, 
                 requirements TEXT, description TEXT, created_at TIMESTAMP)''')
    
    # Applications table
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY, user_id INTEGER, job_id INTEGER, 
                 resume_data BLOB, applied_at TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(id),
                 FOREIGN KEY(job_id) REFERENCES jobs(id))''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user by username and password"""
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def register_user(username, password, role):
    """Register a new user"""
    try:
        conn = sqlite3.connect('recruitment.db')
        c = conn.cursor()
        hashed_password = hash_password(password)
        
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed_password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
