#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "business_automation.db"

class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def query(self, sql, params=(), fetch=False):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return rows

    def list_values(self, table, key_col):
        rows = self.query(f"SELECT {key_col} FROM {table}", fetch=True)
        return [r[key_col] for r in rows]

class BaseTab(ttk.Frame):
    def __init__(self, parent, db, table_name, columns, insert_sql, fk_specs=None):
        super().__init__(parent)
        self.db = db
        self.table = table_name
        self.columns = columns
        self.insert_sql = insert_sql
        self.fk_specs = fk_specs or {}  # {col: (table, key_col)}
        self._build()

    def _build(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=6, pady=6)

        refresh_btn = ttk.Button(toolbar, text="Refresh", command=self.refresh)
        refresh_btn.pack(side="left")

        # Tree
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=12)
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        # Form
        form = ttk.LabelFrame(self, text="Add New")
        form.pack(fill="x", padx=6, pady=6)

        self.widgets = {}
        for i, col in enumerate(self.columns):
            ttk.Label(form, text=col).grid(row=i, column=0, sticky="w", padx=4, pady=4)
            if col in self.fk_specs:
                table, key_col = self.fk_specs[col]
                values = self.db.list_values(table, key_col)
                w = ttk.Combobox(form, values=values, state="readonly")
            else:
                w = ttk.Entry(form, width=40)
            w.grid(row=i, column=1, sticky="we", padx=4, pady=4)
            self.widgets[col] = w

        add_btn = ttk.Button(form, text="Add Record", command=self.add_record)
        add_btn.grid(row=len(self.columns), column=0, columnspan=2, pady=8)

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = self.db.query(f"SELECT * FROM {self.table}", fetch=True)
        for r in rows:
            self.tree.insert("", "end", values=[r[c] for c in self.columns])

        # refresh combobox FK values
        for col, spec in (self.fk_specs or {}).items():
            table, key_col = spec
            values = self.db.list_values(table, key_col)
            w = self.widgets[col]
            if isinstance(w, ttk.Combobox):
                w["values"] = values

    def add_record(self):
        vals = []
        for c in self.columns:
            w = self.widgets[c]
            if isinstance(w, ttk.Combobox):
                vals.append(w.get())
            else:
                vals.append(w.get().strip())
        if any(v == "" for v in vals):
            messagebox.showerror("Validation", "All fields are required.")
            return
        try:
            self.db.query(self.insert_sql, tuple(vals))
            messagebox.showinfo("Success", f"Inserted into {self.table}.")
            for w in self.widgets.values():
                if isinstance(w, ttk.Combobox):
                    w.set("")
                else:
                    w.delete(0, tk.END)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Automation - Admin")
        self.geometry("1100x720")
        self.db = Database(DB_FILE)
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        tabs = [
            ("customers",
             ["customer_id","name","email","phone","company","address"],
             "INSERT INTO customers(customer_id,name,email,phone,company,address) VALUES (?,?,?,?,?,?)",
             {}),
            ("products",
             ["product_id","name","description","unit_price","tax_rate"],
             "INSERT INTO products(product_id,name,description,unit_price,tax_rate) VALUES (?,?,?,?,?)",
             {}),
            ("quotations",
             ["quotation_id","customer_id","product_id","quantity","discount","quotation_date"],
             "INSERT INTO quotations(quotation_id,customer_id,product_id,quantity,discount,quotation_date) VALUES (?,?,?,?,?,?)",
             {"customer_id": ("customers","customer_id"), "product_id": ("products","product_id")}),
            ("orders",
             ["order_id","customer_id","quotation_id","order_date","status"],
             "INSERT INTO orders(order_id,customer_id,quotation_id,order_date,status) VALUES (?,?,?,?,?)",
             {"customer_id": ("customers","customer_id"), "quotation_id": ("quotations","quotation_id")}),
            ("order_items",
             ["order_id","line_no","product_id","quantity","unit_price","discount"],
             "INSERT INTO order_items(order_id,line_no,product_id,quantity,unit_price,discount) VALUES (?,?,?,?,?,?)",
             {"order_id": ("orders","order_id"), "product_id": ("products","product_id")}),
            ("invoices",
             ["invoice_id","quotation_id","order_id","customer_id","invoice_date","due_date","status"],
             "INSERT INTO invoices(invoice_id,quotation_id,order_id,customer_id,invoice_date,due_date,status) VALUES (?,?,?,?,?,?,?)",
             {"quotation_id": ("quotations","quotation_id"), "order_id": ("orders","order_id"), "customer_id": ("customers","customer_id")}),
            ("payments",
             ["payment_id","invoice_id","amount","payment_date","method"],
             "INSERT INTO payments(payment_id,invoice_id,amount,payment_date,method) VALUES (?,?,?,?,?)",
             {"invoice_id": ("invoices","invoice_id")})
        ]

        for table, cols, ins, fks in tabs:
            tab = BaseTab(nb, self.db, table, cols, ins, fks)
            nb.add(tab, text=table.replace("_"," ").title())

if __name__ == "__main__":
    App().mainloop()
