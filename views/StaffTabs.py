import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from models import Order, Customer, Item, OrderLine, UnitPriceVeggie, PackVeggie, WeightedVeggie, PremadeBox
from models.Order import OrderStatus, DeliveryMethod
from .OrderStatusDialog import OrderStatusDialog


class StaffOrdersTab(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

        # Create filter frame
        filterFrame = ttk.LabelFrame(self, text="Filter Orders")
        filterFrame.pack(fill=tk.X, padx=5, pady=5)

        # Status filter
        ttk.Label(filterFrame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.statusVar = tk.StringVar(value="ALL")
        statusCombo = ttk.Combobox(filterFrame, textvariable=self.statusVar,
                                   values=["ALL"] + [status.value for status in OrderStatus])
        statusCombo.pack(side=tk.LEFT, padx=5)

        # Refresh button
        ttk.Button(filterFrame, text="Refresh", command=self.loadOrders).pack(side=tk.LEFT, padx=5)

        # Create orders treeview
        columns = ('Order No', 'Date', 'Customer', 'Status', 'Total', 'Delivery')
        self.orderTree = ttk.Treeview(self, columns=columns, show='headings')

        # Setup column headings
        for col in columns:
            self.orderTree.heading(col, text=col)
            self.orderTree.column(col, width=100)

        self.orderTree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.orderTree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orderTree.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(buttonFrame, text="View Details",
                   command=self.viewOrderDetails).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttonFrame, text="Update Status",
                   command=self.updateOrderStatus).pack(side=tk.LEFT, padx=5)

        # Load initial data
        self.loadOrders()

    def loadOrders(self):
        """Load orders into treeview"""
        for item in self.orderTree.get_children():
            self.orderTree.delete(item)

        with Session(self.engine) as session:
            query = session.query(Order).join(Customer)

            if self.statusVar.get() != "ALL":
                query = query.filter(Order.orderStatus == self.statusVar.get())

            orders = query.all()

            for order in orders:
                self.orderTree.insert('', 'end', values=(
                    order.orderNumber,
                    order.orderDate.strftime('%Y-%m-%d'),
                    f"{order.customer.firstName} {order.customer.lastName}",
                    order.orderStatus,
                    f"${order.total:.2f}",
                    "Yes" if order.deliveryMethod == DeliveryMethod.DELIVERY else "No"
                ))

    def viewOrderDetails(self):
        """Show order details in a new window"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to view")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]

        detailsWindow = tk.Toplevel(self)
        detailsWindow.title(f"Order Details - {orderNum}")
        detailsWindow.geometry("600x600")

        with Session(self.engine) as session:
            order = session.query(Order).filter_by(orderNumber=orderNum).first()

            # Order info
            infoFrame = ttk.LabelFrame(detailsWindow, text="Order Information")
            infoFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(infoFrame, text=f"Order Number: {order.orderNumber}").pack()
            ttk.Label(infoFrame, text=f"Date: {order.orderDate}").pack()
            ttk.Label(infoFrame, text=f"Customer: {order.customer.firstName} {order.customer.lastName}").pack()
            ttk.Label(infoFrame, text=f"Status: {order.orderStatus}").pack()

            if order.deliveryMethod == DeliveryMethod.DELIVERY:
                ttk.Label(infoFrame, text=f"Delivery Address: {order.deliveryAddress}").pack()
                ttk.Label(infoFrame, text=f"Delivery Distance: {order.deliveryDistance}km").pack()
                ttk.Label(infoFrame, text=f"Delivery Fee: ${order.deliveryFee:.2f}").pack()

            # Order items
            itemsFrame = ttk.LabelFrame(detailsWindow, text="Order Items")
            itemsFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            columns = ('Item', 'Quantity', 'Unit Price', 'Total')  # Changed 'Price' to 'Unit Price' for clarity
            itemTree = ttk.Treeview(itemsFrame, columns=columns, show='headings')

            for col in columns:
                itemTree.heading(col, text=col)
                itemTree.column(col, width=100)  # Set consistent column widths

            for line in order.orderLines:
                # Get the appropriate price per unit based on item type
                if hasattr(line.item, 'pricePerUnit'):
                    unit_price = line.item.pricePerUnit
                elif hasattr(line.item, 'pricePerPack'):
                    unit_price = line.item.pricePerPack
                elif hasattr(line.item, 'pricePerKilo'):
                    unit_price = line.item.pricePerKilo
                else:
                    unit_price = line.lineTotal / line.itemNumber if line.itemNumber else 0

                itemTree.insert('', 'end', values=(
                    line.getItemDetails(),
                    line.itemNumber,
                    f"${unit_price:.2f}",
                    f"${line.lineTotal:.2f}"
                ))

            itemTree.pack(fill=tk.BOTH, expand=True)

            # Payment History
            self.addPaymentHistory(detailsWindow, order)

            # Totals frame with proper formatting
            totalsFrame = ttk.LabelFrame(detailsWindow, text="Order Totals")
            totalsFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(totalsFrame, text=f"Subtotal: ${order.subtotal:.2f}").pack(anchor='e')
            if order.discount > 0:
                ttk.Label(totalsFrame, text=f"Discount: -${order.discount:.2f}").pack(anchor='e')
            if order.deliveryFee > 0:
                ttk.Label(totalsFrame, text=f"Delivery Fee: ${order.deliveryFee:.2f}").pack(anchor='e')
            ttk.Label(totalsFrame, text=f"Total: ${order.total:.2f}",
                      font=('Helvetica', 10, 'bold')).pack(anchor='e')

            if order.calcRemainingBalance() > 0:
                ttk.Label(totalsFrame, text=f"Remaining Balance: ${order.calcRemainingBalance():.2f}",
                          foreground='red').pack(anchor='e')

    def addPaymentHistory(self, window, order):
        """Add payment history section to order details"""
        paymentFrame = ttk.LabelFrame(window, text="Payment History")
        paymentFrame.pack(fill=tk.X, padx=10, pady=5)

        columns = ('Date', 'Amount', 'Type')
        paymentTree = ttk.Treeview(paymentFrame, columns=columns, show='headings', height=3)

        for col in columns:
            paymentTree.heading(col, text=col)

        for payment in order.payments:
            paymentTree.insert('', 'end', values=(
                payment.paymentDate.strftime('%Y-%m-%d'),
                f"${payment.paymentAmount:.2f}",
                payment.type
            ))

        paymentTree.pack(fill=tk.X)

    def updateOrderStatus(self):
        """Update order status"""
        selected = self.orderTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to update")
            return

        orderNum = self.orderTree.item(selected[0])['values'][0]

        dialog = OrderStatusDialog(self)
        if dialog.result:
            try:
                with Session(self.engine) as session:
                    order = session.query(Order).filter_by(orderNumber=orderNum).first()
                    new_status = dialog.result.value
                    current_status = order.orderStatus

                    # Check pending order first
                    if current_status == OrderStatus.PENDING.value:
                        messagebox.showerror("Error", "You need to wait for the customer to pay this order")
                        return

                    # Check if trying to mark a pickup order as delivered
                    if (order.deliveryMethod == DeliveryMethod.PICKUP and
                            new_status == OrderStatus.DELIVERED.value):
                        messagebox.showerror("Error", "Pick Up Order cannot be delivered")
                        return

                    # Check if delivery order is being marked as ready to pickup
                    if (order.deliveryMethod == DeliveryMethod.DELIVERY and
                            new_status == OrderStatus.READY_TO_PICKUP.value):
                        messagebox.showerror("Error", "Only Pick Up Order can be Ready To Pick Up")
                        return

                    # Check transitions to completed status
                    if (new_status == OrderStatus.COMPLETED.value and
                            current_status not in [OrderStatus.READY_TO_PICKUP.value, OrderStatus.DELIVERED.value]):
                        messagebox.showerror("Error",
                                             "Order must be Ready To Pick Up or Delivered before marking as Completed")
                        return

                    # Status transition validations
                    if current_status == OrderStatus.SUBMITTED.value:
                        if new_status == OrderStatus.PENDING.value:
                            messagebox.showerror("Error", "Submitted order cannot be changed to Pending")
                            return

                    elif current_status == OrderStatus.PROCESSING.value:
                        if new_status in [OrderStatus.SUBMITTED.value, OrderStatus.PENDING.value]:
                            messagebox.showerror("Error", "Processing order cannot be changed to Submitted or Pending")
                            return

                    elif current_status == OrderStatus.READY_TO_PICKUP.value:
                        if new_status != OrderStatus.COMPLETED.value:
                            messagebox.showerror("Error", "Ready To Pick Up order can only be changed to Completed")
                            return

                    elif current_status == OrderStatus.DELIVERED.value:
                        if new_status != OrderStatus.COMPLETED.value:
                            messagebox.showerror("Error", "Delivered order can only be changed to Completed")
                            return

                    elif current_status == OrderStatus.COMPLETED.value:
                        messagebox.showerror("Error", "Completed order status cannot be changed")
                        return

                    elif current_status == OrderStatus.CANCELLED.value:
                        messagebox.showerror("Error", "Cancelled order status cannot be changed")
                        return

                    order.orderStatus = new_status
                    session.commit()
                    self.loadOrders()
                    messagebox.showinfo("Success", "Order status updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update order status: {str(e)}")


class StaffCustomersTab(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

        # Filter frame
        filterFrame = ttk.LabelFrame(self, text="Filter Customers")
        filterFrame.pack(fill=tk.X, padx=5, pady=5)

        # Customer type filter
        ttk.Label(filterFrame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.typeVar = tk.StringVar(value="ALL")
        typeCombo = ttk.Combobox(filterFrame, textvariable=self.typeVar,
                                 values=["ALL", "Private", "Corporate"])
        typeCombo.pack(side=tk.LEFT, padx=5)

        ttk.Button(filterFrame, text="Apply Filter",
                   command=self.loadCustomers).pack(side=tk.LEFT, padx=5)

        # Customers treeview
        columns = ('Name', 'Type', 'Address', 'Balance', 'Orders')
        self.customerTree = ttk.Treeview(self, columns=columns, show='headings')

        for col in columns:
            self.customerTree.heading(col, text=col)

        self.customerTree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.customerTree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customerTree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        ttk.Button(self, text="View Details",
                   command=self.viewCustomerDetails).pack(pady=5)

        # Load initial data
        self.loadCustomers()

    def loadCustomers(self):
        """Load customers into treeview"""
        for item in self.customerTree.get_children():
            self.customerTree.delete(item)

        with Session(self.engine) as session:
            query = session.query(Customer)

            if self.typeVar.get() == "Private":
                query = query.filter(Customer.type == "customer")
            elif self.typeVar.get() == "Corporate":
                query = query.filter(Customer.type == "Corporate Customer")

            customers = query.all()

            for customer in customers:
                self.customerTree.insert('', 'end', values=(
                    f"{customer.firstName} {customer.lastName}",
                    "Corporate" if customer.type == "Corporate Customer" else "Private",
                    customer.custAddress,
                    f"${customer.custBalance:.2f}",
                    len(customer.orders)
                ))

    def viewCustomerDetails(self):
        """Show customer details and order history"""
        selected = self.customerTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to view")
            return

        customer_name = self.customerTree.item(selected[0])['values'][0]

        detailsWindow = tk.Toplevel(self)
        detailsWindow.title(f"Customer Details - {customer_name}")
        detailsWindow.geometry("800x600")

        with Session(self.engine) as session:
            # Get first name and last name from the full name
            first_name, last_name = customer_name.split(" ", 1)
            customer = session.query(Customer).filter_by(
                firstName=first_name, lastName=last_name).first()

            # Customer info
            infoFrame = ttk.LabelFrame(detailsWindow, text="Customer Information")
            infoFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(infoFrame, text=f"Name: {customer.firstName} {customer.lastName}").pack()
            ttk.Label(infoFrame, text=f"Address: {customer.custAddress}").pack()
            ttk.Label(infoFrame, text=f"Balance: ${customer.custBalance:.2f}").pack()

            if customer.type == "Corporate Customer":
                ttk.Label(infoFrame, text=f"Discount Rate: {customer.discountRate * 100}%").pack()
                ttk.Label(infoFrame, text=f"Credit Limit: ${customer.maxCredit:.2f}").pack()
                ttk.Label(infoFrame, text=f"Minimum Balance: ${customer.minBalance:.2f}").pack()

            # Order history
            historyFrame = ttk.LabelFrame(detailsWindow, text="Order History")
            historyFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            columns = ('Order No', 'Date', 'Status', 'Total')
            historyTree = ttk.Treeview(historyFrame, columns=columns, show='headings')

            for col in columns:
                historyTree.heading(col, text=col)

            for order in customer.orders:
                historyTree.insert('', 'end', values=(
                    order.orderNumber,
                    order.orderDate.strftime('%Y-%m-%d'),
                    order.orderStatus,
                    f"${order.total:.2f}"
                ))

            historyTree.pack(fill=tk.BOTH, expand=True)


class StaffReportsTab(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

        # Reports selection
        reportsFrame = ttk.LabelFrame(self, text="Generate Reports")
        reportsFrame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sales reports
        ttk.Label(reportsFrame, text="Sales Reports", font=('Helvetica', 10, 'bold')).pack(pady=5)

        ttk.Button(reportsFrame, text="Weekly Sales Report",
                   command=lambda: self.generateSalesReport('week')).pack(pady=2)
        ttk.Button(reportsFrame, text="Monthly Sales Report",
                   command=lambda: self.generateSalesReport('month')).pack(pady=2)
        ttk.Button(reportsFrame, text="Yearly Sales Report",
                   command=lambda: self.generateSalesReport('year')).pack(pady=2)

        # Customer reports
        ttk.Label(reportsFrame, text="Customer Reports", font=('Helvetica', 10, 'bold')).pack(pady=5)

        ttk.Button(reportsFrame, text="Private Customers List",
                   command=self.generatePrivateCustomersList).pack(pady=2)
        ttk.Button(reportsFrame, text="Corporate Customers List",
                   command=self.generateCorporateCustomersList).pack(pady=2)

        # Product reports
        ttk.Label(reportsFrame, text="Product Reports", font=('Helvetica', 10, 'bold')).pack(pady=5)

        ttk.Button(reportsFrame, text="Popular Items Report",
                   command=self.generatePopularItemsReport).pack(pady=2)
        ttk.Button(reportsFrame, text="Unpopular Items Report",
                   command=self.generateUnpopularItemsReport).pack(pady=2)

    def generateSalesReport(self, period):
        """Generate sales report for specified period"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title(f"{period.capitalize()} Sales Report")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            now = datetime.now()

            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'month':
                start_date = now - timedelta(days=30)
            else:  # year
                start_date = now - timedelta(days=365)

            orders = session.query(Order).filter(
                Order.orderDate >= start_date,
                Order.orderStatus != OrderStatus.CANCELLED
            ).all()

            # Create report content
            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, f"{period.capitalize()} Sales Report\n", 'title')
            reportText.insert(tk.END, f"Period: {start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}\n\n")

            total_sales = sum(order.total for order in orders)
            total_orders = len(orders)

            reportText.insert(tk.END, f"Total Sales: ${total_sales:.2f}\n")
            reportText.insert(tk.END, f"Total Orders: {total_orders}\n")
            reportText.insert(tk.END,
                              f"Average Order Value: ${(total_sales / total_orders if total_orders else 0):.2f}\n\n")

            # Make text readonly
            reportText.configure(state='disabled')

            # Add export button
            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)

    def generateSalesReport(self, period):
        """Generate sales report for specified period"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title(f"{period.capitalize()} Sales Report")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            now = datetime.now()

            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'month':
                start_date = now - timedelta(days=30)
            else:  # year
                start_date = now - timedelta(days=365)

            orders = session.query(Order).filter(
                Order.orderDate >= start_date,
                Order.orderStatus != OrderStatus.CANCELLED
            ).all()

            # Create report content
            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, f"{period.capitalize()} Sales Report\n", 'title')
            reportText.insert(tk.END, f"Period: {start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}\n\n")

            total_sales = sum(order.total for order in orders)
            total_orders = len(orders)

            reportText.insert(tk.END, f"Total Sales: ${total_sales:.2f}\n")
            reportText.insert(tk.END, f"Total Orders: {total_orders}\n")
            reportText.insert(tk.END,
                              f"Average Order Value: ${(total_sales / total_orders if total_orders else 0):.2f}\n\n")

            # Add delivery statistics
            delivery_orders = sum(1 for order in orders if order.deliveryMethod == DeliveryMethod.DELIVERY)
            reportText.insert(tk.END, f"Delivery Orders: {delivery_orders}\n")
            reportText.insert(tk.END, f"Pickup Orders: {total_orders - delivery_orders}\n\n")

            # Make text readonly
            reportText.configure(state='disabled')

            # Add export button
            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)

    def generatePopularItemsReport(self):
        """Generate report of popular items"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title("Popular Items Report")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            # Query to get item sales count
            query = session.query(
                Item,
                func.count(OrderLine.id).label('sales_count'),
                func.sum(OrderLine.lineTotal).label('total_sales')
            ).join(OrderLine) \
                .group_by(Item.id) \
                .order_by(desc('sales_count')) \
                .limit(10)

            items = query.all()

            # Create report content
            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, "Most Popular Items Report\n", 'title')
            reportText.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")

            reportText.insert(tk.END, "Top 10 Items by Sales Volume:\n\n")

            for i, (item, count, total) in enumerate(items, 1):
                reportText.insert(tk.END, f"{i}. Item: {item.vegName if hasattr(item, 'vegName') else 'Premade Box'}\n")
                reportText.insert(tk.END, f"   Sales Count: {count}\n")
                reportText.insert(tk.END, f"   Total Sales: ${total:.2f}\n\n")

            reportText.configure(state='disabled')

            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)

    def generateUnpopularItemsReport(self):
        """Generate report of unpopular items"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title("Unpopular Items Report")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            # Query to get items with lowest sales
            query = session.query(
                Item,
                func.count(OrderLine.id).label('sales_count'),
                func.sum(OrderLine.lineTotal).label('total_sales')
            ).outerjoin(OrderLine) \
                .group_by(Item.id) \
                .order_by('sales_count') \
                .limit(10)

            items = query.all()

            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, "Least Popular Items Report\n", 'title')
            reportText.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")

            reportText.insert(tk.END, "Bottom 10 Items by Sales Volume:\n\n")

            for i, (item, count, total) in enumerate(items, 1):
                reportText.insert(tk.END, f"{i}. Item: {item.vegName if hasattr(item, 'vegName') else 'Premade Box'}\n")
                reportText.insert(tk.END, f"   Sales Count: {count}\n")
                reportText.insert(tk.END, f"   Total Sales: ${total or 0:.2f}\n\n")

            reportText.configure(state='disabled')

            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)

    def generatePrivateCustomersList(self):
        """Generate list of private customers"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title("Private Customers List")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            customers = session.query(Customer) \
                .filter(Customer.type == "customer") \
                .order_by(Customer.lastName) \
                .all()

            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, "Private Customers Report\n", 'title')
            reportText.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            reportText.insert(tk.END, f"Total Private Customers: {len(customers)}\n\n")

            for customer in customers:
                reportText.insert(tk.END, f"Customer: {customer.firstName} {customer.lastName}\n")
                reportText.insert(tk.END, f"Address: {customer.custAddress}\n")
                reportText.insert(tk.END, f"Current Balance: ${customer.custBalance:.2f}\n")
                reportText.insert(tk.END, f"Total Orders: {len(customer.orders)}\n")
                if customer.orders:
                    last_order = max(customer.orders, key=lambda x: x.orderDate)
                    reportText.insert(tk.END,
                                      f"Last Order: {last_order.orderDate.strftime('%Y-%m-%d')}\n")
                reportText.insert(tk.END, "\n")

            reportText.configure(state='disabled')

            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)

    def generateCorporateCustomersList(self):
        """Generate list of corporate customers"""
        reportWindow = tk.Toplevel(self)
        reportWindow.title("Corporate Customers List")
        reportWindow.geometry("800x600")

        with Session(self.engine) as session:
            customers = session.query(Customer) \
                .filter(Customer.type == "Corporate Customer") \
                .order_by(Customer.lastName) \
                .all()

            reportText = tk.Text(reportWindow, wrap=tk.WORD, padx=10, pady=10)
            reportText.pack(fill=tk.BOTH, expand=True)

            reportText.insert(tk.END, "Corporate Customers Report\n", 'title')
            reportText.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            reportText.insert(tk.END, f"Total Corporate Customers: {len(customers)}\n\n")

            for customer in customers:
                reportText.insert(tk.END, f"Customer: {customer.firstName} {customer.lastName}\n")
                reportText.insert(tk.END, f"Address: {customer.custAddress}\n")
                reportText.insert(tk.END, f"Current Balance: ${customer.custBalance:.2f}\n")
                reportText.insert(tk.END, f"Credit Limit: ${customer.maxCredit:.2f}\n")
                reportText.insert(tk.END, f"Minimum Balance: ${customer.minBalance:.2f}\n")
                reportText.insert(tk.END, f"Discount Rate: {customer.discountRate * 100}%\n")
                reportText.insert(tk.END, f"Total Orders: {len(customer.orders)}\n")
                if customer.orders:
                    last_order = max(customer.orders, key=lambda x: x.orderDate)
                    reportText.insert(tk.END,
                                      f"Last Order: {last_order.orderDate.strftime('%Y-%m-%d')}\n")
                reportText.insert(tk.END, "\n")

            reportText.configure(state='disabled')

            ttk.Button(reportWindow, text="Export Report",
                       command=lambda: self.exportReport(reportText.get('1.0', tk.END))).pack(pady=5)


