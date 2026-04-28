# Edge Function Examples

This directory contains comprehensive examples demonstrating various patterns and use cases for Telnyx Edge Compute functions.

## 🐍 Python Examples

Complete, production-ready examples showing different serverless patterns:

| Example | Description | Key Features |
|---------|-------------|--------------|
| [**Webhook Receiver**](python/webhook-receiver/) | Generic webhook processor with signature verification | HMAC verification, multi-source support, SQLite storage |
| [**Data Processor**](python/data-processor/) | Batch data processing with CSV support | File processing, validation, batch operations |
| [**JSON Transformer**](python/json-transformer/) | JSON manipulation and transformation service | Case conversion, flattening, filtering, history tracking |
| [**JWT Authentication**](python/jwt-auth/) | Complete authentication service with RBAC | JWT tokens, role-based access, protected endpoints |
| [**RESTful API**](python/restful-api/) | Complete CRUD API for product management | Full CRUD, filtering, pagination, validation |

### 🚀 Quick Start (Python)

```bash
cd examples/python

# List available examples  
make list

# Demo a specific example
make demo EXAMPLE=jwt-auth  

# Run an example locally
make run EXAMPLE=restful-api

# Demo each example individually
make demo EXAMPLE=webhook-receiver
make demo EXAMPLE=jwt-auth
# etc.
```

## 🐹 Go Examples

High-performance examples demonstrating Go patterns for edge computing:

| Example | Description | Key Features |
|---------|-------------|--------------|
| [**Middleware Patterns**](go/middleware-patterns/) | HTTP middleware stack demonstration | Logging, authentication, CORS, panic recovery, request timing |

### 🚀 Quick Start (Go)

```bash
cd examples/go

# List available examples
make list

# Demo a specific example
make demo EXAMPLE=middleware-patterns

# Run an example locally
make run EXAMPLE=middleware-patterns
```

## 🟨 JavaScript Examples

Node.js examples for edge computing:

| Example | Description | Key Features |
|---------|-------------|--------------|
| [**Webhook Receiver**](js/webhook-receiver/) | Webhook ingestion with HMAC-SHA256 signature verification | Knative func lifecycle, crypto module, in-memory ring buffer |
| [**MCP Server**](js/mcp-server/) | Telnyx MCP server for AI agents | MCP protocol, streamable HTTP, telnyx-mcp, code execution |

### 🚀 Quick Start (JS)

Function-module examples (webhook-receiver) use the shared `app.js` wrapper and `make` workflow:

```bash
cd examples/js

# List available examples
make list

# Demo a specific example
make demo EXAMPLE=webhook-receiver

# Run an example locally
make run EXAMPLE=webhook-receiver
```

The **mcp-server** example is a standalone Express server — it manages its own HTTP listener and does not use the shared `app.js`/Dockerfile. Run it directly:

```bash
cd examples/js/mcp-server
npm install
TELNYX_API_KEY=<your-key> SHARED_SECRET=dev-secret npm start
```

## 🔷 TypeScript Examples

TypeScript examples that compile to plain Node.js — showcasing the type system for safer edge functions:

| Example | Description | Key Features |
|---------|-------------|--------------|
| [**Call Event Router**](ts/call-event-router/) | Telnyx voice/SMS webhook dispatcher | Discriminated unions, exhaustive switch, `never` guard, typed handlers |
| [**MCP Server**](ts/mcp-server/) | Telnyx MCP server for AI agents | MCP protocol, streamable HTTP, telnyx-mcp, typed config |

### 🚀 Quick Start (TS)

Function-module examples (call-event-router) use the shared `app.js` wrapper and `make` workflow:

```bash
cd examples/ts

# List available examples
make list

# Demo a specific example
make demo EXAMPLE=call-event-router

# Run an example locally (compiles TypeScript inside Docker)
make run EXAMPLE=call-event-router
```

The **mcp-server** example is a standalone Express server — it manages its own HTTP listener and does not use the shared `app.js`/Dockerfile. Run it directly:

