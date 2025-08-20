# AI Bookkeeping SaaS (v1.4 — OCR Edition)

**What’s new in v1.4**
- Scanned PDF support via OCR (pytesseract) with pypdfium2 rendering.
- Sidebar toggle to enable OCR fallback (OFF by default for cloud stability).
- Works for Bank statements and Invoices (CSV / Excel / PDF).

> OCR needs the Tesseract binary. If OCR fails on cloud, toggle OCR off or use digital PDFs.

## Run
pip install -r requirements.txt
streamlit run app.py
