import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.student_view import StudentView
from views.subject_view import SubjectView
from views.marks_view import MarksView
from views.faculty_view import FacultyView
from services.analytics_service import AnalyticsService
from services.insights_service import InsightsService
from services.export_service import ExportService

class DashboardView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True)
        self.setup_ui()
        self.refresh_dashboard()

    def setup_ui(self):
        # Top Navbar (Using ttkbootstrap styles instead of hex colors)
        nav = tb.Frame(self, bootstyle="primary")
        nav.pack(side=TOP, fill=X)
        
        tb.Label(nav, text="Academic Performance Intelligence Platform", font=("Helvetica", 18, "bold"), bootstyle="primary-inverse").pack(side=LEFT, padx=20, pady=15)
        tb.Button(nav, text="Logout", command=self.logout, bootstyle="light-outline").pack(side=RIGHT, padx=10, pady=15)
        tb.Button(nav, text="Refresh DB", command=self.refresh_dashboard, bootstyle="light-outline").pack(side=RIGHT, padx=10, pady=15)
        
        # Sidebar
        sidebar = tb.Frame(self, bootstyle="dark", width=220)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        
        commands = [
            ("Manage Students", self.open_students, "info"),
            ("Manage Subjects", self.open_subjects, "info"),
            ("Manage Faculty", self.open_faculty, "info"),
            ("Enter Marks & Import", self.open_marks, "info"),
            ("KTU Results Upload", self.import_ktu_results, "warning"),
            ("Export CSV", self.export_csv, "success"),
            ("Export Excel", self.export_excel, "success"),
            ("Download Analytics PDF", self.export_pdf, "danger")
        ]
        
        tb.Label(sidebar, text="Navigation", font=("Helvetica", 12, "bold"), bootstyle="dark-inverse").pack(pady=20)
        for text, cmd, style in commands:
            btn = tb.Button(sidebar, text=text, command=cmd, bootstyle=style, width=20)
            btn.pack(pady=5, padx=20)
            
        # Main Work Area
        self.main_area = tb.Canvas(self, bg='white')
        scrollbar = tb.Scrollbar(self, orient="vertical", command=self.main_area.yview, bootstyle="round")
        self.main_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=RIGHT, fill=Y)
        self.main_area.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.content_frame = tb.Frame(self.main_area, bootstyle="default")
        self.main_area.create_window((0,0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda e: self.main_area.configure(scrollregion=self.main_area.bbox("all")))
        
        # 1. Top metric cards row
        self.cards_frame = tb.Frame(self.content_frame)
        self.cards_frame.pack(fill=X, pady=20, padx=20)
        
        # 2. Middle row (Insights and Basic Chart)
        self.mid_frame = tb.Frame(self.content_frame)
        self.mid_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        self.insights_frame = tb.Labelframe(self.mid_frame, text="✨ AI Insights Engine", bootstyle="info", padding=15)
        self.insights_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,10))
        
        self.chart_frame = tb.Labelframe(self.mid_frame, text="Pass vs Fail Distribution", bootstyle="primary", padding=15)
        self.chart_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(10,0))
        
    def create_card(self, parent, title, value, style):
        f = tb.Frame(parent, bootstyle=style)
        f.pack(side=LEFT, expand=True, fill=BOTH, padx=10)
        tb.Label(f, text=title, font=("Helvetica", 11), bootstyle=f"{style}-inverse").pack(pady=(15,5), padx=15)
        tb.Label(f, text=str(value), font=("Helvetica", 24, "bold"), bootstyle=f"{style}-inverse").pack(pady=(0,15), padx=15)
        return f

    def refresh_dashboard(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for widget in self.insights_frame.winfo_children():
            widget.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        stats = AnalyticsService.calculate_subject_difficulty()
        risks = AnalyticsService.identify_at_risk_students()
        insights = InsightsService.generate_ai_insights()
        
        total_students = len(risks)
        high_risk_count = len([x for x in risks if x['risk'] == 'High Risk'])
        
        self.create_card(self.cards_frame, "Analyzed Students", total_students, "success")
        self.create_card(self.cards_frame, "High Risk Academics", high_risk_count, "danger")
        self.create_card(self.cards_frame, "Subjects Indexed", len(stats), "info")
        
        if not insights:
            tb.Label(self.insights_frame, text="No analytical data available yet. Please add data.", font=("Helvetica", 11)).pack(anchor='w', pady=10)
        for text in insights:
            tb.Label(self.insights_frame, text=text, font=("Helvetica", 11), wraplength=400, justify=LEFT).pack(anchor='w', pady=10)
            
        df = AnalyticsService.get_full_dataframe()
        if not df is None and not df.empty:
            fails = len(df[df['marks']<40]['student_name'].unique())
            passes = len(df['student_name'].unique()) - fails
            
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie([passes, fails], labels=['Pass', 'Fail'], autopct='%1.1f%%', colors=['#2fb344', '#d9534f']) # Match cosmo theme
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            plt.close(fig)

    def open_students(self):
        StudentView(tb.Toplevel(title="Manage Students"))
    def open_subjects(self):
        SubjectView(tb.Toplevel(title="Manage Subjects"))
    def open_faculty(self):
        FacultyView(tb.Toplevel(title="Manage Faculty"))
    def open_marks(self):
        MarksView(tb.Toplevel(title="Manage Marks"))
        
    def import_ktu_results(self):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")])
        if filepath:
            from services.import_service import ImportService
            success, msg = ImportService.bulk_import_ktu_results(filepath)
            if success:
                Messagebox.show_info(msg, "Success")
                self.refresh_dashboard()
            else:
                Messagebox.show_error(msg, "Error")

    def export_csv(self):
        from tkinter import filedialog
        from services.export_service import ExportService
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            success, msg = ExportService.export_full_dataset_csv(filepath=filepath)
            if success:
                Messagebox.show_info(msg, "Success")
            else:
                Messagebox.show_error(msg, "Error")

    def export_excel(self):
        from tkinter import filedialog
        from services.export_service import ExportService
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filepath:
            success, msg = ExportService.export_full_dataset_excel(filepath=filepath)
            if success:
                Messagebox.show_info(msg, "Success")
            else:
                Messagebox.show_error(msg, "Error")
                
    def export_pdf(self):
        from tkinter import filedialog
        from services.export_service import ExportService
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            success, msg = ExportService.export_analytics_pdf(filepath=filepath)
            if success:
                Messagebox.show_info(msg, "Success")
            else:
                Messagebox.show_error(msg, "Error")
                
    def logout(self):
        self.pack_forget()
        from views.login_view import LoginView
        LoginView(self.parent)
