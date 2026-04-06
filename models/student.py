from database.db import get_connection

class Student:
    @staticmethod
    def add_student(roll_no, name, semester=1, faculty_id=None):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO students (roll_no, name, current_semester, faculty_id) VALUES (?, ?, ?, ?)", 
                        (roll_no, name, semester, faculty_id))
            conn.commit()
            return True, "Student added successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def evaluate_and_update_risk(student_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM marks WHERE student_id=? AND marks < 40", (student_id,))
            fails = cur.fetchone()[0]
            
            risk = 'Safe'
            if fails >= 3:
                risk = 'High Risk'
            elif fails >= 1:
                risk = 'Moderate Risk'
                
            cur.execute("UPDATE students SET risk_category=? WHERE id=?", (risk, student_id))
            conn.commit()
            return risk
        except Exception as e:
            pass
        finally:
            conn.close()

    @staticmethod
    def get_all_students(faculty_id=None):
        conn = get_connection()
        cur = conn.cursor()
        if faculty_id is not None:
            cur.execute("SELECT * FROM students WHERE faculty_id=?", (faculty_id,))
        else:
            cur.execute("SELECT * FROM students")
        result = cur.fetchall()
        conn.close()
        return result

    @staticmethod
    def update_student(student_id, roll_no, name, semester, faculty_id=None):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE students SET roll_no=?, name=?, current_semester=?, faculty_id=? WHERE id=?", 
                        (roll_no, name, semester, faculty_id, student_id))
            conn.commit()
            return True, "Student updated."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_student(student_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
            return True, "Student deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
