# AI SaaS Bookkeeping (v1.2)

MVP with AI classification (heuristics + optional OpenAI), human-in-the-loop review, GL posting, Trial Balance, VAT logic, exports, SQLite persistence, and Supabase cloud save.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Env
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_SERVICE_OR_ANON_KEY
```

## v1.2 Adds
- OpenAI classifier toggle (fallback to heuristics)
- Supabase REST adapter for suggestions+journals
- SQLite persistence toggle
- Tests + golden dataset
