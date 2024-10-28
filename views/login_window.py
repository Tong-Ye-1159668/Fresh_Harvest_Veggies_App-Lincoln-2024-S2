import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from models.Staff import Staff
from models.Customer import Customer
from .customer_tabs import (
    CustomerOrderTab,
    CustomerCurrentOrdersTab,
    CustomerPreviousOrdersTab,
    CustomerProfileTab
)
from .staff_tabs import (
    StaffOrdersTab,
    StaffCustomersTab,
    StaffReportsTab
)


class LoginWindow(tk.Tk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.title("Fresh Harvest Veggies - Login")
        self.geometry("400x300")

        # Center window
        self.centerWindow()

        # Create main frame
        mainFrame = ttk.Frame(self, padding="20")
        mainFrame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        ttk.Label(mainFrame, text="Fresh Harvest Veggies",
                  font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)

        # Username
        ttk.Label(mainFrame, text="Username:").grid(row=1, column=0, pady=5)
        self.username = tk.StringVar()
        ttk.Entry(mainFrame, textvariable=self.username).grid(row=1, column=1, pady=5)

        # Password
        ttk.Label(mainFrame, text="Password:").grid(row=2, column=0, pady=5)
        self.password = tk.StringVar()
        ttk.Entry(mainFrame, textvariable=self.password, show="*").grid(row=2, column=1, pady=5)

        # Login button
        ttk.Button(mainFrame, text="Login",
                   command=self.login).grid(row=3, column=0, columnspan=2, pady=20)

    def centerWindow(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        with Session(self.engine) as session:
            # Check if staff
            staff = session.query(Staff).filter_by(
                username=username, password=password).first()
            if staff:
                self.withdraw()  # Hide login window
                StaffDashboard(self, self.engine, staff)
                return

            # Check if customer
            customer = session.query(Customer).filter_by(
                username=username, password=password).first()
            if customer:
                self.withdraw()  # Hide login window
                CustomerDashboard(self, self.engine, customer)
                return

            messagebox.showerror("Error", "Invalid username or password")

class CustomerDashboard(tk.Toplevel):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)

        self.engine = engine
        self.customer = customer
        self.title(f"Welcome, {customer.firstName} {customer.lastName}")
        self.geometry("800x600")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self.orderTab = CustomerOrderTab(self.notebook, engine, customer)
        self.currentOrdersTab = CustomerCurrentOrdersTab(self.notebook, engine, customer)
        self.previousOrdersTab = CustomerPreviousOrdersTab(self.notebook, engine, customer)
        self.profileTab = CustomerProfileTab(self.notebook, engine, customer)

        # Add tabs to notebook
        self.notebook.add(self.orderTab, text="Place Order")
        self.notebook.add(self.currentOrdersTab, text="Current Orders")
        self.notebook.add(self.previousOrdersTab, text="Order History")
        self.notebook.add(self.profileTab, text="My Profile")

        # Logout button
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=10)

    def logout(self):
        self.parent.deiconify()  # Show login window
        self.destroy()  # Close dashboard


class StaffDashboard(tk.Toplevel):
    def __init__(self, parent, engine, staff):
        super().__init__(parent)

        self.engine = engine
        self.staff = staff
        self.title(f"Staff Dashboard - {staff.firstName} {staff.lastName}")
        self.geometry("1024x768")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self.ordersTab = StaffOrdersTab(self.notebook, engine)
        self.customersTab = StaffCustomersTab(self.notebook, engine)
        self.reportsTab = StaffReportsTab(self.notebook, engine)

        # Add tabs to notebook
        self.notebook.add(self.ordersTab, text="Manage Orders")
        self.notebook.add(self.customersTab, text="Customers")
        self.notebook.add(self.reportsTab, text="Reports")

        # Logout button
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=10)

    def logout(self):
        self.parent.deiconify()  # Show login window
        self.destroy()  # Close dashboard