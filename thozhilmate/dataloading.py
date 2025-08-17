import sqlite3
import pandas as pd

# Define file paths
files = {
    "customers": "customers.csv",
    "products": "products.csv",
    "quotations": "quotations.csv",
    "invoices": "invoices.csv",
    "payments": "payments.csv",
}

# Connect to SQLite database
conn = sqlite3.connect("business_automation.db")

# Load CSVs into SQLite tables
for table, file in files.items():
    df = pd.read_csv(file)
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"Loaded {file} into table '{table}'")

# Create relationships (foreign keys) - SQLite needs explicit schema
cursor = conn.cursor()

cursor.executescript("""
PRAGMA foreign_keys = ON;

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    company TEXT,
    address TEXT
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    unit_price REAL,
    tax_rate REAL
);

-- Quotations
CREATE TABLE IF NOT EXISTS quotations (
    quotation_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    quantity INTEGER,
    discount REAL,
    quotation_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    quotation_id TEXT,
    customer_id TEXT,
    invoice_date TEXT,
    due_date TEXT,
    status TEXT,
    FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    invoice_id TEXT,
    amount REAL,
    payment_date TEXT,
    method TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);
""")

conn.commit()
conn.close()

print("Database created successfully as business_automation.db")
