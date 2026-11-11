# COGNITION-002 — Observed integration results (post-test, research HOLD)

**Status:** cross-repository *synthetic read-only prototype* verified, not a deployed app or benchmark superiority. This report is post-test; the frozen integration contract at `c44f026d96713e410da2036f1f4cf37e6ea20e84` is unchanged.

## Two independently executed source-owner checks

1. **PUBLIC MOTIF/Free Graph/GHoT smoke** — https://github.com/the-static-collective/MOTIF/actions/runs/43121172828 — 13/13 unit tests passed, exact public Free Graph and GHoT source SHAs verified. Native Free Graph `validate_packet` accepted a synthetic `free-graph.packet/v0` with **3 sources, 4 nodes, 3 unresolved `connects` edges**. No `constitutes`, no owner-local authority, no inferred `descends-from`, and the task world cut stayed `unresolved`. Private MEMENTO was unavailable in public runner, correctly returned **HOLD** instead of a forged success. Synthetic-only artifact: https://github.com/the-static-collective/MOTIF/actions/runs/43121172828/artifacts/13900527503 (archive digest SHA256 `19f85aceac60f56a3fd47dce40806ce29f1c9a3968ef64982fb2ad4302a99e98`).
2. **PRIVATE MEMENTO native Understory test + complete cross-repo smoke** — https://github.com/the-static-collective/MEMENTO/actions/runs/43121190846 — **5/5 private owner validator tests passed**. The private workflow checked out the exact public MOTIF commit `ca836e59fdf63d823f4f1e82f899855a858cbbef`, exact Free Graph and GHoT revisions, and ran `MOTIF bridge.py --memento-root .`. MEMENTO's actual `validateUnderstoryRecords` structurally validated **4 invented historical records: two first-day contacts, one unresolved association, one later activation**. The pipeline revalidated its native public Free Graph packet and asserted no MEMENTO Understory or ledger files were mutated. All steps passed. The private synthetic result stayed in the private CI workspace; it was not uploaded to public artifacts.

### Repair history (not concealed)
The first public bridge passed its public contract tests, but native MEMENTO caught an invalid second-contact UTC hour `T010:00:00Z` in the first private integration trial. The public bridge was corrected to `T10:00:00Z` and a regression test for RFC3339 time added. The private workflow pin was updated to the corrected MOTIF SHA before the successful cross-repo run. No public or private source-owner records were altered. This is a useful example of why source-native validation must be exercised rather than claiming schema compatibility based on a reconstructed fixture.

## Cognitive comparison — still OPEN
The demo produces **five equal-budget single-critic question cards and five equal-budget council cards** over the same recorded source pairs. The council has five heuristic perspectives (skeptic, systems, story, planner, experimenter). This confirms only **question portfolio diversity**, not increased intelligence or usefulness. No independently verified outcomes have been measured for these questions. Values `verified_downstream_successes=0` are counts of observations not yet produced, not zero success rates on administered tasks.

## Invariants proven by these fixture checks
- No private MEMENTO files copied into public MOTIF or Free Graph; public CI cannot see owner-local data.
- No privileged model hidden chain-of-thought read or emitted. Understory is explicit *project-level residue*.
- No absent attention mislabeled `ignored`; no activation backdates original encounter.
- No candidate relation crosses the MEMENTO ADMIT/REFUSE/FOG membrane.
- No automatic self-modification, personal history collection, external network action by runtime, background mobile service, or measurable physical power savings.

## Next falsifier
A separate owner-consented source adapter and an independent evaluation set should test whether rediscovered older associations actually reduce task-solving time/errors or reveal a verifiable, previously missed useful hypothesis **versus** a strong classical provenance-aware retrieval baseline, holding compute/observation/action budgets constant. Allow council to lose.
