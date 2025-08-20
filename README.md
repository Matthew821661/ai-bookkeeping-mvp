# AI SaaS Bookkeeping MVP (Streamlit + Python)

**Goal:** A production-lean MVP that ingests bank statements (CSV/Excel/PDF), proposes AI classifications into a South African-style chart of accounts (IFRS for SMEs-aligned), supports VAT (15%, 0%, Exempt), enables **human review/approval**, posts journals to a **General Ledger**, and produces a **Trial Balance**. 

- UI: Streamlit
- Core: Python, pandas
- OCR: pdfplumber (digital PDFs). Image OCR is stubbed for now.
- Storage: In-memory for MVP. Optional Supabase adapter (env-based) included as a stub.
- Exports: CSV/Excel (TB, Journals).

> This MVP is designed to be **cloud-deployable on Streamlit Cloud** for demos. For real production scale, move the API to FastAPI, add a queue (Celery/Redis), and plug in robust OCR (e.g., Google Vision) and a transformer classifier (e.g., LayoutLM, or OpenAI) behind human-in-the-loop approvals.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push this folder to GitHub.
2. In Streamlit Cloud, set the repo and main file as `app.py`.
3. (Optional) Set secrets in **App Settings → Secrets**:
```toml
[supabase]
url = "https://YOUR_SUPABASE_URL"
key = "YOUR_SERVICE_ROLE_OR_ANON_KEY"
```

## Files

```
ai_bookkeeping_mvp/
├─ app.py                     # Streamlit UI
├─ requirements.txt
├─ README.md
├─ .streamlit/secrets.toml    # Template
├─ src/
│  ├─ chart_of_accounts.py    # SA-style IFRS for SMEs account numbers
│  ├─ models.py               # Dataclasses for Transaction & JournalEntry
│  ├─ classifier.py           # Heuristic + (optional) LLM hook
│  ├─ vat.py                  # VAT engine (15%, 0%, Exempt) + validations
│  ├─ ledger.py               # Journal posting + Trial Balance builder
│  ├─ ocr.py                  # Load CSV/Excel/PDF (digital) → transactions
│  ├─ db.py                   # Local (in-memory) + optional Supabase stub
│  └─ reports.py              # Export TB/Journals to CSV/Excel
└─ sample_data/
   ├─ sample_bank.csv
   └─ sample_invoices.csv
```

## Notes on Compliance (South Africa)
- Chart aligns with **IFRS for SMEs** style groupings (1000–1999 Assets, 2000–2999 Liabilities, 3000–3999 Equity, 4000–4999 Revenue, 5000–5999 Expenses).
- VAT: Implements standard 15%, 0%, and Exempt logic with line-level VAT codes. This is **not legal advice**; please review with a professional.
- Companies Act 71 of 2008 & Income Tax Act considerations are architectural (audit trail, records retention, and classification transparency). Extend with specific schedules/returns as needed (e.g., VAT201 export).

## Roadmap
- Replace heuristics with a transformer model or OpenAI function-calling classifier (with a confidence score).
- Add bank feed connectors (FNB/ABSA/etc.) via approved APIs.
- Supabase/Postgres persistence for multi-tenant SaaS + role-based access.
- Mobile receipt OCR (photo → ledger) + duplicate detection.
- Audit trail UI and PDF viewer with line-to-ledger linkbacks.
