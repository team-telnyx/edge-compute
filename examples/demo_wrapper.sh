#!/bin/bash

# Shared Test Wrapper for Python Edge Function Examples
# Source this file from individual test.sh scripts to get consistent CI/CD behavior
#
# Usage in test.sh:
#   source "$(dirname "$0")/../demo_wrapper.sh"
#   test_case "GET" "/" "" "Test API documentation" "Context here" "Explanation here"
#   finish_tests

set -e  # Exit on any command failure

# Track test results for CI/CD
FAILED_TESTS=0
TOTAL_TESTS=1

# Configuration options
SHORT="${SHORT:-false}"  # Set to true for CI-friendly output
NO_COLOR="${NO_COLOR:-false}"  # Set to true to disable colors

# Colors for better output (if terminal supports it)
if [ -t 1 ] && [ "$NO_COLOR" != "true" ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    NC=''
fi

# Determine function URL (local or deployed)
if [ -z "$FUNCTION_URL" ]; then
    FUNCTION_URL="http://localhost:8080"
    [ "$SHORT" != "true" ] && echo "📍 Using local function URL: $FUNCTION_URL"
else
    [ "$SHORT" != "true" ] && echo "📍 Using deployed function URL: $FUNCTION_URL"
fi

# Add educational context before tests
add_context() {
    local context="$1"
    [ "$SHORT" = "true" ] && return
    echo ""
    echo "   Context: $context"
}

# Add explanations after successful tests
add_explanation() {
    local explanation="$1"
    [ "$SHORT" = "true" ] && return
    echo ""
    echo "   💡 What this demonstrates: $explanation"
}

# Start a logical test section
start_section() {
    local section_name="$1"
    local section_desc="$2"
    [ "$SHORT" = "true" ] && return
    echo ""
    echo "*** $section_name ***"
    echo "$section_desc"
    echo "==============================================="
}

# Debug information for failed tests
debug_failure() {
    local method="$1"
    local path="$2"
    local data="$3"
    local status="$4"
    [ "$SHORT" = "true" ] && return
    echo "   ❌ FAIL - $status"
    echo "   Method: $method"
    echo "   Path:   $path"
    echo "   Data:   $data"
}

# Test HTTP endpoint with automatic failure detection
# Usage: test_http METHOD PATH [DATA] [DESCRIPTION] [EXPECTED_STATUS] [AUTH_TOKEN]
test_http() {
    local method="$1"
    local path="$2"
    local data="${3:-}"
    local description="${4:-Test $method $path}"
    local expected_status="${5:-}"
    local auth_token="${6:-}"

    [ "$SHORT" != "true" ] && echo ""
    echo "🔍 Test $TOTAL_TESTS: $description"
    [ "$SHORT" != "true" ] && echo "   $method $path"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Build curl command based on parameters
    local curl_cmd="curl -s -w \"\\nHTTP_STATUS:%{http_code}\\nTIME:%{time_total}s\" -X \"$method\""

    if [ -n "$auth_token" ]; then
        curl_cmd="$curl_cmd -H \"Authorization: Bearer $auth_token\""
    fi

    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H \"Content-Type: application/json\" -d '$data'"
    fi

    # Allow demo scripts to inject extra headers (e.g. Accept for MCP)
    if [ -n "${EXTRA_HEADERS:-}" ]; then
        curl_cmd="$curl_cmd $EXTRA_HEADERS"
    fi

    curl_cmd="$curl_cmd \"$FUNCTION_URL$path\""

    # Execute request and capture output
    local response
    response=$(eval "$curl_cmd" 2>/dev/null) || {
        echo "   ❌ FAIL - Connection error"
        debug_failure "$method" "$path" "$data" "Connection failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    }

    # Extract HTTP status code
    local status_code
    status_code=$(echo "$response" | grep "HTTP_STATUS:" | cut -d':' -f2)

    # Extract response time
    local response_time
    response_time=$(echo "$response" | grep "TIME:" | cut -d':' -f2)

    # Remove metadata from response body
    local response_body
    response_body=$(echo "$response" | sed '/HTTP_STATUS:/d' | sed '/TIME:/d')

    # Validate response
    local test_passed=true

    if [ -z "$status_code" ]; then
        echo "   ❌ FAIL - No HTTP status received"
        test_passed=false
    elif [ "$status_code" -eq 000 ]; then
        echo "   ❌ FAIL - Connection failed"
        test_passed=false
    elif [ -n "$expected_status" ] && [ "$status_code" -ne "$expected_status" ]; then
        echo "   ❌ FAIL - Expected HTTP $expected_status, got $status_code"
        test_passed=false
    elif [ -z "$expected_status" ] && [ "$status_code" -ge 500 ]; then
        echo "   ❌ FAIL - Server error (HTTP $status_code)"
        test_passed=false
    elif [ -z "$expected_status" ] && [ "$status_code" -ge 400 ]; then
        # If no expected status specified, treat 4xx+ as failure (except for intentional 404 tests)
        if [[ "$path" != *"invalid"* ]] && [[ "$path" != *"nonexistent"* ]] && [ "$status_code" -ne 404 ]; then
            echo "   ❌ FAIL - Client error (HTTP $status_code)"
            test_passed=false
        fi
    fi

    if [ "$test_passed" = true ]; then
        echo "   ✅ PASS (HTTP $status_code, ${response_time})"
    else
        debug_failure "$method" "$path" "$data" "$status_code"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    # Show response body (formatted JSON if possible)
    if [ "$SHORT" != "true" ]; then
        # Use jq for proper JSON validation (handles formatted JSON and arrays)
        if echo "$response_body" | head -1 | jq empty 2>/dev/null; then
            echo "   Response:"
            echo "$response_body" | head -1 | jq . 2>/dev/null | sed 's/^/      /' || echo "$response_body" | head -1 | sed 's/^/   /'
        else
            echo "   Response: $(echo "$response_body" | head -1)"
        fi
    fi
    
    # Return test result (0 for passed, 1 for failed)
    [ "$test_passed" = true ] && return 0 || return 1
}

# Capture HTTP response for further processing
# Usage: response=$(test_http_capture METHOD PATH [DATA] [AUTH_TOKEN])
test_http_capture() {
    local method="$1"
    local path="$2"
    local data="${3:-}"
    local auth_token="${4:-}"

    local curl_cmd="curl -s -w \"\\nHTTP_STATUS:%{http_code}\\n\" -X \"$method\""

    if [ -n "$auth_token" ]; then
        curl_cmd="$curl_cmd -H \"Authorization: Bearer $auth_token\""
    fi

    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -H \"Content-Type: application/json\" -d '$data'"
    fi

    # Allow demo scripts to inject extra headers (e.g. Accept for MCP)
    if [ -n "${EXTRA_HEADERS:-}" ]; then
        curl_cmd="$curl_cmd $EXTRA_HEADERS"
    fi

    curl_cmd="$curl_cmd \"$FUNCTION_URL$path\""

    eval "$curl_cmd"
}

# Expect a specific field in JSON response
# Usage: expect_field "$json_body" "field_name"
expect_field() {
    local json="$1"
    local field="$2"

    if ! echo "$json" | jq -e "has(\"$field\")" >/dev/null; then
        echo "   ❌ FAIL - Missing expected field: $field"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    return 0
}

# Declarative test case wrapper
# Usage: test_case METHOD PATH DATA DESCRIPTION [CONTEXT] [EXPLANATION] [EXPECTED_STATUS] [AUTH_TOKEN]
test_case() {
    local method="$1"
    local path="$2"
    local data="$3"
    local description="$4"
    local context="${5:-}"
    local explanation="${6:-}"
    local expected="${7:-}"
    local token="${8:-}"

    if [ -n "$context" ]; then
        add_context "$context"
    fi

    test_http "$method" "$path" "$data" "$description" "$expected" "$token"

    # Only show explanation if test passed (we can tell from FAILED_TESTS count before vs after)
    local failed_before=$FAILED_TESTS
    if [ -n "$explanation" ] && [ $FAILED_TESTS -eq $failed_before ]; then
        add_explanation "$explanation"
    fi
}

# Rich test function with educational features (legacy compatibility)
# Usage: test_http_rich METHOD PATH [DATA] [DESCRIPTION] [CONTEXT] [EXPLANATION] [EXPECTED_STATUS] [AUTH_TOKEN]
test_http_rich() {
    local method="$1"
    local path="$2"
    local data="${3:-}"
    local description="${4:-}"
    local context="${5:-}"
    local explanation="${6:-}"
    local expected_status="${7:-}"
    local auth_token="${8:-}"

    if [ -n "$context" ]; then
        add_context "$context"
    fi

    test_http "$method" "$path" "$data" "$description" "$expected_status" "$auth_token"
    local test_result=$?

    if [ -n "$explanation" ] && [ $test_result -eq 0 ]; then
        add_explanation "$explanation"
    fi
}

# Test expecting a specific status code (e.g., 404 for not found)
test_http_status() {
    test_http "$1" "$2" "$3" "$4" "$5"
}

# Finish tests and exit with appropriate code
finish_tests() {
    echo ""
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "*** SUMMARY ***"
        echo "$((TOTAL_TESTS-FAILED_TESTS))/$TOTAL_TESTS tests passed"
        exit 0
    else
        echo "*** SUMMARY ***"
        echo "$FAILED_TESTS tests failed! ($((TOTAL_TESTS-FAILED_TESTS))/$TOTAL_TESTS passed)"
        exit 1
    fi
}

# Enhanced finish function with educational summary
# Usage: finish_tests_rich "Educational summary of what was demonstrated"
finish_tests_rich() {
    local what_was_demonstrated="$1"

    echo ""
    [ "$SHORT" != "true" ] && echo "📊 Test Summary: $((TOTAL_TESTS-FAILED_TESTS))/$TOTAL_TESTS tests passed"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo ""
        [ "$SHORT" != "true" ] && echo "🎉 Success! All endpoints are working correctly."

        if [ -n "$what_was_demonstrated" ] && [ "$SHORT" != "true" ]; then
            echo ""
            echo -e "${GREEN}🎓 What you learned:${NC}"
            echo "$what_was_demonstrated"
        fi

        echo ""
        [ "$SHORT" != "true" ] && echo "💡 Next steps:"
        [ "$SHORT" != "true" ] && echo "   - Ready for deployment"
        [ "$SHORT" != "true" ] && echo "   - Test deployed function: FUNCTION_URL=https://your-function.dev.telnyxcompute.com ./test.sh"
        exit 0
    else
        echo -e "${RED}❌ $FAILED_TESTS tests failed! ($((TOTAL_TESTS-FAILED_TESTS))/$TOTAL_TESTS passed)${NC}"
        echo ""
        [ "$SHORT" != "true" ] && echo "🔧 Debug suggestions:"
        [ "$SHORT" != "true" ] && echo "   - Check that the function is running: curl $FUNCTION_URL"
        [ "$SHORT" != "true" ] && echo "   - Verify environment variables: make logs"
        [ "$SHORT" != "true" ] && echo "   - Check function implementation for errors"
        [ "$SHORT" != "true" ] && echo "   - Ensure all required dependencies are installed"
        exit 1
    fi
}

# Helper for when tests are interrupted
cleanup_tests() {
    echo ""
    echo -e "${YELLOW}⚠️ Tests interrupted${NC}"
    finish_tests
}

# Set up signal handlers for clean exit
trap cleanup_tests INT TERM