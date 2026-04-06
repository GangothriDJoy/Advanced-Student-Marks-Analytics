import pandas as pd
from database.db import get_connection
from config.settings import RISK_THRESHOLD_SGPA

class AnalyticsService:
    @staticmethod
    def get_full_dataframe():
        conn = get_connection()
        query = """
            SELECT st.id as student_id, st.roll_no, st.name as student_name, st.current_semester, 
                   st.risk_category, su.subject_code, su.subject_name, su.credits, 
                   m.semester, m.marks, m.grade,
                   c.sgpa, c.cgpa
            FROM marks m
            JOIN students st ON m.student_id = st.id
            JOIN subjects su ON m.subject_id = su.id
            LEFT JOIN cgpa_tracking c ON c.student_id = st.id AND c.semester = m.semester
        """
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Database Analytics Warning: {e}")
            df = pd.DataFrame()
        finally:
            conn.close()
            
        return df


    @staticmethod
    def identify_at_risk_students(df=None):
        if df is None:
            df = AnalyticsService.get_full_dataframe()
        if df.empty: return []
        
        risk_list = []
        # Grouping by name instead of ID just for simplistic representation
        students = df.groupby('student_name')
        for name, group in students:
            fails = len(group[group['marks'] < 40])
            sgpa_series = group['sgpa'].dropna().unique()
            min_sgpa = min(sgpa_series) if len(sgpa_series) > 0 else 10.0
            
            risk = "Safe"
            if fails >= 2 or min_sgpa < RISK_THRESHOLD_SGPA:
                risk = "High Risk"
            elif fails == 1 or min_sgpa < (RISK_THRESHOLD_SGPA + 1.0):
                risk = "Moderate Risk"
                
            risk_list.append({'name': name, 'fails': fails, 'lowest_sgpa': min_sgpa, 'risk': risk})
            
        return risk_list

    @staticmethod
    def calculate_subject_difficulty(df=None):
        if df is None:
            df = AnalyticsService.get_full_dataframe()
        if df.empty: return {}
        
        difficulty = {}
        subjects = df.groupby('subject_name')
        for subj, group in subjects:
            total = len(group)
            fails = len(group[group['marks'] < 40])
            avg_marks = group['marks'].mean()
            pass_percent = ((total - fails) / total) * 100 if total > 0 else 0
            
            # Difficulty Score heuristic
            diff_score = (100 - pass_percent) * 0.6 + (100 - avg_marks) * 0.4
            difficulty[subj] = {
                'pass_percent': round(pass_percent, 2),
                'avg_marks': round(avg_marks, 2),
                'difficulty_score': round(diff_score, 2),
                'classification': 'Most Difficult' if diff_score > 60 else ('Moderate' if diff_score > 30 else 'Easiest')
            }
        return difficulty

    @staticmethod
    def evaluate_faculty_performance(df=None):
        if df is None:
            conn = get_connection()
            query = """
                SELECT f.name as faculty_name, s.subject_name, m.marks
                FROM faculty f
                JOIN faculty_subjects fs ON f.id = fs.faculty_id
                JOIN subjects s ON fs.subject_id = s.id
                JOIN marks m ON s.id = m.subject_id
            """
            try:
                df = pd.read_sql_query(query, conn)
            except Exception as e:
                print(f"Database Analytics Warning: {e}")
                df = pd.DataFrame()
            finally:
                conn.close()
            
        if df.empty: return {}
        
        insights = {}
        for fac_name, group in df.groupby('faculty_name'):
            total = len(group)
            fails = len(group[group['marks'] < 40])
            avg = group['marks'].mean()
            insights[fac_name] = {
                'subjects': list(group['subject_name'].unique()),
                'average': round(avg, 2),
                'pass_percent': round(((total - fails)/total)*100, 2)
            }
        return insights
