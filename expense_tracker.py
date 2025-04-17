import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt

# Database setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
''')

budget = 0.0

# GUI setup
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("850x500")

menu_frame = tk.Frame(root, width=200, bg="#e0e0e0")
menu_frame.pack(side="left", fill="y")

content_frame = tk.Frame(root)
content_frame.pack(side="right", fill="both", expand=True)

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

# Budget UI
def set_budget_ui():
    clear_content()
    tk.Label(content_frame, text="Set Monthly Budget (₹):", font=("Arial", 12)).pack(pady=10)
    budget_entry = tk.Entry(content_frame)
    budget_entry.pack()

    def save_budget():
        global budget
        try:
            budget = float(budget_entry.get())
            messagebox.showinfo("Success", f"✅ Budget set to ₹{budget}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    tk.Button(content_frame, text="Set Budget", command=save_budget).pack(pady=5)

# Add Expense UI
def add_expense_ui():
    clear_content()
    tk.Label(content_frame, text="Add Expense", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(content_frame, text="Date (YYYY-MM-DD):").pack()
    date_entry = tk.Entry(content_frame)
    date_entry.pack()

    tk.Label(content_frame, text="Category:").pack()
    category_entry = tk.Entry(content_frame)
    category_entry.pack()

    tk.Label(content_frame, text="Amount (₹):").pack()
    amount_entry = tk.Entry(content_frame)
    amount_entry.pack()

    tk.Label(content_frame, text="Description:").pack()
    desc_entry = tk.Entry(content_frame)
    desc_entry.pack()

    def add_expense():
        try:
            cursor.execute('''
                INSERT INTO expenses (date, category, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (
                date_entry.get(),
                category_entry.get(),
                float(amount_entry.get()),
                desc_entry.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "✅ Expense added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {e}")

    tk.Button(content_frame, text="Add Expense", command=add_expense).pack(pady=5)

# View Expenses UI
def view_expenses_ui():
    clear_content()
    tk.Label(content_frame, text="All Expenses", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(content_frame, columns=('ID', 'Date', 'Category', 'Amount', 'Description'), show='headings')
    for col in ('ID', 'Date', 'Category', 'Amount', 'Description'):
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill='both', expand=True)

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert('', 'end', values=row)

# Bar Chart
def show_bar_chart():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No expenses to display.")
        return

    categories = [row[0] for row in data]
    totals = [row[1] for row in data]

    plt.figure(figsize=(6,4))
    plt.bar(categories, totals, color='orange')
    plt.title("Expenses by Category (Bar Chart)")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.tight_layout()
    plt.show()

# Pie Chart
def show_pie_chart():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No expenses to display.")
        return

    categories = [row[0] for row in data]
    totals = [row[1] for row in data]

    plt.figure(figsize=(5,5))
    plt.pie(totals, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title("Expenses Distribution (Pie Chart)")
    plt.tight_layout()
    plt.show()

# Export report
def export_report():
    try:
        import pandas as pd
        cursor.execute("SELECT * FROM expenses")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["ID", "Date", "Category", "Amount", "Description"])
        df.to_csv("expense_report.csv", index=False)
        messagebox.showinfo("Exported", "📄 Report exported as 'expense_report.csv'")
    except ImportError:
        messagebox.showerror("Error", "Please install pandas to export reports.")

# Sidebar buttons
tk.Label(menu_frame, text="Menu", font=("Arial", 14, "bold"), bg="#e0e0e0").pack(pady=10)
tk.Button(menu_frame, text="Set Budget", width=20, command=set_budget_ui).pack(pady=5)
tk.Button(menu_frame, text="Add Expense", width=20, command=add_expense_ui).pack(pady=5)
tk.Button(menu_frame, text="View Expenses", width=20, command=view_expenses_ui).pack(pady=5)
tk.Button(menu_frame, text="Show Bar Chart", width=20, command=show_bar_chart).pack(pady=5)
tk.Button(menu_frame, text="Show Pie Chart", width=20, command=show_pie_chart).pack(pady=5)
tk.Button(menu_frame, text="Export Report", width=20, command=export_report).pack(pady=5)
tk.Button(menu_frame, text="Exit", width=20, command=root.quit).pack(pady=5)

root.mainloop()
