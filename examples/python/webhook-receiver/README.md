# Webhook Receiver Example

A generic webhook receiver that can handle incoming webhooks from various services with signature verification.

## Features

- **HMAC-SHA256 Signature Verification**: Secure webhook processing
- **Multi-Source Support**: Handle webhooks from different services
- **In-Memory Storage**: Store and retrieve webhook history
- **Test Endpoints**: Built-in testing capabilities
- **Flexible Data Handling**: Support for JSON and text payloads

## API Endpoints

### GET /
Returns API information and available endpoints.

### GET /webhooks
List the last 10 received webhooks.

### POST /webhook
Receive a webhook with optional signature verification.

**Headers:**
- `x-webhook-signature`: HMAC-SHA256 signature (optional)
- `x-webhook-source`: Source identifier (optional)
- `content-type`: Content type (defaults to application/json)

### POST /webhook/test
Create a test webhook for testing purposes.

## Configuration

**Environment Variables:**
- `WEBHOOK_RECEIVER_SECRET` - Secret key for HMAC signature verification (optional)

## Example Usage

```bash
# Test the webhook receiver
curl https://your-function.dev.telnyxcompute.com/

# Send a test webhook
curl -X POST https://your-function.dev.telnyxcompute.com/webhook/test

# Send a webhook with data
curl -X POST https://your-function.dev.telnyxcompute.com/webhook \
  -H "Content-Type: application/json" \
  -H "x-webhook-source: git_platform" \
  -d '{"event": "push", "repository": "my-repo"}'

# List received webhooks
curl https://your-function.dev.telnyxcompute.com/webhooks
```

## Webhook Signature Format

This receiver expects webhook signatures in the following format:

- **Header**: `x-webhook-signature` 
- **Format**: `sha256=<hex-encoded-hmac>`
- **Algorithm**: HMAC-SHA256
- **Payload**: Raw request body (not JSON-parsed)

**Compatible Services:**
- Git platform webhooks (`X-Hub-Signature-256`)
- GitLab webhooks (`X-Gitlab-Token`) 
- Custom webhooks following HMAC-SHA256 standard

**Example signature generation:**
```python
import hmac
import hashlib

secret = "your-webhook-secret"
payload = '{"event": "test"}'
signature = hmac.new(
    secret.encode('utf-8'), 
    payload.encode('utf-8'), 
    hashlib.sha256
).hexdigest()
header_value = f"sha256={signature}"
```

**Note**: Some services use different header names or formats. Modify the signature verification logic in `func.py` if needed.

## Security

- Always use HTTPS endpoints in production
- Configure webhook secrets for signature verification
- Validate webhook sources and data structure
- Consider implementing rate limiting for production use

**Deployable on Telnyx Edge Compute**