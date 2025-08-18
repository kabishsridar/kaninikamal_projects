#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import sqlite3
from datetime import date, timedelta

DB_FILE = "business_automation.db"


# --------------------------- DB LAYER --------------------------- #
class DB:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    def _connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql, params=(), fetch=False, many=False):
        conn = self._connect()
        cur = conn.cursor()
        try:
            if many:
                cur.executemany(sql, params)
            else:
                cur.execute(sql, params)
            rows = cur.fetchall() if fetch else None
            conn.commit()
            return rows
        finally:
            conn.close()

    def list_values(self, table, key_col):
        rows = self.query(f"SELECT {key_col} FROM {table} ORDER BY {key_col}", fetch=True)
        return [r[key_col] for r in rows]

    def get_scalar(self, sql, params=()):
        rows = self.query(sql, params=params, fetch=True)
        if rows and len(rows) > 0:
            # return the only column of the first row
            keys = rows[0].keys()
            return rows[0][keys[0]]
        return None

    def get_row(self, table, columns, where_sql, where_params):
        sql = f"SELECT {', '.join(columns)} FROM {table} WHERE {where_sql}"
        rows = self.query(sql, where_params, fetch=True)
        return rows[0] if rows else None


# ------------------------ UI METADATA -------------------------- #
# For each table: primary key(s), columns (in display order),
# editable columns, column types, FK mapping, and default-row factory.

def today():
    return date.today().isoformat()

def in_days(n):
    return (date.today() + timedelta(days=n)).isoformat()

TABLES = {
    "customers": {
        "pk": ["customer_id"],
        "columns": ["customer_id", "name", "email", "phone", "company", "address"],
        "editable": ["name", "email", "phone", "company", "address"],  # ids not editable
        "types": {"name": "text", "email": "text", "phone": "text", "company": "text", "address": "text"},
        "fk": {},
        "prefix": "CUST",
        "default": lambda db: {
            "customer_id": next_id(db, "customers", "customer_id", "CUST"),
            "name": "New Customer",
            "email": "",
            "phone": "",
            "company": "",
            "address": ""
        }
    },
    "products": {
        "pk": ["product_id"],
        "columns": ["product_id", "name", "description", "unit_price", "tax_rate"],
        "editable": ["name", "description", "unit_price", "tax_rate"],
        "types": {"name": "text", "description": "text", "unit_price": "float", "tax_rate": "float"},
        "fk": {},
        "prefix": "PROD",
        "default": lambda db: {
            "product_id": next_id(db, "products", "product_id", "PROD"),
            "name": "New Product",
            "description": "",
            "unit_price": 0.0,
            "tax_rate": 18.0
        }
    },
    "quotations": {
        "pk": ["quotation_id"],
        "columns": ["quotation_id", "customer_id", "product_id", "quantity", "discount", "quotation_date"],
        "editable": ["customer_id", "product_id", "quantity", "discount", "quotation_date"],
        "types": {"customer_id": "text", "product_id": "text", "quantity": "int", "discount": "float", "quotation_date": "text"},
        "fk": {"customer_id": ("customers", "customer_id"), "product_id": ("products", "product_id")},
        "prefix": "QUO",
        "default": lambda db: {
            "quotation_id": next_id(db, "quotations", "quotation_id", "QUO"),
            "customer_id": first_or_blank(db, "customers", "customer_id"),
            "product_id": first_or_blank(db, "products", "product_id"),
            "quantity": 1,
            "discount": 0.0,
            "quotation_date": today()
        }
    },
    "orders": {
        "pk": ["order_id"],
        "columns": ["order_id", "customer_id", "quotation_id", "order_date", "status"],
        "editable": ["customer_id", "quotation_id", "order_date", "status"],
        "types": {"customer_id": "text", "quotation_id": "text_or_null", "order_date": "text", "status": "text"},
        "fk": {"customer_id": ("customers", "customer_id"), "quotation_id": ("quotations", "quotation_id")},
        "prefix": "ORD",
        "default": lambda db: {
            "order_id": next_id(db, "orders", "order_id", "ORD"),
            "customer_id": first_or_blank(db, "customers", "customer_id"),
            "quotation_id": None,
            "order_date": today(),
            "status": "Pending"
        }
    },
    "order_items": {
        "pk": ["order_id", "line_no"],
        "columns": ["order_id", "line_no", "product_id", "quantity", "unit_price", "discount"],
        "editable": ["product_id", "quantity", "unit_price", "discount"],  # do not edit composite key inline
        "types": {"product_id": "text", "quantity": "int", "unit_price": "float", "discount": "float"},
        "fk": {"order_id": ("orders", "order_id"), "product_id": ("products", "product_id")},
        "prefix": None,  # composite PK
        "default": lambda db: default_order_item(db)
    },
    "invoices": {
        "pk": ["invoice_id"],
        "columns": ["invoice_id", "quotation_id", "order_id", "customer_id", "invoice_date", "due_date", "status"],
        "editable": ["quotation_id", "order_id", "customer_id", "invoice_date", "due_date", "status"],
        "types": {"quotation_id": "text_or_null", "order_id": "text_or_null", "customer_id": "text", "invoice_date": "text", "due_date": "text", "status": "text"},
        "fk": {"quotation_id": ("quotations", "quotation_id"), "order_id": ("orders", "order_id"), "customer_id": ("customers", "customer_id")},
        "prefix": "INV",
        "default": lambda db: {
            "invoice_id": next_id(db, "invoices", "invoice_id", "INV"),
            "quotation_id": None,
            "order_id": None,
            "customer_id": first_or_blank(db, "customers", "customer_id"),
            "invoice_date": today(),
            "due_date": in_days(14),
            "status": "Pending"
        }
    },
    "payments": {
        "pk": ["payment_id"],
        "columns": ["payment_id", "invoice_id", "amount", "payment_date", "method"],
        "editable": ["invoice_id", "amount", "payment_date", "method"],
        "types": {"invoice_id": "text", "amount": "float", "payment_date": "text", "method": "text"},
        "fk": {"invoice_id": ("invoices", "invoice_id")},
        "prefix": "PAY",
        "default": lambda db: {
            "payment_id": next_id(db, "payments", "payment_id", "PAY"),
            "invoice_id": first_or_blank(db, "invoices", "invoice_id"),
            "amount": 0.0,
            "payment_date": today(),
            "method": "UPI"
        }
    },
}


