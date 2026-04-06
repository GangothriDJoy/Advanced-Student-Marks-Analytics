import sqlite3
import hashlib
import os

DB_PATH = 'student_analytics.db'
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_connection():
    # Enable foreign keys for CASCADE deletes
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Execute the SQL schema
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())
        
    # Auto-migrate: Add role and linked_faculty_id to users if they don't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'admin'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN linked_faculty_id INTEGER")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN faculty_id INTEGER")
    except sqlite3.OperationalError:
        pass # Column already exists
    
    # Insert default admin if not exists (admin / admin123)
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
            ('admin', hashed_pw, 'admin')
        )
    
    conn.commit()
    conn.close()
