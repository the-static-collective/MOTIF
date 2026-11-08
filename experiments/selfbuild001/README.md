# SELF-BUILD-001 — MOTIF asks: *How can I make myself?*

**Experimental, local, inspectable, permission-bounded.** This is a first executable answer to the self-construction question. It is **not** unrestricted recursive self-programming or proof of independent new algorithm invention.

## The actual question → action loop

1. **Orient from evidence.** Parse five checked-out source modules using Python AST. Record their SHA-256s, names observed, absent interface declarations, and key things that remain unknown. A symbol existing is **not evidence of working integration**.
2. **Ask a next question:** “Can I construct a bounded child that asks and acts on its own next question?”
3. **Do the next thing:** emit `motif_seed.py` and a separate `test_motif_seed.py` into a *new local staging directory*, using reviewed fixed templates. Interpolations are encoded data, not arbitrary executable prompts.
4. **Independently check:** verify exact source/test bytes, then execute the child and its four contract tests in fresh Python processes with timeouts. Python `-I` is only interpreter isolation, **not** a security sandbox.
5. **Return result and ask forward:** name exactly what passed and what remains unjustified; next inquiry asks whether genuine cartridge composition and independently measured integrations can replace the template.

The generated child is a tiny working research cartridge: given an interface inventory, it orients which names it knows and lacks, asks its own next relevant question, and **executes the fixed count operation**, returning a receipt-like result. This is a **template instance**. It neither writes its own source nor authenticates upstream modules.

## Scope of the inventory

MOTIF-003 `analyze_first_moves` / `witness_gap`; FIR-001 `FIRWorld` / `Claim`; MATHAL-001 `execute` / `compose_runs`; WITNESS-CHAIN-001 `State` / `propose`; NEXT-STEP-001 `orient` / `advance`.

The experiment is stacked on `experiment/next-step-001-20261107`, which itself depends on other unmerged research branches. There is no change to `main` or an automatic GitHub push by the child. Source checksums detect source changes; they do not authenticate who wrote the code.

## Reproduce

Python >= 3.10; stdlib only:

```bash
cd experiments/selfbuild001
python -m unittest -v test_selfbuild.py
python benchmark.py
python selfbuild.py
```

- The test suite includes tampered code, missing symbols, unparseable code, symlinks, stale source, spent budgets, and external-action claims.
- A checkout of the stacked repository additionally checks against actual upstream modules; isolated local fixtures skip that integration test.
- `benchmark.py` uses **four deliberately simple synthetic interface-list examples** and a weak constant-question baseline. It cannot demonstrate general reasoning ability or novel algorithms.

## Constraints and future questions

The answer to “Can MOTIF make itself?” is **partially, in a bounded template-instantiation sense**. It has a source-informed orientation, a finite question/action loop, and a verified tiny child. It has *not* synthesized new code structures, constructed the full agent architecture, discovered the actual best design, or deployed itself.

The next meaningful experiment is **SELF-BUILD-002: replace template-only inventory with actual interface contracts**, composition tests that use live executable MOTIF cartridges, differential tests against older controls, a constrained generator proposing multiple variations, and immutable review gates. Only authorized callers should promote a reviewed candidate to a repository branch or service.
