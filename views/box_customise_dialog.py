import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from models import Veggie
from models.PremadeBox import PremadeBox


class CustomBoxDialog(tk.Toplevel):
    def __init__(self, parent, engine, box_size):
        super().__init__(parent)
        self.engine = engine
        self.box_size = box_size
        self.result = None
        self.selected_veggies = []

        self.title(f"Customize {box_size} Box")
        self.geometry("800x600")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Available veggies frame (left side)
        availableFrame = ttk.LabelFrame(self, text="Available Veggies")
        availableFrame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Create Treeview for available veggies
        self.availableTree = ttk.Treeview(availableFrame,
                                          columns=('Name', 'Type'),
                                          show='headings')
        self.availableTree.heading('Name', text='Name')
        self.availableTree.heading('Type', text='Type')
        self.availableTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons frame (middle)
        buttonFrame = ttk.Frame(self)
        buttonFrame.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(buttonFrame, text="Add >",
                   command=self.addVeggie).pack(pady=5)
        ttk.Button(buttonFrame, text="< Remove",
                   command=self.removeVeggie).pack(pady=5)

        # Selected veggies frame (right side)
        selectedFrame = ttk.LabelFrame(self, text="Selected Veggies")
        selectedFrame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Create Treeview for selected veggies
        self.selectedTree = ttk.Treeview(selectedFrame,
                                         columns=('Name', 'Type'),
                                         show='headings')
        self.selectedTree.heading('Name', text='Name')
        self.selectedTree.heading('Type', text='Type')
        self.selectedTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Info label
        max_veggies = PremadeBox.getMaxVeggies(box_size)
        ttk.Label(self,
                  text=f"Select up to {max_veggies} veggies for your {box_size} box").grid(
            row=1, column=0, columnspan=3, pady=5)

        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Bottom buttons
        bottomFrame = ttk.Frame(self)
        bottomFrame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(bottomFrame, text="Cancel",
                   command=self.cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottomFrame, text="Confirm",
                   command=self.confirm).pack(side=tk.LEFT, padx=5)

        # Load available veggies
        self.loadVeggies()

    def loadVeggies(self):
        """Load available veggies from database"""
        with Session(self.engine) as session:
            veggies = session.query(Veggie).all()
            for veggie in veggies:
                if hasattr(veggie, 'vegName'):  # Check if it's a veggie
                    veggie_type = type(veggie).__name__.replace('Veggie', '')
                    self.availableTree.insert('', 'end',
                                              values=(veggie.vegName, veggie_type))

    def addVeggie(self):
        """Add selected veggie to box"""
        selected = self.availableTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a veggie to add")
            return

        max_veggies = PremadeBox.getMaxVeggies(self.box_size)
        if len(self.selectedTree.get_children()) >= max_veggies:
            messagebox.showwarning("Warning",
                                   f"Maximum {max_veggies} veggies allowed for {self.box_size} box")
            return

        # Move item from available to selected
        values = self.availableTree.item(selected[0])['values']
        self.selectedTree.insert('', 'end', values=values)
        self.availableTree.delete(selected[0])

    def removeVeggie(self):
        """Remove selected veggie from box"""
        selected = self.selectedTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a veggie to remove")
            return

        # Move item from selected back to available
        values = self.selectedTree.item(selected[0])['values']
        self.availableTree.insert('', 'end', values=values)
        self.selectedTree.delete(selected[0])

    def confirm(self):
        """Confirm selection"""
        selected_items = []
        for item in self.selectedTree.get_children():
            values = self.selectedTree.item(item)['values']
            selected_items.append(values[0])  # Store veggie names

        self.result = selected_items
        self.destroy()

    def cancel(self):
        """Cancel selection"""
        self.result = None
        self.destroy()