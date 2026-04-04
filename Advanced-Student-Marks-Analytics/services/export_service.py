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
        return PdfReportService.generate_report(filepath)
