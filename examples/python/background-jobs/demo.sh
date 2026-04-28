#!/bin/bash

# Background Job Processor Test Script
# Tests job creation, monitoring, and management

set -e

echo "⚙️ Testing Background Job Processor Function"
echo "============================================="

# Check if function is running locally or deployed
if [ -z "$FUNCTION_URL" ]; then
    FUNCTION_URL="http://localhost:8080"
    echo "📍 Using local function URL: $FUNCTION_URL"
else
    echo "📍 Using deployed function URL: $FUNCTION_URL"
fi

echo ""

# Global variables for storing job IDs
DATA_JOB_ID=""
EMAIL_JOB_ID=""
IMAGE_JOB_ID=""

# Test 1: API Info
echo "1️⃣ Testing API info endpoint..."
curl -s "$FUNCTION_URL/" | python3 -m json.tool
echo -e "\n"

# Test 2: Health check
echo "2️⃣ Testing health check..."
curl -s "$FUNCTION_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 3: Create data processing job
echo "3️⃣ Creating data processing job..."
DATA_JOB_RESPONSE=$(curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "data_processing",
    "payload": {
      "records": [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200},
        {"id": 3, "name": "Carol", "value": 150},
        {"id": 4, "name": "Dave", "value": 300},
        {"id": 5, "name": "Eve", "value": 250}
      ]
    },
    "priority": 5
  }')

echo "$DATA_JOB_RESPONSE" | python3 -m json.tool

# Extract job ID
DATA_JOB_ID=$(echo "$DATA_JOB_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('job_id', ''))
except:
    print('')
" 2>/dev/null || echo "")

echo -e "\n"

# Test 4: Create email batch job
echo "4️⃣ Creating email batch job..."
EMAIL_JOB_RESPONSE=$(curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email_batch",
    "payload": {
      "recipients": [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "user4@example.com"
      ],
      "template": "welcome_email"
    },
    "priority": 3
  }')

echo "$EMAIL_JOB_RESPONSE" | python3 -m json.tool

# Extract job ID
EMAIL_JOB_ID=$(echo "$EMAIL_JOB_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('job_id', ''))
except:
    print('')
" 2>/dev/null || echo "")

echo -e "\n"

# Test 5: Create image resize job
echo "5️⃣ Creating image resize job..."
IMAGE_JOB_RESPONSE=$(curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image_resize",
    "payload": {
      "images": [
        "/uploads/photo1.jpg",
        "/uploads/photo2.png",
        "/uploads/photo3.gif"
      ],
      "target_size": "800x600"
    },
    "priority": 1
  }')

echo "$IMAGE_JOB_RESPONSE" | python3 -m json.tool

# Extract job ID
IMAGE_JOB_ID=$(echo "$IMAGE_JOB_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('job_id', ''))
except:
    print('')
" 2>/dev/null || echo "")

echo -e "\n"

# Test 6: Create report generation job
echo "6️⃣ Creating report generation job..."
curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "report_generation",
    "payload": {
      "report_type": "monthly_sales",
      "date_range": "2024-01"
    }
  }' | python3 -m json.tool
echo -e "\n"

# Test 7: Create cleanup job
echo "7️⃣ Creating cleanup job..."
curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "cleanup",
    "payload": {
      "cleanup_type": "temp_files",
      "days_old": 30
    }
  }' | python3 -m json.tool
echo -e "\n"

# Test 8: List all jobs
echo "8️⃣ Listing all jobs..."
curl -s "$FUNCTION_URL/jobs" | python3 -m json.tool
echo -e "\n"

# Test 9: Get specific job details
echo "9️⃣ Getting specific job details..."
if [ -n "$DATA_JOB_ID" ]; then
    echo "Data processing job details:"
    curl -s "$FUNCTION_URL/jobs/$DATA_JOB_ID" | python3 -m json.tool
else
    echo "❌ No data job ID available"
fi
echo -e "\n"

# Wait a moment for jobs to process
echo "⏳ Waiting for jobs to process..."
sleep 3
echo ""

# Test 10: Get updated job status
echo "🔟 Getting updated job status..."
if [ -n "$DATA_JOB_ID" ]; then
    echo "Updated data processing job status:"
    curl -s "$FUNCTION_URL/jobs/$DATA_JOB_ID" | python3 -m json.tool
else
    echo "❌ No data job ID available"
fi
echo -e "\n"

# Test 11: List jobs by status
echo "1️⃣1️⃣ Listing completed jobs..."
curl -s "$FUNCTION_URL/jobs?status=completed" | python3 -m json.tool
echo -e "\n"

# Test 12: List jobs by type
echo "1️⃣2️⃣ Listing email batch jobs..."
curl -s "$FUNCTION_URL/jobs?type=email_batch" | python3 -m json.tool
echo -e "\n"

# Test 13: Cancel a job (if still pending/running)
echo "1️⃣3️⃣ Testing job cancellation..."
if [ -n "$EMAIL_JOB_ID" ]; then
    echo "Attempting to cancel email job:"
    curl -s -X DELETE "$FUNCTION_URL/jobs/$EMAIL_JOB_ID" | python3 -m json.tool
else
    echo "❌ No email job ID available for cancellation test"
fi
echo -e "\n"

# Test 14: Get processing statistics
echo "1️⃣4️⃣ Getting processing statistics..."
curl -s "$FUNCTION_URL/stats" | python3 -m json.tool
echo -e "\n"

# Test 15: Test invalid job type
echo "1️⃣5️⃣ Testing invalid job type..."
curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "invalid_job_type",
    "payload": {}
  }' | python3 -m json.tool
echo -e "\n"

# Test 16: Test malformed job request
echo "1️⃣6️⃣ Testing malformed job request..."
curl -s -X POST "$FUNCTION_URL/jobs" \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}' | python3 -m json.tool
echo -e "\n"

# Test 17: Test non-existent job lookup
echo "1️⃣7️⃣ Testing non-existent job lookup..."
curl -s "$FUNCTION_URL/jobs/00000000-0000-0000-0000-000000000000" | python3 -m json.tool
echo -e "\n"

# Test 18: 404 handling
echo "1️⃣8️⃣ Testing 404 handling..."
curl -s "$FUNCTION_URL/nonexistent" | python3 -m json.tool
echo -e "\n"

# Final health check
echo "🏁 Final health check..."
curl -s "$FUNCTION_URL/health" | python3 -m json.tool
echo -e "\n"

echo "✅ All background job processor tests completed!"
echo ""
echo "💡 Usage examples:"
echo "   export FUNCTION_URL=https://your-function.dev.telnyxcompute.com"
echo "   ./test.sh"
echo ""
echo "📊 Job Types Available:"
echo "   • data_processing - Process data records"  
echo "   • email_batch - Send batch emails"
echo "   • image_resize - Resize images"
echo "   • report_generation - Generate reports"
echo "   • cleanup - Clean up old data"