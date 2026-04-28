# Middleware Patterns - Go Example

This example demonstrates how to implement and chain middleware in Go for HTTP request processing. Middleware provides a powerful pattern for adding cross-cutting concerns like logging, authentication, error handling, and CORS to your web applications.

## What You'll Learn

- **Middleware Chain Pattern**: How to create composable middleware that can be chained together
- **Request Context**: How to pass data through the middleware chain using Go's context
- **Authentication Middleware**: Bearer token validation with route exceptions
- **Logging Middleware**: Request ID generation, timing, and structured logging
- **Recovery Middleware**: Panic handling to prevent server crashes
- **CORS Middleware**: Cross-origin request handling
- **Separation of Concerns**: Each middleware handles one specific responsibility

## Middleware Components

### 1. Logging Middleware
- Generates unique request IDs for tracking
- Logs request start and completion with timing
- Adds request context for downstream handlers

### 2. Authentication Middleware
- Validates Bearer tokens in Authorization headers
- Provides route exceptions (e.g., health checks)
- Adds user information to request context

### 3. Recovery Middleware
- Catches panics and prevents server crashes
- Returns appropriate HTTP 500 responses
- Logs panic details for debugging

### 4. CORS Middleware
- Sets appropriate CORS headers
- Handles OPTIONS preflight requests
- Enables cross-origin API access

## Architecture

```
Request → Recovery → Logger → CORS → Auth → Handler
```

The middleware chain wraps the main handler, with each middleware:
1. Receiving the request
2. Performing its specific function
3. Calling the next handler in the chain
4. Optionally processing the response

## Environment Variables

```bash
# Authentication
AUTH_TOKEN="demo-token"          # Bearer token for auth middleware

# Optional
LOG_LEVEL="info"                 # Logging level
REQUEST_TIMEOUT="30s"            # Request timeout
DEBUG_MODE="false"               # Enable verbose logging
```

## Testing

The test suite demonstrates all middleware patterns:

```bash
make test EXAMPLE=middleware-patterns
```

### Test Coverage

- **Logging Middleware** (3 tests): Request ID generation, timestamps, duration tracking
- **Authentication Middleware** (4 tests): Token validation, protected endpoints, context injection
- **Health Check Bypass** (2 tests): Route exceptions in auth middleware
- **CORS Middleware** (2 tests): Header setting, preflight handling
- **Recovery Middleware** (1 test): Panic handling and graceful degradation
- **POST Request Handling** (2 tests): Body processing through middleware chain
- **Middleware Chain Order** (2 tests): Proper composition and execution order

## Key Go Concepts Demonstrated

### Middleware Type
```go
type Middleware func(http.Handler) http.Handler
```

### Context Passing
```go
ctx := context.WithValue(r.Context(), "requestID", requestID)
```

### Chain Composition
```go
func ApplyMiddleware(h http.Handler, middleware ...Middleware) http.Handler
```

### Handler Pattern
```go
func Handle(w http.ResponseWriter, r *http.Request) {
    // Apply middleware chain
    handler := ApplyMiddleware(baseHandler, Recovery(), Logger(), CORS(), Auth(token))
    handler.ServeHTTP(w, r)
}
```

## Production Considerations

- **Token Management**: Use secure token generation and validation
- **Rate Limiting**: Add rate limiting middleware for API protection
- **Metrics**: Include Prometheus metrics collection
- **Structured Logging**: Use JSON logging for production systems
- **Security**: Add security headers and input validation middleware

## Extensions

This pattern can be extended with additional middleware:
- Rate limiting
- Request/response compression
- API versioning
- Request validation
- Response caching
- Metrics and observability

The middleware pattern provides a clean, composable way to add cross-cutting concerns to your Go web applications while maintaining separation of concerns and testability.