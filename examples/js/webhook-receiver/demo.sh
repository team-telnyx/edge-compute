#!/bin/bash

# Webhook Receiver Demo Suite (JavaScript)
# Tests HMAC signature verification and webhook ingestion

source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "🪝 Webhook Receiver — JavaScript" "Single-purpose webhook ingestion with HMAC-SHA256 signature verification"

# 1. Service info
test_http_rich "GET" "/" "" "1️⃣ Service Info" \
    "GET / returns service metadata, recent webhook log, and signature verification status" \
    "Function uses init()/handle()/shutdown() lifecycle — the same convention as the edge runtime"

# 2. Receive webhook (no secret configured)
test_http_rich "POST" "/" '{"event":"user.created","user_id":"abc123"}' "2️⃣ Receive Webhook" \
    "POST / ingests a webhook; signature verification is disabled when WEBHOOK_SECRET is unset" \
    "Returns 200 with a webhook_id and timestamp"

# 3. Receive another webhook
test_http_rich "POST" "/" '{"event":"order.paid","order_id":"ord_456","amount":99.99}' "3️⃣ Second Webhook" \
    "Each POST stores an entry in the in-memory ring buffer" \
    "The ring buffer keeps the last MAX_WEBHOOKS entries"

# 4. Receive webhook with source header
test_http_rich "POST" "/" '{"event":"payment.failed","order_id":"ord_789"}' "4️⃣ Webhook with Source Header" \
    "x-webhook-source header is recorded alongside the payload" \
    "Useful for identifying which upstream service sent the webhook"

# 5. Check updated log via GET
test_http_rich "GET" "/" "" "5️⃣ Recent Webhook Log" \
    "GET / now includes the recently received webhooks in recent_webhooks" \
    "total_received should be 3"

# 6. Unsupported method
test_http_status "PUT" "/" "" "6️⃣ Unsupported Method Returns 405" 405 \
    "Only GET and POST are handled" \
    "Other methods return 405 Method Not Allowed"

finish_tests_rich "The JavaScript webhook receiver demonstrates the Knative func runtime convention: module.exports exports init(), handle(context, body), and shutdown() lifecycle hooks. The runtime wrapper (app.js) calls init() once at startup to load secrets from environment variables, passes a context object and auto-parsed body to handle() for each request, and calls shutdown() on exit. HMAC-SHA256 verification uses the built-in crypto module — no external runtime dependencies required."
