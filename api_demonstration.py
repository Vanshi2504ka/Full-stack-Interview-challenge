#!/usr/bin/env python3
"""
API Demonstration Script
Shows how to get customer orders and order details with proper error handling
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:5000"

def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_json_response(response, title):
    """Print formatted JSON response"""
    print(f"\n📋 {title}")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("\n📄 Response Body:")
    try:
        formatted_json = json.dumps(response.json(), indent=2)
        print(formatted_json)
    except json.JSONDecodeError:
        print(response.text)

def demonstrate_get_customer_orders():
    """Demonstrate getting all orders for a specific customer"""
    
    print_separator("GET ALL ORDERS FOR A SPECIFIC CUSTOMER")
    
    # Step 1: Test with valid customer ID
    print("\n🔍 Step 1: Get orders for customer ID 123 (Valid)")
    print("Endpoint: GET /api/customers/123/orders")
    
    try:
        response = requests.get(f"{BASE_URL}/api/customers/123/orders")
        print_json_response(response, "Customer Orders Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Found {len(data['orders'])} orders for customer {data['customer']['name']}")
            print(f"📊 Analytics: {data['analytics']['total_orders']} total orders, {data['analytics']['delivery_rate']}% delivery rate")
        else:
            print(f"❌ Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Step 2: Test with invalid customer ID
    print("\n🔍 Step 2: Get orders for customer ID 99999 (Invalid)")
    print("Endpoint: GET /api/customers/99999/orders")
    
    try:
        response = requests.get(f"{BASE_URL}/api/customers/99999/orders")
        print_json_response(response, "Invalid Customer Error Response")
        
        if response.status_code == 404:
            print("✅ Correctly handled: Customer not found error")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Step 3: Test with query parameters
    print("\n🔍 Step 3: Get orders with query parameters")
    print("Endpoint: GET /api/customers/123/orders?status=Delivered&page=1&per_page=5")
    
    try:
        params = {
            'status': 'Delivered',
            'page': 1,
            'per_page': 5,
            'sort_by': 'created_at',
            'sort_order': 'DESC'
        }
        response = requests.get(f"{BASE_URL}/api/customers/123/orders", params=params)
        print_json_response(response, "Filtered Customer Orders Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Filtered orders by status 'Delivered'")
            print(f"📊 Found {len(data['orders'])} delivered orders")
            print(f"📄 Pagination: Page {data['pagination']['page']} of {data['pagination']['pages']}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def demonstrate_get_specific_order():
    """Demonstrate getting specific order details"""
    
    print_separator("GET SPECIFIC ORDER DETAILS")
    
    # Step 1: Test with valid order ID
    print("\n🔍 Step 1: Get order ID 123 (Valid)")
    print("Endpoint: GET /api/orders/123")
    
    try:
        response = requests.get(f"{BASE_URL}/api/orders/123")
        print_json_response(response, "Order Details Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Order {data['order_id']} details retrieved")
            print(f"👤 Customer: {data['first_name']} {data['last_name']} ({data['email']})")
            print(f"📦 Status: {data['status']}")
            print(f"📍 Location: {data['city']}, {data['state']}, {data['country']}")
            print(f"📅 Created: {data['created_at']}")
            if data['delivered_at']:
                print(f"🚚 Delivered: {data['delivered_at']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Step 2: Test with invalid order ID
    print("\n🔍 Step 2: Get order ID 99999 (Invalid)")
    print("Endpoint: GET /api/orders/99999")
    
    try:
        response = requests.get(f"{BASE_URL}/api/orders/99999")
        print_json_response(response, "Invalid Order Error Response")
        
        if response.status_code == 404:
            print("✅ Correctly handled: Order not found error")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def demonstrate_error_handling():
    """Demonstrate various error scenarios"""
    
    print_separator("ERROR HANDLING DEMONSTRATION")
    
    # Test 1: Invalid customer ID format
    print("\n🔍 Test 1: Invalid customer ID format (string instead of number)")
    print("Endpoint: GET /api/customers/invalid")
    
    try:
        response = requests.get(f"{BASE_URL}/api/customers/invalid")
        print_json_response(response, "Invalid ID Format Error")
        
        if response.status_code == 404:
            print("✅ Correctly handled: Invalid ID format")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    # Test 2: Missing required parameters
    print("\n🔍 Test 2: Test health endpoint to verify API is running")
    print("Endpoint: GET /health")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_json_response(response, "Health Check Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy! Database: {data['database']}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API server is not running")
        print("💡 Start the server with: python run_api.py")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def explain_implementation_steps():
    """Explain how each step was implemented"""
    
    print_separator("IMPLEMENTATION EXPLANATION")
    
    print("""
🔧 **Step-by-Step Implementation Details:**

1. **Database Connection Setup**
   - Used `get_db_connection()` function
   - Enables `sqlite3.Row` for dictionary-like access
   - Proper connection cleanup with `conn.close()`

2. **Input Validation**
   - Validated customer_id parameter type (int)
   - Checked if customer exists before processing
   - Validated query parameters (page, per_page, status, etc.)

3. **Query Building with Security**
   - Used parameterized queries to prevent SQL injection
   - Built WHERE clauses dynamically based on filters
   - Validated sort parameters against allowed fields

4. **Error Handling Strategy**
   - Try-catch blocks around database operations
   - Specific error responses for different scenarios:
     * 404: Resource not found
     * 400: Bad request (invalid parameters)
     * 500: Internal server error
   - Proper HTTP status codes

5. **Response Formatting**
   - Consistent JSON structure across all endpoints
   - Proper datetime field handling (null vs ISO format)
   - Pagination metadata included
   - Analytics data calculated and included

6. **Performance Optimizations**
   - Database indexes on frequently queried columns
   - LIMIT/OFFSET for pagination
   - Efficient JOIN operations
   - Connection pooling ready

7. **Data Processing**
   - Converted database rows to dictionaries
   - Handled null values appropriately
   - Calculated derived metrics (delivery rate, etc.)
   - Formatted timestamps for JSON serialization
""")

def main():
    """Main demonstration function"""
    print("🚀 API Demonstration: Customer Orders & Order Details")
    print("This script demonstrates proper JSON responses and error handling")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ API server is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Please start the server with: python run_api.py")
        return
    
    # Run demonstrations
    demonstrate_get_customer_orders()
    demonstrate_get_specific_order()
    demonstrate_error_handling()
    explain_implementation_steps()
    
    print("\n🎉 Demonstration completed!")
    print("📚 Check the API documentation for more details")

if __name__ == "__main__":
    main() 