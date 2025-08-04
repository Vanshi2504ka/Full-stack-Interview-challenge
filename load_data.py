import pandas as pd
import sqlite3

# Load CSV files
print("Loading users.csv...")
users_df = pd.read_csv('users.csv')
print(f"Loaded {len(users_df)} users")

print("Loading orders.csv...")
orders_df = pd.read_csv('orders.csv')
print(f"Loaded {len(orders_df)} orders")

# Create database
conn = sqlite3.connect('ecommerce.db')

# Create tables and load data
print("Creating database tables...")
users_df.to_sql('users', conn, if_exists='replace', index=False)
orders_df.to_sql('orders', conn, if_exists='replace', index=False)

# Verify data
cursor = conn.cursor()

print("\n=== DATA VERIFICATION ===")
print(f"Users in database: {cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
print(f"Orders in database: {cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]}")

print("\n=== SAMPLE USERS ===")
sample_users = cursor.execute('SELECT id, first_name, last_name, email FROM users LIMIT 5').fetchall()
for user in sample_users:
    print(f"ID: {user[0]}, Name: {user[1]} {user[2]}, Email: {user[3]}")

print("\n=== SAMPLE ORDERS ===")
sample_orders = cursor.execute('SELECT order_id, user_id, status, num_of_item FROM orders LIMIT 5').fetchall()
for order in sample_orders:
    print(f"Order ID: {order[0]}, User ID: {order[1]}, Status: {order[2]}, Items: {order[3]}")

print("\n=== ORDER STATUS DISTRIBUTION ===")
status_dist = cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status').fetchall()
for status, count in status_dist:
    print(f"{status}: {count} orders")

print("\n=== TOP 5 CITIES BY USER COUNT ===")
top_cities = cursor.execute('SELECT city, COUNT(*) FROM users GROUP BY city ORDER BY COUNT(*) DESC LIMIT 5').fetchall()
for city, count in top_cities:
    print(f"{city}: {count} users")

conn.close()
print("\nDatabase created successfully: ecommerce.db") 