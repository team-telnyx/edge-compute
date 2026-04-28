# RESTful CRUD API

A complete RESTful API implementation with full CRUD operations built for Telnyx Edge Compute platform. This example demonstrates a production-ready product management API with SQLite backend, input validation, filtering, pagination, and comprehensive error handling.

## Features

- **Full CRUD Operations** - Create, Read, Update, Delete products
- **SQLite Database** - Persistent storage with automatic initialization
- **Input Validation** - Comprehensive data validation and error handling
- **Filtering & Search** - Advanced query capabilities with multiple filters
- **Pagination** - Efficient data retrieval for large datasets
- **Sorting** - Flexible sorting by multiple fields and directions
- **Category Management** - Product categorization with statistics
- **RESTful Design** - Follows REST principles and HTTP conventions
- **Sample Data** - Pre-loaded with example products for testing

## ⚠️ Database Persistence

**Important**: This example uses SQLite for data storage. In a serverless environment like Telnyx Edge Compute:

- **Local Development**: Data persists between container restarts when using Docker volumes
- **Production Deployment**: Data is **ephemeral** and will be lost when the function scales to zero or restarts
- **Recommendation**: For production use, integrate with external databases (PostgreSQL, MySQL) or use Telnyx's managed storage services

See the [Environment Variables](#environment-variables) section for configuring external database connections.

## API Endpoints

### Product Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | List products with filtering, search, and pagination |
| POST | `/products` | Create a new product |
| GET | `/products/{id}` | Get specific product by ID |
| PUT | `/products/{id}` | Update existing product |
| DELETE | `/products/{id}` | Delete product by ID |

### System & Information

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API information and documentation |
| GET | `/health` | Health check and database status |
| GET | `/categories` | List product categories with counts |
| GET | `/stats` | Database statistics and metrics |

## Data Model

### Product Schema

```json
{
  "id": "uuid",
  "name": "string (required)",
  "description": "string",
  "price": "number (required, positive)",
  "category": "string",
  "stock_quantity": "integer (non-negative)",
  "active": "boolean",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Environment Variables

Configure database behavior:

**Environment Variables:**
- `DATABASE_PATH` - Database file location (optional, defaults to in-memory)

## Usage Examples

### Create Product

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Headphones",
    "description": "High-quality noise-canceling headphones",
    "price": 199.99,
    "category": "Electronics",
    "stock_quantity": 25,
    "active": true
  }'
```

Response:
```json
{
  "message": "Product created successfully",
  "product": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Wireless Headphones",
    "description": "High-quality noise-canceling headphones",
    "price": 199.99,
    "category": "Electronics",
    "stock_quantity": 25,
    "active": true,
    "created_at": "2024-01-01T12:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  }
}
```

### List Products

```bash
# List all products
curl https://your-function.dev.telnyxcompute.com/products

# List with pagination
curl "https://your-function.dev.telnyxcompute.com/products?limit=10&offset=0"

# Filter by category
curl "https://your-function.dev.telnyxcompute.com/products?category=Electronics"

# Search products
curl "https://your-function.dev.telnyxcompute.com/products?search=laptop"

# Filter active products
curl "https://your-function.dev.telnyxcompute.com/products?active=true"

# Sort by price (ascending)
curl "https://your-function.dev.telnyxcompute.com/products?sort=price&order=asc"

# Complex query with multiple filters
curl "https://your-function.dev.telnyxcompute.com/products?category=Electronics&active=true&sort=price&order=desc&limit=5"
```

### Get Product

```bash
curl https://your-function.dev.telnyxcompute.com/products/550e8400-e29b-41d4-a716-446655440000
```

### Update Product

```bash
# Partial update - only specified fields are updated
curl -X PUT https://your-function.dev.telnyxcompute.com/products/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 179.99,
    "stock_quantity": 30,
    "description": "Premium noise-canceling wireless headphones"
  }'
```

### Delete Product

```bash
curl -X DELETE https://your-function.dev.telnyxcompute.com/products/550e8400-e29b-41d4-a716-446655440000
```

## Query Parameters

### List Products Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | `?category=Electronics` |
| `search` | string | Search in name/description | `?search=laptop` |
| `active` | boolean | Filter by active status | `?active=true` |
| `limit` | integer | Max results (1-100) | `?limit=20` |
| `offset` | integer | Skip results | `?offset=10` |
| `sort` | string | Sort field | `?sort=price` |
| `order` | string | Sort direction (asc/desc) | `?order=desc` |

### Available Sort Fields
- `name` - Product name
- `price` - Product price  
- `created_at` - Creation date (default)
- `updated_at` - Last modified date
- `category` - Category name

## Sample Data

The API comes pre-loaded with sample products:

- **MacBook Pro** - High-performance laptop ($2499.99, Electronics)
- **iPhone 15** - Latest smartphone ($999.99, Electronics)  
- **Python Programming** - Programming book ($49.99, Books)
- **Ergonomic Office Chair** - Comfortable chair ($299.99, Furniture)
- **Premium Coffee Beans** - Single-origin coffee ($24.99, Food)

## System Information

### Health Check

```bash
curl https://your-function.dev.telnyxcompute.com/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "database": {
    "status": "connected",
    "path": ":memory:",
    "total_products": 15,
    "active_products": 12
  },
  "version": "1.0.0"
}
```

### Category Statistics

```bash
curl https://your-function.dev.telnyxcompute.com/categories
```

Response:
```json
{
  "categories": [
    {"name": "Electronics", "product_count": 8},
    {"name": "Books", "product_count": 3},
    {"name": "Furniture", "product_count": 2},
    {"name": "Food", "product_count": 2}
  ],
  "total_categories": 4
}
```

### Database Statistics

```bash
curl https://your-function.dev.telnyxcompute.com/stats
```

Response:
```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "products": {
    "total": 15,
    "active": 12,
    "inactive": 3
  },
  "categories": {
    "Electronics": 8,
    "Books": 3,
    "Furniture": 2,
    "Food": 2
  },
  "pricing": {
    "average_price": 324.99,
    "min_price": 24.99,
    "max_price": 2499.99,
    "total_inventory_value": 15749.50
  },
  "recent_activity": {
    "products_added_last_7_days": 5
  }
}
```

## Error Handling

The API provides detailed error responses with appropriate HTTP status codes:

### 400 Bad Request
```json
{
  "error": "Missing required field",
  "message": "Field 'name' is required"
}
```

### 404 Not Found
```json
{
  "error": "Product not found",
  "message": "Product with ID 550e8400-e29b-41d4-a716-446655440000 does not exist"
}
```

### 405 Method Not Allowed
```json
{
  "error": "Method not allowed",
  "message": "Allowed methods: GET, POST"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create product",
  "message": "Database connection error"
}
```

## Input Validation

### Product Creation/Update Rules
- **name**: Required, non-empty string
- **price**: Required, positive number
- **description**: Optional string
- **category**: Optional string (defaults to "General")
- **stock_quantity**: Optional non-negative integer (defaults to 0)
- **active**: Optional boolean (defaults to true)

### Query Parameter Validation
- **limit**: Integer between 1-100 (defaults to 50)
- **offset**: Non-negative integer (defaults to 0)
- **sort**: Must be valid field name
- **order**: Must be "asc" or "desc"

## Development

### Local Testing

```bash
# Install dependencies
pip install -e ".[dev]"

# Run comprehensive tests
chmod +x test.sh
./test.sh
```

**Deployable on Telnyx Edge Compute**

## Architecture

### Database Design
- **SQLite**: Lightweight, serverless database
- **Single Table**: Products table with all attributes
- **Indexes**: Automatic indexing on primary key and common query fields
- **Timestamps**: Automatic creation and update tracking

### API Design Principles
- **RESTful**: Standard HTTP methods and status codes
- **Stateless**: No server-side session management
- **JSON**: Consistent JSON request/response format
- **CORS**: Cross-origin resource sharing enabled
- **Pagination**: Limit/offset pagination for scalability

## Performance Considerations

- **Database**: In-memory for speed, file-based for persistence
- **Pagination**: Default 50 items per page, max 100
- **Indexes**: Automatic SQLite indexing on primary keys
- **Query Optimization**: Efficient SQL queries with proper filtering
- **Memory**: Lightweight implementation suitable for edge environments

## Common Use Cases

- **E-commerce Backend** - Product catalog management
- **Inventory Management** - Stock tracking and updates
- **Content Management** - Article/content CRUD operations
- **User Management** - User profile management (adapt schema)
- **Configuration API** - Application settings management
- **Catalog Service** - Product/service catalog for other services

## Production Considerations

- **Database Location**: Use file-based SQLite for persistence across restarts
- **Input Sanitization**: Additional input validation for production data
- **Rate Limiting**: Consider implementing rate limiting for high-traffic scenarios
- **Logging**: Enhanced logging for production monitoring
- **Backup**: Regular database backups for data protection
- **Authentication**: Add authentication/authorization as needed

This example provides a solid foundation for building production-ready RESTful APIs with complete CRUD functionality in edge computing environments.