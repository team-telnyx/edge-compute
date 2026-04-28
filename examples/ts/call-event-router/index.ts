/**
 * Telnyx Call Event Router — TypeScript Edge Function
 *
 * Receives Telnyx voice and messaging webhook events and routes each to a
 * typed handler using a discriminated union.  TypeScript's exhaustive switch
 * ensures every event type is handled at compile time.
 *
 * Runtime convention (Knative func):
 *   export = { init(), handle(context, body), shutdown() }
 */

import * as crypto from 'crypto';

// ---------------------------------------------------------------------------
// Runtime context interface (provided by the faas-js-runtime)
// ---------------------------------------------------------------------------

interface Logger {
  info(msg: string, data?: Record<string, unknown>): void;
  warn(msg: string, data?: Record<string, unknown>): void;
  error(msg: string, data?: Record<string, unknown>): void;
}

interface Context {
  log: Logger;
  method: string;
  headers: Record<string, string | string[] | undefined>;
  query: Record<string, string>;
  rawBody?: Buffer; // raw request bytes — set by app.js wrapper for HMAC verification
}

interface FunctionResponse {
  statusCode: number;
  body: unknown;
}

// ---------------------------------------------------------------------------
// Telnyx event payload shapes
// ---------------------------------------------------------------------------

interface CallInitiatedPayload {
  call_control_id: string;
  call_leg_id: string;
  call_session_id: string;
  from: string;
  to: string;
  direction: 'inbound' | 'outbound';
  state: 'parked';
}

interface CallAnsweredPayload {
  call_control_id: string;
  call_leg_id: string;
  from: string;
  to: string;
  state: 'active';
}

interface CallHangupPayload {
  call_control_id: string;
  call_leg_id: string;
  from: string;
  to: string;
  hangup_cause: string;
  hangup_source: 'local' | 'remote' | 'system';
  sip_hangup_cause: string;
}

interface MessageReceivedPayload {
  id: string;
  from: { phone_number: string };
  to: Array<{ phone_number: string }>;
  text: string;
  type: 'SMS' | 'MMS';
}

// ---------------------------------------------------------------------------
// Discriminated union — event_type is the discriminant (direct property)
// so TypeScript can narrow the union inside the switch statement below.
// ---------------------------------------------------------------------------

interface CallInitiatedEvent {
  event_type: 'call.initiated';
  id: string;
  occurred_at: string;
  payload: CallInitiatedPayload;
}

interface CallAnsweredEvent {
  event_type: 'call.answered';
  id: string;
  occurred_at: string;
  payload: CallAnsweredPayload;
}

interface CallHangupEvent {
  event_type: 'call.hangup';
  id: string;
  occurred_at: string;
  payload: CallHangupPayload;
}

interface MessageReceivedEvent {
  event_type: 'message.received';
  id: string;
  occurred_at: string;
  payload: MessageReceivedPayload;
}

type TelnyxEvent =
  | CallInitiatedEvent
  | CallAnsweredEvent
  | CallHangupEvent
  | MessageReceivedEvent;

// Telnyx wraps events in a `data` envelope
interface TelnyxWebhook {
  data: TelnyxEvent;
}

// ---------------------------------------------------------------------------
// Webhook signature verification
// ---------------------------------------------------------------------------

let webhookSecret = '';

/**
 * Verify an HMAC-SHA256 webhook signature.
 * Expected header format: "sha256=<hex-digest>"
 * rawBody must be the original request bytes — never re-serialised JSON.
 */
