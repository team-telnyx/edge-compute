# Python Edge Function Examples

This directory contains comprehensive examples of edge functions written in Python, demonstrating various use cases and patterns for serverless computing with Telnyx Edge Compute.

## 🚀 Quick Start

```bash
# List available examples
make list

# Demo a specific example
make demo EXAMPLE=jwt-auth

# Run an example locally
make run EXAMPLE=restful-api


```

## 📋 Available Examples

### 1. **Webhook Receiver** (`webhook-receiver/`)
Generic webhook receiver with HMAC signature verification and multi-source support.

**Features:**
- HMAC-SHA256 signature verification
- Support for git, payment, and chat platform webhooks
- SQLite storage for webhook history
- Configurable via environment variables

**Endpoints:**
- `GET /` - API documentation
- `GET /webhooks` - List received webhooks  
- `POST /webhook` - Receive webhooks
- `POST /webhook/test` - Generate test webhook

### 2. **Data Processor** (`data-processor/`)
Batch data processing with CSV support and validation.

**Features:**
- CSV file processing and validation
- Batch operations with configurable size
- SQLite storage for processed data
- Error handling and reporting

**Endpoints:**
- `GET /` - API documentation
- `POST /process` - Process data batch
- `GET /results/{batch_id}` - Get processing results
- `GET /stats` - Processing statistics

### 3. **JSON Transformer** (`json-transformer/`)
Comprehensive JSON manipulation and transformation service.

**Features:**
- Case conversion (camelCase ↔ snake_case)
- JSON flattening with custom separators
- Advanced filtering with include/exclude rules
- Custom transformation rules
- Transformation history tracking

**Endpoints:**
- `GET /` - API documentation
- `POST /transform/camel-to-snake` - Case conversion
- `POST /transform/snake-to-camel` - Case conversion  
- `POST /transform/flatten` - Flatten nested JSON
- `POST /transform/filter` - Filter JSON data
- `GET /transformations` - Transformation history

### 4. **JWT Authentication** (`jwt-auth/`)
Complete JWT-based authentication and authorization service.

**Features:**
- JWT token generation and validation
- Role-based access control (RBAC)
- Token refresh mechanism
- Protected endpoints with middleware
- Demo users for testing

**Endpoints:**
- `GET /` - API documentation
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout
- `GET /auth/me` - Current user info
- `GET /protected` - Protected resource
- `GET /admin` - Admin-only resource

### 5. **RESTful API** (`restful-api/`)
Complete CRUD API for product management with advanced features.

**Features:**
- Full CRUD operations (Create, Read, Update, Delete)
- SQLite database with persistence
- Query filtering and search
- Pagination support
- Input validation and error handling
- Category management
- Statistics and reporting

**Endpoints:**
- `GET /` - API documentation
- `GET /health` - Database health check
- `GET /products` - List products (with filtering, pagination, search)
- `POST /products` - Create product
- `GET /products/{id}` - Get specific product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `GET /categories` - List categories
- `GET /stats` - Database statistics

## 🛠️ Development Workflow

### Using the Makefile

The included `Makefile` provides a convenient interface for common development tasks:

```bash
# Show all available commands
make help

# Build a specific example
make build EXAMPLE=webhook-receiver

# Run an example (builds if needed)
make run EXAMPLE=jwt-auth PORT=3000

# Run tests (builds and runs if needed)
make test EXAMPLE=restful-api

# View container logs
make logs EXAMPLE=background-jobs

# Open shell in running container
make shell EXAMPLE=data-processor

# Clean up (stop container and remove image)
make clean EXAMPLE=json-transformer

# Build all examples
make build-all

# Test all examples sequentially
make test-all

# Show running containers and images
make stats

# Nuclear cleanup (remove all containers and images)
make nuke
```

### Manual Docker Usage

If you prefer to work with Docker directly:

```bash
# Build an example
cd webhook-receiver
docker build -t my-webhook-receiver -f ../Dockerfile .

# Run the container
docker run -d -p 8080:8080 --name webhook-test my-webhook-receiver

# Run tests
./test.sh

# Test with deployed URL
FUNCTION_URL=https://my-function.dev.telnyxcompute.com ./test.sh
```

## 🏗️ Shared Infrastructure

All examples use a standardized Docker infrastructure:

