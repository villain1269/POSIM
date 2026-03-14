from database import connect
import random
from datetime import datetime

# --- User Management Functions ---
def get_all_users():
    """Get all users for admin management"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY username")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users

def add_user(username, password, full_name, role):
    """Add a new user (admin only)"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (%s, %s, %s, %s)",
            (username, password, full_name, role)
        )
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def update_user_password(user_id, new_password):
    """Update user password"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, user_id))
    db.commit()
    cursor.close()
    db.close()
    return True

def delete_user(user_id):
    """Delete a user (admin only)"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return True

# --- Category Functions ---
def get_categories():
    """Get all inventory categories"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return categories

def add_category(name):
    """Add new category"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

# --- Inventory Functions ---
def add_inventory(name, category_id, brand, unit, quantity, min_threshold=0, user_id=None):
    """Add new inventory item"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO inventory 
               (name, category_id, brand, unit, quantity, min_threshold) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, category_id, brand, unit, quantity, min_threshold)
        )
        inventory_id = cursor.lastrowid
        
        # Record transaction
        if user_id:
            cursor.execute(
                """INSERT INTO inventory_transactions 
                   (inventory_id, change_amount, transaction_type, user_id, notes)
                   VALUES (%s, %s, 'purchase', %s, 'Initial stock')""",
                (inventory_id, quantity, user_id)
            )
        
        db.commit()
        return inventory_id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def update_inventory(item_id, quantity, user_id=None, notes=None):
    """Update inventory quantity"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        # Get current quantity
        cursor.execute("SELECT quantity FROM inventory WHERE id=%s", (item_id,))
        current = cursor.fetchone()
        if not current:
            return False
        
        change = quantity - current[0]
        
        # Update quantity
        cursor.execute("UPDATE inventory SET quantity=%s WHERE id=%s", (quantity, item_id))
        
        # Record transaction if there's a change
        if change != 0 and user_id:
            transaction_type = 'purchase' if change > 0 else 'adjustment'
            cursor.execute(
                """INSERT INTO inventory_transactions 
                   (inventory_id, change_amount, transaction_type, user_id, notes)
                   VALUES (%s, %s, %s, %s, %s)""",
                (item_id, change, transaction_type, user_id, notes)
            )
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def delete_inventory(item_id, user_id=None):
    """Delete inventory item (admin only)"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        # Check if item is used in recipes
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE ingredient_id=%s", (item_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            raise Exception("Cannot delete item that is used in recipes")
        
        cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id,))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def get_inventory():
    """Get all inventory items with category names"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT i.id, i.name, c.name as category, i.brand, i.unit, 
               i.quantity, i.min_threshold
        FROM inventory i
        LEFT JOIN categories c ON i.category_id = c.id
        ORDER BY i.name
    """)
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

def get_low_inventory():
    """Get items below threshold"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT i.id, i.name, i.quantity, i.unit, i.min_threshold
        FROM inventory i
        WHERE i.quantity <= i.min_threshold AND i.min_threshold > 0
        ORDER BY (i.quantity / i.min_threshold)
    """)
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

def get_inventory_transactions(item_id=None, limit=50):
    """Get inventory transaction history"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor(dictionary=True)
    if item_id:
        cursor.execute("""
            SELECT t.*, i.name as item_name, u.username
            FROM inventory_transactions t
            JOIN inventory i ON t.inventory_id = i.id
            LEFT JOIN users u ON t.user_id = u.id
            WHERE t.inventory_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s
        """, (item_id, limit))
    else:
        cursor.execute("""
            SELECT t.*, i.name as item_name, u.username
            FROM inventory_transactions t
            JOIN inventory i ON t.inventory_id = i.id
            LEFT JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            LIMIT %s
        """, (limit,))
    
    transactions = cursor.fetchall()
    cursor.close()
    db.close()
    return transactions

