# Function
import logging
import json
import csv
import io
import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import sqlite3
import threading
from typing import Dict, List, Any, Optional

# Constants
HTTP_SCOPE_TYPE = 'http'


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return Function()


class DataProcessor:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', '/tmp/data_processor.db')
        self.batch_size = int(os.getenv('BATCH_SIZE', '100'))
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    record_data TEXT NOT NULL,
                    status TEXT DEFAULT 'processed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    errors TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT UNIQUE NOT NULL,
                    total_records INTEGER DEFAULT 0,
                    processed_records INTEGER DEFAULT 0,
                    failed_records INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            logging.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise e

    def validate_record(self, record: Dict[str, str]) -> tuple[bool, List[str]]:
        """Validate a single CSV record"""
        errors = []

        # Required fields
        required_fields = ['name', 'email', 'age']
        for field in required_fields:
            if not record.get(field, '').strip():
                errors.append(f"Missing required field: {field}")

        # Email validation (basic)
        email = record.get('email', '')
        if email and '@' not in email:
            errors.append("Invalid email format")

        # Age validation
        age_str = record.get('age', '')
        if age_str:
            try:
                age = int(age_str)
                if age < 0 or age > 150:
                    errors.append("Age must be between 0 and 150")
            except ValueError:
                errors.append("Age must be a valid number")

        return len(errors) == 0, errors

    def process_csv_data(self, csv_content: str, batch_id: str) -> Dict[str, Any]:
        """Process CSV data and return results"""
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            records = list(csv_reader)

            # Create processing job
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO processing_jobs (batch_id, total_records, status)
                VALUES (?, ?, 'processing')
            ''', (batch_id, len(records)))
            conn.commit()

            processed_count = 0
            failed_count = 0
            errors = []

            # Process records in batches
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]

                for record in batch:
                    is_valid, record_errors = self.validate_record(record)

                    if is_valid:
                        # Transform data (example transformations)
                        transformed_record = {
                            'name': record['name'].strip().title(),
                            'email': record['email'].strip().lower(),
                            'age': int(record['age']),
                            'processed_at': datetime.utcnow().isoformat()
                        }

                        # Store processed record
                        cursor.execute('''
                            INSERT INTO processed_data (batch_id, record_data, status)
                            VALUES (?, ?, 'processed')
                        ''', (batch_id, json.dumps(transformed_record)))

                        processed_count += 1
                    else:
                        # Store failed record with errors
                        cursor.execute('''
                            INSERT INTO processed_data (batch_id, record_data, status, errors)
                            VALUES (?, ?, 'failed', ?)
                        ''', (batch_id, json.dumps(record), json.dumps(record_errors)))

                        failed_count += 1
                        errors.extend(record_errors)

                # Simulate processing time
                time.sleep(0.01)

            # Update job status
            cursor.execute('''
                UPDATE processing_jobs
                SET processed_records = ?, failed_records = ?,
                    status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE batch_id = ?
            ''', (processed_count, failed_count, batch_id))

            conn.commit()
            conn.close()

            return {
                'batch_id': batch_id,
                'total_records': len(records),
                'processed_records': processed_count,
                'failed_records': failed_count,
                'status': 'completed',
                'errors': errors[:10] if errors else []  # Limit error list
            }

        except Exception as e:
            logging.error(f"Processing error: {str(e)}")

            # Update job status to failed
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE processing_jobs
                SET status = 'failed', completed_at = CURRENT_TIMESTAMP
                WHERE batch_id = ?
            ''', (batch_id,))
            conn.commit()
            conn.close()

            raise e

    def get_job_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT batch_id, total_records, processed_records, failed_records,
                   status, started_at, completed_at
            FROM processing_jobs WHERE batch_id = ?
        ''', (batch_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'batch_id': row[0],
            'total_records': row[1],
            'processed_records': row[2],
            'failed_records': row[3],
            'status': row[4],
            'started_at': row[5],
            'completed_at': row[6]
        }

    def get_processed_data(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get processed data for a batch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT record_data, status, errors, created_at
            FROM processed_data WHERE batch_id = ?
            ORDER BY id
        ''', (batch_id,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            result = {
                'data': json.loads(row[0]),
                'status': row[1],
                'created_at': row[3]
            }
            if row[2]:  # errors
                result['errors'] = json.loads(row[2])
            results.append(result)

        return results


class Function:
    def __init__(self):
        """ The init method is an optional method where initialization can be
        performed. See the start method for a startup hook which includes
        configuration.
        """
        self.processor = DataProcessor()

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this Function other than readiness
        and liveness probes.

        This method is async because it uses the ASGI protocol for HTTP handling,
        which requires asynchronous send/receive operations.
        """

        # Validate ASGI scope for HTTP requests
        scope_request_type = scope.get('type')
        if scope_request_type is None or scope_request_type != HTTP_SCOPE_TYPE:
            logging.error("Invalid ASGI scope type: %s", scope_request_type)
            await self.send_json_response(send, 400, {
                'error': True,
                'message': 'Bad Request: Invalid scope type'
            })
            return

        logging.info("Processing HTTP request")

        # Get HTTP method and path from scope
        method = scope.get('method', 'GET')
        path = scope.get('path', '/')
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string) if query_string else {}

        try:
            if path == '/':
                await self.handle_root(send)
            elif path == '/health':
                await self.handle_health(send)
            elif path == '/jobs':
                await self.handle_list_jobs(send)
            elif path.startswith('/jobs/'):
                batch_id = path.split('/')[-1]
                if batch_id:
                    await self.handle_job_status(send, batch_id)
                else:
                    await self.send_json_response(send, 400, {"error": "Invalid batch ID"})
            elif path.startswith('/data/'):
                batch_id = path.split('/')[-1]
                if batch_id:
                    await self.handle_get_data(send, batch_id)
                else:
                    await self.send_json_response(send, 400, {"error": "Invalid batch ID"})
            elif path == '/process':
                await self.handle_process_data(scope, receive, send)
            elif path == '/process-async':
                await self.handle_process_async(scope, receive, send)
            else:
                await self.send_json_response(send, 404, {"error": "Endpoint not found"})
        except Exception as e:
            logging.error(f"Request handling error: {str(e)}")
            await self.send_json_response(send, 500, {"error": f"Internal server error: {str(e)}"})

    async def handle_root(self, send):
        """API documentation endpoint"""
        docs = {
            'service': 'Data Processor',
            'version': os.getenv('VERSION', '1.0.0'),
            'description': 'CSV data processing and validation service',
            'endpoints': [
                'GET  / - API documentation',
                'GET  /health - Health check',
                'POST /process - Process CSV data synchronously',
                'POST /process-async - Process CSV data asynchronously',
                'GET  /jobs - List processing jobs',
                'GET  /jobs/{batch_id} - Get job status',
                'GET  /data/{batch_id} - Get processed data'
            ],
            'formats': {
                'input': 'CSV data in request body',
                'output': 'JSON with processing results'
            }
        }
        await self.send_json_response(send, 200, docs)

    async def handle_health(self, send):
        """Health check endpoint"""
        try:
            # Test database connection
            conn = sqlite3.connect(self.processor.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM processing_jobs')
            job_count = cursor.fetchone()[0]
            conn.close()

            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': os.getenv('VERSION', '1.0.0'),
                'database': 'connected',
                'total_jobs': job_count,
                'configuration': {
                    'batch_size': self.processor.batch_size,
                    'max_file_size': self.processor.max_file_size
                }
            }
            await self.send_json_response(send, 200, health)

        except Exception as e:
            health = {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
            await self.send_json_response(send, 503, health)

    async def handle_process_data(self, scope, receive, send):
        """Process CSV data synchronously"""
        try:
            # Get content length from headers
            headers = dict(scope.get('headers', []))
            content_length = int(headers.get(b'content-length', 0))

            if content_length > self.processor.max_file_size:
                await self.send_json_response(send, 413, {"error": "File too large"})
                return

            if content_length == 0:
                await self.send_json_response(send, 400, {"error": "No data provided"})
                return

            # Read request body
            body = b''
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break

            csv_data = body.decode('utf-8')
            batch_id = f"batch_{int(time.time() * 1000)}"

            # Process data
            result = self.processor.process_csv_data(csv_data, batch_id)

            await self.send_json_response(send, 200, {
                'message': 'Data processed successfully',
                'result': result
            })

        except Exception as e:
            logging.error(f"Processing error: {str(e)}")
            await self.send_json_response(send, 500, {"error": f"Processing failed: {str(e)}"})

    async def handle_process_async(self, scope, receive, send):
        """Process CSV data asynchronously"""
        try:
            # Get content length from headers
            headers = dict(scope.get('headers', []))
            content_length = int(headers.get(b'content-length', 0))

            if content_length > self.processor.max_file_size:
                await self.send_json_response(send, 413, {"error": "File too large"})
                return

            # Read request body
            body = b''
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break

            csv_data = body.decode('utf-8')
            batch_id = f"batch_{int(time.time() * 1000)}"

            # Start processing in background thread
            thread = threading.Thread(
                target=self.processor.process_csv_data,
                args=(csv_data, batch_id)
            )
            thread.start()

            await self.send_json_response(send, 202, {
                'message': 'Processing started',
                'batch_id': batch_id,
                'status_url': f'/jobs/{batch_id}',
                'data_url': f'/data/{batch_id}'
            })

        except Exception as e:
            logging.error(f"Async processing error: {str(e)}")
            await self.send_json_response(send, 500, {"error": f"Failed to start processing: {str(e)}"})

    async def handle_job_status(self, send, batch_id: str):
        """Get job processing status"""
        job = self.processor.get_job_status(batch_id)

        if not job:
            await self.send_json_response(send, 404, {"error": "Job not found"})
            return

        await self.send_json_response(send, 200, job)

    async def handle_get_data(self, send, batch_id: str):
        """Get processed data for a job"""
        job = self.processor.get_job_status(batch_id)

        if not job:
            await self.send_json_response(send, 404, {"error": "Job not found"})
            return

        if job['status'] != 'completed':
            await self.send_json_response(send, 200, {
                'message': f"Job status: {job['status']}",
                'job': job
            })
            return

        data = self.processor.get_processed_data(batch_id)

        await self.send_json_response(send, 200, {
            'batch_id': batch_id,
            'job': job,
            'data': data
        })

    async def handle_list_jobs(self, send):
        """List recent processing jobs"""
        conn = sqlite3.connect(self.processor.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT batch_id, total_records, processed_records, failed_records,
                   status, started_at, completed_at
            FROM processing_jobs
            ORDER BY started_at DESC
            LIMIT 50
        ''')

        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'batch_id': row[0],
                'total_records': row[1],
                'processed_records': row[2],
                'failed_records': row[3],
                'status': row[4],
                'started_at': row[5],
                'completed_at': row[6]
            })

        conn.close()

        await self.send_json_response(send, 200, {'jobs': jobs})

    async def send_json_response(self, send, status: int, data: Any):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2, default=str).encode('utf-8')

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
                [b'access-control-allow-origin', b'*'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })

    def start(self, cfg):
        """ start is an optional method which is called when a new Function
        instance is started, such as when scaling up or during an update.
        Provided is a dictionary containing all environmental configuration.

        This method is synchronous (unlike handle) as it's a simple initialization hook.
        """
        logging.info("Data Processor function starting")
        
        # Log configuration details only in debug mode
        if os.getenv('DEBUG_MODE', '').lower() in ('true', '1', 'yes'):
            logging.info(f"Configuration received: {cfg}")
        else:
            logging.info(f"Configuration loaded with {len(cfg)} parameters")
        
        # Debug logging of environment variables
        if os.getenv('DEBUG_MODE', '').lower() in ('true', '1', 'yes'):
            env_vars = {k: v for k, v in os.environ.items() if not k.startswith('_')}
            logging.info(f"Environment variables: {env_vars}")
        else:
            logging.info(f"Configuration loaded with {len(os.environ)} environment variables")
        
        # Ensure database is initialized
        try:
            self.processor.init_database()
            logging.info("Database re-initialized successfully")
        except Exception as e:
            logging.error(f"Database re-initialization failed: {e}")

    def stop(self):
        """ stop is an optional method which is called when a function is
        stopped, such as when scaled down, updated, or manually canceled.
        """
        logging.info("Data Processor function stopping")