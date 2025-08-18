import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "business_automation.db"

class BusinessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Automation System")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f5f5f5")

        style = ttk.Style()
        style.configure("Treeview",
                        font=("Helvetica", 11),
                        rowheight=28)
        style.configure("Treeview.Heading",
                        font=("Helvetica", 12, "bold"))
        style.map("Treeview", background=[("selected", "#cce5ff")])

        style.configure("TButton",
                        font=("Helvetica", 11, "bold"),
                        padding=6,
                        relief="raised")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tables = ["customers", "products", "quotations", "orders", "order_items", "invoices", "payments"]
        self.treeviews = {}

        for table in self.tables:
            frame = tk.Frame(self.notebook, bg="#f5f5f5")
            self.notebook.add(frame, text=table.capitalize())

            label = tk.Label(frame, text=f"{table.capitalize()} Table",
                             font=("Helvetica", 14, "bold"), bg="#f5f5f5", pady=5)
            label.pack()

            tree = ttk.Treeview(frame, show="headings")
            tree.pack(fill="both", expand=True, pady=5)

            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            self.treeviews[table] = tree
            self.populate_table(table)

            # Buttons below each table
            button_frame = tk.Frame(frame, bg="#f5f5f5")
            button_frame.pack(fill="x", pady=5)

            insert_btn = ttk.Button(button_frame, text="➕ Insert Row", command=lambda t=table: self.insert_row(t))
            update_btn = ttk.Button(button_frame, text="✏️ Update Row", command=lambda t=table: self.update_row(t))
            delete_btn = ttk.Button(button_frame, text="🗑️ Delete Row", command=lambda t=table: self.delete_row(t))

            insert_btn.pack(side="left", padx=5)
            update_btn.pack(side="left", padx=5)
            delete_btn.pack(side="left", padx=5)

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    def populate_table(self, table):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cur.fetchall()]

        tree = self.treeviews[table]
        tree.delete(*tree.get_children())
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=120, anchor="center")

        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

        conn.close()

    def insert_row(self, table):
        tree = self.treeviews[table]
        cols = tree["columns"]
        placeholders = ["<Enter value>" for _ in cols]
        tree.insert("", "end", values=placeholders)

    def update_row(self, table):
        tree = self.treeviews[table]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a row to update.")
            return

        item = selected[0]
        values = tree.item(item, "values")
        cols = tree["columns"]

        def save_changes():
            new_values = [entry.get() for entry in entries]
            conn = self.get_connection()
            cur = conn.cursor()

            set_clause = ", ".join([f"{col} = ?" for col in cols[1:]])
            cur.execute(f"UPDATE {table} SET {set_clause} WHERE {cols[0]} = ?",
                        (*new_values[1:], new_values[0]))
            conn.commit()
            conn.close()
            self.populate_table(table)
            edit_win.destroy()

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Row")
        edit_win.geometry("400x400")
        edit_win.configure(bg="#f5f5f5")

        entries = []
        for i, col in enumerate(cols):
            lbl = tk.Label(edit_win, text=col, font=("Helvetica", 11), bg="#f5f5f5")
            lbl.pack(pady=2)
            entry = tk.Entry(edit_win, font=("Helvetica", 11))
            entry.insert(0, values[i])
            entry.pack(pady=2)
            entries.append(entry)

        save_btn = ttk.Button(edit_win, text="💾 Save Changes", command=save_changes)
        save_btn.pack(pady=10)

    def delete_row(self, table):
        tree = self.treeviews[table]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this row?")
        if confirm:
            item = selected[0]
            values = tree.item(item, "values")
            pk_col = tree["columns"][0]

            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table} WHERE {pk_col} = ?", (values[0],))
            conn.commit()
            conn.close()
            self.populate_table(table)


if __name__ == "__main__":
    root = tk.Tk()
    app = BusinessApp(root)
    root.mainloop()
