# MOTIF native MCP aperture 001 — read-only, stateless, real Python execution

**Source:** `the-static-collective/MOTIF` main. **Date:** 2026-11-15.

## Why this exists

MOTIF's earlier `Living Reasoner` plugin is skills-only. The fuller 18-tool Forest MCP v0.3 is in draft PR #160 and OAuth-only 11-tool gateway is in draft PR #243; neither is automatically available in a user's ChatGPT session. Those larger components need a real OAuth identity provider, a persistent volume, hosting, and separately authorized native execution.

This is a **small independent, safe first live aperture**: a stateless HTTPS MCP interface deployed using Vercel Python Functions, importing the **actual committed** `motif.reason_spine` and `motif.branch_garden` code from main. It uses no duplicate/reimplemented numerical algorithm, storage, credentials or third-party actions. It does not replace or merge either Forest PR.

## Available native MCP tools

1. `motif_analyze_case`: actually calls `motif.reason_spine.analyze` on a bounded authored `motif.reason-case/v1`. Explains ranked probes, contradictions, witness revisions and abstention, with human review.
2. `motif_compare_policies`: actually calls `motif.reason_spine.comparison`, running original fixed-order classical, strong classical information-gain, and MOTIF cost/risk-sensitive policies on the same supplied case. LLM and human transfer remain **NOT_RUN**.
3. `motif_information_gain`: actually calls `motif.reason_spine.information_gain` after original `validate_case`.
4. `motif_merge_review`: actually calls `motif.branch_garden.merge_verdict` and returns only a recommendation; it **never merges**.
5. `motif_public_branch_leads`: reads **one** page of publicly visible GitHub branch heads and SHA pins, then calls native `motif.branch_garden.suggest` for optional lexical triage. This is source-discovery only; not the full native Git branch reader, not source inspection, no executing unmerged code or method promotion.

**Status semantics:** Tests can prove code runs on authored fixtures. A working endpoint can prove calls are executable. Neither establishes artificial general intelligence, causal truth, novel algorithms, valid external-source identity, or improved LLM performance.

## Endpoint and deployment

- `GET /health`: unauthenticated public readiness metadata only.
- `POST /mcp`: standard stateless JSON-RPC 2.0 Streamable HTTP, `initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`. Returns ordinary `application/json` tool results. No server-side session.
- `GET /mcp`: 405 (stateless; no SSE subscription). This is intended for MCP clients supporting JSON response mode.
- `POST /api/mcp`: equivalent underlying Python function.
- `vercel.json` rewrites `/mcp` and `/health` to that Python function.

**Host:** Vercel project linked to `the-static-collective/MOTIF`, production branch main, Python 3.12 (Vercel-supported runtime; CI also tests canonical source on 3.11). Project name can be `motif-native-readonly-mcp`. This project is independent of an unmerged OAuth gateway and requires no Railway persistent disk.

## Security/operating boundary

- **No authentication:** The first stateless aperture intentionally contains ONLY bounded, public/author-supplied, side-effect-free computations; it is not a personal data service. Do not send private research records, financial data, personal information, unpublished witness reports, confidential messages, credentials or user-specific memory to this public endpoint.
- It has no state, no sessions, no arbitrary filesystem reader, no Git merge API, no external write, no Docker socket, no native unmerged executor, no API keys, and no administrative tools. Tool annotations are readonly.
- The public GitHub branch reader uses a **fixed trusted public URL**, cannot access arbitrary URLs, and limits one page/one remote request, request length, page number and response size.
- Server rejects unsupported methods, extra tool arguments, malformed cases, JSON bodies exceeding 40KB, and output beyond a bound. Negative tests assert blocked `forest_execute_reviewed` and similar tools.
- Public unauthenticated compute may still incur Vercel hobby-plan execution/egress charges through abuse or load; monitor platform usage and apply deployment limits if available. For private cases use the future OAuth Forest gateway (PR #243) instead.
- This endpoint never stores user cases but hosted platform infrastructure can retain request metadata. No model-generated tool call constitutes consent to external action.

## Proof gates

1. **CI_TESTED:** GitHub Actions native-core import, test of real output, matched strong-classical comparison, HTTP JSON-RPC handshake, malformed case rejection and no-write tests pass.
2. **HOST_DEPLOYED:** Public HTTPS origin responds `/health` and `/mcp`, advertises exactly 5 reviewed tools.
3. **NATIVE_RUN_VERIFIED:** An authenticated operator independently uses the deployed tool to run the original author-designed fence fixture (which remains a synthetic test), not merely an import success.
4. **CHATGPT_CONNECTED:** A **new** MCP-backed plugin is created/connected from the above origin and explicitly used for at least one case; new because current platform's skills-only plugin cannot gain an MCP declaration after initial creation.
5. **FOREST_AUTH_PENDING:** Existing full Forest OAuth gateway remains separate, no claims of production login or execution of PR #160's unmerged methods.

## Example JSON-RPC probe

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"motif_analyze_case","arguments":{"case":{"schema":"motif.reason-case/v1","question":"Which invented relation explains the mismatch between two drawings?","goal":"Choose the next safe observation in a fictional drawing.","hypotheses":[{"id":"camera","predictions":{"angle":"yes"}},{"id":"post","predictions":{"angle":"no"}}],"tests":[{"id":"angle","cost":0.04,"risk":0}],"reports":[]}}}}
```

Expected native result: a `motif.reason-spine/v1` receipt with proposed next probe `angle`, human review, no automatic external action and no claim of real-world causal verification.

## Path to full MOTIF v0.3

Once a real OAuth issuer, persistent volume, appropriate hosting and owner-sub configuration exist, return to the already-written 11-tool read-only Forest gateway (PR #243, child of #160). Connect it as a separate protected MCP origin and test end-to-end authorization; do not silently replace this stateless public read-only endpoint with arbitrary method execution. Read actual PR source and fresh tests first.
