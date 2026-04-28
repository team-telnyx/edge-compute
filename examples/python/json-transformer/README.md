# JSON Transformer

A comprehensive JSON transformation service built for Telnyx Edge Compute platform. This example demonstrates various JSON manipulation techniques including case conversion, flattening, filtering, and custom transformations.

## Features

- **Case Conversion** - Transform between camelCase and snake_case
- **JSON Flattening** - Flatten nested JSON structures with custom separators
- **Data Filtering** - Filter data by field inclusion/exclusion and value conditions  
- **Data Aggregation** - Aggregate numeric data with various operations
- **Custom Transformations** - Apply flexible transformation rules
- **Transformation History** - Track all transformation operations

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/transformations` | List transformation history (last 20) |
| POST | `/transform` | Apply generic transformation with custom rules |
| POST | `/transform/camel-to-snake` | Convert camelCase to snake_case |
| POST | `/transform/snake-to-camel` | Convert snake_case to camelCase |
| POST | `/transform/flatten` | Flatten nested JSON structure |
| POST | `/transform/filter` | Filter JSON data by rules |
| POST | `/transform/aggregate` | Aggregate JSON data |

## Usage Examples

### Case Conversion

#### camelCase to snake_case
```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform/camel-to-snake \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe", 
    "userDetails": {
      "phoneNumber": "555-0123",
      "emailAddress": "john@example.com"
    }
  }'
```

#### snake_case to camelCase
```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform/snake-to-camel \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "user_details": {
      "phone_number": "555-0123", 
      "email_address": "john@example.com"
    }
  }'
```

### JSON Flattening

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform/flatten \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "profile": {
        "name": "John Doe",
        "contact": {
          "email": "john@example.com",
          "phone": "555-0123"
        }
      }
    },
    "separator": "."
  }'
```

Response:
```json
{
  "user.profile.name": "John Doe",
  "user.profile.contact.email": "john@example.com", 
  "user.profile.contact.phone": "555-0123"
}
```

### Data Filtering

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform/filter \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "age": 30,
      "email": "john@example.com",
      "salary": 75000,
      "department": "Engineering"
    },
    "filters": {
      "include_fields": ["name", "email", "department"],
      "value_filters": {
        "age": {"min": 25, "max": 65}
      }
    }
  }'
```

### Data Aggregation

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform/aggregate \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "revenue": 100000,
      "employees": 50,
      "products": 25
    },
    "aggregations": {
      "total_revenue": {"field": "revenue", "operation": "sum"},
      "avg_revenue_per_employee": {"field": "revenue", "operation": "avg"},
      "employee_count": {"field": "employees", "operation": "count"}
    }
  }'
```

### Custom Transformation

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/transform \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "firstName": "john",
      "lastName": "doe", 
      "userEmail": "JOHN@EXAMPLE.COM"
    },
    "rules": {
      "firstName": {"type": "format", "format": "uppercase"},
      "lastName": {"type": "format", "format": "uppercase"},
      "userEmail": {"type": "format", "format": "lowercase"}
    },
    "operation": "format_names"
  }'
```

## Transformation Rules

### Generic Transform Rules
- `rename`: Rename field to new name
- `convert_case`: Convert string case (snake/camel)
- `format`: Apply formatting (uppercase/lowercase)

### Filter Rules
- `include_fields`: Array of fields to include
- `exclude_fields`: Array of fields to exclude  
- `value_filters`: Object with field-specific value conditions
  - `min`/`max`: Numeric range filters
  - Direct value: Exact match filter

### Aggregation Operations
- `sum`: Sum numeric values
- `count`: Count non-null values  
- `avg`: Average numeric values
- `min`: Minimum numeric value
- `max`: Maximum numeric value
- `concat`: Concatenate string values

## Response Format

All transformations return:

```json
{
  "message": "Transformation completed successfully",
  "transformation_id": "transform_1640995200000",
  "operation": "camel-to-snake",
  "original_data": { /* input data */ },
  "transformed_data": { /* output data */ }
}
```

## Transformation History

```bash
# View transformation history
curl https://your-function.dev.telnyxcompute.com/transformations
```

Returns the last 20 transformations with metadata:
- Transformation ID and timestamp
- Operation type and rules applied
- Input/output data sizes
- Processing statistics

## Development

### Local Testing  

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
chmod +x test.sh
./test.sh
```

**Deployable on Telnyx Edge Compute**

## Common Use Cases

- **API Response Transformation** - Convert between different naming conventions
- **Data Migration** - Transform data formats during system migrations
- **ETL Pipelines** - Extract, transform, and load data processing  
- **API Integration** - Adapt data formats between different services
- **Data Cleaning** - Normalize and clean JSON data structures
- **Schema Conversion** - Transform between different JSON schemas

## Performance Notes

- In-memory processing suitable for moderate JSON sizes
- Recursive operations handle deeply nested structures
- Transformation history limited to last 20 operations
- Custom separators supported for flattening operations
- Error handling for malformed JSON and invalid rules

This example provides a flexible foundation for building JSON transformation services that can handle various data manipulation requirements in edge computing environments.