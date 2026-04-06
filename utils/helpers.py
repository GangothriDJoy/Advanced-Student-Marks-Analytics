from config.settings import GRADE_POINTS

def marks_to_grade(marks):
    if marks >= 90: return 'O'
    elif marks >= 85: return 'A+'
    elif marks >= 80: return 'A'
    elif marks >= 70: return 'B+'
    elif marks >= 60: return 'B'
    elif marks >= 50: return 'C'
    elif marks >= 40: return 'P'
    else: return 'F'

def grade_to_marks(grade):
    grade = str(grade).strip().upper()
    mapping = {
        'O': 95, 'S': 95, 'A+': 87, 'A': 82, 'B+': 75, 'B': 65, 'C': 55, 'P': 42, 'F': 30, 'FE': 0, 'I': 0
    }
    return mapping.get(grade, 0)

def calculate_sgpa(subject_marks_credits):
    """
    Calculates SGPA.
    Expects a list of tuples: (marks, credits)
    """
    total_credits = 0
    earned_points = 0
    for marks, creds in subject_marks_credits:
        grade = marks_to_grade(marks)
        point = GRADE_POINTS.get(grade, 0)
        earned_points += point * creds
        total_credits += creds
        
    if total_credits == 0: 
        return 0.0
    return round(earned_points / total_credits, 2)
