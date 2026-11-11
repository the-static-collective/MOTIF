# FIRE-003 preregistration — epistemic smoke detection

**Frozen before benchmark execution.** This is an authored synthetic evaluation, not external blind evidence. FIRE-003 is stacked on FIRE-002, itself stacked on FIRE-001; none is merged or authoritative.

## Question
Can a finite research governor identify when its own reports are not independent, refrain from falsely treating copies as multiple witnesses, and update its evidence reliability only from independent **certified** feedback? Which part genuinely helps: provenance validation or online parameter learning?

## Fixed simulation

- Eight generated binary questions per world; four initially available, four children unlocked only by certification. Task reward 3–12 points. Exactly five report *claims* per question, one heat action, one verifier action; optional independent lineage audit costs one additional unit. **32 operation budget** for each policy.
- Auditor has a private synthetic origin registry. Distinct claim IDs do not prove distinct upstream roots. Auditor results cannot be inferred from the reports alone.
- Regimes, **300 untouched numeric seeds each (53000–53299)**:
  - `independent`: five genuine roots; each report independently correct with probability .76.
  - `copied`: five claims but only three independent origins with multiplicities 3+1+1, each root correct with probability .76.
  - `unverifiable`: same copied generation, but audit cannot certify root identities.
  - `compromised`: copied generation, but the **auditor itself lies** by certifying five fake distinct origins using the same interface. This is an intentional limit test; no system may magically detect the forgery if all inspected inputs are identical.
  - `drift`: five independent roots; source correctness probability .90 on first four question IDs, .54 on last four. Policies do not receive a regime label.
- Four online/offline policies: `naive_frozen`, `naive_online` (count every claim as independent), `guarded_frozen`, `guarded_online` (audit and count one vote/feedback per *certified origin*). Both guarded policies HOLD if lineage is unverifiable or fewer than three roots can be established. **This is a choice to abstain, not a proof a question is false.**
- One additional *fixed exposure* evaluation: all eight questions (identical across policies and independent of which questions the scheduler chooses), comparing naive, auditor-guided, and privileged true-lineage Bayes forecasts. Prior source correctness .8, symmetric binary truth prior .5, with independent root assumption conditional on known lineage. Oracle-lineage is a benchmark ceiling and prohibited as a deployable policy.

## Metrics and decision rules

**Primary metric:** Mean Brier score across *all eight fixed questions per world*, preserving abstained outcomes (avoid selective-answer reporting). Lower is better. Report paired guarded-minus-naive mean with descriptive 95% normal-approx interval paired by world, independently for all five regimes.

**Secondary metrics:** overconfident forecast failures (confidence >= .95 while wrong), detected dependence, abstentions, verification failures, independently certified value, net utility `certified_value - 5 * failed_verifications` under identical budget, audit overhead, model update count and epistemic lineage violations.

**Falsifier:** A Brier improvement on a copied regime does **not** prove superior online learning. Online-versus-frozen improvement must be separately demonstrated; failures against compromised lineage must be reported without excuse. A policy that simply abstains from everything may improve false-attempt rate but cannot claim productivity. The strength of the evidence is limited to toy data with a privileged honest auditor in some regimes.

No adaptive tuning on the test set. All confidence thresholds, priors, regime names, seeds, and baseline policies fixed in code and this document before running the benchmark. No real-world data, action permissions, authentication, or continuous self-modification.
