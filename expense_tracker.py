
import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

# ---------------- DATABASE CONNECTION ----------------
def connect_db():
    return oracledb.connect(
        user="system",
        password="Anchal915@",
        dsn="localhost:1521/FREEPDB1"
    )


# ---------------- LOAD EXPENSES ----------------
def load_expenses():
    try:
        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT expense_id, expense_name, amount, category,
                   TO_CHAR(expense_date, 'DD-MON-YYYY')
            FROM system.expenses
            ORDER BY expense_id DESC
        """)

        rows = cur.fetchall()

        for item in expense_table.get_children():
            expense_table.delete(item)

        total = 0

        for row in rows:
            expense_table.insert("", tk.END, values=row)
            total += float(row[2])

        total_label.config(text=f"Total Expenses: ₹{total:.2f}")

        cur.close()
        con.close()

    except Exception as error:
        messagebox.showerror(
            "Database Connection Error",
            f"Could not load expenses.\n\n{error}"
        )


# ---------------- ADD EXPENSE ----------------
def add_expense():
    name = name_entry.get().strip()
    amount_text = amount_entry.get().strip()
    category = category_box.get().strip()

    if not name or not amount_text or not category:
        messagebox.showwarning(
            "Missing Information",
            "Please enter the name, amount and category."
        )
        return

    try:
        amount = float(amount_text)

        if amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Amount must be greater than zero."
            )
            return

    except ValueError:
        messagebox.showwarning(
            "Invalid Amount",
            "Please enter a valid numeric amount."
        )
        return

    con = None
    cur = None

    try:
        con = connect_db()
        cur = con.cursor()

        # Calling the Oracle PL/SQL procedure
        cur.callproc(
            "SYSTEM.ADD_EXPENSE",
            [name, amount, category]
        )

        con.commit()

        name_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        category_box.set("")

        load_expenses()

        messagebox.showinfo(
            "Success",
            "Expense added successfully!"
        )

    except Exception as error:
        if con:
            con.rollback()

        messagebox.showerror(
            "Database Error",
            f"Expense could not be added.\n\n{error}"
        )

    finally:
        if cur:
            cur.close()
        if con:
            con.close()


# ---------------- DELETE EXPENSE ----------------
def delete_expense():
    selected = expense_table.selection()

    if not selected:
        messagebox.showwarning(
            "Select Record",
            "Please select an expense to delete."
        )
        return

    expense_id = expense_table.item(
        selected[0], "values"
    )[0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Do you want to delete this expense?"
    )

    if not confirm:
        return

    con = None
    cur = None

    try:
        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "DELETE FROM system.expenses WHERE expense_id = :id",
            {"id": expense_id}
        )

        con.commit()
        load_expenses()

        messagebox.showinfo(
            "Deleted",
            "Expense deleted successfully!"
        )

    except Exception as error:
        if con:
            con.rollback()

        messagebox.showerror(
            "Database Error",
            str(error)
        )

    finally:
        if cur:
            cur.close()
        if con:
            con.close()


# ---------------- GUI WINDOW ----------------
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("850x600")
root.configure(bg="#F2F4FF")
root.resizable(True, True)

# Heading
heading = tk.Label(
    root,
    text="EXPENSE TRACKER",
    font=("Arial", 25, "bold"),
    bg="#4338CA",
    fg="white",
    pady=18
)
heading.pack(fill="x")

subtitle = tk.Label(
    root,
    text="Manage your daily expenses easily",
    font=("Arial", 11),
    bg="#F2F4FF",
    fg="#555577"
)
subtitle.pack(pady=10)

# Input form
form = tk.Frame(root, bg="white", padx=18, pady=18)
form.pack(padx=25, pady=8, fill="x")

tk.Label(
    form, text="Expense Name",
    bg="white", font=("Arial", 10, "bold")
).grid(row=0, column=0, padx=8, pady=5, sticky="w")

name_entry = tk.Entry(form, width=23, font=("Arial", 11))
name_entry.grid(row=1, column=0, padx=8, pady=5)

tk.Label(
    form, text="Amount (₹)",
    bg="white", font=("Arial", 10, "bold")
).grid(row=0, column=1, padx=8, pady=5, sticky="w")

amount_entry = tk.Entry(form, width=17, font=("Arial", 11))
amount_entry.grid(row=1, column=1, padx=8, pady=5)

tk.Label(
    form, text="Category",
    bg="white", font=("Arial", 10, "bold")
).grid(row=0, column=2, padx=8, pady=5, sticky="w")

category_box = ttk.Combobox(
    form,
    values=[
        "Food", "Travel", "Shopping",
        "Education", "Bills", "Other"
    ],
    width=18,
    state="readonly",
    font=("Arial", 10)
)
category_box.grid(row=1, column=2, padx=8, pady=5)

add_button = tk.Button(
    form,
    text=" + Add Expense ",
    command=add_expense,
    bg="#4F46E5",
    fg="white",
    activebackground="#3730A3",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    padx=10,
    pady=7,
    cursor="hand2"
)
add_button.grid(row=1, column=3, padx=12, pady=5)

# Table
table_frame = tk.Frame(root, bg="#F2F4FF")
table_frame.pack(padx=25, pady=12, fill="both", expand=True)

columns = ("ID", "Name", "Amount", "Category", "Date")

expense_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

for column in columns:
    expense_table.heading(column, text=column)
    expense_table.column(
        column,
        width=140,
        anchor="center"
    )

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=expense_table.yview
)

expense_table.configure(yscrollcommand=scrollbar.set)
expense_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Bottom controls
bottom = tk.Frame(root, bg="#F2F4FF")
bottom.pack(fill="x", padx=25, pady=10)

total_label = tk.Label(
    bottom,
    text="Total Expenses: ₹0.00",
    font=("Arial", 16, "bold"),
    bg="#F2F4FF",
    fg="#15803D"
)
total_label.pack(side="left", pady=8)

delete_button = tk.Button(
    bottom,
    text="Delete Selected",
    command=delete_expense,
    bg="#DC2626",
    fg="white",
    activebackground="#991B1B",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    padx=12,
    pady=7,
    cursor="hand2"
)
delete_button.pack(side="right", padx=5)

refresh_button = tk.Button(
    bottom,
    text="Refresh",
    command=load_expenses,
    bg="#0F766E",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    padx=12,
    pady=7,
    cursor="hand2"
)
refresh_button.pack(side="right", padx=5)

# Load saved records and start GUI
load_expenses()
root.mainloop()
