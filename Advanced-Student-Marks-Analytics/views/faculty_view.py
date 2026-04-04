import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from models.faculty import Faculty
from models.subject import Subject

class FacultyView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        add_frame = tb.Labelframe(self, text="Add New Faculty", padding=15, bootstyle="info")
        add_frame.pack(fill=X, pady=10)
        
        tb.Label(add_frame, text="Faculty Name:", font=("Helvetica", 10)).pack(side=LEFT, padx=5)
        self.name_var = tb.StringVar()
        tb.Entry(add_frame, textvariable=self.name_var, font=("Helvetica", 10)).pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(add_frame, text="Add Faculty", command=self.add_faculty, bootstyle="primary").pack(side=LEFT, padx=5)
        
        list_frame = tb.Labelframe(self, text="Existing Faculty", padding=15, bootstyle="info")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        columns = ("ID", "Name")
        self.tree = tb.Treeview(list_frame, columns=columns, show="headings", height=8, bootstyle="primary")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Faculty Name")
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        btn_frame = tb.Frame(list_frame)
        btn_frame.pack(fill=X, pady=5)
        tb.Button(btn_frame, text="Delete Selected Faculty", command=self.delete_faculty, bootstyle="danger").pack(side=RIGHT, padx=5)
        
        assign_frame = tb.Labelframe(self, text="Assign Subject to Selected Faculty", padding=15, bootstyle="success")
        assign_frame.pack(fill=X, pady=10)
        
        self.selected_faculty_lbl = tb.Label(assign_frame, text="Selected Faculty: None", font=("Helvetica", 11, "bold"))
        self.selected_faculty_lbl.pack(pady=10)
        
        assign_inner = tb.Frame(assign_frame)
        assign_inner.pack(fill=X)
        
        tb.Label(assign_inner, text="Select Subject:", font=("Helvetica", 10)).pack(side=LEFT, padx=5)
        
        self.subjects = Subject.get_all_subjects()
        self.subject_dict = {f"{s[1]} - {s[2]}": s[0] for s in self.subjects}
        self.subject_combo = tb.Combobox(assign_inner, values=list(self.subject_dict.keys()), state="readonly", bootstyle="success")
        self.subject_combo.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        tb.Button(assign_inner, text="Assign", command=self.assign, bootstyle="success").pack(side=LEFT, padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        facs = Faculty.get_all_faculty()
        for f in facs:
            self.tree.insert("", END, values=f)
            
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            self.selected_faculty_lbl.config(text=f"Selected Faculty: {vals[1]} (ID: {vals[0]})")
            
    def add_faculty(self):
        name = self.name_var.get()
        if not name:
            Messagebox.show_warning("Name required.", "Error")
            return
        Faculty.add_faculty(name)
        self.name_var.set("")
        self.load_data()
        
    def delete_faculty(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a faculty to delete.", "Error")
            return
        
        fac_id = self.tree.item(selected[0], "values")[0]
        fac_name = self.tree.item(selected[0], "values")[1]
        
        resp = Messagebox.yesno(f"Are you sure you want to delete {fac_name}?", "Confirm Delete")
        if resp == "Yes":
            success, msg = Faculty.delete_faculty(fac_id)
            if success:
                Messagebox.show_info("Faculty deleted.", "Success")
                self.load_data()
            else:
                Messagebox.show_error(msg, "Error")
        
    def assign(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a faculty first.", "Error")
            return
        fac_id = self.tree.item(selected[0], "values")[0]
        subj_str = self.subject_combo.get()
        if not subj_str:
            Messagebox.show_warning("Select a subject first.", "Error")
            return
        subj_id = self.subject_dict[subj_str]
        
        success, msg = Faculty.assign_subject(fac_id, subj_id)
        if success:
            Messagebox.show_info("Assigned successfully.", "Success")
        else:
            Messagebox.show_error(msg, "Error")
