# RESTful API Documentation

## Overview
This RESTful API provides access to customer data and order statistics from the ecommerce database. The API includes pagination, filtering, and comprehensive statistics endpoints.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Load Data (if not already done)
```bash
python database_loader.py
```

### 3. Start the API Server
```bash
python run_api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns API status and database connection info

### Customer Endpoints

#### List All Customers (with pagination)
- **GET** `/api/customers`
- **Query Parameters:**
  - `page` (optional): Page number (default: 1)
  - `per_page` (optional): Items per page, max 100 (default: 20)
  - `search` (optional): Search in name or email
  - `city` (optional): Filter by city
  - `gender` (optional): Filter by gender (M/F)

**Example:**
```bash
# Get first 10 customers
curl "http://localhost:5000/api/customers?page=1&per_page=10"

# Search for customers in a specific city
curl "http://localhost:5000/api/customers?city=New York&page=1&per_page=20"

# Search by name or email
curl "http://localhost:5000/api/customers?search=john&page=1&per_page=10"
```

**Response:**
```json
{
  "customers": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "age": 30,
      "gender": "M",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "created_at": "2023-01-15T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100000,
    "pages": 10000
  }
}
```

#### Get Specific Customer
- **GET** `/api/customers/{customer_id}`
- Returns detailed customer information including their orders

**Example:**
```bash
curl "http://localhost:5000/api/customers/123"
```

### Order Endpoints

#### List All Orders (with pagination)
- **GET** `/api/orders`
- **Query Parameters:**
  - `page` (optional): Page number (default: 1)
  - `per_page` (optional): Items per page, max 100 (default: 20)
  - `status` (optional): Filter by order status
  - `user_id` (optional): Filter by customer ID

**Example:**
```bash
# Get all delivered orders
curl "http://localhost:5000/api/orders?status=Delivered&page=1&per_page=20"

# Get orders for a specific customer
curl "http://localhost:5000/api/orders?user_id=123&page=1&per_page=10"
```

#### Get Specific Order
- **GET** `/api/orders/{order_id}`
- Returns detailed order information with customer details

### Statistics Endpoints

#### Overview Statistics
- **GET** `/api/stats/overview`
- Returns high-level statistics about customers and orders

**Response:**
```json
{
  "total_customers": 100000,
  "total_orders": 50000,
  "status_distribution": {
    "Delivered": 25000,
    "Cancelled": 15000,
    "Shipped": 8000,
    "Pending": 2000
  },
  "average_items_per_order": 2.45,
  "top_cities": [
    {"city": "New York", "count": 5000},
    {"city": "Los Angeles", "count": 3000}
  ]
}
```

#### Customer Statistics
- **GET** `/api/stats/customers`
- Returns detailed customer analytics

**Response:**
```json
{
  "gender_distribution": {
    "M": 52000,
    "F": 48000
  },
  "age_distribution": [
    {"age_group": "18-24", "count": 15000},
    {"age_group": "25-34", "count": 25000}
  ],
  "traffic_sources": [
    {"traffic_source": "google", "count": 30000},
    {"traffic_source": "facebook", "count": 20000}
  ],
  "top_customers": [
    {
      "first_name": "John",
      "last_name": "Smith",
      "email": "john.smith@example.com",
      "order_count": 15
    }
  ]
}
```

## Web Interface

A web-based customer viewer is available at `http://localhost:5000/customer_viewer.html` (you can open the HTML file directly in your browser).

Features:
- Real-time search and filtering
- Pagination controls
- Statistics display
- Responsive design

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **404**: Resource not found
- **500**: Internal server error

Error responses include a message:
```json
{
  "error": "Customer not found"
}
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (starts from 1)
- `per_page`: Number of items per page (max 100)

The response includes pagination metadata:
```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100000,
    "pages": 5000
  }
}
```

## Filtering and Search

### Customer Filters
- **search**: Searches in first_name, last_name, and email fields
- **city**: Filters by city (partial match)
- **gender**: Filters by gender (M/F)

### Order Filters
- **status**: Filters by order status
- **user_id**: Filters by customer ID

## Performance Considerations

- Database indexes are created on frequently queried columns
- Pagination limits prevent large result sets
- Maximum 100 items per page to maintain performance
- Efficient SQL queries with proper JOINs

## Database Schema

The API works with the existing database schema:

### Users Table
- `id`, `first_name`, `last_name`, `email`, `age`, `gender`
- `state`, `street_address`, `postal_code`, `city`, `country`
- `latitude`, `longitude`, `traffic_source`, `created_at`

### Orders Table
- `order_id`, `user_id`, `status`, `gender`
- `created_at`, `returned_at`, `shipped_at`, `delivered_at`
- `num_of_item`

## Example Usage

### Using curl
```bash
# Get customers with pagination
curl "http://localhost:5000/api/customers?page=1&per_page=10"

# Search for customers
curl "http://localhost:5000/api/customers?search=john&city=New York"

# Get statistics
curl "http://localhost:5000/api/stats/overview"
```

### Using JavaScript/Fetch
```javascript
// Get customers
const response = await fetch('/api/customers?page=1&per_page=20');
const data = await response.json();
console.log(data.customers);

// Search customers
const searchResponse = await fetch('/api/customers?search=john&gender=M');
const searchData = await searchResponse.json();
console.log(searchData.customers);
```

### Using Python requests
```python
import requests

# Get customers
response = requests.get('http://localhost:5000/api/customers', params={
    'page': 1,
    'per_page': 20,
    'city': 'New York'
})
customers = response.json()['customers']

# Get statistics
stats_response = requests.get('http://localhost:5000/api/stats/overview')
stats = stats_response.json()
print(f"Total customers: {stats['total_customers']}")
```

## Troubleshooting

1. **Database not found**: Run `python database_loader.py` first
2. **Port already in use**: Change the port in `run_api.py`
3. **CORS issues**: The API includes CORS headers for web access
4. **Large datasets**: Use pagination to avoid timeout issues

## Development

To extend the API:
1. Add new endpoints in `api.py`
2. Update the documentation
3. Test with the provided HTML interface
4. Consider adding authentication for production use 