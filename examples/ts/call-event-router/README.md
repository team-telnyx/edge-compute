# Call Event Router (TypeScript)

A Telnyx Edge Function that receives Telnyx voice and messaging webhook events and routes each to a typed handler using a **discriminated union**.

TypeScript's exhaustive `switch` guarantees at compile time that every supported event type is handled — adding a new event to the union without a matching case is a build error.

## Supported events

| Event type | Description |
|------------|-------------|
| `call.initiated` | Inbound or outbound call started |
| `call.answered` | Call was answered |
| `call.hangup` | Call ended — includes hangup cause and source |
| `message.received` | Inbound SMS or MMS |

## How it works

Each event type is an interface with `event_type` as a literal type:

```typescript
type TelnyxEvent =
  | CallInitiatedEvent   // { event_type: 'call.initiated', payload: CallInitiatedPayload }
  | CallAnsweredEvent    // { event_type: 'call.answered',  payload: CallAnsweredPayload  }
  | CallHangupEvent      // { event_type: 'call.hangup',    payload: CallHangupPayload   }
  | MessageReceivedEvent // { event_type: 'message.received', payload: ... }
```

The `dispatch()` function switches on `event.event_type`. TypeScript narrows the union at each branch, so handlers receive their specific typed payload without casting. The `default: never` guard causes a compile error if any union member is unhandled.

## Deploy

```bash
npm run build        # compile TypeScript → dist/
telnyx-edge ship
```

## Test with curl

```bash
# Simulate a call.initiated event
curl -X POST https://<your-function-url> \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "event_type": "call.initiated",
      "id": "evt_abc123",
      "occurred_at": "2026-01-01T12:00:00Z",
      "payload": {
        "call_control_id": "ccc_xyz",
        "call_leg_id": "leg_1",
        "call_session_id": "sess_1",
        "from": "+15550001111",
        "to": "+15550002222",
        "direction": "inbound",
        "state": "parked"
      }
    }
  }'

# Simulate an inbound SMS
curl -X POST https://<your-function-url> \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "event_type": "message.received",
      "id": "evt_def456",
      "occurred_at": "2026-01-01T12:01:00Z",
      "payload": {
        "id": "msg_1",
        "from": { "phone_number": "+15550001111" },
        "to": [{ "phone_number": "+15550002222" }],
        "text": "Hello from Telnyx!",
        "type": "SMS"
      }
    }
  }'

# View recent event log + per-type counts
curl https://<your-function-url>
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_EVENTS` | `500` | In-memory ring buffer size |

```bash
telnyx-edge secrets add TELNYX_WEBHOOK_SECRET "your-telnyx-webhook-secret"
```
