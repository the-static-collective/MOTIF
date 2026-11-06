# THOUGHT-010 — The Local Thought Door (MOTIF → JAR;VIS / Free Graph)

**Stage:** executable **local contract**, synthetic development, optional and manually invoked. Extends THOUGHT-006–009 in a stacked PR. Python 3.11 standard library. Not a deployed endpoint, not a connected agent, not a verified ontology, not a Free Graph owner adoption, and not permission to execute anything.

## Why this exists

A person should be able to say **"I have three ideas. Help me explore them"** rather than fill out a worksheet. Another project (JAR;VIS) can send a small versioned JSON request through the same local interface. MOTIF returns what reasoning it can support, what it *cannot* yet establish, and which geometric thought-space views (0..n) it selected. The physical placement of nodes never certifies a relation. Pencil remains exploratory; pen remains scoped and separately gated.

THOUGHT-009's actual router takes **typed goals**. This door offers a deliberately transparent keyword routing hint for simple questions (`connect`, `depend`, `conflict`, `enable`). If no keyword is recognized, it chooses `inventory` without geometry. This is **not semantic comprehension**, language learning, reliable parsing, or LLM instruction following. A caller can explicitly provide the task goals instead.

## Real source-owned contracts inspected

- [JAR;VIS README](https://github.com/the-static-collective/JAR-VIS/blob/main/README.md): independently owned local attendant; side effects require authorization; its local tools use a Node.js desk. No assumption JAR;VIS currently implements a MOTIF consumer.
- [Free Graph contract v0](https://github.com/the-static-collective/Free-Graph/blob/main/docs/contract-v0.md), [schema](https://github.com/the-static-collective/Free-Graph/blob/main/schema/free-graph-v0.schema.json) and [actual validator](https://github.com/the-static-collective/Free-Graph/blob/main/scripts/fg_core.py): canonical content addressed IDs, explicit task world cut, no authority transfer, nonconstituting seed records. An export packet is **only a proposal**; an owner gate is required for adoption.
- THOUGHT-007 source (`ThoughtField`) + THOUGHT-008 analysis (`ThoughtViews`) + THOUGHT-009 selector (`ViewRouter`). The door **calls the actual modules**, not a mock reproduction or disconnected design sketch.

## Request protocol

`motif.thought-door.request.v1` is a bounded JSON object:

- `request_id`: caller-chosen correlation label, **not an authenticated identity**.
- `caller`: `jarvis-local | free-graph-local | operator-local`. A declared local caller label does not grant permissions.
- `purpose` and optional `question` (bounded text).
- `mode=ideas`: **1..24 idea strings**, each given a distinct persistent concept and manifestation within one ephemeral local run; **same words never automatically merge**. Optional typed `relationships` of `{from:int,to:int,predicate,origin,status}` use *idea indices* and require explicit `AUTHORED` or `HYPOTHESIS_ONLY`. `AUTHORED` means caller declared the edge, not proved it. No edges are extracted from word similarity or proximity.
- `mode=snapshot`: consume an actual THOUGHT-007 `field_snapshot` plus THOUGHT-008 attributed `relations`, with an optional explicitly named `anchor` manifest. Reject missing bindings and unknown anchor names; no label lookup.
- Task controls: optional `goals` (`association`, `dependency`, `tension`, `affordance`, `inventory`), `max_views` (0..5), `phase` (`ABSTRACT_PENCIL`, `CONCRETE_PENCIL`, `PEN_REVIEW`), `seed`, `show_geometry` and `include_views`.
- `privacy=PRIVATE_LOCAL` by default, `PUBLIC_FIXTURE` only after caller explicitly declares synthetic/public provenance.
- `export=FREE_GRAPH_V0` is **held** unless **both** `privacy=PUBLIC_FIXTURE` and `allow_export=true`. Production private data are never automatically public-exportable. Even with export permitted, no network transmission or receiver-side admission takes place.

CLI:

```bash
cd experiments/thought-010
python door.py example-ideas.json
python -m unittest -v test_door.py
python demo.py > demo-results.json
```

The CLI reads one explicitly supplied local input file and writes JSON to stdout only. It does not start a server, open a socket, launch an external process, write to JAR;VIS, commit PEN, mutate Free Graph, or create durable records. It uses a self-deleting temporary ThoughtField when starting from raw ideas.

## Reply and review boundary

`motif.thought-door.reply.v1` includes typed questions (`QUESTION_ONLY`), source-only answers, selected view summaries, declared-privacy status, source fingerprints, a deterministic reason-routing receipt, and `external_authority=NONE`/`pen_status=UNCHANGED`. Output views with coordinates require explicit `include_views=true`; otherwise the caller receives only compact per-view summaries. The response is a **local output**; a consuming program must apply its *own* permissions before storing, publishing or transmitting it.

The private response does not echo idea labels by default, but stable graph digests and IDs are **not cryptographic anonymity**, and any caller with access to the original input or raw views can see context. Do not ingest sensitive user records into public synthetic fixtures. The contract is not a multiuser auth/privacy service.

### Free Graph v0 seed export

When explicitly authorized for `PUBLIC_FIXTURE`, the door emits a valid content-addressed `free-graph.packet/v0` with source/node/link IDs computed using Free Graph's canonical JSON algorithm:

- Each **manifestation** receives its own proposed `claim` node; multiple expressions with the same word remain distinct.
- Authored or hypothetical MOTIF edges become `connects` with **status `proposed`**, **authority `none`**, with the original declared status retained in an extension. No `constitutes`, `tests` or `bears-on` is invented.
- `task_world_cut.status=unresolved`, `modes=['seed','re-enter']`, with missing owner-current evidence and admission explicitly recorded.
- The packet remains a local exportable file **only when the operator saves the stdout**. It does not update Free Graph or confer authority on the receiving world.

The test suite can invoke the real **source-owner Free Graph validator**, when `FREE_GRAPH_CORE` is set to the full path of a checked-out `scripts/fg_core.py`. The CI workflow fetches a **pinned commit** of Free Graph to run this validation reproducibly; a passing shape/hash test is not a guarantee of semantic truth or future compatibility.

## Security, falsifiers and abstention

- Invalid schema, unknown caller label, excess input, unknown endpoints, forbidden relations, unsupported phases/permissions, non-JSON floats, and faulty bindings fail closed.
- No auto-linking of duplicate words; a source-provided expression is not an authenticated real-world concept.
- Switching from zero geometry to multiple geometry must preserve the exact same source-only answers and questions; changing geometric coordinates cannot create a PEN commitment.
- Source-root names and their supposed independence are **not authenticated**.
- Private input + attempted Free Graph export → HOLD, without a packet.
- **Maximum 120KB per request**; local input constraints are independent from upstream source log capacity.
- Free Graph’s content hashes guard payload integrity, *not truth, authorship or consent.*
- No actual JAR;VIS app code is changed by the MOTIF-side PR alone; a separate opt-in consumer should demonstrate the crossing with its own tests.

## Next experiment

An optional, explicitly invoked **local JAR;VIS Node consumer** should call this CLI through a pinned MOTIF checkout, refuse unrecognized response schema or any non-NONE authority, and expose the result to the human-first desk. A *real* integration requires an owner-reviewed JAR;VIS PR and a deliberate operator-enabled affordance. A private/real-data workflow will require owner-specific user consent, retention limits, and redaction verification.
