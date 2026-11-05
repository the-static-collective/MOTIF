# MOTIF MAP-003: Ask Free Graph, not a hardcoded four-organ pipeline

This is a source-pinned downstream consumer of [Free Graph REASON-SPACE-001 PR #20](https://github.com/the-static-collective/free-graph/pull/20) and [MOTIF MAP-002 PR #74](https://github.com/the-static-collective/MOTIF/pull/74).

**The architectural pivot:** The four native reasoning tools are not permanent named steps of a universal pipeline. Each operator contributes a `probe`, `finding`, or `receipt` to a historical **Free Graph reasoning trail**. Questions, hypotheses, source loci, unresolved claims and future tests are represented through the **existing five portable Free Graph verbs** and immutable content-addressed records. Different future problems can have different tools and topologies without creating a new graph grammar or universal authority.

## What actually runs

`ask_freegraph.py` verifies all four original Free Graph Python source files—`fg_core`, `fg_ops`, `reason_space`, `motif_reason_bridge`—against exact Git blob SHA-1 and checks `git rev-parse HEAD` against the pinned Free Graph owner commit `a74d018a4ebc7398733e5d98da8f7d389621fb9a`. It also verifies the original historical MOTIF MAP-002 receipt's Git blob SHA-1 at its immutable source cut. Nothing is installed from a network or dynamically imported before these checks.

Then it invokes the **actual source-owned Free Graph code**, which converts the prior native multi-organ investigation to Free Graph v0 historical packets:
- `all`: full question, candidate, five native probes/results, next proposed question;
- `evidence`: bounded emphasis on hypothesis, tests and recorded findings;
- `next`: bounded look at what remains unanswered.

Their immutable record IDs remain identical where a record appears in multiple lenses. None grants owner authority. All cuts are `unresolved` and `re-enter` only.

Finally **MOTIF asks Free Graph itself** to analyze the resulting graph. Free Graph's original `pressure(packet)` inspects `tests` and `bears-on` records against an unresolved hypothesis. It returns a typed gap and proposes the smallest *kind of next question*—not a remote tool execution.

The current frozen case has two refusals and three unresolved bearings with no support. Thus it proposes: **"What source-owned, reproducible positive specimen would actually support this claim, rather than merely connect to it?"** This is a deterministic abstract graph rule applied to a real prior source-owned result. It is not evidence of autonomous general reasoning.

## What remains deliberately unimplemented

No unrestricted GitHub read, live GRAFT scout, new source-owner execution authority, new GRAFT adapter, signed owner gate, human contact, repository rewrite, remote provider calls, model training or measured Joules. The prior research fixture remains pinned and static; we haven't demonstrated selecting among arbitrary new tools or discovering new schemata.

Original source rights and currentness remain with source owners. **Provenance may travel; authority stays local.**

## Reproduce

Checkout the exact Free Graph commit from `freegraph.lock.json` into `sources/free-graph` alongside this MOTIF branch, then:

```sh
python3 -m unittest discover -s fieldwork/map-of-maps-003 -p 'test_*.py' -v
python3 fieldwork/map-of-maps-003/ask_freegraph.py --freegraph-root sources/free-graph
```

The dedicated GitHub workflow runs the real original Free Graph code against MOTIF's byte-pinned earlier receipt, tests the three-lens identity invariants and retains JSON evidence.

**Scientific status:** A source-owned experimental *data/control-plane interface* in two GitHub PRs, not a merged or deployed multi-tool autonomous agent.
