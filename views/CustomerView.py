import tkinter as tk
from tkinter import ttk
from .Sidebar import Sidebar
from .CustomerTabs import CustomerOrderTab, CustomerCurrentOrdersTab, CustomerPreviousOrdersTab, CustomerProfileTab


class CustomerView(tk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer
        self.parent = parent

        # Configure main window
        self.parent.title(f"Welcome to Fresh Harvest Veggies, {customer.firstName} {customer.lastName}")
        self.parent.geometry("1440x810")
        self.parent.minsize(1280, 720)
        self.parent.maxsize(1600, 900)

        # Create sidebar
        self.sidebar = Sidebar(self, userType="customer")

        # Create main content container with adjusted position and width
        self.mainContainer = tk.Frame(self, bg='white')
        self.mainContainer.place(relx=0.15, rely=0, relwidth=0.85, relheight=1)

        # Initialize frames
        self.frames = {
            'newOrder': CustomerOrderTab(self.mainContainer, self.engine, self.customer),
            'currentOrders': CustomerCurrentOrdersTab(self.mainContainer, self.engine, self.customer),
            'orderHistory': CustomerPreviousOrdersTab(self.mainContainer, self.engine, self.customer),
            'profile': CustomerProfileTab(self.mainContainer, self.engine, self.customer)
        }

        # Setup navigation commands
        self.setupNavigation()

        # Show default page (New Order)
        self.showFrame('newOrder')

    def setupNavigation(self):
        """Setup navigation commands for sidebar buttons"""
        self.sidebar.addCommand("New Order", lambda: self.showFrame('newOrder'))
        self.sidebar.addCommand("Current Orders", lambda: self.showFrame('currentOrders'))
        self.sidebar.addCommand("Order History", lambda: self.showFrame('orderHistory'))
        self.sidebar.addCommand("My Profile", lambda: self.showFrame('profile'))
        self.sidebar.addCommand("Logout", self.parent.destroy)

    def showFrame(self, frameName):
        """Show selected frame and hide others"""
        # Hide all frames
        for frame in self.frames.values():
            frame.place_forget()

        # Show selected frame
        self.frames[frameName].place(relx=0, rely=0, relwidth=1, relheight=1)

        # If frame has a refresh method, call it
        if hasattr(self.frames[frameName], 'loadOrders'):
            self.frames[frameName].loadOrders()
        elif hasattr(self.frames[frameName], 'refreshProfile'):
            self.frames[frameName].refreshProfile()