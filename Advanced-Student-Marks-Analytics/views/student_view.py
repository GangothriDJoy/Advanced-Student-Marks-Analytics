import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from models.student import Student
from models.faculty import Faculty

class StudentView(tb.Frame):
    def __init__(self, parent, faculty_id=None):
        super().__init__(parent)
        self.parent = parent
        self.faculty_id = faculty_id
        
        # Load faculty mappings for Admin use
        self.faculties = Faculty.get_all_faculty()
        self.faculty_dict = {f"{f[1]}": f[0] for f in self.faculties}
        
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        form_frame = tb.Frame(self)
        form_frame.pack(fill=X, pady=10)
        
        tb.Label(form_frame, text="Roll No:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.roll_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.roll_var, font=("Helvetica", 10), width=15).grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_frame, text="Name:", font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.name_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.name_var, font=("Helvetica", 10), width=20).grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_frame, text="Semester:", font=("Helvetica", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.semester_var = tb.StringVar(value="1")
        tb.Entry(form_frame, textvariable=self.semester_var, font=("Helvetica", 10), width=5).grid(row=0, column=5, padx=5, pady=5)
        
        # If Admin mode, allow assigning a specific explicitly managing faculty
        if self.faculty_id is None:
            tb.Label(form_frame, text="Assign Faculty:", font=("Helvetica", 10)).grid(row=0, column=6, padx=5, pady=5)
            self.faculty_var = tb.StringVar()
            self.faculty_combo = tb.Combobox(form_frame, textvariable=self.faculty_var, values=list(self.faculty_dict.keys()), state="readonly", width=15)
            self.faculty_combo.grid(row=0, column=7, padx=5, pady=5)
        
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, pady=15)
        
        tb.Button(btn_frame, text="Add Student", command=self.add_student, bootstyle="primary").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update Selected", command=self.update_student, bootstyle="info").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Delete Selected", command=self.delete_student, bootstyle="danger").pack(side=LEFT, padx=5)
        
        columns = ("ID", "Roll No", "Name", "Semester", "Risk", "Faculty ID")
        self.tree = tb.Treeview(self, columns=columns, show="headings", bootstyle="primary")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Faculty ID" and self.faculty_id is not None:
                self.tree.column(col, width=0, stretch=False) # Hide Faculty ID column from Faculty view
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        students = Student.get_all_students(self.faculty_id)
        for s in students:
            # Table fields map implicitly from the DB queries
            self.tree.insert("", END, values=s)
            
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.roll_var.set(values[1])
            self.name_var.set(values[2])
            if len(values) >= 4: self.semester_var.set(values[3])
            # Load combobox value if Admin mode
            if self.faculty_id is None and len(values) >= 6 and values[5] and values[5] != "None":
                faculty_db_id = int(values[5])
                # Find matching faculty name from dict to set combobox
                for name, f_id in self.faculty_dict.items():
                    if f_id == faculty_db_id:
                        self.faculty_var.set(name)
                        break
            
    def add_student(self):
        roll = self.roll_var.get()
        name = self.name_var.get()
        sem = self.semester_var.get()
        
        fac_id = self.faculty_id
        if self.faculty_id is None:
            fac_id = self.faculty_dict.get(self.faculty_var.get(), None)
            
        if not roll or not name or not sem:
            Messagebox.show_warning("Roll, Name, Semester fields required.", "Error")
            return
            
        success, msg = Student.add_student(roll, name, int(sem), fac_id)
        if success:
            self.load_data()
            self.roll_var.set("")
            self.name_var.set("")
        else:
            Messagebox.show_error(msg, "Error")
            
    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a student to update.", "Error")
            return
        student_id = self.tree.item(selected[0], "values")[0]
        roll = self.roll_var.get()
        name = self.name_var.get()
        sem = self.semester_var.get()
        
        fac_id = self.faculty_id
        if self.faculty_id is None:
            fac_id = self.faculty_dict.get(self.faculty_var.get(), None)
            
        if not roll or not name or not sem:
             Messagebox.show_warning("All fields required.", "Error")
             return
             
        success, msg = Student.update_student(student_id, roll, name, int(sem), fac_id)
        if success:
            self.load_data()
        else:
            Messagebox.show_error(msg, "Error")
            
    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a student to delete.", "Error")
            return
        student_id = self.tree.item(selected[0], "values")[0]
        msg_box = Messagebox.yesno("Are you sure you want to delete this student?", "Confirm")
        if msg_box == "Yes":
            success, msg = Student.delete_student(student_id)
            if success:
                self.load_data()
                self.roll_var.set("")
                self.name_var.set("")
            else:
                Messagebox.show_error(msg, "Error")
