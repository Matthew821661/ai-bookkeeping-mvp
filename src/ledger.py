from __future__ import annotations
import pandas as pd
from typing import List, Optional
from dataclasses import dataclass
from .models import JournalEntry
from .chart_of_accounts import CODE_TO_ACCOUNT

@dataclass
class LedgerState:
    journals: List[JournalEntry]

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for j in self.journals:
            acc = CODE_TO_ACCOUNT.get(j.account_code)
            rows.append({
                "date": j.date,
                "account_code": j.account_code,
                "account_name": acc.name if acc else "",
                "type": acc.type if acc else "",
                "debit": j.debit,
                "credit": j.credit,
                "vat_code": j.vat_code,
                "vat_amount": j.vat_amount,
                "memo": j.memo or "",
                "link_ref": j.link_ref or "",
                "created_by": j.created_by,
                "confidence": j.confidence,
                "reason": j.reason or "",
            })
        return pd.DataFrame(rows)

def post_entry(state: LedgerState, entry: JournalEntry):
    state.journals.append(entry)

def post_double_entry(state: LedgerState, date, debit_acc, credit_acc, amount, memo="", link_ref=None, created_by="AI", vat_code="NONE", confidence=1.0, reason=None):
    from .models import JournalEntry
    amount = round(float(amount), 2)
    if amount == 0:
        return
    post_entry(state, JournalEntry(date=date, account_code=debit_acc, debit=amount, credit=0.0, memo=memo, link_ref=link_ref, created_by=created_by, vat_code=vat_code, confidence=confidence, reason=reason))
    post_entry(state, JournalEntry(date=date, account_code=credit_acc, debit=0.0, credit=amount, memo=memo, link_ref=link_ref, created_by=created_by, vat_code=vat_code, confidence=confidence, reason=reason))

def trial_balance(state: LedgerState) -> pd.DataFrame:
    df = state.to_dataframe()
    if df.empty:
        return pd.DataFrame(columns=["account_code","account_name","type","debit","credit"])
    tb = df.groupby(["account_code","account_name","type"], as_index=False)[["debit","credit"]].sum()
    # Present as per accounting convention
    tb["balance"] = tb["debit"] - tb["credit"]
    # Split into debit/credit columns for presentation
    tb["TB_Debit"] = tb["balance"].apply(lambda x: x if x > 0 else 0.0)
    tb["TB_Credit"] = tb["balance"].apply(lambda x: -x if x < 0 else 0.0)
    return tb[["account_code","account_name","type","TB_Debit","TB_Credit"]].sort_values("account_code")

def reset(state: LedgerState):
    state.journals.clear()
