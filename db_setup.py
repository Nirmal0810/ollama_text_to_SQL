import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("banking_fb.db")
cur = conn.cursor()

# Enable foreign key constraint
cur.execute("PRAGMA foreign_keys = ON;")

# --- Create tables ---

cur.execute("""
CREATE TABLE IF NOT EXISTS customer (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone_number TEXT,
    city TEXT,
    created_at DATE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS account (
    account_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    account_number TEXT UNIQUE,
    account_type TEXT,
    balance DECIMAL,
    opened_date DATE,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transaction_intent (
    intent_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    account_id INTEGER,
    amount DECIMAL,
    customer_location TEXT,
    intent_date DATE,
    intent_type TEXT,
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY(account_id) REFERENCES account(account_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transaction_history (
    transaction_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    transaction_type TEXT,
    amount DECIMAL,
    transaction_date DATE,
    status TEXT,
    remarks TEXT,
    FOREIGN KEY(account_id) REFERENCES account(account_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS loan_details (
    loan_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    loan_type TEXT,
    loan_amount DECIMAL,
    interest_rate DECIMAL,
    start_date DATE,
    end_date DATE,
    status TEXT,
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);
""")

# --- Insert sample data ---

# Customer records
cur.executemany("""
INSERT INTO customer (first_name, last_name, email, phone_number, city, created_at)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    ("Alice", "Brown", "alice.brown@example.com", "9876543210", "London", "2022-01-15"),
    ("Bob", "Smith", "bob.smith@example.com", "8765432109", "New York", "2021-05-20"),
    ("Charlie", "Davis", "charlie.davis@example.com", "7654321098", "Paris", "2023-03-10"),
    ("Diana", "Johnson", "diana.johnson@example.com", "6543210987", "Tokyo", "2020-07-05")
])

# Account records
cur.executemany("""
INSERT INTO account (customer_id, account_number, account_type, balance, opened_date, status)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, "ACC1001", "Savings", 12500.75, "2022-01-20", "Active"),
    (2, "ACC1002", "Current", 8500.50, "2021-06-01", "Active"),
    (3, "ACC1003", "Savings", 5400.00, "2023-03-15", "Active"),
    (4, "ACC1004", "Loan", -12000.00, "2020-07-10", "Active")
])

# Transaction Intent records
cur.executemany("""
INSERT INTO transaction_intent (customer_id, account_id, amount, customer_location, intent_date, intent_type)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 1, 1000.00, "London", "2025-01-12", "Deposit"),
    (2, 2, 2000.50, "New York", "2025-02-05", "Withdrawal"),
    (3, 3, 150.75, "Paris", "2025-03-18", "Transfer"),
    (4, 4, 5000.00, "Tokyo", "2025-04-10", "Repayment")
])

# Transaction History records
cur.executemany("""
INSERT INTO transaction_history (account_id, transaction_type, amount, transaction_date, status, remarks)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, "Credit", 1000.00, "2025-01-12", "Completed", "Salary credited"),
    (2, "Debit", 2000.50, "2025-02-05", "Completed", "ATM withdrawal"),
    (3, "Transfer", 150.75, "2025-03-18", "Completed", "Transfer to savings"),
    (4, "Debit", 5000.00, "2025-04-10", "Pending", "Loan repayment processing")
])

# Loan details
cur.executemany("""
INSERT INTO loan_details (customer_id, loan_type, loan_amount, interest_rate, start_date, end_date, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    (1, "Home Loan", 250000.00, 6.5, "2021-01-01", "2031-01-01", "Active"),
    (2, "Car Loan", 35000.00, 7.2, "2022-03-01", "2027-03-01", "Active"),
    (3, "Personal Loan", 15000.00, 9.0, "2023-06-01", "2026-06-01", "Active"),
    (4, "Education Loan", 20000.00, 5.5, "2020-09-01", "2025-09-01", "Active")
])

# Commit and close
conn.commit()
conn.close()

print("Banking database 'bank_demo.db' created successfully with sample data.")
