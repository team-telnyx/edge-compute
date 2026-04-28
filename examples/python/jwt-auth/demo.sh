#!/bin/bash

# JWT Authentication Test Script
# Tests authentication flow and protected endpoints using enhanced test wrapper

# Load shared test wrapper with rich educational features
source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "🔐 JWT Authentication & Authorization" "Complete JWT workflow with role-based access control"

# Test 1: API Documentation
test_http_rich "GET" "/" "" "1️⃣ Get API Documentation" \
    "Every secure API should provide clear documentation of available endpoints" \
    "Self-documenting APIs help developers understand authentication requirements and available features"

# Test 2: Admin Login
test_http_rich "POST" "/auth/login" '{"username":"admin","password":"admin123"}' "2️⃣ Admin Login" \
    "Testing authentication with valid admin credentials - the foundation of JWT security" \
    "Successful login returns both access token (short-lived) and refresh token (long-lived) for secure session management"

# Extract tokens from login response for subsequent tests
ACCESS_TOKEN=""
REFRESH_TOKEN=""
if [ $FAILED_TESTS -eq 0 ]; then
    # Get the last login response 
    LOGIN_RESPONSE=$(curl -s -X POST "$FUNCTION_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}')
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null || echo "")
        REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('refresh_token', ''))" 2>/dev/null || echo "")
        echo "🔑 Extracted tokens for subsequent tests"
    fi
fi

start_section "🛡️ Token-Based Authorization" "Testing protected endpoints and role-based access"

# Test 3: Protected endpoint with token
if [ -n "$ACCESS_TOKEN" ]; then
    test_http_rich "GET" "/protected" "" "3️⃣ Access Protected Endpoint" \
        "Testing JWT token validation on protected resources" \
        "Valid JWT tokens grant access to protected endpoints, demonstrating successful authentication" \
        "" "$ACCESS_TOKEN"
else
    echo "⚠️ Skipping protected endpoint test - no access token available"
fi

# Test 4: User information  
if [ -n "$ACCESS_TOKEN" ]; then
    test_http_rich "GET" "/user" "" "4️⃣ Get User Information" \
        "Extracting user identity from JWT claims for personalization" \
        "JWTs can carry user metadata, enabling personalized responses without database lookups" \
        "" "$ACCESS_TOKEN"
else
    echo "⚠️ Skipping user info test - no access token available"
fi

start_section "👑 Admin Role Authorization" "Testing role-based access control (RBAC)"

# Test 5: Admin endpoint
if [ -n "$ACCESS_TOKEN" ]; then
    test_http_rich "GET" "/admin" "" "5️⃣ Access Admin Endpoint" \
        "Testing role-based authorization - only admin users should access this endpoint" \
        "Role-based access control (RBAC) ensures users can only access appropriate resources based on their permissions" \
        "" "$ACCESS_TOKEN"
else
    echo "⚠️ Skipping admin endpoint test - no access token available"
fi

# Test 6: List users (admin only)
if [ -n "$ACCESS_TOKEN" ]; then
    test_http_rich "GET" "/users" "" "6️⃣ List All Users (Admin Only)" \
        "Administrative endpoints for user management require elevated privileges" \
        "Admin-only endpoints demonstrate fine-grained permission control in JWT-based systems" \
        "" "$ACCESS_TOKEN"
else
    echo "⚠️ Skipping user list test - no access token available"
fi

start_section "♻️ Token Lifecycle Management" "Testing token refresh and session management"

# Test 7: Token refresh
if [ -n "$REFRESH_TOKEN" ]; then
    test_http_rich "POST" "/auth/refresh" "{\"refresh_token\":\"$REFRESH_TOKEN\"}" "7️⃣ Refresh Access Token" \
        "Using refresh token to obtain new access token without re-authentication" \
        "Refresh tokens enable seamless session extension while maintaining security through short-lived access tokens"
else
    echo "⚠️ Skipping token refresh test - no refresh token available"
fi

start_section "🚫 Security & Error Handling" "Testing authentication failures and edge cases"

# Test 8: Access without token (should fail)
test_http_rich "GET" "/protected" "" "8️⃣ Access Protected Endpoint Without Token" \
    "Testing security: protected endpoints should reject requests without authentication" \
    "Proper authentication validation ensures unauthorized users cannot access protected resources" \
    401

# Test 9: Access with invalid token (should fail)
test_http_rich "GET" "/protected" "" "9️⃣ Access with Invalid Token" \
    "Testing JWT validation: malformed or expired tokens should be rejected" \
    "Robust token validation prevents security vulnerabilities from invalid or tampered tokens" \
    401

# Test 10: Invalid login credentials
test_http_rich "POST" "/auth/login" '{"username":"admin","password":"wrongpassword"}' "🔟 Invalid Login Attempt" \
    "Testing credential validation and secure error handling" \
    "Proper authentication failures protect against brute force attacks while providing helpful error messages" \
    401

# Test 11: Logout
if [ -n "$REFRESH_TOKEN" ]; then
    test_http_rich "POST" "/auth/logout" "{\"refresh_token\":\"$REFRESH_TOKEN\"}" "1️⃣1️⃣ User Logout" \
        "Secure session termination invalidates tokens to prevent unauthorized future access" \
        "Proper logout functionality ensures sessions are securely terminated when users are done"
else
    echo "⚠️ Skipping logout test - no refresh token available"
fi

# Finish with educational summary
finish_tests_rich "
• 🔐 Complete JWT authentication flow with secure credential validation
• 🎫 Token-based authorization using access tokens (short-lived) and refresh tokens (long-lived)  
• 👑 Role-based access control (RBAC) with admin vs user permissions
• 🛡️ Secure token validation and proper rejection of invalid/missing tokens
• ♻️ Token lifecycle management including refresh and logout
• 🚫 Comprehensive error handling for authentication failures
• 🔒 Security best practices: password hashing, token expiry, session management
• 📚 Production-ready patterns for JWT-based authentication in serverless functions
"