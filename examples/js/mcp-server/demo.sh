#!/bin/bash

# MCP Server Demo Suite (JavaScript)
# Tests the Telnyx MCP server health probes and MCP protocol endpoints
# Requires SHARED_SECRET to be set (used for bearer-token auth)

source "$(dirname "$0")/../../demo_wrapper.sh"

# Build auth args from SHARED_SECRET
AUTH_ARGS=()
if [ -n "${SHARED_SECRET:-}" ]; then
    AUTH_ARGS=(-H "Authorization: Bearer $SHARED_SECRET")
fi

start_section "🤖 MCP Server — JavaScript" "Telnyx MCP server exposing API tools to AI agents via streamable HTTP"

# 1. Health check
test_http_rich "GET" "/health" "" "1️⃣ Health Check" \
    "GET /health returns 200 OK — used by Knative for container probes" \
    "Liveness and readiness probes are also available at /health/liveness and /health/readiness"

# 2. Liveness probe
test_http_rich "GET" "/health/liveness" "" "2️⃣ Liveness Probe" \
    "GET /health/liveness confirms the process is alive" \
    "Knative uses this to decide whether to restart the container"

# 3. Readiness probe
test_http_rich "GET" "/health/readiness" "" "3️⃣ Readiness Probe" \
    "GET /health/readiness confirms the server is ready to accept traffic" \
    "Knative uses this to decide whether to route traffic to this pod"

# 4. MCP Initialize (streamable HTTP requires Accept: application/json, text/event-stream)
EXTRA_HEADERS="-H \"Accept: application/json, text/event-stream\""
if [ -n "${SHARED_SECRET:-}" ]; then
    EXTRA_HEADERS="$EXTRA_HEADERS -H \"Authorization: Bearer $SHARED_SECRET\""
fi
test_http_rich "POST" "/" \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo","version":"1.0.0"}}}' \
    "4️⃣ MCP Initialize" \
    "POST / with an MCP initialize request starts a new session" \
    "The server responds with its capabilities and available tools (execute, search_docs)"
EXTRA_HEADERS=""

# 5. MCP execute tool call (multi-step: initialize → initialized → tools/call)
echo ""
echo "🔍 Test $TOTAL_TESTS: 5️⃣ MCP Execute Tool Call"
[ "$SHORT" != "true" ] && echo "   POST / (initialize → initialized → tools/call)"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

MCP_SESSION=$(curl -s -D- -X POST "$FUNCTION_URL/" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    "${AUTH_ARGS[@]}" \
    -d '{"jsonrpc":"2.0","id":10,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo-execute","version":"1.0.0"}}}' 2>&1 \
    | grep -i 'mcp-session-id' | tr -d '\r' | awk '{print $2}')

if [ -z "$MCP_SESSION" ]; then
    echo "   ❌ FAIL - Could not obtain mcp-session-id"
    FAILED_TESTS=$((FAILED_TESTS + 1))
else
    # Send initialized notification
    curl -s -o /dev/null -X POST "$FUNCTION_URL/" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json, text/event-stream" \
        -H "mcp-session-id: $MCP_SESSION" \
        "${AUTH_ARGS[@]}" \
        -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

    # Call execute tool
    EXEC_RESPONSE=$(curl -s -X POST "$FUNCTION_URL/" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json, text/event-stream" \
        -H "mcp-session-id: $MCP_SESSION" \
        "${AUTH_ARGS[@]}" \
        -d '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"execute","arguments":{"code":"async function run(client) { console.log(\"hello from execute\"); }"}}}')

    if echo "$EXEC_RESPONSE" | grep -q '"isError":true'; then
        echo "   ❌ FAIL - execute tool returned isError:true"
        [ "$SHORT" != "true" ] && echo "   Response: $(echo "$EXEC_RESPONSE" | grep '^data:' | head -1)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    elif echo "$EXEC_RESPONSE" | grep -q '"result"'; then
        echo "   ✅ PASS (execute tool returned a successful result)"
        [ "$SHORT" != "true" ] && add_context "Full MCP session: initialize → initialized → tools/call for execute"
        [ "$SHORT" != "true" ] && add_explanation "The execute tool ran code and returned output — confirms Deno + ESM resolution works"
    else
        echo "   ❌ FAIL - Unexpected response"
        [ "$SHORT" != "true" ] && echo "   Response: $(echo "$EXEC_RESPONSE" | head -1)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
fi

# 6. Unsupported method on health endpoint
test_http_status "POST" "/health" "" "6️⃣ POST to Health Endpoint" 401 \
    "Health endpoints only respond to GET — POST falls through to auth middleware" \
    "Returns 401 when SHARED_SECRET is set, 503 when unset"

finish_tests_rich "The JavaScript MCP server demonstrates how to run a Model Context Protocol server as a Telnyx Edge Function. The telnyx-mcp library handles the MCP protocol, tool registration, and code execution — this example just wires it into an Express HTTP server with Knative health probes. AI agents connect via streamable HTTP transport on POST / and can use two tools: 'execute' to run code against the Telnyx SDK, and 'search_docs' to find SDK documentation."
