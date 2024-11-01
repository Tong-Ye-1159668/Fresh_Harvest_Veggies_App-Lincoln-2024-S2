import tkinter as tk
from tkinter import ttk
from .Sidebar import Sidebar
from .StaffTabs import StaffOrdersTab, StaffCustomersTab, StaffReportsTab, StaffInventoryTab  # Add this


class StaffView(tk.Frame):
    def __init__(self, parent, engine, staff):
        super().__init__(parent)
        self.engine = engine
        self.staff = staff
        self.parent = parent

        # Configure main window
        self.parent.title(f'Fresh Harvest Veggies - Staff Portal ({staff.firstName} {staff.lastName})')
        self.parent.geometry("1440x810")
        self.parent.minsize(1280, 720)
        self.parent.maxsize(1600, 900)

        # Create sidebar
        self.sidebar = Sidebar(self, userType="staff")

        # Create main content container
        self.mainContainer = tk.Frame(self, bg='white')
        self.mainContainer.place(relx=0.25, rely=0, relwidth=0.75, relheight=1)

        # Initialize frames
        self.frames = {
            'orders': StaffOrdersTab(self.mainContainer, self.engine),
            'customers': StaffCustomersTab(self.mainContainer, self.engine),
            'reports': StaffReportsTab(self.mainContainer, self.engine),
            'inventory': StaffInventoryTab(self.mainContainer, self.engine)  # Add this
        }

        # Setup navigation
        self.setupNavigation()

        # Show default frame
        self.showFrame('orders')

    def setupNavigation(self):
        """Setup navigation commands for sidebar buttons"""
        self.sidebar.addCommand("Manage Orders", lambda: self.showFrame('orders'))
        self.sidebar.addCommand("Manage Customers", lambda: self.showFrame('customers'))
        self.sidebar.addCommand("Generate Reports", lambda: self.showFrame('reports'))
        self.sidebar.addCommand("View Inventory", lambda: self.showFrame('inventory'))  # Add this
        self.sidebar.addCommand("Logout", self.parent.destroy)

    def showFrame(self, frameName):
        """Show selected frame and hide others"""
        print(f"Switching to frame: {frameName}")  # Debug print

        # Hide all frames
        for frame in self.frames.values():
            frame.place_forget()

        # Show selected frame
        self.frames[frameName].place(relx=0, rely=0, relwidth=1, relheight=1)

        # Refresh frame data if needed
        if hasattr(self.frames[frameName], 'loadOrders'):
            self.frames[frameName].loadOrders()
        elif hasattr(self.frames[frameName], 'loadCustomers'):
            self.frames[frameName].loadCustomers()
        elif hasattr(self.frames[frameName], 'loadItems'):  # Add this
            self.frames[frameName].loadItems()