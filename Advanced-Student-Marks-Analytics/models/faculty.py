from database.db import get_connection

import hashlib

class Faculty:
    @staticmethod
    def add_faculty(name):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO faculty (name) VALUES (?)", (name,))
            faculty_id = cur.lastrowid
            
            username = name.strip()
            # Basic fallback for empty/weird usernames, though UI usually catches it
            if not username: username = f"faculty_{faculty_id}"
            
            hashed_pw = hashlib.sha256('password123'.encode()).hexdigest()
            cur.execute(
                "INSERT INTO users (username, password_hash, role, linked_faculty_id) VALUES (?, ?, ?, ?)", 
                (username, hashed_pw, 'faculty', faculty_id)
            )
            
            conn.commit()
            return True, "Faculty added."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_all_faculty():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM faculty")
        result = cur.fetchall()
        conn.close()
        return result

    @staticmethod
    def assign_subject(faculty_id, subject_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO faculty_subjects (faculty_id, subject_id) VALUES (?, ?)", (faculty_id, subject_id))
            conn.commit()
            return True, "Subject assigned."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
            
    @staticmethod
    def get_faculty_subjects(faculty_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.subject_code, s.subject_name 
            FROM subjects s
            JOIN faculty_subjects fs ON s.id = fs.subject_id
            WHERE fs.faculty_id = ?
        """, (faculty_id,))
        result = cur.fetchall()
        conn.close()
        return result

    @staticmethod
    def delete_faculty(faculty_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM faculty WHERE id=?", (faculty_id,))
            cur.execute("DELETE FROM users WHERE linked_faculty_id=?", (faculty_id,))
            cur.execute("DELETE FROM faculty_subjects WHERE faculty_id=?", (faculty_id,))
            conn.commit()
            return True, "Faculty deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