```bash
cd examples/ts/mcp-server
npm install
npm run build
TELNYX_API_KEY=<your-key> SHARED_SECRET=dev-secret npm start
```

## 🎯 Shared Features

All examples include:
- ✅ **Complete implementation** with proper error handling
- ✅ **Environment configuration** via secrets/env vars
- ✅ **Production patterns** for authentication, validation, logging
- ✅ **Documentation** with usage examples and API reference

Most examples use the **function-module pattern** (`init()`/`handle()`/`shutdown()` lifecycle) and the shared `app.js` wrapper, `Dockerfile`, and `Makefile` targets. **Standalone examples** (mcp-server) manage their own HTTP server and dependencies — see their individual READMEs for build and run instructions.

## 📁 Directory Structure

```
examples/
├── README.md                    # This file - examples overview
├── python/                      # Python examples directory
│   ├── README.md               # Python-specific documentation
│   ├── Dockerfile              # Shared Docker infrastructure
│   ├── Makefile               # Build and test automation
│   ├── webhook-receiver/       # Example: webhook processing
│   ├── data-processor/         # Example: batch data processing
│   ├── json-transformer/       # Example: JSON manipulation
│   ├── jwt-auth/              # Example: authentication service
│   └── restful-api/           # Example: CRUD API
├── go/                        # Go examples directory
│   ├── README.md             # Go-specific documentation
│   ├── Dockerfile            # Shared Docker infrastructure
│   ├── Makefile             # Build and test automation
│   ├── app.go               # HTTP server template
│   └── middleware-patterns/ # Example: middleware stack
├── js/                        # JavaScript (Node.js) examples directory
│   ├── app.js               # Local dev wrapper (mirrors faas-js-runtime)
│   ├── Dockerfile            # Shared Docker infrastructure (node:18-alpine)
│   ├── Makefile             # Build and test automation
│   ├── webhook-receiver/    # Function-module: webhook ingestion with HMAC verification
│   └── mcp-server/          # Standalone: Telnyx MCP server for AI agents
└── ts/                        # TypeScript examples directory
    ├── app.js               # Local dev wrapper (compiled TS entry point)
    ├── Dockerfile            # Shared Docker infrastructure (compiles TS inside container)
    ├── Makefile             # Build and test automation
    ├── call-event-router/   # Function-module: typed Telnyx webhook event router
    └── mcp-server/          # Standalone: Telnyx MCP server for AI agents (TypeScript)
```

## 🛠️ Development Workflow

### Local Development
1. **Choose an example**: Browse the examples and pick one that matches your use case
2. **Demo locally**: Use `make demo EXAMPLE=<name>` to run it locally with Docker
3. **Modify for your needs**: Copy the example and adapt it to your requirements
4. **Deploy**: Deploy to Telnyx Edge Compute

## 🎯 Use Case Mapping

**API Development** → Start with `restful-api` (Python) for full CRUD patterns  
**Webhook Processing** → Use `webhook-receiver` (JS or Python) or `call-event-router` (TS) for event dispatch  
**Authentication** → Implement `jwt-auth` (Python) patterns for secure APIs  
**Data Processing** → Build on `data-processor` (Python) for file/batch operations  
**Data Transformation** → Use `json-transformer` (Python) for format conversions  
**AI / MCP Integration** → Use `mcp-server` (TS or JS) to expose Telnyx API tools to AI agents  
**Middleware / Observability** → See `middleware-patterns` (Go) for logging and CORS  

## 📚 Learning Path

1. **Beginner**: Start with `webhook-receiver` (JS) to understand HTTP handling and routing basics
2. **Intermediate**: Try `restful-api` (Python) for database operations and CRUD patterns
3. **Advanced (TS)**: Explore `call-event-router` (TS) for type-safe event dispatch patterns
4. **Advanced (Go)**: Explore `middleware-patterns` (Go) for composable middleware design

## 🔗 Related Documentation

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [Telnyx Edge CLI](https://github.com/team-telnyx/edge-compute)