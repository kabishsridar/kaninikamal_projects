import csv
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

original_data = []  # Never modified
current_data = []   # For display

def load_csv():
    global original_data, current_data
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        original_data = list(reader)
        current_data = original_data.copy()

    update_columns()
    display_data(current_data)

def update_columns():
    # First row contains headers
    headers = original_data[0]
    column_menu['menu'].delete(0, 'end')
    for col in headers:
        column_menu['menu'].add_command(label=col, command=tk._setit(column_var, col))
    tree["columns"] = headers
    for h in headers:
        tree.heading(h, text=h)

def apply_filter():
    global current_data
    col_name = column_var.get()
    val = value_var.get()

    if not col_name or not val:
        messagebox.showwarning("Input Error", "Please select a column and enter a value")
        return

    try:
        col_index = original_data[0].index(col_name)
    except ValueError:
        messagebox.showerror("Error", "Column not found")
        return

    try:
        filter_val = float(val)
        current_data = [original_data[0]] + [
            row for row in original_data[1:]
            if float(row[col_index]) >= filter_val
        ]
    except ValueError:
        current_data = [original_data[0]] + [
            row for row in original_data[1:]
            if row[col_index] == val
        ]

    display_data(current_data)

def display_data(data):
    for row in tree.get_children():
        tree.delete(row)
    for row in data[1:]:  # skip header
        tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV Filter App")

    load_btn = tk.Button(root, text="Load CSV", command=load_csv)
    load_btn.pack()

    column_var = tk.StringVar()
    column_menu = tk.OptionMenu(root, column_var, "")
    column_menu.pack()

    value_var = tk.StringVar()
    value_entry = tk.Entry(root, textvariable=value_var)
    value_entry.pack()

    filter_btn = tk.Button(root, text="Apply Filter", command=apply_filter)
    filter_btn.pack()

    tree = ttk.Treeview(root, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
