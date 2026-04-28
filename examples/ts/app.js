'use strict';

/**
 * Local development wrapper for TypeScript edge functions.
 *
 * Identical to the JavaScript wrapper — loads the compiled function via
 * require('.') which resolves to the "main" field in package.json.
 * For TypeScript examples, "main" points to "dist/index.js" (the compiled
 * output), so this wrapper works without modification after `npm run build`.
 *
 * See ../js/app.js for full documentation.
 */

const http = require('http');
const { URL } = require('url');

const fn = require('.');

function buildLogger(req) {
  const ts = () => new Date().toISOString();
  const prefix = () => `[${ts()}] [${req.method} ${req.url}]`;
  return {
    info:  (msg, data) => console.log(`${prefix()} INFO  ${msg}`, data != null ? JSON.stringify(data) : ''),
    warn:  (msg, data) => console.warn(`${prefix()} WARN  ${msg}`, data != null ? JSON.stringify(data) : ''),
    error: (msg, data) => console.error(`${prefix()} ERROR ${msg}`, data != null ? JSON.stringify(data) : ''),
  };
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const raw = await readBody(req);

  let body;
  const ct = req.headers['content-type'] || '';
  if (raw.length > 0) {
    if (ct.includes('application/json')) {
      try { body = JSON.parse(raw.toString('utf-8')); } catch { body = raw.toString('utf-8'); }
    } else {
      body = raw.toString('utf-8');
    }
  }

  const parsedURL = new URL(req.url, 'http://localhost');
  const context = {
    method:  req.method,
    headers: req.headers,
    query:   Object.fromEntries(parsedURL.searchParams),
    log:     buildLogger(req),
    rawBody: raw, // raw Buffer — use for HMAC signature verification, not re-serialised body
  };

  try {
    const result = await fn.handle(context, body);

    const statusCode   = result?.statusCode  ?? 200;
    const extraHeaders = result?.headers     ?? {};
    const responseBody = result?.body        ?? result;

    let payload;
    if (Buffer.isBuffer(responseBody)) {
      payload = responseBody;
    } else if (typeof responseBody === 'string') {
      payload = responseBody;
    } else {
      payload = JSON.stringify(responseBody, null, 2);
    }

    res.writeHead(statusCode, { 'Content-Type': 'application/json', ...extraHeaders });
    res.end(payload);
  } catch (err) {
    console.error('Handler error:', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Internal server error', message: err.message }));
  }
});

if (typeof fn.init === 'function') {
  try { fn.init(); } catch (err) { console.error('init() failed:', err); process.exit(1); }
}

const port = parseInt(process.env.PORT || '8080', 10);
server.listen(port, () => console.log(`Function running on port ${port}`));

function shutdown() {
  if (typeof fn.shutdown === 'function') {
    try { fn.shutdown(); } catch (err) { console.error('shutdown() error:', err); }
  }
  process.exit(0);
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
