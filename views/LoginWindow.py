import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from models.Staff import Staff
from models.Customer import Customer
from .CustomerView import CustomerView
from .StaffView import StaffView



class LoginWindow(tk.Tk):
    def __init__(self, engine):
        super().__init__()

        self.engine = engine
        self.title("Fresh Harvest Veggies - Login")
        self.geometry("500x500")

        # Center window
        self.centerWindow()

        # Create main frame
        mainFrame = ttk.Frame(self, padding="20")
        mainFrame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Logo frame
        logoFrame = ttk.Frame(mainFrame)
        logoFrame.grid(row=0, column=0, columnspan=2, pady=20)

        # Load and display logo
        try:
            self.logo = tk.PhotoImage(file='static/logo.png')
            self.logo = self.logo.subsample(3, 3)
            logoLabel = ttk.Label(logoFrame, image=self.logo)
            logoLabel.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Title
        ttk.Label(mainFrame,
                 text="Fresh Harvest Veggies",
                 font=('Helvetica', 16, 'bold')).grid(row=1, column=0, columnspan=2, pady=20)

        # Username
        ttk.Label(mainFrame, text="Username:").grid(row=2, column=0, pady=5)
        self.username = tk.StringVar()
        ttk.Entry(mainFrame, textvariable=self.username).grid(row=2, column=1, pady=5)

        # Password
        ttk.Label(mainFrame, text="Password:").grid(row=3, column=0, pady=5)
        self.password = tk.StringVar()
        ttk.Entry(mainFrame, textvariable=self.password, show="*").grid(row=3, column=1, pady=5)

        # Login button
        loginButton = ttk.Button(mainFrame, text="Login", command=self.login)
        loginButton.grid(row=4, column=0, columnspan=2, pady=20)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        mainFrame.grid_columnconfigure(1, weight=1)

    def centerWindow(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def handleLogout(self, window):
        """Handle logout and window cleanup"""
        window.destroy()
        self.deiconify()  # Show login window
        self.username.set("")  # Clear login fields
        self.password.set("")

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
                # Create new window for staff view using Toplevel
                staffWindow = tk.Toplevel(self)
                staffWindow.geometry("1280x720")
                staffView = StaffView(staffWindow, self.engine, staff)
                staffView.pack(fill=tk.BOTH, expand=True)
                staffWindow.protocol("WM_DELETE_WINDOW", lambda: self.handleLogout(staffWindow))
                self.withdraw()
                return

            # Check if customer
            customer = session.query(Customer).filter_by(
                username=username, password=password).first()
            if customer:
                # Create new window for customer view using Toplevel
                customerWindow = tk.Toplevel(self)
                customerWindow.geometry("1280x720")
                customerView = CustomerView(customerWindow, self.engine, customer)
                customerView.pack(fill=tk.BOTH, expand=True)
                customerWindow.protocol("WM_DELETE_WINDOW", lambda: self.handleLogout(customerWindow))
                self.withdraw()
                return

            messagebox.showerror("Error", "Invalid username or password")
