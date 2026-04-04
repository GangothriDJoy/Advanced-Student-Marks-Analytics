import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
from views.marks_view import MarksView

class FacultyDashboardView(tb.Frame):
    def __init__(self, parent, faculty_id):
        super().__init__(parent)
        self.parent = parent
        self.faculty_id = faculty_id
        self.pack(fill=BOTH, expand=True)
        self.setup_ui()

    def setup_ui(self):
        # Top Navbar
        nav = tb.Frame(self, bootstyle="info")
        nav.pack(side=TOP, fill=X)
        
        tb.Label(nav, text="Faculty Dashboard", font=("Helvetica", 18, "bold"), bootstyle="info-inverse").pack(side=LEFT, padx=20, pady=15)
        tb.Button(nav, text="Logout", command=self.logout, bootstyle="light-outline").pack(side=RIGHT, padx=10, pady=15)
        
        # Sidebar
        sidebar = tb.Frame(self, bootstyle="dark", width=250)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        
        tb.Label(sidebar, text="Navigation", font=("Helvetica", 12, "bold"), bootstyle="dark-inverse").pack(pady=20)
        
        btn_marks = tb.Button(sidebar, text="Manage My Subjects Marks", command=self.open_marks, bootstyle="primary", width=25)
        btn_marks.pack(pady=15, padx=20)
        
        btn_students = tb.Button(sidebar, text="Manage Students", command=self.open_students, bootstyle="info", width=25)
        btn_students.pack(pady=5, padx=20)
        
        btn_password = tb.Button(sidebar, text="Change Password", command=self.change_password_dialog, bootstyle="warning", width=25)
        btn_password.pack(pady=15, padx=20)
            
        # Main Work Area
        self.main_area = tb.Canvas(self, bg='white')
        self.main_area.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.content_frame = tb.Frame(self.main_area, bootstyle="default")
        self.content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        tb.Label(self.content_frame, text="Welcome to the Faculty Interface", font=("Helvetica", 16, "bold")).pack(pady=(50, 10))
        tb.Label(self.content_frame, text="Use the navigation menu to enter grades for your subjects or register new students.", font=("Helvetica", 12)).pack()
        
    def open_marks(self):
        MarksView(tb.Toplevel(title="Manage My Marks"), faculty_id=self.faculty_id)

    def open_students(self):
        from views.student_view import StudentView
        StudentView(tb.Toplevel(title="Manage Students"), faculty_id=self.faculty_id)
        
    def change_password_dialog(self):
        self.pwd_win = tb.Toplevel(title="Change Password")
        self.pwd_win.geometry("400x350")
        
        frame = tb.Frame(self.pwd_win, padding=20)
        frame.pack(fill=BOTH, expand=True)
        
        tb.Label(frame, text="Old Password:", font=("Helvetica", 10)).pack(pady=5, anchor=W)
        self.old_pw_var = tb.StringVar()
        tb.Entry(frame, textvariable=self.old_pw_var, show="*", width=30).pack(pady=5)
        
        tb.Label(frame, text="New Password:", font=("Helvetica", 10)).pack(pady=5, anchor=W)
        self.new_pw_var = tb.StringVar()
        tb.Entry(frame, textvariable=self.new_pw_var, show="*", width=30).pack(pady=5)
        
        tb.Label(frame, text="Confirm New Password:", font=("Helvetica", 10)).pack(pady=5, anchor=W)
        self.confirm_pw_var = tb.StringVar()
        tb.Entry(frame, textvariable=self.confirm_pw_var, show="*", width=30).pack(pady=5)
        
        tb.Button(frame, text="Update Password", command=self.save_new_password, bootstyle="success").pack(pady=20)
        
    def save_new_password(self):
        old_pw = self.old_pw_var.get()
        new_pw = self.new_pw_var.get()
        confirm_pw = self.confirm_pw_var.get()
        
        if not old_pw or not new_pw or not confirm_pw:
            Messagebox.show_warning("All fields are required.", "Warning")
            return
            
        if new_pw != confirm_pw:
            Messagebox.show_error("New passwords do not match.", "Error")
            return
            
        import hashlib
        from database.db import get_connection
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Verify old password
        hashed_old = hashlib.sha256(old_pw.encode()).hexdigest()
        cur.execute("SELECT id FROM users WHERE linked_faculty_id=? AND password_hash=?", (self.faculty_id, hashed_old))
        if not cur.fetchone():
            Messagebox.show_error("Incorrect old password.", "Error")
            conn.close()
            return
            
        hashed_new = hashlib.sha256(new_pw.encode()).hexdigest()
        cur.execute("UPDATE users SET password_hash=? WHERE linked_faculty_id=?", (hashed_new, self.faculty_id))
        conn.commit()
        conn.close()
        
        Messagebox.show_info("Password updated successfully!", "Success")
        self.pwd_win.destroy()
        
    def logout(self):
        self.pack_forget()
        from views.login_view import LoginView
        LoginView(self.parent)