def check_inventory_availability(product_id, quantity=1):
    """
    Check if enough inventory is available for a product
    Returns: (bool, message) - True if available, False with reason if not
    """
    db = connect()
    if not db:
        return False, "Database connection error"
    
    cursor = db.cursor()
    try:
        # Get recipe ingredients for the product
        cursor.execute("""
            SELECT i.id, i.name, i.unit, r.max_qty, i.quantity
            FROM recipes r
            JOIN inventory i ON r.ingredient_id = i.id
            WHERE r.product_id = %s
        """, (product_id,))
        
        ingredients = cursor.fetchall()
        
        # If no recipe found, assume it's a non-food item (like pastry) that just needs to exist
        if not ingredients:
            # Check if product exists at all
            cursor.execute("SELECT COUNT(*) FROM products WHERE id=%s AND is_active=1", (product_id,))
            if cursor.fetchone()[0] == 0:
                return False, "Product not found"
            return True, "Available (no recipe tracking)"
        
        # Check each ingredient
        for ing in ingredients:
            ing_id, name, unit, max_qty, current_qty = ing
            needed = max_qty * quantity
            
            if current_qty < needed:
                return False, f"Not enough {name} (need {needed:.2f}{unit}, have {current_qty:.2f}{unit})"
        
        return True, "Available"
    
    except Exception as e:
        return False, f"Error checking inventory: {str(e)}"
    finally:
        cursor.close()
        db.close()

