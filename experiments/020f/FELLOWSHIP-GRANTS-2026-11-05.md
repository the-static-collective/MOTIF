# MOTIF-020F Field Challenge: Fellowship × Grants (November 5, 2026)

**Run:** Exact MOTIF-020F `InsideOutBox` Python dynamic program in GitHub Actions `42033676965`, committed on branch `experiments/020f-planz-omission-20261105`. Targeted workflow **passed**, including 15 existing core tests and 7 new scenario regression tests. The full monorepo workflow is separate.

**Question:** Does the time-aware, omission-cost-sensitive planner independently endorse the assistant's November 5–December–January prioritization?

## Source discipline

- Nexus Greater Minnesota Community Wealth Building Cohort: **November 6, 2026 at 5:00 p.m. Central**. Official source: https://nexuscp.org/apply-now-greater-mn-community-wealth-building-cohort/ . Eligibility, participant team, and submission remain **UNCONFIRMED**.
- Riverside Fellowship: **December 4, 2026** is the user's confirmed gathering date. Host/venue authority and operational commitments remain partly unresolved. **November 12 and November 18 are assistant-suggested INTERNAL review targets**, not church deadlines.
- Mozilla Fellowship letter of intent: **December 17, 2026 at 11:59 p.m. Pacific**. Official source: https://www.mozillafoundation.org/en/what-we-do/grantmaking/fellowship/ .
- Reynolds Journalism Institute fellowship: **January 8, 2027** deadline. Official source: https://rjionline.org/about-rji-fellowships/ .
- Voqal application: user previously confirmed **SUBMITTED**. No immediate reapplication is modeled.

The real PlanZ attention snapshot `ATTENTION-2026-10-28-005` and its original native validator are source-pinned and read-only. The public PlanZ index has **no verified deadline, per-project utility, or execution authority**. For the non-hypothetical source-only reading, MOTIF returns `HOLD_NO_VERIFIED_INACTION_VALUATION`.

## Deliberately invented sensitivity scenarios

The model assigns **hypothetical value units**, not dollars, acceptance probabilities, people served, or measured impact. It has an explicitly fictional cap on the number of attention units available and assumes each question consumes one model time bucket; it does NOT perform a real outreach, application, or venue negotiation. The values are chosen to test the effect of shifting deadlines and available attention, not derived from historical outcomes.

Scenario | Suggested *review question* for Nov 5 | Optimal synthetic value | Myopic synthetic value | Modeled loss of one time bucket
--- | --- | ---: | ---: | ---:
Base (4 attention units) | Check Nexus team/eligibility | **25** | 21 | 4
Higher capacity (5 units) | Check Nexus team/eligibility | **28** | 22 | 6
Group **proven** nonviable (not merely unconfirmed) | WAIT now; Riverside host decision within assumed window | **21** | 21 | 0
Riverside host's *effective* decision window closes Nov 5 | **Riverside host decision**, not Nexus | **24** | 24 | 8
Both host and Nexus now urgent, but two simultaneous questions permitted | **Check both** | **28** | 24 | 12
Nexus inquiry low modeled value | WAIT now; later Riverside inquiry | **21** | 21 | 0
No defensible quantitative assumptions | **HOLD**, no numerical recommendation | 0 (no values supplied) | 0 | 0

All results are direct executions of the same finite-horizon `InsideOutBox` program with different *declared* inputs. Exact source and scenario code: `experiments/020f/fellowship_timeline.py`; falsifying tests: `experiments/020f/test_fellowship_timeline.py`.

### What agrees with the earlier advice

Under the explicit base assumptions MOTIF chooses **asking about the actual Nexus team and eligibility on Nov 5**, then (in model windows) venue authority by the internal Nov 12 checkpoint, staffing by internal Nov 18, and a Mozilla evidence outline by Dec 17. This does **not** mean submitting a false or group-less application: the question tests whether a genuine group can participate. The model is deliberately not a participant/owner communication system.

### Where MOTIF disagrees

If Riverside's last useful decision really closes today, and only one inquiry can be pursued, it chooses the **host question first** over Nexus. With capacity for two genuinely independent parallel questions, it selects both. If Nexus is actually impossible, there is no reason to pursue that option. And when no grounded utility or timing numbers are supplied, it simply **HOLDs** rather than inventing a grand numeric priority.

### What the experiment DOES NOT establish

- There is no externally observed benefit or validated probability; a plan cannot manufacture a deadline, consent or a partner's commitment. All scores are **artificial illustrative units**.
- A hypothetical four- or five-unit two-month attention budget does not estimate the user's actual schedule or effort; each modeled time bucket compresses days/weeks into one step.
- A smarter baseline with the same complete temporal model is classical dynamic programming and must tie. This is not proof of algorithmic superiority.
- The experiment does not yet model the value of **learning the team/host answer**, question duration uncertainty, genuine dependency ordering, field transport, or user economic constraints. Model results are **conditional rankings**, not operational instructions from a calibrated agent.

**Next honest empirical input:** Whether an actual Nexus learning group is willing and able to attend the cohort, and whether Pastor Lee/Paula can confirm rooms, authority and responsible operators before the Fellowship event. These are reversible requests for information. Their responses could update the assumptions. No outside party has been contacted by the model.
