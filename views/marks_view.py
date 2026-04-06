import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from models.student import Student
from models.subject import Subject
from models.marks import Marks

class MarksView(tb.Frame):
    def __init__(self, parent, faculty_id=None):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self.students = Student.get_all_students(faculty_id)
        
        if faculty_id:
            from models.faculty import Faculty
            self.subjects = Faculty.get_faculty_subjects(faculty_id)
        else:
            self.subjects = Subject.get_all_subjects()
        
        self.student_dict = {f"{s[1]} - {s[2]}": s[0] for s in self.students}
        self.subject_dict = {s[1]: s[0] for s in self.subjects}
        
        self.create_widgets()
        
    def create_widgets(self):
        top_frame = tb.Frame(self)
        top_frame.pack(fill=X, pady=10)
        
        tb.Label(top_frame, text="Select Student:", font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.student_combo = tb.Combobox(top_frame, values=list(self.student_dict.keys()), state="readonly", width=35, bootstyle="primary")
        self.student_combo.grid(row=0, column=1, padx=5, pady=5)
        self.student_combo.bind("<<ComboboxSelected>>", self.load_student_marks)
        
        form_frame = tb.Labelframe(self, text="Add/Update Marks", padding=15, bootstyle="info")
        form_frame.pack(fill=X, pady=15)
        
        tb.Label(form_frame, text="Semester:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.sem_var = tb.StringVar(value="1")
        tb.Entry(form_frame, textvariable=self.sem_var, width=5, font=("Helvetica", 10)).grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_frame, text="Subject:", font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.subject_combo = tb.Combobox(form_frame, values=list(self.subject_dict.keys()), state="readonly", bootstyle="primary")
        self.subject_combo.grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_frame, text="Marks (0-100):", font=("Helvetica", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.marks_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.marks_var, width=15, font=("Helvetica", 10)).grid(row=0, column=5, padx=5, pady=5)
        
        tb.Button(form_frame, text="Save Marks", command=self.save_marks, bootstyle="success").grid(row=0, column=6, padx=15)
        tb.Button(form_frame, text="View All Class Marks", command=self.view_all_marks, bootstyle="info").grid(row=0, column=7, padx=15)
        
        columns = ("ID", "Subject", "Marks", "Grade", "Semester")
        self.tree = tb.Treeview(self, columns=columns, show="headings", bootstyle="primary")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=BOTH, expand=True)
        
    def load_student_marks(self, event=None):
        student_str = self.student_combo.get()
        if not student_str:
            return
            
        student_id = self.student_dict[student_str]
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        marks = Marks.get_marks_for_student(student_id)
        for m in marks:
            # marks from db: m.id, s.subject_code, s.subject_name, m.marks, m.grade, m.semester
            self.tree.insert("", END, values=(m[0], f"{m[1]} - {m[2]}", m[3], m[4], m[5]))
            
    def save_marks(self):
        student_str = self.student_combo.get()
        subject_str = self.subject_combo.get()
        marks_str = self.marks_var.get()
        sem_str = self.sem_var.get()
        
        if not student_str or not subject_str or not marks_str or not sem_str:
            Messagebox.show_warning("All fields required.", "Error")
            return
            
        try:
            marks = int(marks_str)
            sem = int(sem_str)
            if not (0 <= marks <= 100):
                raise ValueError
        except ValueError:
            Messagebox.show_error("Marks must be between 0 and 100 and semester numeric.", "Error")
            return
            
        student_id = self.student_dict[student_str]
        subject_id = self.subject_dict[subject_str]
        
        success, msg = Marks.add_or_update_marks(student_id, subject_id, sem, marks)
        if success:
            self.load_student_marks()
            self.marks_var.set("")
        else:
            Messagebox.show_error(msg, "Error")

    def view_all_marks(self):
        win = tb.Toplevel(title="All Students Marks")
        win.geometry("700x500")
        
        columns = ("Roll No", "Name", "Subject", "Marks", "Grade", "Semester")
        tree = tb.Treeview(win, columns=columns, show="headings", bootstyle="primary")
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        for s in self.students:
            student_id = s[0]
            student_roll = s[1]
            student_name = s[2]
            
            marks = Marks.get_marks_for_student(student_id)
            for m in marks:
                tree.insert("", END, values=(student_roll, student_name, f"{m[1]} - {m[2]}", m[3], m[4], m[5]))
