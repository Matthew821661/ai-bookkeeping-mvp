import re
from typing import Tuple, Dict, Any
from .chart_of_accounts import NAME_TO_CODE

# Simple heuristics to bootstrap classification
KEYWORD_TO_ACCOUNT = {
    r"\b(bank\s?charges|monthly\s?fee|service\s?fee)\b": "Bank Charges",
    r"\b(fuel|garage|shell|total|engen|bp)\b": "Fuel Expense",
    r"\b(airtime|data|vodacom|mtn|cell c|telkom)\b": "Telephone & Internet",
    r"\b(rent|lease)\b": "Rent Expense",
    r"\b(salary|wages|payroll)\b": "Salaries & Wages",
    r"\b(repairs?|maintenance)\b": "Repairs & Maintenance",
    r"\b(stationery|ink|paper|office)\b": "Office Supplies",
    r"\b(interest\s+received)\b": "Interest Received",
    r"\b(payment\s+from|deposit|received)\b": "Sales Revenue",
    r"\b(sales|invoice)\b": "Sales Revenue",
    r"\b(shoprite|pick ?n ?pay|spar|checkers|woolworths)\b": "Cost of Sales",
}

def classify(description: str, amount: float) -> Tuple[int, str, float, str]:
    """
    Returns (account_code, vat_code, confidence, reason)
    amount > 0 = inflow (likely income, debtor receipt, etc.)
    amount < 0 = outflow (expense, supplier, etc.)
    """
    desc = (description or "").lower()

    # Interest Received (often positive)
    if "interest" in desc and amount > 0:
        return NAME_TO_CODE["interest received"], "EXEMPT", 0.95, "Keyword match: interest received (exempt)"

    for pattern, account_name in KEYWORD_TO_ACCOUNT.items():
        if re.search(pattern, desc):
            # VAT defaults: expenses STD, revenue STD unless keyword signals EXEMPT
            vat_code = "STD"
            if account_name == "Interest Received":
                vat_code = "EXEMPT"
            if amount > 0 and account_name == "Sales Revenue":
                vat_code = "STD"
            code = NAME_TO_CODE[account_name.lower()]
            return code, vat_code, 0.75, f"Heuristic '{pattern}' → {account_name}"

    # Fallbacks by sign
    if amount > 0:
        return NAME_TO_CODE["sales revenue"], "STD", 0.55, "Fallback: positive amount assumed revenue"
    else:
        return NAME_TO_CODE["cost of sales"], "STD", 0.55, "Fallback: negative amount assumed expense"
