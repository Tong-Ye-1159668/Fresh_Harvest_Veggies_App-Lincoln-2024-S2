import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from datetime import datetime

from models import PremadeBox, UnitPriceVeggie, PackVeggie, WeightedVeggie, Item, Order
from models.Order import DeliveryMethod, Order,OrderStatus


class CustomerOrderTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create two frames
        leftFrame = ttk.Frame(self)
        leftFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        rightFrame = ttk.Frame(self)
        rightFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame - Available Items
        ttk.Label(leftFrame, text="Available Items", font=('Helvetica', 12, 'bold')).pack()

        # Create Treeview for items
        self.itemTree = ttk.Treeview(leftFrame, columns=('Name', 'Type', 'Price', 'Stock'), show='headings')
        self.itemTree.heading('Name', text='Name')
        self.itemTree.heading('Type', text='Type')
        self.itemTree.heading('Price', text='Price')
        self.itemTree.heading('Stock', text='Available')
        self.itemTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add quantity spinbox and Add to Cart button
        quantityFrame = ttk.Frame(leftFrame)
        quantityFrame.pack(fill=tk.X, pady=5)
        ttk.Label(quantityFrame, text="Quantity:").pack(side=tk.LEFT)
        self.quantity = tk.IntVar(value=1)
        ttk.Spinbox(quantityFrame, from_=1, to=100, textvariable=self.quantity).pack(side=tk.LEFT, padx=5)
        ttk.Button(quantityFrame, text="Add to Cart", command=self.addToCart).pack(side=tk.LEFT)

        # Right frame - Shopping Cart
        ttk.Label(rightFrame, text="Shopping Cart", font=('Helvetica', 12, 'bold')).pack()

        # Create Treeview for cart
        self.cartTree = ttk.Treeview(rightFrame, columns=('Name', 'Quantity', 'Price'), show='headings')
        self.cartTree.heading('Name', text='Name')
        self.cartTree.heading('Quantity', text='Quantity')
        self.cartTree.heading('Price', text='Price')
        self.cartTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Order summary
        summaryFrame = ttk.LabelFrame(rightFrame, text="Order Summary")
        summaryFrame.pack(fill=tk.X, pady=5)

        # Delivery options with distance input
        deliveryFrame = ttk.LabelFrame(summaryFrame, text="Delivery Options")
        deliveryFrame.pack(fill=tk.X, pady=5)

        # Delivery method radio buttons
        self.deliveryMethod = tk.StringVar(value="PICKUP")
        ttk.Radiobutton(deliveryFrame, text="Pickup",
                        variable=self.deliveryMethod,
                        value="PICKUP",
                        command=self.updateDeliveryFields).pack(padx=5, pady=2)
        ttk.Radiobutton(deliveryFrame, text="Delivery (+$10)",
                        variable=self.deliveryMethod,
                        value="DELIVERY",
                        command=self.updateDeliveryFields).pack(padx=5, pady=2)

        # Delivery details frame
        self.deliveryDetailsFrame = ttk.Frame(deliveryFrame)
        self.deliveryDetailsFrame.pack(fill=tk.X, padx=5, pady=5)

        # Address input
        ttk.Label(self.deliveryDetailsFrame, text="Delivery Address:").pack()
        self.address = tk.StringVar()
        ttk.Entry(self.deliveryDetailsFrame, textvariable=self.address, width=40).pack(pady=2)

        # Distance input
        ttk.Label(self.deliveryDetailsFrame, text="Distance (km):").pack()
        self.distance = tk.StringVar()
        ttk.Entry(self.deliveryDetailsFrame, textvariable=self.distance, width=10).pack(pady=2)
        ttk.Label(self.deliveryDetailsFrame,
                  text="*Delivery available within 20km radius only").pack()

        # Initially hide delivery details
        self.deliveryDetailsFrame.pack_forget()

        # Total
        self.totalLabel = ttk.Label(summaryFrame, text="Total: $0.00")
        self.totalLabel.pack(pady=5)

        # Checkout button
        ttk.Button(rightFrame, text="Proceed to Checkout", command=self.checkout).pack(pady=5)

        # Load initial data
        self.loadItems()

    def loadItems(self):
        """Load available items from database"""
        with Session(self.engine) as session:
            items = session.query(Item).all()
            for item in self.itemTree.get_children():
                self.itemTree.delete(item)

            for item in items:
                if isinstance(item, WeightedVeggie):
                    self.itemTree.insert('', 'end', values=(item.vegName, 'Weight',
                                                            f"${item.pricePerKilo}/kg", f"{item.weight}kg"))
                elif isinstance(item, PackVeggie):
                    self.itemTree.insert('', 'end', values=(item.vegName, 'Pack',
                                                            f"${item.pricePerPack}/pack", item.numberOfPacks))
                elif isinstance(item, UnitPriceVeggie):
                    self.itemTree.insert('', 'end', values=(item.vegName, 'Unit',
                                                            f"${item.pricePerUnit}/unit", item.quantity))
                elif isinstance(item, PremadeBox):
                    self.itemTree.insert('', 'end', values=(f"Premade Box {item.boxSize}", 'Box',
                                                            self.getBoxPrice(item.boxSize), item.numbOfBoxes))

    def addToCart(self):
        """Add selected item to cart"""
        selected = self.itemTree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to add")
            return

        item_data = self.itemTree.item(selected[0])['values']
        quantity = self.quantity.get()

        # Add to cart tree
        self.cartTree.insert('', 'end', values=(item_data[0], quantity,
                                                f"${float(item_data[2].replace('$', '')) * quantity:.2f}"))
        self.updateTotal()

    def updateDeliveryFields(self):
        """Show/hide delivery fields based on delivery method"""
        if self.deliveryMethod.get() == "DELIVERY":
            self.deliveryDetailsFrame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.deliveryDetailsFrame.pack_forget()
        self.updateTotal()

    def validateDelivery(self):
        """Validate delivery distance"""
        if self.deliveryMethod.get() == "DELIVERY":
            try:
                distance = float(self.distance.get())
                if distance > 20:
                    messagebox.showerror("Error",
                                         "Delivery is only available within 20km radius")
                    return False
                if not self.address.get().strip():
                    messagebox.showerror("Error",
                                         "Please enter delivery address")
                    return False
                return True
            except ValueError:
                messagebox.showerror("Error",
                                     "Please enter a valid distance in kilometers")
                return False
        return True

    def updateTotal(self):
        """Update order total"""
        total = 0
        for item in self.cartTree.get_children():
            price = float(self.cartTree.item(item)['values'][2].replace('$', ''))
            total += price

        if self.deliveryMethod.get() == "DELIVERY":
            total += 10
            self.deliveryDetailsFrame.pack()
        else:
            self.deliveryDetailsFrame.pack_forget()

        self.totalLabel.config(text=f"Total: ${total:.2f}")

    def checkout(self):
        """Process checkout"""
        if not self.cartTree.get_children():
            messagebox.showerror("Error", "Cart is empty")
            return

        if not self.validateDelivery():
            return

        # Create order
        try:
            with Session(self.engine) as session:
                order = Order(
                    orderCustomer=self.customer.id,
                    orderNumber=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    deliveryMethod=DeliveryMethod[self.deliveryMethod.get()]
                )

                if self.deliveryMethod.get() == "DELIVERY":
                    order.deliveryAddress = self.address.get()
                    order.deliveryDistance = float(self.distance.get())
                    order.deliveryFee = 10.0

                session.add(order)
                session.commit()

                messagebox.showinfo("Success", "Order placed successfully!")
                self.clearCart()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")

    def clearCart(self):
        """Clear shopping cart"""
        for item in self.cartTree.get_children():
            self.cartTree.delete(item)
        self.updateTotal()


class CustomerCurrentOrdersTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create orders treeview
        columns = ('Order No', 'Date', 'Status', 'Total', 'Delivery')
        self.orderTree = ttk.Treeview(self, columns=columns, show='headings')

        # Setup column headings
        for col in columns:
            self.orderTree.heading(col, text=col)

        self.orderTree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttonFrame, text="View Details",
                   command=self.viewOrderDetails).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Cancel Order",
                   command=self.cancelOrder).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Refresh",
                   command=self.loadOrders).pack(side=tk.LEFT, padx=5)

        # Load initial data
        self.loadOrders()

    def loadOrders(self):
        """Load current orders"""
        for item in self.orderTree.get_children():
            self.orderTree.delete(item)

        with Session(self.engine) as session:
            orders = session.query(Order).filter(
                Order.orderCustomer == self.customer.id,
                Order.orderStatus.in_([
                    OrderStatus.PENDING.value,
                    OrderStatus.PROCESSING.value
                ])
            ).all()

            for order in orders:
                self.orderTree.insert('', 'end', values=(
                    order.orderNumber,
                    order.orderDate.strftime('%Y-%m-%d'),
                    order.orderStatus,
                    f"${order.total:.2f}",
                    "Yes" if order.deliveryMethod == DeliveryMethod.DELIVERY else "No"
                ))

    def viewOrderDetails(self):
        """Show order details"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to view")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]
        self.showOrderDetails(orderNum)

    def showOrderDetails(self, orderNum):
        """Display order details in new window"""
        detailsWindow = tk.Toplevel(self)
        detailsWindow.title(f"Order Details - {orderNum}")
        detailsWindow.geometry("600x400")

        with Session(self.engine) as session:
            order = session.query(Order).filter_by(orderNumber=orderNum).first()

            # Order info
            infoFrame = ttk.LabelFrame(detailsWindow, text="Order Information")
            infoFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(infoFrame, text=f"Order Number: {order.orderNumber}").pack()
            ttk.Label(infoFrame, text=f"Date: {order.orderDate}").pack()
            ttk.Label(infoFrame, text=f"Status: {order.orderStatus}").pack()

            if order.deliveryMethod == DeliveryMethod.DELIVERY:
                ttk.Label(infoFrame, text=f"Delivery Address: {order.deliveryAddress}").pack()
                ttk.Label(infoFrame, text=f"Delivery Fee: ${order.deliveryFee:.2f}").pack()

            # Items
            itemsFrame = ttk.LabelFrame(detailsWindow, text="Order Items")
            itemsFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            columns = ('Item', 'Quantity', 'Price', 'Total')
            itemTree = ttk.Treeview(itemsFrame, columns=columns, show='headings')
            for col in columns:
                itemTree.heading(col, text=col)

            for line in order.orderLines:
                itemTree.insert('', 'end', values=(
                    line.getItemDetails(),
                    line.itemNumber,
                    f"${line.lineTotal / line.itemNumber:.2f}",
                    f"${line.lineTotal:.2f}"
                ))

            itemTree.pack(fill=tk.BOTH, expand=True)

            # Totals
            totalsFrame = ttk.Frame(detailsWindow)
            totalsFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(totalsFrame, text=f"Subtotal: ${order.subtotal:.2f}").pack()
            if order.discount > 0:
                ttk.Label(totalsFrame, text=f"Discount: ${order.discount:.2f}").pack()
            if order.deliveryFee > 0:
                ttk.Label(totalsFrame, text=f"Delivery Fee: ${order.deliveryFee:.2f}").pack()
            ttk.Label(totalsFrame, text=f"Total: ${order.total:.2f}",
                      font=('Helvetica', 10, 'bold')).pack()

    def cancelOrder(self):
        """Cancel selected order"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to cancel")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]

        try:
            with Session(self.engine) as session:
                order = session.query(Order).filter_by(orderNumber=orderNum).first()
                if order.cancelOrder():
                    session.commit()
                    messagebox.showinfo("Success", "Order cancelled successfully")
                    self.loadOrders()
                else:
                    messagebox.showerror("Error", "Order cannot be cancelled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")


class CustomerPreviousOrdersTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create orders treeview
        columns = ('Order No', 'Date', 'Status', 'Total')
        self.orderTree = ttk.Treeview(self, columns=columns, show='headings')

        for col in columns:
            self.orderTree.heading(col, text=col)

        self.orderTree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        ttk.Button(self, text="View Details",
                   command=self.viewOrderDetails).pack(pady=5)

        # Load initial data
        self.loadOrders()

    def loadOrders(self):
        """Load previous orders"""
        for item in self.orderTree.get_children():
            self.orderTree.delete(item)

        with Session(self.engine) as session:
            orders = session.query(Order).filter(
                Order.orderCustomer == self.customer.id,
                Order.orderStatus.in_([
                    OrderStatus.FULFILLED.value,
                    OrderStatus.CANCELLED.value,
                    OrderStatus.DELIVERED.value
                ])
            ).order_by(Order.orderDate.desc()).all()

            for order in orders:
                self.orderTree.insert('', 'end', values=(
                    order.orderNumber,
                    order.orderDate.strftime('%Y-%m-%d'),
                    order.orderStatus,
                    f"${order.total:.2f}"
                ))

    def viewOrderDetails(self):
        """Show order details"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to view")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]
        self.showOrderDetails(orderNum)  # Reuse the same method from CurrentOrdersTab


class CustomerProfileTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create profile frame
        profileFrame = ttk.LabelFrame(self, text="My Profile")
        profileFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Customer details
        ttk.Label(profileFrame, text=f"Name: {customer.firstName} {customer.lastName}").pack(pady=2)
        ttk.Label(profileFrame, text=f"Username: {customer.username}").pack(pady=2)
        ttk.Label(profileFrame, text=f"Address: {customer.custAddress}").pack(pady=2)
        ttk.Label(profileFrame, text=f"Current Balance: ${customer.custBalance:.2f}").pack(pady=2)
        ttk.Label(profileFrame, text=f"Maximum Owing: ${customer.maxOwing:.2f}").pack(pady=2)

        if customer.type == "Corporate Customer":
            ttk.Label(profileFrame, text=f"Discount Rate: {customer.discountRate * 100}%").pack(pady=2)
            ttk.Label(profileFrame, text=f"Credit Limit: ${customer.maxCredit:.2f}").pack(pady=2)
            ttk.Label(profileFrame, text=f"Minimum Balance: ${customer.minBalance:.2f}").pack(pady=2)