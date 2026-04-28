# Background Job Processor Function
import logging
import json
import time
import threading
import queue
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import sqlite3
import os

# Constants
HTTP_SCOPE_TYPE = 'http'


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(Enum):
    DATA_PROCESSING = "data_processing"
    EMAIL_BATCH = "email_batch" 
    IMAGE_RESIZE = "image_resize"
    REPORT_GENERATION = "report_generation"
    CLEANUP = "cleanup"


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return BackgroundJobProcessor()


class JobWorker:
    """ Worker thread that processes background jobs.
    """
    def __init__(self, job_processor):
        self.job_processor = job_processor
        self.running = False
        self.thread = None

    def start(self):
        """ Start the worker thread.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._work_loop)
            self.thread.daemon = True
            self.thread.start()
            logging.info("Job worker started")

    def stop(self):
        """ Stop the worker thread.
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            logging.info("Job worker stopped")

    def _work_loop(self):
        """ Main work loop for processing jobs.
        """
        while self.running:
            try:
                # Get next job from queue (timeout to allow stopping)
                job = self.job_processor.job_queue.get(timeout=1.0)
                
                # Process the job
                self._process_job(job)
                
                # Mark queue task as done
                self.job_processor.job_queue.task_done()
                
            except queue.Empty:
                # Timeout occurred, continue loop
                continue
            except Exception as e:
                logging.error(f"Worker error: {e}")
                # Mark queue task as done even on error
                self.job_processor.job_queue.task_done()

    def _process_job(self, job: Dict[str, Any]):
        """ Process a single job.
        """
        job_id = job['id']
        job_type = job['type']
        
        try:
            logging.info(f"Processing job {job_id} of type {job_type}")
            
            # Update job status to running
            self.job_processor._update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())
            
            # Process based on job type
            if job_type == JobType.DATA_PROCESSING.value:
                self._process_data_job(job)
            elif job_type == JobType.EMAIL_BATCH.value:
                self._process_email_batch(job)
            elif job_type == JobType.IMAGE_RESIZE.value:
                self._process_image_resize(job)
            elif job_type == JobType.REPORT_GENERATION.value:
                self._process_report_generation(job)
            elif job_type == JobType.CLEANUP.value:
                self._process_cleanup(job)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Mark job as completed
            self.job_processor._update_job_status(
                job_id, JobStatus.COMPLETED, 
                completed_at=datetime.utcnow(),
                result={"message": "Job completed successfully"}
            )
            
        except Exception as e:
            logging.error(f"Job {job_id} failed: {e}")
            
            # Mark job as failed
            self.job_processor._update_job_status(
                job_id, JobStatus.FAILED,
                completed_at=datetime.utcnow(),
                error=str(e)
            )

    def _process_data_job(self, job: Dict[str, Any]):
        """ Process data processing job.
        """
        payload = job.get('payload', {})
        records = payload.get('records', [])
        
        # Simulate processing time
        time.sleep(2)
        
        # Process each record
        processed_count = 0
        for record in records:
            # Simulate record processing
            time.sleep(0.1)
            processed_count += 1
            
            # Update progress
            progress = (processed_count / len(records)) * 100
            self.job_processor._update_job_progress(job['id'], progress)
        
        logging.info(f"Processed {processed_count} records")

    def _process_email_batch(self, job: Dict[str, Any]):
        """ Process email batch job.
        """
        payload = job.get('payload', {})
        recipients = payload.get('recipients', [])
        template = payload.get('template', 'default')
        
        # Simulate email sending
        time.sleep(1)
        
        sent_count = 0
        for recipient in recipients:
            # Simulate email sending delay
            time.sleep(0.2)
            sent_count += 1
            
            # Update progress
            progress = (sent_count / len(recipients)) * 100
            self.job_processor._update_job_progress(job['id'], progress)
        
        logging.info(f"Sent {sent_count} emails using template '{template}'")

    def _process_image_resize(self, job: Dict[str, Any]):
        """ Process image resize job.
        """
        payload = job.get('payload', {})
        images = payload.get('images', [])
        target_size = payload.get('target_size', '800x600')
        
        # Simulate image processing
        time.sleep(1)
        
        processed_count = 0
        for image in images:
            # Simulate image resize time
            time.sleep(0.5)
            processed_count += 1
            
            # Update progress
            progress = (processed_count / len(images)) * 100
            self.job_processor._update_job_progress(job['id'], progress)
        
        logging.info(f"Resized {processed_count} images to {target_size}")

    def _process_report_generation(self, job: Dict[str, Any]):
        """ Process report generation job.
        """
        payload = job.get('payload', {})
        report_type = payload.get('report_type', 'summary')
        date_range = payload.get('date_range', 'last_30_days')
        
        # Simulate report generation stages
        stages = ['collecting_data', 'processing', 'formatting', 'finalizing']
        
        for i, stage in enumerate(stages):
            logging.info(f"Report generation: {stage}")
            time.sleep(1)
            
            # Update progress
            progress = ((i + 1) / len(stages)) * 100
            self.job_processor._update_job_progress(job['id'], progress)
        
        logging.info(f"Generated {report_type} report for {date_range}")

    def _process_cleanup(self, job: Dict[str, Any]):
        """ Process cleanup job.
        """
        payload = job.get('payload', {})
        cleanup_type = payload.get('cleanup_type', 'temp_files')
        days_old = payload.get('days_old', 7)
        
        # Simulate cleanup process
        time.sleep(3)
        
        # Update progress in stages
        for progress in [25, 50, 75, 100]:
            time.sleep(0.5)
            self.job_processor._update_job_progress(job['id'], progress)
        
        logging.info(f"Cleanup completed: {cleanup_type} older than {days_old} days")


