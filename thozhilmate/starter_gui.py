import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "business_automation.db"


class DatabaseManager:
    """Handles all database operations"""

    def __init__(self, db_file):
        self.db_file = db_file

    def execute_query(self, query, params=(), fetch=False):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute(query, params)
        data = cur.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return data


class BaseTab(ttk.Frame):
    """Base class for each table tab"""

    def __init__(self, parent, db, table_name, columns, insert_query):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.columns = columns
        self.insert_query = insert_query

        # UI setup
        self.setup_ui()

    def setup_ui(self):
        # Treeview to show data
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10)

        # Form for new data
        form_frame = ttk.LabelFrame(self, text="Add New Record")
        form_frame.pack(fill="x", pady=10)

        self.entries = {}
        for i, col in enumerate(self.columns):
            ttk.Label(form_frame, text=col).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[col] = entry

        add_btn = ttk.Button(form_frame, text="Add Record", command=self.add_record)
        add_btn.grid(row=len(self.columns), columnspan=2, pady=10)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.db.execute_query(f"SELECT * FROM {self.table_name}", fetch=True)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_record(self):
        values = [self.entries[col].get().strip() for col in self.columns]
        if not all(values):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            self.db.execute_query(self.insert_query, values)
            messagebox.showinfo("Success", f"Record added to {self.table_name}!")
            self.load_data()
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))


class BusinessApp(tk.Tk):
    """Main Application"""

    def __init__(self):
        super().__init__()
        self.title("Business Automation System")
        self.geometry("900x600")

        self.db = DatabaseManager(DB_FILE)

        # Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Tabs
        tabs_config = [
            ("customers", ["customer_id", "name", "email", "phone", "company", "address"],
             "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)"),
            ("products", ["product_id", "name", "description", "unit_price", "tax_rate"],
             "INSERT INTO products VALUES (?, ?, ?, ?, ?)"),
            ("quotations", ["quotation_id", "customer_id", "product_id", "quantity", "discount", "quotation_date"],
             "INSERT INTO quotations VALUES (?, ?, ?, ?, ?, ?)"),
            ("invoices", ["invoice_id", "quotation_id", "customer_id", "invoice_date", "due_date", "status"],
             "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?)"),
            ("payments", ["payment_id", "invoice_id", "amount", "payment_date", "method"],
             "INSERT INTO payments VALUES (?, ?, ?, ?, ?)")
        ]

        for table_name, cols, insert_query in tabs_config:
            tab = BaseTab(notebook, self.db, table_name, cols, insert_query)
            notebook.add(tab, text=table_name.capitalize())


if __name__ == "__main__":
    app = BusinessApp()
    app.mainloop()
