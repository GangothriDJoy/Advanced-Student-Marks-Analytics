from database.db import get_connection
from utils.helpers import marks_to_grade

class Marks:
    @staticmethod
    def add_or_update_marks(student_id, subject_id, semester, marks):
        grade = marks_to_grade(marks)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM marks WHERE student_id=? AND subject_id=? AND semester=?", 
                        (student_id, subject_id, semester))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE marks SET marks=?, grade=? WHERE id=?", (marks, grade, row[0]))
            else:
                cur.execute("INSERT INTO marks (student_id, subject_id, semester, marks, grade) VALUES (?, ?, ?, ?, ?)", 
                            (student_id, subject_id, semester, marks, grade))
            conn.commit()
            
            from models.student import Student
            Student.evaluate_and_update_risk(student_id)
            
            return True, "Marks saved successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_marks_for_student(student_id, semester=None):
        conn = get_connection()
        cur = conn.cursor()
        if semester:
            cur.execute("""
                SELECT m.id, s.subject_code, s.subject_name, m.marks, m.grade, m.semester
                FROM marks m 
                JOIN subjects s ON m.subject_id = s.id 
                WHERE m.student_id = ? AND m.semester = ?
            """, (student_id, semester))
        else:
            cur.execute("""
                SELECT m.id, s.subject_code, s.subject_name, m.marks, m.grade, m.semester
                FROM marks m 
                JOIN subjects s ON m.subject_id = s.id 
                WHERE m.student_id = ?
                ORDER BY m.semester ASC
            """, (student_id,))
        result = cur.fetchall()
        conn.close()
        return result
