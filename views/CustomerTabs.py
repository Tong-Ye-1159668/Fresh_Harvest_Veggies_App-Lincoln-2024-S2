import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session
from datetime import datetime

from models import PremadeBox, UnitPriceVeggie, PackVeggie, WeightedVeggie, Item, Order, DebitCardPayment, \
    CreditCardPayment, Customer, OrderLine, Veggie, Payment
from models.Order import DeliveryMethod, Order,OrderStatus
from views.BoxCustomiseDialog import CustomBoxDialog


class CustomerOrderTab(ttk.Frame):
    def __init__(self, parent, engine, customer):
        super().__init__(parent)
        self.engine = engine
        self.customer = customer

        # Create main container with 4 columns
        mainContainer = ttk.Frame(self)
        mainContainer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left frame - Available Items (1/4 of width)
        leftFrame = ttk.LabelFrame(mainContainer, text="Available Items")
        leftFrame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)

        # Center frame - Shopping Cart (1/4 of width)
        centerFrame = ttk.LabelFrame(mainContainer, text="Shopping Cart")
        centerFrame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=5, pady=5)

        # Right Frame Content - Order Summary (2/4 of width)
        rightFrame = ttk.LabelFrame(mainContainer, text="Order Summary")
        rightFrame.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Configure grid weights for 4 columns (1:1:2 ratio)
        mainContainer.grid_columnconfigure(0, weight=1)  # Available Items (1/4)
        mainContainer.grid_columnconfigure(1, weight=1)  # Shopping Cart (1/4)
        mainContainer.grid_columnconfigure(2, weight=2)  # Order Summary (2/4)
        mainContainer.grid_rowconfigure(0, weight=1)

        # Left Frame Content - Available Items
        self.itemTree = ttk.Treeview(leftFrame, columns=('Name', 'Type', 'Price', 'Stock'), show='headings')
        self.itemTree.heading('Name', text='Name')
        self.itemTree.heading('Type', text='Type')
        self.itemTree.heading('Price', text='Price')
        self.itemTree.heading('Stock', text='Available')

        # Set specific widths for the columns
        self.itemTree.column('Name', width=100)
        self.itemTree.column('Type', width=60)
        self.itemTree.column('Price', width=70)
        self.itemTree.column('Stock', width=70)

        # Add scrollbar to Available Items
        itemScrollbar = ttk.Scrollbar(leftFrame, orient="vertical", command=self.itemTree.yview)
        itemScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.itemTree.configure(yscrollcommand=itemScrollbar.set)
        self.itemTree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add quantity spinbox and Add to Cart button
        quantityFrame = ttk.Frame(leftFrame)
        quantityFrame.pack(fill=tk.X, pady=5)
        ttk.Label(quantityFrame, text="Quantity:").pack(side=tk.LEFT, padx=(0, 2))
        self.quantity = tk.StringVar(value="1")

        # Create different quantity inputs based on item type
        self.intQuantitySpinbox = ttk.Spinbox(quantityFrame, from_=1, to=100,
                                              textvariable=self.quantity, width=8)
        self.floatQuantitySpinbox = ttk.Entry(quantityFrame,
                                              textvariable=self.quantity,
                                              width=8)
        self.currentQuantityWidget = self.intQuantitySpinbox
        self.currentQuantityWidget.pack(side=tk.LEFT, padx=2)

        ttk.Button(quantityFrame, text="Add to Cart",
                   command=self.addToCart).pack(side=tk.LEFT, padx=2)

        # Center Frame Content - Shopping Cart
        self.cartTree = ttk.Treeview(centerFrame, columns=('Name', 'Quantity', 'Price'), show='headings')
        self.cartTree.heading('Name', text='Name')
        self.cartTree.heading('Quantity', text='Quantity')
        self.cartTree.heading('Price', text='Price')

        # Set specific widths for the cart columns
        self.cartTree.column('Name', width=100)
        self.cartTree.column('Quantity', width=70)
        self.cartTree.column('Price', width=70)

        # Add scrollbar to Shopping Cart
        cartScrollbar = ttk.Scrollbar(centerFrame, orient="vertical", command=self.cartTree.yview)
        cartScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cartTree.configure(yscrollcommand=cartScrollbar.set)
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
        self.address = tk.StringVar(value=self.customer.custAddress)  # Pre-fill with customer's address
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
            try:
                # Get quantity and validate it's an integer
                quantity = int(self.quantity.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return

                # Extract base price for the box size
                base_price = float(PremadeBox.getBoxPrice(box_size).replace('$', ''))
                total_price = base_price * quantity

                # Format selected veggies for display
                selected_veggies = ", ".join(dialog.result)

                # Add to cart with selected veggies
                self.cartTree.insert('', 'end', values=(
                    f"Premade Box {box_size} ({selected_veggies})",  # Name and contents
                    quantity,  # Quantity
                    f"${total_price:.2f}"  # Total price
                ))

                # Update cart total
                self.updateTotal()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding box to cart: {str(e)}")

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

        # Check if it's a premade box before entering session context
        if "Premade Box" in item_data[0]:
            self.handleCustomBox(item_data)
            return

        try:
            # Validate quantity before database operations
            if item_data[1] == 'Weight':  # For weighted veggies
                quantity = float(self.quantity.get())
                if quantity < 0.01:
                    messagebox.showerror("Error", "Minimum weight must be 0.01 kg")
                    return
            else:  # For other items
                quantity = int(self.quantity.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return

            # Start database session
            with Session(self.engine) as session:
                # Refresh customer object within session
                self.customer = session.merge(self.customer)

                # Extract price from price string
                price_str = item_data[2]  # e.g., "$7.99/kg" or "$5.00/pack" or "$3.00/unit"
                price_parts = price_str.replace('$', '').split('/')
                base_price = float(price_parts[0])

                # Calculate total price based on item type
                if item_data[1] == 'Weight':
                    total_price = base_price * quantity
                    quantity_display = f"{quantity:.2f}"  # Format weight to 2 decimal places
                else:
                    total_price = base_price * quantity
                    quantity_display = str(quantity)

                # Query the actual item from database
                if item_data[1] == 'Weight':
                    item = session.query(WeightedVeggie).filter_by(vegName=item_data[0]).first()
                    if not item or item.weight < quantity:
                        raise ValueError(f"Insufficient stock for {item_data[0]}")
                elif item_data[1] == 'Pack':
                    item = session.query(PackVeggie).filter_by(vegName=item_data[0]).first()
                    if not item or item.numberOfPacks < quantity:
                        raise ValueError(f"Insufficient stock for {item_data[0]}")
                elif item_data[1] == 'Unit':
                    item = session.query(UnitPriceVeggie).filter_by(vegName=item_data[0]).first()
                    if not item or item.quantity < quantity:
                        raise ValueError(f"Insufficient stock for {item_data[0]}")
                else:
                    raise ValueError(f"Unknown item type: {item_data[1]}")

                # Add to cart tree (do this before committing to ensure no database errors)
                self.cartTree.insert('', 'end', values=(
                    item_data[0],
                    quantity_display,
                    f"${total_price:.2f}"
                ))

                # Update stock in database
                if isinstance(item, WeightedVeggie):
                    item.weight -= quantity
                elif isinstance(item, PackVeggie):
                    item.numberOfPacks -= quantity
                elif isinstance(item, UnitPriceVeggie):
                    item.quantity -= quantity

                # Commit the transaction
                session.commit()

                # Update cart total
                self.updateTotal()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error adding item to cart: {str(e)}")
            if 'session' in locals():
                session.rollback()

        # Reset quantity spinbox to default
        self.quantity.set("1")

    def removeFromCart(self):
        """Remove selected item from cart"""
        selected = self.cartTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        self.cartTree.delete(selected)
        self.updateTotal()

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

        # Apply discount for corporate customers
        if self.customer.type == "Corporate Customer":
            discount_amount = subtotal * self.customer.discountRate
            discount_label = ttk.Label(self,
                                       text=f"Discount ({self.customer.discountRate * 100}%): -${discount_amount:.2f}")

            # Calculate total with discount
            total = (subtotal - discount_amount) + delivery_fee
            self.totalLabel.config(text=f"Total (after discount): ${total:.2f}")
        else:
            # Regular customer - no discount
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
                # Get fresh customer data
                customer = session.query(Customer).get(self.customer.id)

                # Calculate order amount (before discount)
                total_amount = float(self.totalLabel.cget("text").split('$')[1])

                # Apply discount for corporate customers
                if customer.type == "Corporate Customer":
                    # Apply the discount to the total amount
                    discounted_amount = total_amount * (1 - customer.discountRate)
                else:
                    discounted_amount = total_amount

                # Calculate total need-to-pay amount from PENDING orders
                pending_orders = session.query(Order).filter(
                    Order.orderCustomer == customer.id,
                    Order.orderStatus == OrderStatus.PENDING.value
                ).all()

                total_need_to_pay = sum(order.calcRemainingBalance() for order in pending_orders)
                potential_need_to_pay = total_need_to_pay + discounted_amount

                # Check against appropriate limit based on customer type
                if customer.type == "Corporate Customer":
                    limit = customer.maxCredit
                    limit_name = "credit limit"
                else:
                    limit = customer.maxOwing
                    limit_name = "maximum owing limit"

                if potential_need_to_pay > limit:
                    # Show different messages based on customer type
                    if customer.type == "Corporate Customer":
                        messagebox.showerror("Error",
                                             f"Cannot place order: Total need-to-pay amount (${potential_need_to_pay:.2f}) "
                                             f"would exceed your {limit_name} (${limit:.2f})\n"
                                             f"Current unpaid amount: ${total_need_to_pay:.2f}\n"
                                             f"New order amount: ${total_amount:.2f}\n"
                                             f"Discounted order amount: ${discounted_amount:.2f}")
                    else:
                        messagebox.showerror("Error",
                                             f"Cannot place order: Total need-to-pay amount (${potential_need_to_pay:.2f}) "
                                             f"would exceed your {limit_name} (${limit:.2f})\n"
                                             f"Current unpaid amount: ${total_need_to_pay:.2f}\n"
                                             f"New order amount: ${total_amount:.2f}")
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

                # Save to database
                session.add(order)
                session.commit()

                messagebox.showinfo("Success", "Order placed successfully!"
                                               "\nPlease go to Current Orders tab to make a payment.")
                self.clearCart()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            session.rollback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")
            session.rollback()

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

        # Update columns to include Remaining Payment
        columns = ('Order No', 'Date', 'Status', 'Total', 'Need to Pay', 'Delivery')
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
            if order.orderStatus in [OrderStatus.PROCESSING.value, OrderStatus.SUBMITTED.value]:
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
                    OrderStatus.SUBMITTED.value,
                    OrderStatus.PROCESSING.value
                ])
            ).all()

            for order in orders:
                remaining_payment = order.calcRemainingBalance()
                self.orderTree.insert('', 'end', values=(
                    order.orderNumber,
                    order.orderDate.strftime('%Y-%m-%d'),
                    order.orderStatus,
                    f"${order.total:.2f}",
                    f"${remaining_payment:.2f}",
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
        detailsWindow.geometry("800x600")

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
                    self.loadOrders()
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

        # Initialize widget variables
        self.creditCardEntry = None
        self.debitCardEntry = None

        self.title("Make Payment")
        self.geometry("400x650")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Create main container frame
        mainFrame = ttk.Frame(self, padding="20")
        mainFrame.pack(fill=tk.BOTH, expand=True)

        # Create all frames and widgets
        self.createOrderDetailsFrame(mainFrame)
        self.createPaymentMethodFrame(mainFrame)
        self.createPaymentAmountFrame(mainFrame)
        self.createCreditCardFrame(mainFrame)
        self.createDebitCardFrame(mainFrame)
        self.createBalanceFrame(mainFrame)
        self.createButtonFrame()

        # Setup bindings after all widgets are created
        self.setupBindings()

    def createOrderDetailsFrame(self, parent):
        detailsFrame = ttk.LabelFrame(parent, text="Order Details")
        detailsFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(detailsFrame, text=f"Order Number: {self.order.orderNumber}").pack()
        ttk.Label(detailsFrame, text=f"Order Total: ${self.order.total:.2f}").pack()

        remainingOrderBalance = self.order.calcRemainingBalance()
        ttk.Label(detailsFrame,
                  text=f"Remaining Payment: ${remainingOrderBalance:.2f}",
                  font=('Helvetica', 10, 'bold')).pack()

        balance_color = 'green' if self.order.customer.custBalance > 0 else 'black'
        ttk.Label(detailsFrame,
                  text=f"Current Balance: ${self.order.customer.custBalance:.2f}",
                  font=('Helvetica', 10),
                  foreground=balance_color).pack()

    def createPaymentMethodFrame(self, parent):
        methodFrame = ttk.LabelFrame(parent, text="Payment Method")
        methodFrame.pack(fill=tk.X, padx=10, pady=5)

        self.paymentMethod = tk.StringVar(value="credit")
        ttk.Radiobutton(methodFrame, text="Credit Card",
                        variable=self.paymentMethod,
                        value="credit",
                        command=self.updateCardFields).pack(padx=5, pady=2)
        ttk.Radiobutton(methodFrame, text="Debit Card",
                        variable=self.paymentMethod,
                        value="debit",
                        command=self.updateCardFields).pack(padx=5, pady=2)

        useBalanceBtn = ttk.Radiobutton(methodFrame, text="Pay with Balance",
                                        variable=self.paymentMethod,
                                        value="balance",
                                        command=self.updatePaymentFields)
        useBalanceBtn.pack(padx=5, pady=2)

        if self.order.customer.custBalance <= 0:
            useBalanceBtn.configure(state='disabled')

    def createPaymentAmountFrame(self, parent):
        amountFrame = ttk.LabelFrame(parent, text="Payment Amount")
        amountFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(amountFrame, text="Amount:").pack()
        self.amount = tk.StringVar(value=f"{self.order.calcRemainingBalance():.2f}")
        self.amountEntry = ttk.Entry(amountFrame, textvariable=self.amount)
        self.amountEntry.pack(pady=5)

    def createCreditCardFrame(self, parent):
        self.creditFrame = ttk.LabelFrame(parent, text="Credit Card Details")
        self.creditFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.creditFrame, text="Card Number:").pack()
        self.creditCardNumber = tk.StringVar()
        self.creditCardEntry = ttk.Entry(self.creditFrame, textvariable=self.creditCardNumber)
        self.creditCardEntry.pack(pady=2)

        ttk.Label(self.creditFrame, text="Expiry Date (MM/YY):").pack()
        self.expiryDate = tk.StringVar()
        ttk.Entry(self.creditFrame, textvariable=self.expiryDate).pack(pady=2)

        ttk.Label(self.creditFrame, text="Card Type:").pack()
        self.cardType = tk.StringVar(value="Visa")
        cardTypeCombo = ttk.Combobox(self.creditFrame,
                                     textvariable=self.cardType,
                                     values=["Visa", "Mastercard", "American Express"],
                                     state='readonly')
        cardTypeCombo.pack(pady=2)

    def createDebitCardFrame(self, parent):
        self.debitFrame = ttk.LabelFrame(parent, text="Debit Card Details")
        self.debitFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.debitFrame, text="Card Number:").pack()
        self.debitCardNumber = tk.StringVar()
        self.debitCardEntry = ttk.Entry(self.debitFrame, textvariable=self.debitCardNumber)
        self.debitCardEntry.pack(pady=2)

        ttk.Label(self.debitFrame, text="Bank Name:").pack()
        self.bankName = tk.StringVar()
        ttk.Entry(self.debitFrame, textvariable=self.bankName).pack(pady=2)

        # Initially hide debit frame
        self.debitFrame.pack_forget()

    def createBalanceFrame(self, parent):
        self.balanceFrame = ttk.LabelFrame(parent, text="Balance Payment Details")
        self.balanceFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.balanceFrame,
                  text=f"Available Balance: ${self.order.customer.custBalance:.2f}").pack()

        # Initially hide balance frame
        self.balanceFrame.pack_forget()

    def createButtonFrame(self):
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        ttk.Button(buttonFrame, text="Cancel",
                   command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Make Payment",
                   command=self.processPayment).pack(side=tk.RIGHT, padx=5)

    def setupBindings(self):
        """Setup all event bindings"""
        self.amountEntry.bind('<KeyRelease>', self.validateAmount)
        self.creditCardEntry.bind('<KeyRelease>',
                                  lambda e: self.validateCardNumber(self.creditCardNumber))
        self.debitCardEntry.bind('<KeyRelease>',
                                 lambda e: self.validateCardNumber(self.debitCardNumber))

    def updatePaymentFields(self):
        """Show/hide appropriate payment fields based on payment method"""
        if self.paymentMethod.get() == "credit":
            self.creditFrame.pack(fill=tk.X, padx=10, pady=5)
            self.debitFrame.pack_forget()
            self.balanceFrame.pack_forget()
        elif self.paymentMethod.get() == "debit":
            self.debitFrame.pack(fill=tk.X, padx=10, pady=5)
            self.creditFrame.pack_forget()
            self.balanceFrame.pack_forget()
        else:  # balance payment
            self.balanceFrame.pack(fill=tk.X, padx=10, pady=5)
            self.creditFrame.pack_forget()
            self.debitFrame.pack_forget()
            # Validate amount against available balance
            try:
                amount = float(self.amount.get())
                if amount > self.order.customer.custBalance:
                    self.amount.set(str(self.order.customer.custBalance))
            except ValueError:
                pass

    def validateAmount(self, event):
        """Validate amount to allow only digits and two decimal places"""
        value = self.amount.get().strip()

        # If empty, allow it
        if not value:
            return

        # Remove all non-digit characters except decimal point
        filtered = ''.join(char for char in value if char.isdigit() or char == '.')

        # Handle multiple decimal points
        decimal_points = filtered.count('.')
        if decimal_points > 1:
            # Keep only the first decimal point
            parts = filtered.split('.')
            filtered = parts[0] + '.' + ''.join(parts[1:])

        # Handle decimal places
        if '.' in filtered:
            main, decimal = filtered.split('.')
            # Limit to 2 decimal places
            filtered = main + '.' + decimal[:2]

        # Update the entry if value has changed
        if filtered != value:
            self.amount.set(filtered)

    def validateCardNumber(self, cardVar):
        """Validate card number to only allow digits"""
        value = cardVar.get()
        # Remove any non-digits
        digits_only = ''.join(filter(str.isdigit, value))
        cardVar.set(digits_only)

    def updateCardFields(self):
        """Show/hide appropriate card fields based on payment method"""
        if self.paymentMethod.get() == "credit":
            self.creditFrame.pack(fill=tk.X, padx=10, pady=5)
            self.debitFrame.pack_forget()
        else:
            self.debitFrame.pack(fill=tk.X, padx=10, pady=5)
            self.creditFrame.pack_forget()

    def validateFields(self):
        """Validate input fields based on payment method"""
        try:
            # Validate amount
            amount_str = self.amount.get().strip()
            if not amount_str:
                raise ValueError("Please enter payment amount")

            try:
                amount = float(amount_str)
            except ValueError:
                raise ValueError("Invalid payment amount format")

            if amount <= 0:
                raise ValueError("Payment amount must be greater than 0")

            # Validate amount format
            if '.' in amount_str:
                _, decimals = amount_str.split('.')
                if len(decimals) > 2:
                    raise ValueError("Amount can only have up to 2 decimal places")

            # For balance payment, check if sufficient balance available
            if self.paymentMethod.get() == "balance":
                if amount > self.order.customer.custBalance:
                    raise ValueError(f"Insufficient balance (Available: ${self.order.customer.custBalance:.2f})")

            if self.paymentMethod.get() == "credit":
                # Validate credit card fields
                card_number = self.creditCardNumber.get().strip()
                if not card_number:
                    raise ValueError("Please enter credit card number")
                if not card_number.isdigit():
                    raise ValueError("Credit card number must contain only digits")
                if len(card_number) < 16:
                    raise ValueError("Credit card number must be at least 16 digits")
                if len(card_number) > 20:
                    raise ValueError("Credit card number cannot exceed 20 digits")

                # Validate expiry date
                expiry = self.expiryDate.get().strip()
                if not expiry:
                    raise ValueError("Please enter expiry date")
                if not expiry or len(expiry) != 5:  # MM/YY format
                    raise ValueError("Please enter expiry date in MM/YY format")

                try:
                    month, year = expiry.split('/')
                    exp_month = int(month)
                    exp_year = 2000 + int(year)  # Convert YY to YYYY

                    # Get current date
                    current_date = datetime.now()
                    current_year = current_date.year
                    current_month = current_date.month

                    # Validate month range
                    if not (1 <= exp_month <= 12):
                        raise ValueError("Invalid expiry month")

                    # Check if card is expired
                    if exp_year < current_year or \
                            (exp_year == current_year and exp_month < current_month):
                        raise ValueError("Card has expired")

                except ValueError as e:
                    if str(e) in ["Invalid expiry month", "Card has expired"]:
                        raise
                    raise ValueError("Invalid expiry date format. Use MM/YY")

                # Validate card type is selected
                if not self.cardType.get():
                    raise ValueError("Please select card type")

            elif self.paymentMethod.get() == "debit":
                # Validate debit card fields
                card_number = self.debitCardNumber.get().strip()
                if not card_number:
                    raise ValueError("Please enter debit card number")
                if not card_number.isdigit():
                    raise ValueError("Debit card number must contain only digits")
                if len(card_number) < 16:
                    raise ValueError("Debit card number must be at least 16 digits")
                if len(card_number) > 20:
                    raise ValueError("Debit card number cannot exceed 20 digits")

                # Validate bank name
                if not self.bankName.get().strip():
                    raise ValueError("Please enter bank name")

            return True

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False

    def processPayment(self):
        """Process the payment with balance top-up for excess amounts"""
        if not self.validateFields():
            return

        try:
            amount = float(self.amount.get())
            with Session(self.engine) as session:
                order = session.merge(self.order)
                remaining_balance = order.calcRemainingBalance()

                # Calculate payment allocation
                total_needed = remaining_balance
                if total_needed <= 0:
                    messagebox.showerror("Error", "Order is already fully paid")
                    return

                # Calculate how much of the payment goes to the order vs excess
                payment_amount = min(amount, total_needed)
                excess_amount = max(0, amount - total_needed)

                # Create payment based on method
                if self.paymentMethod.get() == "balance":
                    # Validate sufficient balance
                    if order.customer.custBalance < payment_amount:
                        messagebox.showerror("Error", "Insufficient balance")
                        return

                    # Deduct payment from customer balance
                    order.customer.custBalance -= payment_amount
                    payment = Payment(
                        paymentAmount=payment_amount,
                        paymentDate=datetime.now()
                    )

                elif self.paymentMethod.get() == "credit":
                    payment = CreditCardPayment(
                        paymentAmount=payment_amount,
                        paymentDate=datetime.now(),
                        cardNumber=self.creditCardNumber.get().strip(),
                        cardExpiryDate=datetime.strptime(self.expiryDate.get().strip(), "%m/%y"),
                        cardType=self.cardType.get()
                    )

                    # Add excess to balance for credit card payment
                    if excess_amount > 0:
                        order.customer.custBalance += excess_amount

                else:  # debit card
                    payment = DebitCardPayment(
                        paymentAmount=payment_amount,
                        paymentDate=datetime.now(),
                        debitCardNumber=self.debitCardNumber.get().strip(),
                        bankName=self.bankName.get().strip()
                    )

                    # Add excess to balance for debit card payment
                    if excess_amount > 0:
                        order.customer.custBalance += excess_amount

                # Add payment to order
                payment.order = order
                session.add(payment)

                # Update order status based on remaining balance after payment
                new_remaining = order.calcRemainingBalance() - payment_amount
                if new_remaining <= 0:
                    order.orderStatus = OrderStatus.SUBMITTED.value
                else:
                    # Keep as PENDING for partial payments
                    order.orderStatus = OrderStatus.PENDING.value

                # Commit all changes
                session.commit()

                # Prepare success message
                message = f"Payment processed successfully:\n\n"
                message += f"Order payment: ${payment_amount:.2f}\n"
                if excess_amount > 0:
                    message += f"Added to balance: ${excess_amount:.2f}\n"
                message += f"Order status: {order.orderStatus}\n"
                if excess_amount > 0:
                    message += f"\nNew balance: ${order.customer.custBalance:.2f}"
                if new_remaining > 0:
                    message += f"\nRemaining to pay: ${new_remaining:.2f}"

                messagebox.showinfo("Success", message)
                self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
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

        # Buttons frame
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(fill=tk.X, padx=5, pady=5)

        # Add both View Details and Refresh buttons
        ttk.Button(buttonFrame,
                   text="View Details",
                   command=self.viewOrderDetails).pack(side=tk.LEFT, padx=5)

        ttk.Button(buttonFrame,
                   text="Refresh",
                   command=self.loadOrders).pack(side=tk.LEFT, padx=5)

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
                    OrderStatus.READY_TO_PICKUP.value,
                    OrderStatus.CANCELLED.value,
                    OrderStatus.DELIVERED.value,
                    OrderStatus.COMPLETED.value
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
        detailsWindow.geometry("800x600")

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
        self.profileFrame = ttk.LabelFrame(self, text="My Profile")
        self.profileFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create labels with instance variables so we can update them
        self.nameLabel = ttk.Label(self.profileFrame)
        self.nameLabel.pack(pady=2)

        self.usernameLabel = ttk.Label(self.profileFrame)
        self.usernameLabel.pack(pady=2)

        self.addressLabel = ttk.Label(self.profileFrame)
        self.addressLabel.pack(pady=2)

        self.balanceLabel = ttk.Label(self.profileFrame)
        self.balanceLabel.pack(pady=2)

        self.maxOwingLabel = ttk.Label(self.profileFrame)
        self.maxOwingLabel.pack(pady=2)

        # For corporate customers
        if customer.type == "Corporate Customer":
            self.discountLabel = ttk.Label(self.profileFrame)
            self.discountLabel.pack(pady=2)

            self.creditLimitLabel = ttk.Label(self.profileFrame)
            self.creditLimitLabel.pack(pady=2)

            self.minBalanceLabel = ttk.Label(self.profileFrame)
            self.minBalanceLabel.pack(pady=2)

        # Add refresh button
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(buttonFrame,
                   text="Refresh",
                   command=self.refreshProfile,
                   width=20).pack(pady=5)

        # Load initial data
        self.refreshProfile()

    def refreshProfile(self):
        """Refresh profile information"""
        try:
            with Session(self.engine) as session:
                customer = session.query(Customer).get(self.customer.id)

                # Update the display
                self.nameLabel.config(text=f"Name: {customer.firstName} {customer.lastName}")
                self.usernameLabel.config(text=f"Username: {customer.username}")
                self.addressLabel.config(text=f"Address: {customer.custAddress}")

                # Set balance label color based on amount
                balance_color = 'green' if customer.custBalance > 0 else 'red' if customer.custBalance < 0 else 'black'
                self.balanceLabel.config(
                    text=f"Current Balance: ${customer.custBalance:.2f}",
                    foreground=balance_color
                )

                # Hide maxOwing for corporate customers
                if customer.type != "Corporate Customer":
                    self.maxOwingLabel.config(text=f"Maximum Owing: ${customer.maxOwing:.2f}")
                    self.maxOwingLabel.pack(pady=2)
                else:
                    self.maxOwingLabel.pack_forget()
                    # Show corporate specific information
                    self.discountLabel.config(text=f"Discount Rate: {customer.discountRate * 100}%")
                    self.creditLimitLabel.config(text=f"Credit Limit: ${customer.maxCredit:.2f}")
                    self.minBalanceLabel.config(text=f"Minimum Balance: ${customer.minBalance:.2f}")

                self.customer = customer

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh profile: {str(e)}")