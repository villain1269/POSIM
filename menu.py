import tkinter as tk
from tkinter import messagebox
from pos import POSWindow
from inventory_manager import InventoryManagerWindow

class MainMenu:
    def __init__(self, root, user):
        self.root = root
        self.user = user  # user should be a dict with id, username, role, full_name
        
        root.title(f"Bean & Brew POS - Welcome {user.get('full_name', user['username'])}")
        root.geometry("500x450")
        root.configure(bg='#f5f5f5')
        
        # Center the window
        root.eval('tk::PlaceWindow . center')
        
        # Header
        header_frame = tk.Frame(root, bg='#6F4E37', height=80)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Bean & Brew", 
                font=("Arial", 20, "bold"), 
                bg='#6F4E37', fg='white').pack(pady=20)
        
        # User info
        info_frame = tk.Frame(root, bg='#f5f5f5')
        info_frame.pack(pady=20)
        
        role_display = {
            'admin': 'Administrator',
            'cashier': 'Cashier',
            'inventory_manager': 'Inventory Manager'
        }.get(user['role'], user['role'])
        
        tk.Label(info_frame, text=f"Logged in as: {user.get('full_name', user['username'])}",
                font=("Arial", 12), bg='#f5f5f5').pack()
        tk.Label(info_frame, text=f"Role: {role_display}",
                font=("Arial", 10), bg='#f5f5f5', fg='#6F4E37').pack()
        
        # Menu buttons
        button_frame = tk.Frame(root, bg='#f5f5f5')
        button_frame.pack(expand=True)
        
        button_style = {
            'font': ('Arial', 11),
            'width': 25,
            'height': 2,
            'bd': 0,
            'cursor': 'hand2'
        }
        
        # POS Button (admin and cashier)
        if user['role'] in ['admin', 'cashier']:
            tk.Button(button_frame, text="🛒 Point of Sale", bg='#28a745', fg='white',
                     command=self.open_pos, **button_style).pack(pady=5)
        
        # Inventory Button (all roles but with different permissions)
        inventory_text = "📦 View Inventory"
        if user['role'] in ['admin', 'inventory_manager']:
            inventory_text = "📦 Manage Inventory"
        
        tk.Button(button_frame, text=inventory_text, bg='#007bff', fg='white',
                 command=self.open_inventory, **button_style).pack(pady=5)
        
        # User Management (admin only)
        if user['role'] == 'admin':
            tk.Button(button_frame, text="👥 Manage Users", bg='#6c757d', fg='white',
                     command=self.open_user_management, **button_style).pack(pady=5)
        
        # Reports (admin only)
        if user['role'] == 'admin':
            tk.Button(button_frame, text="📊 Reports", bg='#ffc107',
                     command=self.open_reports, **button_style).pack(pady=5)
        
        # Logout button
        tk.Button(root, text="🚪 Logout", bg='#dc3545', fg='white',
                 font=('Arial', 11), width=20, height=1,
                 command=self.logout).pack(pady=20)
    
    def open_pos(self):
        POSWindow(self.root, self.user['id'])
    
    def open_inventory(self):
        InventoryManagerWindow(self.root, self.user)
    
    def open_user_management(self):
        messagebox.showinfo("User Management", "User management feature coming soon!")
    
    def open_reports(self):
        messagebox.showinfo("Reports", "Reports feature coming soon!")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from login import start_login
            start_login()