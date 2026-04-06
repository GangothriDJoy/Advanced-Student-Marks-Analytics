import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
import hashlib
from database.db import get_connection

class LoginView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        
    def create_widgets(self):
        # Create a centered card-like frame
        container = tb.Frame(self, padding="30 30 30 30", bootstyle="light")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tb.Label(container, text="System Login", font=("Helvetica", 24, "bold"), bootstyle="primary").grid(row=0, column=0, columnspan=2, pady=(0,30))
        
        tb.Label(container, text="Username:", font=("Helvetica", 11)).grid(row=1, column=0, sticky=tk.E, pady=10, padx=10)
        self.username_var = tk.StringVar()
        tb.Entry(container, textvariable=self.username_var, font=("Helvetica", 11), width=25).grid(row=1, column=1, pady=10, padx=10)
        
        tb.Label(container, text="Password:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=tk.E, pady=10, padx=10)
        self.password_var = tk.StringVar()
        tb.Entry(container, textvariable=self.password_var, show="*", font=("Helvetica", 11), width=25).grid(row=2, column=1, pady=10, padx=10)
        
        tb.Button(container, text="Login", command=self.attempt_login, bootstyle="primary", width=20).grid(row=3, column=0, columnspan=2, pady=(30,0))
        
    def attempt_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            Messagebox.show_warning("All fields are required!", "Validation Error")
            return
            
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, role, linked_faculty_id FROM users WHERE username=? AND password_hash=?", (username, hashed_pw))
        user = cur.fetchone()
        conn.close()
        
        if user:
            self.pack_forget()
            user_id, role, linked_faculty_id = user
            if role == 'faculty':
                from views.faculty_dashboard_view import FacultyDashboardView
                FacultyDashboardView(self.parent, linked_faculty_id)
            else:
                from views.dashboard_view import DashboardView
                DashboardView(self.parent)
        else:
            Messagebox.show_error("Invalid username or password.", "Login Failed")
