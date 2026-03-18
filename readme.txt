# Bean & Brew POS System

A comprehensive Point of Sale system with integrated inventory management for coffee shops and cafes. Built with Python and MySQL.

---

## 📋 Table of Contents
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation Guide](#-installation-guide)
- [Default Login Credentials](#-default-login-credentials)
- [User Roles & Permissions](#-user-roles--permissions)
- [System Structure](#-system-structure)
- [Usage Guide](#-usage-guide)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 👥 Multi-User Role System
- **Admin**: Full system access
- **Inventory Manager**: Manage stock levels
- **Cashier**: Process sales only

### 📦 Inventory Management
- Add, edit, and delete inventory items
- Track quantities with units (g, ml, pcs)
- Set minimum thresholds for low stock alerts
- Color-coded status indicators (yellow for low stock, red for out of stock)
- Transaction history for each item
- Quick "Add Stock" functionality

### 🍽️ Menu Management
- Create and manage menu items
- Set prices for each item
- Build recipes using inventory ingredients
- Define min/max quantities for realistic variation
- Activate/deactivate menu items

### 💰 Point of Sale
- Intuitive product selection with add-ons
- Automatic inventory deduction
- Random variation between recipe quantities
- Itemized receipts showing add-ons
- Real-time stock availability checking

---

## 🛠 Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Python Tkinter |
| Backend | Python 3.8+ |
| Database | MySQL 5.7+ |
| Database Connector | mysql-connector-python |

---

## 📥 Installation Guide

### Prerequisites
- Python 3.8 or higher
- MySQL Server 5.7 or higher
- Git (optional)

### Step 1: Clone the Repository
```bash
git clone https://github.com/villain1269/POSIM.git
cd POSIM
```

### Step 2: Install MySQL
Download and install MySQL from [mysql.com](https://dev.mysql.com/downloads/)

**Default MySQL credentials used in this project:**
- Username: `root`
- Password: `password123!`

*Note: If you use a different password, update it in `database.py`*

### Step 3: Install Python Dependencies
```bash
pip install mysql-connector-python
```

### Step 4: Configure Database Connection

Open `database.py` and update with your MySQL credentials:
```python
DB_HOST = "localhost"
DB_USER = "root"           
DB_PASSWORD = "password123!"  # Change this to your MySQL password
DB_NAME = "bean_brew_pos"
```

### Step 5: Initialize the Database (CRITICAL STEP)

#### ⭐ **Option A: Using Python Script (HIGHLY RECOMMENDED)**
The `init_db.py` script automatically:
- Creates all database tables
- Sets up default categories
- Adds sample inventory items
- Creates menu items with recipes
- Configures product add-ons
- Creates default user accounts

Run this single command:
```bash
python init_db.py
```

**Expected output:**
```
✅ Categories inserted
✅ Users inserted
✅ Inventory items inserted
✅ Products inserted
✅ Recipes inserted
✅ Product addons inserted

==================================================
✅ DATABASE INITIALIZED SUCCESSFULLY!
==================================================
👥 Users: 3
📁 Categories: 8
📦 Inventory items: 7
🛒 Products: 11
📝 Recipes: 8
➕ Add-ons: 7
==================================================

Default login credentials:
   Admin: admin / admin123
   Cashier: cashier / cashier123
   Inventory Manager: inventory / inventory123
==================================================
```

#### Option B: Using MySQL Command Line (Alternative)
```bash
mysql -u root -p < schema.sql
```
(Enter your MySQL password when prompted)

### Step 6: Run the Application
```bash
python main.py
```

---

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Cashier** | `cashier` | `cashier123` |
| **Inventory Manager** | `inventory` | `inventory123` |

> **⚠️ SECURITY NOTE**: Change these default passwords immediately after first login!

---

## 👤 User Roles & Permissions

Feature	Admin	            Inventory Manager	Cashier
Process Sales	            ✅	        ❌	    ✅
View Inventory	            ✅	        ✅	    ✅ (read-only)
Add Inventory Items	        ✅	        ✅	    ❌
Edit Inventory Quantities	✅	        ✅	    ❌
Delete Inventory Items	    ✅	        ❌	    ❌
Add Stock to Existing Items	✅	        ✅	    ❌
Manage Menu Items & Recipes	✅	        ❌	    ❌
View Transaction History	✅	        ✅	    ❌
Manage Categories	        ✅	        ❌	    ❌
User Management*	        ✅	        ❌	    ❌

*User management interface coming soon

---

## 📁 System Structure

```
bean-brew-pos/
│
├── main.py                 # Application entry point
├── login.py                # Login window
├── menu.py                 # Main menu interface
├── pos.py                  # Point of Sale window with add-ons
├── inventory_manager.py    # Full inventory management GUI
├── functions.py            # Core business logic & database operations
├── database.py             # Database connection handler
├── init_db.py              # ⭐ DATABASE SETUP SCRIPT (RUN THIS FIRST!)
├── schema.sql              # SQL database schema (alternative)
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 💻 Usage Guide

### For Administrators

1. **Login** with admin credentials (`admin` / `admin123`)
2. **Inventory Tab**: Add ingredients and supplies
   - Click "➕ New Item" to add inventory
   - Fill in name, category, brand, unit, quantity
   - Set minimum threshold for low stock alerts
3. **Menu Items Tab**: Create menu items
   - Add item name and price
   - Build recipe by adding ingredients from inventory
   - Set min/max quantities for each ingredient
   - Configure add-ons (extra shot, different milk, etc.)
4. **Transaction History**: View all inventory changes
5. **Categories Tab**: Manage inventory categories

### For Inventory Managers

1. **Login** with inventory manager credentials (`inventory` / `inventory123`)
2. View current inventory levels with color-coded status
3. **Add Stock**: Select item → Click "Add Stock" → Enter amount
4. **Update Quantities**: Select item → Edit quantity → Click "Update Quantity"
5. Monitor low stock alerts (highlighted in yellow)
6. View transaction history for audit trail

### For Cashiers

1. **Login** with cashier credentials (`cashier` / `cashier123`)
2. Select products from the left panel
3. For items with add-ons (like lattes), a dialog will appear to customize
4. Adjust quantity as needed
5. Click "Add to Cart"
6. Review cart and total
7. Click "Checkout" to complete sale
8. Receipt will be displayed automatically

---

## 🔧 Troubleshooting

### Database Connection Issues
```
Error: Can't connect to MySQL server
```
- ✅ Verify MySQL is running (`net start MySQL` on Windows)
- ✅ Check credentials in `database.py` match your MySQL installation
- ✅ Ensure database `bean_brew_pos` exists (run `init_db.py`)
- ✅ Try connecting manually: `mysql -u root -p`

### Import Errors
```
ImportError: cannot import name 'X' from 'functions'
```
- ✅ Make sure all files are in the same directory
- ✅ Check for typos in function names
- ✅ Verify you have the latest version of all files

### Login Failures
```
Invalid login!
```
- ✅ Use default credentials: admin/admin123
- ✅ Run `python init_db.py` to reset users
- ✅ Check database connection
- ✅ Verify users table was created: `SELECT * FROM users;`

### Permission Errors
```
Permission Denied
```
- ✅ Log in with appropriate role for the action
- ✅ Some features are role-restricted by design
- ✅ Admin has all permissions

### No Data in Tables
```
Inventory/Products appear empty
```
- ✅ You forgot to run `init_db.py`!
- ✅ Run it now: `python init_db.py`
- ✅ This populates all sample data

### MySQL Command Line Hangs
- ✅ Use `init_db.py` instead (recommended)
- ✅ Or use MySQL Workbench GUI
- ✅ Restart MySQL service

### "Module not found" Errors
```
ModuleNotFoundError: No module named 'mysql'
```
- ✅ Install the connector: `pip install mysql-connector-python`

---

## 🚀 Quick Start Summary

For new users, just remember these 4 commands:

```bash
# 1. Install the Python connector
pip install mysql-connector-python

# 2. Set up the database (creates everything automatically)
python init_db.py

# 3. Launch the application
python main.py

# 4. Log in with:
#    Admin: admin / admin123
```

That's it! The `init_db.py` script handles ALL database setup automatically - tables, categories, inventory items, products, recipes, add-ons, and default users.

---

## 🚀 Future Enhancements

- [ ] User management interface (add/edit/delete users)
- [ ] Sales reports and analytics dashboard
- [ ] Export data to CSV/Excel
- [ ] Barcode scanning integration
- [ ] Customer loyalty program
- [ ] Multiple store locations support
- [ ] Cloud backup integration
- [ ] Email receipts
- [ ] Discount and promotion system
- [ ] Table management for dine-in

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Update documentation as needed
- Test thoroughly before submitting

---

## 📄 License

This project is for educational purposes. Feel free to modify and adapt for your own use.

---

## 🙏 Acknowledgments

- Python Tkinter community
- MySQL documentation
- Coffee shops everywhere for inspiration ☕

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console
3. Make sure you ran `python init_db.py` first
4. Create an issue on GitHub: [https://github.com/villain1269/POSIM/issues](https://github.com/villain1269/POSIM/issues)

---

**Bean & Brew POS System** - Brewing success, one cup at a time! ☕

*Made with ❤️ for coffee shop owners and operators*

---

## 📊 Database Schema Overview

The system uses 8 tables with proper foreign key relationships:

|         Table            |                     Purpose                     |
|----------------|---------|
| `users`                  | System users with role-based access             |
| `categories`             | Inventory categories (Coffee Beans, Milk, etc.) |
| `inventory`              | Track stock items with quantities and thresholds|
| `products`               | Menu items for sale (drinks, food, add-ons)     |
| `recipes`                | Links products to inventory ingredients         |
| `product_addons`         | Configurable extras for menu items              |
| `sales`                  | Transaction records                             |
| `sale_items`             | Individual items in each sale                   |
| `inventory_transactions` | Audit log for all inventory changes             |

---

## ⚙️ Configuration Files

### `database.py`
```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "password123!"  # Change this to your MySQL password
DB_NAME = "bean_brew_pos"
```

### `requirements.txt`
```txt
mysql-connector-python>=8.0.0
```

---

## 🧪 Testing

To verify your installation:

```bash
# Test database connection
python -c "from database import connect; print('Connected!' if connect() else 'Failed!')"

# Initialize database with sample data
python init_db.py

# Run the application
python main.py
```
