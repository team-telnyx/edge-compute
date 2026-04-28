# RESTful CRUD API Function
import logging
import json
import sqlite3
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import parse_qs

# Constants
HTTP_SCOPE_TYPE = 'http'


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return RestfulAPI()


class RestfulAPI:
    def __init__(self):
        """ Initialize the RESTful API with SQLite database.
        """
        self.db_path = os.getenv('DATABASE_PATH', '/tmp/api.db')
        self._init_database()

    def _init_database(self):
        """ Initialize SQLite database with products table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                stock_quantity INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create some sample data if table is empty
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ('MacBook Pro', 'High-performance laptop for developers', 2499.99, 'Electronics', 15, 1),
                ('iPhone 15', 'Latest smartphone with advanced camera', 999.99, 'Electronics', 25, 1),
                ('Python Programming', 'Comprehensive guide to Python development', 49.99, 'Books', 100, 1),
                ('Ergonomic Office Chair', 'Comfortable chair for long work sessions', 299.99, 'Furniture', 8, 1),
                ('Premium Coffee Beans', 'Single-origin arabica coffee beans', 24.99, 'Food', 50, 1)
            ]
            
            for product in sample_products:
                product_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO products (id, name, description, price, category, stock_quantity, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product_id, *product))

        conn.commit()
        conn.close()
        logging.info("Database initialized with sample products")

    def _get_db_connection(self):
        """ Get database connection.
        """
        return sqlite3.connect(self.db_path)

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this RESTful API.
        """
        # Validate ASGI scope for HTTP requests
        scope_request_type = scope.get('type')
        if scope_request_type is None or scope_request_type != HTTP_SCOPE_TYPE:
            logging.error("Invalid ASGI scope type: %s", scope_request_type)
            await send({
                'type': 'http.response.start',
                'status': 400,
                'headers': [[b'content-type', b'application/json']],
            })
            await send({
                'type': 'http.response.body',
                'body': json.dumps({"error": "Invalid request type"}).encode(),
            })
            return

        method = scope.get('method', 'GET')
        path = scope.get('path', '/')
        query_string = scope.get('query_string', b'').decode('utf-8')

        # Route handling
        if method == 'GET' and path == '/':
            await self._handle_info(send)
        elif method == 'GET' and path == '/health':
            await self._handle_health(send)
        elif path == '/products':
            if method == 'GET':
                await self._handle_list_products(query_string, send)
            elif method == 'POST':
                await self._handle_create_product(scope, receive, send)
            else:
                await self._handle_405(send, ['GET', 'POST'])
        elif path.startswith('/products/'):
            product_id = path.split('/')[-1]
            if method == 'GET':
                await self._handle_get_product(product_id, send)
            elif method == 'PUT':
                await self._handle_update_product(product_id, scope, receive, send)
            elif method == 'DELETE':
                await self._handle_delete_product(product_id, send)
            else:
                await self._handle_405(send, ['GET', 'PUT', 'DELETE'])
        elif path == '/categories':
            if method == 'GET':
                await self._handle_list_categories(send)
            else:
                await self._handle_405(send, ['GET'])
        elif path == '/stats':
            if method == 'GET':
                await self._handle_stats(send)
            else:
                await self._handle_405(send, ['GET'])
        else:
            await self._handle_404(send)

    async def _handle_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "RESTful CRUD API",
            "version": "1.0.0",
            "description": "Complete CRUD API for product management with SQLite backend",
            "endpoints": [
                "GET  / - API information",
                "GET  /health - Health check and database status",
                "GET  /products - List products with filtering and pagination",
                "POST /products - Create a new product",
                "GET  /products/{id} - Get specific product by ID",
                "PUT  /products/{id} - Update existing product",
                "DELETE /products/{id} - Delete product by ID",
                "GET  /categories - List product categories",
                "GET  /stats - Get database statistics"
            ],
            "features": [
                "Full CRUD operations (Create, Read, Update, Delete)",
                "SQLite database with persistence",
                "Query filtering and search",
                "Pagination support",
                "Input validation",
                "Error handling",
                "Category management",
                "Statistics and reporting"
            ],
            "query_parameters": {
                "category": "Filter by category",
                "search": "Search in name and description",
                "active": "Filter by active status (true/false)",
                "limit": "Limit number of results (max 100)",
                "offset": "Skip number of results for pagination",
                "sort": "Sort field (name, price, created_at)",
                "order": "Sort order (asc/desc)"
            }
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_health(self, send):
        """ Handle health check endpoint.
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Check database connectivity
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
            active_products = cursor.fetchone()[0]
            
            conn.close()

            health_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": {
                    "status": "connected",
                    "path": self.db_path,
                    "total_products": total_products,
                    "active_products": active_products
                },
                "version": "1.0.0"
            }

            await self._send_json_response(send, 200, health_data)

        except Exception as e:
            await self._send_json_response(send, 503, {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _handle_list_products(self, query_string: str, send):
        """ Handle listing products with filtering and pagination.
        """
        try:
            # Parse query parameters
            params = parse_qs(query_string) if query_string else {}
            
            # Extract parameters
            category = params.get('category', [None])[0]
            search = params.get('search', [None])[0]
            active = params.get('active', [None])[0]
            limit = min(int(params.get('limit', ['50'])[0]), 100)
            offset = max(int(params.get('offset', ['0'])[0]), 0)
            sort_field = params.get('sort', ['created_at'])[0]
            sort_order = params.get('order', ['desc'])[0].upper()

            # Validate sort parameters
            valid_sort_fields = ['name', 'price', 'created_at', 'updated_at', 'category']
            if sort_field not in valid_sort_fields:
                sort_field = 'created_at'
            
            if sort_order not in ['ASC', 'DESC']:
                sort_order = 'DESC'

            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Build query with filters
            query = 'SELECT * FROM products WHERE 1=1'
            query_params = []

            if category:
                query += ' AND LOWER(category) = LOWER(?)'
                query_params.append(category)

            if search:
                query += ' AND (LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))'
                search_term = f'%{search}%'
                query_params.extend([search_term, search_term])

            if active is not None:
                active_val = active.lower() in ['true', '1', 'yes']
                query += ' AND active = ?'
                query_params.append(1 if active_val else 0)

            # Add sorting and pagination
            query += f' ORDER BY {sort_field} {sort_order} LIMIT ? OFFSET ?'
            query_params.extend([limit, offset])

            cursor.execute(query, query_params)
            rows = cursor.fetchall()

            # Get total count for pagination
            count_query = 'SELECT COUNT(*) FROM products WHERE 1=1'
            count_params = []
            
            if category:
                count_query += ' AND LOWER(category) = LOWER(?)'
                count_params.append(category)
            
            if search:
                count_query += ' AND (LOWER(name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))'
                search_term = f'%{search}%'
                count_params.extend([search_term, search_term])
            
            if active is not None:
                active_val = active.lower() in ['true', '1', 'yes']
                count_query += ' AND active = ?'
                count_params.append(1 if active_val else 0)

            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]

            conn.close()

            # Format products
            products = []
            for row in rows:
                products.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3],
                    'category': row[4],
                    'stock_quantity': row[5],
                    'active': bool(row[6]),
                    'created_at': row[7],
                    'updated_at': row[8]
                })

            response_data = {
                'products': products,
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'category': category,
                    'search': search,
                    'active': active,
                    'sort': sort_field,
                    'order': sort_order.lower()
                }
            }

            await self._send_json_response(send, 200, response_data)

        except Exception as e:
            logging.error(f"List products error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to list products",
                "message": str(e)
            })

    async def _handle_create_product(self, scope, receive, send):
        """ Handle creating a new product.
        """
        try:
            body = await self._read_request_body(receive)
            product_data = json.loads(body.decode('utf-8'))

            # Validate required fields
            required_fields = ['name', 'price']
            for field in required_fields:
                if field not in product_data or not product_data[field]:
                    await self._send_json_response(send, 400, {
                        "error": "Missing required field",
                        "message": f"Field '{field}' is required"
                    })
                    return

            # Validate data types
            try:
                price = float(product_data['price'])
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except (ValueError, TypeError):
                await self._send_json_response(send, 400, {
                    "error": "Invalid price",
                    "message": "Price must be a positive number"
                })
                return

            # Generate product ID
            product_id = str(uuid.uuid4())

            # Extract and validate fields
            name = product_data['name'].strip()
            description = product_data.get('description', '').strip()
            category = product_data.get('category', 'General').strip()
            stock_quantity = max(int(product_data.get('stock_quantity', 0)), 0)
            active = bool(product_data.get('active', True))

            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO products (id, name, description, price, category, stock_quantity, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_id, name, description, price, category, stock_quantity, active))

            conn.commit()
            conn.close()

            # Return created product
            created_product = {
                'id': product_id,
                'name': name,
                'description': description,
                'price': price,
                'category': category,
                'stock_quantity': stock_quantity,
                'active': active,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }

            await self._send_json_response(send, 201, {
                'message': 'Product created successfully',
                'product': created_product
            })

        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must be valid JSON"
            })
        except Exception as e:
            logging.error(f"Create product error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to create product",
                "message": str(e)
            })

    async def _handle_get_product(self, product_id: str, send):
        """ Handle getting a specific product by ID.
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                await self._send_json_response(send, 404, {
                    "error": "Product not found",
                    "message": f"Product with ID {product_id} does not exist"
                })
                return

            product = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'category': row[4],
                'stock_quantity': row[5],
                'active': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            }

            await self._send_json_response(send, 200, {'product': product})

        except Exception as e:
            logging.error(f"Get product error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to get product",
                "message": str(e)
            })

    async def _handle_update_product(self, product_id: str, scope, receive, send):
        """ Handle updating an existing product.
        """
        try:
            # Check if product exists
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            existing_product = cursor.fetchone()
            
            if not existing_product:
                conn.close()
                await self._send_json_response(send, 404, {
                    "error": "Product not found",
                    "message": f"Product with ID {product_id} does not exist"
                })
                return

            body = await self._read_request_body(receive)
            update_data = json.loads(body.decode('utf-8'))

            # Build update query dynamically
            update_fields = []
            update_params = []

            # Validate and add fields to update
            if 'name' in update_data:
                name = update_data['name'].strip()
                if not name:
                    conn.close()
                    await self._send_json_response(send, 400, {
                        "error": "Invalid name",
                        "message": "Name cannot be empty"
                    })
                    return
                update_fields.append('name = ?')
                update_params.append(name)

            if 'description' in update_data:
                update_fields.append('description = ?')
                update_params.append(update_data['description'].strip())

            if 'price' in update_data:
                try:
                    price = float(update_data['price'])
                    if price < 0:
                        raise ValueError("Price cannot be negative")
                    update_fields.append('price = ?')
                    update_params.append(price)
                except (ValueError, TypeError):
                    conn.close()
                    await self._send_json_response(send, 400, {
                        "error": "Invalid price",
                        "message": "Price must be a positive number"
                    })
                    return

            if 'category' in update_data:
                update_fields.append('category = ?')
                update_params.append(update_data['category'].strip())

            if 'stock_quantity' in update_data:
                try:
                    stock = max(int(update_data['stock_quantity']), 0)
                    update_fields.append('stock_quantity = ?')
                    update_params.append(stock)
                except (ValueError, TypeError):
                    conn.close()
                    await self._send_json_response(send, 400, {
                        "error": "Invalid stock quantity",
                        "message": "Stock quantity must be a non-negative integer"
                    })
                    return

            if 'active' in update_data:
                update_fields.append('active = ?')
                update_params.append(bool(update_data['active']))

            if not update_fields:
                conn.close()
                await self._send_json_response(send, 400, {
                    "error": "No fields to update",
                    "message": "At least one field must be provided for update"
                })
                return

            # Add updated_at timestamp
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_params.append(product_id)

            # Execute update
            update_query = f'UPDATE products SET {", ".join(update_fields)} WHERE id = ?'
            cursor.execute(update_query, update_params)
            conn.commit()

            # Get updated product
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            updated_row = cursor.fetchone()
            conn.close()

            updated_product = {
                'id': updated_row[0],
                'name': updated_row[1],
                'description': updated_row[2],
                'price': updated_row[3],
                'category': updated_row[4],
                'stock_quantity': updated_row[5],
                'active': bool(updated_row[6]),
                'created_at': updated_row[7],
                'updated_at': updated_row[8]
            }

            await self._send_json_response(send, 200, {
                'message': 'Product updated successfully',
                'product': updated_product
            })

        except json.JSONDecodeError:
            await self._send_json_response(send, 400, {
                "error": "Invalid JSON",
                "message": "Request body must be valid JSON"
            })
        except Exception as e:
            logging.error(f"Update product error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to update product",
                "message": str(e)
            })

    async def _handle_delete_product(self, product_id: str, send):
        """ Handle deleting a product by ID.
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if product exists
            cursor.execute('SELECT name FROM products WHERE id = ?', (product_id,))
            existing_product = cursor.fetchone()

            if not existing_product:
                conn.close()
                await self._send_json_response(send, 404, {
                    "error": "Product not found",
                    "message": f"Product with ID {product_id} does not exist"
                })
                return

            product_name = existing_product[0]

            # Delete the product
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            conn.close()

            await self._send_json_response(send, 200, {
                'message': 'Product deleted successfully',
                'deleted_product': {
                    'id': product_id,
                    'name': product_name
                }
            })

        except Exception as e:
            logging.error(f"Delete product error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to delete product",
                "message": str(e)
            })

    async def _handle_list_categories(self, send):
        """ Handle listing all product categories.
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM products 
                GROUP BY category 
                ORDER BY category
            ''')
            rows = cursor.fetchall()
            conn.close()

            categories = []
            for row in rows:
                categories.append({
                    'name': row[0],
                    'product_count': row[1]
                })

            await self._send_json_response(send, 200, {
                'categories': categories,
                'total_categories': len(categories)
            })

        except Exception as e:
            logging.error(f"List categories error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to list categories",
                "message": str(e)
            })

    async def _handle_stats(self, send):
        """ Handle getting database statistics.
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Get basic counts
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
            active_products = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM products WHERE active = 0')
            inactive_products = cursor.fetchone()[0]

            # Get category distribution
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM products 
                GROUP BY category 
                ORDER BY count DESC
            ''')
            category_stats = dict(cursor.fetchall())

            # Get price statistics
            cursor.execute('''
                SELECT 
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    SUM(price * stock_quantity) as total_inventory_value
                FROM products 
                WHERE active = 1
            ''')
            price_stats = cursor.fetchone()

            # Get recent activity (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM products 
                WHERE created_at > datetime('now', '-7 days')
            ''')
            recent_products = cursor.fetchone()[0]

            conn.close()

            stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'products': {
                    'total': total_products,
                    'active': active_products,
                    'inactive': inactive_products
                },
                'categories': category_stats,
                'pricing': {
                    'average_price': round(price_stats[0], 2) if price_stats[0] else 0,
                    'min_price': price_stats[1] if price_stats[1] else 0,
                    'max_price': price_stats[2] if price_stats[2] else 0,
                    'total_inventory_value': round(price_stats[3], 2) if price_stats[3] else 0
                },
                'recent_activity': {
                    'products_added_last_7_days': recent_products
                }
            }

            await self._send_json_response(send, 200, stats)

        except Exception as e:
            logging.error(f"Stats error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to get stats",
                "message": str(e)
            })

    async def _read_request_body(self, receive):
        """ Read and return request body.
        """
        body = b''
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body

    async def _handle_404(self, send):
        """ Handle 404 responses.
        """
        await self._send_json_response(send, 404, {
            "error": "Not found",
            "message": "Endpoint not found"
        })

    async def _handle_405(self, send, allowed_methods: List[str]):
        """ Handle 405 Method Not Allowed responses.
        """
        await send({
            'type': 'http.response.start',
            'status': 405,
            'headers': [
                [b'content-type', b'application/json'],
                [b'allow', ', '.join(allowed_methods).encode()],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps({
                "error": "Method not allowed",
                "message": f"Allowed methods: {', '.join(allowed_methods)}"
            }).encode(),
        })

    async def _send_json_response(self, send, status: int, data: Dict[str, Any]):
        """ Send JSON response.
        """
        response_body = json.dumps(data, indent=2, default=str)

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'access-control-allow-origin', b'*'],
                [b'access-control-allow-methods', b'GET, POST, PUT, DELETE, OPTIONS'],
                [b'access-control-allow-headers', b'Content-Type'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the RESTful API.
        """
        logging.info("RESTful CRUD API starting")
        
        # Load configuration from environment
        self.db_path = cfg.get('DATABASE_PATH', self.db_path)
        
        # Initialize database if needed
        self._init_database()
        
        # Warn about ephemeral storage in serverless environments
        if self.db_path.startswith('/tmp'):
            logging.warning("⚠️ Database is stored in /tmp - data will be lost on container restart")
            logging.warning("⚠️ For production, consider using external database or persistent storage")
        
        logging.info(f"API started with database: {self.db_path}")

    def stop(self):
        """ Stop the RESTful API.
        """
        logging.info("RESTful CRUD API stopping")