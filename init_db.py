import mysql.connector
from mysql.connector import Error

def init_database():
    try:
        # Connect without database selected
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123!"  # CHANGE THIS to their MySQL password
        )
        cursor = conn.cursor()
        
        # Drop and create database
        cursor.execute("DROP DATABASE IF EXISTS bean_brew_pos")
        cursor.execute("CREATE DATABASE bean_brew_pos")
        cursor.execute("USE bean_brew_pos")
        
        # ===========================================
        # CREATE TABLES
        # ===========================================
        
        # Users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'cashier', 'inventory_manager') NOT NULL,
                full_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        
        # Inventory table
        cursor.execute("""
            CREATE TABLE inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                brand VARCHAR(100),
                category_id INT,
                unit VARCHAR(20) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
                min_threshold DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Products table
        cursor.execute("""
            CREATE TABLE products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                product_type ENUM('finished', 'ingredient', 'addon') DEFAULT 'finished',
                is_ingredient BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recipes table
        cursor.execute("""
            CREATE TABLE recipes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                ingredient_id INT NOT NULL,
                min_qty DECIMAL(10,2) NOT NULL,
                max_qty DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (ingredient_id) REFERENCES inventory(id)
            )
        """)
        
        # Product addons table
        cursor.execute("""
            CREATE TABLE product_addons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                addon_id INT NOT NULL,
                additional_price DECIMAL(10,2) DEFAULT 0,
                max_quantity INT DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                FOREIGN KEY (addon_id) REFERENCES products(id)
            )
        """)
        
        # Sales table
        cursor.execute("""
            CREATE TABLE sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                total_amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Sale items table
        cursor.execute("""
            CREATE TABLE sale_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sale_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                price_at_time DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Inventory transactions table
        cursor.execute("""
            CREATE TABLE inventory_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                inventory_id INT NOT NULL,
                change_amount DECIMAL(10,2) NOT NULL,
                transaction_type ENUM('purchase', 'sale', 'adjustment') NOT NULL,
                user_id INT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # ===========================================
        # INSERT DEFAULT DATA
        # ===========================================
        
        # Insert categories
        categories = [
            ('Coffee Beans',), ('Milk',), ('Syrups',), ('Powders',),
            ('Pastries',), ('Snacks',), ('Supplies',), ('General',)
        ]
        cursor.executemany("INSERT INTO categories (name) VALUES (%s)", categories)
        print("✅ Categories inserted")
        
        # Insert users
        users = [
            ('admin', 'admin123', 'admin', 'Administrator'),
            ('cashier', 'cashier123', 'cashier', 'Cashier User'),
            ('inventory', 'inventory123', 'inventory_manager', 'Inventory Manager')
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role, full_name) VALUES (%s, %s, %s, %s)",
            users
        )
        print("✅ Users inserted")
        
        # Get category IDs for reference
        cursor.execute("SELECT id, name FROM categories")
        cat_ids = {name: id for id, name in cursor.fetchall()}
        
        # Insert inventory items
        inventory_items = [
            ('Espresso Beans', 'Lavazza', cat_ids['Coffee Beans'], 'g', 5000, 1000),
            ('Whole Milk', 'Fresh', cat_ids['Milk'], 'ml', 10000, 2000),
            ('Vanilla Syrup', 'Monin', cat_ids['Syrups'], 'ml', 3000, 500),
            ('Matcha Powder', 'Ito En', cat_ids['Powders'], 'g', 2000, 400),
            ('Chocolate Chip Cookie', 'Homemade', cat_ids['Pastries'], 'pcs', 50, 10),
            ('Croissant', 'Homemade', cat_ids['Pastries'], 'pcs', 30, 5),
            ('Sugar Packets', 'Generic', cat_ids['General'], 'pcs', 500, 100)
        ]
        cursor.executemany("""
            INSERT INTO inventory (name, brand, category_id, unit, quantity, min_threshold)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, inventory_items)
        print("✅ Inventory items inserted")
        
        # Insert products
        products = [
            ('Espresso', 3.50, 'finished', False),
            ('Latte', 4.50, 'finished', False),
            ('Cappuccino', 4.00, 'finished', False),
            ('Matcha Latte', 5.00, 'finished', False),
            ('Hot Chocolate', 4.00, 'finished', False),
            ('Cookie', 2.00, 'finished', False),
            ('Croissant', 3.00, 'finished', False),
            ('Extra Shot', 0.75, 'addon', True),
            ('Vanilla Syrup', 0.50, 'addon', True),
            ('Soy Milk', 0.50, 'addon', True),
            ('Whipped Cream', 0.25, 'addon', False)
        ]
        cursor.executemany("""
            INSERT INTO products (name, price, product_type, is_ingredient)
            VALUES (%s, %s, %s, %s)
        """, products)
        print("✅ Products inserted")
        
        # Get product IDs for recipes
        cursor.execute("SELECT id, name FROM products")
        prod_ids = {name: id for id, name in cursor.fetchall()}
        
        # Get inventory IDs for recipes
        cursor.execute("SELECT id, name FROM inventory")
        inv_ids = {name: id for id, name in cursor.fetchall()}
        
        # Insert recipes
        recipes = [
            # Espresso uses beans
            (prod_ids['Espresso'], inv_ids['Espresso Beans'], 18, 22),
            # Latte uses beans and milk
            (prod_ids['Latte'], inv_ids['Espresso Beans'], 18, 22),
            (prod_ids['Latte'], inv_ids['Whole Milk'], 150, 200),
            # Cappuccino uses beans and milk
            (prod_ids['Cappuccino'], inv_ids['Espresso Beans'], 18, 22),
            (prod_ids['Cappuccino'], inv_ids['Whole Milk'], 100, 150),
            # Matcha Latte uses matcha and milk
            (prod_ids['Matcha Latte'], inv_ids['Matcha Powder'], 10, 15),
            (prod_ids['Matcha Latte'], inv_ids['Whole Milk'], 200, 250),
            # Hot Chocolate uses milk
            (prod_ids['Hot Chocolate'], inv_ids['Whole Milk'], 150, 200),
            # Cookie uses cookie
            (prod_ids['Cookie'], inv_ids['Chocolate Chip Cookie'], 1, 1),
            # Croissant uses croissant
            (prod_ids['Croissant'], inv_ids['Croissant'], 1, 1),
            # Extra Shot uses more beans
            (prod_ids['Extra Shot'], inv_ids['Espresso Beans'], 18, 22),
            # Vanilla Syrup (addon) uses vanilla syrup
            (prod_ids['Vanilla Syrup'], inv_ids['Vanilla Syrup'], 10, 15)
        ]
        cursor.executemany("""
            INSERT INTO recipes (product_id, ingredient_id, min_qty, max_qty)
            VALUES (%s, %s, %s, %s)
        """, recipes)
        print("✅ Recipes inserted")
        
        # Insert product addons
        addons = [
            # Latte addons
            (prod_ids['Latte'], prod_ids['Extra Shot'], 0.75, 3),
            (prod_ids['Latte'], prod_ids['Vanilla Syrup'], 0.50, 2),
            (prod_ids['Latte'], prod_ids['Soy Milk'], 0.50, 1),
            (prod_ids['Latte'], prod_ids['Whipped Cream'], 0.25, 1),
            # Matcha Latte addons
            (prod_ids['Matcha Latte'], prod_ids['Extra Shot'], 0.75, 2),
            (prod_ids['Matcha Latte'], prod_ids['Soy Milk'], 0.50, 1),
            # Espresso addons
            (prod_ids['Espresso'], prod_ids['Extra Shot'], 0.75, 2),
            # Cappuccino addons
            (prod_ids['Cappuccino'], prod_ids['Extra Shot'], 0.75, 2),
            (prod_ids['Cappuccino'], prod_ids['Whipped Cream'], 0.25, 1),
            # Hot Chocolate addons
            (prod_ids['Hot Chocolate'], prod_ids['Whipped Cream'], 0.25, 1),
            (prod_ids['Hot Chocolate'], prod_ids['Vanilla Syrup'], 0.50, 1)
        ]
        cursor.executemany("""
            INSERT INTO product_addons (product_id, addon_id, additional_price, max_quantity)
            VALUES (%s, %s, %s, %s)
        """, addons)
        print("✅ Product addons inserted")
        
        # Commit all changes
        conn.commit()
        
        # ===========================================
        # SUMMARY
        # ===========================================
        print("\n" + "="*50)
        print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
        print("="*50)
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM categories")
        cats_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM inventory")
        inv_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        prod_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM product_addons")
        addon_count = cursor.fetchone()[0]
        
        print(f"👥 Users: {users_count}")
        print(f"📁 Categories: {cats_count}")
        print(f"📦 Inventory items: {inv_count}")
        print(f"🛒 Products: {prod_count}")
        print(f"📝 Recipes: {recipe_count}")
        print(f"➕ Add-ons: {addon_count}")
        print("="*50)
        print("\nDefault login credentials:")
        print("   Admin: admin / admin123")
        print("   Cashier: cashier / cashier123")
        print("   Inventory Manager: inventory / inventory123")
        print("="*50)
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    init_database()
