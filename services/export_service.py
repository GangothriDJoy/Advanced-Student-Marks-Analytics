import pandas as pd
from services.analytics_service import AnalyticsService
import os

class ExportService:
    @staticmethod
    def export_full_dataset_excel(filepath="Academic_Dataset_Export.xlsx"):
        df = AnalyticsService.get_full_dataframe()
        if df.empty:
            return False, "No data available."
        try:
            df.to_excel(filepath, index=False)
            return True, f"Exported successfully to {filepath}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def export_full_dataset_csv(filepath="Academic_Dataset_Export.csv"):
        df = AnalyticsService.get_full_dataframe()
        if df.empty:
            return False, "No data available."
        try:
            df.to_csv(filepath, index=False)
            return True, f"Exported successfully to {filepath}"
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def export_analytics_pdf(filepath="Student_Performance_Report.pdf"):
        from services.pdf_report_service import PdfReportService
        df = AnalyticsService.get_full_dataframe()
        if df.empty:
            return False, "No data available."
            
        import os
        # Extract department from KTU Roll No (e.g., MAC20CS052 -> extract CS)
        dept_col = df['roll_no'].astype(str).str.extract(r'^[A-Za-z]+[0-9]{2}([A-Za-z]{2})', expand=False)
        df['department'] = dept_col.fillna('General')
        
        departments = df['department'].unique()
        base_name, ext = os.path.splitext(filepath)
        if not ext:
            ext = ".pdf"
            
        successes = 0
        errors = []
        
        for dept in departments:
            dept_df = df[df['department'] == dept].copy()
            if dept_df.empty:
                continue
                
            # Formulate specific filepath (e.g., Analysis_CS.pdf)
            if len(departments) == 1:
                dept_filepath = filepath
            else:
                dept_filepath = f"{base_name}_{dept}{ext}"
            
            # Use expanded names if known
            dept_full_name = dept
            if dept == 'CS': dept_full_name = 'Computer Science & Engineering'
            elif dept == 'ME': dept_full_name = 'Mechanical Engineering'
            elif dept == 'CE': dept_full_name = 'Civil Engineering'
            elif dept == 'EC': dept_full_name = 'Electronics & Communication Engg.'
            elif dept == 'EE': dept_full_name = 'Electrical & Electronics Engg.'
            elif dept == 'IT': dept_full_name = 'Information Technology'
            
            success, msg = PdfReportService.generate_report(filepath=dept_filepath, df=dept_df, department_name=dept_full_name)
            if success:
                successes += 1
            else:
                errors.append(f"{dept}: {msg}")
                
        if successes > 0 and len(errors) == 0:
            return True, f"Successfully generated {successes} separate department PDF(s)."
        elif successes > 0:
            return True, f"Generated {successes} PDFs, but encountered some errors: {', '.join(errors)}"
        else:
            return False, f"Failed to generate PDFs: {', '.join(errors)}"