# Helpers that need DB available (defined after TABLES for clarity)
def next_id(db: DB, table, col, prefix):
    """Generate next ID like PREFIX### scanning existing max numeric suffix."""
    rows = db.query(f"SELECT {col} FROM {table} WHERE {col} LIKE ? ORDER BY {col}", (f"{prefix}%",), fetch=True)
    max_n = 0
    for r in rows:
        val = r[col]
        try:
            n = int(''.join(ch for ch in val if ch.isdigit()))
            if n > max_n:
                max_n = n
        except Exception:
            continue
    return f"{prefix}{max_n + 1:03d}"


def first_or_blank(db: DB, table, col):
    v = db.get_scalar(f"SELECT {col} FROM {table} ORDER BY {col} LIMIT 1")
    return v if v is not None else ""


def default_order_item(db: DB):
    order_id = db.get_scalar("SELECT order_id FROM orders ORDER BY order_date DESC LIMIT 1") or first_or_blank(db, "orders", "order_id")
    if not order_id:
        # If no orders exist, create a temporary one to satisfy NOT NULL constraints
        new_order_id = next_id(db, "orders", "order_id", "ORD")
        db.query(
            "INSERT INTO orders(order_id, customer_id, quotation_id, order_date, status) VALUES (?,?,?,?,?)",
            (new_order_id, first_or_blank(db, "customers", "customer_id"), None, today(), "Pending")
        )
        order_id = new_order_id

    # next line number
    next_ln = db.get_scalar("SELECT COALESCE(MAX(line_no), 0) + 1 FROM order_items WHERE order_id=?", (order_id,)) or 1
    product_id = first_or_blank(db, "products", "product_id")
    unit_price = db.get_scalar("SELECT unit_price FROM products WHERE product_id=?", (product_id,)) or 0.0
    return {
        "order_id": order_id,
        "line_no": int(next_ln),
        "product_id": product_id,
        "quantity": 1,
        "unit_price": float(unit_price),
        "discount": 0.0
    }


