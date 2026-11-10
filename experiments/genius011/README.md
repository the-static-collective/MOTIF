# MOTIF-GENIUS-011 — THE UNSUSPECTED RELATION

**Status: RESEARCH HOLD.** This is executable experimental software stacked on unmerged GENIUS-010. No change to main, Trench, MCP, JAR;VIS, external sources or the physical world.

## Question

GENIUS-010 selected from three *engineer-named* candidate explanations. This trial asks whether MOTIF can instead **construct a previously unnamed relational hypothesis from three independent accounts**, compose its next falsifiable question, test it against separate prospective evidence, and retain any source disagreements without pretending that recurring words establish causation.

The creative inspiration is Povenmire's parallel storylines converging, Acaster's later callbacks changing earlier interpretation, Nolan's difference between event order and disclosure order, and Bacon/Aquinas's insistence on evidentiary objections. These analogies are NOT evidence of psychological or artistic qualities.

## Classical prior art

- Yan & Han, *gSpan: Graph-Based Substructure Pattern Mining*, ICDM 2002, DOI https://doi.org/10.1109/ICDM.2002.1184038. Frequent-graph substructure mining and canonicalization are established. This experiment does **not** implement gSpan, which is much more scalable.
- The Center for Open Science, https://www.cos.io/initiatives/prereg-more-information, and discussion of exploratory versus confirmatory analyses, https://pmc.ncbi.nlm.nih.gov/articles/PMC6706998/. Hypothesis generation on one dataset must be separated from later testing; selection affects statistical error guarantees.
- Classical Fisher exact contingency tests and Bonferroni correction, used here to compare two simulated intervention arms per thread. They do not certify a real underlying mechanism, validate randomization, or authenticate experimental custody.
- Prior MOTIF GENIUS-009/010: immutable source-owner records, later interpretations and refusal of repeated evidence. We **actually import** these modules.

## Step 1: Generate candidate relationships from unfamiliar source graphs

Three independent synthetic strands are named glasshouse, broadcast and parcel. Each has locally named vertices, signed directed graph edges, explicit evidence IDs, a source-origin root, and repeated misleading surface words. The algorithm receives NO hypothesis-name menu.

It enumerates *every connected two-edge signed directed subgraph*, computes the minimum canonical serialization across vertex-name permutations, and intersects the three graph motif sets. If the same abstract pattern occurs in all three independent strands, it creates a **new candidate expression** consisting of:

- Its canonical directed and sign-sensitive graph structure (not a memorized label).
- Exactly which two public source edges support it in each of the three strands.
- A generated question: Would intervening on this motif increase independently measured success in all three contexts?
- A SHA-256 premeasurement commitment to that question and its source witnesses.

The hidden operative motif varies by synthetic seed and is NOT an input to the question generator.

**This is combinatorial synthesis within an existing grammar, not free-form invention of a causal theory or physical instrument.** The test uses a hypothetical intervention provided by the simulator. If no shared graph motif exists, or if independent source origins cannot be asserted, return HOLD before measuring.

## Step 2: Separate question invention from confirmation

The candidate set is committed BEFORE the simulator generates the synthetic outcomes. Each candidate is tested independently in each strand using 40 Bernoulli observations per arm, with fixed outcome-independent withholding. Only explicitly public outcomes can be scored or transported.

The predeclared family-wise significance threshold is **0.05 divided by (24 possible pattern tests × 3 strands)**; each positive strand must also show an observed risk difference >=0.25. Three of three distinct-source positive contrasts are necessary. If **multiple different candidates** survive, HOLD rather than select the most attractive story.

Distinct public trial IDs and origin roots are required; repeated IDs are not independent witnesses. The simulated randomization attestation is merely a fixture field. The family-wise guarantee applies only if the test assumptions and predeclared family really hold; it is not a guarantee about observational or real-world cases.

After one conditional bridge passes, GENIUS-010 and GENIUS-009 append a **later source-owned interpretation** connecting three independent earlier observations. Original statements do NOT change. The source and test evidence include hashes/receipts; these are not cryptographically signed real-world custody proofs.

## Nine adversarial scenario families

| Family | Hidden engineered challenge | Intended evidentiary disposition |
| --- | --- | --- |
| TRUE | One of two structurally synthesized relationships matters in all three contexts | Test and retain only the supported generated hypothesis. |
| TRUE_RENAMED | The actual relational mechanism persists under unfamiliar variable labels | Track structure, not vocabulary. |
| NULL | Shared motifs exist but cause no simulated test-outcome change | HOLD instead of forcing a bridge. |
| CONFOUNDED | A familiar structural pattern is not an intervention effect | HOLD; extra posthoc observational control below. |
| PARTIAL | Only two strands support the effect | HOLD and retain third-strand dissent. |
| OPPOSED | A candidate helps two strands and harms one | HOLD uniform explanation. |
| ECHO_ROOT | Three apparent sources disclose the same origin root | HOLD pseudoindependent evidence. |
| RIVAL | Two distinct candidate patterns both show simulated effects | HOLD unresolved competing explanations. |
| NO_SHARED | The source graphs share no two-edge pattern | HOLD without inventing one. |

The first benchmark uses two diagnostic validation seeds and six separate heldout synthetic seeds per regime. The study design SHA-256 is computed before future outcomes are generated; all cases still come from **one engineer-authored simulator** and are not independent blind tasks.

### Extra observational confounding check (explicitly POSTHOC)

After inspecting the first 54 test cases, a separate control was added. A latent Z affects an observational exposure and an outcome, producing large correlations even though the exposure itself does not cause the outcome. Such evidence is tagged OBSERVATIONAL_NOT_RANDOMIZED and cannot be passed to the randomized-intervention gate: it yields **HOLD_OBSERVATIONAL_DATA_NOT_AN_INTERVENTION**. The added test is an engineering correction, NOT a new blinded result. It is archived separately.

## Strong controls and honesty

**Weak lexical control:** chooses the identical recurring surface phrase; this is deliberately bad, not a state-of-the-art learner.

**Strong classical control:** exact canonical subgraph enumeration plus exactly the same source-aware Fisher/Bonferroni tests given the same inputs would return the **same hypotheses and judgments**. This prototype combines established techniques into an auditable pipeline; it does NOT outperform modern graph-mining, causal inference, or mathematical discovery methods.

**Hard limit:** only directed signed **two-edge** relations and simulated binary outcomes can be represented. Important nonlocal structures, time/causal dependencies, source collusion, invalid sampling and genuine physical experiment design remain unaddressed. Source-root distinctions are asserted by synthetic IDs, not proven by real external custodians. No general language invention or historically novel mathematics demonstrated.

## Reproduce

From a checkout of this branch:

    python -m unittest discover -s experiments/genius011 -p 'test_*.py' -v
    python experiments/genius011/benchmark.py > /tmp/motif-genius011.json
    python experiments/genius011/controls.py > /tmp/motif-genius011-posthoc-confounding.json

CI archives the original synthetic event and evidence packets separately from the later posthoc survey.

## Next independent falsifier

An outside author supplies three unfamiliar *source-owned real graphs* without disclosing a target connection. MOTIF should propose testable relations, respecting source custody, under explicit compute and information budgets. A separate independent evaluator should run ethically authorized prospective tests and compare with a well-tuned established graph miner and causal-discovery planner given the SAME tools and evidence. Any success must be measured in externally verified discoveries, not matching our own synthetic mechanism generator.

**Rule: a structural resemblance is a question. A surviving conditional intervention effect is evidence. Neither is a license to rewrite the old witnesses.**
