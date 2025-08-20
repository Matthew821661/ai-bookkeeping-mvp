from typing import Tuple
def compute_vat(amount_inclusive: float, vat_code: str) -> Tuple[float, float]:
    code = (vat_code or "NONE").upper()
    if code == "STD":
        vat = round(amount_inclusive * 15.0 / 115.0, 2)
        net = round(amount_inclusive - vat, 2)
        return vat, net
    elif code == "ZERO":
        return 0.0, round(amount_inclusive, 2)
    elif code in ("EXEMPT","NONE"):
        return 0.0, round(amount_inclusive, 2)
    return 0.0, round(amount_inclusive, 2)
