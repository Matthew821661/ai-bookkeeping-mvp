from dataclasses import dataclass

@dataclass(frozen=True)
class Account:
    code: int
    name: str
    type: str

CHART = [
    Account(1000, "Bank - Current Account", "Asset"),
    Account(1010, "Accounts Receivable (Debtors Control)", "Asset"),
    Account(1020, "Inventory", "Asset"),
    Account(1030, "VAT Input", "Asset"),
    Account(1040, "Prepayments", "Asset"),
    Account(2000, "Accounts Payable (Creditors Control)", "Liability"),
    Account(2010, "VAT Output", "Liability"),
    Account(2020, "Accruals", "Liability"),
    Account(2030, "Income Received in Advance", "Liability"),
    Account(3000, "Owner's Equity", "Equity"),
    Account(3100, "Retained Earnings", "Equity"),
    Account(4000, "Sales Revenue", "Revenue"),
    Account(4010, "Other Income", "Revenue"),
    Account(4020, "Interest Received", "Revenue"),
    Account(5000, "Cost of Sales", "Expense"),
    Account(5100, "Bank Charges", "Expense"),
    Account(5110, "Fuel Expense", "Expense"),
    Account(5120, "Repairs & Maintenance", "Expense"),
    Account(5130, "Telephone & Internet", "Expense"),
    Account(5140, "Office Supplies", "Expense"),
    Account(5150, "Rent Expense", "Expense"),
    Account(5160, "Salaries & Wages", "Expense"),
    Account(5170, "Professional Fees", "Expense"),
]
CODE_TO_ACCOUNT = {a.code: a for a in CHART}
NAME_TO_CODE = {a.name.lower(): a.code for a in CHART}
