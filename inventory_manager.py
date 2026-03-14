import tkinter as tk
from tkinter import ttk, messagebox
from database import connect
from functions import (
    get_inventory, add_inventory, update_inventory, delete_inventory,
    get_low_inventory, get_inventory_transactions,
    get_categories, add_category,
    get_menu_items, add_menu_item, update_menu_item, delete_menu_item,
    get_recipe_for_menu_item
)

class InventoryManagerWindow:
    def __init__(self, parent, user):
        self.win = tk.Toplevel(parent)
        self.win.title("Inventory Management System")
        self.win.geometry("1200x700")
        self.user = user  # User dict with id, role, username
        
        # Set permissions based on role
        self.can_edit = user['role'] in ['admin', 'inventory_manager']
        self.can_add = user['role'] in ['admin', 'inventory_manager']
        self.can_delete = user['role'] == 'admin'
        self.can_view_transactions = user['role'] in ['admin', 'inventory_manager']
        self.can_manage_menu = user['role'] == 'admin'  # Only admins can manage menu items
        
        self.create_widgets()
        self.load_categories()
        self.load_inventory()
        self.check_low_inventory()
    
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Inventory Management
        self.inventory_frame = ttk.Frame(notebook)
        notebook.add(self.inventory_frame, text="Inventory Items")
        self.create_inventory_tab()
        
        # Tab 2: Menu Items (Admin only)
        if self.can_manage_menu:
            self.menu_frame = ttk.Frame(notebook)
            notebook.add(self.menu_frame, text="Menu Items")
            self.create_menu_tab()
        
        # Tab 3: Transactions (if permission)
        if self.can_view_transactions:
            self.transactions_frame = ttk.Frame(notebook)
            notebook.add(self.transactions_frame, text="Transaction History")
            self.create_transactions_tab()
        
        # Tab 4: Categories (admin only)
        if self.user['role'] == 'admin':
            self.categories_frame = ttk.Frame(notebook)
            notebook.add(self.categories_frame, text="Manage Categories")
            self.create_categories_tab()
    
    def create_inventory_tab(self):
        # Main container
        main_frame = ttk.Frame(self.inventory_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Inventory list with search
        left_frame = ttk.LabelFrame(main_frame, text="Inventory Items", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_inventory())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Refresh", command=self.load_inventory).pack(side=tk.RIGHT)
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Category", "Brand", "Unit", "Quantity", "Min Threshold", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Set column headings and widths
        column_widths = [50, 200, 120, 150, 60, 100, 100, 100]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar for low inventory count
        self.status_label = ttk.Label(left_frame, text="", foreground="red")
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Right panel - Edit form
        right_frame = ttk.LabelFrame(main_frame, text="Item Details", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(right_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields in scrollable frame
        row = 0
        
        # New Item button at the top
        if self.can_add:
            new_item_btn = ttk.Button(scrollable_frame, text="➕ New Item", command=self.prepare_new_item)
            new_item_btn.grid(row=row, column=0, columnspan=2, pady=(0, 10), sticky=tk.E)
            row += 1
        
        # Item Name
        ttk.Label(scrollable_frame, text="Item Name:*", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(scrollable_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Category
        ttk.Label(scrollable_frame, text="Category:*", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(scrollable_frame, textvariable=self.category_var, width=27)
        self.category_combo.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Brand
        ttk.Label(scrollable_frame, text="Brand:", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.brand_var = tk.StringVar()
        brand_entry = ttk.Entry(scrollable_frame, textvariable=self.brand_var, width=30)
        brand_entry.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Unit
        ttk.Label(scrollable_frame, text="Unit:*", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(scrollable_frame, textvariable=self.unit_var, 
                                  values=["g", "ml", "pcs", "kg", "L", "pack", "bottle", "bag"], width=27)
        unit_combo.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Current Quantity
        ttk.Label(scrollable_frame, text="Current Quantity:*", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.qty_var = tk.StringVar()
        qty_entry = ttk.Entry(scrollable_frame, textvariable=self.qty_var, width=30)
        qty_entry.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Min Threshold
        ttk.Label(scrollable_frame, text="Min Threshold:", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.threshold_var = tk.StringVar(value="0")
        threshold_entry = ttk.Entry(scrollable_frame, textvariable=self.threshold_var, width=30)
        threshold_entry.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Notes
        ttk.Label(scrollable_frame, text="Notes:", font=("Arial", 10)).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(scrollable_frame, textvariable=self.notes_var, width=30)
        notes_entry.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        row += 1
        
        # Required fields hint
        ttk.Label(scrollable_frame, text="* Required fields", font=("Arial", 8, "italic"), 
                  foreground="gray").grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Buttons frame
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        button_count = 0
        if self.can_add:
            ttk.Button(button_frame, text="➕ Add New Item", command=self.add_item, 
                      width=15).grid(row=0, column=button_count, padx=5)
            button_count += 1
        
        if self.can_edit:
            ttk.Button(button_frame, text="✏️ Update Qty", command=self.update_item, 
                      width=15).grid(row=0, column=button_count, padx=5)
            button_count += 1
            ttk.Button(button_frame, text="📦 Add Stock", command=self.add_stock, 
                      width=15).grid(row=0, column=button_count, padx=5)
            button_count += 1
        
        if self.can_delete:
            ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_item, 
                      width=15).grid(row=0, column=button_count, padx=5)
            button_count += 1
        
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_fields, 
                  width=15).grid(row=0, column=button_count, padx=5)
        
        # Configure column weights
        scrollable_frame.grid_columnconfigure(0, weight=0)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        
        # Set initial state of fields
        if self.can_add or self.can_edit:
            name_entry.config(state='normal')
            self.category_combo.config(state='normal')
            brand_entry.config(state='normal')
            unit_combo.config(state='normal')
            qty_entry.config(state='normal')
            threshold_entry.config(state='normal')
            notes_entry.config(state='normal')
        else:
            name_entry.config(state='readonly')
            self.category_combo.config(state='readonly')
            brand_entry.config(state='readonly')
            unit_combo.config(state='readonly')
            qty_entry.config(state='readonly')
            threshold_entry.config(state='readonly')
            notes_entry.config(state='normal')
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # Double-click to view details
        self.tree.bind("<Double-1>", self.show_item_details)
    
    def create_menu_tab(self):
        """Create menu items management tab"""
        # Main container
        main_frame = ttk.Frame(self.menu_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Menu items list
        left_frame = ttk.LabelFrame(main_frame, text="Menu Items", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.menu_search_var = tk.StringVar()
        self.menu_search_var.trace('w', lambda *args: self.filter_menu_items())
        ttk.Entry(search_frame, textvariable=self.menu_search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Refresh", command=self.load_menu_items).pack(side=tk.RIGHT)
        
        # Treeview for menu items
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Price", "Status")
        self.menu_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.menu_tree.heading("ID", text="ID")
        self.menu_tree.heading("Name", text="Menu Item")
        self.menu_tree.heading("Price", text="Price")
        self.menu_tree.heading("Status", text="Status")
        
        self.menu_tree.column("ID", width=50)
        self.menu_tree.column("Name", width=200)
        self.menu_tree.column("Price", width=100)
        self.menu_tree.column("Status", width=100)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.menu_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.menu_tree.xview)
        self.menu_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.menu_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Right panel - Menu item details and recipe
        right_frame = ttk.LabelFrame(main_frame, text="Menu Item Details", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create notebook for tabs within menu section
        menu_notebook = ttk.Notebook(right_frame)
        menu_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Basic Info
        info_frame = ttk.Frame(menu_notebook)
        menu_notebook.add(info_frame, text="Basic Info")
        
        # Form fields in info frame
        current_row = 0
        
        ttk.Label(info_frame, text="Menu Item Name:*", font=("Arial", 10)).grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.menu_name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.menu_name_var, width=30).grid(row=current_row, column=1, pady=5, padx=5, sticky=tk.W)
        current_row += 1
        
        ttk.Label(info_frame, text="Price:*", font=("Arial", 10)).grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.menu_price_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.menu_price_var, width=30).grid(row=current_row, column=1, pady=5, padx=5, sticky=tk.W)
        current_row += 1
        
        ttk.Label(info_frame, text="Status:", font=("Arial", 10)).grid(row=current_row, column=0, sticky=tk.W, pady=5)
        self.menu_status_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(info_frame, text="Active", variable=self.menu_status_var).grid(row=current_row, column=1, sticky=tk.W, pady=5)
        current_row += 1
        
        # Tab 2: Recipe Ingredients
        recipe_frame = ttk.Frame(menu_notebook)
        menu_notebook.add(recipe_frame, text="Recipe")
        
        # Available ingredients list
        ing_frame = ttk.LabelFrame(recipe_frame, text="Add Ingredients", padding="5")
        ing_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Ingredient selection
        select_frame = ttk.Frame(ing_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(select_frame, text="Ingredient:").pack(side=tk.LEFT)
        self.ingredient_combo = ttk.Combobox(select_frame, width=25)
        self.ingredient_combo.pack(side=tk.LEFT, padx=5)
        
        # Quantity inputs
        qty_frame = ttk.Frame(ing_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(qty_frame, text="Min Qty:").pack(side=tk.LEFT)
        self.min_qty_var = tk.StringVar(value="0")
        ttk.Entry(qty_frame, textvariable=self.min_qty_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(qty_frame, text="Max Qty:").pack(side=tk.LEFT)
        self.max_qty_var = tk.StringVar(value="0")
        ttk.Entry(qty_frame, textvariable=self.max_qty_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(qty_frame, text="Add to Recipe", command=self.add_ingredient_to_recipe).pack(side=tk.LEFT, padx=10)
        
        # Recipe ingredients list
        recipe_list_frame = ttk.LabelFrame(recipe_frame, text="Recipe Ingredients", padding="5")
        recipe_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("ID", "Ingredient", "Unit", "Min Qty", "Max Qty")
        self.recipe_tree = ttk.Treeview(recipe_list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.recipe_tree.heading(col, text=col)
            self.recipe_tree.column(col, width=100)
        
        self.recipe_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(recipe_list_frame, text="Remove Selected", command=self.remove_from_recipe).pack(pady=5)
        
        # Buttons for menu item
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="➕ New Menu Item", command=self.prepare_new_menu_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save Menu Item", command=self.save_menu_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete Menu Item", command=self.delete_menu_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_menu_form).pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.menu_tree.bind("<<TreeviewSelect>>", self.on_menu_item_select)
        
        # Load data
        self.load_menu_items()
        self.load_ingredients_for_combo()
    
    def create_transactions_tab(self):
        """Create transaction history tab"""
        frame = ttk.Frame(self.transactions_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for transactions
        columns = ("ID", "Date", "Item", "Change", "Type", "User", "Notes")
        self.trans_tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        column_widths = [50, 150, 200, 100, 100, 150, 200]
        for col, width in zip(columns, column_widths):
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.trans_tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.trans_tree.xview)
        self.trans_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.trans_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Refresh button
        ttk.Button(frame, text="Refresh", command=self.load_transactions).grid(row=2, column=0, pady=10)
        
        # Load transactions
        self.load_transactions()
    
    def create_categories_tab(self):
        """Create category management tab (admin only)"""
        frame = ttk.Frame(self.categories_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # List of categories
        list_frame = ttk.LabelFrame(frame, text="Existing Categories", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.cat_listbox = tk.Listbox(list_frame, height=15)
        self.cat_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add new category
        add_frame = ttk.LabelFrame(frame, text="Add New Category", padding="10")
        add_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(add_frame, text="Category Name:").pack(pady=5)
        self.new_cat_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_cat_var, width=25).pack(pady=5)
        
        ttk.Button(add_frame, text="Add Category", command=self.add_category).pack(pady=10)
        
        # Load categories
        self.load_categories_list()
    
    def load_categories(self):
        """Load categories into combobox"""
        categories = get_categories()
        self.categories = {name: id for id, name in categories}
        self.category_combo['values'] = list(self.categories.keys())
    
    def load_categories_list(self):
        """Load categories into listbox"""
        categories = get_categories()
        self.cat_listbox.delete(0, tk.END)
        for id, name in categories:
            self.cat_listbox.insert(tk.END, f"{name}")
    
    def load_inventory(self):
        """Load inventory items into treeview"""
        # Clear existing items
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        items = get_inventory()
        low_count = 0
        
        for item in items:
            # Check if low inventory
            status = "OK"
            tags = ()
            try:
                qty_float = float(item[5])
                threshold_float = float(item[6]) if item[6] else 0
                
                if qty_float <= threshold_float and threshold_float > 0:
                    status = "LOW STOCK"
                    tags = ('low',)
                    low_count += 1
                elif qty_float == 0:
                    status = "OUT OF STOCK"
                    tags = ('out',)
            except:
                pass
            
            self.tree.insert("", tk.END, values=(
                item[0], item[1], item[2], item[3], item[4], 
                f"{item[5]:.2f}", f"{item[6]:.2f}" if item[6] else "0.00", status
            ), tags=tags)
        
        # Configure tag colors
        self.tree.tag_configure('low', background='#fff3cd')
        self.tree.tag_configure('out', background='#f8d7da')
        
        # Update status
        if low_count > 0:
            self.status_label.config(text=f"⚠ {low_count} item(s) below minimum threshold")
        else:
            self.status_label.config(text="")
    
    def load_menu_items(self):
        """Load menu items into treeview"""
        if not hasattr(self, 'menu_tree'):
            return
        
        # Clear existing
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        
        items = get_menu_items()
        for item in items:
            status = "Active" if item[3] else "Inactive"
            tags = ()
            if not item[3]:
                tags = ('inactive',)
            
            self.menu_tree.insert("", tk.END, values=(
                item[0], item[1], f"${item[2]:.2f}", status
            ), tags=tags)
        
        # Configure tag colors
        self.menu_tree.tag_configure('inactive', background='#f0f0f0')
    
    def load_ingredients_for_combo(self):
        """Load ingredients into combo box"""
        items = get_inventory()
        self.ingredient_list = {f"{item[1]} ({item[4]})": item[0] for item in items}
        self.ingredient_combo['values'] = list(self.ingredient_list.keys())
    
    def load_recipe_for_menu_item(self, menu_item_id):
        """Load recipe ingredients for selected menu item"""
        # Clear recipe tree
        for row in self.recipe_tree.get_children():
            self.recipe_tree.delete(row)
        
        recipe = get_recipe_for_menu_item(menu_item_id)
        for ing in recipe:
            self.recipe_tree.insert("", tk.END, values=(
                ing['ingredient_id'],
                ing['ingredient_name'],
                ing['unit'],
                f"{ing['min_qty']:.2f}",
                f"{ing['max_qty']:.2f}"
            ))
    
    def load_transactions(self):
        """Load transaction history"""
        if not hasattr(self, 'trans_tree'):
            return
        
        # Clear existing
        for row in self.trans_tree.get_children():
            self.trans_tree.delete(row)
        
        transactions = get_inventory_transactions(limit=100)
        
        for t in transactions:
            # Format date if it's a datetime object
            if t['created_at']:
                date_str = t['created_at'].strftime("%Y-%m-%d %H:%M") if hasattr(t['created_at'], 'strftime') else str(t['created_at'])
            else:
                date_str = "N/A"
            
            self.trans_tree.insert("", tk.END, values=(
                t['id'],
                date_str,
                t['item_name'],
                f"{t['change_amount']:+.2f}",
                t['transaction_type'].upper(),
                t['username'] or 'System',
                t['notes'] or ''
            ))
    
    def filter_inventory(self):
        """Filter inventory based on search term"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if search_term in str(values[1]).lower() or search_term in str(values[3]).lower():
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)
    
    def filter_menu_items(self):
        """Filter menu items based on search term"""
        search_term = self.menu_search_var.get().lower()
        
        for item in self.menu_tree.get_children():
            values = self.menu_tree.item(item)['values']
            if search_term in str(values[1]).lower():
                self.menu_tree.reattach(item, '', 'end')
            else:
                self.menu_tree.detach(item)
    
    def check_low_inventory(self):
        """Alert if there are low inventory items"""
        low_items = get_low_inventory()
        if low_items and self.user['role'] in ['admin', 'inventory_manager']:
            message = "LOW INVENTORY ALERT:\n\n"
            for item in low_items:
                message += f"• {item[1]}: {item[2]:.2f} {item[3]} (Threshold: {item[4]})\n"
            messagebox.showwarning("Low Inventory", message)
    
    def add_item(self):
        """Add new inventory item"""
        if not self.can_add:
            messagebox.showerror("Permission Denied", "You don't have permission to add items")
            return
        
        # Validate inputs
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Item name is required")
            return
        
        category_name = self.category_var.get()
        if not category_name:
            messagebox.showerror("Error", "Please select a category")
            return
        
        category_id = self.categories.get(category_name)
        brand = self.brand_var.get().strip()
        unit = self.unit_var.get()
        
        if not unit:
            messagebox.showerror("Error", "Please select a unit")
            return
        
        try:
            quantity = float(self.qty_var.get() or 0)
            threshold = float(self.threshold_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Quantity and Threshold must be numbers")
            return
        
        # Add to database
        try:
            add_inventory(name, category_id, brand, unit, quantity, threshold, self.user['id'])
            messagebox.showinfo("Success", f"{name} added successfully")
            self.load_inventory()
            self.load_ingredients_for_combo()  # Refresh ingredient list
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_item(self):
        """Update selected inventory item quantity"""
        if not self.can_edit:
            messagebox.showerror("Permission Denied", "You don't have permission to update items")
            return
        
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to update")
            return
        
        item_id = self.tree.item(selected)['values'][0]
        
        try:
            quantity = float(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return
        
        notes = self.notes_var.get().strip()
        
        try:
            update_inventory(item_id, quantity, self.user['id'], notes)
            messagebox.showinfo("Success", "Item quantity updated successfully")
            self.load_inventory()
            self.load_ingredients_for_combo()  # Refresh ingredient list
            if self.can_view_transactions:
                self.load_transactions()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_stock(self):
        """Add stock to existing item"""
        if not self.can_edit:
            messagebox.showerror("Permission Denied", "You don't have permission to update items")
            return
        
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to add stock")
            return
        
        # Create dialog for adding stock
        dialog = tk.Toplevel(self.win)
        dialog.title("Add Stock")
        dialog.geometry("300x250")
        dialog.transient(self.win)
        dialog.grab_set()
        
        item_id = self.tree.item(selected)['values'][0]
        current_qty = float(self.tree.item(selected)['values'][5])
        
        tk.Label(dialog, text=f"Item: {self.tree.item(selected)['values'][1]}", 
                font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(dialog, text=f"Current Quantity: {current_qty:.2f}").pack()
        
        tk.Label(dialog, text="Amount to Add:").pack(pady=5)
        add_var = tk.StringVar(value="0")
        tk.Entry(dialog, textvariable=add_var, width=10).pack()
        
        tk.Label(dialog, text="Notes:").pack(pady=5)
        notes_var = tk.StringVar()
        tk.Entry(dialog, textvariable=notes_var, width=25).pack()
        
        def do_add():
            try:
                amount = float(add_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Please enter a positive number")
                    return
                
                new_qty = current_qty + amount
                notes = notes_var.get().strip() or f"Added {amount} {self.tree.item(selected)['values'][4]}"
                
                update_inventory(item_id, new_qty, self.user['id'], notes)
                self.load_inventory()
                self.load_ingredients_for_combo()
                dialog.destroy()
                messagebox.showinfo("Success", f"Added {amount} to inventory")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        tk.Button(dialog, text="Add", command=do_add, bg="green", fg="white").pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def delete_item(self):
        """Delete selected inventory item"""
        if not self.can_delete:
            messagebox.showerror("Permission Denied", "Only admins can delete items")
            return
        
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to delete")
            return
        
        item_id = self.tree.item(selected)['values'][0]
        item_name = self.tree.item(selected)['values'][1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete '{item_name}'?\n\nThis action cannot be undone."
        )
        if not confirm:
            return
        
        try:
            delete_inventory(item_id)
            self.load_inventory()
            self.load_ingredients_for_combo()
            self.clear_fields()
            messagebox.showinfo("Success", f"{item_name} deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_category(self):
        """Add new category (admin only)"""
        name = self.new_cat_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a category name")
            return
        
        if add_category(name):
            self.new_cat_var.set("")
            self.load_categories()
            self.load_categories_list()
            messagebox.showinfo("Success", f"Category '{name}' added")
        else:
            messagebox.showerror("Error", "Category already exists or invalid name")
    
    def add_ingredient_to_recipe(self):
        """Add selected ingredient to recipe"""
        if not self.ingredient_combo.get():
            messagebox.showwarning("No Selection", "Please select an ingredient")
            return
        
        try:
            min_qty = float(self.min_qty_var.get())
            max_qty = float(self.max_qty_var.get())
            
            if min_qty <= 0 or max_qty <= 0:
                messagebox.showerror("Error", "Quantities must be greater than 0")
                return
            
            if min_qty > max_qty:
                messagebox.showerror("Error", "Min quantity cannot be greater than max quantity")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantities must be numbers")
            return
        
        # Get ingredient info
        selected_text = self.ingredient_combo.get()
        ingredient_id = self.ingredient_list.get(selected_text)
        
        if not ingredient_id:
            return
        
        # Get ingredient details from inventory
        items = get_inventory()
        ingredient_name = ""
        ingredient_unit = ""
        for item in items:
            if item[0] == ingredient_id:
                ingredient_name = item[1]
                ingredient_unit = item[4]
                break
        
        # Check if already in recipe
        for child in self.recipe_tree.get_children():
            values = self.recipe_tree.item(child)['values']
            if values[0] == ingredient_id:
                messagebox.showinfo("Already Added", "This ingredient is already in the recipe")
                return
        
        # Add to recipe tree
        self.recipe_tree.insert("", tk.END, values=(
            ingredient_id,
            ingredient_name,
            ingredient_unit,
            f"{min_qty:.2f}",
            f"{max_qty:.2f}"
        ))
        
        # Clear inputs
        self.ingredient_combo.set("")
        self.min_qty_var.set("0")
        self.max_qty_var.set("0")
    
    def remove_from_recipe(self):
        """Remove selected ingredient from recipe"""
        selected = self.recipe_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an ingredient to remove")
            return
        
        self.recipe_tree.delete(selected)
    
    def save_menu_item(self):
        """Save menu item with recipe"""
        if not self.can_manage_menu:
            messagebox.showerror("Permission Denied", "Only admins can manage menu items")
            return
        
        # Validate
        name = self.menu_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Menu item name is required")
            return
        
        try:
            price = float(self.menu_price_var.get())
            if price <= 0:
                messagebox.showerror("Error", "Price must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return
        
        # Get recipe ingredients from tree
        ingredients = []
        for child in self.recipe_tree.get_children():
            values = self.recipe_tree.item(child)['values']
            ingredients.append({
                'ingredient_id': values[0],
                'min_qty': float(values[3]),
                'max_qty': float(values[4])
            })
        
        if not ingredients:
            confirm = messagebox.askyesno(
                "No Ingredients", 
                "This menu item has no ingredients. Are you sure you want to save it?"
            )
            if not confirm:
                return
        
        # Check if updating or adding
        selected = self.menu_tree.focus()
        try:
            if selected:
                # Update existing
                menu_id = self.menu_tree.item(selected)['values'][0]
                update_menu_item(menu_id, name, price, self.menu_status_var.get(), ingredients)
                messagebox.showinfo("Success", f"Menu item '{name}' updated successfully")
            else:
                # Add new
                menu_id = add_menu_item(name, price, self.menu_status_var.get(), ingredients)
                messagebox.showinfo("Success", f"Menu item '{name}' added successfully")
            
            self.load_menu_items()
            self.clear_menu_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_menu_item(self):
        """Delete selected menu item"""
        if not self.can_manage_menu:
            messagebox.showerror("Permission Denied", "Only admins can delete menu items")
            return
        
        selected = self.menu_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a menu item to delete")
            return
        
        menu_id = self.menu_tree.item(selected)['values'][0]
        menu_name = self.menu_tree.item(selected)['values'][1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete '{menu_name}'?\n\nThis will also delete its recipe."
        )
        if not confirm:
            return
        
        try:
            delete_menu_item(menu_id)
            self.load_menu_items()
            self.clear_menu_form()
            messagebox.showinfo("Success", f"Menu item '{menu_name}' deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def on_item_select(self, event):
        """Handle inventory item selection"""
        selected = self.tree.focus()
        if not selected:
            return
        
        values = self.tree.item(selected)['values']
        self.name_var.set(values[1])
        self.category_var.set(values[2] or "")
        self.brand_var.set(values[3] or "")
        self.unit_var.set(values[4] or "")
        self.qty_var.set(f"{values[5]}")
        self.threshold_var.set(f"{values[6]}")
        self.notes_var.set("")
    
    def on_menu_item_select(self, event):
        """Handle menu item selection"""
        selected = self.menu_tree.focus()
        if not selected:
            return
        
        values = self.menu_tree.item(selected)['values']
        menu_id = values[0]
        menu_name = values[1]
        price = float(values[2].replace('$', ''))
        status = values[3] == "Active"
        
        self.menu_name_var.set(menu_name)
        self.menu_price_var.set(f"{price:.2f}")
        self.menu_status_var.set(status)
        
        # Load recipe
        self.load_recipe_for_menu_item(menu_id)
    
    def show_item_details(self, event):
        """Show detailed item information"""
        selected = self.tree.focus()
        if not selected:
            return
        
        values = self.tree.item(selected)['values']
        
        detail_win = tk.Toplevel(self.win)
        detail_win.title(f"Item Details - {values[1]}")
        detail_win.geometry("600x500")
        
        # Item details
        details = [
            ("ID:", values[0]),
            ("Name:", values[1]),
            ("Category:", values[2]),
            ("Brand:", values[3]),
            ("Unit:", values[4]),
            ("Current Quantity:", f"{values[5]}"),
            ("Minimum Threshold:", f"{values[6]}"),
            ("Status:", values[7])
        ]
        
        frame = ttk.Frame(detail_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        for i, (label, value) in enumerate(details):
            ttk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Show recent transactions
        if self.can_view_transactions:
            ttk.Label(frame, text="Recent Transactions:", font=("Arial", 10, "bold")).grid(
                row=len(details), column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
            
            transactions = get_inventory_transactions(values[0], 10)
            
            # Create text widget with scrollbar
            trans_frame = ttk.Frame(frame)
            trans_frame.grid(row=len(details)+1, column=0, columnspan=2, pady=5, sticky="nsew")
            
            trans_text = tk.Text(trans_frame, height=8, width=70)
            trans_scroll = ttk.Scrollbar(trans_frame, orient="vertical", command=trans_text.yview)
            trans_text.configure(yscrollcommand=trans_scroll.set)
            
            trans_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            for t in transactions:
                if t['created_at']:
                    date_str = t['created_at'].strftime("%Y-%m-%d %H:%M") if hasattr(t['created_at'], 'strftime') else str(t['created_at'])
                else:
                    date_str = "N/A"
                sign = "+" if t['change_amount'] > 0 else ""
                trans_text.insert(tk.END, 
                    f"{date_str} - "
                    f"{sign}{t['change_amount']:.2f} ({t['transaction_type']}) - "
                    f"{t['username'] or 'System'}\n"
                    f"  Notes: {t['notes'] or 'N/A'}\n\n")
            
            trans_text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Close", command=detail_win.destroy).pack(pady=20)
    
    def clear_fields(self):
        """Clear inventory form fields"""
        self.name_var.set("")
        self.category_var.set("")
        self.brand_var.set("")
        self.unit_var.set("")
        self.qty_var.set("")
        self.threshold_var.set("0")
        self.notes_var.set("")
        self.tree.selection_remove(self.tree.focus())
    
    def clear_menu_form(self):
        """Clear menu item form fields"""
        self.menu_name_var.set("")
        self.menu_price_var.set("")
        self.menu_status_var.set(True)
        
        # Clear recipe tree
        for row in self.recipe_tree.get_children():
            self.recipe_tree.delete(row)
        
        self.menu_tree.selection_remove(self.menu_tree.focus())
    
    def prepare_new_item(self):
        """Prepare inventory form for new item"""
        self.clear_fields()
    
    def prepare_new_menu_item(self):
        """Prepare menu form for new item"""
        self.clear_menu_form()