import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password123!",  # match exactly
        database="bean_brew_pos"
    )
    print("Connected!")
    conn.close()
except mysql.connector.Error as err:
    print("Error:", err)