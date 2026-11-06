# MOTIF Forest MCP — Railway deployment handoff

**Status:** Deployment-ready container configuration; no Railway service has been created, no endpoint deployed, and no ChatGPT custom plugin registered. Requires the owner's Railway connection and secret configuration.

## Deployment choice

Use Railway as the single-instance, persistent **MCP front door** (FastAPI/SQLite) and keep the RING-002/RING-004 native Docker experiments disabled in that front-door container. For native, source-owned experiments, a separate isolated worker using Modal Sandboxes or Railway Sandboxes is a later integration, never a Docker socket inside the public API container.

## Source

- GitHub repository: `the-static-collective/MOTIF`
- Source branch for review: `integration/motif-living-forest-mcp-v03` (draft PR #160)
- Railway root directory: `integrations/motif-living-reasoner`
- Dockerfile: `Dockerfile` (in that root directory). Identical local reference: `Dockerfile.railway` in the downloadable package.
- Source artifact: `release-v0.3.zip` pinned to SHA-256 `7f442cefc995115b5383faf87e0f922a594d7f0a480039c2e5aecc85c122c993`; build rejects mismatched bytes.

## Railway setup

1. In Railway, create a project → Deploy from GitHub; choose `the-static-collective/MOTIF` and the review branch. Set **Root Directory** to `integrations/motif-living-reasoner`. Confirm Dockerfile auto-detection (no Railpack override).
2. Add a **persistent volume mounted at `/data`**; keep replicas = 1. The entrypoint fixes root-owned volume permissions and drops to unprivileged UID 10001 before starting the app. Back up `sessions.sqlite3` and SQLite WAL files consistently; don't lose the volume on redeploy.
3. Configure environment variables in Railway's private Variables interface (not in code):
   - `MOTIF_MCP_API_KEY`: random secret at least 32 chars, ideally 48+ random bytes in URL-safe form. Never paste into chat, GitHub, screenshots, or logs.
   - `MOTIF_MCP_DB=/data/sessions.sqlite3` (also Dockerfile default).
   - `MOTIF_ALLOWED_ORIGINS`: blank unless the verified client sends an Origin. If used, specify exact trusted HTTPS origins only.
   - `MOTIF_GITHUB_READ_TOKEN`: optional, scoped *read-only* GitHub token for source catalog API; **do not** use a write token.
   - `PORT`: Railway provides this automatically, the entrypoint reads it dynamically.
4. Expose a Railway HTTPS domain under Service → Settings → Networking → Generate Domain. Set the deployment healthcheck to `/healthz`. Do not route untrusted traffic to `/data` or attach a Docker socket.
5. Verify `GET https://YOUR-RAILWAY-DOMAIN/healthz` returns JSON `"status":"running"` and **no session data**. The MCP endpoint is `/mcp` and rejects requests missing the private bearer key (`401`).
6. With a securely stored token on your own machine, test an authenticated MCP `initialize`, `tools/list` and `forest_goals` call using JSON-RPC Streamable HTTP. Confirm return sessions persist across a deployment restart.

### Local HTTP protocol smoke test

Set a secret in your *local shell* (not an issue/comment), then run:

```sh
curl -fsS "https://YOUR-RAILWAY-DOMAIN/healthz"
curl -i "https://YOUR-RAILWAY-DOMAIN/mcp" \
  -H "Authorization: Bearer $MOTIF_MCP_API_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"motif-smoke","version":"0.1"}}}'
```

## IMPORTANT: ChatGPT authentication compatibility

The current MOTIF v0.3 server accepts a **fixed bearer token**, not an OAuth 2.1 authorization flow. OpenAI's latest *Add custom MCP server* UI documents **OAuth, no auth, or mixed OAuth/no-auth** (not arbitrary bearer/API-key entry). Its `mcp.json` API-key declaration is valid in the plugin schema but does **not** guarantee connection through the ChatGPT UI. **Do not select "No authentication" for this private service, and do not disable authentication to make it connect.**

To connect this protected instance from ChatGPT, implement a proper OAuth 2.1 protected resource/server integration backed by a trusted identity provider, or use a compatible secure MCP tunnel after validating its credential handling. Verify actual end-to-end initialization and tool calls before claiming a ChatGPT connection. This is a separate, explicit engineering gate after Railway hosts the endpoint.

## Why not deploy all native cartridges on Railway?

The authenticated API container does not include Docker, the daemon, or all historical MOTIF git objects. It still supports six built-in common-case operators, live **read-only** forest discovery, exact SHA source inspection, RING-003 declared hypergraph selection, and durable review/feedback sessions. Calling `forest_execute_reviewed` for RING-002/RING-004 will HOLD until a genuinely isolated worker is deployed and wired in; this is intentional, not a missing promise.

For native execution, provision a short-lived **Modal Sandbox** or **Railway Sandbox**, fetch *only* the pinned original source commits, supply only typed public evidence, execute with no credentials/network and hard resource limits, verify the resulting hashes and schemas, and return bounded receipts. This future worker must be a separate private service. It is not implemented in this Railway deployment.

## No automatic financial commitment

Railway has a free tier and a paid Hobby tier; usage limits and prices can change. The deployer should review the current Railway billing estimate before enabling persistent services. A deployed web API may incur compute and volume charges even when idle.