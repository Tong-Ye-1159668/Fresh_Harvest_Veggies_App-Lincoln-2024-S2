import tkinter as tk
from tkinter import ttk
from models.Order import OrderStatus


class OrderStatusDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        # Configure dialog
        self.title("Update Order Status")
        self.geometry("300x200")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.centerDialog()

        # Create content
        mainFrame = ttk.Frame(self, padding="20")
        mainFrame.pack(fill=tk.BOTH, expand=True)

        # Status selection
        ttk.Label(mainFrame, text="Select New Status:").pack(pady=10)

        self.statusVar = tk.StringVar()
        self.statusCombo = ttk.Combobox(mainFrame,
                                        textvariable=self.statusVar,
                                        values=[status.value for status in OrderStatus],
                                        state='readonly')
        self.statusCombo.pack(pady=5)

        # Buttons
        buttonFrame = ttk.Frame(mainFrame)
        buttonFrame.pack(pady=20)

        ttk.Button(buttonFrame, text="Update", command=self.updateStatus).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

        # Wait for user interaction
        self.wait_window()

    def centerDialog(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()

        # Get parent window position
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        # Calculate position
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        self.geometry(f'{width}x{height}+{x}+{y}')

    def updateStatus(self):
        """Update the status and close dialog"""
        if self.statusVar.get():
            self.result = OrderStatus(self.statusVar.get())
            self.destroy()

    def cancel(self):
        """Cancel the operation"""
        self.result = None
        self.destroy()