import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from models import Order, Customer, Item, OrderLine
from models.Order import OrderStatus, DeliveryMethod
from .order_status_dialog import OrderStatusDialog


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

            columns = ('Item', 'Quantity', 'Price', 'Total')
            itemTree = ttk.Treeview(itemsFrame, columns=columns, show='headings')

            for col in columns:
                itemTree.heading(col, text=col)

            for line in order.orderLines:
                itemTree.insert('', 'end', values=(
                    line.getItemDetails(),
                    line.itemNumber,
                    f"${line.item.pricePerUnit if hasattr(line.item, 'pricePerUnit') else ''}",
                    f"${line.lineTotal:.2f}"
                ))

            itemTree.pack(fill=tk.BOTH, expand=True)

            # Payment History
            self.addPaymentHistory(detailsWindow, order)

            # Totals
            totalsFrame = ttk.Frame(detailsWindow)
            totalsFrame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(totalsFrame, text=f"Subtotal: ${order.subtotal:.2f}").pack()
            if order.discount > 0:
                ttk.Label(totalsFrame, text=f"Discount: ${order.discount:.2f}").pack()
            if order.deliveryFee > 0:
                ttk.Label(totalsFrame, text=f"Delivery Fee: ${order.deliveryFee:.2f}").pack()
            ttk.Label(totalsFrame, text=f"Total: ${order.total:.2f}", font=('Helvetica', 10, 'bold')).pack()

            if order.calcRemainingBalance() > 0:
                ttk.Label(totalsFrame, text=f"Remaining Balance: ${order.calcRemainingBalance():.2f}",
                          foreground='red').pack()

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
                    order.orderStatus = dialog.result.value
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
