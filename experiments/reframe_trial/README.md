# MOTIF three-bet reframe pilot

**Status: synthetic pilot, research HOLD.** This runs learned moves, decision-value
probes and cumulative method reuse through one shared planner. Every case and
mechanism in the bundled pilot is authored. The three scenario labels use the
same transition grammar. Cross-family blind transfer remains an open test.

## What ran

1. **Learn a reframe.** Native MOTIF-006 induces a guarded reuse move from two
   verified traces and a guarded alignment/connection move from two more.
   The planner can propose them for different resources. The adapter maps a
   synthetic resource slot to the native MOTIF-002/006 type `bike`. Each macro
   still expands into its original steps, at full primitive cost. The primitive
   comparator can assemble the same steps.
2. **Buy the observation that changes the decision.** Choose among single and
   paired observations by the expected value of the best guard-valid route
   after the reply, minus observation cost. This is exact for the declared
   single-round menu, supplied joint prior and positive guards. A paired check
   costs two observations. The owner reveals only the committed reading,
   then separately verifies the underlying action sequence. Fixed order and
   entropy per observation are diagnostic baselines. Exact primitive
   planning plus the same decision rule is the strong control.
3. **Check compounding.** Independently rediscover and induce a third move in
   accumulated, last-round-only and frozen-start arms. Compare total charged
   work, then replay each learned candidate on a new binding and two guard
   counterexamples. The owner verifies a valid interface and rejects an invalid
   interface and denied permission. All three arms retain access to primitives.

## Observed results

| Arm | Verified deliveries | Total observation cost | Total execution cost | Net decision value | Planning guard budget |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed order | 7/8 | 8 | 63 | 27 | 2,304 |
| Entropy per cost | 7/8 | 8 | 63 | 27 | 2,304 |
| Exact primitive | 7/8 | 10 | 51 | 37 | 8,928 |
| MOTIF with learned moves | 7/8 | 10 | 51 | 37 | 15,312 |

For eight paired cases, a delivered outcome earns 14 synthetic units, minus
actual primitive and observation costs. The planning guard budget is shown
separately. With both candidate moves, the chosen plans use 13 outer calls
instead of 19. All four policies hold on the no-route case. Both exact policies
avoid spending an observation on it. Some relevant probes have a real cost
even when their answer forces the fallback.

| Library for discovering the next operator | Calls per discovery plan | Primitive execution cost per plan | Charged guard budget |
| --- | ---: | ---: | ---: |
| Accumulated | 3 | 5 | 1,101 |
| Last round only | 4 | 5 | 881 |
| Frozen start | 5 | 5 | 601 |

The charged budget includes the planned primitive replay length of each
candidate, source demonstration rechecks, induction rechecks and bounded
candidate verification. Failed macro replays may stop early, so the planned
length is a conservative charge. These counts are neither timings nor a
complete measure of engineering cost. The accumulated library compresses
the discovery plans but costs **more** under this measure. There is no
positive compounding result in this pilot.

The FIELD-004 receipt fix canonicalizes unordered target sets before hashing.
A subprocess test verifies identical output under three Python hash seeds.
The archived FIELD-004 packet remains a separate source revision.

## Run

Python 3.11+ and standard library only.

```sh
python -m unittest discover -s experiments/006 -v
python -m unittest discover -s experiments/field004 -v
python -m unittest discover -s experiments/reframe_trial -v
python experiments/reframe_trial/trial.py > motif-reframe-pilot.json
```

The report includes source digests, committed plans and checks, owner responses,
verified outcomes, and all three compounding arms. It is byte-stable across
the tested hash seeds.

## Bring separate case and outcome files

The scorer can use the same fixed grammar with separately authored case and
outcome files. These files stay outside the repository. The evaluator holds
outcomes and commits a contingent plan before revealing a reading to the
decision policy. Keep outcome files with the scorer until run time.

`cases.json`

```json
[
  {"family": "tabletop", "label": "case-01", "release_allowed": true,
   "alternative": true, "interface_unknown": false}
]
```

`outcomes.json`

```json
{"tabletop:case-01": ["reusable"]}
```

The outcome list contains the true members of `reusable`, `cosmetic_mark`,
and `interface_fits` if the interface is unknown. An omitted member is false.
Use `--cases cases.json --outcomes outcomes.json`. External input replaces
the scored cohort only. The bundled compounding protocol still uses the
fixed source demonstrations. A confirmatory study needs independent
mechanisms beyond this grammar, an independent scorer, and matched model,
human and classical baselines where applicable. A promising follow-up is a
goal-directed macro index that reduces candidate checks while preserving the
same exact execution objective. Compare that index with classical relevance
filtering before attributing any gain to learned operators.
