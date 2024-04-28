import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import re
from tkcalendar import DateEntry  # Import DateEntry widget from tkcalendar

# Database initialization
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()

# Create user table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT UNIQUE, age INTEGER, sex TEXT, contact_number TEXT, username TEXT UNIQUE, password TEXT)''')

# Create expense table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, category TEXT, date TEXT)''')

# Function to handle user registration
def register_user():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    email = email_entry.get()
    age = age_entry.get()
    sex = sex_var.get()  # Get selected sex from radio button
    contact_number = contact_number_entry.get()
    username = register_username_entry.get()
    password = register_password_entry.get()

    # Check if fields are empty
    if not all([first_name, last_name, email, age, sex, contact_number, username, password]):
        messagebox.showerror("Error", "All fields are required")
        return

    # Email validation using regex
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid email address")
        return

    # Contact number validation
    if not contact_number.isdigit() or len(contact_number) != 11:
        messagebox.showerror("Error", "Invalid contact number. Please enter 11 digits.")
        return

    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        messagebox.showerror("Error", "Username already exists")
        return

    # Insert new user into the database
    c.execute("INSERT INTO users (first_name, last_name, email, age, sex, contact_number, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (first_name, last_name, email, age, sex, contact_number, username, password))
    conn.commit()
    messagebox.showinfo("Success", "Registration successful")

# Function to handle user login
def login():
    username = login_username_entry.get()
    password = login_password_entry.get()

    # Check if fields are empty
    if not all([username, password]):
        messagebox.showerror("Error", "Username and password are required")
        return

    # Check if username and password match
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        # Proceed to main app screen
        messagebox.showinfo("Success", "Login successful")
        main_app_screen(user[0])  # Pass user ID to main app screen function
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Function to handle user logout
def logout():
    # Close the main app window
    main_app_window.destroy()
    # Re-display the login window
    login_window.deiconify()

# Function to switch to the registration page
def switch_to_registration():
    login_window.withdraw()
    register_window.deiconify()

# Function to switch to the login page
def switch_to_login():
    register_window.withdraw()
    login_window.deiconify()

# Function to display main app screen
def main_app_screen(user_id):
    # Close login window
    login_window.withdraw()

    # Create main app window
    global main_app_window
    main_app_window = tk.Toplevel()
    main_app_window.title("Expense Tracker - Main App")

    # Function to add expense
    def add_expense():
        amount = amount_entry.get()
        if not amount:
            messagebox.showerror("Error", "Amount cannot be empty")
            return
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a valid number")
            return
        category = category_var.get()  # Get selected category from dropdown menu
        date = date_entry.get()  # Get selected date from DateEntry widget

        # Insert expense into database
        c.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)", (user_id, amount, category, date))
        conn.commit()
        messagebox.showinfo("Success", "Expense added successfully")
        update_expense_list()
        clear_fields()

    # Function to update expense list
    def update_expense_list():
        # Clear current expense list
        for row in expense_tree.get_children():
            expense_tree.delete(row)
        # Fetch and display expenses for the user
        c.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
        expenses = c.fetchall()
        for expense in expenses:
            # Format amount to display with 2 decimal places and Philippine peso symbol
            formatted_amount = "₱{:,.2f}".format(expense[2])
            expense_tree.insert('', 'end', values=(expense[0], expense[1], formatted_amount, expense[3], expense[4]))

    # Function to delete selected expense
    def delete_expense():
        selected_item = expense_tree.selection()
        if selected_item:
            expense_id = expense_tree.item(selected_item, 'values')[0]
            c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            messagebox.showinfo("Success", "Expense deleted successfully")
            update_expense_list()
        else:
            messagebox.showerror("Error", "Please select an expense to delete")

    # Function to handle user logout
    def logout_from_main_app():
        # Close the main app window
        main_app_window.destroy()
        # Re-display the login window
        login_window.deiconify()

    # Function to clear entry fields
    def clear_fields():
        amount_entry.delete(0, tk.END)
        category_var.set("Choose Category")  # Set default value in dropdown
        date_entry.set_date(datetime.today())  # Set today's date in DateEntry widget

    # Widgets for adding expenses
    amount_label = tk.Label(main_app_window, text="Amount:")
    amount_label.grid(row=0, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(main_app_window)
    amount_entry.grid(row=0, column=1, padx=10, pady=5)
    amount_entry.config(validate="key", validatecommand=(amount_entry.register(validate_amount), "%P"))

    category_label = tk.Label(main_app_window, text="Category:")
    category_label.grid(row=1, column=0, padx=10, pady=5)
    # Dropdown menu for category selection with placeholder
    category_var = tk.StringVar(main_app_window)
    category_var.set("Choose Category")  # Placeholder
    category_options = ["","Food", "Transportation", "Shopping", "Entertainment", "Utilities", "Health", "Other"]
    category_dropdown = ttk.OptionMenu(main_app_window, category_var, *category_options)
    category_dropdown.grid(row=1, column=1, padx=10, pady=5)

    date_label = tk.Label(main_app_window, text="Date:")
    date_label.grid(row=2, column=0, padx=10, pady=5)
    date_entry = DateEntry(main_app_window, date_pattern='m/d/y')  # DateEntry widget for date input
    date_entry.grid(row=2, column=1, padx=10, pady=5)

    add_expense_button = tk.Button(main_app_window, text="Add Expense", command=add_expense)
    add_expense_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    # Expense Treeview
    global expense_tree
    expense_tree = ttk.Treeview(main_app_window, columns=('ID', 'User ID', 'Amount', 'Category', 'Date'), show='headings')
    expense_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    expense_tree.heading('ID', text='ID')
    expense_tree.heading('User ID', text='User ID')
    expense_tree.heading('Amount', text='Amount')
    expense_tree.heading('Category', text='Category')
    expense_tree.heading('Date', text='Date')

    # Update and delete expense buttons
    update_expense_button = tk.Button(main_app_window, text="Update Expense List", command=update_expense_list)
    update_expense_button.grid(row=5, column=0, padx=10, pady=5)

    delete_expense_button = tk.Button(main_app_window, text="Delete Expense", command=delete_expense)
    delete_expense_button.grid(row=5, column=1, padx=10, pady=5)

    # Logout button
    logout_button = tk.Button(main_app_window, text="Logout", command=logout_from_main_app)
    logout_button.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

# Validation function for amount entry
def validate_amount(value):
    if value == "":
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False

# UI setup for login window
login_window = tk.Tk()
login_window.title("Expense Tracker - Login")

login_username_label = tk.Label(login_window, text="Username:")
login_username_label.grid(row=0, column=0, padx=10, pady=5)
login_username_entry = tk.Entry(login_window)
login_username_entry.grid(row=0, column=1, padx=10, pady=5)

login_password_label = tk.Label(login_window, text="Password:")
login_password_label.grid(row=1, column=0, padx=10, pady=5)
login_password_entry = tk.Entry(login_window, show="*")
login_password_entry.grid(row=1, column=1, padx=10, pady=5)

login_button = tk.Button(login_window, text="Login", command=login)
login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

switch_to_register_button = tk.Button(login_window, text="Go Register", command=switch_to_registration)
switch_to_register_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

# UI setup for registration window
register_window = tk.Toplevel()
register_window.title("Expense Tracker - Register")
register_window.withdraw()  # Hide registration window initially

first_name_label = tk.Label(register_window, text="First Name:")
first_name_label.grid(row=0, column=0, padx=10, pady=5)
first_name_entry = tk.Entry(register_window)
first_name_entry.grid(row=0, column=1, padx=10, pady=5)

last_name_label = tk.Label(register_window, text="Last Name:")
last_name_label.grid(row=1, column=0, padx=10, pady=5)
last_name_entry = tk.Entry(register_window)
last_name_entry.grid(row=1, column=1, padx=10, pady=5)

email_label = tk.Label(register_window, text="Email:")
email_label.grid(row=2, column=0, padx=10, pady=5)
email_entry = tk.Entry(register_window)
email_entry.grid(row=2, column=1, padx=10, pady=5)

age_label = tk.Label(register_window, text="Age:")
age_label.grid(row=3, column=0, padx=10, pady=5)
age_entry = tk.Entry(register_window)
age_entry.grid(row=3, column=1, padx=10, pady=5)

sex_label = tk.Label(register_window, text="Sex:")
sex_label.grid(row=4, column=0, padx=10, pady=5)
sex_var = tk.StringVar()
male_radio = tk.Radiobutton(register_window, text="Male", variable=sex_var, value="Male")
male_radio.grid(row=4, column=1, padx=10, pady=5)
female_radio = tk.Radiobutton(register_window, text="Female", variable=sex_var, value="Female")
female_radio.grid(row=4, column=2, padx=10, pady=5)

contact_number_label = tk.Label(register_window, text="Contact Number:")
contact_number_label.grid(row=5, column=0, padx=10, pady=5)
contact_number_entry = tk.Entry(register_window)
contact_number_entry.grid(row=5, column=1, padx=10, pady=5)

register_username_label = tk.Label(register_window, text="Username:")
register_username_label.grid(row=6, column=0, padx=10, pady=5)
register_username_entry = tk.Entry(register_window)
register_username_entry.grid(row=6, column=1, padx=10, pady=5)

register_password_label = tk.Label(register_window, text="Password:")
register_password_label.grid(row=7, column=0, padx=10, pady=5)
register_password_entry = tk.Entry(register_window, show="*")
register_password_entry.grid(row=7, column=1, padx=10, pady=5)

register_button = tk.Button(register_window, text="Register", command=register_user)
register_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

switch_to_login_button = tk.Button(register_window, text="Go Login", command=switch_to_login)
switch_to_login_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

login_window.mainloop()

# Close database connection when the app exits
conn.close()
