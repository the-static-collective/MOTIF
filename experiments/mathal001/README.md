# MATHAL-001 + NUNUMATHAL-001 — Crossings that earn their arrows

**Status:** experimental, synthetic, dependency on unmerged `FIR-001` (`experiments/fir001/fir.py`). Read-only with respect to MOTIF's existing experiments; no external actions or autonomous proof generation.

## Implements

- `mathal.py`: typed, deterministic FIR `Program` and `Step` operations against a *copy* of a declared `FIRWorld`; exact constitutional markers include **identity and warrants**, not just role counts. An aborted program refuses to commit partial results and still retains its attempt receipt. `compose_runs` checks the complete intermediate world, not a printed carrier label. `receipt_projection` supports limited query-indexed projections **without claiming global minimality**.
- `nunumathal.py`: independently computed finite simple graph transitions (add isolated vertex, attach leaf, subdivide edge), with exact changes to vertices, edges, components, isolates, and cycle rank. `compare` applies a **numeral-removal control** to the computed signature and always leaves any *shared-mechanism* inference as **I (proposal)**, even if signatures match.
- `nominate_motif003`: a read-only integration point taking actual `MOTIF-003` synthetic affordance candidate rows and converting the hypothetical moves to **I**, never admitted facts. No mutation of MOTIF-003's state or permissions.

## Run

```bash
cd experiments/mathal001
python -m unittest -v test_mathal.py
```

Works with Python 3.10+ and standard library only.

## Honest limitations

- No proof-term checker: a `Warrant` is still a declaration, not cryptographic or mathematical verification.
- Exact world composition depends on explicitly typed `Claim`, `Relation`, string addresses, and `Warrant` records; there is no general graph-to-FIR compiler or all-purpose theorem prover.
- The second-order signatures are small, intentionally lossy controls, **not** proof of mechanism identity or scientific novelty. A countermodel is included: attaching a leaf and subdividing an edge can have the **same five-component delta but different graph structures and mechanisms**.
- A receipt projection is a *declared view*, not automatically the globally minimal sufficient receipt for all future questions.
- The MOTIF-003 adapter is experimental read-only nomination, **not a production router** or automatic learning system.

## Source ancestry

Owner-authored Google Drive texts: *nuMATHELOLOGY*, 2nd ed., chapters 1–10; *nunuMath v0.2* §§5–10, 19; *nunuMATH: First Course in FIR Systems* chapters 6–14; *Twelve Worlds Before the Arrow*. Compatible with the draft FIR-001 branch. Test witnesses are synthetic, not claims about a real-world action system.
