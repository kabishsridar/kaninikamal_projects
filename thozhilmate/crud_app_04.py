import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "business_automation.db"

class BusinessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Automation System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f2f5")

        # Style setup
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview styling
        style.configure("Treeview",
                        font=("Segoe UI", 11),
                        rowheight=28,
                        background="#ffffff",
                        fieldbackground="#f9f9f9")
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 12, "bold"),
                        foreground="white",
                        background="#0078D7")
        style.map("Treeview", background=[("selected", "#4a90e2")])

        # Button styling
        self.button_style = {"font": ("Segoe UI", 11, "bold"),
                             "bg": "#0078D7",
                             "fg": "white",
                             "relief": "raised",
                             "bd": 3,
                             "activebackground": "#005a9e"}

        # Notebook (Tabs) styling
        style.configure("TNotebook.Tab",
                        font=("Segoe UI", 12, "bold"),
                        padding=[15, 8],
                        background="#d9e6f2")
        style.map("TNotebook.Tab",
                  background=[("selected", "#0078D7")],
                  foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tables = ["customers", "products", "quotations", "orders", "order_items", "invoices", "payments"]
        self.treeviews = {}

        for table in self.tables:
            self.create_tab(table)

    def run_query(self, query, params=()):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def create_tab(self, table):
        frame = tk.Frame(self.notebook, bg="#f0f2f5")
        self.notebook.add(frame, text=table.capitalize())

        # Treeview
        columns = [col[1] for col in self.run_query(f"PRAGMA table_info({table})").fetchall()]
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=120, anchor="center")

        self.treeviews[table] = tree
        self.load_data(table)

        # Buttons
        btn_frame = tk.Frame(frame, bg="#f0f2f5")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Insert Row", command=lambda t=table: self.insert_row(t), **self.button_style).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Delete Row", command=lambda t=table: self.delete_row(t), **self.button_style).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Save Edits", command=lambda t=table: self.update_row(t), **self.button_style).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Refresh", command=lambda t=table: self.load_data(t), **self.button_style).grid(row=0, column=3, padx=10)

        # User marker
        marker_label = tk.Label(frame, text=f"Manage {table.capitalize()} Table", font=("Segoe UI", 14, "bold"), bg="#f0f2f5", fg="#333")
        marker_label.pack(pady=5)

    def load_data(self, table):
        tree = self.treeviews[table]
        for item in tree.get_children():
            tree.delete(item)
        rows = self.run_query(f"SELECT * FROM {table}").fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

    def insert_row(self, table):
        columns = [col[1] for col in self.run_query(f"PRAGMA table_info({table})").fetchall()]
        placeholders = ["?" for _ in columns]
        default_values = [None if col == "id" else f"New {col}" for col in columns]
        try:
            self.run_query(f"INSERT INTO {table} ({','.join(columns[1:])}) VALUES ({','.join(placeholders[1:])})", tuple(default_values[1:]))
            self.load_data(table)
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))

    def delete_row(self, table):
        tree = self.treeviews[table]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Delete Error", "No row selected.")
            return
        item = tree.item(selected)
        row_id = item["values"][0]
        try:
            self.run_query(f"DELETE FROM {table} WHERE id=?", (row_id,))
            self.load_data(table)
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def update_row(self, table):
        tree = self.treeviews[table]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Update Error", "No row selected.")
            return
        item = tree.item(selected)
        row_values = item["values"]
        columns = [col[1] for col in self.run_query(f"PRAGMA table_info({table})").fetchall()]
        try:
            set_clause = ",".join([f"{col}=?" for col in columns[1:]])
            self.run_query(f"UPDATE {table} SET {set_clause} WHERE id=?", tuple(row_values[1:] + [row_values[0]]))
            self.load_data(table)
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessApp(root)
    root.mainloop()