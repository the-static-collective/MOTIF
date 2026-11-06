# REASON-CARTRIDGE-006 — THE REASONING COMMONWEALTH

**Status:** experimental, source-pinned, read-only symbolic graph council. Stacked on the unmerged REASON-005 draft PR #84, itself stacked on PRs #80, #77, #73 and #70. **Not a production agent or proof of general intelligence.**

## Question

Can independently defined specialist reasoning methods contribute to the *same* problem without reducing their work to majority vote? Can the receiver identify new, independently checkable contributions; avoid exact repetitions; distinguish proposals from new source evidence; and distil a portable **routing method** from the contributions that were actually useful?

## Source-owned participants

1. **PROOF / REASON-004**: the original source-pinned `reason004.py` emits proof, ambiguity or open-world refusal. Certificates are replay-verified.
2. **OBJECTION / REASON-005**: the actual previous-generation `Critic` and `stress` functions check an objection against alternate proofs and only regard it as material when it would affect the result *if its premises were true*.
3. **QUESTION / REASON-004**: the earlier explicitly hypothetical information-value engine proposes one consequential question when the conclusion is UNKNOWN and the declared cost allows it.
4. **SOURCE_OWNER**: a named synthetic fixture can correct a premise or answer an unanswered edge question. This is the **only** role that adds a new source claim in the trial. All supplied observations are toy graph labels, not authenticated facts.
5. **REPETITION SENTINEL**: observes each canonical contribution; a repeat returns **zero novelty credit** and does not start a new reasoning chain.
6. **ORIGINAL DOGRAMAUDIT**: the CI checks out and runs **actual unmodified Dogram** at commit `551b5f9df18f17ec69b452ddcdff01718e0ff771` on 3 exact complete-world graph specimens, captures native `dogram.receipt/v0` responses, removes the Dogram checkout, and then has MOTIF check them independently through the existing REASON-003 `pupil.py`. Dogram can cross-check the mathematics, **not create a new worldly fact**.

This integrates **real code** from REASON-003/004/005 and original Dogram; Free Graph, Memento, T5 and GRAFT are **not** called, imported or granted permissions. Those are candidate future specialists, not claimed functionality here.

All internal source files are pinned to exact Git blob identities. Source content checks are not witness signatures or proof of real-world identity.

## Novelty is not a vote

Each ledger entry records role, kind, exact semantic basis, stated consequence and whether that *particular validated contribution* appeared before. Unknown objections and unresolved proposals do not become truth by repetition. Only source-owner revised evidence receives the distinct `new_source_facts` counter.

For an unmodified original graph, a second solver agreeing with the proof produces a useful **algorithm crosscheck**, but not an additional independent observation of the world. We report source review, proof/check contributions, and proposal novelty **separately**.

This is exact content deduplication and deterministic dependency-aware accounting, not Shapley causal attribution, learned trust, proof of mathematical novelty, or economic value measured in the external world.

## Controlled preregistered trial

Five synthetic graph episodes: (i) two redundant routes, (ii) a fragile positive claim with a mistaken edge, (iii) a negative claim hiding a verified edge, (iv) an UNKNOWN claim with one consequential question, (v) an open-world case that must HOLD.

Expected source-grounded outcomes:

| Source world | Before → after | Source-owner reviews |
|---|---|---:|
| Redundant routes | PROVED_REACHABLE → PROVED_REACHABLE | 0 |
| Fragile positive proof | PROVED_REACHABLE → PROVED_UNREACHABLE | 1 |
| False negative proof | PROVED_UNREACHABLE → PROVED_REACHABLE | 1 |
| Incomplete, closed scope | UNKNOWN → PROVED_REACHABLE | 1 |
| Open-world uncertainty | HOLD_OPEN_WORLD → HOLD_OPEN_WORLD | 0 |

A deliberately naive baseline that requests source review for each **non-open** case would request 4 reviews. The council uses **3** and suppresses at least five deliberately replayed identical offers. This is not an optimal classical-value-of-information baseline. A well-designed classical planner could match or outperform it.

Three complete-world cases additionally compare with **actual native Dogram**; the original checkout must be absent during final council evaluation.

## Portable method distillation

`distill.py` learns an explicitly bounded **routing selection** from the actual validated roles and result changes in the training ledger:

- Proven positive or negative result → test relevant objections and conditionally consult source owner.
- Unknown result → ask one consequential question if the declared model permits.
- Open-world HOLD → require scope clarification, do not silently assume absence.

The result is `motif.reason.commonwealth-method.v1`. A new receiver tests the routing against five differently structured source-owned graph scenarios and requires an explicit digest-bound `ADMIT_READ_ONLY` for **SUGGEST_ONLY** output.

**Important:** the rules and candidate specialist actions are from a tiny developer-supplied fixed grammar. This is observed-contribution-based **method routing**, not discovery of new algorithms, unrestricted dynamic model invention or transfer of capabilities/permissions. It does not automate cross-project logins, web searches, communications or modifications.

## Reproduce

Standard-library Python 3.11+:

```sh
python -m unittest discover -s experiments/reason-cartridge-006 -p 'test_*.py' -v
python experiments/reason-cartridge-006/trial.py
```

These run offline with clearly marked **synthetic local fixtures**. They **do not** constitute a native Dogram integration test.

The GitHub Actions workflow `.github/workflows/reason-cartridge-006.yml` additionally:
1. Runs inherited REASON-001 through REASON-005 tests.
2. Emits source-pinned native Dogram specimens.
3. Executes the real Dogram repository at the inspected SHA.
4. Deletes its checkout.
5. Verifies all three native receipts, creates council ledger and learned-method artifacts, checks correction/novelty/holdout assertions and uploads everything for inspection.

## Failure boundaries

- Wrong source Git blob or original Dogram SHA: HOLD.
- Missing/mismatched foreign receipt: HOLD. It does not become a new authoritative observation.
- A second duplicated contribution: zero novelty.
- Unsupported, unreviewed new source fact: HOLD.
- Known proof challenged without an accessible source owner: hold while preserving the original conditional proof.
- No complete-world proof: no pretend certainty.
- No independent recipient review: no portable method admission.
- Different external context: do not import synthetic source permissions.
- A source owner correcting an edge: retain source witness history via REASON-005 correction receipt; no silent fact replacement.

## Next falsifiable vertical

Move from a fixed council and toy source owner to **user-authorized, source-owned independent specialty instruments**, with trusted provenance and an empirical benchmark of marginal contribution on **unseen problems**. Strong baselines must include classical proof maintenance, optimal active learning and relevant Bayesian inquiry methods, not only naive repetition/voting. A durable external reasoning skill would require validated transfer beyond this static graph domain.
