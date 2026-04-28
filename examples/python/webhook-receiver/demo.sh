#!/bin/bash

# Webhook Receiver Test Script  
# Tests webhook processing, storage, and signature verification using enhanced test wrapper

# Load shared test wrapper with rich educational features
source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "📨 Webhook Processing & Storage" "Complete webhook receiver functionality with security validation"

# Test 1: API Documentation
test_http_rich "GET" "/" "" "1️⃣ Get API Documentation" \
    "Self-documenting APIs provide clear guidance for webhook integration" \
    "Good webhook APIs document all endpoints, expected payloads, and security requirements"

# Test 2: Initial Webhooks List (should be empty)
test_http_rich "GET" "/webhooks" "" "2️⃣ List Webhooks (Initial State)" \
    "Verifying empty state before webhook processing begins" \
    "Clean initial state ensures webhook storage is working correctly"

start_section "🔗 Webhook Reception & Parsing" "Testing webhook payload processing from various sources"

# Test 3: Create Test Webhook
test_http_rich "POST" "/webhook/test" "" "3️⃣ Create Test Webhook" \
    "Testing basic webhook endpoint availability and response handling" \
    "Webhook endpoints should accept POST requests and respond with confirmation"

# Test 4: Send Git Repository Webhook
git_webhook='{
  "ref": "refs/heads/main",
  "repository": {
    "name": "example-repo",
    "owner": {"login": "testuser"}
  },
  "pusher": {"name": "testuser"},
  "commits": [
    {
      "id": "abc123",
      "message": "Update README",
      "author": {"name": "Test User"}
    }
  ]
}'
test_http_rich "POST" "/webhook" "$git_webhook" "4️⃣ Send Git Repository Webhook" \
    "Testing webhook payload processing for version control system events" \
    "Git webhooks enable automated CI/CD workflows triggered by repository changes"

# Test 5: Send Payment Processing Webhook
payment_webhook='{
  "type": "payment.succeeded",
  "data": {
    "object": {
      "id": "pay_1234567890",
      "amount": 2000,
      "currency": "usd",
      "status": "succeeded"
    }
  }
}'
test_http_rich "POST" "/webhook" "$payment_webhook" "5️⃣ Send Payment Processing Webhook" \
    "Testing webhook processing for financial transaction events" \
    "Payment webhooks enable real-time transaction processing and order fulfillment"

# Test 6: Send Chat Platform Webhook  
chat_webhook='{
  "text": "New message from channel",
  "user_name": "testuser", 
  "channel": "#general",
  "timestamp": "1609459200"
}'
test_http_rich "POST" "/webhook" "$chat_webhook" "6️⃣ Send Chat Platform Webhook" \
    "Testing webhook processing for communication platform events" \
    "Chat webhooks enable automated responses and integrations with messaging systems"

# Test 7: Send Custom Application Webhook
custom_webhook='{"message": "Custom application event", "source": "internal_system", "event_type": "user_signup"}'
test_http_rich "POST" "/webhook" "$custom_webhook" "7️⃣ Send Custom Application Webhook" \
    "Testing generic webhook handling for custom application events" \
    "Custom webhooks allow integration between internal systems and external services"

start_section "🔐 Security & Signature Validation" "Testing webhook authentication and security features"

# Test 8: Webhook with Signature Validation
add_context "Testing webhook signature validation - critical for production security"
echo ""
echo -e "${BLUE}🔍 8️⃣ Test Webhook with Signature${NC}"
echo "📍 POST /webhook (with signature headers)"
echo "Note: This demonstrates signature validation when WEBHOOK_RECEIVER_SECRET is configured"
curl -s -w "\nHTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "x-webhook-source: test_system" \
    -H "x-webhook-signature: sha256=invalid_signature" \
    -d '{"test": "signature_validation", "event": "security_test"}' \
    "$FUNCTION_URL/webhook"
echo "------------------------------------------"
add_explanation "Webhook signature validation prevents unauthorized payload injection and ensures data integrity"

start_section "📋 Webhook Storage & Retrieval" "Testing webhook persistence and querying capabilities"

# Test 9: List All Webhooks
test_http_rich "GET" "/webhooks" "" "9️⃣ List All Received Webhooks" \
    "Verifying webhook storage and retrieval functionality" \
    "Webhook storage enables audit trails, debugging, and replay capabilities for integration troubleshooting"

start_section "🚫 Error Handling & Edge Cases" "Testing webhook system resilience"

# Test 10: Test Invalid Endpoint
test_http_rich "GET" "/invalid" "" "🔟 Test Invalid Endpoint" \
    "Testing 404 error handling for undefined routes" \
    "Proper error handling provides clear feedback when incorrect endpoints are accessed"

# Finish with comprehensive educational summary
finish_tests_rich "
• 📨 **Webhook Reception**: Process HTTP POST requests with JSON payloads from various sources
• 🔍 **Payload Parsing**: Extract and validate webhook data from different event formats  
• 💾 **Persistent Storage**: Store received webhooks for audit, debugging, and replay
• 🔐 **Security Validation**: Implement signature verification for webhook authenticity
• 🏷️ **Source Identification**: Track webhook origins for routing and processing logic
• 📋 **Query Interface**: Retrieve stored webhooks via REST API for analysis
• 🛡️ **Error Handling**: Graceful failure modes for malformed or invalid requests
• 🔄 **Integration Patterns**: Support common webhook patterns from git, payment, chat, and custom systems
• 🎯 **Production Ready**: Includes security headers, validation, and proper HTTP status codes
• 📚 **Extensible Design**: Easily adaptable for specific business logic and custom webhook processing
"