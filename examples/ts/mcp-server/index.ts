/**
 * Telnyx MCP Server — TypeScript Edge Function
 *
 * A Model Context Protocol (MCP) server that exposes Telnyx API tools to AI
 * agents via streamable HTTP transport.  Agents can execute TypeScript code
 * against the Telnyx SDK and search the SDK documentation.
 *
 * The heavy lifting is done by the `telnyx-mcp` library — this file wires it
 * into an Express HTTP server with Knative health probes.
 */

import express from 'express';
import { configureLogger, getLogger } from 'telnyx-mcp/logger';
import { streamableHTTPApp } from 'telnyx-mcp/http';
import type { McpOptions } from 'telnyx-mcp/options';

configureLogger({ level: 'info', pretty: false });

const mcpOptions: McpOptions = {
  codeExecutionMode: 'local',
};

const mcpApp = streamableHTTPApp({
  mcpOptions,
  clientOptions: {
    apiKey: process.env.TELNYX_API_KEY,
  },
});

const app = express();

// Knative health probes (no auth required)
app.get('/health', (_req, res) => { res.status(200).send('OK'); });
app.get('/health/liveness', (_req, res) => { res.status(200).send('OK'); });
app.get('/health/readiness', (_req, res) => { res.status(200).send('OK'); });

// Bearer-token auth — SHARED_SECRET is required unless running locally
const sharedSecret = process.env.SHARED_SECRET;
if (!sharedSecret) {
  getLogger().warn('SHARED_SECRET is not set — MCP endpoint is unauthenticated. This exposes your TELNYX_API_KEY to anyone who can reach this server. Set SHARED_SECRET before deploying.');
  app.use((req, res, next) => {
    if (req.method === 'POST') {
      res.status(503).json({
        error: 'SHARED_SECRET not configured',
        message: 'This MCP server requires SHARED_SECRET to be set. Run: telnyx-edge secrets add SHARED_SECRET "$(openssl rand -hex 32)"',
      });
      return;
    }
    next();
  });
} else {
  app.use((req, res, next) => {
    const auth = req.headers.authorization || '';
    if (auth !== `Bearer ${sharedSecret}`) {
      res.status(401).json({ error: 'Unauthorized' });
      return;
    }
    next();
  });
  getLogger().info('Bearer-token auth enabled (SHARED_SECRET is set)');
}

// Mount MCP handler (after auth middleware)
app.use(mcpApp);

const port = parseInt(process.env.PORT || '8080', 10);

app.listen(port, () => {
  getLogger().info(`Telnyx MCP Server listening on port ${port}`);
});
