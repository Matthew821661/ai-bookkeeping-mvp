import pdfplumber, pandas as pd, io
from typing import List, Dict
from datetime import datetime

def load_bank_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes))
    return normalize_bank_df(df)

def load_bank_excel(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes))
    return normalize_bank_df(df)

def load_bank_pdf(file_bytes: bytes) -> pd.DataFrame:
    """
    Very light PDF line extraction (digital PDFs). Real bank statements vary widely.
    Expect to adapt per bank using regex.
    """
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    # naive parsing: find lines with date, description, amount
    rows = []
    for line in text.splitlines():
        # crude pattern: DD/MM/YYYY ... amount
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        # Try parse first token as date
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                d = datetime.strptime(parts[0], fmt).date()
                break
            except:
                d = None
        if not d:
            continue
        # last token might be amount with +/-
        try:
            amt = float(parts[-1].replace(",",""))
        except:
            continue
        desc = " ".join(parts[1:-1])
        rows.append({"date": d, "description": desc, "amount": amt})
    df = pd.DataFrame(rows)
    return normalize_bank_df(df)

def normalize_bank_df(df: pd.DataFrame) -> pd.DataFrame:
    # Rename common columns
    cols = {c.lower().strip(): c for c in df.columns}
    # Try to map common variants
    mapping = {}
    for c in df.columns:
        lc = c.lower().strip()
        if lc in ("date","transaction date","txn date"):
            mapping[c] = "date"
        elif lc in ("description","details","narrative","particulars"):
            mapping[c] = "description"
        elif lc in ("amount","debit/credit","value","amt"):
            mapping[c] = "amount"
        elif lc in ("reference","ref","id"):
            mapping[c] = "reference"
    df = df.rename(columns=mapping)
    # Coerce required columns
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    else:
        raise ValueError("No 'date' column detected.")
    if "description" not in df.columns:
        df["description"] = ""
    if "amount" not in df.columns:
        raise ValueError("No 'amount' column detected.")
    # Ensure floats
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)
    if "reference" not in df.columns:
        df["reference"] = ""
    # Keep essential cols
    return df[["date","description","amount","reference"]]
