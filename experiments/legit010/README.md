# MOTIF-LEGIT-010 — THE SELF-BOOTSTRAP

**Research status:** experimental branch, separate draft PR, RESEARCH HOLD.
**Question:** Can the current MOTIF code literally **run itself to produce
the next reasoning program**, then reuse that generated program to produce
a third generation, with checkable mathematical semantics?

**Answer: YES, in a restricted typed Boolean program language.** Not
unrestricted Python self-editing, new mathematical axioms, or agent autonomy.

## The actual executed three-generation experiment

This invokes the **unmodified LEGIT-009 synthesizer**. The previous
generator is not reconstructed from scratch or simulated. We import
\`experiments/legit009/synthesizer.py::cegis\` and
\`load_verified\` and execute them to create the original library.

**Level 0 — Existing MOTIF writes its own building blocks.**
LEGIT-009's real CEGIS program produces 16 minimum-NAND programs
covering every binary Boolean truth function. Each is checked against a
separately written two-input Boolean interpreter and a full four-case oracle.

**Level 1 — The generator writes a successor *search algorithm*.**
The new meta-CEGIS engine combines pairs of these *generated* programs in
two binary-tree shapes and six input orders. It discovers 3,072 possible
two-operation constructions, which implement **152 distinct three-input
Boolean truth functions**.

It begins by trying to distinguish different candidate behaviors using
one observed input. If two programs have identical observed behavior but
different complete Boolean behavior, a verifier supplies an explicit
counterexample. The method adds that input and tries again. After **seven
genuine meta-counterexamples**, it learns the necessary **eight-input
signature** and proves the selected index separates every distinct
function expressible in this grammar.

The generated portable
\`motif.self-composed-search-program.v1\` then uses those signatures to
retain the cheapest executable representative of each of the 152
equivalence classes, instead of keeping 3,072 redundant constructions.

This **95.05% reduction in stored candidate count** is an optimization of
the search *representation*, **not** a proof that the overall generator
is faster in wall-clock time. Discovering the index and enumerating the
original catalog also costs computation. Finding all eight input rows is
an honest negative result for a smaller discriminating signature.

**Level 2 — Execute the self-written search program to invent new programs.**
The new strategy actually runs CEGIS against independently coded
**eight-case** three-variable verifiers. The target semantics do not
appear as source code in the learner; only the separate oracle can
provide counterexamples.

| Novel 3-input task | Minimum generated NANDs in this composition grammar |
|---|---:|
| Odd parity of three inputs | **8** |
| All three inputs are true | **4** |
| At least one is true | **6** |
| All three inputs are false | **7** |
| First two agree AND third is true | **7** |
| First two disagree AND third is true | **6** |

The separate exact classical composer tries **all 3,072 arrangements**
using its own evaluator and finds the **same** least NAND count for each.
The candidate does not beat that optimized classical solution.

The constrained grammar also **correctly HOLDs** on three-input
MAJORITY: it cannot be expressed with only two binary operations in the
restricted tree structure. This is not a claim that majority is
mathematically impossible or that classical logic cannot compute it.

A separate flat primitive-only NAND search with a **five-gate limit**
evaluated **549,069 terminal circuits** and found no circuit for 3-input
odd parity. The generated eight-gate composed program solves it. That
demonstrates a **larger reachable problem** via certified subroutine
composition within two very different fixed budgets—not superiority
over an unrestricted classical synthesizer or a proof that eight gates
is globally optimal for the raw three-input NAND language.

**Level 3 — Reuse the newly generated three-input method to write a
four-input method.** The system takes the just-generated parity3 circuit,
attaches a separately LEGIT-009-generated binary XOR circuit, writes a
**12-NAND four-input parity program**, and proves it on all **16** input
combinations with a separate Boolean interpreter.

The parent program hashes and the newly written instructions are
preserved in the next-generation cartridge. Every generated algorithm
must pass mathematical re-verification before its **typed data**
instructions are executed.

The methods are stored as **readable, machine-executable JSON**, not
Python source code that would be loaded with \`eval\` or admitted to the
production tree. Both the generated candidate search algorithm and the
three- and four-variable instructions are now **committed for review** at

\`experiments/legit010/generated/self_written_algorithms.json\`.

That committed artifact was taken directly from the successful GitHub
Actions run and tests compare it against a **fresh execution** of the
original LEGIT-009 engine. No autonomous GitHub write permissions were
given to the generated programs.

## Integration with MOTIF's real earlier code

The generated three-input method reads the actual existing
LEGIT-007 synthetic witness provenance graphs. It checks a *narrow,
declared Boolean diagnostic*: odd parity among the first three
distinct declared source-root claims.

All **320** previous witness graphs were considered, with **160** having
at least three source roots. The generated output matches the
direct Boolean reference without changing the existing witness
model, posterior, source identity assumptions or external state.

This doesn't measure witness credibility or authenticate source roots.
It's a crosswire demonstrating the **generated method really executes**
inside an earlier system.

## Why it counts as "using itself"

There are now three distinct, executable program levels:

1. A **handwritten previous-generation algorithm generator** that
   outputs binary NAND programs.
2. A **second-generation generated search algorithm**, built using those
   self-generated programs and updated from counterexamples, that outputs
   independently checked three-variable programs.
3. A **third-generation program**, generated by composing an actual
   second-generation program with another original generated program.

The output of one generation becomes an **executable building block**
for the next. The important novelty within the project is the
*implemented self-reuse and proof-gated feedback loop*.

What is **NOT** true: the whole algorithm generator was autonomously
invented, its Python code was automatically rewritten, or the
instructions escaped the typed interpreter. The meta-CEGIS grammar,
composition machinery, equality-class concept, and verification
contracts were programmed by the assistant.

## Verification and limitations

- **28 initial adversarial unit tests passed**, expanded to **30** after
  adding committed-artifact replay and re-verification tests.
- All 16 old binary programs, 6 new three-input programs, and 1 new
  four-input program are separately rechecked.
- Tampered programs, forged rehashed incomplete search policies, mutated
  parents, invalid source wiring, and wrong specification identities
  fail closed.
- A strong **classical exhaustive composition** comparator ties, rather
  than losing artificially.
- Program-source checksums prove internal content integrity, **not**
  real signatures or source ownership.
- All source semantics and targets were generated by this assistant,
  not supplied by an independent research institution. No hidden
  third-party SyGuS challenge is claimed.
- The experiment did not compute actual CPU, elapsed-time or energy
  superiority; a 95.05% candidate-index reduction is not a 95.05%
  runtime reduction.
- Native XOR/AND/OR machine operations can be more efficient than NAND
  networks. The NAND gate counts are meaningful only for that declared
  low-level instruction model.
- Generated programs remain **DRAFT / RESEARCH HOLD**. No unrestricted
  code synthesis, auto-promotion to main, external action dispatch,
  self-modification of server code or human decision authority.

### Repeat the actual self-bootstrap

From repository root, Python 3.11 standard library only:

\`\`\`bash
python -m unittest discover -s experiments/legit010 -p 'test_*.py' -v
python experiments/legit010/benchmark.py --emit
\`\`\`

The second command writes a portable generated algorithm artifact
to \`/tmp/motif-legit010-self-generated-algorithms.json\`. The CI run
archives it alongside the exact counterexample transcripts and
independent source-verification results.

## Where to go next

The next rigorous experiment is **self-generated solver transformation**,
rather than just *self-generated solver inputs*: synthesize a candidate
source-code transformation in a constrained typed DSL (e.g., factor
shared subexpressions, safely prune dominated branches, cache proven
subproblems), use a SAT/SMT or proof-assistant verifier to show it is
semantics-preserving, then ask it to transform its own synthesizer under
a fixed instruction budget.

Compare to a **fully tuned classical synthesis+superoptimization portfolio**
on an independently authored sealed test set, with real compute timing.
Any unverified generated transformation must remain inert.

**The correct goal is better verified algorithms per unit of resource,
not exemption from mathematical proof.**