# --- Product Functions ---
def get_products():
    """Get all active products"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("SELECT id, name, price FROM products WHERE is_active=1 ORDER BY name")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

def get_recipe(product_id):
    """Get recipe ingredients for a product"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT i.id, i.name, i.unit, r.min_qty, r.max_qty, i.quantity
        FROM recipes r
        JOIN inventory i ON r.ingredient_id = i.id
        WHERE r.product_id = %s
    """, (product_id,))
    ingredients = cursor.fetchall()
    cursor.close()
    db.close()
    return ingredients

def deduct_inventory(product_id, quantity_sold=1, user_id=None):
    """Deduct inventory based on recipe and quantity sold"""
    ingredients = get_recipe(product_id)
    if not ingredients:
        return False
    
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        for ing in ingredients:
            ing_id, name, unit, min_qty, max_qty, current_qty = ing
            # Use random quantity within range for each unit sold
            total_used = 0
            for _ in range(quantity_sold):
                used_qty = random.uniform(float(min_qty), float(max_qty))
                total_used += used_qty
            
            # Check if enough inventory
            if current_qty < total_used:
                raise Exception(f"Insufficient {name}! Need {total_used:.2f}{unit}, have {current_qty:.2f}{unit}")
            
            # Update inventory
            cursor.execute(
                "UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                (total_used, ing_id)
            )
            
            # Record transaction
            if user_id:
                cursor.execute(
                    """INSERT INTO inventory_transactions 
                       (inventory_id, change_amount, transaction_type, user_id, notes)
                       VALUES (%s, %s, 'sale', %s, %s)""",
                    (ing_id, -total_used, user_id, f"Product ID {product_id} x{quantity_sold}")
                )
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

# --- Sales Functions ---
def create_sale(user_id, items):
    """
    Create a new sale with proper transaction handling
    items: list of dicts [{'product_id':1, 'quantity':2}, ...]
    Returns: sale_id if successful
    """
    db = connect()
    if not db:
        raise Exception("Database connection error")
    
    cursor = db.cursor()
    try:
        # Start transaction
        db.start_transaction()
        
        # Calculate total and get product prices
        total = 0
        sale_items = []
        
        for item in items:
            cursor.execute("SELECT price FROM products WHERE id=%s AND is_active=1", (item['product_id'],))
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Product ID {item['product_id']} not found or inactive")
            
            price = result[0]
            subtotal = price * item['quantity']
            total += subtotal
            sale_items.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'price': price
            })
        
        # Insert sale
        cursor.execute(
            "INSERT INTO sales (user_id, total_amount) VALUES (%s, %s)",
            (user_id, total)
        )
        sale_id = cursor.lastrowid
        
        # Insert sale items and update inventory
        for item in sale_items:
            # Insert sale item
            cursor.execute(
                """INSERT INTO sale_items 
                   (sale_id, product_id, quantity, price_at_time) 
                   VALUES (%s, %s, %s, %s)""",
                (sale_id, item['product_id'], item['quantity'], item['price'])
            )
            
            # Get recipe for this product
            cursor.execute("""
                SELECT ingredient_id, min_qty, max_qty 
                FROM recipes 
                WHERE product_id = %s
            """, (item['product_id'],))
            
            recipes = cursor.fetchall()
            
            # If product has recipe, deduct ingredients
            if recipes:
                for ing_id, min_qty, max_qty in recipes:
                    # Calculate total used with random variation
                    total_used = 0
                    for _ in range(item['quantity']):
                        total_used += random.uniform(float(min_qty), float(max_qty))
                    
                    # Check current quantity
                    cursor.execute("SELECT quantity FROM inventory WHERE id=%s FOR UPDATE", (ing_id,))
                    current_qty = cursor.fetchone()
                    if not current_qty:
                        raise Exception(f"Ingredient ID {ing_id} not found")
                    
                    current_qty = current_qty[0]
                    if current_qty < total_used:
                        # Get ingredient name for better error message
                        cursor.execute("SELECT name FROM inventory WHERE id=%s", (ing_id,))
                        ing_name = cursor.fetchone()[0]
                        raise Exception(f"Insufficient {ing_name}! Need {total_used:.2f}, have {current_qty:.2f}")
                    
                    # Update inventory
                    cursor.execute(
                        "UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                        (total_used, ing_id)
                    )
                    
                    # Record transaction
                    cursor.execute(
                        """INSERT INTO inventory_transactions 
                           (inventory_id, change_amount, transaction_type, user_id, notes)
                           VALUES (%s, %s, 'sale', %s, %s)""",
                        (ing_id, -total_used, user_id, f"Sale #{sale_id} - Product ID {item['product_id']} x{item['quantity']}")
                    )
        
        # Commit transaction
        db.commit()
        return sale_id
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()
def get_menu_items():
    """Get all menu items"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, price, is_active 
        FROM products 
        WHERE product_type = 'finished'
        ORDER BY name
    """)
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

def add_menu_item(name, price, is_active=True, ingredients=None):
    """Add a new menu item with its recipe"""
    db = connect()
    if not db:
        return None
    
    cursor = db.cursor()
    try:
        # Insert product
        cursor.execute("""
            INSERT INTO products (name, price, product_type, is_active) 
            VALUES (%s, %s, 'finished', %s)
        """, (name, price, is_active))
        product_id = cursor.lastrowid
        
        # Insert recipe ingredients
        if ingredients:
            for ing in ingredients:
                cursor.execute("""
                    INSERT INTO recipes (product_id, ingredient_id, min_qty, max_qty)
                    VALUES (%s, %s, %s, %s)
                """, (product_id, ing['ingredient_id'], ing['min_qty'], ing['max_qty']))
        
        db.commit()
        return product_id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def update_menu_item(product_id, name, price, is_active, ingredients=None):
    """Update a menu item and its recipe"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        # Update product
        cursor.execute("""
            UPDATE products 
            SET name = %s, price = %s, is_active = %s
            WHERE id = %s
        """, (name, price, is_active, product_id))
        
        # Delete old recipe
        cursor.execute("DELETE FROM recipes WHERE product_id = %s", (product_id,))
        
        # Insert new recipe
        if ingredients:
            for ing in ingredients:
                cursor.execute("""
                    INSERT INTO recipes (product_id, ingredient_id, min_qty, max_qty)
                    VALUES (%s, %s, %s, %s)
                """, (product_id, ing['ingredient_id'], ing['min_qty'], ing['max_qty']))
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def delete_menu_item(product_id):
    """Delete a menu item (cascade will delete recipes)"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()

def get_recipe_for_menu_item(product_id):
    """Get recipe ingredients for a menu item"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            r.ingredient_id,
            i.name as ingredient_name,
            i.unit,
            r.min_qty,
            r.max_qty
        FROM recipes r
        JOIN inventory i ON r.ingredient_id = i.id
        WHERE r.product_id = %s
        ORDER BY i.name
    """, (product_id,))
    
    recipe = cursor.fetchall()
    cursor.close()
    db.close()
    return recipe