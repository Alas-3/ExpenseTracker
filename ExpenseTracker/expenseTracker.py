import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk
import sqlite3
import datetime
import calendar

# Create a database connection
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()

# Create expense table
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY,
             date TEXT,
             amount REAL,
             category TEXT,
             description TEXT)''')

conn.commit()

# Function to update existing data in the database to match the new date format
def update_date_format():
    c.execute("SELECT id, date FROM expenses")
    expenses = c.fetchall()
    for expense in expenses:
        expense_id = expense[0]
        old_date_str = expense[1]
        c.execute("UPDATE expenses SET date = ? WHERE id = ?", (old_date_str, expense_id))
    conn.commit()
    messagebox.showinfo("Success", "Date format updated successfully!")

# Call the function to update the date format
update_date_format()

# Function to add expense to database
def add_expense():
    raw_date = date_entry.get_date()
    date = raw_date.strftime('%Y-%m-%d')
    amount = amount_entry.get()
    category = category_var.get()
    description = description_entry.get("1.0", tk.END)

    # Ensure amount format
    if amount and '.' not in amount:
        amount += '.00'

    if date and amount and category and category != "Select Category":
        c.execute('''INSERT INTO expenses (date, amount, category, description)
                     VALUES (?, ?, ?, ?)''', (date, amount, category, description))
        conn.commit()
        messagebox.showinfo("Success", "Expense added successfully!")
        clear_entries()
        refresh_expense_list()  
        update_dashboard()  
    else:
        messagebox.showerror("Error", "Please fill in all fields and select a category.")

# Function to remove expense from database
def remove_expense():
    selected_item = expense_tree.selection()
    if selected_item:
        expense_id = expense_tree.item(selected_item, 'values')[0]
        c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        messagebox.showinfo("Success", "Expense removed successfully!")
        refresh_expense_list()  
        update_dashboard()  
    else:
        messagebox.showerror("Error", "Please select an expense to remove.")

# Function to clear entry fields
def clear_entries():
    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete("1.0", tk.END)

# Function to refresh expense list
def refresh_expense_list():
    expense_tree.delete(*expense_tree.get_children())  
    populate_expense_list()

# Function to populate expense list
def populate_expense_list():
    c.execute("SELECT * FROM expenses")
    expenses = c.fetchall()
    for expense in expenses:
        formatted_amount = f"₱{expense[2]:,.2f}"
        expense_tree.insert('', 'end', values=(expense[0], expense[1], formatted_amount, expense[3], expense[4]))

# Function to update dashboard statistics
def update_dashboard():
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    start_of_prev_month = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    end_of_prev_month = start_of_month - datetime.timedelta(days=1)

    total_today = calculate_total_expense(today, today)
    total_week = calculate_total_expense(start_of_week, end_of_week)
    total_month = calculate_total_expense(start_of_month, end_of_month)
    total_prev_month = calculate_total_expense(start_of_prev_month, end_of_prev_month)

    today_label.config(text=f"Today's Expense: ₱{total_today:,.2f}")
    week_label.config(text=f"This Week's Expense: ₱{total_week:,.2f}")
    month_label.config(text=f"This Month's Expense: ₱{total_month:,.2f}")
    prev_month_label.config(text=f"Last Month's Expense: ₱{total_prev_month:,.2f}")

# Function to calculate total expense within a date range
def calculate_total_expense(start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    c.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (start_date_str, end_date_str))
    total_expense = c.fetchone()[0]
    return total_expense if total_expense is not None else 0

# Function to switch to expense list page
def show_expense_list():
    expense_list_frame.lift()  
    refresh_expense_list()
    update_dashboard()  

# Function to switch back to main page
def show_main_page():
    main_frame.lift()  

# Main window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("800x600")

bg_color = "#f0f0f0"
accent_color = "#4CAF50"
text_color = "#333333"

root.config(bg=bg_color)
root.attributes('-fullscreen', True)

main_frame = tk.Frame(root, bg=bg_color)
main_frame.place(relwidth=1, relheight=1)  

title_label = tk.Label(main_frame, text="Expense Tracker", bg=bg_color, fg=text_color, font=("Helvetica", 30, "bold"))
title_label.pack(pady=(30, 50))

expense_frame = tk.Frame(main_frame, bg=bg_color)
expense_frame.pack(expand=True)

date_label = tk.Label(expense_frame, text="Date:", bg=bg_color, fg=text_color, font=("Helvetica", 14))
date_label.grid(row=0, column=0, padx=5, pady=5)
date_entry = DateEntry(expense_frame, width=12, background='#FFFFFF',
                       foreground='#333333', borderwidth=2, font=("Helvetica", 12))
date_entry.grid(row=0, column=1, padx=5, pady=5)

amount_label = tk.Label(expense_frame, text="Amount:", bg=bg_color, fg=text_color, font=("Helvetica", 14))
amount_label.grid(row=1, column=0, padx=5, pady=5)
amount_entry = tk.Entry(expense_frame, font=("Helvetica", 12))
amount_entry.grid(row=1, column=1, padx=5, pady=5)

category_label = tk.Label(expense_frame, text="Category:", bg=bg_color, fg=text_color, font=("Helvetica", 14))
category_label.grid(row=2, column=0, padx=5, pady=5)
category_var = tk.StringVar()
category_var.set("Select Category")
categories = ["Food", "Transport", "Shopping", "Bills", "Etc"]
category_dropdown = tk.OptionMenu(expense_frame, category_var, *categories)
category_dropdown.config(bg='#FFFFFF', fg='#333333', font=("Helvetica", 12))
category_dropdown.grid(row=2, column=1, padx=5, pady=5)

description_label = tk.Label(expense_frame, text="Description:", bg=bg_color, fg=text_color, font=("Helvetica", 14))
description_label.grid(row=3, column=0, padx=5, pady=5)
description_entry = tk.Text(expense_frame, height=5, width=30, font=("Helvetica", 12))
description_entry.grid(row=3, column=1, padx=5, pady=5)

add_button = tk.Button(expense_frame, text="Add Expense", command=add_expense, bg=accent_color, fg='#FFFFFF', font=("Helvetica", 14))
add_button.grid(row=4, columnspan=2, padx=5, pady=20, sticky="ew")

expense_button = tk.Button(expense_frame, text="Go to Expense List", command=show_expense_list, bg=accent_color, fg='#FFFFFF', font=("Helvetica", 14))
expense_button.grid(row=5, columnspan=2, padx=5, pady=10, sticky="ew")

loading_label = tk.Label(root, text="Loading...", bg=bg_color, fg=text_color, font=("Helvetica", 14))

expense_list_frame = tk.Frame(root, bg=bg_color)
expense_list_frame.place(relwidth=1, relheight=1)  

button_frame = tk.Frame(expense_list_frame, bg=bg_color)
button_frame.pack(side="top", fill="x", padx=10, pady=10)

remove_button = tk.Button(button_frame, text="Remove Expense", command=remove_expense, bg=accent_color, fg='#FFFFFF', font=("Helvetica", 14), state=tk.DISABLED)
remove_button.pack(side="right", padx=(0, 10))

back_button = tk.Button(button_frame, text="Go to Main Page", command=show_main_page, bg=accent_color, fg='#FFFFFF', font=("Helvetica", 14))
back_button.pack(side="right")

stats_frame = tk.Frame(expense_list_frame, bg=bg_color)
stats_frame.pack(side="left", fill="y", padx=10, pady=20)

today_label = tk.Label(stats_frame, text="Today's Expense: ₱0.00", bg=bg_color, fg=text_color, font=("Helvetica", 14))
today_label.pack(anchor="w", padx=5, pady=5)

week_label = tk.Label(stats_frame, text="This Week's Expense: ₱0.00", bg=bg_color, fg=text_color, font=("Helvetica", 14))
week_label.pack(anchor="w", padx=5, pady=5)

month_label = tk.Label(stats_frame, text="This Month's Expense: ₱0.00", bg=bg_color, fg=text_color, font=("Helvetica", 14))
month_label.pack(anchor="w", padx=5, pady=5)

prev_month_label = tk.Label(stats_frame, text="Last Month's Expense: ₱0.00", bg=bg_color, fg=text_color, font=("Helvetica", 14))
prev_month_label.pack(anchor="w", padx=5, pady=5)

treeview_frame = tk.Frame(expense_list_frame, bg=bg_color)
treeview_frame.pack(side="right", fill="both", expand=True, padx=10, pady=20)

filter_frame = tk.Frame(treeview_frame, bg=bg_color)
filter_frame.pack(pady=20)

filter_options = ["Date Added (Descending)", "Date of Expense (Ascending)", "Date of Expense (Descending)"]
filter_var = tk.StringVar()
filter_var.set("Sort by...")
filter_dropdown = tk.OptionMenu(filter_frame, filter_var, *filter_options)
filter_dropdown.config(bg=accent_color, fg='#FFFFFF', font=("Helvetica", 14))
filter_dropdown.pack(pady=10)

expense_tree = ttk.Treeview(treeview_frame, columns=("ID", "Date", "Amount", "Category", "Description"), show="headings", height=6)
expense_tree.pack(side="top", fill="both", expand=True)

expense_tree.heading("ID", text="ID")
expense_tree.heading("Date", text="Date")
expense_tree.heading("Amount", text="Amount")
expense_tree.heading("Category", text="Category")
expense_tree.heading("Description", text="Description")

expense_tree.bind("<ButtonRelease-1>", lambda event: remove_button.config(state=tk.NORMAL if expense_tree.selection() else tk.DISABLED))

populate_expense_list()

root.mainloop()

conn.close()
