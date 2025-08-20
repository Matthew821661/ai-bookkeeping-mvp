from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

VATCode = Literal["STD", "ZERO", "EXEMPT", "NONE"]  # STD=15%, ZERO=0%, EXEMPT=no VAT (e.g., interest), NONE=not applicable

class Transaction(BaseModel):
    date: date
    description: str
    amount: float  # Positive for inflow, negative for outflow
    reference: Optional[str] = None
    source: Optional[str] = None  # e.g., "bank_csv", "bank_pdf", "invoice_csv"
    currency: str = "ZAR"

class JournalEntry(BaseModel):
    date: date
    account_code: int
    debit: float = 0.0
    credit: float = 0.0
    memo: Optional[str] = None
    vat_code: VATCode = "NONE"
    vat_amount: float = 0.0
    link_ref: Optional[str] = None  # to original transaction
    created_by: str = "AI"  # "AI" or "Human"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: Optional[str] = None
