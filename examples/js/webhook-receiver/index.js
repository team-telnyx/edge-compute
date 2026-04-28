'use strict';

const crypto = require('crypto');

// Loaded once at init time
let webhookSecret;

// In-memory log of recent webhooks (ring buffer, max MAX_WEBHOOKS entries)
const received = [];
const MAX_WEBHOOKS = parseInt(process.env.MAX_WEBHOOKS || '500', 10);

/**
 * Verify an HMAC-SHA256 webhook signature.
 * Expected header format: "sha256=<hex-digest>"
 */
function verifySignature(rawBody, signature) {
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

module.exports = {
  /**
   * init() is called once before the function starts accepting requests.
   * Load secrets and any one-time setup here.
   */
  init() {
    webhookSecret = process.env.WEBHOOK_SECRET || '';
    if (webhookSecret) {
      console.log('Webhook signature verification: enabled');
    } else {
      console.log('Webhook signature verification: disabled (set WEBHOOK_SECRET to enable)');
    }
  },

  /**
   * handle() is called for every incoming HTTP request.
   *
   * @param {object} context - Request context provided by the runtime
   *   context.method   - HTTP method (GET, POST, ...)
   *   context.headers  - Request headers
   *   context.query    - Parsed query string parameters
   *   context.log      - Structured logger (pino-compatible)
   * @param {unknown} body - Parsed request body (auto-decoded by runtime if JSON)
   * @returns {{ statusCode: number, body: object }} HTTP response
   */
  handle: async (context, body) => {
    const { method, headers, log, rawBody } = context;

    // POST / — receive and verify a webhook
    if (method === 'POST') {
      const signature = headers['x-webhook-signature'] || '';
      const source    = headers['x-webhook-source']    || 'unknown';

      // Guard: empty body with signature verification enabled is always invalid
      if (webhookSecret && (!rawBody || rawBody.length === 0)) {
        return {
          statusCode: 400,
          body: { error: 'Empty body', message: 'Signature verification requires a non-empty request body' },
        };
      }

      // Verify against the original raw bytes — re-serialising a parsed JSON body
      // loses whitespace/formatting and would reject valid signatures.
      if (webhookSecret && !verifySignature(rawBody, signature)) {
        return {
          statusCode: 401,
          body: { error: 'Invalid signature', message: 'Webhook signature verification failed' },
        };
      }

      const entry = {
        id:                `whk_${Date.now()}`,
        timestamp:         new Date().toISOString(),
        source,
        signature_verified: !!webhookSecret,
        data:               body,
      };

      received.push(entry);
      if (received.length > MAX_WEBHOOKS) received.shift();

      log.info({ webhook_id: entry.id, source }, 'Webhook received');

      return {
        statusCode: 200,
        body: {
          message:    'Webhook received successfully',
          webhook_id: entry.id,
          timestamp:  entry.timestamp,
        },
      };
    }

    // GET / — list recent webhooks + service info
    if (method === 'GET') {
      return {
        statusCode: 200,
        body: {
          service:  'webhook-receiver',
          version:  '1.0.0',
          signature_verification: webhookSecret ? 'enabled' : 'disabled',
          recent_webhooks:  received.slice(-10),
          total_received:   received.length,
        },
      };
    }

    return { statusCode: 405, body: { error: 'Method not allowed' } };
  },

  /**
   * shutdown() is called when the function is stopping.
   */
  shutdown() {
    console.log(`Webhook receiver shutting down — processed ${received.length} webhooks`);
  },
};
