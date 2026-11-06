# MOTIF Living Reasoner v0.3 — living forest + MCP server

**Status: implemented and locally tested; NOT deployed, registered or connected to ChatGPT.**

A personal single-owner MCP service wrapping the earlier executable MOTIF v0.1 skill. This is a bounded same-case reasoning tool, not an LLM, network agent, autonomous patcher, or a live executor of every MOTIF branch. No external actions or GitHub writes are performed by the server.

## What runs

- **18 MCP tools:** nine original common-case operators and nine forest tools; see `FOREST.md` for full capabilities and source pins.
- **6 executable common-case operators:** `source.audit`, `claim.challenge`, `question.forge`, `work.plan`, `affordance.frontier`, `integrate.review`.
- **Dependency-aware composition:** exact finite selection under a budget, computed waves with shared typed input and outputs (not unrelated demos).
- **Durable return:** SQLite stored sessions, revision checks against racing/stale writes, hash-chain integrity checks, and explicit `PLAN_REVIEW` / `RESULT_REVIEW` checkpoints.
- **Reflection:** the result checkpoint recommends one next human question; it never initiates another cycle automatically.
- **Security:** personal bearer token, Origin rejection, request-size bounds, local-only default host, deliberate read/write tool annotations, no credentials in result/manifest, and no arbitrary source-code execution.

### Prerequisites

Python 3.11+ and `fastapi` / `uvicorn` from `requirements.txt` (or Docker). The original skill engine is standard-library Python. The server implements a **minimal, no-SSE Streamable HTTP JSON-RPC subset directly with FastAPI** rather than using the official MCP SDK; `GET /mcp` returns HTTP 405 as permitted. Test it against MCP Inspector and the actual ChatGPT client before production use. Its manual implementation is not a claim of conformance to every optional MCP feature.

### Start locally

```bash
cd motif-living-reasoner
python -m pip install -r requirements.txt
# Set this to a persistent, unique random secret in your terminal or deployment secret manager.
export MOTIF_MCP_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python -m mcp_server.server
```

The service listens on `127.0.0.1:8000`. Its endpoint is `http://127.0.0.1:8000/mcp`; public ChatGPT cannot reach this local URL without a secure tunnel. For a personal remote connection, deploy behind a valid **HTTPS** endpoint, keep the same secret in the host's private environment, attach a persistent disk/volume for SQLite, and update `mcp.json` with the actual endpoint URL. Never put the secret in the manifest, source files, GitHub, logs or chat.

### Quick local wire check

Use MCP Inspector (`npx @modelcontextprotocol/inspector`) with Streamable HTTP, `http://127.0.0.1:8000/mcp`, and a bearer Authorization header. Verify `initialize`, `tools/list`, `start_session`, `record_feedback`, `execute_reviewed`, `resume_session`, and `reflect_session`. This requires Node/npm and Internet access for initial Inspector installation.

Or use Python's built-in unittest runner:

```bash
python -m unittest discover -s skills/motif-reasoner/tests -p 'test_*.py' -v
python -m unittest discover -s mcp_server/tests -p 'test_*.py' -v
```

### Container deployment

```bash
docker build -t motif-living-reasoner:0.2 .
docker volume create motif-sessions
docker run --rm -p 127.0.0.1:8000:8000 \
  -e MOTIF_MCP_API_KEY="$MOTIF_MCP_API_KEY" \
  -v motif-sessions:/data motif-living-reasoner:0.2
```

For remote deployment, provide HTTPS using a reverse proxy or managed container host. `MOTIF_ALLOWED_ORIGINS` may be set to a comma-separated list of explicitly trusted HTTPS origins if the actual client sends an `Origin` header; unrecognized browser origins are always rejected. Configure proxy-level limits and production logging. This starter has **single-owner, single-token access**; it is not multi-user OAuth, role-based isolation, or a production credential service.

### Connecting to ChatGPT

1. Deploy at a reachable `https://…/mcp` URL; verify real MCP initialization and authentication first.
2. In ChatGPT **web** Plugins, use **Add custom MCP server**, add that URL and your supported connection authentication, and review the permission warning. For personal plugins, you can use the normal Create as a plugin flow. Exact authentication choices vary by installation flow.
3. Replace the placeholder URL in `mcp.json` before packaging a plugin. The `api_key` + `headerScheme: bearer` metadata contains **no key**. Current OpenAI plugin submission documentation warns that its public submission portal's connection form does not accept API-key declarations; use a compatible personal setup flow or upgrade to OAuth 2.1 for broader deployment.
4. Start a test chat: ask MOTIF to inspect an actual typed case; review its route; approve it explicitly; execute; evaluate and return. Use `list_sessions` and `resume_session` in later chats.

**This zip is not a live endpoint.** There is no registered `plugin_asdk_app...` ID or connected account yet. Remote hosting and plugin installation remain separate user-controlled actions.

## Why the review stops matter

The built-in engine will not execute a session's selected methods until `PLAN_REVIEW` is approved. The model cannot independently attest human consent, so the skill explicitly forbids fabricating approval: a client can technically call an approval tool, but the service has no independent human identity proof. Its effects are confined to its local case and SQLite session, with no external writes. After execution it always stops at `RESULT_REVIEW`, which exposes contradictory evidence and one best next question. `accept` and `revise` are explicit feedback events; `reopen_session` starts a new review cycle.

Session hashes detect accidental or naive content alteration, **not** malicious tampering by someone who controls the database. Back up the database separately if durable research receipts matter.

## Native MOTIF integration boundary (updated in v0.3)

MOTIF's repository has RING-002 source-native triad adapters and RING-003 typed hypergraph selection on experimental branches. This package **does not silently import or execute that code**. The next phase is to make pinned, source-owned adapters exchange artifacts from one actual shared question, then benchmark each method alone versus dynamic composition and classical controls. Newly discovered branches should enter as indexed, non-executable candidates until review, isolation and meaningful interoperability tests.

## Files

- `skills/motif-reasoner/SKILL.md` — agent conversation/reinspection workflow.
- `skills/motif-reasoner/scripts/motif.py` — v0.1 local computational engine.
- `mcp_server/service.py` — durable session and review transition service.
- `mcp_server/server.py` — authenticated HTTP MCP JSON-RPC transport; `python -m mcp_server` also supports local stdio JSON-RPC.
- `mcp.json` — **placeholder URL**, editable portable MCP manifest.
- `Dockerfile` — unprivileged container with persistent SQLite mount.
- `examples/first-spiral.json` — synthetic demonstration case, not independently verified source evidence.

## v0.3 — Source-indexed, selectively executable forest

See [FOREST.md](FOREST.md) for the exact RING-002/003/004 source pins, nine additional MCP tools, discovery, reviewed native sandbox execution, measured synthetic shared-case comparison, and deployment constraints. All branches can be indexed read-only; only three original native adapters are executable, and only if a trusted Docker worker and full git checkout are available. The front-door Dockerfile **deliberately does not mount a host Docker socket**.

The original RING-004 independently authored source-owned code reports full three-native 32/32 and strong classical control 32/32 on each of two *author-created synthetic* task seeds. No incremental accuracy advantage over the strong baseline has been demonstrated. The new wrappers were tested locally with fake native outputs; no additional native experiment was claimed.

This package is **not yet publicly hosted**, and no ChatGPT personal plugin was installed by this build.