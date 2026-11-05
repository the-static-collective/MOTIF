# MOTIF-021 — Before blaming the river, inspect how you asked

The user asked for a credits-free intelligence that can evaluate physical computation and eventually energy through the existing GHoT runtime. MOTIF-020 already crosswired a real GHoT CPU/memory resource benchmark. This new experiment asks an additional, less obvious question:

> **What if the diagnostic's question is malformed, and the world is answering faithfully?**

## The real unexpected failure

GHoT-002 initially queried three fixed public USGS gauges using an OGC `datetime` interval formatted *as dates only*. This inadvertently placed the interval's upper end at **00:00Z**, although the experiment ran around **15:00Z**. All three reported latest midnight values, provoking `HOLD_NO_FRESH_SOURCE_WITNESS_OBSERVED` under the predeclared twelve-hour criterion.

This **was not demonstrated sensor lag**: our question omitted the hours after midnight. The actual HTTP requests completed with 200 responses, about **824,285 public response-body bytes** and **1.567310 seconds summed request time**, but the response lacked the range required to answer the original question. The false-stale receipt is kept for audit at `ghot/evidence/002-initial-window-truncation-2026-11-05.json` in GHoT PR #136.

The question encoder was repaired to require full offset-aware UTC ISO timestamps in both URL query bounds, and a regression test now refuses date-only input. A separate real read-only public run then found three recent reported sensor values, each latest `2026-11-05T13:45:00Z`, with **822,771 payload bytes** and **1.839210 seconds** summed request time. This correction is a new physical test, *not a retroactive success* of the initial one.

## Another actual execution: stop once you have useful evidence

GHoT-003, a new source-owned run, then *physically executed* the stop-on-first-fresh policy. It sent **one** read-only USGS HTTPS request to Blue Earth, received **270,808 payload bytes**, spent **745,783,791 request wall ns**, obtained a public reported `2580 cfs` reading timestamped `2026-11-05T14:00:00Z`, and stopped before requesting Le Sueur or Mankato.

No queries were sent to the two skipped sites in that run. The source data is a *reported discharge measurement*, not flood advice, a stage threshold or proof of physical truth. Comparing this one-call run with the earlier all-three run is **not a matched causal savings experiment**: different times, source reporting states and networks could affect the comparison. 003 therefore makes no claim about electrical energy saved. Network wire bytes are not known; the captured bytes are HTTP response-body sizes.

## The new diagnostic

`experiments/021/question_integrity.py` verifies the exact source-owned Git blobs of all three machine-generated receipts from GHoT commit `1517d2ac822ed1e6cfa30320a0f1e4574b6b0e55`. It independently checks source identity, totals, timestamps, held dispositions, actual work, unknown-energy boundaries, and importantly that a *counterfactual* stopping policy is not misrepresented as an *actually executed* policy.

It proposes a new testable question:

> Can MOTIF check the fidelity of its question's URL, timestamps and requested horizon **before** expending resources or blaming the sensor?

This is a method-level correction. The upstream source-code fix was **human-approved and committed**, not autonomous model self-modification. There is no inference that this experiment increases intelligence globally. It demonstrates a real, reproducible failure of the experimental instrumentation and a physically retested repaired protocol.

```sh
python3 -m unittest discover -s experiments/021 -p "test_*.py" -v
python3 experiments/021/question_integrity.py --out question-integrity-021.json
```

CI cross-checks exact GHoT evidence source bytes and retains the computed diagnostic. No network requests are made by MOTIF-021 itself. Source-backed runs in GHoT:
- [initial misencoded UTC query](https://github.com/the-static-collective/GHoT/actions/runs/42049678911)
- [repaired full UTC question](https://github.com/the-static-collective/GHoT/actions/runs/42050095727)
- [actual conditional policy](https://github.com/the-static-collective/GHoT/actions/runs/42050598075)

The most important unresolved assumption is **time-of-issue source provenance**. Request URLs weren't preserved in those old per-request receipts; the diagnosis relies on documented code and a regression-guarded repair. Future probes should archive the exact requested URL, response status, appropriate timestamp, source bytes hash, and an attribution of power draw *only if a trustworthy device meter is present*.