### Dockerfile
- **Base Image**: `python:3.11-slim`
- **ASGI Server**: uvicorn for HTTP serving
- **Inline Wrapper**: Automatic ASGI wrapper generation
- **Port**: Container serves on port 8080

### Directory Structure
Each example follows this structure:
```
example-name/
├── function/
│   ├── __init__.py          # Import wrapper: from .func import new
│   └── func.py              # Main function implementation
├── func.toml                # Function configuration
├── pyproject.toml           # Python package configuration (name = "function")
├── test.sh                  # Comprehensive test script
└── README.md               # Example-specific documentation
```

### Environment Variables
Examples support configuration via environment variables:
- `DATABASE_PATH` - SQLite database location (default: `/tmp/{example}.db`)
- `FUNCTION_URL` - Base URL for testing (default: `http://localhost:8080`)
- Example-specific variables (JWT_SECRET, WEBHOOK_RECEIVER_SECRET, etc.)

### Security-Related Variables
- `DEBUG_MODE` - Enable verbose logging with sensitive data (**NEVER use in production**)
- `ENVIRONMENT` - Environment indicator (`development`/`production`) for security validations

## 🧪 Testing

Each example includes a comprehensive test script (`test.sh`) that:
- Tests all endpoints and functionality
- Includes error cases and edge conditions
- Supports both local and deployed testing
- Provides detailed output with response formatting
- Times requests and shows HTTP status codes

### Test Script Usage

```bash
# Test locally (default)
./test.sh

# Test deployed function
FUNCTION_URL=https://your-function.dev.telnyxcompute.com ./test.sh

# Run via Makefile
make test EXAMPLE=jwt-auth
```

## 📦 Dependencies

All examples are designed to minimize dependencies:
- **Core**: Python 3.11+ with standard library
- **HTTP Server**: uvicorn (automatically installed)
- **Database**: SQLite3 (built into Python)
- **Specific**: JWT example uses PyJWT library

Dependencies are declared in each example's `pyproject.toml`.

## 🔧 Configuration

### Function Configuration (`func.toml`)
```toml
[edge_compute]
func_id = "example-function-id"
func_name = "example-function-name"

# Environment variables can be configured via Telnyx Edge CLI:
# Set environment variables:
# DATABASE_PATH=/persistent/db.sqlite
# JWT_SECRET=your-secret-key
```

### Python Package Configuration (`pyproject.toml`)
```toml
[project]
name = "function"  # Must be "function" for Docker compatibility
description = "Function description"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = [
    # Runtime dependencies
]
```

## 🚀 Deployment

### Using Telnyx Edge CLI

```bash
# Create new function
# Create function from example

# Copy example code
cp -r webhook-receiver/function/* my-webhook-receiver/
cp webhook-receiver/func.toml my-webhook-receiver/
cp webhook-receiver/pyproject.toml my-webhook-receiver/

# Deploy
cd my-webhook-receiver
# Deploy function
```

### Environment Configuration

Set up secrets and configuration:
```bash
# Set environment variables:
DATABASE_PATH=/persistent/webhooks.db
JWT_SECRET=your-super-secret-jwt-key-change-in-production
WEBHOOK_RECEIVER_SECRET=your-webhook-secret
```

## 📚 Learning Path

**Beginner**: Start with `webhook-receiver` for basic HTTP handling
**Intermediate**: Try `restful-api` for CRUD operations and database work  
**Advanced**: Explore `jwt-auth` for security and `restful-api` for comprehensive CRUD operations

Each example builds on common patterns while demonstrating specific use cases.

## 🤝 Contributing

When adding new examples:
1. Follow the standard directory structure
2. Include comprehensive tests in `test.sh`
3. Use environment variables for configuration
4. Add your example to the `EXAMPLES` list in `Makefile`
5. Update this README with documentation

## 📖 Documentation Structure

This directory contains the **runnable code** for all Python examples. Each example has:

- **`function/func.py`** - Main implementation  
- **`test.sh`** - Comprehensive test suite
- **`README.md`** - Example-specific documentation
- **`func.toml`** - Function configuration
- **`pyproject.toml`** - Python package configuration

**Additional resources:**
- Each example has its own detailed README.md with implementation specifics
- See the main examples overview at [`../README.md`](../README.md)

## 📖 Additional Resources

- [Telnyx Edge Compute Documentation](https://docs.telnyx.com/edge-compute)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)
- [SQLite Python Tutorial](https://docs.python.org/3/library/sqlite3.html)