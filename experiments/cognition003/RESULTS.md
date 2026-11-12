# COGNITION-003 — Verified scores and repair provenance (post-evaluation)

**DRAFT / RESEARCH HOLD.** First scored evidence for MOTIF's proposed associative-resurfacing mechanism under a two-day synthetic author-written repair world. This file was prepared **after** the frozen tests. Preregistration `2af4905777eeeadd7ab213db323ce12fe5b92a45` is unchanged.

## Verified CI sources

- Public MOTIF 16/16 tests, original 640 heldout cases and independent owner action-receipt audit: https://github.com/the-static-collective/MOTIF/actions/runs/43126334720 — **GREEN**. 32 new fixed seeds x 5 regimes x 4 policies, plus 80 separately recorded development cases.
- Complete public results and every synthetic owner TEST/REPAIR receipt: https://github.com/the-static-collective/MOTIF/actions/runs/43126334720/artifacts/13902952914 ; zipped SHA256 `da56242271cae053515c7025524461be6de671f413633b34c17a63810c7dbdea`.
- Private MEMENTO owner-native Understory seven-record validation + public native Free Graph/GHoT integration: https://github.com/the-static-collective/MEMENTO/actions/runs/43126437990 — **GREEN**; tests and all task stages passed, with private MEMENTO history/ledger unchanged. This integration used the development seed 71001. Private records were never uploaded publicly.
- Earlier attempts: first run failed because tests imported `circuit` before the public module's allowed source-relative import; corrected the test import order. Next test run exposed an **instrumented lookup accounting error for an unmatched cue** (online BFS had 0 counted operations for its initial node lookup). The online graph accounting was corrected to include one cue-lookup operation, with no change to policy, source packet, test seeds or owner truth. The final test and 640-case rerun passed. These are engineering corrections, not a replacement blinded trial; the cohort remains researcher-selected, not independent.

## Primary outcome — actual independently simulator-verified repairs

Each policy sees 32 fixed heldout seeds per regime; max 2 real diagnostic TEST actions and 1 REPAIR per case. A successful repair requires a positive actual owner TEST receipt for the exact module and an independently verified REPAIR receipt. The 2 drifts may be unresolvable from old information.

| Regime | MOTIF resurfacing | Classical precomputed (strong) | Classical online BFS (strong) | Recent-only (weak ablation) |
| --- | ---: | ---: | ---: | ---: |
| Stable | 32/32 | 32/32 | 32/32 | 0/32 |
| Drift to historical alternative | 32/32 | 32/32 | 32/32 | 0/32 |
| Drift to unmodeled component | 0/32 | 0/32 | 0/32 | 0/32 |
| Echoed old source, duplicate root | 32/32 | 32/32 | 32/32 | 0/32 |
| Unrelated new cue | 0/32 | 0/32 | 0/32 | 0/32 |
| **Total** | **96/160** | **96/160** | **96/160** | **0/160** |

**The three source-aware controllers tied on every matched outcome**. This is an engineered demonstration of a *mechanism*, not MOTIF outperforming a strong classical retrieval method. The recent-only comparator is intentionally impoverished by losing its old source archive; its failure is not evidence that conventional memory retrieval is weak. Three regimes had a discoverable old-history solution by construction; two deliberately did not.

All informed controllers:
- Made exactly **192 independent diagnostic TEST actions** per 160 cases (32 stable + 64 alternative drift + 64 unmodeled drift + 32 source echo, none for unrelated trigger).
- Made **96** verified successful REPAIR actions.
- Made **zero unverified/unsafe repairs**, correctly declined all 32 unmatched cues, and refused the echoed primary source in all 32 echo cases while still recovering the independently sourced alternative.
- **Preserved historical Understory contacts:** the new activation references prior unresolved association events, and the actual private owner-native validation confirmed four historical contacts, two unresolved associations and one later activation. No old source was rewritten.
- **Actual native Free Graph graph** was used to validate and traverse candidate chains; all links remained unresolved and nonconstituting, and source-origin independence was enforced.

## Foreground-idle dividend: relevant but not novel
- Both MOTIF and strong classical precomputed controller spent **4 instrumented graph-link operations** per case in the synthetic prior-day idle window; on the new event each spent **1 indexed wake operation**.
- Classical online BFS did no prior precompile, with **5 instrumented wake operations** on matching cues (and **1** on unmatched cues), with **identical verified repairs**.
- That is only a deliberately defined graph-operation accounting difference; wall-clock latency, power, runtime cost, downstream social usefulness and real-world urgency have **not** been measured. Since the strong classical cache obtained the same prewarm benefit, no unique MOTIF advantage was demonstrated.

## Mechanism status and constraints
- `motif_resurface` emitted explicit resurfacing opportunities for **128/160** heldout incidents with source-bound candidate paths, including 32 drift-unmodeled incidents where old information could not locate the present fault. Those 32 were not falsely repaired.
- The new incident only provided a cue, not a question asking to recall the past. This shows **event-triggered associative recall in a programmed simulator**, not spontaneous novel intention or biological subconscious thought.
- GHoT decided whether the simulated idle preparation was eligible. No actual phone power measurement, background process, or user data was used.
- Every candidate was treated as `PENCIL_NOT_A_REPAIR` until a separate owner TEST result. No private MEMENTO storage write, remote task, learned weights or code self-update occurred.

## The next falsifier
Make the paths genuinely unfamiliar: outside-authored incident stream with altered vocabulary, uncertain source quality, relations longer than two hops, storage costs and real urgent timelines. Compare MOTIF and well-tuned classical provenance-aware index/search using the **same memory, compute, privacy and action access**. The new question is whether proactive associative reactivation improves **verified downstream user outcomes** beyond what ordinary indexed retrieval can accomplish—not whether reusing yesterday's notes is helpful in an authored game.
