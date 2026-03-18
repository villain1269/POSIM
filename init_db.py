import mysql.connector
from mysql.connector import Error

def init_database():
    try:
        # Connect without database selected
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password123!"  # Change this to their MySQL password
        )
        cursor = conn.cursor()
        
        # Drop and create database
        cursor.execute("DROP DATABASE IF EXISTS bean_brew_pos")
        cursor.execute("CREATE DATABASE bean_brew_pos")
        cursor.execute("USE bean_brew_pos")
        
        # Create users table
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
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        
        # Create inventory table
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
        
        # Create products table
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
        
        # Create recipes table
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
        
        # Create product_addons table
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
        
        # Create sales table
        cursor.execute("""
            CREATE TABLE sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                total_amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create sale_items table
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
        
        # Create inventory_transactions table
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
        
        # Insert default categories
        categories = [
            ('Coffee Beans',), ('Milk',), ('Syrups',), ('Powders',),
            ('Pastries',), ('Snacks',), ('Supplies',), ('General',)
        ]
        cursor.executemany("INSERT INTO categories (name) VALUES (%s)", categories)
        
        # Insert default users
        users = [
            ('admin', 'admin123', 'admin', 'Administrator'),
            ('cashier', 'cashier123', 'cashier', 'Cashier User'),
            ('inventory', 'inventory123', 'inventory_manager', 'Inventory Manager')
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role, full_name) VALUES (%s, %s, %s, %s)",
            users
        )
        
        conn.commit()
        print("✅ Database initialized successfully!")
        print("👥 Users: 3")
        print("📁 Categories: 8")
        
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_database()