# ------------------------- UI COMPONENTS ----------------------- #
class EditableTree(ttk.Treeview):
    """Treeview with inline editing for single cell via Entry/Combobox overlay."""
    def __init__(self, master, table_name, meta, db: DB, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.table = table_name
        self.meta = meta
        self.db = db
        self.active_editor = None  # (widget, item_id, col_id)

        # Styling: larger row height
        style = ttk.Style(self)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

        # close editor on click elsewhere
        self.bind("<Button-1>", self._on_click_anywhere, add="+")
        self.bind("<Double-1>", self._begin_edit)

    def _on_click_anywhere(self, event):
        # commit any active editor if exists and click is outside
        if self.active_editor:
            widget, item_id, col_id = self.active_editor
            if isinstance(widget, ttk.Entry) or isinstance(widget, ttk.Combobox):
                # trigger save by simulating Return
                self._commit_editor()
        # allow normal processing to continue

    def _begin_edit(self, event):
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        item_id = self.identify_row(event.y)
        col_id = self.identify_column(event.x)
        if not item_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        col_name = self["columns"][col_index]

        # disallow editing PK columns
        if col_name in self.meta["pk"]:
            return

        # only allowed editable columns
        if col_name not in self.meta["editable"]:
            return

        bbox = self.bbox(item_id, col_id)
        if not bbox:
            return
        x, y, w, h = bbox
        # get current value
        item = self.item(item_id)
        old_value = item["values"][col_index]

        # FK? -> Combobox; else Entry
        if col_name in self.meta["fk"]:
            ref_table, ref_key = self.meta["fk"][col_name]
            values = self.db.list_values(ref_table, ref_key)
            editor = ttk.Combobox(self, values=values, state="readonly")
            editor.set(old_value or "")
        else:
            editor = ttk.Entry(self)
            editor.insert(0, old_value if old_value is not None else "")

        editor.place(x=x, y=y, width=w, height=h)
        editor.focus()
        editor.bind("<Return>", lambda e: self._commit_editor())
        editor.bind("<Escape>", lambda e: self._cancel_editor())
        editor.bind("<FocusOut>", lambda e: self._commit_editor())
        self.active_editor = (editor, item_id, col_id)

    def _cancel_editor(self):
        if not self.active_editor:
            return
        editor, *_ = self.active_editor
        editor.destroy()
        self.active_editor = None

    def _commit_editor(self):
        if not self.active_editor:
            return
        editor, item_id, col_id = self.active_editor
        col_index = int(col_id.replace("#", "")) - 1
        col_name = self["columns"][col_index]
        new_val = editor.get()
        editor.destroy()
        self.active_editor = None

        # get pk values from row
        vals = list(self.item(item_id, "values"))
        pk_cols = self.meta["pk"]
        pk_vals = [vals[self["columns"].index(pk)] for pk in pk_cols]

        # coerce type
        expected = self.meta["types"].get(col_name, "text")
        try:
            coerced = coerce_value(new_val, expected)
        except ValueError as e:
            messagebox.showerror("Invalid value", str(e))
            return

        # build SQL update
        set_sql = f"{col_name}=?"
        where_sql = " AND ".join([f"{pk}=?" for pk in pk_cols])
        sql = f"UPDATE {self.table} SET {set_sql} WHERE {where_sql}"

        try:
            self.db.query(sql, (coerced, *pk_vals))
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        # update tree cell
        vals[col_index] = coerced
        self.item(item_id, values=vals)


def coerce_value(val, expected_type):
    if expected_type == "int":
        if str(val).strip() == "":
            raise ValueError("This field requires an integer.")
        return int(val)
    if expected_type == "float":
        if str(val).strip() == "":
            raise ValueError("This field requires a number.")
        return float(val)
    if expected_type == "text_or_null":
        return None if str(val).strip() == "" else str(val)
    # default: text
    return str(val)


# ----------------------------- MAIN APP ----------------------------- #
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Business Automation — Admin")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.db = DB()

        # global readable fonts
        self._setup_fonts()

        # notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        # build tabs
        self.trees = {}
        for table_name, meta in TABLES.items():
            self._build_tab(table_name, meta)

    def _setup_fonts(self):
        # Improve default Tk fonts (cross-platform safe choices)
        default_font = tkfont.nametofont("TkDefaultFont")
        text_font = tkfont.nametofont("TkTextFont")
        menu_font = tkfont.nametofont("TkMenuFont")
        heading_font = tkfont.nametofont("TkHeadingFont")

        for f in (default_font, text_font, menu_font):
            f.configure(family="Segoe UI", size=10)

        heading_font.configure(family="Segoe UI Semibold", size=10)

        # Make buttons and labels use padding-friendly style
        style = ttk.Style(self)
        style.configure("TButton", padding=(10, 6))
        style.configure("TLabel", padding=(2, 2))

    def _build_tab(self, table, meta):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text=table.replace("_", " ").title())

        # toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(6, 0))

        btn_refresh = ttk.Button(toolbar, text="⟳ Refresh", command=lambda t=table: self._refresh(t))
        btn_insert = ttk.Button(toolbar, text="➕ Insert Row", command=lambda t=table: self._insert_row(t))
        btn_delete = ttk.Button(toolbar, text="🗑 Delete", command=lambda t=table: self._delete_selected(t))

        btn_refresh.pack(side="left", padx=4)
        btn_insert.pack(side="left", padx=4)
        btn_delete.pack(side="left", padx=4)

        # tree
        cols = meta["columns"]
        tree = EditableTree(frame, table, meta, self.db, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            tree.heading(c, text=c)
            # Wider columns for text-ish fields
            width = 160 if c in ("description", "address") else 120
            tree.column(c, width=width, anchor="center")
        tree.pack(fill="both", expand=True, pady=8)

        # scrollbar
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.place(in_=tree, relx=1.0, rely=0, relheight=1.0, x=-1)

        self.trees[table] = tree
        self._refresh(table)

    def _refresh(self, table):
        meta = TABLES[table]
        tree = self.trees[table]
        tree.delete(*tree.get_children())
        cols = meta["columns"]
        rows = self.db.query(f"SELECT {', '.join(cols)} FROM {table}", fetch=True)
        for r in rows or []:
            vals = [r[c] if r[c] is not None else "" for c in cols]
            tree.insert("", "end", values=vals)

    def _delete_selected(self, table):
        meta = TABLES[table]
        tree = self.trees[table]
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a row to delete.")
            return
        item_id = sel[0]
        vals = list(tree.item(item_id, "values"))
        pk_cols = meta["pk"]
        pk_vals = [vals[tree["columns"].index(pk)] for pk in pk_cols]

        pretty_id = ", ".join(f"{k}={v}" for k, v in zip(pk_cols, pk_vals))
        if not messagebox.askyesno("Confirm delete", f"Delete from {table} where {pretty_id}?"):
            return

        where_sql = " AND ".join([f"{pk}=?" for pk in pk_cols])
        sql = f"DELETE FROM {table} WHERE {where_sql}"
        try:
            self.db.query(sql, tuple(pk_vals))
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        tree.delete(item_id)

    def _insert_row(self, table):
        meta = TABLES[table]
        defaults = meta["default"](self.db)

        # Build INSERT
        cols = meta["columns"]
        # do not include non-editable PKs only if they are auto? Here all PKs are part of defaults too.
        insert_cols = cols
        placeholders = ", ".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO {table} ({', '.join(insert_cols)}) VALUES ({placeholders})"
        values = [defaults.get(c) for c in insert_cols]

        try:
            self.db.query(sql, tuple(values))
        except Exception as e:
            messagebox.showerror("Insert failed", str(e))
            return

        # Add to tree and select it
        tree = self.trees[table]
        # Convert None -> "" for display
        display_vals = [("" if v is None else v) for v in values]
        iid = tree.insert("", "end", values=display_vals)
        tree.selection_set(iid)
        tree.see(iid)


# ----------------------------- ENTRYPOINT ----------------------------- #
if __name__ == "__main__":
    # Wire the helpers that depend on DB into TABLES (they’re referenced above)
    # (No-op here; functions already see DB via parameters.)

    app = App()
    app.mainloop()