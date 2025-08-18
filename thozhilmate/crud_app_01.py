import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "business_automation.db"

# ---------------- Backend ---------------- #
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()

    def fetch(self, table):
        self.cur.execute(f"SELECT * FROM {table}")
        return self.cur.fetchall()

    def update(self, table, row_id, col_name, new_val):
        self.cur.execute(f"UPDATE {table} SET {col_name}=? WHERE id=?", (new_val, row_id))
        self.conn.commit()

    def delete(self, table, row_id):
        self.cur.execute(f"DELETE FROM {table} WHERE id=?", (row_id,))
        self.conn.commit()

    def insert(self, table, cols, placeholders):
        self.cur.execute(
            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",
            placeholders
        )
        self.conn.commit()
        return self.cur.lastrowid

# ---------------- Frontend ---------------- #
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CRM/ERP Manager")
        self.db = Database()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tables = {
            "customers": ["id", "name", "email", "phone"],
            "products": ["id", "name", "price", "stock"]
        }

        for table, cols in self.tables.items():
            self.create_tab(table, cols)

    def create_tab(self, table, columns):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=table.capitalize())

        # Treeview
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        tree.pack(fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=100, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Load data
        self.load_data(table, tree, columns)

        # Bind events
        tree.bind("<Double-1>", lambda e, t=table, tr=tree, c=columns: self.edit_cell(e, t, tr, c))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="➕ Insert Row", command=lambda t=table, tr=tree, c=columns: self.insert_row(t, tr, c)).pack(side="left", padx=5, pady=5)
        ttk.Button(btn_frame, text="🗑 Delete Row", command=lambda t=table, tr=tree: self.delete_row(t, tr)).pack(side="left", padx=5, pady=5)

        # Store reference
        setattr(self, f"{table}_tree", tree)

    def load_data(self, table, tree, columns):
        tree.delete(*tree.get_children())
        rows = self.db.fetch(table)
        for row in rows:
            tree.insert("", "end", values=row)

    def edit_cell(self, event, table, tree, columns):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        col_name = columns[col_index]

        if col_name == "id":  # Don't allow editing ID
            return

        item = tree.item(row_id)
        old_value = item["values"][col_index]

        # Get row DB id
        db_id = item["values"][0]

        # Place Entry box
        x, y, w, h = tree.bbox(row_id, col_id)
        entry = ttk.Entry(tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, old_value)
        entry.focus()

        def save_edit(event=None):
            new_val = entry.get()
            entry.destroy()

            # Update DB
            self.db.update(table, db_id, col_name, new_val)

            # Update UI
            values = list(item["values"])
            values[col_index] = new_val
            tree.item(row_id, values=values)

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def delete_row(self, table, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a row to delete.")
            return
        item = tree.item(selected[0])
        row_id = item["values"][0]

        confirm = messagebox.askyesno("Confirm", f"Delete {table} row with id={row_id}?")
        if confirm:
            self.db.delete(table, row_id)
            tree.delete(selected[0])

    def insert_row(self, table, tree, columns):
        placeholder = ["<new>" if col != "id" else "" for col in columns]
        # Insert into DB with default placeholders
        db_cols = [c for c in columns if c != "id"]
        db_values = [""] * len(db_cols)
        new_id = self.db.insert(table, db_cols, db_values)

        placeholder[0] = new_id  # Set real ID
        tree.insert("", "end", values=placeholder)


# ---------------- Run ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()