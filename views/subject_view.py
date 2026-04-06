import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from models.subject import Subject

class SubjectView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        form_frame = tb.Frame(self)
        form_frame.pack(fill=X, pady=10)
        
        # Row 1
        tb.Label(form_frame, text="Code:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.code_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.code_var, font=("Helvetica", 10), width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_frame, text="Name:", font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.name_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.name_var, font=("Helvetica", 10), width=20).grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_frame, text="Credits:", font=("Helvetica", 10)).grid(row=0, column=4, padx=5, pady=5)
        self.credits_var = tb.StringVar()
        tb.Entry(form_frame, textvariable=self.credits_var, font=("Helvetica", 10), width=10).grid(row=0, column=5, padx=5, pady=5)
        
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, pady=15)
        
        tb.Button(btn_frame, text="Add", command=self.add_subject, bootstyle="primary").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Update", command=self.update_subject, bootstyle="info").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Delete", command=self.delete_subject, bootstyle="danger").pack(side=LEFT, padx=5)
        
        columns = ("ID", "Code", "Name", "Credits")
        self.tree = tb.Treeview(self, columns=columns, show="headings", bootstyle="primary")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        subjects = Subject.get_all_subjects()
        # Ensure subjects returns (id, code, name, credits)
        for s in subjects:
            self.tree.insert("", END, values=s)
            
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.code_var.set(values[1])
            self.name_var.set(values[2])
            self.credits_var.set(values[3])
            
    def add_subject(self):
        code = self.code_var.get()
        name = self.name_var.get()
        credits_str = self.credits_var.get()
        
        if not code or not name or not credits_str:
            Messagebox.show_warning("All fields required.", "Error")
            return
            
        try:
            credits = int(credits_str)
        except ValueError:
            Messagebox.show_warning("Credits must be an integer.", "Error")
            return
            
        success, msg = Subject.add_subject(code, name, credits)
        if success:
            self.load_data()
            self.name_var.set("")
            self.code_var.set("")
            self.credits_var.set("")
        else:
            Messagebox.show_error(msg, "Error")
            
    def update_subject(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a subject.", "Error")
            return
        subj_id = self.tree.item(selected[0], "values")[0]
        code = self.code_var.get()
        name = self.name_var.get()
        credits_str = self.credits_var.get()
        
        try:
            credits = int(credits_str)
        except ValueError:
            Messagebox.show_warning("Credits must be an integer.", "Error")
            return
            
        success, msg = Subject.update_subject(subj_id, code, name, credits)
        if success:
            self.load_data()
        else:
            Messagebox.show_error(msg, "Error")
            
    def delete_subject(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Select a subject.", "Error")
            return
        subj_id = self.tree.item(selected[0], "values")[0]
        msg_box = Messagebox.yesno("Are you sure you want to delete this subject?", "Confirm")
        if msg_box == "Yes":
            success, msg = Subject.delete_subject(subj_id)
            if success:
                self.load_data()
                self.name_var.set("")
                self.code_var.set("")
                self.credits_var.set("")
            else:
                Messagebox.show_error(msg, "Error")
