import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from datetime import timedelta
import re
from tkcalendar import DateEntry
import calendar
from ttkthemes import ThemedTk

# Database initialization
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()

# Create user table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT UNIQUE, age INTEGER, sex TEXT, contact_number TEXT, username TEXT UNIQUE, password TEXT)''')

# Create expense table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, category TEXT, date TEXT)''')

# Add admin account if not exists
c.execute("SELECT * FROM users WHERE username='admin'")
admin_exists = c.fetchone()
if not admin_exists:
    c.execute("INSERT INTO users (first_name, last_name, email, age, sex, contact_number, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              ("Admin", "Admin", "admin@example.com", 0, "NA", "NA", "admin", "password"))
    conn.commit()

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
    # Clear fields after successful registration
    clear_register_fields()

# Function to clear registration fields
def clear_register_fields():
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    sex_var.set(None)  # Clear radio button selection
    contact_number_entry.delete(0, tk.END)
    register_username_entry.delete(0, tk.END)
    register_password_entry.delete(0, tk.END)

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
        if username == 'admin':  # Check if the logged-in user is admin
            # Proceed to admin dashboard
            messagebox.showinfo("Success", "Login successful as admin")
            admin_dashboard()
        else:
            # Proceed to main app screen for regular users
            messagebox.showinfo("Success", "Login successful")
            main_app_screen(user[0])  # Pass user ID to main app screen function
        # Clear fields after successful login
        clear_login_fields()
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Function to clear login fields
def clear_login_fields():
    login_username_entry.delete(0, tk.END)
    login_password_entry.delete(0, tk.END)

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
    register_window.withdraw()  # Close the registration window
    login_window.deiconify()    # Display the login window


# Function to display main app screen
def main_app_screen(user_id):
    # Close login window
    login_window.withdraw()

    # Create main app window
    global main_app_window
    main_app_window = ThemedTk(theme="plastik")  # Apply theme to the main app window
    main_app_window.title("Expense Tracker - Main App")
    main_app_window.attributes('-fullscreen', True)  # Set window to full screen
    main_app_window.geometry("800x600")  # Set window size

    # Center window contents
    center_window(main_app_window)

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

    # Function to display statistics overview
    def show_statistics():
        # Get current date
        current_date = datetime.today().date()

        # Get start and end dates for this week, this month, and this year
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_of_month = current_date.replace(day=1)
        end_of_month = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        start_of_year = current_date.replace(month=1, day=1)
        end_of_year = current_date.replace(month=12, day=31)

        # Initialize variables to store total expenses
        total_today_expense = 0
        total_week_expense = 0
        total_month_expense = 0
        total_year_expense = 0

        # Iterate through items in the expense treeview
        for item in expense_tree.get_children():
            values = expense_tree.item(item, 'values')
            expense_date = datetime.strptime(values[4], '%m/%d/%Y').date()
            expense_amount = float(values[2][1:].replace(',', ''))  # Remove currency symbol and comma
            # Check if expense date falls within today
            if expense_date == current_date:
                total_today_expense += expense_amount
            # Check if expense date falls within this week
            if start_of_week <= expense_date <= end_of_week:
                total_week_expense += expense_amount
            # Check if expense date falls within this month
            if start_of_month <= expense_date <= end_of_month:
                total_month_expense += expense_amount
            # Check if expense date falls within this year
            if start_of_year <= expense_date <= end_of_year:
                total_year_expense += expense_amount

        # Format total expenses to display two decimal places
        total_today_expense = "{:.2f}".format(total_today_expense)
        total_week_expense = "{:.2f}".format(total_week_expense)
        total_month_expense = "{:.2f}".format(total_month_expense)
        total_year_expense = "{:.2f}".format(total_year_expense)

        # Display statistics overview
        messagebox.showinfo(
            "Statistics Overview",
            f"Total expense for today: ₱{total_today_expense}\n"
            f"Total expense for this week: ₱{total_week_expense}\n"
            f"Total expense for this month: ₱{total_month_expense}\n"
            f"Total expense for this year: ₱{total_year_expense}"
        )

    # Apply styling
    main_app_window.configure(background="white")  # Set background color

    # Widgets for adding expenses
    amount_label = tk.Label(main_app_window, text="Amount:", bg="white")  # Set background color
    amount_label.pack(padx=10, pady=5, anchor="center")

    amount_entry = tk.Entry(main_app_window)
    amount_entry.pack(padx=10, pady=5, anchor="center")
    amount_entry.config(validate="key", validatecommand=(amount_entry.register(validate_amount), "%P"))

    category_label = tk.Label(main_app_window, text="Category:", bg="white")  # Set background color
    category_label.pack(padx=10, pady=5, anchor="center")

    # Dropdown menu for category selection with placeholder
    category_var = tk.StringVar(main_app_window)
    category_var.set("Choose Category")  # Placeholder
    category_options = ["", "Food", "Transportation", "Shopping", "Entertainment", "Utilities", "Health", "Other"]
    category_dropdown = ttk.OptionMenu(main_app_window, category_var, *category_options)
    category_dropdown.pack(padx=10, pady=5, anchor="center")

    date_label = tk.Label(main_app_window, text="Date:", bg="white")  # Set background color
    date_label.pack(padx=10, pady=5, anchor="center")

    date_entry = DateEntry(main_app_window, date_pattern='m/d/y')  # DateEntry widget for date input
    date_entry.pack(padx=10, pady=5, anchor="center")

    add_expense_button = tk.Button(main_app_window, text="Add Expense", command=add_expense, bg="green", fg="white")  # Set background and foreground color
    add_expense_button.pack(padx=10, pady=5, anchor="center")

    # Expense Treeview
    global expense_tree
    expense_tree = ttk.Treeview(main_app_window, columns=('ID', 'User ID', 'Amount', 'Category', 'Date'), show='headings')
    expense_tree.pack(padx=10, pady=5, anchor="center")

    expense_tree.heading('ID', text='ID')
    expense_tree.heading('User ID', text='User ID')
    expense_tree.heading('Amount', text='Amount')
    expense_tree.heading('Category', text='Category')
    expense_tree.heading('Date', text='Date')

    # Create a frame below the expense tree view
    button_frame = tk.Frame(main_app_window)
    button_frame.pack(pady=10)

    # Update and delete expense buttons
    update_expense_button = tk.Button(button_frame, text="Update Expense List", command=update_expense_list, bg="green", fg="white")  # Set background and foreground color
    update_expense_button.pack(side="left", padx=10)

    delete_expense_button = tk.Button(button_frame, text="Delete Expense", command=delete_expense, bg="green", fg="white")  # Set background and foreground color
    delete_expense_button.pack(side="left", padx=10)

    # Statistics overview button
    stats_button = tk.Button(button_frame, text="Statistics Overview", command=show_statistics, bg="green", fg="white")  # Set background and foreground color
    stats_button.pack(side="left", padx=10)

    # Logout button
    logout_button = tk.Button(button_frame, text="Logout", command=logout_from_main_app, bg="green", fg="white")  # Set background and foreground color
    logout_button.pack(side="left", padx=10)



# Function to fetch expenses for a specific period
def fetch_expenses_for_period(user_id, start_date, end_date):
    # Convert start_date and end_date to the format used in the database ('m/d/y')
    start_date_str = start_date.strftime('%m/%d/%Y')
    end_date_str = end_date.strftime('%m/%d/%Y')
    
    # Execute SQL query to fetch expenses within the specified period
    c.execute("SELECT * FROM expenses WHERE user_id=? AND date BETWEEN ? AND ?", (user_id, start_date_str, end_date_str))
    
    # Return fetched expenses
    return c.fetchall()

# Function to handle user deletion
def delete_user():
    selected_item = user_tree.selection()
    if selected_item:
        user_id = user_tree.item(selected_item, 'values')[0]
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        messagebox.showinfo("Success", "User deleted successfully")
        update_user_list()
    else:
        messagebox.showerror("Error", "Please select a user to delete")

# Function to update user list
def update_user_list():
    # Clear current user list
    for row in user_tree.get_children():
        user_tree.delete(row)
    # Fetch and display all user accounts
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    for user in users:
        user_tree.insert('', 'end', values=user)

# Function to handle admin logout
def logout_admin(admin_window):
    # Close the admin dashboard window
    admin_window.destroy()
    # Re-display the login window
    login_window.deiconify()

# Admin Dashboard
def admin_dashboard():
    # Close login window
    login_window.withdraw()

    # Create admin dashboard window
    admin_window = tk.Tk()  # Use Tk instead of Toplevel to ensure full-screen behavior
    admin_window.title("Admin Dashboard")
    admin_window.attributes('-fullscreen', True)  # Open window in full screen

    # User Treeview
    global user_tree
    user_tree = ttk.Treeview(admin_window, columns=('ID', 'First Name', 'Last Name', 'Email', 'Age', 'Sex', 'Contact Number', 'Username', 'Password'), show='headings')
    user_tree.pack(fill="both", expand=True, padx=10, pady=5)

    user_tree.heading('ID', text='ID')
    user_tree.heading('First Name', text='First Name')
    user_tree.heading('Last Name', text='Last Name')
    user_tree.heading('Email', text='Email')
    user_tree.heading('Age', text='Age')
    user_tree.heading('Sex', text='Sex')
    user_tree.heading('Contact Number', text='Contact Number')
    user_tree.heading('Username', text='Username')
    user_tree.heading('Password', text='Password')

    # Adjusting column widths based on content
    user_tree.column('ID', width=50)
    user_tree.column('First Name', width=100)
    user_tree.column('Last Name', width=100)
    user_tree.column('Email', width=200)
    user_tree.column('Age', width=50)
    user_tree.column('Sex', width=50)
    user_tree.column('Contact Number', width=150)
    user_tree.column('Username', width=100)
    user_tree.column('Password', width=100)


    # Fetch and display all user accounts
    update_user_list()

    # Button Frame
    button_frame = tk.Frame(admin_window)
    button_frame.pack(pady=10)

    # Delete User Button
    delete_user_button = tk.Button(button_frame, text="Delete User", command=delete_user, bg="green", fg="white")  # Set background and foreground color
    delete_user_button.pack(side="left", padx=10)

    # Admin logout button
    logout_button = tk.Button(button_frame, text="Logout", command=lambda: logout_admin(admin_window), bg="green", fg="white")  # Set background and foreground color
    logout_button.pack(side="left", padx=10)

    # Center window contents
    center_window(admin_window)

# Center window function
def center_window(window):
    window.update_idletasks()
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    x = (width // 2) - (width // 2)
    y = (height // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

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
login_window = ThemedTk(theme="plastik")  # Apply theme to the login window
login_window.title("Expense Tracker - Login")
login_window.configure(background="white")  # Set background color to white
login_window.attributes('-fullscreen', True)  # Set window to full screen

login_frame = tk.Frame(login_window, bg="white")  # Set background color
login_frame.pack(expand=True)

login_username_label = tk.Label(login_frame, text="Username:", bg="white", font=("Arial", 14))  # Set background color and font size
login_username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
login_username_entry = tk.Entry(login_frame, width=40, font=("Arial", 14))  # Adjust width and font size of entry widget
login_username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

login_password_label = tk.Label(login_frame, text="Password:", bg="white", font=("Arial", 14))  # Set background color and font size
login_password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
login_password_entry = tk.Entry(login_frame, show="*", width=40, font=("Arial", 14))  # Adjust width and font size of entry widget
login_password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

login_button = tk.Button(login_frame, text="Login", command=login, bg="green", fg="white", font=("Arial", 14), width=20)  # Adjust font size and width of button widget
login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

switch_to_register_button = tk.Button(login_frame, text="Go Register", command=switch_to_registration, bg="green", fg="white", font=("Arial", 14), width=20)  # Adjust font size and width of button widget
switch_to_register_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# UI setup for registration window
register_window = ThemedTk(theme="plastik")  # Apply theme to the registration window
register_window.title("Expense Tracker - Register")
register_window.attributes('-fullscreen', True)  # Set window to full screen
register_window.configure(background="white")  # Set background color to white

# Function to center window contents
def center_window_content(window):
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# UI setup for registration frame
register_frame = tk.Frame(register_window, bg="white")  # Set background color
register_frame.pack(expand=True, fill="both")  # Make the frame expand to fill the entire window
register_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame on the screen

# Function to create labels and entries with consistent styling
def create_entry_with_label(label_text, row, column):
    label = tk.Label(register_frame, text=label_text, bg="white", font=("Arial", 12))  # Set background color and font
    label.grid(row=row, column=column, padx=10, pady=5, sticky="e")
    entry = tk.Entry(register_frame, font=("Arial", 12))  # Set font
    entry.grid(row=row, column=column + 1, padx=10, pady=5, sticky="w")
    return entry

first_name_entry = create_entry_with_label("First Name:", 0, 0)
last_name_entry = create_entry_with_label("Last Name:", 1, 0)
email_entry = create_entry_with_label("Email:", 2, 0)
age_entry = create_entry_with_label("Age:", 3, 0)
contact_number_entry = create_entry_with_label("Contact Number:", 4, 0)
register_username_entry = create_entry_with_label("Username:", 5, 0)
register_password_entry = create_entry_with_label("Password:", 6, 0)

# Radio buttons for sex selection
sex_label = tk.Label(register_frame, text="Sex:", bg="white", font=("Arial", 12))  # Set background color and font
sex_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
sex_var = tk.StringVar(register_frame)
sex_var.set("Male")  # Set default value for radio button
sex_radio_male = tk.Radiobutton(register_frame, text="Male", variable=sex_var, value="Male", bg="white", font=("Arial", 12))  # Set background color and font
sex_radio_male.grid(row=7, column=1, padx=10, pady=5, sticky="w")
sex_radio_female = tk.Radiobutton(register_frame, text="Female", variable=sex_var, value="Female", bg="white", font=("Arial", 12))  # Set background color and font
sex_radio_female.grid(row=7, column=2, padx=10, pady=5, sticky="w")

# Register button
register_button = tk.Button(register_frame, text="Register", command=register_user, bg="green", fg="white", font=("Arial", 12))  # Set background, foreground color, and font
register_button.grid(row=8, column=0, columnspan=3, pady=10)

# Switch to login button
switch_to_login_button = tk.Button(register_frame, text="Go Login", command=switch_to_login, bg="green", fg="white", font=("Arial", 12))  # Set background, foreground color, and font
switch_to_login_button.grid(row=9, column=0, columnspan=3, pady=10)


# Center the login window initially
center_window(login_window)

# Start the tkinter event loop
login_window.mainloop()


# Close database connection
conn.close()
