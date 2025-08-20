from src.classifier import classify
from src.chart_of_accounts import NAME_TO_CODE
def test_interest_exempt():
    code, vat, conf, reason = classify("Interest Received", 10.0)
    assert code == NAME_TO_CODE["interest received"] and vat == "EXEMPT"
def test_negative_defaults_to_expense():
    code, vat, conf, reason = classify("Random shop", -100.0)
    assert code == NAME_TO_CODE["cost of sales"]
def test_keyword_fuel():
    code, vat, conf, reason = classify("Shell Fuel Station", -200.0)
    assert code == NAME_TO_CODE["fuel expense"] and vat == "STD"
