import io, re, pdfplumber, pandas as pd
from datetime import datetime
from PIL import Image

# Try to import OCR libs safely
try:
    import pytesseract
    TESS_AVAILABLE = True
except Exception:
    pytesseract = None
    TESS_AVAILABLE = False

try:
    import pypdfium2 as pdfium
    PDFIUM_AVAILABLE = True
except Exception:
    pdfium = None
    PDFIUM_AVAILABLE = False

def _extract_text_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text

def _ocr_text_pdf(file_bytes: bytes, dpi: int = 200) -> str:
    if not (TESS_AVAILABLE and PDFIUM_AVAILABLE):
        return ""
    text_out = []
    pdf = pdfium.PdfDocument(io.BytesIO(file_bytes))
    for i in range(len(pdf)):
        page = pdf[i]
        pil_image = page.render(scale=dpi/72).to_pil()
        txt = pytesseract.image_to_string(pil_image)
        text_out.append(txt)
    return "\n".join(text_out)

# -------- Bank loaders --------
def load_bank_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes))
    return normalize_bank_df(df)

def load_bank_excel(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes))
    return normalize_bank_df(df)

def load_bank_pdf(file_bytes: bytes, enable_ocr: bool = False) -> pd.DataFrame:
    text = _extract_text_pdf(file_bytes)
    df = parse_bank_from_text(text)
    if df.empty and enable_ocr:
        text = _ocr_text_pdf(file_bytes)
        df = parse_bank_from_text(text)
    if df.empty:
        raise ValueError("Could not parse any transactions from the PDF. For scanned PDFs, enable OCR and ensure Tesseract is installed.")
    return normalize_bank_df(df)

def parse_bank_from_text(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        d = None
        for fmt in ("%d/%m/%Y","%Y-%m-%d","%d-%m-%Y"):
            try:
                d = datetime.strptime(parts[0], fmt).date()
                break
            except: pass
        if not d:
            continue
        amt_str = parts[-1].replace(",","").replace("(","-").replace(")","")
        try:
            amt = float(amt_str)
        except:
            continue
        desc = " ".join(parts[1:-1])
        rows.append({"date": d, "description": desc, "amount": amt})
    return pd.DataFrame(rows)

def normalize_bank_df(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for c in df.columns:
        lc = c.lower().strip()
        if lc in ("date","transaction date","txn date","value date"): mapping[c] = "date"
        elif lc in ("description","details","narrative","particulars"): mapping[c] = "description"
        elif lc in ("amount","debit/credit","value","amt","debit","credit"): mapping[c] = "amount"
        elif lc in ("reference","ref","id"): mapping[c] = "reference"
    df = df.rename(columns=mapping)
    if "date" in df.columns: df["date"] = pd.to_datetime(df["date"]).dt.date
    else: raise ValueError("No 'date' column detected.")
    if "description" not in df.columns: df["description"] = ""
    if "amount" not in df.columns: raise ValueError("No 'amount' column detected.")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)
    if "reference" not in df.columns: df["reference"] = ""
    return df[["date","description","amount","reference"]]

# -------- Invoice loaders --------
def load_invoice_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes))
    return normalize_invoice_df(df)

def load_invoice_excel(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes))
    return normalize_invoice_df(df)

def load_invoice_pdf(file_bytes: bytes, enable_ocr: bool = False) -> pd.DataFrame:
    text = _extract_text_pdf(file_bytes)
    df = parse_invoice_from_text(text)
    if df.empty and enable_ocr:
        text = _ocr_text_pdf(file_bytes)
        df = parse_invoice_from_text(text)
    if df.empty:
        raise ValueError("Could not parse fields from the invoice PDF. For scanned PDFs, enable OCR and ensure Tesseract is installed.")
    return normalize_invoice_df(df)

def parse_invoice_from_text(text: str) -> pd.DataFrame:
    rows = []
    mdate = re.search(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", text)
    inv_date = None
    if mdate:
        for fmt in ("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y"):
            try:
                inv_date = datetime.strptime(mdate.group(1), fmt).date(); break
            except: pass
    mtotal = re.search(r"Total\s*[:=]?\s*R?\s*([0-9,]+\.?[0-9]*)", text, re.I)
    if mtotal:
        amt = float(mtotal.group(1).replace(",",""))
        rows.append({"date": inv_date, "description": "Invoice (OCR/digital parsed)", "amount": amt, "reference": "", "vat_code": "STD"})
    return pd.DataFrame(rows)

def normalize_invoice_df(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for c in df.columns:
        lc = c.lower().strip()
        if lc in ("date","invoice date","txn date"): mapping[c] = "date"
        elif lc in ("description","item","details"): mapping[c] = "description"
        elif lc in ("amount","total","grand total"): mapping[c] = "amount"
        elif lc in ("reference","ref","invoice","invoice no","invoice #"): mapping[c] = "reference"
        elif lc in ("vat","vat_code","tax_code"): mapping[c] = "vat_code"
    df = df.rename(columns=mapping)
    if "date" in df.columns: df["date"] = pd.to_datetime(df["date"]).dt.date
    else: raise ValueError("Invoice file missing a 'date' column.")
    if "description" not in df.columns: df["description"] = "Invoice"
    if "amount" not in df.columns: raise ValueError("Invoice file missing an 'amount' column.")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)
    if "reference" not in df.columns: df["reference"] = ""
    if "vat_code" not in df.columns: df["vat_code"] = "STD"
    return df[["date","description","amount","reference","vat_code"]]
