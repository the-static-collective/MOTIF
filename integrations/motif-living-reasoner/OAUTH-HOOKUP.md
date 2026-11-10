# MCP-HOOKUP-001 — OAuth 2.1 protected MCP front door

**Source:** draft child of [MOTIF forest MCP v0.3 PR #160](https://github.com/the-static-collective/MOTIF/pull/160). The v0.3 server stays byte-for-byte pinned to the existing SHA-256 ZIP. This patch adds a **real, testable OAuth resource server boundary** around the in-process existing server. It is **NOT an OAuth authorization server** and does not create a Railway deployment, an identity provider, a ChatGPT connection, or a functioning login on its own.

## What the gateway does

1. Publishes `/.well-known/oauth-protected-resource` for ChatGPT authorization discovery.
2. Refuses calls to `/mcp` without a signed, short-lived JWT **access token** from a configured HTTPS issuer with configured JWKS signature, exact issuer, exact resource audience, valid expiry/issued-at, `motif:read` scope and the one allowlisted immutable user `sub`.
3. Sends the original v0.3 fixed bearer secret only **inside the same process**, via an ASGI in-memory call. Incoming client Authorization is replaced after verification. The original non-OAuth `mcp_server.server:app` is not directly served on any port.
4. Exposes only 11 source-reviewed read tools. `tools/list` filters the original 18-tool response and adds per-tool `securitySchemes: [{type:'oauth2',scopes:['motif:read']}]`; direct execution or feedback calls are refused at the boundary even when the caller names an existing backend tool.
5. Publishes an unauthenticated no-secrets `/healthz` route. Does not expose other original paths such as docs, OpenAPI, database, or debug.
6. Leaves Docker/native worker access closed, one instance, one SQLite owner, and exact-source forest admission untouched.

This is deliberately **read-only** for the first ChatGPT hookup. Future review and execution tools require a *separate verifiable human confirmation* protocol rather than treating model-emitted `approved:true` or generic OAuth consent as genuine case-specific consent.

## Before you deploy (human-owned configuration)

**An actual compatible OAuth 2.1 / OIDC identity provider is mandatory.** Prefer a maintained provider such as Auth0 or Stytch, not a self-written password/authorization-code server. Verify that provider metadata advertises S256 PKCE, authorization code flow, compatible CIMD/DCR or predefined client, issuer identification if stable redirects are used, and RFC 8707 `resource` audience binding. It must issue *signed JWT access tokens*, not opaque-only access tokens or ID tokens, with the proper `aud`, `iss`, `sub`, `iat`, `exp`, and the granted `scope` string.

For example, Auth0 deployments may need **Resource Parameter Compatibility Profile** enabled so MCP's `resource` parameter sets the intended JWT audience. Test this against Auth0 before considering a live installation successful.

Configure your provider's API/resource identifier as the **exact HTTPS origin** of the MOTIF MCP deployment, such as `https://motif.example.com` (NOT `/mcp`). Give it the permission `motif:read`; authorize your specific immutable user subject. Use the exact issuer identifier from discovery, including any trailing slash. Register the **exact callback shown by ChatGPT's plugin management**, choosing an appropriate CIMD, DCR, or predefined client mode. Do not invent a client secret or redirect URI.

### Railway environment (private Variables panel)

| Variable | Value | Notes |
| --- | --- | --- |
| `MOTIF_OAUTH_RESOURCE` | `https://<your-host>` | Public HTTPS origin; no `/mcp`. Must equal JWT `aud`. |
| `MOTIF_OAUTH_ISSUER` | `https://<your-idp-issuer>/` | Exact IDP issuer including trailing slash when present. |
| `MOTIF_OAUTH_JWKS_URL` | `https://<your-idp>/.../jwks.json` | Trusted signing keys URI from provider metadata, not from user JWT headers. |
| `MOTIF_OAUTH_ALLOWED_SUB` | provider immutable subject | Only this one user may connect. Never use changing email addresses. |
| `MOTIF_MCP_API_KEY` | random secret, 48+ bytes URL-safe | *Internal only* legacy v0.3 transport secret, not the OAuth access token. |
| `MOTIF_MCP_DB` | `/data/sessions.sqlite3` | Persistent one-instance SQLite. |
| `PORT` | Railway assigned | Automatic. |

The Dockerfile deploys from **this branch**, root `integrations/motif-living-reasoner`, with one instance and `/data` volume. The start script **fails closed** if JWT provider configuration is missing or malformed. It never falls back to public fixed-bearer authorization. The original server's token is not accepted directly from any remote client.

## Connection sequence

1. Configure the identity provider and host, then verify `GET https://<host>/healthz` returns `gateway:oauth` and `GET https://<host>/.well-known/oauth-protected-resource` returns exactly the configured issuer/resource.
2. Verify an unauthenticated `POST https://<host>/mcp` gets **401** with `WWW-Authenticate` containing `resource_metadata`.
3. In ChatGPT web, add custom MCP server `https://<host>/mcp` using **OAuth**; choose the registration path your IDP actually supports. Authenticate as the one allowed subject. Rejecting with 401 for another subject is expected.
4. Confirm `initialize`, `tools/list`, and one read-only `forest_goals` call. Tool discovery should show **11 tools**, never feedback/execute names. Refresh the plugin after tool schema changes.
5. Check server logs for auth failures WITHOUT logging authorization headers, tokens, proof packets or private session content. Verify session persistence and recovery across one restart.

## Reproduction and falsification

```sh
python -m pip install 'PyJWT[crypto]==2.13.0' 'httpx==0.28.1'
python -m unittest -v test_oauth_gateway.py

# Run on the pinned release root (as in the read-only CI workflow):
python smoke_pinned_server.py
```

Tests reject missing/wrong token, wrong signer, audience, issuer, user, scope, expired token, mutations, JSON-RPC batches, oversized requests, and direct access to internal routes. A pinned package integration smoke tests the real original 18-tool server through the gateway using a **test-only stub OAuth verifier**; it does not prove a real IdP login or ChatGPT UI connection.

## Important limits and risk register

- **Provider-dependent**: ChatGPT OAuth flow, CIMD, DCR and actual mobile ChatGPT invocation have not been field-tested. The gateway verifies JWTs but does not implement token issuance, logout, refresh, revocation lists, or OAuth authorization-code endpoint. For rapid revocation, use short-lived access tokens, provider rotation and disable the owner subject / restart the service when required.
- **Single-owner only**: A fixed SQLite database and internal key are not multi-tenant isolation. Do not extend this to an arbitrary app installation or peer TranchNode identity without per-subject authorization and storage separation.
- **HTTPS terminates at Railway**: Configure the public domain and proxy settings; no requests to the original app are routable directly. Do not expose an alternate port to `mcp_server.server:app`.
- **Pinned release**: The authenticated wrapper changes transport security, not the reviewed 18-tool v0.3 reasoner logic, native benchmark availability, or the proof-carrying work in later draft PRs.
- **JWKS is not online revocation**: Token signature and expiry checks are necessary but not sufficient to implement immediate revocation or reliable provider session logout. Rate limiting, monitoring and upstream WAF must be handled by hosting infrastructure.
- **No automatic action**: `forest_execute_reviewed` and `execute_reviewed` remain blocked by default regardless of OAuth grants. That is intentional.

## Upstream documentation

- [OpenAI authenticated plugin MCP servers](https://developers.openai.com/plugins/build/auth)
- [Add custom MCP server](https://developers.openai.com/api/docs/guides/custom-mcp-server)
- [MCP server development](https://developers.openai.com/plugins/build/mcp-server)
- [Auth0 MCP resource parameter compatibility](https://support.auth0.com/center/s/article/mcp-audience-error-with-auth0)
