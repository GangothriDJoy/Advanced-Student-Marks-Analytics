import pandas as pd
from models.student import Student
from models.subject import Subject
from models.marks import Marks

class ImportService:
    @staticmethod
    def bulk_import_marks(filepath):
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(filepath)
            else:
                return False, "Unsupported file format. Use CSV or Excel."

            required_cols = ['Roll_No', 'Subject_Code', 'Semester', 'Marks']
            for col in required_cols:
                if col not in df.columns:
                    return False, f"Missing required column: {col}"

            students = {s[1]: s[0] for s in Student.get_all_students()}
            subjects = {s[1]: s[0] for s in Subject.get_all_subjects()}

            imported_count = 0
            for _, row in df.iterrows():
                roll = str(row['Roll_No']).strip()
                code = str(row['Subject_Code']).strip()
                sem = int(row['Semester'])
                m = int(row['Marks'])

                if roll in students and code in subjects:
                    success, _ = Marks.add_or_update_marks(students[roll], subjects[code], sem, m)
                    if success:
                        imported_count += 1
                        
            return True, f"Successfully imported {imported_count} records."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def bulk_import_ktu_results(filepath):
        try:
            if filepath.lower().endswith('.pdf'):
                return ImportService.parse_ktu_pdf(filepath)
            elif filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(filepath)
            else:
                return False, "Unsupported file format. Use PDF, CSV or Excel."

            required_cols = ['Register_No', 'Student_Name', 'Semester']
            for col in required_cols:
                if col not in df.columns:
                    return False, f"Missing required KTU column: {col}"

            from utils.helpers import grade_to_marks
            from database.db import get_connection

            imported_count = 0
            subject_cols = [c for c in df.columns if c not in required_cols]

            for _, row in df.iterrows():
                roll = str(row['Register_No']).strip()
                name = str(row['Student_Name']).strip()
                sem = int(row['Semester'])

                Student.add_student(roll, name, sem)
                
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM students WHERE roll_no=?", (roll,))
                student_id_row = cur.fetchone()
                if not student_id_row:
                    conn.close()
                    continue
                student_id = student_id_row[0]
                
                for code in subject_cols:
                    grade = str(row[code]).strip()
                    if grade == 'nan' or not grade: continue
                    marks_val = grade_to_marks(grade)
                    
                    Subject.add_subject(code, code, 3)
                    
                    cur.execute("SELECT id FROM subjects WHERE subject_code=?", (code,))
                    subject_id_row = cur.fetchone()
                    if subject_id_row:
                        subject_id = subject_id_row[0]
                        success, _ = Marks.add_or_update_marks(student_id, subject_id, sem, marks_val)
                        if success: imported_count += 1
                        
                conn.close()
            return True, f"Successfully processed KTU format and imported {imported_count} subject grades."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def parse_ktu_pdf(filepath):
        import re
        from models.student import Student
        from models.subject import Subject
        from models.marks import Marks
        from utils.helpers import grade_to_marks
        from database.db import get_connection
        try:
            text = ImportService._extract_text_from_any_pdf(filepath)
            diag = ""
            if "[EXTRACT_ERRORS:" in text:
                parts = text.split("[EXTRACT_ERRORS:")
                text = parts[0]
                diag = "\n\nDiagnostics:\n" + parts[1].rstrip("]")
            if not text or len(text.strip()) < 5:
                return False, (
                    "Could not extract readable text from this document."
                    + diag +
                    "\n\nFor scanned PDFs, install Tesseract OCR:\n"
                    "  https://github.com/UB-Mannheim/tesseract/wiki"
                )
            text = text.replace('\x00', '').replace('\r', '\n')

            # ── Auto-detect format ──────────────────────────────────────────
            is_summary = any(k in text for k in ('KTU-ID', 'Sub.Code', 'Pass %', 'Sub.Name', 'Pass%'))
            if is_summary:
                return ImportService._parse_ktu_result_summary(text)

            # ── Format 2: Individual grade sheet ────────────────────────────
            roll_pattern  = re.compile(r'\b([A-Z]{2,4}\d{2}[A-Z]{2}\d{3})\b', re.IGNORECASE)
            grade_pattern = re.compile(
                r'\b([A-Z]{2,3}\d{3,4})\s*[:(–\-]?\s*([OASBCPFI][+]?E?)(?!\w)', re.IGNORECASE)
            rolls_found    = list(roll_pattern.finditer(text))
            imported_count = 0
            conn = get_connection()
            cur  = conn.cursor()

            for i, roll_match in enumerate(rolls_found):
                roll    = roll_match.group(1).strip().upper()
                start   = roll_match.end()
                end     = rolls_found[i + 1].start() if i + 1 < len(rolls_found) else len(text)
                segment = text[start:end]
                grade_hits = grade_pattern.findall(segment)
                if not grade_hits:
                    continue
                Student.add_student(roll, roll, 1)
                cur.execute("SELECT id FROM students WHERE roll_no=?", (roll,))
                sid_row = cur.fetchone()
                if not sid_row:
                    continue
                student_id = sid_row[0]
                for code, grade in grade_hits:
                    code      = code.strip().upper()
                    grade     = grade.strip().upper()
                    marks_val = grade_to_marks(grade)
                    Subject.add_subject(code, code, 3)
                    cur.execute("SELECT id FROM subjects WHERE subject_code=?", (code,))
                    subj_row = cur.fetchone()
                    if subj_row:
                        success, _ = Marks.add_or_update_marks(student_id, subj_row[0], 1, marks_val)
                        if success:
                            imported_count += 1
            conn.close()
            if imported_count == 0:
                preview = text.strip()[:300].replace('\n', ' | ')
                return False, (
                    "No grade entries found.\n\n"
                    f"Extracted text sample:\n{preview}"
                )
            return True, f"Successfully imported {imported_count} individual grades."
        except Exception as e:
            return False, f"Parsing failed: {str(e)}"

    @staticmethod
    def _parse_ktu_result_summary(text):
        """Parse KTU class result analysis PDF (KTU-ID list + Subject pass-rate table)."""
        import re
        from models.student import Student
        from models.subject import Subject
        from models.marks import Marks
        from database.db import get_connection

        # Detect semester number from text like 'S5 (2023 - 2027 Batch)'
        sem_match = re.search(r'\bS(\d)\b', text)
        semester  = int(sem_match.group(1)) if sem_match else 1

        # ── Parse students: roll numbers and names ───────────────────────────
        # After "KTU-ID | NAME |", tokens alternate: roll | name | roll | name…
        roll_re = re.compile(r'\b([A-Z]{2,4}\d{2}[A-Z]{2}\d{3})\b', re.IGNORECASE)
        all_rolls = roll_re.findall(text)
        # Extract name after each roll number
        student_pairs = re.findall(
            r'\b([A-Z]{2,4}\d{2}[A-Z]{2}\d{3})\b\s*\|\s*([A-Z][A-Z\s\.]+?)(?=\s*\||\n)',
            text, re.IGNORECASE)

        students_data = {}
        for roll, name in student_pairs:
            roll = roll.strip().upper()
            name = name.strip()
            if roll and name:
                students_data[roll] = name
        # Fallback: all roll numbers without names
        for roll in all_rolls:
            roll = roll.strip().upper()
            if roll not in students_data:
                students_data[roll] = roll

        # ── Parse subjects with pass rates ──────────────────────────────────
        # Format: CST301 | FORMAL LANGUAGES AND | 78 | 1 | 97.50
        subject_re = re.compile(
            r'\b([A-Z]{2,3}\d{3,4})\b\s*\|\s*([^|]{3,60}?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)',
            re.IGNORECASE)
        subjects_data = []
        for m in subject_re.finditer(text):
            code     = m.group(1).strip().upper()
            name     = m.group(2).strip()
            passed   = int(m.group(3))
            failed   = int(m.group(4))
            pass_pct = float(m.group(5))
            subjects_data.append((code, name, passed, failed, pass_pct))

        if not students_data and not subjects_data:
            return False, "No student or subject data found in this KTU result summary."

        conn = get_connection()
        cur  = conn.cursor()
        imported_count = 0

        # Import students
        student_ids = {}
        for roll, name in students_data.items():
            Student.add_student(roll, name, semester)
            cur.execute("SELECT id FROM students WHERE roll_no=?", (roll,))
            sid = cur.fetchone()
            if sid:
                student_ids[roll] = sid[0]

        # Import subjects and derive class-average marks from pass rate
        for code, name, passed, failed, pass_pct in subjects_data:
            Subject.add_subject(code, name, 3)
            cur.execute("SELECT id FROM subjects WHERE subject_code=?", (code,))
            subj_row = cur.fetchone()
            if not subj_row:
                continue
            subj_id = subj_row[0]

            # Derive representative mark from pass rate
            if pass_pct >= 90:
                rep_mark = 78   # B+ level
            elif pass_pct >= 75:
                rep_mark = 65   # B level
            elif pass_pct >= 60:
                rep_mark = 55   # C level
            elif pass_pct >= 40:
                rep_mark = 45   # Pass level
            else:
                rep_mark = 32   # Fail

            # Assign class-average mark to each student
            for roll, stu_id in student_ids.items():
                success, _ = Marks.add_or_update_marks(stu_id, subj_id, semester, rep_mark)
                if success:
                    imported_count += 1

        conn.close()
        n_stu  = len(student_ids)
        n_subj = len(subjects_data)
        return True, (
            f"KTU Result Summary imported:\n"
            f"  • {n_stu} students\n"
            f"  • {n_subj} subjects\n"
            f"  • {imported_count} mark records\n\n"
            f"Semester {semester} — Marks derived from subject pass rates.\n"
            f"Dashboard analytics are now available!"
        )

    @staticmethod
    def _extract_text_from_any_pdf(filepath):
        """Exhaustive multi-strategy extractor. Never hides real errors."""
        text = ""
        errors = []

        # ── Strategy 0a: fitz plain text (fastest, works on most KTU PDFs) ──
        try:
            import fitz
            doc = fitz.open(filepath)
            for page in doc:
                for mode in ("text", "words", "blocks"):
                    try:
                        if mode == "words":
                            words = page.get_text("words")
                            text += " ".join(w[4] for w in words) + "\n"
                        elif mode == "blocks":
                            blocks = page.get_text("blocks")
                            text += " ".join(b[4] for b in blocks if isinstance(b[4], str)) + "\n"
                        else:
                            text += (page.get_text("text") or "") + "\n"
                    except Exception:
                        pass
            doc.close()
            if len(text.strip()) > 5:
                return text
            text = ""  # reset and try OCR path
        except Exception as e:
            errors.append(f"fitz: {e}")

        # ── Strategy 0b: fitz render + pytesseract per-page OCR ─────────────
        try:
            import fitz
            import pytesseract
            from PIL import Image
            import io
            doc = fitz.open(filepath)
            for page in doc:
                pix = page.get_pixmap(dpi=250)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text += pytesseract.image_to_string(img, lang='eng') + "\n"
            doc.close()
            if len(text.strip()) > 5:
                return text
            text = ""
        except Exception as e:
            errors.append(f"fitz+OCR: {e}")

        # ── Strategy 1: pdfplumber ───────────────────────────────────────────
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    pg_text = page.extract_text() or ""
                    text += pg_text + "\n"
                    for table in page.extract_tables():
                        for row in table:
                            text += " ".join([str(c) for c in row if c]) + "\n"
            if len(text.strip()) > 5:
                return text
            text = ""
        except Exception as e:
            errors.append(f"pdfplumber: {e}")

        # ── Strategy 2: PyPDF2 ───────────────────────────────────────────────
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    ext = page.extract_text() or ""
                    text += ext + "\n"
            if len(text.strip()) > 5:
                return text
            text = ""
        except Exception as e:
            errors.append(f"PyPDF2: {e}")

        # ── Strategy 3: pdf2image + pytesseract (needs Poppler) ─────────────
        try:
            import pytesseract
            from pdf2image import convert_from_path
            for page_img in convert_from_path(filepath, dpi=200):
                text += pytesseract.image_to_string(page_img, lang='eng') + "\n"
            if len(text.strip()) > 5:
                return text
        except Exception as e:
            errors.append(f"pdf2image+OCR: {e}")

        # Return whatever we have, plus error details in a comment
        if errors:
            text += "\n[EXTRACT_ERRORS: " + " | ".join(errors) + "]"
        return text


