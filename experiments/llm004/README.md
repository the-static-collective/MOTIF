# MOTIF LLM-004 — REASON HYPERMAP

**Status: executable research prototype; DRAFT / NOT MERGED / NOT DEPLOYED.** Stacked on [LLM-003](https://github.com/the-static-collective/MOTIF/pull/316) → [LLM-002](https://github.com/the-static-collective/MOTIF/pull/314) → [LLM-001](https://github.com/the-static-collective/MOTIF/pull/311). MOTIF owns local reasoning; Free Graph remains a separate historical traversal substrate. JAR;VIS, Understory, MEMENTO and personal source records are not imported.

## Reason Hypermap, in one sentence

**A mistake is not a node marked 'bad'; it is a traceable transition from a provisional explanation, through a discriminating test and an independent source report, to a revision of the remaining possible explanations and the next choice of inquiry.**

### Actual executable graph

```text
hypothesis H7 ──┐
prediction P   ├─[reified test-revises-possibilities hyperedge]──> source receipt R
test T         ┘                 │                           ├──> counterexample C (when reported)
                                └───────────────────────────└──> posterior revision Δ
                                        │
                                 revised hypotheses
                                        │
                           next question selected for value
```

`hypermap.py` implements immutable-value source-rooted nodes, multi-terminal hyperedges, independent owner receipt calls, a probabilistic hypothesis family, canonical content-addressed event IDs, immutable prior snapshots, no retroactive rewriting and optional counterfactual PENCIL forks. Nodes can be hypotheses, source observations, predictions, tests, receipts, counterexamples, revisions and unresolved questions. The source-root set prevents repeating the same report as multiple witnesses. Model-generated claims cannot become independent observations.

`ReasonHypermap.view()` exposes five bounded lenses—epistemic, causal, decision, lineage, and narrative—over the SAME record identities. Changing the lens never changes source content, authority, history or consent.

`free_graph_adapter.py` exports a real [Free Graph v0](https://github.com/the-static-collective/free-graph) packet with source IDs, node IDs, link IDs, task world cut, non-imports and residual fog. Many-to-many hyperedges are represented as ordinary intermediate artifact nodes and existing `connects`, `tests`, `bears-on`, `descends-from` relations, without inventing a sixth verb or an `owner-local` constitution. The official Free Graph validator at pinned public source commit `ec0ad8743c5faac3f3675760bbafcbcb1df846c1` is independently run in CI against the ACTUALLY generated fixture. This validates historical traversal format, not metaphysical or real-world truth.

`viewer.py` renders the generated map as a self-contained, offline clickable HTML. Users can switch the five epistemic/causal/decision/lineage/narrative lenses, click source nodes and reified hyperedges, inspect exact provenance, and review the hypothetical posterior. All pixels come from the generated real fixture JSON—not invented graph edges. It is **read only**, browser-contained and contains only a curated public synthetic illustration (selected by the independent grader as a helpful wrong hypothesis, not a representative case). CI also syntax-checks its shipped JavaScript.

## Source-owned actual experiment

Research frozen at `PREREGISTRATION.md` before implementation (`8bc8ec5db637e4fb7dc19c45d15246b73c19cfe9`). Use the actual independent fictional owner in `../llm003/error_dividend.py`: eight possible Boolean rules, 160 author-generated heldout owner seeds, four feedback regimes, zero to three probes. The posterior and evidence selection are computed without seeing the hidden true program. Separate `grade()` may consult owner truth **only after** probe results; grade metrics never enter the public graph or the policy. No human or physical real-world data.

Primary arms: Shannon information gain, deliberately challenging the favorite, Bayes predictive-decision gain, and no-probe. A separately frozen post-hoc fairness control, `classical_ig_stop`, uses the SAME 0.04 rational-stopping rule as the decision-gain policy. All policies have the same maximum budget and source access; some rationally spend fewer probes.

### Observed 160-seed toy results (2026-11-12)

| Independent reporting regime / maximum budget | Strategy | Final accuracy | Net accuracy − 0.04 per actual probe |
| --- | --- | ---: | ---: |
| Truthful / 1 | Classical information gain | 80.86% | 76.86% |
| Truthful / 1 | Challenge favored hypothesis | 81.02% | 77.02% |
| Truthful / 1 | **Bayes decision gain** | **82.97%** | **78.97%** |
| Truthful / 3 | Classical information gain (forced probes) | 100% | 88.00% |
| Truthful / 3 | **Classical IG + rational stopping** | **100%** | **91.38%** |
| Truthful / 3 | Challenge favored hypothesis | 100% | 88.00% |
| Truthful / 3 | Bayes decision gain + rational stopping | 99.69% | 90.69% |
| No independent source / 3 | Any spending policy | 68.67% | at most 56.67% |
| No independent source / 3 | No probe | 68.67% | **68.67%** |

All values are fractions of correct author-owned eight-input synthetic decisions, not verified real-user answers. Rounded values come from GitHub Actions; inspect the full machine JSON for every regime and budget. In truthful one-probe settings, decision-focused selection had the best point result; in truthful three-probe settings, **strong classical information gain with the same rational stopping rule won**, even though decision-gain and challenge methods also found useful counterexamples. The particular change in measured net utility can reflect cost-aware stopping; it is not novel mathematics or general performance evidence.

### What happened to wrong hypotheses?

- The graph stores *reported contradiction*, *independence of witness root*, and *posterior update* as separate types of event. Inaccurate owner reports are distinguishable from truly verified counterexamples only to the separate scorer.
- `wrong_helpful_net` requires an actually wrong provisional guess, independent and *truthful* source report, plus an independently graded accuracy improvement that exceeds the cost of the test. An unverified or echoed report never earns this reward.
- A correct prediction can also be informative. Some wrong guesses result in no measurable gain or cause regressions. Wrong final user-facing answers are never beneficial by fiat.
- With noise, the method can learn the wrong lesson. When feedback is absent or an echo of an existing root, no posterior update occurs; continued probes merely incur cost.

## Run locally (Python 3.11 standard library)

```sh
PYTHONPATH=experiments/llm003:experiments/llm004 python -m unittest discover -s experiments/llm004 -p 'test_*.py' -v
PYTHONPATH=experiments/llm003:experiments/llm004 python experiments/llm004/run_experiment.py --out /tmp/reason-hypermap
python experiments/llm004/viewer.py /tmp/reason-hypermap/specimen-map.json /tmp/reason-hypermap/reason-hypermap.html
```

Run source-owned Free Graph validation against the pinned public contract:

```sh
python external/free-graph-contract/scripts/fg.py validate /tmp/reason-hypermap/specimen-free-graph.json
```

Generated files: `reason-hypermap-study.json` (all policies), `specimen-map.json` (public source-owned graph), `specimen-free-graph.json` (portable projection), `specimen-counterfactuals.json` (PENCIL alternatives and independent test grading), and `reason-hypermap.html` (offline explorer). GitHub Actions uploads them as a downloadable artifact; the HTML viewer is already self-contained and requires no server.

## Honest boundary

The original LLM-003 trained genuine pretrained SmolLM2 suffix graph controls. **LLM-004 does not directly run that model.** It adds a source-respecting, testable memory substrate for what future model forks might believe and revise. Its correctness checks are about provenance, typed events, counterfactual isolation, Free Graph portability and synthetic policy evaluation—not general reasoning intelligence or live API integration. There is no production memory sync, owner authentication, physical safety certification or autonomous actuation.

The next real benchmark must take newly authored, heldout JAR;VIS-style public/consented tasks, bind the actual LLM-003 pretrained model proposals to this map, and independently verify whether counterexample memory improves *later* decision accuracy per cost against classical search and a no-memory model. A claim of real improvement requires this second owner and real source pressure.
