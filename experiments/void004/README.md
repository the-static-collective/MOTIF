# VOID-004 — The Ten-Try Fortress (iteration-aware wave survival)

**Research HOLD / stacked draft following VOID-003.** A user's explicit research prompt asks whether MOTIF, *knowing that attempts will repeat*, will invest in information whose benefit arrives in a later try. This deliberately small, standalone survival-wave game makes that question executable and falsifiable. It is an **author-designed synthetic fortress**, not a Crafter extension, real survival experiment, independent benchmark, autonomous general agent or superiority proof.

## The fortress

```text
###########
#.........#
#..A...B..#
#.........#
#....H....#
#.........#
#..C...D..#
#.........#
###########
```

`H` is the human-defended hub. The four reachable relay towers `A`–`D` advertise which *wave numbers* they might reveal, not the attack directions. All four are four legal orthogonal steps from the hub. The fortress faces **24 sequential waves**, each secretly coming through one of four gates (`N/E/S/W`). Defend all 24 consecutively to clear. The same map and threat schedule return on each attempt. Every wrongly defended wave ends that attempt, but its actual direction is observed afterward and may be learned for next time. Defense, source receipts, and movement are simulated; nothing affects a real game or person.

Each attempt permits up to four pre-wave movement steps and **one** information charge. The charge can either read the relay reached by physically traversing the map (giving three currently unknown or redundant future wave directions), **or** be saved to sonar one current unknown wave. The choice makes information an investment rather than a free addition. The agent knows it can retry up to 14 times and that 10 is the desired target, not a required stopping limit.

The owner alone knows the 24 directions. An agent receives the public map, known wave numbers at relays, and actual source-backed observations after a legal move/sonar/defense. It cannot read hidden gate directions before an authorized revealing event. Only witnessed facts carry across attempts. Imagined future information access stays PENCIL, not INK. Hashes preserve local integrity, not third-party identity.

## Fair comparisons

- `motif_iterative`: invokes the repository's **original MOTIF-003** `analyze_first_moves` and considers downstream opportunities to use future information. Its explicit deterministic heuristic is not an optimized trained learning policy.
- `classical_iterative`: a strong, conventional *scoped* one-trial expected-survival model plus a discounted future-information value term, with identical information and attempts. The baseline is not an exact globally optimal POMDP.
- `classical_immediate`: saves sonar for the immediate threat rather than advance scouting; useful diagnostic but **not a strong general comparator**.
- `classical_no_memory`: keeps the strong classical selector but clears acquired facts after every defeat; tests whether retention matters, not a fair claim of MOTIF-specific superiority.

Both iteration-aware methods are permitted to tie or lose. None can inspect the test seeds' hidden lanes, and all encounter identical seed-specific fortress truth. Because each run is deterministic, repeating one seed is not independent evidence; the primary unit is the 24 **predeclared distinct heldout map/wave seeds**.

## Reproduce

Python 3.10+ standard library, from repository root:

```bash
python -m unittest discover -s experiments/void004 -p 'test_*.py' -v
python experiments/void004/waves.py --split development > void004-development.json
python experiments/void004/waves.py --split heldout --full-receipts > void004-heldout.json
```

The Actions workflow `.github/workflows/void-004.yml` verifies the preregistration file's SHA-256 and unit tests before executing the heldout study, checks source integrity and source-limited results, then stores the **full receipts** as a downloadable artifact. Locally authored game code should not be mistaken for third-party blind evaluation. The 24 heldout seed values and fixed primary metric are frozen in [PREREGISTRATION.md](PREREGISTRATION.md).

## What counts as learning here?

- The controller can replan across attempts using actual failed defenses, sonar readings and relay notes. These are factual receipts within the game.
- No model weights update; the program applies explicit deterministic policies to accumulated historical knowledge. Calling this *learned neural intelligence* would be inaccurate.
- Success is an engine-confirmed complete 24-wave defense, not predicted survival or territory count.
- `completed_at=11` or later is a real answer; an unfinished agent is counted as 15 restricted attempts in the aggregate. Always show failures.
- Do not present `motif_iterative` vs weak no-memory or short-horizon arms as evidence of improvement over classical planning. The decisive comparison is the **same-memory `classical_iterative`** baseline.

## Next harder falsifier

Try the same protocol on independently authored maps, map-layout drift between resets, noisy or contradictory tower reports and choices involving physical resources. Then test online operator revision and real sandboxed Crafter gameplay. Freeze fresh seeds before each challenge and report when classical methods remain equally good or better.
