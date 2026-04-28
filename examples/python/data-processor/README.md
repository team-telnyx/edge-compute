# Data Processor

A comprehensive CSV data processing function built for Telnyx Edge Compute platform. This example demonstrates how to process, validate, and transform CSV data with both synchronous and asynchronous processing capabilities.

## Features

- **CSV Data Validation** - Comprehensive data validation with error reporting
- **Batch Processing** - Configurable batch sizes for efficient processing
- **Data Transformation** - Built-in data cleaning and formatting
- **SQLite Database** - Local data storage with job tracking
- **Async Processing** - Background processing with status monitoring
- **RESTful API** - Complete CRUD operations for data management

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API documentation and service info |
| GET | `/health` | Health check with database status |
| POST | `/process` | Process CSV data synchronously |
| POST | `/process-async` | Process CSV data asynchronously |
| GET | `/jobs` | List recent processing jobs |
| GET | `/jobs/{batch_id}` | Get job processing status |
| GET | `/data/{batch_id}` | Get processed data for a job |

## Environment Variables

Configure processing behavior:

**Environment Variables:**
- `DATABASE_PATH` - Database file location (default: in-memory)
- `BATCH_SIZE` - Records per batch (default: 100)
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 10MB)
- `DEBUG_MODE` - Enable debug logging (default: false, NEVER enable in production)

### ⚠️ Security Warning

**DEBUG_MODE**: When enabled, logs detailed configuration and environment variables that may contain sensitive information. **NEVER enable in production environments.**

## CSV Format Requirements

The processor expects CSV data with the following required fields:
- `name` - Full name (required)
- `email` - Email address (required, basic validation)  
- `age` - Age in years (required, 0-150 range)

Additional fields are preserved in the output.

### Example CSV Data

```csv
name,email,age,city
John Doe,john@example.com,30,New York
Jane Smith,jane@example.com,25,San Francisco
```

## Usage Examples

### Synchronous Processing

```bash
# Process CSV data and get immediate results
curl -X POST https://your-function.dev.telnyxcompute.com/process \
  -H "Content-Type: text/csv" \
  --data-binary @data.csv
```

### Asynchronous Processing

```bash
# Start processing job
curl -X POST https://your-function.dev.telnyxcompute.com/process-async \
  -H "Content-Type: text/csv" \
  --data-binary @large_data.csv

# Check job status
curl https://your-function.dev.telnyxcompute.com/jobs/batch_1640995200000

# Get processed data when complete
curl https://your-function.dev.telnyxcompute.com/data/batch_1640995200000
```

### Health Check

```bash
curl https://your-function.dev.telnyxcompute.com/health
```

### List Jobs

```bash
curl https://your-function.dev.telnyxcompute.com/jobs
```

## Response Formats

### Processing Response

```json
{
  "message": "Data processed successfully",
  "result": {
    "batch_id": "batch_1640995200000",
    "total_records": 100,
    "processed_records": 95,
    "failed_records": 5,
    "status": "completed",
    "errors": ["Missing required field: email", "Invalid age format"]
  }
}
```

### Job Status Response

```json
{
  "batch_id": "batch_1640995200000",
  "total_records": 100,
  "processed_records": 95,
  "failed_records": 5,
  "status": "completed",
  "started_at": "2021-12-31T12:00:00",
  "completed_at": "2021-12-31T12:01:30"
}
```

## Data Validation Rules

- **Name**: Must be non-empty string, title-cased in output
- **Email**: Must contain '@' symbol, lowercased in output
- **Age**: Must be integer between 0-150
- **Required Fields**: All three fields must be present

Invalid records are stored with error details and excluded from processed output.

## Development

### Local Testing

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests with sample data
chmod +x test.sh
./test.sh
```

**Deployable on Telnyx Edge Compute**

## Performance Characteristics

- **Batch Processing**: Configurable batch sizes (default: 100 records)
- **Memory Usage**: In-memory processing with SQLite storage
- **File Size Limits**: Configurable max file size (default: 10MB)
- **Async Processing**: Background threads for large datasets
- **Error Handling**: Graceful handling of malformed data

## Common Use Cases

- Customer data import and validation
- Sales data processing and transformation  
- Survey response data cleaning
- Financial transaction validation
- Inventory data synchronization
- CRM data migration

## Error Handling

The processor provides detailed error reporting:
- Field-level validation errors
- Data type conversion errors  
- Missing required field notifications
- File size limit violations
- Processing job failures with rollback

This example provides a robust foundation for building data processing pipelines that can handle various CSV formats and validation requirements.