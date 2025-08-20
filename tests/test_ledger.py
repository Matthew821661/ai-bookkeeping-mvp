from datetime import date
from src.ledger import LedgerState, post_double_entry, trial_balance
def test_trial_balance_balances():
    state = LedgerState(journals=[])
    post_double_entry(state, date.today(), 5000, 4000, 100.0, memo="Test")
    tb = trial_balance(state)
    assert round(tb["TB_Debit"].sum(),2) == round(tb["TB_Credit"].sum(),2)
