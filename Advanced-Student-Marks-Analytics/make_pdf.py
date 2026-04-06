from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
c = canvas.Canvas('C:/Users/sreen/Downloads/dummy_ktu_result.pdf', pagesize=letter)
c.drawString(100, 750, 'APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY')
c.drawString(100, 700, 'Student Result Analysis - S5 (2023 - 2027 Batch)')
c.drawString(100, 680, 'KTU-ID | NAME | Pass %')
c.drawString(100, 650, 'MAC21CS050 | ARUN KUMAR | 100')
c.drawString(100, 630, 'MAC21CS051 | BHARATH | 100')
c.drawString(100, 610, 'MAC21CS052 | CHANDU | 100')
c.drawString(100, 550, 'Subject Pass Rates:')
c.drawString(100, 530, 'CST301 | FORMAL LANGUAGES | 78 | 2 | 97.50')
c.drawString(100, 510, 'CST303 | COMPUTER NETWORKS | 70 | 10 | 87.50')
c.drawString(100, 490, 'CST305 | SOFTWARE ENGINEERING | 60 | 20 | 75.00')
c.save()
