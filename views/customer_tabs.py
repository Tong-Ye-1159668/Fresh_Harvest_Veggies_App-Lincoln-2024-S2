import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from datetime import datetime

from models import PremadeBox, UnitPriceVeggie, PackVeggie, WeightedVeggie, Item, Order, DebitCardPayment, \
    CreditCardPayment, Customer, OrderLine, Veggie
from models.Order import DeliveryMethod, Order,OrderStatus
from views.box_customise_dialog import CustomBoxDialog


class CustomerOrderTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create main container with 3 columns
        mainContainer = ttk.Frame(self)
        mainContainer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left frame - Available Items (1/3 of width)
        leftFrame = ttk.LabelFrame(mainContainer, text="Available Items")
        leftFrame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Center frame - Shopping Cart (1/3 of width)
        centerFrame = ttk.LabelFrame(mainContainer, text="Shopping Cart")
        centerFrame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Right Frame Content - Order Summary
        rightFrame = ttk.LabelFrame(mainContainer, text="Order Summary")
        rightFrame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        mainContainer.grid_columnconfigure(0, weight=1)
        mainContainer.grid_columnconfigure(1, weight=1)
        mainContainer.grid_columnconfigure(2, weight=1)
        mainContainer.grid_rowconfigure(0, weight=1)

        # Left Frame Content - Available Items
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
        self.quantity = tk.StringVar(value="1")  # Changed to StringVar

        # Create different quantity inputs based on item type
        self.intQuantitySpinbox = ttk.Spinbox(quantityFrame, from_=1, to=100,
                                              textvariable=self.quantity)
        self.floatQuantitySpinbox = ttk.Entry(quantityFrame,
                                              textvariable=self.quantity,
                                              width=10)
        self.currentQuantityWidget = self.intQuantitySpinbox  # Default
        self.currentQuantityWidget.pack(side=tk.LEFT, padx=5)

        ttk.Button(quantityFrame, text="Add to Cart",
                   command=self.addToCart).pack(side=tk.LEFT)

        # Center Frame Content - Cart Items
        self.cartTree = ttk.Treeview(centerFrame, columns=('Name', 'Quantity', 'Price'), show='headings')
        self.cartTree.heading('Name', text='Name')
        self.cartTree.heading('Quantity', text='Quantity')
        self.cartTree.heading('Price', text='Price')
        self.cartTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add Remove button under cart
        ttk.Button(centerFrame, text="Remove Selected",
                  command=self.removeFromCart).pack(pady=5)

        # Cart Total Display
        totalsFrame = ttk.LabelFrame(rightFrame, text="Cart Total")
        totalsFrame.pack(fill=tk.X, pady=5, padx=5)

        # Show detailed price breakdown
        self.itemsTotalLabel = ttk.Label(totalsFrame, text="Items Total: $0.00", font=('Helvetica', 10))
        self.itemsTotalLabel.pack(pady=2)

        self.deliveryFeeLabel = ttk.Label(totalsFrame, text="Delivery Fee: $0.00", font=('Helvetica', 10))
        self.deliveryFeeLabel.pack(pady=2)

        ttk.Separator(totalsFrame, orient='horizontal').pack(fill=tk.X, pady=5)

        self.totalLabel = ttk.Label(totalsFrame, text="Total: $0.00", font=('Helvetica', 12, 'bold'))
        self.totalLabel.pack(pady=2)

        # Delivery Options
        deliveryFrame = ttk.LabelFrame(rightFrame, text="Delivery Options")
        deliveryFrame.pack(fill=tk.X, pady=5, padx=5)

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

        ttk.Label(self.deliveryDetailsFrame, text="Delivery Address:").pack()
        self.address = tk.StringVar()
        ttk.Entry(self.deliveryDetailsFrame, textvariable=self.address, width=40).pack(pady=2)

        ttk.Label(self.deliveryDetailsFrame, text="Distance (km):").pack()
        self.distance = tk.StringVar()
        ttk.Entry(self.deliveryDetailsFrame, textvariable=self.distance, width=10).pack(pady=2)
        ttk.Label(self.deliveryDetailsFrame,
                 text="*Delivery available within 20km radius only").pack()

        # Initially hide delivery details
        self.deliveryDetailsFrame.pack_forget()

        # Add space before buttons
        ttk.Separator(rightFrame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Action Buttons Frame
        buttonFrame = ttk.Frame(rightFrame)
        buttonFrame.pack(fill=tk.X, pady=10, padx=5)

        # Clear Cart button (left-aligned)
        ttk.Button(buttonFrame, text="Clear Cart",
                  command=self.clearCart).pack(side=tk.LEFT, padx=5)

        # Submit Order button (right-aligned)
        ttk.Button(buttonFrame, text="Submit Order",
                  command=self.submitOrder).pack(side=tk.RIGHT, padx=5)

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
                    # Show price per kg for weighted items
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Weight',
                        f"${item.pricePerKilo}/kg",
                        f"{item.weight}kg"
                    ))
                elif isinstance(item, PackVeggie):
                    # Show price per pack
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Pack',
                        f"${item.pricePerPack}/pack",
                        item.numberOfPacks
                    ))
                elif isinstance(item, UnitPriceVeggie):
                    # Show price per unit
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Unit',
                        f"${item.pricePerUnit}/unit",
                        item.quantity
                    ))
                elif isinstance(item, PremadeBox):
                    # Show simple price for box (no unit needed)
                    price = PremadeBox.getBoxPrice(item.boxSize)
                    self.itemTree.insert('', 'end', values=(
                        f"Premade Box {item.boxSize}",
                        'Box',
                        price,  # Already includes $ sign
                        item.numbOfBoxes
                    ))

    def handleCustomBox(self, item_data):
        """Handle customization of premade box"""
        box_size = item_data[0].split()[-1]  # Get size from "Premade Box S/M/L"

        dialog = CustomBoxDialog(self, self.engine, box_size)
        self.wait_window(dialog)

        if dialog.result:
            # Add box to cart with selected veggies
            quantity = self.quantity.get()
            price = float(PremadeBox.getBoxPrice(box_size).replace('$', ''))
            total_price = price * quantity

            # Create cart entry with veggie list
            veggie_list = ", ".join(dialog.result)
            self.cartTree.insert('', 'end', values=(
                f"{item_data[0]} ({veggie_list})",
                quantity,
                f"${total_price:.2f}"
            ))
            self.updateTotal()

    # Add method to switch quantity input type
    def updateQuantityInput(self):
        """Switch between integer and float quantity input based on selected item"""
        selected = self.itemTree.selection()
        if not selected:
            return

        item_data = self.itemTree.item(selected[0])['values']

        # Remove current widget
        self.currentQuantityWidget.pack_forget()

        # Show appropriate widget based on item type
        if item_data[1] == 'Weight':  # For weighted veggies
            self.currentQuantityWidget = self.floatQuantitySpinbox
        else:  # For other items
            self.currentQuantityWidget = self.intQuantitySpinbox

        self.currentQuantityWidget.pack(side=tk.LEFT, padx=5)

    def addToCart(self):
        """Add selected item to cart"""
        selected = self.itemTree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to add")
            return

        item_data = self.itemTree.item(selected[0])['values']
        quantity = self.quantity.get()

        # Check if it's a premade box
        if "Premade Box" in item_data[0]:
            self.handleCustomBox(item_data)
            return

        # For other items (veggies)
        try:
            if isinstance(self.currentQuantityWidget, ttk.Entry):
                # For weighted items
                quantity = float(self.quantity.get())
            else:
                # For other items
                quantity = int(self.quantity.get())

            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return

        try:
            # Extract price from price string
            price_str = item_data[2]  # e.g., "$7.99/kg" or "$5.00/pack" or "$3.00/unit"

            # Remove $ and split by /
            price_parts = price_str.replace('$', '').split('/')
            base_price = float(price_parts[0])

            # Calculate total price based on item type
            if '/kg' in price_str:
                # For weighted items, quantity is in kg
                total_price = base_price * quantity
            else:
                # For other items (pack, unit), simple multiplication
                total_price = base_price * quantity

            # Add to cart tree
            self.cartTree.insert('', 'end', values=(
                item_data[0],  # Name
                quantity,  # Quantity
                f"${total_price:.2f}"  # Total price
            ))

            self.updateTotal()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid price format: {price_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item to cart: {str(e)}")

    def removeFromCart(self):
        """Remove selected item from cart"""
        selected = self.cartTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        self.cartTree.delete(selected)
        self.updateTotal()

    def showCartSummary(self):
        """Show a summary window for cart total"""
        summaryWindow = tk.Toplevel(self)
        summaryWindow.title("Cart Summary")
        summaryWindow.geometry("400x300")

        # Make window modal
        summaryWindow.transient(self)
        summaryWindow.grab_set()

        # Center window
        summaryWindow.update_idletasks()
        width = summaryWindow.winfo_width()
        height = summaryWindow.winfo_height()
        x = (summaryWindow.winfo_screenwidth() // 2) - (width // 2)
        y = (summaryWindow.winfo_screenheight() // 2) - (height // 2)
        summaryWindow.geometry(f'{width}x{height}+{x}+{y}')

        # Create content
        ttk.Label(summaryWindow, text="Cart Summary",
                  font=('Helvetica', 12, 'bold')).pack(pady=10)

        # Cart items frame
        cartFrame = ttk.LabelFrame(summaryWindow, text="Items in Cart")
        cartFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create Treeview for cart items
        columns = ('Item', 'Quantity', 'Price')
        cartSummaryTree = ttk.Treeview(cartFrame, columns=columns, show='headings', height=5)

        for col in columns:
            cartSummaryTree.heading(col, text=col)

        # Add all items from cart
        cart_total = 0
        for item in self.cartTree.get_children():
            values = self.cartTree.item(item)['values']
            cartSummaryTree.insert('', 'end', values=values)
            # Add to total (remove $ and convert to float)
            cart_total += float(values[2].replace('$', ''))

        cartSummaryTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Total information
        totalFrame = ttk.Frame(summaryWindow)
        totalFrame.pack(fill=tk.X, padx=10, pady=5)

        # Show subtotal
        ttk.Label(totalFrame, text=f"Subtotal: ${cart_total:.2f}",
                  font=('Helvetica', 10)).pack(pady=2)

        # Show delivery fee if applicable
        if self.deliveryMethod.get() == "DELIVERY":
            ttk.Label(totalFrame, text="Delivery Fee: $10.00",
                      font=('Helvetica', 10)).pack(pady=2)
            ttk.Label(totalFrame, text=f"Total: ${cart_total + 10:.2f}",
                      font=('Helvetica', 10, 'bold')).pack(pady=2)
        else:
            ttk.Label(totalFrame, text=f"Total: ${cart_total:.2f}",
                      font=('Helvetica', 10, 'bold')).pack(pady=2)

        # Buttons
        buttonFrame = ttk.Frame(summaryWindow)
        buttonFrame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttonFrame, text="Continue Shopping",
                   command=summaryWindow.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Proceed to Checkout",
                   command=lambda: [summaryWindow.destroy(), self.submitOrder()]).pack(side=tk.LEFT, padx=5)

    def viewFullCart(self):
        """Show full cart details"""
        cartWindow = tk.Toplevel(self)
        cartWindow.title("Shopping Cart")
        cartWindow.geometry("500x400")

        ttk.Label(cartWindow, text="Shopping Cart",
                  font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Create Treeview for cart items
        columns = ('Item', 'Quantity', 'Price')
        cartDetailTree = ttk.Treeview(cartWindow, columns=columns, show='headings')

        for col in columns:
            cartDetailTree.heading(col, text=col)

        # Add all items from cart
        cart_total = 0
        for item in self.cartTree.get_children():
            values = self.cartTree.item(item)['values']
            cartDetailTree.insert('', 'end', values=values)
            cart_total += float(values[2].replace('$', ''))

        cartDetailTree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Total and delivery info
        infoFrame = ttk.LabelFrame(cartWindow, text="Order Summary")
        infoFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(infoFrame, text=f"Subtotal: ${cart_total:.2f}").pack(pady=2)
        if self.deliveryMethod.get() == "DELIVERY":
            ttk.Label(infoFrame, text="Delivery Fee: $10.00").pack(pady=2)
            ttk.Label(infoFrame,
                      text=f"Total: ${cart_total + 10:.2f}",
                      font=('Helvetica', 10, 'bold')).pack(pady=2)
        else:
            ttk.Label(infoFrame,
                      text=f"Total: ${cart_total:.2f}",
                      font=('Helvetica', 10, 'bold')).pack(pady=2)

        # Buttons
        buttonFrame = ttk.Frame(cartWindow)
        buttonFrame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttonFrame, text="Close",
                   command=cartWindow.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Checkout",
                   command=lambda: [cartWindow.destroy(), self.submitOrder()]).pack(side=tk.LEFT, padx=5)

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
        subtotal = 0
        for item in self.cartTree.get_children():
            price = float(self.cartTree.item(item)['values'][2].replace('$', ''))
            subtotal += price

        # Update items total
        self.itemsTotalLabel.config(text=f"Items Total: ${subtotal:.2f}")

        # Calculate delivery fee
        delivery_fee = 10.0 if self.deliveryMethod.get() == "DELIVERY" else 0.0
        self.deliveryFeeLabel.config(text=f"Delivery Fee: ${delivery_fee:.2f}")

        # Calculate total
        total = subtotal + delivery_fee
        self.totalLabel.config(text=f"Total: ${total:.2f}")

    def submitOrder(self):
        """Submit and process the order"""
        if not self.cartTree.get_children():
            messagebox.showerror("Error", "Cart is empty!")
            return

        if not self.validateDelivery():
            return

        try:
            with Session(self.engine) as session:
                # Calculate total order amount
                total_amount = float(self.totalLabel.cget("text").split('$')[1])

                # Check if order would exceed maxOwing
                customer = session.query(Customer).get(self.customer.id)
                if customer.custBalance - total_amount < -customer.maxOwing:
                    messagebox.showerror("Error",
                                         "This order would exceed your maximum owing limit.")
                    return

                # Create new order
                order = Order(
                    orderCustomer=self.customer.id,
                    orderNumber=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    deliveryMethod=DeliveryMethod[self.deliveryMethod.get()]
                )

                if self.deliveryMethod.get() == "DELIVERY":
                    order.deliveryAddress = self.address.get()
                    order.deliveryDistance = float(self.distance.get())
                    order.deliveryFee = 10.0

                # Process cart items
                for item in self.cartTree.get_children():
                    cart_item = self.cartTree.item(item)['values']
                    item_name = cart_item[0].split(' (')[0]  # Get base name without customization
                    quantity = float(cart_item[1])
                    price = float(cart_item[2].replace('$', ''))

                    # Find the item in database and update stock
                    db_item = None
                    if "Premade Box" in item_name:
                        box_size = item_name.split()[-1]  # Get 'S', 'M', or 'L'
                        db_item = session.query(PremadeBox).filter_by(boxSize=box_size).first()
                    else:
                        # For veggies
                        db_item = session.query(Veggie).filter_by(vegName=item_name).first()

                    if db_item:
                        # Update stock based on item type
                        if isinstance(db_item, WeightedVeggie):
                            if db_item.weight < quantity:
                                raise ValueError(f"Insufficient stock for {item_name}")
                            db_item.weight -= quantity
                        elif isinstance(db_item, PackVeggie):
                            if db_item.numberOfPacks < quantity:
                                raise ValueError(f"Insufficient stock for {item_name}")
                            db_item.numberOfPacks -= int(quantity)
                        elif isinstance(db_item, UnitPriceVeggie):
                            if db_item.quantity < quantity:
                                raise ValueError(f"Insufficient stock for {item_name}")
                            db_item.quantity -= int(quantity)
                        elif isinstance(db_item, PremadeBox):
                            if db_item.numbOfBoxes < quantity:
                                raise ValueError(f"Insufficient stock for {item_name}")
                            db_item.numbOfBoxes -= int(quantity)

                        # Create order line
                        order_line = OrderLine(
                            itemNumber=quantity,
                            lineTotal=price
                        )
                        order_line.item = db_item
                        order.orderLines.append(order_line)
                    else:
                        raise ValueError(f"Item not found: {item_name}")

                # Calculate and set totals
                order.subtotal = sum(line.lineTotal for line in order.orderLines)
                order.total = order.subtotal + (10.0 if self.deliveryMethod.get() == "DELIVERY" else 0.0)

                # Update customer balance
                customer.custBalance -= order.total

                # Save to database
                session.add(order)
                session.commit()

                messagebox.showinfo("Success",
                                    f"Order placed successfully!\nYour new balance: ${customer.custBalance:.2f}")
                self.clearCart()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            session.rollback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")
            session.rollback()

    def clearCart(self):
        """Clear all items from cart"""
        for item in self.cartTree.get_children():
            self.cartTree.delete(item)
        self.updateTotal()
        if self.deliveryMethod.get() == "DELIVERY":
            self.deliveryMethod.set("PICKUP")
            self.updateDeliveryFields()


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
        ttk.Button(buttonFrame, text="Make Payment",
                   command=self.makePayment).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Refresh",
                   command=self.loadOrders).pack(side=tk.LEFT, padx=5)

        # Load initial data
        self.loadOrders()

    def makePayment(self):
        """Open payment window for selected order"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to pay")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]

        with Session(self.engine) as session:
            order = session.query(Order).filter_by(orderNumber=orderNum).first()
            if not order:
                messagebox.showerror("Error", "Order not found")
                return

            # Check if order is already in PROCESSING status
            if order.orderStatus == OrderStatus.PROCESSING.value:
                messagebox.showinfo("Information", "You have already paid for this order.")
                return

            # Show payment dialog
            paymentWindow = PaymentDialog(self, self.engine, order)
            self.wait_window(paymentWindow)

            # Refresh orders after payment
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

            # Payment History
            paymentFrame = ttk.LabelFrame(detailsWindow, text="Payment History")
            paymentFrame.pack(fill=tk.X, padx=10, pady=5)

            paymentColumns = ('Date', 'Amount', 'Type')
            paymentTree = ttk.Treeview(paymentFrame, columns=paymentColumns, show='headings', height=3)

            for col in paymentColumns:
                paymentTree.heading(col, text=col)

            for payment in order.payments:
                paymentTree.insert('', 'end', values=(
                    payment.paymentDate.strftime('%Y-%m-%d'),
                    f"${payment.paymentAmount:.2f}",
                    payment.type
                ))

            paymentTree.pack(fill=tk.X)

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

            # Show remaining balance if any
            remaining = order.calcRemainingBalance()
            if remaining > 0:
                ttk.Label(totalsFrame, text=f"Remaining Balance: ${remaining:.2f}",
                          foreground='red').pack()

    def cancelOrder(self):
        """Cancel selected order"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to cancel")
            return

        if not messagebox.askyesno("Confirm Cancellation",
                                   "Are you sure you want to cancel this order?"):
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]

        try:
            with Session(self.engine) as session:
                order = session.query(Order).filter_by(orderNumber=orderNum).first()

                success, message = order.cancelOrder()
                if success:
                    session.commit()
                    messagebox.showinfo("Success", message)
                    self.loadOrders()  # Refresh the order list
                else:
                    messagebox.showerror("Error", message)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")


