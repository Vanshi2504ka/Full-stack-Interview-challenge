#!/usr/bin/env python3
"""
RESTful API for Customer Data and Order Statistics
Provides endpoints for accessing user data and order analytics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DB_NAME = "ecommerce.db"

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def serialize_datetime(obj):
    """Convert datetime objects to string for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if os.path.exists(DB_NAME) else 'not found'
    })

# Customer endpoints
@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        city = request.args.get('city')
        gender = request.args.get('gender')
        search = request.args.get('search')
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if city:
            where_conditions.append("city LIKE ?")
            params.append(f"%{city}%")
        
        if gender:
            where_conditions.append("gender = ?")
            params.append(gender.upper())
        
        if search:
            where_conditions.append("(first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM users{where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get customers
        query = f"""
            SELECT id, first_name, last_name, email, age, gender, 
                   city, state, country, created_at
            FROM users{where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        customers = cursor.fetchall()
        
        # Convert to list of dictionaries
        customers_list = []
        for customer in customers:
            customer_dict = dict(customer)
            customer_dict['created_at'] = customer_dict['created_at'] if customer_dict['created_at'] else None
            customers_list.append(customer_dict)
        
        conn.close()
        
        return jsonify({
            'customers': customers_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get customer details
        cursor.execute("""
            SELECT id, first_name, last_name, email, age, gender, 
                   state, street_address, postal_code, city, country,
                   latitude, longitude, traffic_source, created_at
            FROM users 
            WHERE id = ?
        """, [customer_id])
        
        customer = cursor.fetchone()
        
        if not customer:
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get customer's orders
        cursor.execute("""
            SELECT order_id, status, created_at, returned_at, 
                   shipped_at, delivered_at, num_of_item
            FROM orders 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, [customer_id])
        
        orders = cursor.fetchall()
        
        # Convert to dictionary
        customer_dict = dict(customer)
        customer_dict['created_at'] = customer_dict['created_at'] if customer_dict['created_at'] else None
        customer_dict['orders'] = [dict(order) for order in orders]
        
        conn.close()
        
        return jsonify(customer_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order endpoints
@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if status:
            where_conditions.append("status = ?")
            params.append(status)
        
        if user_id:
            where_conditions.append("user_id = ?")
            params.append(user_id)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM orders{where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get orders with customer info
        query = f"""
            SELECT o.order_id, o.user_id, o.status, o.gender, 
                   o.created_at, o.returned_at, o.shipped_at, o.delivered_at, o.num_of_item,
                   u.first_name, u.last_name, u.email, u.city
            FROM orders o
            JOIN users u ON o.user_id = u.id{where_clause}
            ORDER BY o.created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        orders = cursor.fetchall()
        
        # Convert to list of dictionaries
        orders_list = []
        for order in orders:
            order_dict = dict(order)
            # Convert datetime fields
            for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
                order_dict[field] = order_dict[field] if order_dict[field] else None
            orders_list.append(order_dict)
        
        conn.close()
        
        return jsonify({
            'orders': orders_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.order_id, o.user_id, o.status, o.gender, 
                   o.created_at, o.returned_at, o.shipped_at, o.delivered_at, o.num_of_item,
                   u.first_name, u.last_name, u.email, u.city, u.state, u.country
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.order_id = ?
        """, [order_id])
        
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return jsonify({'error': 'Order not found'}), 404
        
        # Convert to dictionary
        order_dict = dict(order)
        # Convert datetime fields
        for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
            order_dict[field] = order_dict[field] if order_dict[field] else None
        
        conn.close()
        
        return jsonify(order_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Statistics endpoints
@app.route('/api/stats/overview', methods=['GET'])
def get_overview_stats():
    """Get overview statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total customers and orders
        cursor.execute("SELECT COUNT(*) FROM users")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        # Order status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM orders 
            GROUP BY status
        """)
        status_distribution = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Average items per order
        cursor.execute("SELECT AVG(num_of_item) FROM orders WHERE num_of_item IS NOT NULL")
        avg_items = cursor.fetchone()[0]
        
        # Top cities by customer count
        cursor.execute("""
            SELECT city, COUNT(*) as count
            FROM users 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_cities = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_customers': total_customers,
            'total_orders': total_orders,
            'status_distribution': status_distribution,
            'average_items_per_order': round(avg_items, 2) if avg_items else 0,
            'top_cities': top_cities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/customers', methods=['GET'])
def get_customer_stats():
    """Get customer-related statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Gender distribution
        cursor.execute("""
            SELECT gender, COUNT(*) as count
            FROM users 
            WHERE gender IS NOT NULL
            GROUP BY gender
        """)
        gender_distribution = {row['gender']: row['count'] for row in cursor.fetchall()}
        
        # Age distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN age < 25 THEN '18-24'
                    WHEN age < 35 THEN '25-34'
                    WHEN age < 45 THEN '35-44'
                    WHEN age < 55 THEN '45-54'
                    WHEN age < 65 THEN '55-64'
                    ELSE '65+'
                END as age_group,
                COUNT(*) as count
            FROM users 
            WHERE age IS NOT NULL
            GROUP BY age_group
            ORDER BY age_group
        """)
        age_distribution = [dict(row) for row in cursor.fetchall()]
        
        # Traffic source distribution
        cursor.execute("""
            SELECT traffic_source, COUNT(*) as count
            FROM users 
            WHERE traffic_source IS NOT NULL
            GROUP BY traffic_source
            ORDER BY count DESC
            LIMIT 10
        """)
        traffic_sources = [dict(row) for row in cursor.fetchall()]
        
        # Customers with most orders
        cursor.execute("""
            SELECT u.first_name, u.last_name, u.email, COUNT(o.order_id) as order_count
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.first_name, u.last_name, u.email
            ORDER BY order_count DESC
            LIMIT 10
        """)
        top_customers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'gender_distribution': gender_distribution,
            'age_distribution': age_distribution,
            'traffic_sources': traffic_sources,
            'top_customers': top_customers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/orders', methods=['GET'])
def get_order_stats():
    """Get order-related statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Monthly order trends
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as count
            FROM orders 
            WHERE created_at IS NOT NULL
            GROUP BY month
            ORDER BY month
        """)
        monthly_trends = [dict(row) for row in cursor.fetchall()]
        
        # Order completion rate by month
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                status,
                COUNT(*) as count
            FROM orders 
            WHERE created_at IS NOT NULL
            GROUP BY month, status
            ORDER BY month, status
        """)
        completion_by_month = [dict(row) for row in cursor.fetchall()]
        
        # Average order value by city
        cursor.execute("""
            SELECT u.city, AVG(o.num_of_item) as avg_items, COUNT(o.order_id) as order_count
            FROM users u
            JOIN orders o ON u.id = o.user_id
            GROUP BY u.city
            HAVING order_count > 10
            ORDER BY avg_items DESC
            LIMIT 10
        """)
        city_stats = [dict(row) for row in cursor.fetchall()]
        
        # Order status timeline
        cursor.execute("""
            SELECT 
                status,
                AVG(JULIANDAY(delivered_at) - JULIANDAY(created_at)) as avg_delivery_days
            FROM orders 
            WHERE status = 'Delivered' 
                AND created_at IS NOT NULL 
                AND delivered_at IS NOT NULL
        """)
        delivery_timeline = cursor.fetchone()
        avg_delivery_days = round(delivery_timeline[1], 1) if delivery_timeline and delivery_timeline[1] else None
        
        conn.close()
        
        return jsonify({
            'monthly_trends': monthly_trends,
            'completion_by_month': completion_by_month,
            'city_stats': city_stats,
            'average_delivery_days': avg_delivery_days
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search endpoint
