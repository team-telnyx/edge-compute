# AGENTS.md

This repository participates in Telnyx's "Win the Bot" agent-readiness initiative. AI coding agents working in this repo should read this file first.

## Purpose

`edge-compute` hosts the Telnyx Edge CLI (`telnyx-edge`) and a set of example workloads in `examples/` (TypeScript, JavaScript, Python, Go). The most agent-relevant example is `examples/ts/mcp-server/`, a Model Context Protocol server that exposes Telnyx API tools to AI agents over streamable HTTP. That example is the fast-follow deployment target for Ora MCP-compliance work tracked in the cross-repo execution plan (Phase 5/6).

## Safe Commands

The repo has no top-level package.json, no top-level lockfile, and no GitHub Actions workflows. All build/test commands live inside individual examples.

For the MCP server example:

```bash
cd examples/ts/mcp-server
npm install
npm run build
TELNYX_API_KEY=test SHARED_SECRET=dev-secret npm start
# Local server listens on :8080. Override with PORT.
curl -s http://localhost:8080/health/readiness
```

For other examples, use the `package.json` / `Makefile` / language-native commands inside each example directory. Do not assume a workspace-level install works.

## Testing Strategy

There is no repo-wide test runner. When adding or changing an example:

- Run the example's own `npm run build` (or language equivalent) before opening a PR.
- For `examples/ts/mcp-server/`, exercise the MCP flows documented in its README (initialize, tools/list, a valid tool call, an invalid tool call) against the local server.
- Health probes (`/health`, `/health/liveness`, `/health/readiness`) must remain unauthenticated so Knative probes keep working after deploy.

## PR Expectations

- Branch from `main`; keep PRs small and focused on one example or one CLI concern.
- No CODEOWNERS file is present. Recent reviewers on MCP-example and docs PRs include @yiumingtelnyx and @vika-zakharova; request review from them when the change touches `examples/ts/mcp-server/` or example docs.
- Runtime deployment is **not** wired through GitHub Actions. Edge functions are deployed manually via the CLI:
  ```bash
  telnyx-edge new-func --from-dir=examples/ts/mcp-server --name=<your-name>
  telnyx-edge secrets add TELNYX_API_KEY <key>
  telnyx-edge secrets add SHARED_SECRET "$(openssl rand -hex 32)"
  telnyx-edge ship
  ```
  Do not assume CI will deploy a merged PR.

## API & Security Boundaries

- `SHARED_SECRET` is required for deployed POSTs to the MCP example server. Without it the server rejects all MCP requests with 503.
- Health probe endpoints are intentionally unauthenticated.
- Never commit `.env` files, `TELNYX_API_KEY` values, shared secrets, or any other credential. Use `telnyx-edge secrets add` for runtime secrets.
- Do not change the MCP example auth model (e.g. swap `SHARED_SECRET` for OAuth) without owner approval.

## Agent-Readiness Tracking

- Cross-repo plan: https://github.com/team-telnyx/win-the-bot/blob/main/cases/ora-agent-readiness/cross-repo-execution-plan.md (Phase 5 §14 and Phase 6 cover this repo's MCP example)
- Score impact map: https://github.com/team-telnyx/win-the-bot/blob/main/cases/ora-agent-readiness/score-impact-map.md
- Live Ora score: https://ora.run/score/telnyx.com

## Out of Scope Without Human Review

- Do not change the MCP example auth model (`SHARED_SECRET` vs OAuth/PKCE) without owner approval.
- Do not publish a live `serverUrl` in any `/.well-known/mcp/server-card.json` (lives in `dotcom-monorepo`) without confirming the Edge function URL is stable and the auth decision is signed off.
- Do not remove or authenticate the Knative health probe endpoints.
- Do not commit secrets, API keys, or `.env` files.
