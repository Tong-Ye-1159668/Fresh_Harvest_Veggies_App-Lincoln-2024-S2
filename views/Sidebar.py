import tkinter as tk
from tkinter import ttk


class Sidebar:
    def __init__(self, root, userType="customer"):
        self.root = root
        self.userType = userType
        self.buttons = {}

        # Colors
        self.colors = {
            'sidebar_bg': '#283662',
            'highlight': '#6fffe9',
            'text': 'white',
            'hover': '#4361ee',
            'active': '#1c2541'
        }

        # Create sidebar frame with narrower width
        self.sidebar = tk.Frame(root, bg=self.colors['sidebar_bg'])
        self.sidebar.place(relx=0, rely=0, relwidth=0.15, relheight=1)

        # Find the root Tk window
        self.master_window = self._get_master_window(root)

        # Logo/Brand area
        self.setupBrandArea()

        # Menu items (excluding logout)
        self.setupMenuItems()

        # Logout button at bottom
        self.setupLogoutButton()

    def _get_master_window(self, widget):
        """Get the root Tk window"""
        parent = widget.master
        while parent is not None:
            if isinstance(parent, tk.Tk):
                return parent
            parent = parent.master
        return widget

    def setupBrandArea(self):
        """Setup the brand area with logo"""
        brandFrame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        brandFrame.place(relx=0, rely=0, relwidth=1, relheight=0.15)

        # Store logo as a class attribute with correct relative path
        self.logo = tk.PhotoImage(file='static/logo.png')
        self.logo = self.logo.subsample(4, 4)

        logoLabel = tk.Label(brandFrame, image=self.logo, bg=self.colors['sidebar_bg'])
        logoLabel.image = self.logo
        logoLabel.place(relx=0.5, rely=0.5, anchor="center")

    def createMenuButton(self, parent, text, command=None, highlight=False):
        """Create a styled menu button"""
        btnFrame = tk.Frame(parent, bg=self.colors['sidebar_bg'])
        btnFrame.pack(fill=tk.X, pady=2)

        btnStyle = {
            'bg': self.colors['highlight'] if highlight else self.colors['sidebar_bg'],
            'fg': self.colors['active'] if highlight else self.colors['text'],
            'font': ("Arial", 14, "bold") if highlight else ("Arial", 12, "bold"),
            'activebackground': '#affc41' if highlight else self.colors['hover'],
            'activeforeground': self.colors['active'] if highlight else self.colors['text'],
            'bd': 0,
            'cursor': 'hand2',
            'anchor': "w",
            'padx': 10
        }

        btn = tk.Button(btnFrame, text=text, command=command, **btnStyle)
        btn.pack(fill=tk.X, ipady=8)

        self.buttons[text] = btn
        return btn

    def setupMenuItems(self):
        """Setup menu items based on user type"""
        menuFrame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        menuFrame.place(relx=0, rely=0.15, relwidth=1, relheight=0.7)  # Reduced height to make room for logout

        if self.userType == "customer":
            self.setupCustomerMenu(menuFrame)
        else:
            self.setupStaffMenu(menuFrame)

    def setupCustomerMenu(self, menuFrame):
        """Setup customer menu items"""
        menuItems = [
            ("New Order", None, False),  # Changed highlight to False
            ("Current Orders", None, False),
            ("Order History", None, False),
            ("My Profile", None, False)
        ]

        for text, cmd, highlight in menuItems:
            btn = self.createMenuButton(menuFrame, text, cmd, highlight)

    def setupStaffMenu(self, menuFrame):
        """Setup staff menu items"""
        menuItems = [
            ("Manage Orders", None, True),
            ("Manage Customers", None, False),
            ("Generate Reports", None, False)
        ]  # Removed Logout from here

        for text, cmd, highlight in menuItems:
            self.createMenuButton(menuFrame, text, cmd, highlight)

    def setupLogoutButton(self):
        """Setup logout button at bottom of sidebar"""
        # Create frame for logout button at bottom
        logoutFrame = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        logoutFrame.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)

        # Create logout button with slightly different style
        btnStyle = {
            'bg': '#ff4444',
            'fg': self.colors['text'],
            'font': ("Arial", 12, "bold"),
            'activebackground': '#fca311',
            'activeforeground': 'white',
            'bd': 0,
            'cursor': 'hand2',
            'anchor': "w",
            'padx': 10
        }

        logoutBtn = tk.Button(logoutFrame, text="Logout", **btnStyle)
        logoutBtn.pack(fill=tk.X, ipady=8, pady=10)
        self.buttons["Logout"] = logoutBtn

    def addCommand(self, buttonText, command):
        """Add command to existing button by text"""
        if buttonText in self.buttons:
            self.buttons[buttonText].config(command=command)
            return True
        return False