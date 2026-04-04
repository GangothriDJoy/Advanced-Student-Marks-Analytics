from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from services.analytics_service import AnalyticsService
import datetime
import os

class ReportService:
    @staticmethod
    def generate_pdf_report(filename="Student_Performance_Report.pdf"):
        stats = AnalyticsService.get_class_statistics()
        if not stats:
            return False, "No data available to generate report."
            
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("Advanced Student Marks Analytics System", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Date Generated: {date_str}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Class Statistics
        elements.append(Paragraph("Overall Class Statistics", styles['Heading2']))
        stats_data = [
            ["Metric", "Value"],
            ["Class Average", f"{stats['class_average']:.2f}"],
            ["Highest Scorer", stats['highest_scorer']],
            ["Lowest Scorer", stats['lowest_scorer']],
            ["Total Passed", str(stats['pass_fail']['Pass'])],
            ["Total Failed", str(stats['pass_fail']['Fail'])]
        ]
        t1 = Table(stats_data, colWidths=[200, 200])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t1)
        elements.append(Spacer(1, 12))
        
        # Toppers
        elements.append(Paragraph("Top 3 Students", styles['Heading2']))
        top_data = [["Rank", "Student Name", "Total Marks"]]
        for i, (name, marks) in enumerate(stats['top_3'].items(), start=1):
            top_data.append([str(i), name, str(marks)])
            
        t2 = Table(top_data, colWidths=[50, 200, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 12))
        
        # Subject Averages
        elements.append(Paragraph("Subject-wise Averages", styles['Heading2']))
        subj_data = [["Subject", "Average Marks"]]
        for subj, avg in stats['subject_averages'].items():
            subj_data.append([subj, f"{avg:.2f}"])
            
        t3 = Table(subj_data, colWidths=[200, 200])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgreen),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t3)
        
        try:
            doc.build(elements)
            return True, f"Report successfully generated at:\n{os.path.abspath(filename)}"
        except Exception as e:
            return False, str(e)
