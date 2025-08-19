#!/usr/bin/env python3
import sqlite3
import pandas as pd
from pathlib import Path

DB_FILE = "business_automation.db"
CSV_DIR = Path("..\\thozhilmate\\")

FILES = {
    "customers": CSV_DIR / "customers.csv",
    "products": CSV_DIR / "products.csv",
    "quotations": CSV_DIR / "quotations.csv",
    "orders": CSV_DIR / "orders.csv",
    "order_items": CSV_DIR / "order_items.csv",
    "invoices": CSV_DIR / "invoices.csv",
    "payments": CSV_DIR / "payments.csv",
}

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS quotations;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    address TEXT
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    unit_price REAL NOT NULL,
    tax_rate REAL NOT NULL
);

CREATE TABLE quotations (
    quotation_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    discount REAL DEFAULT 0,
    quotation_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    quotation_id TEXT,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE order_items (
    order_id TEXT NOT NULL,
    line_no INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount REAL DEFAULT 0,
    PRIMARY KEY (order_id, line_no),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE invoices (
    invoice_id TEXT PRIMARY KEY,
    quotation_id TEXT,
    order_id TEXT,
    customer_id TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_date TEXT NOT NULL,
    method TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""

def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
 
    for table, path in FILES.items():
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Loaded {path} -> {table} ({len(df)} rows)")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_FILE}")

if __name__ == "__main__":
    main()
