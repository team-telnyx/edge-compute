#!/bin/bash

# JSON Transformer Test Script
# Tests JSON transformation, field mapping, data filtering, and aggregation using enhanced test wrapper

# Load shared test wrapper with rich educational features
source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "🔄 JSON Transformation & Mapping" "Complete data transformation pipeline with field mapping and filtering"

# Test 1: API Documentation
test_http_rich "GET" "/" "" "1️⃣ Get API Documentation" \
    "Transformation APIs should clearly document available operations and data formats" \
    "Self-documenting transformation services help developers understand mapping capabilities and supported operations"

start_section "📝 Field Mapping & Restructuring" "Testing JSON structure transformation and field operations"

# Test 2: Simple Field Mapping
simple_mapping='{
  "data": {
    "first_name": "John",
    "last_name": "Doe", 
    "email_address": "john@example.com",
    "user_age": 30
  },
  "mapping": {
    "name": "{{first_name}} {{last_name}}",
    "email": "{{email_address}}",
    "age": "{{user_age}}"
  }
}'

test_http_rich "POST" "/transform" "$simple_mapping" "2️⃣ Simple Field Mapping" \
    "Testing basic field mapping and string interpolation" \
    "Field mapping enables data structure transformation between different API schemas and data formats"

# Test 3: Complex Nested Transformation
nested_transformation='{
  "data": {
    "user": {
      "profile": {
        "personal": {"name": "Jane Smith", "age": 28},
        "contact": {"email": "jane@example.com", "phone": "555-0123"}
      },
      "settings": {"notifications": true, "theme": "dark"}
    }
  },
  "mapping": {
    "user_name": "{{user.profile.personal.name}}",
    "user_email": "{{user.profile.contact.email}}",
    "contact_phone": "{{user.profile.contact.phone}}",
    "preferences": {
      "notifications_enabled": "{{user.settings.notifications}}",
      "ui_theme": "{{user.settings.theme}}"
    }
  }
}'

test_http_rich "POST" "/transform" "$nested_transformation" "3️⃣ Nested Data Transformation" \
    "Testing deep object traversal and hierarchical data restructuring" \
    "Nested transformations handle complex data structures and enable flattening or restructuring of hierarchical data"

start_section "🔍 Data Filtering & Validation" "Testing conditional logic and data validation"

# Test 4: Conditional Field Transformation
conditional_transform='{
  "data": {
    "items": [
      {"name": "Widget A", "price": 10.99, "category": "Electronics", "in_stock": true},
      {"name": "Widget B", "price": 0, "category": "Electronics", "in_stock": false},
      {"name": "Widget C", "price": 25.50, "category": "Home", "in_stock": true}
    ]
  },
  "mapping": {
    "available_items": "{{items | where: in_stock == true}}",
    "electronics": "{{items | where: category == Electronics}}",
    "priced_items": "{{items | where: price > 0}}"
  }
}'

test_http_rich "POST" "/transform" "$conditional_transform" "4️⃣ Conditional Data Filtering" \
    "Testing conditional logic and data filtering capabilities" \
    "Conditional transformations enable business logic application and data quality filtering"

start_section "📊 Data Aggregation & Analytics" "Testing mathematical operations and data summarization"

# Test 5: Aggregation Operations
aggregation_data='{
  "data": {
    "sales": [
      {"region": "North", "amount": 1000, "products": 25},
      {"region": "South", "amount": 1500, "products": 30}, 
      {"region": "East", "amount": 800, "products": 20},
      {"region": "West", "amount": 1200, "products": 28}
    ]
  },
  "mapping": {
    "total_sales": "{{sales | sum: amount}}",
    "total_products": "{{sales | sum: products}}",
    "average_sale": "{{sales | avg: amount}}",
    "top_region": "{{sales | max: amount | select: region}}"
  }
}'

test_http_rich "POST" "/transform" "$aggregation_data" "5️⃣ Data Aggregation Operations" \
    "Testing mathematical aggregation and statistical operations" \
    "Aggregation transforms enable real-time analytics and business intelligence from raw data streams"

start_section "🧹 Data Cleansing & Standardization" "Testing data normalization and cleanup operations"

# Test 6: Data Cleansing
data_cleansing='{
  "data": {
    "users": [
      {"email": " JOHN@EXAMPLE.COM ", "phone": "555-123-4567", "name": "john doe"},
      {"email": "jane@DOMAIN.com", "phone": "(555) 987-6543", "name": "JANE SMITH"}
    ]
  },
  "mapping": {
    "cleaned_users": {
      "email": "{{users.email | lower | trim}}",
      "phone": "{{users.phone | digits_only}}",
      "name": "{{users.name | title_case}}"
    }
  }
}'

test_http_rich "POST" "/transform" "$data_cleansing" "6️⃣ Data Cleansing & Normalization" \
    "Testing data standardization and cleanup operations" \
    "Data cleansing ensures consistent formats and removes inconsistencies from incoming data streams"

start_section "🚫 Error Handling & Edge Cases" "Testing transformation resilience and error recovery"

# Test 7: Invalid JSON Structure
test_http_rich "POST" "/transform" '{"invalid": json}' "7️⃣ Invalid JSON Handling" \
    "Testing malformed JSON input and error handling" \
    "Robust error handling prevents system failures from invalid input and provides clear diagnostic information" \
    400

# Test 8: Missing Field References
missing_fields='{
  "data": {"name": "John"},
  "mapping": {"full_info": "{{name}} - {{missing_field}} - {{another.nested.missing}}"}
}'

test_http_rich "POST" "/transform" "$missing_fields" "8️⃣ Missing Field References" \
    "Testing undefined field handling and graceful degradation" \
    "Missing field handling ensures transforms continue processing even when source data is incomplete"

# Test 9: Empty Data Processing
empty_data='{"data": {}, "mapping": {"result": "{{empty_field}}"}}'
test_http_rich "POST" "/transform" "$empty_data" "9️⃣ Empty Data Processing" \
    "Testing empty input handling and null value processing" \
    "Empty data handling ensures the transformation pipeline remains stable with missing or null inputs"

start_section "🔧 Advanced Features" "Testing complex transformation scenarios"

# Test 10: Health Check
test_http_rich "GET" "/health" "" "🔟 System Health Check" \
    "Verifying transformation service availability and system status" \
    "Health monitoring ensures transformation services are operational and ready to process data"

# Test 11: Invalid Endpoint
test_http_rich "GET" "/invalid" "" "1️⃣1️⃣ Test Invalid Endpoint" \
    "Testing 404 error handling for undefined routes" \
    "Proper endpoint validation provides clear feedback for incorrect API usage" \
    404

# Finish with comprehensive educational summary
finish_tests_rich "
• 🔄 **JSON Transformation**: Convert data structures between different formats and schemas
• 📝 **Field Mapping**: Map and restructure JSON fields with flexible template syntax
• 🔍 **Data Filtering**: Apply conditional logic and business rules to filter datasets
• 📊 **Aggregation Operations**: Perform mathematical operations and statistical analysis on data
• 🧹 **Data Cleansing**: Standardize and normalize data formats for consistency
• 🎯 **Template Engine**: Use powerful templating for complex data transformations
• 🔧 **Error Recovery**: Handle malformed data and missing fields gracefully
• 📈 **Performance**: Efficient processing of large JSON datasets with streaming support
• 🏗️ **Extensible Design**: Framework for custom transformation functions and operations  
• 📚 **Production Ready**: Includes validation, error handling, and monitoring capabilities
"