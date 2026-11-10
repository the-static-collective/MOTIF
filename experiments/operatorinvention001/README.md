# OPERATOR-INVENTION-001 — From needing a missing operation to writing executable code

**Status:** finite, local, synthetic program-synthesis research. Draft stacked on `experiment/language-growth-001-20261109`. No mainline merge, general mathematics discovery, autonomous program modification, or real-world action.

## The question MOTIF asked

> I can describe a missing counting operation, but I do not have its implementation. Can I construct an executable algorithm from elementary computational steps, test it against unseen problems, and refuse a proposed program when the evidence fails?

## What was *not* handed to the synthesizer

The candidate set contains **no ready-made four-cycle counter, path-three counter, or COUNT_XY implementation**. It is generated from a limited, supplied *control-flow grammar*:

- `FOR x IN vertices`, optional `FOR y IN vertices`;
- conjunction of 1–3 undirected edge predicates `E(u,v)` with variables chosen from a,b,x,y;
- optional distinctness guard;
- `count += 1`, return count.

The symbolic `Program` AST may be **interpreted** against graph states. Its `emit_source()` method additionally **constructs Python source** containing actual nested loops, conditionals and accumulator statements. Thus the compiled child is not merely an interpreter importing the previously authored counting operator. The compiler's syntax templates and primitive meaning are manually written, so this is *not* unrestricted source invention or automatic discovery of new looping principles.

## Evidence and search

The original 237-program feature language is run against the four-cycle-increment measurements and fails on a finite observed graph prefix. The new synthesizer enumerates 62 eligible loop programs. It selects synthetic graph interventions by disagreement among surviving candidate predictions, obtains the outcome only *after* choosing each intervention, and filters its version space. It requires at least three separate training interventions and does not use validation, test or OOD outcomes to choose the intervention sequence. After freezing a simplicity-preferred consistent program, it checks a separate validation split; any counterexample leads to `HOLD` instead of retuning. Undecidable equivalence on available inputs is not treated as global uniqueness.

The resulting program is equivalent to:

```python
count = 0
for x in vertices:
    for y in vertices:
        if edge(a, x) and edge(x, y) and edge(b, y):
            count += 1
return count
```

The exact generated program is included in the demonstration result. The source code is emitted by a typed compiler from the selected AST and executed in a separate interpreter with pinned upstream source bytes. A subprocess is **not a security sandbox**. It runs only a known local, trusted checkout. No external code, model-written shell command, network, payment or repo-write authority is supplied. Source hashes detect drift, not source authenticity; unpinned dependencies are possible.

## Evaluation (local)

Run in a full stacked checkout:

```bash
cd experiments/operatorinvention001
python -m unittest -v test_operatorinvention.py
python operatorinvention.py
python benchmark.py
```

Experiments use prewritten synthetic simple undirected graph fixtures from `LANGUAGE-GROWTH-001`, with disjoint split IDs and the same mathematical mechanism across all splits. The training oracle computes 4-cycle count differences; a separately implemented graph-neighbor algorithm is used as the strong classical baseline **only during evaluation**.

The experiment additionally asks the same code synthesizer to rediscover **triangle-increment code**, exercising a one-loop alternative without changing the primitive AST grammar. It uses the earlier MOTIF graph code rather than a new independent physical or external source.

### Controls

- Compare with the pre-existing handwritten path-three counter (strong baseline).
- Remove the two-loop primitive; synthesis should HOLD on four-cycle task.
- Corrupt the validation oracle; refusal, no silent update.
- Show too few training interventions cannot license a new operator.
- Cross-check emitted code with the AST interpreter on held-out and OOD inputs.
- Verify actual child execution with a separate Python process; replay its prediction against a hand-written baseline.
- Reject malformed ASTs, invalid budgets and leaked splits, bad indices, symlinks, source drift, child edits and unauthorized overwrite.
- Perform vertex-renaming metamorphic invariance check.

Any success here is inside a **small human-chosen search grammar**. The experiment doesn't establish novel computer science, historically new mathematical facts, independent causal verification, or production readiness. Its benchmark will explicitly report if random selection performs as well as active selection.

## Next question

> Can MOTIF *construct a new control-flow pattern*, rather than choosing between one and two predeclared loops? Can it infer the minimum necessary primitives from a failed synthesis trace and prove that an added primitive improves held-out task families more than it increases search cost?
