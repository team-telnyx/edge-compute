# MCP Server (TypeScript)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that runs as a Telnyx Edge Compute function. Exposes Telnyx API tools to AI agents via the streamable HTTP transport.

## What it does

The server provides two MCP tools to connected AI agents:

| Tool | Description |
|------|-------------|
| `execute` | Write and run TypeScript code against the Telnyx SDK |
| `search_docs` | Search Telnyx SDK documentation for methods, parameters, and examples |

## How it works

The `telnyx-mcp` library does the heavy lifting — it implements the MCP protocol, registers tools, and handles code execution. This example wires it into an Express HTTP server with Knative health probes so it can run as an edge function.

```
Client (AI agent)
  │
  ▼  POST / (MCP streamable HTTP)
┌─────────────────────────┐
│  Express + telnyx-mcp   │
│  ┌───────────────────┐  │
│  │ execute           │  │  Runs TS code against Telnyx SDK
│  │ search_docs       │  │  Searches SDK documentation
│  └───────────────────┘  │
└─────────────────────────┘
```

## Security

Set `SHARED_SECRET` to require a bearer token on all MCP requests. Health check endpoints are always unauthenticated so Knative probes continue to work.

```bash
telnyx-edge secrets add SHARED_SECRET "$(openssl rand -hex 32)"
```

`SHARED_SECRET` is required — without it the server rejects all MCP requests with 503. When set, clients must send `Authorization: Bearer <secret>`. Health checks remain open so Knative probes still work.

## Deploy

```bash
# Install dependencies and compile TypeScript
npm install
npm run build

# Set your Telnyx API key and shared secret
telnyx-edge secrets add TELNYX_API_KEY <your-api-key>
telnyx-edge secrets add SHARED_SECRET "$(openssl rand -hex 32)"

# Ship to edge
telnyx-edge ship
```

## Local development

```bash
npm install
npm run build
TELNYX_API_KEY=<your-key> SHARED_SECRET=dev-secret npm start
```

The server listens on port 8080 by default (`PORT` env var to override).

## Connect an MCP client

Point your MCP client at the function URL using streamable HTTP transport:

```
https://<your-func-url>/
```

### Claude Desktop example

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "telnyx": {
      "url": "https://<your-func-url>/",
      "headers": {
        "Authorization": "Bearer <your-shared-secret>"
      }
    }
  }
}
```

### curl — list available tools

```bash
# Initialize a session and list tools
curl -X POST https://<your-func-url>/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer <your-shared-secret>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `TELNYX_API_KEY` | Telnyx API key for upstream API calls | Yes |
| `SHARED_SECRET` | Bearer token for inbound auth — required for deployed functions | Yes (deploy) |
| `PORT` | HTTP listen port (default: `8080`) | No |

## Health checks

Knative readiness/liveness probes are served at:

- `GET /health`
- `GET /health/liveness`
- `GET /health/readiness`

## Project structure

```
index.ts          # Entry point — imports telnyx-mcp, adds health probes, starts server
package.json      # Dependencies (telnyx-mcp does the heavy lifting)
tsconfig.json     # TypeScript config
func.toml         # Edge Compute function config (func_id set by CLI)
```
