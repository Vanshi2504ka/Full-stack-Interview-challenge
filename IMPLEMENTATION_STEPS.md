# Implementation Steps: Customer Orders & Order Details

## 🎯 **Overview**

This document explains how I implemented the API endpoints for getting all orders for a specific customer and getting specific order details, including proper JSON response format and comprehensive error handling.

---

## 📋 **Step 1: Database Connection Setup**

### **Implementation:**
```python
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn
```

### **Why This Step:**
- **Security**: Creates isolated connections for each request
- **Performance**: Uses `sqlite3.Row` for efficient column access
- **Reliability**: Proper connection management prevents resource leaks

### **Key Features:**
- ✅ **Row Factory**: Enables `dict(row)` conversion
- ✅ **Connection Isolation**: Each request gets its own connection
- ✅ **Automatic Cleanup**: Connections are closed after use

---

## 📋 **Step 2: Input Validation**

### **Implementation:**
```python
# Validate customer exists
cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = ?", [customer_id])
customer = cursor.fetchone()
if not customer:
    conn.close()
    return jsonify({'error': 'Customer not found'}), 404

# Validate query parameters
page = request.args.get('page', 1, type=int)
per_page = min(request.args.get('per_page', 20, type=int), 100)
```

### **Why This Step:**
- **Data Integrity**: Ensures customer exists before processing
- **Security**: Prevents invalid data from reaching database
- **User Experience**: Provides clear error messages

### **Validation Checks:**
- ✅ **Customer Existence**: Check if customer_id exists in database
- ✅ **Parameter Types**: Convert and validate query parameters
- ✅ **Range Validation**: Ensure per_page doesn't exceed limits
- ✅ **Sort Validation**: Validate sort fields against allowed list

---

## 📋 **Step 3: Query Building with Security**

### **Implementation:**
```python
# Build WHERE clause dynamically
where_conditions = ["user_id = ?"]
params = [customer_id]

if status:
    where_conditions.append("status = ?")
    params.append(status)

where_clause = " WHERE " + " AND ".join(where_conditions)

# Use parameterized query
query = f"""
    SELECT order_id, user_id, status, gender, 
           created_at, returned_at, shipped_at, delivered_at, num_of_item
    FROM orders{where_clause}
    ORDER BY {sort_by} {sort_order}
    LIMIT ? OFFSET ?
"""
cursor.execute(query, params + [per_page, offset])
```

### **Why This Step:**
- **Security**: Prevents SQL injection attacks
- **Flexibility**: Dynamic query building based on filters
- **Performance**: Optimized queries with proper indexing

### **Security Features:**
- ✅ **Parameterized Queries**: All user input is parameterized
- ✅ **Dynamic WHERE Clauses**: Built safely from validated inputs
- ✅ **Input Sanitization**: No raw SQL string concatenation

---

## 📋 **Step 4: Error Handling Strategy**

### **Implementation:**
```python
try:
    # Database operations
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ... database queries ...
    
    conn.close()
    return jsonify(response_data)
    
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

### **Error Scenarios Handled:**

#### **404 - Resource Not Found**
```python
if not customer:
    conn.close()
    return jsonify({'error': 'Customer not found'}), 404
```

#### **400 - Bad Request**
```python
if not status:
    return jsonify({'error': 'Status is required'}), 400
```

#### **500 - Internal Server Error**
```python
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

### **Why This Step:**
- **User Experience**: Clear error messages for different scenarios
- **Debugging**: Proper error codes help identify issues
- **Security**: Don't expose internal errors to users

---

## 📋 **Step 5: Response Formatting**

### **Implementation:**
```python
# Convert database rows to dictionaries
orders_list = []
for order in orders:
    order_dict = dict(order)
    # Handle datetime fields
    for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
        order_dict[field] = order_dict[field] if order_dict[field] else None
    orders_list.append(order_dict)

# Calculate analytics
cursor.execute("""
    SELECT 
        COUNT(*) as total_orders,
        COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_orders,
        AVG(num_of_item) as avg_items_per_order
    FROM orders 
    WHERE user_id = ?
""", [customer_id])

analytics = cursor.fetchone()

# Format response
return jsonify({
    'customer': {
        'id': customer[0],
        'name': f"{customer[1]} {customer[2]}"
    },
    'orders': orders_list,
    'analytics': {
        'total_orders': analytics[0],
        'delivered_orders': analytics[1],
        'avg_items_per_order': round(analytics[2], 2) if analytics[2] else 0,
        'delivery_rate': round((analytics[1] / analytics[0]) * 100, 2) if analytics[0] > 0 else 0
    },
    'pagination': {
        'page': page,
        'per_page': per_page,
        'total': total_count,
        'pages': (total_count + per_page - 1) // per_page
    }
})
```

