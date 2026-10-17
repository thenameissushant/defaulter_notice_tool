"""
Settings in one place so nobody has to dig through the code when the
loan dump layout changes (it does, every few months).

Left side  = the name we use inside the code
Right side = the list of header names that mean the same thing in the dump
"""

COLUMN_ALIASES = {
    "loan_no":      ["loan account no", "loan_account_no", "loan no", "lan", "agreement no"],
    "name":         ["customer name", "borrower name", "name", "customer_name"],
    "address":      ["address", "customer address", "residential address"],
    "mobile":       ["mobile", "mobile no", "phone", "contact no"],
    "emi_amount":   ["emi", "emi amount", "emi_amount", "installment"],
    "overdue":      ["overdue amount", "overdue", "total overdue", "arrears"],
    "outstanding":  ["pos", "principal outstanding", "outstanding", "outstanding amount"],
    "emis_missed":  ["emis missed", "no of emi missed", "emi missed", "unpaid emis"],
    "last_due_date": ["last due date", "due date", "emi due date"],
}

# Columns we cannot work without. Everything else is nice to have.
REQUIRED = ["loan_no", "name", "emi_amount"]

# Bucket rules. Kept as numbers here so Legal can change them without touching logic.
EARLY_STAGE_MAX = 2     # 1 or 2 EMIs missed  -> reminder-type notice
SEVERE_STAGE_MIN = 3    # 3 or more missed    -> legal notice

# Company / advocate details printed on the notice. Replace with real ones.
LENDER_NAME = "ABC Finance Ltd."
ADVOCATE_NAME = "Adv. R. K. Sharma"
ADVOCATE_ENROLMENT = "D/1234/2015"
ADVOCATE_ADDRESS = "Chamber 12, District Court Complex, New Delhi"
NOTICE_RESPONSE_DAYS = 15
