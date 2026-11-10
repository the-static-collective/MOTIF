# MOTIF Phone ↔ ChatGPT — APP-BRIDGE-001

**Status 2026-11-09:** design plus six locally passing offline Python bridge tests. Not a mobile app, OAuth provider, deployed MCP server, installed plugin, or live ChatGPT integration. This branch is based on draft PR #160 and does not unpack or modify its v0.3 release ZIP.

## Two complementary ways to use the same reasoner

**Inside ChatGPT (plugin host):** Make the v0.3 HTTP MCP front door reachable over HTTPS and authenticate it with a proper OAuth 2.1 authorization server (MCP protected-resource metadata, OAuth discovery, PKCE S256, CIMD or DCR, scope and audience checks). Add the endpoint through ChatGPT's custom MCP server connection; a standard MCP Apps UI can render evidence graphs, route alternatives, receipts and approval screens *inside ChatGPT*. The current fixed bearer secret is **not** OAuth and must not be disabled merely to get connected. Use this route first for a phone-accessible MOTIF **within the existing ChatGPT interface**.

**Inside a standalone MOTIF Android app (app host):** There is now a documented **Sign in with ChatGPT** option for eligible locally running open-source projects, with distinct identity and ChatGPT-plan-usage permissions. Use the official SIWC DevKit and a device credential store, and keep the app's own chat history. Signing in does **not** import ChatGPT conversations, memory, files, or plugin installations. The published SIWC plan-sharing preview **does not support hosted MCP/connectors**, but supports client-executed function tools. The adapter in this directory converts the already-reviewed MOTIF MCP read-tool descriptors to Responses function-tools; a trusted app-side transport handles the call. Reviewable writes pass through a separate UI path with exact-argument, one-use, expiring tickets. The code is transport-injected; it does **not** implement SIWC, Android sign-in, HTTP MCP or user identity. The official current working example is Electron desktop; test Android redirect/callback and secure storage before claiming mobile availability.

**Developer-funded API fallback:** A standalone app can also invoke Responses with `server_url` for remote MCP and OAuth authorization using an appropriate OpenAI API account. That is a separate billing and authentication path from ChatGPT-plan sharing. API keys and the MOTIF service-wide bearer secret must never ship in an APK.

```text
ChatGPT web/mobile -- MCP OAuth 2.1 --> MOTIF HTTPS MCP -- reviewed reasoner
                                  |                           |
                          MCP Apps evidence UI       sandboxed native worker (later)

MOTIF Android app -- SIWC identity / plan permission --> eligible Responses model
       |                                                    |
       +-- local model function calls via app bridge <------+
       |                  |
       +-- private app state and later TranchNode kernel
                          |
                   trusted per-user MOTIF transport
```

## Source boundaries and controls

- New branches in the MOTIF forest are indexed as **source-only**. This adapter's explicit read allowlist cannot be expanded by a tool description, model output or a newly indexed branch.
- Mutating or execution-oriented tools are **not exposed to the model function list**. A user-reviewed UI action must match the exact canonical tool + JSON arguments, within a short expiry and once only. This is an accidental-invocation guard, **not** proof of the user’s physical identity or a replacement for server-side authentication/authorization. UI code must never let the model call `approve_from_ui`.
- All access tokens, consent records and account identity mapping remain in trusted host components. Neither model context nor a rendered graph receives raw credentials. No service-wide token in the client.
- A graph fact or external evidence node is **not** automatically shared with another phone. Export only independently approved, revocable, fact-specific, recipient-specific evidence.
- PR #233 (COLLECTIVE-001 proof-carrying answer) is the proposed owner for evidence ancestry, proof scope and verified re-entry. PR #237 (COLLECTIVE-002 three nodes) is research-only loopback/HMAC evidence exchange, **not** a secure mobile networking layer. Do not claim either is integrated or merged.
- Native experiments remain isolated from the public front door; never attach a Docker socket or run arbitrary branch code from model requests.

## What exists in this PR

`bridge.py` exports `MotifFunctionBridge.model_functions`, `call_from_model`, `stage_review`, `approve_from_ui` and `call_from_ui`. It has no dependencies outside Python 3.10+ standard library, makes no network calls and requires the application to inject its own trusted callable transport. `test_bridge.py` has six executable tests for read allowlisting, no model writes, exact one-use review, expiry, invalid payload limits and malformed schemas.

Run: `cd integrations/motif-app-bridge && python -m unittest -v test_bridge.py`

## Acceptance gates

1. Re-test the actual source archive in #160, MCP Inspector initialization, `tools/list` and actual review stops; branch publication alone is not a production test.
2. Build OAuth2.1 protected resource + issuer via a maintained provider, validate token issuer/audience/scopes/expiry, then actually install a **personal MOTIF ChatGPT plugin** and confirm operation on mobile and desktop. Do not expose the existing static bearer.
3. Make a minimal Android chat + graph + receipt + human confirmation UI. Test the local tool bridge and one-time approvals before connecting AI.
4. Validate SIWC use and platform callback support on the target Android device. In this preview, use **local function tools**, never hosted MCP on the token-sharing path. Keep a fallback that does not impersonate first-party ChatGPT.
5. Add typed, proof-carrying re-entry from #233, then eventually sovereign evidence exchange from canonical TranchNode contracts after proper consent, revocation, independent verification and equal-information classical comparisons.

**Still unimplemented:** an APK, OpenAI account sign-in, a live model/function loop, HTTP MCP transport for the mobile app, server OAuth, live plugin registration, verified cross-host continuity, native worker deployment, privacy-tested peer-to-peer exchange.

## Verified references

- [ChatGPT MCP plugin quickstart](https://developers.openai.com/plugins/build/app-quickstart)
- [Plugin OAuth requirements](https://developers.openai.com/plugins/build/auth)
- [MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui)
- [Open-source SIWC integration](https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt)
- [SIWC preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations)
- [Responses remote MCP](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
- [MOTIF forest MCP v0.3 PR #160](https://github.com/the-static-collective/MOTIF/pull/160)
- [MOTIF proof-carrying answer PR #233](https://github.com/the-static-collective/MOTIF/pull/233)
- [MOTIF TranchNode-inspired app prototype PR #237](https://github.com/the-static-collective/MOTIF/pull/237)
