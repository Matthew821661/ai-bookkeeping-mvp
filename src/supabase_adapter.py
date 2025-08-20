import os, requests, time
from typing import List, Dict, Any
BASE = os.environ.get("SUPABASE_URL","").rstrip("/")
KEY = os.environ.get("SUPABASE_KEY","")
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type":"application/json"}
def _post(table: str, rows: List[Dict[str, Any]]):
    if not BASE or not KEY: raise RuntimeError("Supabase credentials not set")
    url = f"{BASE}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=rows, params={"return":"minimal"})
    if not r.ok: raise RuntimeError(f"Supabase error {r.status_code}: {r.text}")
def save_journals(rows: List[Dict[str, Any]]):
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = [{
        "jdate": str(r.get("date")),
        "account_code": int(r.get("account_code",0)),
        "debit": float(r.get("debit",0.0)),
        "credit": float(r.get("credit",0.0)),
        "memo": r.get("memo",""),
        "vat_code": r.get("vat_code","NONE"),
        "vat_amount": float(r.get("vat_amount",0.0)),
        "link_ref": r.get("link_ref",""),
        "created_by": r.get("created_by","Human"),
        "confidence": float(r.get("confidence",1.0)),
        "reason": r.get("reason",""),
        "created_at": now,
    } for r in rows]
    _post("journals", payload)
def save_suggestions(rows: List[Dict[str, Any]]):
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = [{
        "tdate": str(r.get("date")),
        "description": r.get("description",""),
        "amount": float(r.get("amount",0.0)),
        "suggested_account": int(r.get("suggested_account",0)),
        "vat_code": r.get("vat_code","NONE"),
        "confidence": float(r.get("confidence",1.0)),
        "reason": r.get("reason",""),
        "link_ref": r.get("link_ref",""),
        "created_at": now,
    } for r in rows]
    _post("suggestions", payload)
