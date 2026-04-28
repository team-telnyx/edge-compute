# Webhook Receiver (JavaScript)

A single-purpose edge function that ingests webhooks and verifies HMAC-SHA256 signatures. No external dependencies — uses only Node.js built-ins.

## How it works

The function uses the Knative `func` runtime convention: `module.exports` exports an object with `init()`, `handle()`, and `shutdown()` lifecycle hooks. The runtime calls `init()` once at startup and `handle(context, body)` for each request.

## Endpoints

| Method | Description |
|--------|-------------|
| `POST /` | Receive and verify a webhook |
| `GET /`  | List recent webhooks + service info |

## Deploy

```bash
telnyx-edge ship
```

## Receiving webhooks

```bash
# No signature verification (WEBHOOK_SECRET not set)
curl -X POST https://<your-function-url> \
  -H "Content-Type: application/json" \
  -d '{"event": "user.created", "user_id": "abc123"}'

# With HMAC-SHA256 signature
SECRET="your-signing-secret"
PAYLOAD='{"event":"order.paid","order_id":"ord_456"}'
SIG="sha256=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')"

curl -X POST https://<your-function-url> \
  -H "Content-Type: application/json" \
  -H "x-webhook-signature: $SIG" \
  -H "x-webhook-source: stripe" \
  -d "$PAYLOAD"
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_WEBHOOKS` | `500` | In-memory ring buffer size |
| `WEBHOOK_SECRET` | *(unset)* | HMAC secret — enables signature verification |

```bash
telnyx-edge secrets add WEBHOOK_SECRET "your-signing-secret"
```