class BackgroundJobProcessor:
    def __init__(self):
        """ Initialize the background job processor.
        """
        self.db_path = os.getenv('DATABASE_PATH', '/tmp/jobs.db')
        self.max_queue_size = int(os.getenv('MAX_QUEUE_SIZE', '1000'))
        self.worker_count = int(os.getenv('WORKER_COUNT', '3'))
        
        # Initialize job queue and workers
        self.job_queue = queue.Queue(maxsize=self.max_queue_size)
        self.workers = []
        
        # Initialize database
        self._init_database()

    def _init_database(self):
        """ Initialize SQLite database for job storage.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                progress REAL DEFAULT 0.0,
                result TEXT,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3
            )
        ''')

        conn.commit()
        conn.close()
        logging.info("Job database initialized")

    def _start_workers(self):
        """ Start worker threads.
        """
        for i in range(self.worker_count):
            worker = JobWorker(self)
            worker.start()
            self.workers.append(worker)
        
        logging.info(f"Started {self.worker_count} workers")

    def _stop_workers(self):
        """ Stop all worker threads.
        """
        for worker in self.workers:
            worker.stop()
        self.workers.clear()

    def _create_job(self, job_type: str, payload: Dict[str, Any], priority: int = 0) -> str:
        """ Create a new job and add it to the database.
        """
        job_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jobs (id, type, status, payload, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (job_id, job_type, JobStatus.PENDING.value, json.dumps(payload), priority))
        
        conn.commit()
        conn.close()
        
        return job_id

    def _queue_job(self, job_id: str):
        """ Queue a job for processing.
        """
        # Get job from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Job {job_id} not found")
        
        job = {
            'id': row[0],
            'type': row[1],
            'status': row[2],
            'payload': json.loads(row[3]),
            'priority': row[4]
        }
        
        try:
            self.job_queue.put(job, block=False)
        except queue.Full:
            raise ValueError("Job queue is full")

    def _update_job_status(self, job_id: str, status: JobStatus, **kwargs):
        """ Update job status in database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = ['status = ?']
        params = [status.value]
        
        for key, value in kwargs.items():
            if key in ['started_at', 'completed_at']:
                updates.append(f'{key} = ?')
                params.append(value.isoformat() if isinstance(value, datetime) else value)
            elif key in ['result', 'error']:
                updates.append(f'{key} = ?')
                params.append(json.dumps(value) if isinstance(value, dict) else value)
            elif key == 'retry_count':
                updates.append(f'{key} = ?')
                params.append(value)
        
        params.append(job_id)
        
        cursor.execute(f'UPDATE jobs SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
        conn.close()

    def _update_job_progress(self, job_id: str, progress: float):
        """ Update job progress.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET progress = ? WHERE id = ?', (progress, job_id))
        conn.commit()
        conn.close()

    def _get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """ Get job details by ID.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'type': row[1],
            'status': row[2],
            'payload': json.loads(row[3]),
            'priority': row[4],
            'created_at': row[5],
            'started_at': row[6],
            'completed_at': row[7],
            'progress': row[8],
            'result': json.loads(row[9]) if row[9] else None,
            'error': row[10],
            'retry_count': row[11],
            'max_retries': row[12]
        }

    def _list_jobs(self, status: Optional[str] = None, job_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """ List jobs with optional filtering.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM jobs'
        params = []
        conditions = []
        
        if status:
            conditions.append('status = ?')
            params.append(status)
        
        if job_type:
            conditions.append('type = ?')
            params.append(job_type)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append({
                'id': row[0],
                'type': row[1], 
                'status': row[2],
                'priority': row[4],
                'created_at': row[5],
                'started_at': row[6],
                'completed_at': row[7],
                'progress': row[8],
                'retry_count': row[11],
                'max_retries': row[12]
            })
        
        return jobs

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this background job processor.
        """
        # Validate ASGI scope for HTTP requests
        scope_request_type = scope.get('type')
        if scope_request_type is None or scope_request_type != HTTP_SCOPE_TYPE:
            logging.error("Invalid ASGI scope type: %s", scope_request_type)
            await send({
                'type': 'http.response.start',
                'status': 400,
                'headers': [[b'content-type', b'application/json']],
            })
            await send({
                'type': 'http.response.body',
                'body': json.dumps({"error": "Invalid request type"}).encode(),
            })
            return

        method = scope.get('method', 'GET')
        path = scope.get('path', '/')

        # Route handling
        if method == 'GET' and path == '/':
            await self._handle_info(send)
        elif method == 'GET' and path == '/health':
            await self._handle_health(send)
        elif method == 'POST' and path == '/jobs':
            await self._handle_create_job(scope, receive, send)
        elif method == 'GET' and path == '/jobs':
            await self._handle_list_jobs(scope, send)
        elif method == 'GET' and path.startswith('/jobs/') and len(path.split('/')) == 3:
            job_id = path.split('/')[-1]
            await self._handle_get_job(job_id, send)
        elif method == 'DELETE' and path.startswith('/jobs/') and len(path.split('/')) == 3:
            job_id = path.split('/')[-1]
            await self._handle_cancel_job(job_id, send)
        elif method == 'GET' and path == '/stats':
            await self._handle_stats(send)
        else:
            await self._handle_404(send)

    async def _handle_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "Background Job Processor",
            "version": "1.0.0",
            "description": "Asynchronous background job processing service",
            "endpoints": [
                "GET  / - API information",
                "GET  /health - Health check and system status",
                "POST /jobs - Create and queue a new job",
                "GET  /jobs - List jobs with optional filtering",
                "GET  /jobs/{job_id} - Get specific job details",
                "DELETE /jobs/{job_id} - Cancel a pending job",
                "GET  /stats - Get processing statistics"
            ],
            "job_types": [
                "data_processing - Process batches of data records",
                "email_batch - Send batch emails to recipients",
                "image_resize - Resize batches of images",
                "report_generation - Generate reports and documents",
                "cleanup - Clean up old files and data"
            ],
            "configuration": {
                "worker_count": self.worker_count,
                "max_queue_size": self.max_queue_size,
                "database_path": self.db_path
            }
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_health(self, send):
        """ Handle health check endpoint.
        """
        try:
            # Check database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM jobs')
            total_jobs = cursor.fetchone()[0]
            conn.close()

            # Check worker status
            active_workers = len([w for w in self.workers if w.running])
            queue_size = self.job_queue.qsize()

            health_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "workers": {
                    "active": active_workers,
                    "total": len(self.workers),
                    "status": "running" if active_workers > 0 else "stopped"
                },
                "queue": {
                    "size": queue_size,
                    "max_size": self.max_queue_size
                },
                "jobs": {
                    "total": total_jobs
                }
            }

            await self._send_json_response(send, 200, health_data)

        except Exception as e:
            await self._send_json_response(send, 503, {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _handle_create_job(self, scope, receive, send):
        """ Handle job creation endpoint.
        """
        try:
            body = await self._read_request_body(receive)
            job_data = json.loads(body.decode('utf-8'))

            job_type = job_data.get('type', '').strip()
            payload = job_data.get('payload', {})
            priority = job_data.get('priority', 0)

            # Validate job type
            valid_types = [jt.value for jt in JobType]
            if job_type not in valid_types:
                await self._send_json_response(send, 400, {
                    "error": "Invalid job type",
                    "message": f"Job type must be one of: {valid_types}"
                })
                return

            # Create job
            job_id = self._create_job(job_type, payload, priority)
            
            # Queue job for processing
            self._queue_job(job_id)

            await self._send_json_response(send, 201, {
                "message": "Job created and queued successfully",
                "job_id": job_id,
                "type": job_type,
                "status": "pending",
                "priority": priority
            })

        except queue.Full:
            await self._send_json_response(send, 503, {
                "error": "Job queue full",
                "message": "Cannot accept new jobs at this time"
            })
        except Exception as e:
            logging.error(f"Job creation error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Job creation failed",
                "message": str(e)
            })

    async def _handle_list_jobs(self, scope, send):
        """ Handle list jobs endpoint.
        """
        try:
            # Parse query parameters
            query_string = scope.get('query_string', b'').decode('utf-8')
            params = {}
            
            if query_string:
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value

            status = params.get('status')
            job_type = params.get('type')
            limit = min(int(params.get('limit', '50')), 200)  # Max 200 jobs

            jobs = self._list_jobs(status, job_type, limit)

            await self._send_json_response(send, 200, {
                "jobs": jobs,
                "total": len(jobs),
                "filters": {
                    "status": status,
                    "type": job_type,
                    "limit": limit
                }
            })

        except Exception as e:
            logging.error(f"List jobs error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to list jobs",
                "message": str(e)
            })

    async def _handle_get_job(self, job_id: str, send):
        """ Handle get job details endpoint.
        """
        try:
            job = self._get_job(job_id)
            
            if not job:
                await self._send_json_response(send, 404, {
                    "error": "Job not found",
                    "message": f"Job {job_id} does not exist"
                })
                return

            await self._send_json_response(send, 200, job)

        except Exception as e:
            logging.error(f"Get job error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to get job",
                "message": str(e)
            })

    async def _handle_cancel_job(self, job_id: str, send):
        """ Handle job cancellation endpoint.
        """
        try:
            job = self._get_job(job_id)
            
            if not job:
                await self._send_json_response(send, 404, {
                    "error": "Job not found",
                    "message": f"Job {job_id} does not exist"
                })
                return

            if job['status'] not in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
                await self._send_json_response(send, 400, {
                    "error": "Cannot cancel job",
                    "message": f"Job is in {job['status']} state"
                })
                return

            # Update job status to cancelled
            self._update_job_status(job_id, JobStatus.CANCELLED, completed_at=datetime.utcnow())

            await self._send_json_response(send, 200, {
                "message": "Job cancelled successfully",
                "job_id": job_id
            })

        except Exception as e:
            logging.error(f"Cancel job error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to cancel job",
                "message": str(e)
            })

    async def _handle_stats(self, send):
        """ Handle statistics endpoint.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get job counts by status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM jobs 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Get job counts by type
            cursor.execute('''
                SELECT type, COUNT(*) as count 
                FROM jobs 
                GROUP BY type
            ''')
            type_counts = dict(cursor.fetchall())
            
            # Get recent completion rate (last 24 hours)
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM jobs 
                WHERE created_at > datetime('now', '-1 day')
            ''')
            recent_stats = cursor.fetchone()
            
            conn.close()

            completion_rate = 0
            if recent_stats[0] > 0:
                completion_rate = (recent_stats[1] / recent_stats[0]) * 100

            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "recent_24h": {
                    "total_jobs": recent_stats[0],
                    "completed_jobs": recent_stats[1],
                    "completion_rate_percent": round(completion_rate, 2)
                },
                "system": {
                    "active_workers": len([w for w in self.workers if w.running]),
                    "queue_size": self.job_queue.qsize(),
                    "max_queue_size": self.max_queue_size
                }
            }

            await self._send_json_response(send, 200, stats)

        except Exception as e:
            logging.error(f"Stats error: {e}")
            await self._send_json_response(send, 500, {
                "error": "Failed to get stats",
                "message": str(e)
            })

    async def _read_request_body(self, receive):
        """ Read and return request body.
        """
        body = b''
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
        return body

    async def _handle_404(self, send):
        """ Handle 404 responses.
        """
        await self._send_json_response(send, 404, {
            "error": "Not found",
            "message": "Endpoint not found"
        })

    async def _send_json_response(self, send, status: int, data: Dict[str, Any]):
        """ Send JSON response.
        """
        response_body = json.dumps(data, indent=2, default=str)

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
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the background job processor.
        """
        logging.info("Background Job Processor starting")
        
        # Load configuration from environment
        self.db_path = cfg.get('DATABASE_PATH', self.db_path)
        self.max_queue_size = int(cfg.get('MAX_QUEUE_SIZE', str(self.max_queue_size)))
        self.worker_count = int(cfg.get('WORKER_COUNT', str(self.worker_count)))
        
        # Ensure database is initialized with updated config
        self._init_database()
        
        # Start worker threads if not already started
        if not self.workers:
            self._start_workers()
        
        logging.info(f"Job processor started with {self.worker_count} workers")

    def stop(self):
        """ Stop the background job processor.
        """
        logging.info("Background Job Processor stopping")
        
        # Stop workers
        self._stop_workers()
        
        # Wait for queue to empty (with timeout)
        try:
            self.job_queue.join()
        except:
            pass
            
        logging.info("Job processor stopped")