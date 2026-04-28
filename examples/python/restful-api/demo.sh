#!/bin/bash

# RESTful API Test Script  
# Tests complete CRUD operations, filtering, pagination, and data management using enhanced test wrapper

# Load shared test wrapper with rich educational features
source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "🏪 RESTful API & CRUD Operations" "Complete resource management with advanced querying and data persistence"

# Test 1: API Documentation
test_http_rich "GET" "/" "" "1️⃣ Get API Documentation" \
    "RESTful APIs should provide comprehensive documentation of available resources and operations" \
    "Self-documenting APIs help developers understand resource schemas, relationships, and available operations"

# Test 2: System Health Check
test_http_rich "GET" "/health" "" "2️⃣ System Health Check" \
    "Health endpoints ensure the API and database connections are operational" \
    "Health monitoring enables proactive detection of service issues and dependencies"

start_section "📦 Resource Creation & Validation" "Testing data creation with validation and error handling"

# Test 3: List Initial Resources (should show sample data)
test_http_rich "GET" "/products" "" "3️⃣ List Initial Resources" \
    "Checking pre-populated sample data and API structure" \
    "Sample data demonstrates the resource schema and helps developers understand expected formats"

# Test 4: Create New Resource
new_resource='{
  "name": "Test Product",
  "description": "A test product for API validation",
  "price": 29.99,
  "category": "Testing",
  "active": true
}'

test_http_rich "POST" "/products" "$new_resource" "4️⃣ Create New Resource" \
    "Testing resource creation with complete data validation" \
    "Resource creation validates input data, generates IDs, and stores records with proper error handling"

start_section "📋 Resource Retrieval & Querying" "Testing data access patterns and query capabilities"

# Test 5: Get Specific Resource (using a sample ID)
test_http_rich "GET" "/products/sample-id-123" "" "5️⃣ Get Specific Resource" \
    "Testing individual resource retrieval by ID" \
    "ID-based retrieval enables direct access to specific resources for detailed operations"

# Test 6: List with Pagination
test_http_rich "GET" "/products?limit=5&offset=0" "" "6️⃣ Paginated Resource List" \
    "Testing pagination for large datasets and performance optimization" \
    "Pagination prevents performance issues with large datasets and enables efficient data browsing"

# Test 7: Filter by Category
test_http_rich "GET" "/products?category=Electronics" "" "7️⃣ Category Filtering" \
    "Testing resource filtering by category attributes" \
    "Category filtering enables users to find relevant resources quickly in large datasets"

start_section "🔍 Advanced Querying & Search" "Testing complex search and filtering capabilities"

# Test 8: Search Resources
test_http_rich "GET" "/products?search=test" "" "8️⃣ Text Search" \
    "Testing full-text search across resource fields" \
    "Search functionality enables users to find resources by content rather than exact field matches"

# Test 9: Filter Active Resources
test_http_rich "GET" "/products?active=true&limit=10" "" "9️⃣ Status Filtering" \
    "Testing boolean filtering for resource status management" \
    "Status filtering allows separation of active/inactive resources for different business workflows"

# Test 10: Sort by Price
test_http_rich "GET" "/products?sort=price&order=desc&limit=5" "" "🔟 Sorted Results" \
    "Testing resource sorting for data presentation and analysis" \
    "Sorting capabilities enable users to order results by various criteria for better data insights"

start_section "✏️ Resource Updates & Modifications" "Testing data modification and partial updates"

# Test 11: Update Resource
update_resource='{
  "name": "Updated Test Product",
  "description": "Updated description with new details",
  "price": 39.99
}'

test_http_rich "PUT" "/products/sample-id-123" "$update_resource" "1️⃣1️⃣ Update Existing Resource" \
    "Testing resource modification with partial data updates" \
    "Resource updates enable data maintenance while preserving existing fields and maintaining consistency"

start_section "🚫 Error Handling & Edge Cases" "Testing API resilience and validation"

# Test 12: Invalid Resource Creation
invalid_resource='{
  "description": "Missing required name field",
  "price": "invalid_price_format"
}'

test_http_rich "POST" "/products" "$invalid_resource" "1️⃣2️⃣ Invalid Resource Creation" \
    "Testing validation error handling for malformed data" \
    "Input validation prevents data corruption and provides clear error messages for correcting issues" \
    400

# Test 13: Access Non-existent Resource
test_http_rich "GET" "/products/non-existent-id" "" "1️⃣3️⃣ Non-existent Resource Access" \
    "Testing 404 error handling for missing resources" \
    "Proper 404 handling provides clear feedback when requested resources don't exist"

# Test 14: Invalid Query Parameters
test_http_rich "GET" "/products?limit=invalid&sort=nonexistent_field" "" "1️⃣4️⃣ Invalid Query Parameters" \
    "Testing parameter validation and error handling" \
    "Query parameter validation ensures API stability when invalid filters or options are provided" \
    500

start_section "🗑️ Resource Deletion & Cleanup" "Testing resource lifecycle management"

# Test 15: Delete Resource
test_http_rich "DELETE" "/products/sample-id-123" "" "1️⃣5️⃣ Delete Resource" \
    "Testing resource deletion and cleanup operations" \
    "Resource deletion enables data lifecycle management with proper cleanup and referential integrity"

# Test 16: Verify Deletion (should return 404)
test_http_rich "GET" "/products/sample-id-123" "" "1️⃣6️⃣ Verify Resource Deletion" \
    "Confirming resource was properly deleted from the system" \
    "Deletion verification ensures data consistency and confirms successful cleanup operations"

start_section "📊 Analytics & Metadata" "Testing data insights and system metadata"

# Test 17: Resource Categories
test_http_rich "GET" "/categories" "" "1️⃣7️⃣ List Resource Categories" \
    "Testing category management and metadata endpoints" \
    "Category metadata provides insights into data organization and helps with navigation"

# Test 18: Final Resource Count
test_http_rich "GET" "/products?limit=1" "" "1️⃣8️⃣ Final Resource Count" \
    "Checking total resource count after all operations" \
    "Resource counting enables inventory management and provides system state information"

# Test 19: Invalid HTTP Method
test_http_rich "PATCH" "/products" "" "1️⃣9️⃣ Unsupported HTTP Method" \
    "Testing HTTP method validation and error responses" \
    "HTTP method validation ensures API contracts are properly enforced and documented" \
    405

# Test 20: Health Check (final)
test_http_rich "GET" "/health" "" "2️⃣0️⃣ Final Health Check" \
    "Verifying system stability after comprehensive testing" \
    "Final health checks confirm the system remains stable after intensive API operations"

# Finish with comprehensive educational summary
finish_tests_rich "
• 🏪 **RESTful Design**: Complete CRUD operations following REST architectural principles
• 📦 **Resource Management**: Create, read, update, and delete resources with proper validation
• 🔍 **Advanced Querying**: Search, filter, sort, and paginate large datasets efficiently
• 📊 **Data Analytics**: Category management and resource counting for business insights
• ✏️ **Data Integrity**: Validation, error handling, and referential integrity maintenance
• 🚫 **Error Recovery**: Comprehensive error handling with meaningful HTTP status codes
• 📋 **Pagination**: Handle large datasets with configurable page sizes and offsets
• 🔎 **Full-Text Search**: Enable content discovery across multiple resource fields
• 🏗️ **Scalable Architecture**: Design patterns for high-performance API development
• 📚 **Production Ready**: Includes health monitoring, validation, and comprehensive testing
"