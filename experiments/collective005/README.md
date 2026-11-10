# COLLECTIVE-005 — Primitive Birth / The Question the Old Language Cannot Ask

**Stacked draft** on COLLECTIVE-004 #245 (then #239, #235, #233,
THOUGHT-028). Research only; no merges, installation or autonomous action.

## User-approved frontier

Can MOTIF diagnose that even its expanded question language cannot
distinguish two possible worlds, construct a NEW executable measurement
from raw underlying graph primitives without being given a prewritten
operator named after the target answer, and demonstrate that it works on
independently authored heldout mathematical graphs?

This escalates COLLECTIVE-004's graph-edge/degree-pair vocabulary.
The COLLECTIVE-005 primitive language does NOT contain a built-in PATH4,
COUNT_SIMPLE_PATHS, or DEGREE_PAIR operation. It supplies four lower
level atoms: BIND_VERTEX, ADJACENT, ALL_DISTINCT, COUNT. A human-supplied
growth rule repeatedly appends one bound vertex and one adjacency condition,
bounded to four edges. This is BOUNDED PROGRAM SYNTHESIS, not unlimited
primitive invention or autonomous semantics.

## The actual source

Use the original Read-Wilson 1998 Atlas of Graphs via LEGIT-022, with
NetworkX 3.4.2 and independently verified source data SHA256:

    73fc416df0164923607751cb759f4ae81deb5f6550bf25be59c86de3b747e41d

Original source-protocol freezes 14 train and 28 heldout graph pairs before
candidate program construction. Original data independently authored;
pair selection and public train/heldout split are MOTIF engineer-authored,
not externally blind.

COLLECTIVE-004 established that 12/28 heldout graph pairs could not be
distinguished by the original feature menu. Its new degree-pair existential
questions resolved 10/12 and explicitly preserved two HOLDS: Atlas 482/483
and 552/553. The training split contains another unresolved pair 769/770.

## Primitive growth, actual executable source

On the Atlas 769/770 TRAIN problem, MOTIF first checks that *both* old
question grammars genuinely have identical signatures for the two models.

It composes questions using increasingly many bound variables and adjacency
constraints. Simple path counts with one, two, and three edges DO NOT
distinguish the training models. Four edges does: Atlas 769=76 and 770=73
unordered simple four-edge paths.

The system generates literal nested executable Python loops from the new
typed AST, not a prewritten four-edge path counter. A separate
permutations-based finite enumerator and independent NetworkX path-search
oracle confirm each candidate.

The selected AST freezes on TRAIN. The heldout evaluator uses that exact
program on all 28 originally selected Atlas pairs, without adapting it.

| Previously unresolved original Atlas pair | Frozen program counts |
| --- | --- |
| 482/483 | 25 / 22 |
| 552/553 | 21 / 18 |

The old-plus-degreepair grammar distinguished neither pair. The newly
composed measurement distinguishes both. A local synthetic Atlas source
owner is asked once for each of two possible realized graphs in each pair:
4 independently rechecked observations, 4/4 correct finite selections.

A strong classical enumerator with access to exactly the SAME low-level
primitives and depth budget obtains identical results (2/2). This is
a new expressive capability relative to our restricted former language,
NOT superiority over classical program synthesis.

## Proof-carrying source record

Every new result contains the actual source-pinned National Treasure
Same State, Different World question, actual independently originated
Atlas source protocol, precise candidate graph pair, prior-grammar
inadequacy evidence, the whole unsuccessful smaller-program search,
the typed AST, emitted runnable code, finite oracle checks, source
count observation, source revision and limitations. On re-entry all
relevant results are rechecked, and zero investigative questions are
repeated. Forged observations and revised sources refuse to verify.

## Boundaries

- Not fundamentally novel mathematics: enumerating simple paths is known.
- Not unrestricted primitive invention: atoms, AST and depth bound supplied.
- Not unmodeled-world discovery: both hypothesis graphs supplied; only
  simulated source owner's realized choice is hidden.
- Not external-blind: original graph data independent-origin, but split
  publicly reconstructible and our own benchmark design.
- No general language understanding, verified physical-world fact,
  live external agent, collective intelligence superiority, or deployment.
- No measured net latency gain: replay verification also costs compute.

## Reproduce

Source checkouts via GitHub Actions. Python 3.11, Node, Git and pinned
NetworkX 3.4.2.

    python -m pip install networkx==3.4.2

    NT_CASE_ROOT=external/nt-cases NT_BOX_ROOT=external/nt-question-box \
    ATLAS_ROOT=external/motif-legit022 \
      python -m unittest discover -s experiments/collective005 -p 'test_*.py' -v

    python experiments/collective005/atlas_trial.py \
      --atlas-root external/motif-legit022 \
      --case-root external/nt-cases \
      --box-root external/nt-question-box \
      > collective005-primitive-birth-evidence.json

GitHub Actions publishes all source, query, mathematical and refusal receipts.

## Next hard falsifier

Test the frozen question-growth engine on genuinely different graph families
where path counting cannot help, and on a mathematically unrelated task
domain. Allow a meta-language to propose different generic binder, predicate
and reduction patterns under hard budgets. Use independently authored
challenge tasks and equal-information classical baselines. Count HOLDs,
failures and costly unproductive search alongside successes.
