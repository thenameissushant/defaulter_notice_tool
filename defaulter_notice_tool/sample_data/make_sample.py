"""Makes a fake dump so the tool can be demoed without any real customer data."""
import random
import pandas as pd

random.seed(7)
first = ["Amit", "Rahul", "Priya", "Neha", "Vikram", "Sunita", "Rohit", "Anjali", "Manoj", "Kavita", "Deepak", "Pooja"]
last = ["Sharma", "Verma", "Singh", "Gupta", "Yadav", "Mishra", "Kumar", "Jain", "Chauhan", "Malik"]
cities = ["Gurgaon", "Noida", "Faridabad", "Delhi", "Ghaziabad", "Rohtak"]

rows = []
for i in range(1, 301):
    emi = random.choice([8500, 12000, 15500, 21000, 33000])
    missed = random.choices([0, 1, 2, 3, 4, 5], weights=[30, 25, 20, 15, 6, 4])[0]
    rows.append({
        "Loan Account No": f"LN{100000 + i}",
        "Customer Name": f"{random.choice(first)} {random.choice(last)}",
        "Address": f"H.No {random.randint(1, 400)}, Sector {random.randint(1, 60)}, {random.choice(cities)}",
        "Mobile": str(random.randint(7000000000, 9999999999)),
        "EMI Amount": emi,
        "Overdue Amount": emi * missed + (random.randint(0, 900) if missed else 0),
        "POS": emi * random.randint(12, 60),
    })

# a few messy rows, because real dumps are never clean
rows[10]["EMI Amount"] = 0
rows.append({})  # blank row
pd.DataFrame(rows).to_excel("sample_data/loan_dump_sample.xlsx", index=False)
print("sample_data/loan_dump_sample.xlsx created")
