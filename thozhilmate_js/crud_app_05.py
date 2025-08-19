#!/usr/bin/env python3
"""
app_tkinter_fixed.py

Tkinter admin UI for business_automation.db
Features:
 - Insert (real DB insert with sensible defaults)
 - Edit (popup dialog; PKs locked)
 - Delete (uses actual PK columns; supports composite PKs)
 - Refresh
 - Styled tabs & 3D-like buttons
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import re
from datetime import date, timedelta

DB_FILE = "business_automation.db"


# ------------------------ DB HELPERS ------------------------ #
class DBHelper:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def fetchall(self, sql, params=()):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()

    def fetchone(self, sql, params=()):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchone()

    def execute(self, sql, params=()):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return cur

    def executemany(self, sql, seq_of_params):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.executemany(sql, seq_of_params)
            conn.commit()
            return cur

    # Schema introspection
    def table_info(self, table):
        rows = self.fetchall(f"PRAGMA table_info({table})")
        # returns list of dicts
        return [dict(r) for r in rows]

    def primary_keys(self, table):
        info = self.table_info(table)
        # pk field gives order (0 if not pk)
        pk_cols = [col["name"] for col in sorted(info, key=lambda c: c["pk"]) if col["pk"] > 0]
        return pk_cols

    def columns(self, table):
        info = self.table_info(table)
        return [col["name"] for col in info]

    def foreign_keys(self, table):
        rows = self.fetchall(f"PRAGMA foreign_key_list({table})")
        # returns mapping from local column -> (ref_table, ref_column)
        mapping = {}
        for r in rows:
            # r has keys: id, seq, table, from, to, on_update, on_delete, match
            mapping[r["from"]] = (r["table"], r["to"])
        return mapping

    # Helpers for generating sensible default PKs like CUST001, PROD001, INV001
    def _extract_suffix(self, s):
        # returns trailing digits as int or None
        if s is None:
            return None
        m = re.search(r"(\d+)$", str(s))
        return int(m.group(1)) if m else None

    def generate_next_id(self, table, col_name, prefix_hint=None, pad=3):
        # Query existing values for the column
        rows = self.fetchall(f"SELECT {col_name} FROM {table} WHERE {col_name} IS NOT NULL")
        max_n = 0
        prefix = None
        for r in rows:
            val = r[col_name]
            if val is None:
                continue
            s = str(val)
            m = re.search(r"^([A-Za-z_ \-]*?)(\d+)$", s)
            if m:
                p = m.group(1)
                n = int(m.group(2))
                if prefix is None:
                    prefix = p
                # If prefix mismatches we still use numeric max across prefixes
                if n > max_n:
                    max_n = n
            else:
                # fallback to find digits anywhere at end
                n = self._extract_suffix(s)
                if n and n > max_n:
                    max_n = n
        if prefix is None:
            # derive prefix from hint or column name
            if prefix_hint:
                prefix = str(prefix_hint)
            else:
                # use first 3 letters of column name uppercase
                prefix = col_name[:3].upper()
        next_n = max_n + 1
        return f"{prefix}{str(next_n).zfill(pad)}"

    def first_value(self, table, col):
        r = self.fetchone(f"SELECT {col} FROM {table} WHERE {col} IS NOT NULL LIMIT 1")
        return r[col] if r else None

    def max_line_no_for_order(self, order_id):
        r = self.fetchone("SELECT COALESCE(MAX(line_no),0) as mx FROM order_items WHERE order_id=?", (order_id,))
        return r["mx"] if r else 0

    def insert_row(self, table, field_values):
        # field_values: dict column->value (must include all not-null columns ideally)
        cols = list(field_values.keys())
        placeholders = ",".join(["?"] * len(cols))
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        values = [field_values[c] for c in cols]
        self.execute(sql, tuple(values))

    # Build a sensible default row dict for insertion
    def build_default_row(self, table):
        info = self.table_info(table)
        cols = [c["name"] for c in info]
        notnull = {c["name"]: bool(c["notnull"]) for c in info}
        types = {c["name"]: c["type"].upper() for c in info}
        pks = [c["name"] for c in sorted(info, key=lambda r: r["pk"]) if c["pk"] > 0]
        fks = self.foreign_keys(table)

        defaults = {}
        # Special handling for order_items composite PK
        if table == "order_items":
            # ensure at least one order exists; if not create one
            order_row = self.fetchone("SELECT order_id FROM orders ORDER BY order_date DESC LIMIT 1")
            if order_row:
                order_id = order_row["order_id"]
            else:
                # create a default order (simple)
                order_id = self.generate_next_id("orders", "order_id", prefix_hint="ORD")
                self.execute(
                    "INSERT INTO orders(order_id, customer_id, quotation_id, order_date, status) VALUES (?,?,?,?,?)",
                    (order_id, self.first_value("customers", "customer_id") or "", None, date.today().isoformat(), "Pending")
                )
            # line no
            next_ln = self.max_line_no_for_order(order_id) + 1
            # default product
            product_id = self.first_value("products", "product_id") or ""
            unit_price = 0.0
            if product_id:
                r = self.fetchone("SELECT unit_price FROM products WHERE product_id=?", (product_id,))
                unit_price = float(r["unit_price"]) if r and r["unit_price"] is not None else 0.0
            defaults = {
                "order_id": order_id,
                "line_no": next_ln,
                "product_id": product_id,
                "quantity": 1,
                "unit_price": unit_price,
                "discount": 0.0
            }
            return defaults

        # General handling
        for c in info:
            name = c["name"]
            typ = types.get(name, "")
            val = None

            # Primary key single-column: try to generate next id if text-like
            if name in pks and len(pks) == 1:
                # generate ID
                val = self.generate_next_id(table, name)
                defaults[name] = val
                continue

            # If this column references a FK, try to take a first value from referenced table
            if name in fks:
                ref_table, ref_col = fks[name]
                val = self.first_value(ref_table, ref_col)
                if val is not None:
                    defaults[name] = val
                    continue
                # else leave None or fallback below

            # For typical SQL types
            if "INT" in typ:
                val = 0
            elif "REAL" in typ or "FLOA" in typ or "DOUB" in typ:
                val = 0.0
            elif "DATE" in typ or "TIME" in typ:
                val = date.today().isoformat()
            else:
                # text-like
                val = f"New {name.replace('_',' ').title()}"
            defaults[name] = val

        return defaults

    # Build WHERE clause and values for pk lookup
    def build_pk_where(self, table, row_values):
        # row_values: dict col->val OR sequence aligned to table columns
        info = self.table_info(table)
        cols = [c["name"] for c in info]
        pk_cols = [c["name"] for c in sorted(info, key=lambda r: r["pk"]) if c["pk"] > 0]
        if not pk_cols:
            return None, None
        # Accept row_values as dict or tuple/list
        if isinstance(row_values, dict):
            pk_vals = [row_values.get(pk) for pk in pk_cols]
        else:
            # assume sequence aligned to cols
            mapping = dict(zip(cols, row_values))
            pk_vals = [mapping.get(pk) for pk in pk_cols]
        where_clause = " AND ".join([f"{pk}=?" for pk in pk_cols])
        return where_clause, tuple(pk_vals)


# ------------------------ UI APP ------------------------ #
class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("தொழில்மேட் - ThozilMate")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.db = DBHelper()

        # fonts and styles
        self._configure_style()

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=12)

        # Build tabs
        self.trees = {}
        self._build_all_tabs()

    def _configure_style(self):
        style = ttk.Style(self)
        # choose a modern theme if available
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Fonts
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 11), foreground="#ffffff")
        style.configure("TNotebook.Tab", font=("Segoe UI Semibold", 11), padding=[12, 8])

        # Notebook tab colors
        style.map("TNotebook.Tab", background=[("selected", "#0078D7")], foreground=[("selected", "#ffffff")])

        # Buttons with 3D-like effect
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(10, 6), relief="raised")
        # We'll use regular Tk Buttons for colored 3D effect because ttk styling is platform-dependent.

    def _build_all_tabs(self):
        tables = self.db.fetchall("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        table_names = [r["name"] for r in tables]
        # Order tabs in preferred order if present
        preferred = ["customers", "products", "quotations", "orders", "order_items", "invoices", "payments"]
        ordered = [t for t in preferred if t in table_names] + [t for t in table_names if t not in preferred]

        for table in ordered:
            self._build_tab(table)

    def _build_tab(self, table):
        frame = ttk.Frame(self.nb)
        label = table.replace("_", " ").title()
        self.nb.add(frame, text=label)

        # Top marker
        marker = ttk.Label(frame, text=f"Manage {label}", font=("Segoe UI Semibold", 14))
        marker.pack(anchor="w", pady=(8, 4), padx=8)

        # Toolbar (Refresh + Insert + Edit + Delete)
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", padx=8, pady=6)

        btn_refresh = tk.Button(toolbar, text="⟳ Refresh", command=lambda t=table: self.load_table(t),
                                bg="#f0f0f0", bd=2, relief="raised", padx=10, pady=6)
        btn_insert = tk.Button(toolbar, text="➕ Insert Row", command=lambda t=table: self.insert_row(t),
                               bg="#0078D7", fg="white", bd=3, relief="raised", padx=10, pady=6)
        btn_edit = tk.Button(toolbar, text="✏️ Edit Row", command=lambda t=table: self.edit_selected(t),
                             bg="#2B8A3E", fg="white", bd=3, relief="raised", padx=10, pady=6)
        btn_delete = tk.Button(toolbar, text="🗑 Delete", command=lambda t=table: self.delete_selected(t),
                               bg="#B22222", fg="white", bd=3, relief="raised", padx=10, pady=6)

        btn_refresh.pack(side="left", padx=(0, 6))
        btn_insert.pack(side="left", padx=(0, 6))
        btn_edit.pack(side="left", padx=(0, 6))
        btn_delete.pack(side="left", padx=(0, 6))

        # Treeview
        cols = self.db.columns(table)
        tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            # larger width for description-like columns
            width = 200 if "description" in c or "address" in c else 120
            tree.heading(c, text=c)
            tree.column(c, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Bind double-click on a row to open edit dialog
        tree.bind("<Double-1>", lambda ev, t=table: self.edit_selected(t))

        # Save reference and load data
        self.trees[table] = tree
        self.load_table(table)

    # ---------------- Table operations ---------------- #
    def load_table(self, table):
        tree = self.trees[table]
        # clear
        for iid in tree.get_children():
            tree.delete(iid)
        cols = self.db.columns(table)
        rows = self.db.fetchall(f"SELECT {', '.join(cols)} FROM {table}")
        for r in rows:
            values = [r[c] if r[c] is not None else "" for c in cols]
            tree.insert("", "end", values=values)

    def insert_row(self, table):
        # Build defaults
        defaults = self.db.build_default_row(table)
        if not defaults:
            messagebox.showerror("Insert error", "Could not build default values for this table.")
            return
        try:
            # Insert with columns that appear in defaults only
            cols = list(defaults.keys())
            placeholders = ",".join(["?"] * len(cols))
            sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
            vals = [defaults[c] for c in cols]
            self.db.execute(sql, tuple(vals))
        except Exception as e:
            messagebox.showerror("Insert failed", str(e))
            return
        self.load_table(table)
        # Select last inserted row (best-effort: find by PK)
        pk_cols = self.db.primary_keys(table)
        tree = self.trees[table]
        # find item matching PK(s) from defaults
        for iid in tree.get_children():
            vals = tree.item(iid, "values")
            mapping = dict(zip(self.db.columns(table), vals))
            match = True
            for pk in pk_cols:
                if str(mapping.get(pk)) != str(defaults.get(pk, mapping.get(pk))):
                    match = False
                    break
            if match:
                tree.selection_set(iid)
                tree.see(iid)
                break

    def edit_selected(self, table):
        tree = self.trees[table]
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Edit row", "Please select a row to edit (or double-click it).")
            return
        iid = sel[0]
        cols = self.db.columns(table)
        current_vals = list(tree.item(iid, "values"))
        current_map = dict(zip(cols, current_vals))
        pk_cols = self.db.primary_keys(table)

        # Edit dialog
        dlg = tk.Toplevel(self)
        dlg.title(f"Edit {table}")
        dlg.geometry("520x520")
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        entries = {}
        fk_map = self.db.foreign_keys(table)

        row_i = 0
        for col in cols:
            lbl = ttk.Label(frm, text=col)
            lbl.grid(row=row_i, column=0, sticky="w", pady=6)
            # PKs disabled (not editable)
            if col in pk_cols:
                ent = ttk.Entry(frm)
                ent.insert(0, current_map.get(col, ""))
                ent.config(state="disabled")
            else:
                if col in fk_map:
                    ref_table, ref_col = fk_map[col]
                    # Combobox of possible values from ref_table
                    vals = [v[ref_col] for v in self.db.fetchall(f"SELECT {ref_col} FROM {ref_table}")]
                    ent = ttk.Combobox(frm, values=vals, state="readonly")
                    ent.set(current_map.get(col, ""))
                else:
                    ent = ttk.Entry(frm)
                    ent.insert(0, current_map.get(col, ""))

            ent.grid(row=row_i, column=1, sticky="ew", pady=6, padx=6)
            entries[col] = ent
            row_i += 1

        frm.columnconfigure(1, weight=1)

        # Save button
        def do_save():
            # Build update excluding PKs
            to_update = []
            params = []
            for col, widget in entries.items():
                if col in pk_cols:
                    continue
                value = widget.get()
                # coerce types if needed (basic)
                info = next((it for it in self.db.table_info(table) if it["name"] == col), None)
                typ = info["type"].upper() if info else ""
                if value == "" and info and info["notnull"]:
                    messagebox.showerror("Validation", f"Column {col} cannot be empty.")
                    return
                if value == "":
                    coerced = None
                else:
                    if "INT" in typ:
                        try:
                            coerced = int(value)
                        except ValueError:
                            messagebox.showerror("Validation", f"{col} requires integer value.")
                            return
                    elif "REAL" in typ or "FLOA" in typ or "DOUB" in typ:
                        try:
                            coerced = float(value)
                        except ValueError:
                            messagebox.showerror("Validation", f"{col} requires numeric value.")
                            return
                    else:
                        coerced = value
                to_update.append(f"{col} = ?")
                params.append(coerced)
            if not to_update:
                messagebox.showinfo("No changes", "Nothing to update.")
                dlg.destroy()
                return
            # where clause for PKs
            where_clause, pk_vals = self.db.build_pk_where(table, current_map)
            if where_clause is None:
                messagebox.showerror("Update error", "Table has no primary key; update not supported.")
                dlg.destroy()
                return
            sql = f"UPDATE {table} SET {', '.join(to_update)} WHERE {where_clause}"
            try:
                self.db.execute(sql, tuple(params) + tuple(pk_vals))
            except Exception as e:
                messagebox.showerror("DB error", str(e))
                return
            dlg.destroy()
            self.load_table(table)

        btn_save = tk.Button(dlg, text="💾 Save", bg="#0078D7", fg="white", bd=3, relief="raised", padx=12, pady=6, command=do_save)
        btn_save.pack(side="right", padx=12, pady=12)

    def delete_selected(self, table):
        tree = self.trees[table]
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Select a row to delete.")
            return
        iid = sel[0]
        cols = self.db.columns(table)
        vals = tree.item(iid, "values")
        pk_where, pk_vals = self.db.build_pk_where(table, vals)
        if not pk_where:
            messagebox.showerror("Delete error", "Table has no primary key; unsafe to delete from UI.")
            return
        pretty = " AND ".join([f"{k}={v}" for k, v in zip(self.db.primary_keys(table), pk_vals)])
        if not messagebox.askyesno("Confirm delete", f"Delete row where {pretty}?"):
            return
        try:
            self.db.execute(f"DELETE FROM {table} WHERE {pk_where}", pk_vals)
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return
        self.load_table(table)


# --------------------------- Run --------------------------- #
if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
