"""
Diagnostic script – run from the project root:
  python diag_pdf.py path\to\your\ktu_result.pdf
"""
import sys, os, traceback

if len(sys.argv) < 2:
    print("Usage: python diag_pdf.py <path_to_ktu_pdf>")
    sys.exit(1)

filepath = sys.argv[1]
print(f"\n=== Diagnosing: {filepath} ===\n")

# Strategy 0 – PyMuPDF / fitz
print("--- Strategy 0: fitz (PyMuPDF) ---")
try:
    import fitz
    doc = fitz.open(filepath)
    text = ""
    for i, page in enumerate(doc):
        pg = page.get_text("text")
        print(f"  Page {i+1}: {len(pg)} chars extracted")
        text += pg
    doc.close()
    print(f"  TOTAL: {len(text.strip())} chars")
    if text.strip():
        print("  SAMPLE:\n", text.strip()[:500])
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()

print()

# Strategy 1 – pdfplumber
print("--- Strategy 1: pdfplumber ---")
try:
    import pdfplumber
    with pdfplumber.open(filepath) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            pg = page.extract_text() or ""
            print(f"  Page {i+1}: {len(pg)} chars extracted")
            text += pg
    print(f"  TOTAL: {len(text.strip())} chars")
    if text.strip():
        print("  SAMPLE:\n", text.strip()[:500])
except Exception as e:
    print(f"  FAILED: {e}")
    traceback.print_exc()

print()

# Report Python version and installed packages
print("--- Environment ---")
print(f"  Python: {sys.version}")
for pkg in ["fitz", "pdfplumber", "PyPDF2", "pytesseract"]:
    try:
        m = __import__(pkg)
        print(f"  {pkg}: OK ({getattr(m, '__version__', 'version unknown')})")
    except ImportError as e:
        print(f"  {pkg}: MISSING – {e}")
