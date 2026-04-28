# Webhook Receiver Function
import logging
import json
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Constants
HTTP_SCOPE_TYPE = 'http'


def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return WebhookReceiver()


class WebhookReceiver:
    def __init__(self):
        """ Initialize the webhook receiver with in-memory storage.
        """
        self.webhooks = []  # In-memory storage for demo purposes
        self.webhook_secret = None  # Will be set from config

    def _verify_signature(self, body: bytes, signature: str) -> bool:
        """ Verify webhook signature using HMAC-SHA256.
        """
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this webhook receiver.
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
        elif method == 'GET' and path == '/webhooks':
            await self._handle_list_webhooks(send)
        elif method == 'POST' and path == '/webhook':
            await self._handle_webhook_receive(scope, receive, send)
        elif method == 'POST' and path == '/webhook/test':
            await self._handle_test_webhook(send)
        else:
            await self._handle_404(send)

    async def _handle_info(self, send):
        """ Handle API info endpoint.
        """
        response_data = {
            "service": "Webhook Receiver",
            "version": "1.0.0",
            "description": "Generic webhook receiver for processing incoming webhooks",
            "endpoints": [
                "GET  / - API information",
                "GET  /webhooks - List received webhooks",
                "POST /webhook - Receive webhook (with signature verification)",
                "POST /webhook/test - Send test webhook"
            ],
            "features": [
                "HMAC-SHA256 signature verification",
                "Webhook logging and storage",
                "Multiple webhook source support"
            ]
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_list_webhooks(self, send):
        """ Handle listing received webhooks.
        """
        response_data = {
            "webhooks": self.webhooks[-10:],  # Return last 10 webhooks
            "total_received": len(self.webhooks)
        }

        await self._send_json_response(send, 200, response_data)

    async def _handle_webhook_receive(self, scope, receive, send):
        """ Handle incoming webhook with signature verification.
        """
        try:
            # Read request body
            body = b''
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break

            # Get headers
            headers = dict(scope.get('headers', []))
            signature = headers.get(b'x-webhook-signature', b'').decode('utf-8')
            webhook_source = headers.get(b'x-webhook-source', b'unknown').decode('utf-8')
            content_type = headers.get(b'content-type', b'application/json').decode('utf-8')

            # Verify signature if secret is configured
            if self.webhook_secret and not self._verify_signature(body, signature):
                await self._send_json_response(send, 401, {
                    "error": "Invalid signature",
                    "message": "Webhook signature verification failed"
                })
                return

            # Parse webhook data
            try:
                webhook_data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                webhook_data = body.decode('utf-8', errors='replace')

            # Store webhook
            webhook_entry = {
                "id": f"webhook_{int(time.time() * 1000)}",
                "timestamp": datetime.utcnow().isoformat(),
                "source": webhook_source,
                "content_type": content_type,
                "signature_verified": bool(self.webhook_secret),
                "data": webhook_data
            }

            self.webhooks.append(webhook_entry)

            logging.info(f"Received webhook from {webhook_source}")

            await self._send_json_response(send, 200, {
                "message": "Webhook received successfully",
                "webhook_id": webhook_entry["id"],
                "timestamp": webhook_entry["timestamp"]
            })

        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            await self._send_json_response(send, 500, {
                "error": "Internal server error",
                "message": str(e)
            })

    async def _handle_test_webhook(self, send):
        """ Handle sending a test webhook.
        """
        test_webhook = {
            "id": f"test_{int(time.time() * 1000)}",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "test",
            "content_type": "application/json",
            "signature_verified": False,
            "data": {
                "event": "test",
                "message": "This is a test webhook",
                "payload": {
                    "user_id": "12345",
                    "action": "test_event",
                    "metadata": {
                        "source": "telnyx-edge-test",
                        "environment": "development"
                    }
                }
            }
        }

        self.webhooks.append(test_webhook)

        await self._send_json_response(send, 200, {
            "message": "Test webhook created",
            "webhook_id": test_webhook["id"],
            "data": test_webhook["data"]
        })

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
        response_body = json.dumps(data, indent=2)

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [b'content-type', b'application/json'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body.encode(),
        })

    def start(self, cfg):
        """ Start the webhook receiver and load configuration.
        """
        logging.info("Webhook Receiver starting")
        
        # Load webhook secret from environment or config
        self.webhook_secret = cfg.get('WEBHOOK_RECEIVER_SECRET') or cfg.get('WEBHOOK_SECRET') or cfg.get('webhook_secret')
        
        if self.webhook_secret:
            logging.info("Webhook signature verification enabled")
        else:
            logging.warning("No webhook secret configured - signature verification disabled")

    def stop(self):
        """ Stop the webhook receiver.
        """
        logging.info("Webhook Receiver stopping")
        logging.info(f"Processed {len(self.webhooks)} webhooks during this session")