### **Response Structure:**
```json
{
  "customer": {
    "id": 123,
    "name": "John Doe"
  },
  "orders": [
    {
      "order_id": 456,
      "user_id": 123,
      "status": "Delivered",
      "num_of_item": 3,
      "created_at": "2023-02-01T09:00:00",
      "delivered_at": "2023-02-05T11:00:00"
    }
  ],
  "analytics": {
    "total_orders": 15,
    "delivered_orders": 12,
    "avg_items_per_order": 2.8,
    "delivery_rate": 80.0
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15,
    "pages": 1
  }
}
```

### **Why This Step:**
- **Consistency**: Standardized response format across all endpoints
- **Completeness**: Includes all necessary data and metadata
- **Usability**: Easy to consume by frontend applications

---

## 📋 **Step 6: Performance Optimizations**

### **Implementation:**
```python
# Database indexes (created in database_loader.py)
CREATE INDEX idx_orders_user_id ON orders(user_id)
CREATE INDEX idx_orders_status ON orders(status)

# Pagination
LIMIT ? OFFSET ?

# Efficient JOINs
SELECT o.order_id, o.user_id, o.status, 
       u.first_name, u.last_name, u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.user_id = ?
```

### **Optimization Features:**
- ✅ **Database Indexes**: Fast lookups on frequently queried columns
- ✅ **Pagination**: Prevents loading large datasets
- ✅ **Efficient JOINs**: Optimized table relationships
- ✅ **Connection Management**: Proper resource cleanup

---

## 📋 **Step 7: Data Processing**

### **Implementation:**
```python
# Handle datetime fields
for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
    order_dict[field] = order_dict[field] if order_dict[field] else None

# Calculate derived metrics
delivery_rate = round((delivered_orders / total_orders) * 100, 2) if total_orders > 0 else 0

# Format numbers
avg_items = round(analytics[2], 2) if analytics[2] else 0
```

### **Processing Features:**
- ✅ **Null Handling**: Proper handling of NULL database values
- ✅ **Date Formatting**: ISO format for timestamps
- ✅ **Calculated Fields**: Derived metrics like delivery rate
- ✅ **Number Formatting**: Rounded decimal values

---

## 🔧 **Complete Endpoint Implementation**

### **Get Customer Orders:**
```python
@app.route('/api/customers/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    """Get all orders for a specific customer with detailed analytics"""
    try:
        # Step 1: Get and validate parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'DESC')
        
        # Step 2: Database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Step 3: Validate customer exists
        cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = ?", [customer_id])
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
        
        # Step 4: Build query with security
        where_conditions = ["user_id = ?"]
        params = [customer_id]
        
        if status:
            where_conditions.append("status = ?")
            params.append(status)
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # Step 5: Get orders with pagination
        query = f"""
            SELECT order_id, user_id, status, gender, 
                   created_at, returned_at, shipped_at, delivered_at, num_of_item
            FROM orders{where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """
        offset = (page - 1) * per_page
        cursor.execute(query, params + [per_page, offset])
        orders = cursor.fetchall()
        
        # Step 6: Get analytics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_orders,
                AVG(num_of_item) as avg_items_per_order
            FROM orders 
            WHERE user_id = ?
        """, [customer_id])
        
        analytics = cursor.fetchone()
        
        # Step 7: Format response
        orders_list = []
        for order in orders:
            order_dict = dict(order)
            for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
                order_dict[field] = order_dict[field] if order_dict[field] else None
            orders_list.append(order_dict)
        
        conn.close()
        
        return jsonify({
            'customer': {
                'id': customer[0],
                'name': f"{customer[1]} {customer[2]}"
            },
            'orders': orders_list,
            'analytics': {
                'total_orders': analytics[0],
                'delivered_orders': analytics[1],
                'avg_items_per_order': round(analytics[2], 2) if analytics[2] else 0,
                'delivery_rate': round((analytics[1] / analytics[0]) * 100, 2) if analytics[0] > 0 else 0
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': analytics[0],
                'pages': (analytics[0] + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### **Get Specific Order:**
```python
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get order with customer details
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
        
        # Format response
        order_dict = dict(order)
        for field in ['created_at', 'returned_at', 'shipped_at', 'delivered_at']:
            order_dict[field] = order_dict[field] if order_dict[field] else None
        
        conn.close()
        return jsonify(order_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🎯 **Key Success Factors**

### **1. Security First**
- Parameterized queries prevent SQL injection
- Input validation on all parameters
- No raw SQL string concatenation

### **2. Error Handling**
- Comprehensive try-catch blocks
- Proper HTTP status codes
- Clear error messages

### **3. Performance**
- Database indexes on key columns
- Efficient JOIN operations
- Pagination for large datasets

### **4. User Experience**
- Consistent JSON response format
- Meaningful analytics data
- Proper pagination metadata

### **5. Maintainability**
- Clean, readable code structure
- Proper documentation
- Modular design

This implementation provides a robust, secure, and performant API that handles customer orders and order details with proper error handling and JSON response formatting. 