import os, json, re
from typing import Tuple
MODEL = os.environ.get("OPENAI_MODEL","gpt-4o-mini")
def _build_prompt(description: str, amount: float) -> str:
    sign = "inflow (likely income/receipt)" if amount > 0 else "outflow (likely expense/payment)"
    return f"""
You are a South Africa-focused bookkeeping assistant following IFRS for SMEs and VAT rules (15% STD, ZERO, EXEMPT).
Transaction: "{description}"
Amount: {amount} ({sign})
Return JSON with keys: account_name, vat_code (STD/ZERO/EXEMPT/NONE), confidence (0..1), reason.
Only output JSON.
"""
def classify_with_openai(description: str, amount: float) -> Tuple[str,str,float,str]:
    api_key = os.environ.get("OPENAI_API_KEY","")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(description, amount)
    resp = client.chat.completions.create(model=MODEL, messages=[{"role":"system","content":"You are a precise bookkeeping classifier."},{"role":"user","content":prompt}], temperature=0.0, max_tokens=200)
    txt = resp.choices[0].message.content.strip()
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise RuntimeError("No JSON found from model")
    data = json.loads(m.group(0))
    return str(data.get("account_name","")), str(data.get("vat_code","NONE")).upper(), float(data.get("confidence",0.0)), str(data.get("reason",""))
