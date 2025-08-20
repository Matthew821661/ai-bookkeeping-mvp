import os, sqlite3
from typing import Any, Dict, List
from datetime import datetime

DB_PATH = os.environ.get("BOOKKEEPING_DB_PATH", "bookkeeping.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jdate TEXT NOT NULL,
    account_code INTEGER NOT NULL,
    debit REAL NOT NULL,
    credit REAL NOT NULL,
    memo TEXT,
    vat_code TEXT,
    vat_amount REAL,
    link_ref TEXT,
    created_by TEXT,
    confidence REAL,
    reason TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journals(jdate);
"""

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()

def save_journal_rows(rows: List[Dict[str, Any]]):
    init_db()
    with get_conn() as conn:
        cur = conn.cursor()
        for r in rows:
            cur.execute("""
                INSERT INTO journals (jdate, account_code, debit, credit, memo, vat_code, vat_amount, link_ref, created_by, confidence, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(r.get("date")),
                int(r["account_code"]),
                float(r.get("debit",0.0)),
                float(r.get("credit",0.0)),
                r.get("memo",""),
                r.get("vat_code","NONE"),
                float(r.get("vat_amount",0.0)),
                r.get("link_ref",""),
                r.get("created_by","Human"),
                float(r.get("confidence",1.0)),
                r.get("reason",""),
                datetime.utcnow().isoformat()
            ))
        conn.commit()

def load_journals() -> List[Dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT jdate, account_code, debit, credit, memo, vat_code, vat_amount, link_ref, created_by, confidence, reason FROM journals ORDER BY id ASC")
        rows = cur.fetchall()
        cols = ["date","account_code","debit","credit","memo","vat_code","vat_amount","link_ref","created_by","confidence","reason"]
        return [dict(zip(cols, r)) for r in rows]

def clear_journals():
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM journals")
        conn.commit()
