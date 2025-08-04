#!/usr/bin/env python3
"""
Database CSV Loader and Verifier
Loads users.csv and orders.csv into database tables and verifies the data
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import sys

class DatabaseLoader:
    def __init__(self, db_name="ecommerce.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"✅ Connected to database: {self.db_name}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def create_tables(self):
        """Create users and orders tables"""
        try:
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    age INTEGER,
                    gender CHAR(1),
                    state VARCHAR(100),
                    street_address TEXT,
                    postal_code VARCHAR(20),
                    city VARCHAR(100),
                    country VARCHAR(100),
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    traffic_source VARCHAR(50),
                    created_at TIMESTAMP
                )
            ''')
            
            # Orders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    gender CHAR(1),
                    created_at TIMESTAMP,
                    returned_at TIMESTAMP,
                    shipped_at TIMESTAMP,
                    delivered_at TIMESTAMP,
                    num_of_item INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create indexes for better performance
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_city ON users(city)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
            
            self.conn.commit()
            print("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def load_users_csv(self, csv_file="users.csv"):
        """Load users data from CSV file"""
        try:
            print(f"📊 Loading users from {csv_file}...")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"📈 Found {len(df)} users in CSV")
            
            # Clean and prepare data
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Insert data into database
            df.to_sql('users', self.conn, if_exists='replace', index=False)
            
            print(f"✅ Successfully loaded {len(df)} users into database")
            return True
            
        except Exception as e:
            print(f"❌ Error loading users: {e}")
            return False
    
    def load_orders_csv(self, csv_file="orders.csv"):
        """Load orders data from CSV file"""
        try:
            print(f"📊 Loading orders from {csv_file}...")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"📈 Found {len(df)} orders in CSV")
            
            # Clean and prepare data
            date_columns = ['created_at', 'returned_at', 'shipped_at', 'delivered_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Insert data into database
            df.to_sql('orders', self.conn, if_exists='replace', index=False)
            
            print(f"✅ Successfully loaded {len(df)} orders into database")
            return True
            
        except Exception as e:
            print(f"❌ Error loading orders: {e}")
            return False
    
    def verify_data(self):
        """Verify that data was loaded correctly"""
        try:
            print("\n🔍 Verifying loaded data...")
            
            # Check users table
            self.cursor.execute("SELECT COUNT(*) FROM users")
            user_count = self.cursor.fetchone()[0]
            print(f"👥 Users in database: {user_count}")
            
            # Check orders table
            self.cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = self.cursor.fetchone()[0]
            print(f"📦 Orders in database: {order_count}")
            
            # Sample data verification
            print("\n📋 Sample Users:")
            self.cursor.execute("SELECT id, first_name, last_name, email, city FROM users LIMIT 5")
            users_sample = self.cursor.fetchall()
            for user in users_sample:
                print(f"  ID: {user[0]}, Name: {user[1]} {user[2]}, Email: {user[3]}, City: {user[4]}")
            
            print("\n📋 Sample Orders:")
            self.cursor.execute("SELECT order_id, user_id, status, num_of_item FROM orders LIMIT 5")
            orders_sample = self.cursor.fetchall()
            for order in orders_sample:
                print(f"  Order ID: {order[0]}, User ID: {order[1]}, Status: {order[2]}, Items: {order[3]}")
            
            # Data quality checks
            print("\n🔍 Data Quality Checks:")
            
            # Check for null emails
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE email IS NULL")
            null_emails = self.cursor.fetchone()[0]
            print(f"  Users with null emails: {null_emails}")
            
            # Check for orders without valid user_id
            self.cursor.execute("SELECT COUNT(*) FROM orders o LEFT JOIN users u ON o.user_id = u.id WHERE u.id IS NULL")
            orphan_orders = self.cursor.fetchone()[0]
            print(f"  Orders with invalid user_id: {orphan_orders}")
            
            # Check order status distribution
            self.cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
            status_dist = self.cursor.fetchall()
            print("  Order status distribution:")
            for status, count in status_dist:
                print(f"    {status}: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying data: {e}")
            return False
    
    def run_analysis_queries(self):
        """Run some analysis queries to demonstrate data access"""
        try:
            print("\n📊 Data Analysis Queries:")
            
            # Top 5 cities by user count
            print("\n🏙️  Top 5 Cities by User Count:")
            self.cursor.execute("""
                SELECT city, COUNT(*) as user_count 
                FROM users 
                GROUP BY city 
                ORDER BY user_count DESC 
                LIMIT 5
            """)
            top_cities = self.cursor.fetchall()
            for city, count in top_cities:
                print(f"  {city}: {count} users")
            
            # Order completion rate
            print("\n📈 Order Completion Rate:")
            self.cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) as percentage
                FROM orders 
                GROUP BY status
            """)
            completion_stats = self.cursor.fetchall()
            for status, count, percentage in completion_stats:
                print(f"  {status}: {count} orders ({percentage}%)")
            
            # Average items per order
            self.cursor.execute("SELECT AVG(num_of_item) FROM orders WHERE num_of_item IS NOT NULL")
            avg_items = self.cursor.fetchone()[0]
            print(f"\n📦 Average items per order: {avg_items:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error running analysis: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("🔒 Database connection closed")
    
    def run_full_process(self):
        """Run the complete data loading and verification process"""
        print("🚀 Starting Database CSV Loader and Verifier")
        print("=" * 50)
        
        # Connect to database
        if not self.connect_database():
            return False
        
        # Create tables
        if not self.create_tables():
            return False
        
        # Load CSV files
        if not self.load_users_csv():
            return False
        
        if not self.load_orders_csv():
            return False
        
        # Verify data
        if not self.verify_data():
            return False
        
        # Run analysis
        if not self.run_analysis_queries():
            return False
        
        # Close connection
        self.close_connection()
        
        print("\n🎉 Process completed successfully!")
        return True

def main():
    """Main function"""
    loader = DatabaseLoader()
    success = loader.run_full_process()
    
    if success:
        print("\n✅ All operations completed successfully!")
        print("📁 Database file created: ecommerce.db")
        print("📊 You can now query the database using SQLite tools")
    else:
        print("\n❌ Some operations failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 