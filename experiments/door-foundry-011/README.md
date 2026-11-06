# MOTIF-011 — THE EVIDENCE FRONTIER: SOURCE ROOTS, NOT ECHOES

**One incorrect report repeated seven times is not seven independent observations.**

This source-native, executable experiment extends [MOTIF-010 #92](https://github.com/the-static-collective/MOTIF/pull/92): MOTIF maintains an append-only graph of synthetic report dependencies, uses exactly **one likelihood factor per declared original source root**, retains every relay and conflict, and reruns downstream Bayesian beliefs, possible next questions and decisions. An entirely separate [CANNON-096](https://github.com/the-static-collective/CANNON/pull/96) reviewer independently recomputes report parentage, content provenance, original binary PNG source digests, and **exact rational Bayesian posteriors in JavaScript**, never importing the MOTIF application code into its Bayesian arithmetic.

### Experiment — fully synthetic, not actual witnesses

MOTIF-009 first creates four separate real binary PNG candidate worlds (crate left/right × wall partial/full). It asserts **none is observed**. The earlier GRAFT-030 visual executable remains source-pinned; CANNON-095 verified that generated code, not real-world image authenticity.

For each deliberately chosen synthetic truth, ten report receipts arrive:

- **R001:** one original simulated sensor reports the **wrong wall extent**, assigned an explicitly hypothetical **80%** conditional accuracy.
- **R002–R007:** six retransmissions referencing earlier reports **in the same source origin A**, reproducing the same incorrect assertion. These are distinct report receipts but zero additional independent likelihood factors.
- **R008–R010:** three **differently declared** simulated source roots B, C, D report the correct wall extent. Their independently assumed 80% accuracy is a test assumption, not a measured or authenticated fact.

Crucially, original report A and the contradictory B/C/D reports all remain visible in an append-only content-hash chain. The probabilistic update **does not delete the inconvenient first report**. Even a duplicate copy stays recorded but does not multiply the likelihood.

### What it actually calculates

- **Source-aware Bayesian reference:** one likelihood per declared source origin, resulting from four root events only.
- **Invalid naive report-counting control:** ten likelihood factors, improperly treating all seven copies of the wrong rumor as independent.
- **Independent direct classical check:** MOTIF-010 likelihood-product batch Bayes agrees exactly with every source-aware update.
- **Independent CANNON-096 check:** source-pinned MOTIF original bytes, actual PNG source evidence, every parent/child report, original sensor record, conflict ledger, append-only hash chain and every exact rational posterior recomputed by independent JavaScript.

The experiment runs for **all four synthetic truth fixtures**, scoring the probability of the held truth's **wall extent** and its implied simulated action. These are **designed rumor-attack fixtures** with one bad root and three good roots; the comparison is not representative of real news, conversations, or independent people.

| Metric (lower better) | Source-root grouped model | Invalid naive copied-report baseline |
|---|---:|---:|
| Mean simulated Brier score | **0.020118** | 0.983759 |
| Mean simulated decision regret | **1.0** | 3.5 |
| Different claimed source roots | 4 | 4 |
| Reports actually present | 10 | 10 |
| Additional *independent* information contributed by six explicit copies | **0** | Incorrectly counts six |

The grouped model produces less overconfidence **in these constructed examples**. This does NOT prove superiority to conventional source-collapsed Bayesian reasoning (which matches), independence discovery, statistical calibration, or performance on real-world misinformation.

### Important epistemic failure boundary

**CANNON checks whether reports *declare* a shared source and whether those declarations form a valid graph. It does NOT verify that root IDs refer to separate actual witnesses.** Four sockpuppet accounts could falsely claim four independent roots, and a structurally consistent hash chain cannot discover that from the metadata alone.

Furthermore, 80% accuracy, conditional independence of declared roots, original priors, true-world labels and outcome penalties are all simulated assumptions. Source SHA-256 verifies bytes, **not truth or independence**. The original CANNON receipt verifies generated visual operator source; CANNON-096 produces an **unsigned HOLD**, never a production endorsement. No real people were contacted, no measurements acquired, no human reply asserted, no external service called, and no action or merge automatically performed.

### Architecture

```text
MOTIF-007 text ambiguity
      ↓
MOTIF-006 original PNG worlds + source-checked GRAFT-030
      ↓
MOTIF-009 question tree (all four worlds remain hypothetical)
      ↓
MOTIF-010 exact Bayesian belief ledger
      ↓
MOTIF-011 declared provenance DAG
      ├─ A original wrong report
      │   └─ copied → copied → copied → copied → copied → copied
      ├─ B independent *by fixture*, contradicts A
      ├─ C independent *by fixture*, agrees with B
      └─ D independent *by fixture*, agrees with B/C
      ↓
Root-only Bayesian posterior vs intentionally wrong all-copy posterior
      ↓
New unsent question / possible decision — no physical action
      ↓
Independent CANNON-096 JavaScript BigInt rational evidence reviewer
      ↓
HOLD (dependence structure checked; source independence unverified)
```

### Source and reproducibility

- `experiments/door-foundry-011/source_graph.py`: strictly typed report receipts, same-origin dependency chains, exact rational posterior, preserved disagreement and belief/question recalculation, four-case controlled benchmark.
- `experiments/door-foundry-011/test_source_graph.py`: **25 native adversarial tests** of duplicate sources, unverified authority, altered copy claims, orphan/cross-source edges, altered source PNGs, contradiction preservation, Bayesian equivalence and predicted regret.
- `experiments/door-foundry-011/README.md` (this dossier).
- `.github/workflows/door-foundry-011.yml`: immutable original GRAFT/CANNON/MOTIF source checkouts, GRAFT owner tests, original MOTIF-010 controls (**23** tests), MOTIF-011 tests (**25**), and **independent CANNON-096** source-byte, Bayesian math and full-content check with an evidence artifact.

The CANNON-096 reviewer itself has a separate successful hosted GitHub Actions workflow and its own malicious-data tests. It checks original MOTIF-011 at immutable `c41ff828e167a406fab25ef2b0a272be5e736ad2` and independently inspects actual original MOTIF-009 binary PNG files.

Run the dedicated workflow, or once its original source checkouts and earlier image/active-question receipts are present:

```sh
python experiments/door-foundry-011/source_graph.py \
  --question-dir evidence/original-active-question \
  --out evidence/source-dependence

node cannon096-source/experiments/cannon-096/review.mjs \
  --motif motif011-source \
  --question evidence/original-active-question \
  --ledger evidence/source-dependence \
  --out evidence/cannon-096-independent-evidence-review.json
```

**Next falsifiable frontier:** use actual *user-permitted* source attestations and provenance discovery (not self-declared identities), evaluate hidden common upstream sources and correlated sensor errors, calibrate reliability on prospective unseen data, and test recovery when the real scene lies outside the four hypotheses. **Proof of a valid attribution graph is not proof that the attributions are true.**