# Add new PaymentDialog class
class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, engine, order):
        super().__init__(parent)
        self.engine = engine
        self.order = order

        self.title("Make Payment")
        self.geometry("400x500")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Order details frame
        detailsFrame = ttk.LabelFrame(self, text="Order Details")
        detailsFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(detailsFrame, text=f"Order Number: {order.orderNumber}").pack()
        ttk.Label(detailsFrame, text=f"Order Total: ${order.total:.2f}").pack()

        # Calculate remaining balance
        remainingBalance = order.calcRemainingBalance()
        ttk.Label(detailsFrame, text=f"Remaining Balance: ${remainingBalance:.2f}",
                  font=('Helvetica', 10, 'bold')).pack()

        # Payment method frame
        methodFrame = ttk.LabelFrame(self, text="Payment Method")
        methodFrame.pack(fill=tk.X, padx=10, pady=5)

        self.paymentMethod = tk.StringVar(value="credit")
        ttk.Radiobutton(methodFrame, text="Credit Card",
                        variable=self.paymentMethod,
                        value="credit").pack(padx=5, pady=2)
        ttk.Radiobutton(methodFrame, text="Debit Card",
                        variable=self.paymentMethod,
                        value="debit").pack(padx=5, pady=2)

        # Payment amount frame
        amountFrame = ttk.LabelFrame(self, text="Payment Amount")
        amountFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(amountFrame, text="Amount:").pack()
        self.amount = tk.StringVar(value=f"{remainingBalance:.2f}")
        ttk.Entry(amountFrame, textvariable=self.amount).pack(pady=5)

        # Card details frame
        self.cardFrame = ttk.LabelFrame(self, text="Card Details")
        self.cardFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.cardFrame, text="Card Number:").pack()
        self.cardNumber = tk.StringVar()
        ttk.Entry(self.cardFrame, textvariable=self.cardNumber).pack(pady=2)

        ttk.Label(self.cardFrame, text="Expiry Date (MM/YY):").pack()
        self.expiryDate = tk.StringVar()
        ttk.Entry(self.cardFrame, textvariable=self.expiryDate).pack(pady=2)

        ttk.Label(self.cardFrame, text="CVV:").pack()
        self.cvv = tk.StringVar()
        ttk.Entry(self.cardFrame, textvariable=self.cvv, show="*").pack(pady=2)

        # Buttons
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(buttonFrame, text="Cancel",
                   command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Make Payment",
                   command=self.processPayment).pack(side=tk.RIGHT, padx=5)

    def processPayment(self):
        """Process the payment"""
        try:
            # Clean the amount string and convert to float
            amount_str = self.amount.get().strip()
            amount = float(amount_str)

            if amount <= 0:
                messagebox.showerror("Error", "Payment amount must be greater than 0")
                return

            with Session(self.engine) as session:
                order = session.merge(self.order)
                customer = order.customer

                # Create payment based on method
                if self.paymentMethod.get() == "credit":
                    payment = CreditCardPayment(
                        paymentAmount=amount,
                        paymentDate=datetime.now(),
                        cardNumber=self.cardNumber.get().strip(),
                        cardExpiryDate=datetime.strptime(self.expiryDate.get().strip(), "%m/%y"),
                        cardType="Credit"
                    )
                else:
                    payment = DebitCardPayment(
                        paymentAmount=amount,
                        paymentDate=datetime.now(),
                        debitCardNumber=self.cardNumber.get().strip(),
                        bankName="Default Bank"
                    )

                payment.order = order
                session.add(payment)

                # Update customer balance
                customer.custBalance += amount

                # Update order status to PROCESSING after payment
                order.orderStatus = OrderStatus.PROCESSING.value

                session.commit()

                messagebox.showinfo("Success",
                                    f"Payment of ${amount:.2f} processed successfully\n" +
                                    f"New balance: ${customer.custBalance:.2f}\n" +
                                    "Order status updated to Processing")
                self.destroy()

        except ValueError as e:
            # Add more specific error messages
            if "time data" in str(e):
                messagebox.showerror("Error", "Please enter date in MM/YY format")
            else:
                messagebox.showerror("Error", "Please enter a valid payment amount")
        except Exception as e:
            messagebox.showerror("Error", f"Payment failed: {str(e)}")

        except ValueError as e:
            # Add more specific error messages
            if "time data" in str(e):
                messagebox.showerror("Error", "Please enter date in MM/YY format")
            else:
                messagebox.showerror("Error", "Please enter a valid payment amount")
        except Exception as e:
            messagebox.showerror("Error", f"Payment failed: {str(e)}")

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

            # Payment History
            paymentFrame = ttk.LabelFrame(detailsWindow, text="Payment History")
            paymentFrame.pack(fill=tk.X, padx=10, pady=5)

            paymentColumns = ('Date', 'Amount', 'Type')
            paymentTree = ttk.Treeview(paymentFrame, columns=paymentColumns, show='headings', height=3)

            for col in paymentColumns:
                paymentTree.heading(col, text=col)

            for payment in order.payments:
                paymentTree.insert('', 'end', values=(
                    payment.paymentDate.strftime('%Y-%m-%d'),
                    f"${payment.paymentAmount:.2f}",
                    payment.type
                ))

            paymentTree.pack(fill=tk.X)

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