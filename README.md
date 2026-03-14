Bean & Brew POS System

A comprehensive Point of Sale system with integrated inventory management for coffee shops and cafes. Built with Python and MySQL.
📋 Table of Contents

    Features

    Technology Stack

    Installation Guide

    Default Login Credentials

    User Roles & Permissions

    System Structure

    Usage Guide

    Troubleshooting

    Contributing

    License

✨ Features
👥 Multi-User Role System

    Admin: Full system access

    Inventory Manager: Manage stock levels

    Cashier: Process sales only

📦 Inventory Management

    Add, edit, and delete inventory items

    Track quantities with units (g, ml, pcs)

    Set minimum thresholds for low stock alerts

    Color-coded status indicators

    Transaction history for each item

    Quick "Add Stock" functionality

🍽️ Menu Management

    Create and manage menu items

    Set prices for each item

    Build recipes using inventory ingredients

    Define min/max quantities for realistic variation

    Activate/deactivate menu items

💰 Point of Sale

    Intuitive product selection

    Automatic inventory deduction

    Random variation between recipe quantities

    Itemized receipts

    Real-time stock availability checking

🛠 Technology Stack
Component	Technology
Frontend	Python Tkinter
Backend	Python 3.8+
Database	MySQL 5.7+
Database Connector	mysql-connector-python
📥 Installation Guide
Prerequisites

    Python 3.8 or higher

    MySQL Server 5.7 or higher

    Git (optional)

Step 1: Clone the Repository
bash

git clone https://github.com/yourusername/bean-brew-pos.git
cd bean-brew-pos

Step 2: Install MySQL

Download and install MySQL from mysql.com
Step 3: Install Python Dependencies
bash

pip install mysql-connector-python

Step 4: Configure Database Connection

Edit database.py and update with your MySQL credentials:
python

DB_HOST = "localhost"
DB_USER = "root"           # Your MySQL username
DB_PASSWORD = "yourpassword"  # Your MySQL password
DB_NAME = "bean_brew_pos"

Step 5: Initialize the Database
Option A: Using Python Script (Recommended)
bash

python init_db.py

Option B: Using MySQL Command Line
bash

mysql -u root -p < schema.sql

(Enter your MySQL password when prompted)
Step 6: Run the Application
bash

python main.py

🔑 Default Login Credentials
Role	Username	Password
Admin	admin	admin123
Cashier	cashier	cashier123
Inventory Manager	inventory	inventory123

    ⚠️ SECURITY NOTE: Change these default passwords immediately after first login!

👤 User Roles & Permissions
Feature	Admin	Inventory Manager	Cashier
Process Sales	✅	❌	✅
View Inventory	✅	✅	✅ (read-only)
Add Inventory Items	✅	✅	❌
Edit Inventory	✅	✅	❌
Delete Inventory	✅	❌	❌
Add Stock	✅	✅	❌
Manage Menu Items	✅	❌	❌
View Transactions	✅	✅	❌
Manage Categories	✅	❌	❌
User Management*	✅	❌	❌

*User management interface coming soon
📁 System Structure
text

bean-brew-pos/
│
├── main.py                 # Application entry point
├── login.py                # Login window
├── menu.py                 # Main menu interface
├── pos.py                  # Point of Sale window
├── inventory_manager.py    # Inventory management GUI
├── functions.py            # Core business logic
├── database.py             # Database connection handler
├── init_db.py              # Database initialization script
├── schema.sql              # SQL database schema
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file

💻 Usage Guide
For Administrators

    Login with admin credentials

    Inventory Tab: Add ingredients and supplies

        Click "➕ New Item" to add inventory

        Fill in name, category, brand, unit, quantity

        Set minimum threshold for alerts

    Menu Items Tab: Create menu items

        Add item name and price

        Build recipe by adding ingredients

        Set min/max quantities for each ingredient

    Transaction History: View all inventory changes

    Categories Tab: Manage inventory categories

For Inventory Managers

    Login with inventory manager credentials

    View current inventory levels

    Add Stock: Select item → Click "Add Stock"

    Update Quantities: Select item → Edit quantity → Click "Update Quantity"

    Monitor low stock alerts (highlighted in yellow)

For Cashiers

    Login with cashier credentials

    Select products from the left panel

    Adjust quantity as needed

    Click "Add to Cart"

    Review cart and total

    Click "Checkout" to complete sale

    Receipt will be displayed automatically

🔧 Troubleshooting
Database Connection Issues
text

Error: Can't connect to MySQL server

    Verify MySQL is running

    Check credentials in database.py

    Ensure database bean_brew_pos exists

Import Errors
text

ImportError: cannot import name 'X' from 'functions'

    Make sure all files are in the same directory

    Check for typos in function names

    Verify function exists in functions.py

Login Failures
text

Invalid login!

    Use default credentials: admin/admin123

    Check database connection

    Verify users table has data

Permission Errors
text

Permission Denied

    Log in with appropriate role

    Some features are role-restricted

MySQL Command Line Hangs

    Use init_db.py instead

    Or use MySQL Workbench GUI

    Or just restart the MySQL server

Development Guidelines

    Follow PEP 8 style guide

    Add comments for complex logic

    Update documentation as needed

    Test thoroughly before submitting

🚀 Future Enhancements

    User management interface (add/edit users)

    Sales reports and analytics dashboard

    Export data to CSV/Excel

    Barcode scanning integration

    Customer loyalty program

    Multiple store locations support

    Cloud backup integration

    Email receipts

    Discount and promotion system

    Table management for dine-in

📄 License

This project is for educational purposes. Feel free to modify and adapt for your own use.
🙏 Acknowledgments

    Python Tkinter community

    MySQL documentation

    Coffee shops everywhere for inspiration ☕

📞 Support

For issues or questions:

    Check the troubleshooting section

    Review error messages in the console

    Create an issue on GitHub


Bean & Brew POS System - Brewing success, one cup at a time! ☕

Made with ❤️ for coffee shop owners and operators
