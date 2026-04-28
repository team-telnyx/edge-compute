#!/bin/bash

# Call Event Router Demo Suite (TypeScript)
# Tests discriminated union routing for Telnyx voice and messaging events

source "$(dirname "$0")/../../demo_wrapper.sh"

start_section "📞 Call Event Router — TypeScript" "Telnyx webhook event router using discriminated union types"

# 1. Service info
test_http_rich "GET" "/" "" "1️⃣ Service Info" \
    "GET / returns service metadata, total_processed count, and per-type breakdown" \
    "Shows the event log is empty before any events are processed"

# 2. call.initiated
test_http_rich "POST" "/" \
    '{"data":{"event_type":"call.initiated","id":"evt_1","occurred_at":"2026-01-01T12:00:00Z","payload":{"call_control_id":"ccc_1","call_leg_id":"leg_1","call_session_id":"sess_1","from":"+15550001111","to":"+15550002222","direction":"inbound","state":"parked"}}}' \
    "2️⃣ call.initiated Event" \
    "Inbound call started — TypeScript narrows TelnyxEvent to CallInitiatedEvent in the switch" \
    "handler receives typed payload: from, to, direction, call_control_id"

# 3. call.answered
test_http_rich "POST" "/" \
    '{"data":{"event_type":"call.answered","id":"evt_2","occurred_at":"2026-01-01T12:00:05Z","payload":{"call_control_id":"ccc_1","call_leg_id":"leg_1","from":"+15550001111","to":"+15550002222","state":"active"}}}' \
    "3️⃣ call.answered Event" \
    "Call was answered — union narrows to CallAnsweredEvent" \
    "Each handler is a separate typed function; no casting is needed in any branch"

# 4. call.hangup
test_http_rich "POST" "/" \
    '{"data":{"event_type":"call.hangup","id":"evt_3","occurred_at":"2026-01-01T12:01:30Z","payload":{"call_control_id":"ccc_1","call_leg_id":"leg_1","from":"+15550001111","to":"+15550002222","hangup_cause":"normal_clearing","hangup_source":"remote","sip_hangup_cause":"200"}}}' \
    "4️⃣ call.hangup Event" \
    "Call ended — hangup_source is typed as 'local' | 'remote' | 'system'" \
    "TypeScript enforces valid literal values at compile time"

# 5. message.received
test_http_rich "POST" "/" \
    '{"data":{"event_type":"message.received","id":"evt_4","occurred_at":"2026-01-01T12:02:00Z","payload":{"id":"msg_1","from":{"phone_number":"+15550001111"},"to":[{"phone_number":"+15550002222"}],"text":"Hello from Telnyx!","type":"SMS"}}}' \
    "5️⃣ message.received Event" \
    "Inbound SMS — MessageReceivedEvent has a completely different payload shape" \
    "TypeScript ensures each handler can only access fields that exist for its specific event"

# 6. Unsupported event type
test_http_status "POST" "/" \
    '{"data":{"event_type":"call.unknown","id":"evt_5","occurred_at":"2026-01-01T12:03:00Z","payload":{}}}' \
    "6️⃣ Unsupported Event Type Returns 422" 422 \
    "Unknown event types are rejected before reaching dispatch()" \
    "Runtime validation complements compile-time type safety"

# 7. Missing event_type
test_http_status "POST" "/" \
    '{"data":{"id":"evt_6"}}' \
    "7️⃣ Missing event_type Returns 400" 400 \
    "Payloads without data.event_type are rejected with a clear error" \
    "Input validation happens before any type assertion"

# 8. Final event log
test_http_rich "GET" "/" "" "8️⃣ Event Log After Processing" \
    "GET / now shows all processed events with per-type counts" \
    "total_processed should be 4; by_type shows call.initiated:1, call.answered:1, call.hangup:1, message.received:1"

# 9. Unsupported method
test_http_status "PUT" "/" "" "9️⃣ Unsupported Method Returns 405" 405 \
    "Only GET and POST are handled" \
    "Other methods return 405"

finish_tests_rich "The TypeScript call event router demonstrates discriminated union types — a TypeScript pattern that makes event handling both type-safe and exhaustive. Each Telnyx event type is an interface with event_type as a string literal. The union TelnyxEvent = CallInitiatedEvent | CallAnsweredEvent | CallHangupEvent | MessageReceivedEvent lets TypeScript narrow the type in each switch branch, giving each handler a fully typed payload with no casting required. The default: never guard turns unhandled event types into compile errors — you can't add a new event to the union without also adding a handler."
