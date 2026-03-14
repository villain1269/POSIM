import mysql.connector
from mysql.connector import Error

# MySQL Connection Settings
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "password123!"  # Use the correct password
DB_NAME = "bean_brew_pos"

def connect():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def login_user(username, password):
    """Authenticate user login"""
    db = connect()
    if not db:
        return None
    
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username.strip(), password.strip()))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

def get_inventory_with_details():
    """Get inventory with category hierarchy"""
    db = connect()
    if not db:
        return []
    
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT i.*, ic.name as category_name, 
               parent.name as parent_category
        FROM inventory i
        LEFT JOIN inventory_categories ic ON i.category_id = ic.id
        LEFT JOIN inventory_categories parent ON ic.parent_id = parent.id
        ORDER BY i.name
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def add_inventory_transaction(inventory_id, change_amount, transaction_type, reference_id=None, notes=None):
    """Record inventory transaction"""
    db = connect()
    if not db:
        return False
    
    cursor = db.cursor()
    query = """
        INSERT INTO inventory_transactions 
        (inventory_id, change_amount, transaction_type, reference_id, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (inventory_id, change_amount, transaction_type, reference_id, notes))
    db.commit()
    cursor.close()
    db.close()
    return True