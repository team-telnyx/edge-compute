# Background Job Processor

A comprehensive asynchronous background job processing service built for Telnyx Edge Compute platform. This example demonstrates how to implement a scalable job queue system with worker threads, job persistence, and progress tracking.

## Features

- **Asynchronous Job Processing** - Multi-threaded workers process jobs in background
- **Job Queue Management** - In-memory queue with configurable size limits
- **Job Persistence** - SQLite database storage for job state and history
- **Progress Tracking** - Real-time progress updates for long-running jobs
- **Job Types** - Multiple built-in job types with extensible architecture
- **Priority Scheduling** - Job prioritization and queue ordering
- **Job Cancellation** - Cancel pending or running jobs
- **Statistics & Monitoring** - Comprehensive job processing metrics

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API information and configuration |
| GET | `/health` | Health check with worker and queue status |
| POST | `/jobs` | Create and queue a new background job |
| GET | `/jobs` | List jobs with optional filtering |
| GET | `/jobs/{job_id}` | Get specific job details and progress |
| DELETE | `/jobs/{job_id}` | Cancel a pending or running job |
| GET | `/stats` | Get processing statistics and metrics |

## Supported Job Types

### 1. Data Processing (`data_processing`)
Process batches of data records with progress tracking.

### 2. Email Batch (`email_batch`) 
Send batch emails to multiple recipients using templates.

### 3. Image Resize (`image_resize`)
Resize batches of images to specified dimensions.

### 4. Report Generation (`report_generation`)
Generate reports and documents with multi-stage processing.

### 5. Cleanup (`cleanup`)
Clean up old files and data with configurable retention policies.

## Environment Variables

Configure job processor behavior:

**Environment Variables:**
- `WORKER_COUNT` - Number of worker threads (default: 3)
- `MAX_QUEUE_SIZE` - Maximum jobs in queue (default: 1000)
- `DATABASE_PATH` - SQLite database path (default: in-memory)

## Usage Examples

### Create a Data Processing Job

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "data_processing",
    "payload": {
      "records": [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200},
        {"id": 3, "name": "Carol", "value": 150}
      ]
    },
    "priority": 5
  }'
```

### Create an Email Batch Job

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email_batch",
    "payload": {
      "recipients": [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
      ],
      "template": "welcome_email"
    }
  }'
```

### Create an Image Resize Job

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image_resize",
    "payload": {
      "images": [
        "/uploads/image1.jpg",
        "/uploads/image2.png", 
        "/uploads/image3.gif"
      ],
      "target_size": "800x600"
    }
  }'
```

### Create a Report Generation Job

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "report_generation",
    "payload": {
      "report_type": "monthly_sales",
      "date_range": "2024-01"
    }
  }'
```

### Create a Cleanup Job

```bash
curl -X POST https://your-function.dev.telnyxcompute.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "cleanup",
    "payload": {
      "cleanup_type": "temp_files",
      "days_old": 30
    }
  }'
```

## Job Monitoring

### List All Jobs

```bash
curl https://your-function.dev.telnyxcompute.com/jobs
```

### List Jobs by Status

```bash
# List only completed jobs
curl "https://your-function.dev.telnyxcompute.com/jobs?status=completed"

# List only running jobs  
curl "https://your-function.dev.telnyxcompute.com/jobs?status=running"
```

### List Jobs by Type

```bash
curl "https://your-function.dev.telnyxcompute.com/jobs?type=email_batch"
```

### Get Job Details

```bash
curl https://your-function.dev.telnyxcompute.com/jobs/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "data_processing",
  "status": "running",
  "payload": { /* job payload */ },
  "priority": 5,
  "created_at": "2024-01-01T12:00:00.000000",
  "started_at": "2024-01-01T12:00:05.000000",
  "progress": 65.5,
  "retry_count": 0,
  "max_retries": 3
}
```

### Cancel a Job

```bash
curl -X DELETE https://your-function.dev.telnyxcompute.com/jobs/550e8400-e29b-41d4-a716-446655440000
```

## System Monitoring

### Health Check

```bash
curl https://your-function.dev.telnyxcompute.com/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "database": "connected",
  "workers": {
    "active": 3,
    "total": 3,
    "status": "running"
  },
  "queue": {
    "size": 15,
    "max_size": 1000
  },
  "jobs": {
    "total": 150
  }
}
```

### Processing Statistics

```bash
curl https://your-function.dev.telnyxcompute.com/stats
```

Response:
```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "status_distribution": {
    "completed": 120,
    "running": 5,
    "pending": 10,
    "failed": 2
  },
  "type_distribution": {
    "data_processing": 80,
    "email_batch": 30,
    "image_resize": 15,
    "report_generation": 10,
    "cleanup": 2
  },
  "recent_24h": {
    "total_jobs": 45,
    "completed_jobs": 42,
    "completion_rate_percent": 93.33
  },
  "system": {
    "active_workers": 3,
    "queue_size": 10,
    "max_queue_size": 1000
  }
}
```

## Job States

- **pending** - Job created and queued for processing
- **running** - Job currently being processed by a worker
- **completed** - Job finished successfully
- **failed** - Job failed due to an error
- **cancelled** - Job was cancelled before completion

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

## Architecture

### Components

- **Job Queue**: Thread-safe in-memory queue for pending jobs
- **Worker Threads**: Configurable number of background workers
- **SQLite Database**: Persistent storage for job state and history
- **Job Types**: Extensible job processing implementations
- **Progress Tracking**: Real-time progress updates
- **Statistics Engine**: Processing metrics and monitoring

### Scalability

- **Horizontal Scaling**: Multiple function instances can process different job types
- **Vertical Scaling**: Increase worker count for CPU-bound workloads
- **Queue Management**: Configurable queue sizes prevent memory issues
- **Database Optimization**: Indexes on job status and timestamps for fast queries

## Common Use Cases

- **Data ETL Pipelines** - Extract, transform, and load data processing
- **Email Marketing** - Batch email sending with template processing
- **Media Processing** - Image/video resizing and format conversion
- **Report Generation** - Scheduled report creation and delivery
- **System Maintenance** - Automated cleanup and housekeeping tasks
- **Webhook Processing** - Asynchronous webhook payload processing
- **File Processing** - Batch file operations and transformations

## Performance Considerations

- **Worker Threads**: More workers = higher concurrency but more memory usage
- **Queue Size**: Larger queues handle traffic spikes but use more memory
- **Database Location**: File-based SQLite for persistence, in-memory for speed
- **Job Payload Size**: Large payloads may impact queue performance
- **Progress Updates**: Frequent progress updates may affect processing speed

This example provides a robust foundation for building scalable background job processing systems in edge computing environments.