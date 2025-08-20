# AI Bookkeeping SaaS (v1.2 → v1.3 Base)

An AI-driven bookkeeping SaaS designed to surpass Xero and Sage.

## Features
- Upload bank statements (CSV, Excel, PDF)
- AI classification into General Ledger (IFRS for SMEs, SA VAT Act)
- Manual posting option
- Trial Balance & Ledger reports
- Toggle AI (OpenAI GPT) and database (Supabase or SQLite)
- Sample data included

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
- Main file: `app.py`
- Python version: `3.10`
- Add secrets if using GPT or Supabase:
  ```
  OPENAI_API_KEY = sk-...
  SUPABASE_URL = https://xxx.supabase.co
  SUPABASE_KEY = your_key
  ```

## Next Steps
- v1.3: Debtors/Creditors & Invoice matching
- v1.4: AI "Explain This Entry" button
