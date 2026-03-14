import tkinter as tk
from tkinter import ttk, messagebox
from functions import get_products, deduct_inventory, create_sale, check_inventory_availability


class POSWindow:
    def __init__(self, parent, user_id):
        self.win = tk.Toplevel(parent)
        self.win.title("Point of Sale - New Transaction")
        self.win.geometry("900x600")
        self.user_id = user_id
        self.parent = parent
        
        # Cart data
        self.cart_items = []  # List of dicts: {id, name, price, quantity}
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.win, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Products
        left_frame = ttk.LabelFrame(main_frame, text="Products", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Product treeview
        columns = ("ID", "Product", "Price")
        self.product_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Product", text="Product Name")
        self.product_tree.heading("Price", text="Price")
        
        self.product_tree.column("ID", width=50)
        self.product_tree.column("Product", width=200)
        self.product_tree.column("Price", width=100)
        
        # Scrollbar for products
        product_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=product_scroll.set)
        
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Quantity frame
        qty_frame = ttk.Frame(left_frame)
        qty_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(qty_frame, text="Quantity:").pack(side=tk.LEFT)
        self.qty_var = tk.IntVar(value=1)
        ttk.Spinbox(qty_frame, from_=1, to=99, textvariable=self.qty_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(qty_frame, text="Add to Cart", command=self.add_to_cart).pack(side=tk.LEFT, padx=10)
        
        # Right panel - Cart
        right_frame = ttk.LabelFrame(main_frame, text="Shopping Cart", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Cart treeview
        cart_columns = ("Product", "Price", "Quantity", "Subtotal")
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_columns, show="headings", height=15)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        
        # Scrollbar for cart
        cart_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cart total
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(total_frame, text="Total:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="$0.00", font=("Arial", 14, "bold"), foreground="green")
        self.total_label.pack(side=tk.RIGHT)
        
        # Cart buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Remove Item", command=self.remove_from_cart).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Cart", command=self.clear_cart).pack(side=tk.LEFT, padx=5)
        
        # Checkout button
        ttk.Button(right_frame, text="Checkout", command=self.checkout).pack(fill=tk.X, pady=10)
        
        # Back button
        ttk.Button(right_frame, text="Close", command=self.win.destroy).pack(fill=tk.X)
    
    def load_products(self):
        """Load products into treeview"""
        products = get_products()
        for product in products:
            self.product_tree.insert("", tk.END, values=product, iid=str(product[0]))
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selected = self.product_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product")
            return
        
        product_id = int(selected)
        product_data = self.product_tree.item(selected)['values']
        product_name = product_data[1]
        product_price = float(product_data[2])
        quantity = self.qty_var.get()
        
        # Check inventory availability
        try:
            available, message = check_inventory_availability(product_id, quantity)
            if not available:
                messagebox.showerror("Insufficient Inventory", message)
                return
        except Exception as e:
            # If check fails, proceed with caution
            print(f"Inventory check warning: {e}")
        
        # Check if product already in cart
        for item in self.cart_items:
            if item['id'] == product_id:
                item['quantity'] += quantity
                self.update_cart_display()
                return
        
        # Add new item
        self.cart_items.append({
            'id': product_id,
            'name': product_name,
            'price': product_price,
            'quantity': quantity
        })
        
        self.update_cart_display()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selected = self.cart_tree.focus()
        if not selected:
            return
        
        # Get the item index from the cart
        item_index = int(self.cart_tree.index(selected))
        del self.cart_items[item_index]
        
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items and messagebox.askyesno("Clear Cart", "Clear all items?"):
            self.cart_items = []
            self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart treeview and total"""
        # Clear cart tree
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        
        # Reinsert items
        total = 0
        for item in self.cart_items:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            self.cart_tree.insert("", tk.END, values=(
                item['name'],
                f"${item['price']:.2f}",
                item['quantity'],
                f"${subtotal:.2f}"
            ))
        
        self.total_label.config(text=f"${total:.2f}")
    
    def checkout(self):
        """Process the sale"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "No items in cart")
            return
        
        # Prepare items for sale
        sale_items = []
        for item in self.cart_items:
            sale_items.append({
                'product_id': item['id'],
                'quantity': item['quantity']
            })
        
        try:
            # Create sale and deduct inventory
            sale_id = create_sale(self.user_id, sale_items)
            
            # Show receipt
            self.show_receipt(sale_id)
            
            # Clear cart
            self.cart_items = []
            self.update_cart_display()
            
        except Exception as e:
            messagebox.showerror("Checkout Failed", str(e))
    
    def show_receipt(self, sale_id):
        """Show receipt window"""
        receipt_win = tk.Toplevel(self.win)
        receipt_win.title("Receipt")
        receipt_win.geometry("350x450")
        receipt_win.transient(self.win)
        receipt_win.grab_set()
        
        # Receipt content
        main_frame = ttk.Frame(receipt_win, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        tk.Label(main_frame, text="BEAN & BREW", 
                font=("Arial", 16, "bold"), fg="#6F4E37").pack()
        tk.Label(main_frame, text="=" * 30).pack()
        tk.Label(main_frame, text=f"Receipt #{sale_id}").pack()
        tk.Label(main_frame, text="=" * 30).pack(pady=(0, 10))
        
        # Items
        items_frame = tk.Frame(main_frame)
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        total = 0
        for item in self.cart_items:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            
            item_frame = tk.Frame(items_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(item_frame, text=item['name'], anchor='w').pack(side=tk.LEFT)
            tk.Label(item_frame, text=f"${item['price']:.2f} x {item['quantity']}", anchor='e').pack(side=tk.RIGHT)
            tk.Label(item_frame, text=f"${subtotal:.2f}", anchor='e', font=("Arial", 9, "bold")).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Total
        tk.Label(main_frame, text="-" * 30).pack(pady=10)
        total_frame = tk.Frame(main_frame)
        total_frame.pack(fill=tk.X)
        tk.Label(total_frame, text="TOTAL:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(total_frame, text=f"${total:.2f}", font=("Arial", 14, "bold"), fg="green").pack(side=tk.RIGHT)
        
        # Footer
        tk.Label(main_frame, text="=" * 30).pack(pady=10)
        tk.Label(main_frame, text="Thank you for your business!").pack()
        
        # Print button
        tk.Button(main_frame, text="Close", command=receipt_win.destroy, 
                 bg="#6F4E37", fg="white", width=15).pack(pady=10)