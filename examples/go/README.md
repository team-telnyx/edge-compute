# Go Edge Function Examples

This directory contains high-performance examples of edge functions written in Go, demonstrating various patterns and middleware for serverless computing with Telnyx Edge Compute.

## 🚀 Quick Start

```bash
# List available examples
make list

# Demo a specific example
make demo EXAMPLE=middleware-patterns

# Run an example locally
make run EXAMPLE=middleware-patterns
```

## 📋 Available Examples

### 1. **Middleware Patterns** (`middleware-patterns/`)
Comprehensive HTTP middleware stack demonstration showing common patterns for edge functions.

**Features:**
- Request logging and timing
- JWT authentication with configurable endpoints
- CORS handling for cross-origin requests
- Panic recovery with graceful error responses
- Request ID tracking and context propagation

**Endpoints Tested:**
- `/` - Basic request with logging
- `/protected` - Authentication required
- `/cors` - CORS preflight handling
- `/panic` - Panic recovery demonstration
- `/timing` - Request timing measurement

## 🛠️ Development Workflow

Each Go example follows a consistent structure:

```
example-name/
├── go.mod              # Go module definition
├── handler.go          # Function implementation (package function)
├── func.toml          # Function configuration
├── demo.sh            # Comprehensive demo suite
└── README.md          # Example-specific documentation
```

## 🐳 Docker Support

All examples include Docker support with multi-stage builds:

- **Builder stage**: Compiles Go binary for target architecture
- **Runtime stage**: Lightweight Alpine Linux container
- **Health checks**: Built-in container health monitoring
- **Consistent networking**: All examples expose port 8080

## 📦 Module Structure

Go examples use a two-package structure:

- `package main`: HTTP server boilerplate (shared `app.go`)
- `package function`: Business logic implementation (`handler.go`)

This separation allows for:
- Clean separation of concerns
- Reusable server infrastructure
- Focus on function implementation
- Easy testing and validation

## 🎯 Go-Specific Features

- **Performance**: Compiled binaries for maximum performance
- **Concurrency**: Goroutine-based request handling
- **Static binaries**: No runtime dependencies
- **Fast startup**: Ideal for serverless workloads
- **Memory efficient**: Low footprint for edge deployments