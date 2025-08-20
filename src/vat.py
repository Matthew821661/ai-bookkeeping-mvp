from typing import Tuple
def compute_vat(amount_inclusive: float, vat_code: str) -> Tuple[float, float]:
    """
    Returns (vat_amount, net_amount) given a VAT code.
    STD = 15% inclusive
    ZERO = 0%
    EXEMPT = no VAT (e.g., interest)
    NONE = not applicable/not processed
    """
    code = (vat_code or "NONE").upper()
    if code == "STD":
        vat_amount = round(amount_inclusive * 15.0 / 115.0, 2)
        net = round(amount_inclusive - vat_amount, 2)
        return vat_amount, net
    elif code == "ZERO":
        return 0.0, round(amount_inclusive, 2)
    elif code in ("EXEMPT", "NONE"):
        return 0.0, round(amount_inclusive, 2)
    else:
        return 0.0, round(amount_inclusive, 2)

def vat_balancing_entries(date, link_ref, vat_code, vat_amount):
    """
    Returns (input_vat_entry, output_vat_entry) depending on vat_code and sign.
    For simplicity:
      - Positive amount (expense/purchase) with STD VAT → VAT Input (1030) debit
      - Negative amount (income/sale) with STD VAT → VAT Output (2010) credit
    """
    from .models import JournalEntry
    if vat_amount == 0 or vat_code not in ("STD", "ZERO"):
        return None, None

    if vat_code == "STD":
        # Caller must decide direction via sign of original line.
        # We'll leave creation to ledger.post_with_vat for correct direction.
        pass
    return None, None
