#!/bin/bash

# Middleware Patterns Test Suite
# Tests logging, authentication, recovery, and CORS middleware

# Source the rich testing framework
source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "🔧 Middleware Patterns - Go" "Complete middleware chain demonstration with logging, auth, recovery, and CORS"

# Test 1: Basic request with logging middleware
test_http_rich "GET" "/" "" "1️⃣ Basic Request with Logging" \
    "Tests that the logging middleware generates unique request IDs and logs request details" \
    "Middleware should track request timing and add context to responses"

# Test 2: Request includes timestamp and request ID
test_http_rich "GET" "/" "" "2️⃣ Request Metadata Tracking" \
    "Verifies that logging middleware adds timestamps and request IDs" \
    "Each request should have unique identification and timing information"

# Test 3: Authentication middleware - protected endpoint without auth
test_http_status "GET" "/protected" "" "3️⃣ Protected Endpoint Without Auth" 401 \
    "Tests authentication middleware rejection of unauthorized requests" \
    "Protected endpoints should return 401 without Authorization header"

# Test 4: Authentication middleware - protected endpoint with valid auth
test_http_rich "GET" "/protected" "" "4️⃣ Protected Endpoint With Valid Auth" \
    "Tests successful authentication with Bearer token" \
    "Valid Bearer token should grant access to protected endpoints" \
    "" "demo-token"

# Test 5: Health check bypasses authentication
test_http_rich "GET" "/health" "" "5️⃣ Health Check Bypass" \
    "Tests that health check endpoint bypasses authentication" \
    "Health checks should work without authentication for monitoring"

# Test 6: CORS middleware headers
test_http_status "OPTIONS" "/" "" "6️⃣ CORS Preflight Handling" 200 \
    "Tests CORS middleware handling of OPTIONS requests" \
    "CORS middleware should handle preflight requests correctly"

# Test 7: Recovery middleware handles panics
test_http_status "GET" "/panic" "" "7️⃣ Panic Recovery" 500 \
    "Tests recovery middleware handling of panics" \
    "Panics should be caught and return 500 instead of crashing"

# Test 8: POST request with JSON body
test_http_rich "POST" "/" '{"test": "data"}' "8️⃣ POST Request with JSON" \
    "Tests middleware chain handling of POST requests with JSON data" \
    "POST requests should pass through middleware chain with body intact"

# Test 9: All middleware working together
test_http_rich "GET" "/protected" "" "9️⃣ Complete Middleware Chain" \
    "Tests all middleware working together: logging, CORS, auth, recovery" \
    "Complete middleware chain should process requests seamlessly" \
    "" "demo-token"

# Finish tests with rich summary
finish_tests_rich "Middleware patterns demonstrate how to build composable, reusable request processing layers in Go. The logging middleware provides request tracking and timing, authentication middleware secures endpoints, recovery middleware handles panics gracefully, and CORS middleware enables cross-origin requests. Each middleware can be applied independently or chained together to create sophisticated request processing pipelines while maintaining clean separation of concerns."