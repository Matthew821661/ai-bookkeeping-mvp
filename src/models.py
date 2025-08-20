from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

VATCode = Literal["STD","ZERO","EXEMPT","NONE"]

class Transaction(BaseModel):
    date: date
    description: str
    amount: float  # inflow +, outflow -
    reference: Optional[str] = None
    source: Optional[str] = None
    currency: str = "ZAR"

class JournalEntry(BaseModel):
    date: date
    account_code: int
    debit: float = 0.0
    credit: float = 0.0
    memo: Optional[str] = None
    vat_code: VATCode = "NONE"
    vat_amount: float = 0.0
    link_ref: Optional[str] = None
    created_by: str = "AI"          
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: Optional[str] = None
