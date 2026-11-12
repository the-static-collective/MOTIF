# LLM-004B — Post-hoc strong stopped-information-gain control (frozen before code)
2026-11-12. This addendum follows observation that the Bayes decision-gain arm has a lower average probe cost under 3-step budget than classical IG forced to spend all three attempts. It is explicitly POSTHOC; original primary comparison remains unchanged.

New classical control: choose the maximum Shannon expected information-gain query, but make the SAME rational stopping decision as the decision-gain policy: if its maximum expected Bayes-majority accuracy improvement over all eight binary targets is not greater than 0.04 cost, do not probe. Call it classical_ig_stop. The scoring owner and noise assumptions are unchanged. Compare accuracy, average actual probe count and net accuracy-cost over the original exact 160 heldout synthetic owner seeds, each of 4 regimes and 0..3 query budgets.

Falsifier: if classical_ig_stop ties decision_gain, the previously observed net gain is attributable to stopping rather than new query selection. If another baseline wins, report it. This is not an independently held-out new benchmark, not new mathematics, and cannot support production reliability.
