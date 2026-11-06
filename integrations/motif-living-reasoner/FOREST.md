# MOTIF Living Reasoner — Forest MCP v0.3

**Scope:** live GitHub source indexing, bounded RING-003 selection, RING-002 isolated native demonstrations, RING-004 **same-case synthetic** composition, and durable human checkpoints. Every new branch is **indexed as source only**. There are **three approved source-native methods**, not an arbitrary branch executor. This package has no host-level deployment or connected ChatGPT plugin by itself.

## Source-verified design

- RING-003 pinned commit `9e4fc10c02e09f8e4507ab33994bc2a3115cc3b8`: the exact three-method declared-affordance graph and exact finite subset policy are transcribed into `mcp_server/forest.py`. The declared utilities **do not establish real task success**. Test the port against the original RING-003 suite before changing policies.
- RING-002 native adapters pinned individually:
  - `geometry.procedure-repair`: `a3dc551ababa40c29975c9b54c4eaa515d9dc18c`
  - `thought.language-dev`: `a38c617641adffe52cd4df283996a58f0fe7b973`
  - `reason.proof-objection`: `d0808c6a829fc6ef15d736c325790ddb4d169ab1`
- RING-004 pinned controller `86a0c797bc797e895cf7d17727f34b044a532f30`: three original methods process one source-owned synthetic case packet, with ablations and classical controls. Existing authored synthetic results: both full three-native and strong classical methods return 32/32 for each of two seeds; **no general advantage demonstrated**.

All claims about code execution apply to the source-owned experiment's scope. This MCP package's automated tests cover its wrapper, validation, selection and human checkpoints; they do **not** by themselves rerun the native Docker controller. Reproduction requires Docker and a full git checkout.

## MCP tools (18 total)

Nine previous tools (`catalog_cartridges`, `select_methods`, `start_session`, `resume_session`, `list_sessions`, `record_feedback`, `execute_reviewed`, `reopen_session`, `reflect_session`) still operate the common-case six-operator engine.

Nine forest tools are newly available:

| Tool | What it does |
|---|---|
| `forest_goals` | Show pinned approved methods and typed RING-003 goals |
| `forest_catalog` | Paginate live GitHub branches (or complete cached SHA snapshot) |
| `forest_inspect_source` | Read one bounded UTF-8 file by the indexed exact git commit, never execute |
| `forest_route` | Optimize a declared multi-tail RING-003 hypergraph under a budget |
| `forest_start_trial` | Preserve a pinned RING-002 or RING-004 plan, stop at `PLAN_REVIEW` |
| `forest_resume_trial` | Recover a trial and its checkpoint |
| `forest_list_trials` | Retrieve earlier trials |
| `forest_feedback` | Record actual human approve/accept/hold at allowed checkpoint |
| `forest_execute_reviewed` | Run Docker-pinned source-native benchmark; stops at `RESULT_REVIEW` |

### Minimal selection-only example

Run `forest_goals`, then `forest_route` with:

```json
{"goals":{"cross-instrument-evidence-review":18},"budget":6,"max_methods":3}
```

This selects the original three methods, because RING-003's declared multi-tail edges recognize that they jointly supply the requested affordance. The label `cross-instrument-evidence-review` remains a **design hypothesis**, not proof of general-world understanding. To execute a trial, create it with `forest_start_trial` using the same goals, review the proposed source pins and benchmark type, approve through `forest_feedback`, then call `forest_execute_reviewed`. Inspect results and `forest_resume_trial`, then return to the human rather than automatically accepting an experiment.

### Forest discovery behavior

`forest_catalog(refresh=true)` uses GitHub's public `/branches` API, 100 entries per page, maximum 20 pages / 2,000 passports; an incomplete scan fails and retains the previous complete snapshot. `forest_inspect_source` may read only a pinned branch `README.md`, `docs/...`, or `experiments/...`, at most 60 KB of UTF-8 text; it checks the blob SHA1. The branch's *appearance* never changes the three-method executable allowlist. The optional `MOTIF_GITHUB_READ_TOKEN` is a **read-only private environment variable**, not a required plugin secret. Since this repo is public, anonymous public API requests work subject to rate limits.

### Executing original native sources

Use a **local trusted worker machine with Docker**, not the public-facing API container. A full MOTIF checkout is required, including the 3 original native method commits and RING-003/RING-004 commits. The controller is pinned. The native workers use no-network, non-root, read-only Docker with finite time and resource bounds; no arbitrary code from newly discovered branches is run. The controller itself is source-owned trusted Python, **not** security-hardened against a malicious project maintainer. Pin the worker's Docker image by digest for production.

```sh
# On a machine with GitHub access and Docker:
git clone https://github.com/the-static-collective/MOTIF.git /opt/motif
git -C /opt/motif fetch origin --prune '+refs/heads/*:refs/remotes/origin/*'
docker pull python:3.11-slim
export MOTIF_CHECKOUT=/opt/motif
# Configure MOTIF_MCP_API_KEY and MOTIF_MCP_DB in private environment.
python -m mcp_server.server
```

The included `Dockerfile` starts **the front-door MCP service only**. It does not install Docker or expose the host's socket; therefore it cannot execute original native benchmarks unless a **separate trusted native runner** is provided. Never mount the host Docker socket into a publicly reachable web server to bypass that separation. When the native runner is missing, the tool returns HOLD and leaves the approved trial in READY for a properly equipped worker.

### Deployment boundaries

- HTTPS endpoint required to connect to cloud ChatGPT. Bearer secret and storage volume must be configured through the host's secret manager; don't commit credentials or send keys in chat.
- SQLite persistence requires a mounted durable disk and a **single worker process**; this starter is not a scaled multi-tenant or cross-instance service.
- Native runs are experimental **synthetic**, not real-world causation or permission. RING-004 ties a strong classical baseline; independent real tasks and controls remain required to claim value.
- Updating from a future source commit requires deliberate review and changed pin constants, not implicit admission.

## Test

```sh
python -m unittest discover -s skills/motif-reasoner/tests -p 'test_*.py' -v
python -m unittest discover -s mcp_server/tests -p 'test_*.py' -v
```

To rerun the original RING-004 benchmark rather than wrapper mocks, follow `experiments/cartridge-ring-004/README.md` on the exact pinned experimental branch.