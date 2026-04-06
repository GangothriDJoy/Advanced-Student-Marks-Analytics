from database.db import get_connection

class Subject:
    @staticmethod
    def add_subject(subject_code, subject_name, credits):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO subjects (subject_code, subject_name, credits) VALUES (?, ?, ?)", 
                        (subject_code, subject_name, credits))
            conn.commit()
            return True, "Subject added."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_all_subjects():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM subjects")
        result = cur.fetchall()
        conn.close()
        return result

    @staticmethod
    def update_subject(subject_id, subject_code, subject_name, credits):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE subjects SET subject_code=?, subject_name=?, credits=? WHERE id=?", 
                        (subject_code, subject_name, credits, subject_id))
            conn.commit()
            return True, "Subject updated."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete_subject(subject_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
            conn.commit()
            return True, "Subject deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
