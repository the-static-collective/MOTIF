# MOTIF SELF-ASSEMBLY-001 — Wire real cartridges, do not merely name them

**Status:** bounded *local* experiment, child launcher generated and exercised in a subprocess, **no mainline merge, live agent, remote writes, arbitrary generated code, independent source authenticity, or general algorithm invention**.

## Question posed to MOTIF

> Which combination of my existing executable cartridges could solve a question that one cartridge alone cannot, and can I assemble it, execute it, test it, and retain a receipt?

`assembly.py` contains a finite, inspected registry of **actual functions** already present in the MOTIF repository. It uses a uniform-cost search over **typed input/output ports** to construct a plan from a declared user objective. It then pins the exact bytes of upstream source files. Execution dispatches only registered, locally read-only functions, checks limited output contracts, and returns a scoped answer and question to investigate next. `create_child` writes a compact executable launcher with a pinned plan; the child imports **real original modules**, not a replacement mini-model.

## Two real compositions

**Affordance task:** `MOTIF-003.analyze_first_moves` → `MATHAL-001.nominate_motif003` → `SELF-MIRROR-001.preview_motif003` → scoped report. The exact same artificial graph state produces two different proposals when the declared goal is immediate improvement (`repair`) versus future options (`teach`). The former makes a simulated immediate gain; the latter creates more synthetic future choices. No operation happens in the physical world. The synthetic rewrite rules are supplied by this experiment; the existing MOTIF-003 affordance search itself is imported and executed unchanged.

**Witness task:** `WITNESS-CHAIN-001.fir_receipt` + `NEXT-STEP-001.orient` + `NEXT-STEP-001.advance` → joined report. Existing NEXT-STEP code actually runs three local inquiry operations (relative estimate, exhaustive symmetry check, inquiry design), still retaining ambiguity about absolute truth. The latest question asks what independent evidence would be needed next. No trusted reference is acquired.

Assembly planning **does not train** a model or invent arbitrary adapters. It routes two known data schemas through a **manually declared** small registry using classical shortest-path search. Choice of an immediate versus option-creating policy is based on the caller's explicit priority, not a discovered universal utility function.

## Execute

From a full MOTIF checkout on the branch containing stacked experiments:

```bash
cd experiments/assemblylab001
python -m unittest -v test_assembly.py
python assembly.py
python benchmark.py
```

`assembly.py` launches three generated children in separate temporary directories, executing them as Python subprocesses against pinned repository-owned upstream modules. No arbitrary input Python, shell, network, payment, remote action or auto-merge API is exposed to the generated child. The parent only writes into the caller-selected local staging directory; generated launchers depend on the original modules being present and unchanged. Untrusted Python files are not safe to run merely because they have hashes: this uses a **trusted repository checkout**, not a sandbox.

## Controls and limits

- 32 targeted unit tests include true module calls, separate interpreter execution, two goal-dependent module choices, JSON receipts, bad budgets, wrong port types, input contamination, tampered/linked/missing source files, invalid stage chain, unauthorized F (fact) promotion, truncated search, and mutation checks.
- The benchmark checks 12 synthetic fixtures in each of the two registered domains against a weak **fixed witness-only workflow**. Its coverage difference is not an ML performance comparison, zero-shot generalization, or evidence of a new algorithm.
- Runtime source SHA-256 pins detect *changes* to inventoried files. They do not authenticate GitHub authorship, handle unlisted Python transitive dependencies, verify every original module's semantics, or guarantee containment from malicious code.
- Port typing is explicitly manually declared and locally checked. It is not a general proof assistant and does not infer arbitrary conversions.
- All action outputs remain proposals, finite-model findings, or local receipt counts. No new independent data is manufactured. The assembly does **not** edit its own source, upgrade its registered tools, or deploy changes.

## Questions this experiment leaves open

1. Can MOTIF *discover* a missing adapter interface rather than receive it as a handwritten rule?
2. Can independent held-out tests distinguish a useful new composition from an overfit combination?
3. Can source + execution provenance be independently authenticated rather than merely hash-pinned?
4. Can an explicit human-approved connector adapter produce real task improvement without promoting a proposed claim into a fact?

The next appropriate step is **adapter proposal → isolated build → independently checked regression test → human review**. The current code does not pretend that this step is already implemented.

Stacked parent branch: `experiment/self-build-001-20261107`, which depends on the unmerged NEXT-STEP, witness, decoder, mathal and FIR branches.