class StaffInventoryTab(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

        # Create filter frame
        filterFrame = ttk.LabelFrame(self, text="Filter Items")
        filterFrame.pack(fill=tk.X, padx=5, pady=5)

        # Item type filter
        ttk.Label(filterFrame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.typeVar = tk.StringVar(value="ALL")
        typeCombo = ttk.Combobox(filterFrame, textvariable=self.typeVar,
                                 values=["ALL", "Unit Price Veggies", "Pack Veggies",
                                         "Weighted Veggies", "Premade Boxes"])
        typeCombo.pack(side=tk.LEFT, padx=5)

        ttk.Button(filterFrame, text="Apply Filter",
                   command=self.loadItems).pack(side=tk.LEFT, padx=5)

        # Create items treeview
        columns = ('Name', 'Type', 'Price', 'Stock Info')
        self.itemTree = ttk.Treeview(self, columns=columns, show='headings')

        for col in columns:
            self.itemTree.heading(col, text=col)
            if col == 'Stock Info':
                self.itemTree.column(col, width=200)
            else:
                self.itemTree.column(col, width=100)

        self.itemTree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.itemTree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.itemTree.configure(yscrollcommand=scrollbar.set)

        # Add view details button
        ttk.Button(self, text="View Details",
                   command=self.viewItemDetails).pack(pady=5)

        # Load initial data
        self.loadItems()

    def loadItems(self):
        """Load items into treeview"""
        from models import UnitPriceVeggie, PackVeggie, WeightedVeggie, PremadeBox, Item

        for item in self.itemTree.get_children():
            self.itemTree.delete(item)

        with Session(self.engine) as session:
            items = []

            if self.typeVar.get() == "Unit Price Veggies":
                items = session.query(UnitPriceVeggie).all()
            elif self.typeVar.get() == "Pack Veggies":
                items = session.query(PackVeggie).all()
            elif self.typeVar.get() == "Weighted Veggies":
                items = session.query(WeightedVeggie).all()
            elif self.typeVar.get() == "Premade Boxes":
                items = session.query(PremadeBox).all()
            else:  # ALL
                # Query each type separately and combine results
                unit_price = session.query(UnitPriceVeggie).all()
                pack_veggies = session.query(PackVeggie).all()
                weighted_veggies = session.query(WeightedVeggie).all()
                premade_boxes = session.query(PremadeBox).all()
                items = unit_price + pack_veggies + weighted_veggies + premade_boxes

            for item in items:
                if isinstance(item, UnitPriceVeggie):
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Unit Price',
                        f"${item.pricePerUnit:.2f}/unit",
                        f"Quantity: {item.quantity}"
                    ))
                elif isinstance(item, PackVeggie):
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Pack',
                        f"${item.pricePerPack:.2f}/pack",
                        f"Packs available: {item.numberOfPacks}"
                    ))
                elif isinstance(item, WeightedVeggie):
                    self.itemTree.insert('', 'end', values=(
                        item.vegName,
                        'Weighted',
                        f"${item.pricePerKilo:.2f}/kg",
                        f"Weight available: {item.weight:.2f}kg"
                    ))
                elif isinstance(item, PremadeBox):
                    self.itemTree.insert('', 'end', values=(
                        f"Box {item.boxSize}",
                        'Premade Box',
                        PremadeBox.getBoxPrice(item.boxSize),
                        f"Boxes available: {item.numbOfBoxes}"
                    ))

    def viewItemDetails(self):
        """Show detailed item information"""
        selected = self.itemTree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to view")
            return

        item_name = self.itemTree.item(selected[0])['values'][0]
        item_type = self.itemTree.item(selected[0])['values'][1]

        detailsWindow = tk.Toplevel(self)
        detailsWindow.title(f"Item Details - {item_name}")
        detailsWindow.geometry("400x300")

        with Session(self.engine) as session:
            if item_type == 'Unit Price':
                item = session.query(UnitPriceVeggie).filter_by(vegName=item_name).first()
                ttk.Label(detailsWindow, text=f"Name: {item.vegName}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Price per Unit: ${item.pricePerUnit:.2f}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Available Quantity: {item.quantity}").pack(pady=5)

            elif item_type == 'Pack':
                item = session.query(PackVeggie).filter_by(vegName=item_name).first()
                ttk.Label(detailsWindow, text=f"Name: {item.vegName}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Price per Pack: ${item.pricePerPack:.2f}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Number of Packs: {item.numberOfPacks}").pack(pady=5)

            elif item_type == 'Weighted':
                item = session.query(WeightedVeggie).filter_by(vegName=item_name).first()
                ttk.Label(detailsWindow, text=f"Name: {item.vegName}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Price per Kilo: ${item.pricePerKilo:.2f}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Available Weight: {item.weight:.2f}kg").pack(pady=5)

            elif item_type == 'Premade Box':
                box_size = item_name.split()[-1]  # Get size from "Box S/M/L"
                item = session.query(PremadeBox).filter_by(boxSize=box_size).first()
                ttk.Label(detailsWindow, text=f"Box Size: {item.boxSize}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Price: {PremadeBox.getBoxPrice(item.boxSize)}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Number of Boxes: {item.numbOfBoxes}").pack(pady=5)
                ttk.Label(detailsWindow, text=f"Max Veggies: {PremadeBox.getMaxVeggies(item.boxSize)}").pack(pady=5)

                # Show veggies in box
                if item.veggies:
                    ttk.Label(detailsWindow, text="\nVegetables Included:").pack(pady=5)
                    for veggie in item.veggies:
                        ttk.Label(detailsWindow, text=f"- {veggie.vegName}").pack(pady=2)