function verifySignature(rawBody: Buffer, signature: string): boolean {
  if (!webhookSecret) return true; // verification disabled
  const expected = 'sha256=' + crypto
    .createHmac('sha256', webhookSecret)
    .update(rawBody)
    .digest('hex');
  try {
    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Processed event log
// ---------------------------------------------------------------------------

interface ProcessedEvent {
  id: string;
  event_type: string;
  processed_at: string;
  summary: string;
}

const processed: ProcessedEvent[] = [];
const MAX_EVENTS = parseInt(process.env.MAX_EVENTS ?? '500', 10);

function record(event: TelnyxEvent, summary: string): void {
  processed.push({
    id: event.id,
    event_type: event.event_type,
    processed_at: new Date().toISOString(),
    summary,
  });
  if (processed.length > MAX_EVENTS) processed.shift();
}

// ---------------------------------------------------------------------------
// Per-event-type handlers — each receives a fully typed payload
// ---------------------------------------------------------------------------

function handleCallInitiated(event: CallInitiatedEvent): string {
  const { from, to, direction, call_control_id } = event.payload;
  return `${direction === 'inbound' ? 'Inbound' : 'Outbound'} call from ${from} to ${to} [${call_control_id}]`;
}

function handleCallAnswered(event: CallAnsweredEvent): string {
  const { from, to, call_control_id } = event.payload;
  return `Call answered: ${from} → ${to} [${call_control_id}]`;
}

function handleCallHangup(event: CallHangupEvent): string {
  const { from, to, hangup_cause, hangup_source } = event.payload;
  return `Call ended: ${from} → ${to} (${hangup_source}: ${hangup_cause})`;
}

function handleMessageReceived(event: MessageReceivedEvent): string {
  const { from, to, text, type } = event.payload;
  const preview = text.length > 60 ? `${text.slice(0, 60)}…` : text;
  return `${type} from ${from.phone_number} to ${to.map((t: { phone_number: string }) => t.phone_number).join(', ')}: "${preview}"`;
}

/**
 * dispatch() — routes a TelnyxEvent to the correct typed handler.
 *
 * The `default` branch uses the `never` type to guarantee at compile time
 * that every member of the union is handled.  Adding a new event type to
 * TelnyxEvent without a matching case produces a compile error.
 */
function dispatch(event: TelnyxEvent): string {
  switch (event.event_type) {
    case 'call.initiated':   return handleCallInitiated(event);
    case 'call.answered':    return handleCallAnswered(event);
    case 'call.hangup':      return handleCallHangup(event);
    case 'message.received': return handleMessageReceived(event);
    default: {
      // TypeScript narrows event to `never` here — unreachable at runtime
      // as long as all union members are covered above.
      const _exhaustive: never = event;
      return `Unhandled event type: ${(_exhaustive as { event_type: string }).event_type}`;
    }
  }
}

// ---------------------------------------------------------------------------
// Knative func lifecycle hooks
// ---------------------------------------------------------------------------

export = {
  init() {
    webhookSecret = process.env.TELNYX_WEBHOOK_SECRET ?? '';
    if (webhookSecret) {
      console.log('Webhook signature verification: enabled');
    } else {
      console.log('Webhook signature verification: disabled (set WEBHOOK_SECRET to enable)');
    }
    console.log('Supported event types: call.initiated, call.answered, call.hangup, message.received');
  },

  /**
   * handle() — entry point for every HTTP request.
   *
   * @param context  Request context (method, headers, query, log)
   * @param body     Parsed request body (auto-decoded by runtime if JSON)
   */
  handle: async (context: Context, body?: unknown): Promise<FunctionResponse> => {
    const { method, log } = context;

    // POST / — process an incoming Telnyx webhook event
    if (method === 'POST') {
      const signature = (context.headers['x-telnyx-signature'] as string | undefined) ?? '';

      // Guard: empty body with signature verification enabled is always invalid
      if (webhookSecret && (!context.rawBody || context.rawBody.length === 0)) {
        return { statusCode: 400, body: { error: 'Empty body', message: 'Signature verification requires a non-empty request body' } };
      }

      // Verify against raw bytes before touching the parsed body
      if (webhookSecret && !verifySignature(context.rawBody!, signature)) {
        return { statusCode: 401, body: { error: 'Invalid signature', message: 'Webhook signature verification failed' } };
      }

      if (!body || typeof body !== 'object') {
        return { statusCode: 400, body: { error: 'Invalid body', message: 'Expected a JSON webhook payload' } };
      }

      const webhook = body as { data?: { event_type?: string } };
      if (!webhook.data?.event_type) {
        return { statusCode: 400, body: { error: 'Missing event_type', message: 'Payload must include data.event_type' } };
      }

      const eventType = webhook.data.event_type;
      const supportedTypes = ['call.initiated', 'call.answered', 'call.hangup', 'message.received'];

      if (!supportedTypes.includes(eventType)) {
        return {
          statusCode: 422,
          body: {
            error: 'Unsupported event type',
            event_type: eventType,
            supported: supportedTypes,
          },
        };
      }

      // Unwrap the envelope — dispatch works on event.event_type directly
      // so TypeScript can narrow the discriminated union in the switch.
      const event = (body as TelnyxWebhook).data;
      let summary: string;
      try {
        summary = dispatch(event);
      } catch (err) {
        log.error('Dispatch failed — malformed payload', { event_type: eventType, error: String(err) });
        return { statusCode: 422, body: { error: 'Malformed payload', message: 'Event payload is missing required fields' } };
      }
      record(event, summary);

      log.info('Event processed', { event_type: eventType, id: event.id });

      return {
        statusCode: 200,
        body: {
          message:    'Event processed',
          event_id:   event.id,
          event_type: eventType,
          summary,
        },
      };
    }

    // GET / — recent event log + per-type counts
    if (method === 'GET') {
      const byType: Record<string, number> = {};
      for (const e of processed) {
        byType[e.event_type] = (byType[e.event_type] ?? 0) + 1;
      }

      return {
        statusCode: 200,
        body: {
          service:         'call-event-router',
          version:         '1.0.0',
          total_processed: processed.length,
          by_type:         byType,
          recent:          processed.slice(-10),
        },
      };
    }

    return { statusCode: 405, body: { error: 'Method not allowed' } };
  },

  shutdown() {
    console.log(`Call event router shutting down — processed ${processed.length} events`);
  },
};
