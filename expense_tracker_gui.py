import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- Database Setup ---
conn = sqlite3.connect('expenses.db')
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

# --- Thresholds and Tips for AI ---
category_thresholds = {
    "food": 15, "transport": 10, "party": 2,
    "entertainment": 10, "shopping": 10, "others": 15
}

category_tips = {
    "food": "🍔 You've spent a lot on food. Try eating at home!",
    "transport": "🚌 Use public transport to save money.",
    "party": "🎉 Parties are fun but budget them wisely.",
    "entertainment": "🎬 Try budget-friendly entertainment.",
    "shopping": "🛍️ Limit impulsive purchases!",
    "others": "💰 Review your miscellaneous spending."
}

# --- GUI Setup ---
root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("1000x550")

# --- Left Menu Frame ---
menu_frame = tk.Frame(root, bg="lightgray", width=200)
menu_frame.pack(side="left", fill="y")

# --- Right Content Frame ---
content_frame = tk.Frame(root)
content_frame.pack(side="right", fill="both", expand=True)

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def set_budget():
    global budget
    try:
        budget = float(budget_entry.get())
        messagebox.showinfo("Success", f"Budget set to ₹{budget}")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid number")

def add_expense_form():
    clear_content()

    def save_expense():
        try:
            cursor.execute('''
                INSERT INTO expenses (date, category, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (date_entry.get(), category_entry.get(), float(amount_entry.get()), desc_entry.get()))
            conn.commit()
            messagebox.showinfo("Success", "Expense added!")
        except:
            messagebox.showerror("Error", "Check your inputs")

    tk.Label(content_frame, text="Add New Expense", font=("Arial", 14, "bold")).pack(pady=10)

    form_frame = tk.Frame(content_frame)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    date_entry = tk.Entry(form_frame)
    date_entry.grid(row=0, column=1)

    tk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    category_entry = tk.Entry(form_frame)
    category_entry.grid(row=1, column=1)

    tk.Label(form_frame, text="Amount (₹):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    amount_entry = tk.Entry(form_frame)
    amount_entry.grid(row=2, column=1)

    tk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    desc_entry = tk.Entry(form_frame)
    desc_entry.grid(row=3, column=1)

    tk.Button(content_frame, text="Save Expense", command=save_expense).pack(pady=10)

def view_expenses():
    clear_content()
    tk.Label(content_frame, text="All Expenses", font=("Arial", 16, "bold")).pack(pady=10)

    columns = ('ID', 'Date', 'Category', 'Amount', 'Description')
    tree = ttk.Treeview(content_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill='both', expand=True)

    cursor.execute("SELECT * FROM expenses")
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

def show_ai_suggestions():
    clear_content()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    cat_sums = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0

    tk.Label(content_frame, text="💡 AI Suggestions", font=("Arial", 16, "bold")).pack(pady=10)
    if total == 0:
        tk.Label(content_frame, text="No data to analyze yet.").pack(pady=10)
        return

    for cat, sum_amt in cat_sums:
        percent = (sum_amt / total) * 100
        if cat in category_thresholds and percent > category_thresholds[cat]:
            tip = category_tips.get(cat, "")
            msg = f"{cat.capitalize()} = {percent:.2f}% of total\n{tip}"
            tk.Label(content_frame, text=msg, fg="red", wraplength=500, justify="left").pack(anchor="w", padx=20, pady=5)
        else:
            tk.Label(content_frame, text=f"{cat.capitalize()} = {percent:.2f}% - ✅ OK", fg="green").pack(anchor="w", padx=20, pady=5)

def show_pie_chart():
    clear_content()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        tk.Label(content_frame, text="No data for pie chart").pack()
        return

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    ax.set_title("Expense Distribution (Pie Chart)")

    canvas = FigureCanvasTkAgg(fig, master=content_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def show_bar_chart():
    clear_content()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        tk.Label(content_frame, text="No data for bar chart").pack()
        return

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    fig, ax = plt.subplots()
    ax.bar(categories, amounts, color='skyblue')
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Expense by Category (Bar Chart)")
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=30)

    canvas = FigureCanvasTkAgg(fig, master=content_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def delete_all_data():
    answer = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL expense data?")
    if answer:
        cursor.execute("DELETE FROM expenses")
        conn.commit()
        messagebox.showinfo("Deleted", "All expense records have been deleted.")
        view_expenses()  # Refresh the table


def delete_specific_expense():
    clear_content()
    tk.Label(content_frame, text="Delete Specific Expense", font=("Arial", 16, "bold")).pack(pady=10)

    form_frame = tk.Frame(content_frame)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Enter Expense ID to Delete:").grid(row=0, column=0, padx=5, pady=5)
    id_entry = tk.Entry(form_frame)
    id_entry.grid(row=0, column=1, padx=5, pady=5)

    def delete_by_id():
        try:
            expense_id = int(id_entry.get())
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            result = cursor.fetchone()
            if result:
                confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete expense ID {expense_id}?")
                if confirm:
                    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                    conn.commit()
                    messagebox.showinfo("Deleted", f"Expense ID {expense_id} deleted successfully.")
                    view_expenses()
            else:
                messagebox.showerror("Error", f"No expense found with ID {expense_id}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric ID")

    tk.Button(content_frame, text="Delete Expense", command=delete_by_id, bg="red", fg="white").pack(pady=10)


# --- Menu Buttons ---
tk.Label(menu_frame, text="Menu", font=("Arial", 14, "bold"), bg="lightgray").pack(pady=10)
tk.Label(root, text="Monthly Budget (₹):").pack()
budget_entry = tk.Entry(root)
budget_entry.pack()
tk.Button(menu_frame, text="Set Budget", command=set_budget).pack(pady=5, fill='x')
tk.Button(menu_frame, text="Add Expense", command=add_expense_form).pack(pady=5, fill='x')
tk.Button(menu_frame, text="View Expenses", command=view_expenses).pack(pady=5, fill='x')
tk.Button(menu_frame, text="Show AI Suggestions", command=show_ai_suggestions).pack(pady=5, fill='x')
tk.Button(menu_frame, text="Show Pie Chart", command=show_pie_chart).pack(pady=5, fill='x')
tk.Button(menu_frame, text="Show Bar Chart", command=show_bar_chart).pack(pady=5, fill='x')
tk.Button(menu_frame, text="Delete Specific Expense", command=delete_specific_expense, bg="orange", fg="white", font=("Arial", 10, "bold")).pack(pady=5, fill='x')
#--- tk.Button(menu_frame, text="Exit", command=root.quit).pack(side="bottom", pady=10, fill='x')---
tk.Button(menu_frame, text="Delete All Data", command=delete_all_data, bg="red", fg="white").pack(pady=5, fill='x')
tk.Button(menu_frame, text="Exit", command=root.quit).pack(side="bottom", pady=10, fill='x')

# --- Start with Viewing Expenses ---
view_expenses()

root.mainloop()
