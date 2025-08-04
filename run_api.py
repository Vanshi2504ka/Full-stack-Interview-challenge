#!/usr/bin/env python3
"""
Script to run the RESTful API server
"""

from api import app

if __name__ == '__main__':
    print("🚀 Starting RESTful API Server")
    print("=" * 40)
    print("📊 Available endpoints:")
    print("  GET /health - Health check")
    print("  GET /api/customers - List all customers (with pagination)")
    print("  GET /api/customers/<id> - Get specific customer")
    print("  GET /api/orders - List all orders (with pagination)")
    print("  GET /api/orders/<id> - Get specific order")
    print("  GET /api/stats/overview - Overview statistics")
    print("  GET /api/stats/customers - Customer statistics")
    print("\n🔗 API will be available at: http://localhost:5000")
    print("📖 Example: http://localhost:5000/api/customers?page=1&per_page=10")
    print("\n" + "=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 