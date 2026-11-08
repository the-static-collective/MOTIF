# QC-010 — THE TRACTION LOOP
## Work-as-done, bricolage, historical context and evidence-calibrated safety

**Status:** Research-only draft, stacked on QC-009 Street Sense. **No production modification, no ignition, construction, veterinary treatment, outreach or other physical action performed.** All code examples are synthetic and contain no personally identifying or private material.

## The problem: practical intelligence must meet reality

A person encounters real constraints, selects a tentative arrangement of available things, tries a proportionate probe, notices whether the arrangement physically works, revises their mental model, and improvises another path when necessary.

A purely rule-driven system may respond "this is not the prescribed way to do it" without asking *what, precisely, goes wrong under actual constraints*. A purely optimistic improvisation system may respond "someone survived it, therefore it's safe." Both fail to model reality.

**The right research question is: Which observations and limitations matter for whether this particular action can succeed without unacceptable consequences?**

This draft adds a generic typed *traction loop*:

```text
HUMAN NEED + REUSABLE MATERIALS + LOCAL ENVIRONMENT
              |
    FORM HYPOTHESIS / ANALOGY
              |
      EXPOSE PHYSICAL ASSUMPTIONS
              |
  ANALYZE HAZARD MECHANISMS + UNKNOWN FACTS
              |
  CHOOSE LOW-EXPOSURE / REVERSIBLE PROBE
              |
     OBSERVE SUCCESS / FAILURE / AMBIGUITY
              |
       RECORD A SOURCED WITNESS
              |
   UPDATE CONSTRUCTION / ACTION POSSIBILITIES
              |
   ESCALATE EXPOSURE ONLY AFTER SEPARATE REVIEW
```

**A successful observation confirms that a function occurred under witnessed conditions; it does not automatically prove long-term safety or causal understanding.**

## Anthropological evidence, not selective nostalgia

Anthropology has a precise existing concept for recomposing what is already at hand: **bricolage**. Claude Lévi-Strauss introduced the term in *The Savage Mind* (1962). Later research emphasizes its generative character under constraints. Useful references:

- [Jules Zhao Liu, *Improvisation, collective structure, and culture change: A theory of bricolage* (Anthropological Theory, 2024)](https://www.harvard-yenching.org/research/improvisation-collective-structure-and-culture-change-a-theory-of-bricolage/). Describes regulated improvisation under restricted circumstances.
- [*Bricolage: A Novel Archaeological Perspective on Complex Materialities*](https://doi.org/10.4000/PM.1980). Uses archaeological examples to examine material recombination, opportunistic reuse and inherited craft knowledge.
- [*Safety II professionals: How resilience engineering can transform safety practice*](https://www.sciencedirect.com/science/article/pii/S0951832018309864). Contrasts central specification with guided adaptation to emergent actual conditions.
- [*The Emperor has no clothes: A critique of Safety-II*](https://www.sciencedirect.com/science/article/pii/S0925753520304446). Documents critical objections and reminds us not to claim the adaptive paradigm is proven superior without independent outcome testing.

The **bricoleur** makes things work with a finite, inherited, opportunistic repertoire. Historical precedent can suggest an abstract mechanism—material recombination, fit-testing, thermal containment—but does not establish that a *particular contemporary object* is safe for a specific load, temperature, contamination level, or use.

The correct transfer from historic stone-based hearth construction to an improvised contemporary cooker may be **"stone, geometry and heat can form a useful cooking system"**, followed by **"what properties of these actual salvaged components and this site are verified?"** It is not **"people cooked over stones for millennia, so arbitrary concrete pavers or coated scrap metal are automatically safe."**

## Empirical safety rather than prestige contests

Safety should be informed by *mechanisms, exposure, observed outcomes, uncertainty and recoverability*, not the mere prestige or indignation of an authority. At the same time, risk is not refuted simply because one attempt succeeded or a living being survived an injury.

This prototype keeps three distinct judgments:

1. **Physical hazard mechanism.** Credible severe hazards—fracture/spalling from unsuitable heated masonry, toxic residue on food-contact surfaces, fire spread, harmful ventilation—can require a HOLD or REFUSE for hot operation. This is not a moral judgment or a global ban on reusing materials.
2. **Unknown, context-dependent limitation.** Unknown material properties, moisture, personal condition, access permissions or surroundings produce named unanswered questions. Small observation and reversible fit tests remain available when those tests don't expose the severe mechanism.
3. **Function observed vs safety verified.** A witnessed successful cold fit, cooked meal or repaired mechanism is a real report worth preserving. It still does not verify lifetime safety. A failure is information that opens alternate candidates rather than signaling that all improvisation is pointless.

The code does **not** assign unsupported numerical risk probabilities, derive health conclusions from animal survival, or assume an ancient method is universally appropriate. It uses coarse severity/scope gates as a first falsifiable representation, not a validated occupational/fire-safety standard.

**Medical boundary:** An animal's continued survival with exposed bone does not mean the condition is harmless. Open fractures require prompt veterinary care; worsening skin loss may have treatable causes and contagion risks. These medical conclusions are separate from engineering experimentation. Consult [Merck Veterinary Manual on feline bone injuries](https://www.merckvetmanual.com/cat-owners/bone%2C-joint%2C-and-muscle-disorders-of-cats/bone-disorders-in-cats) and [mange](https://www.merckvetmanual.com/cat-owners/skin-disorders-of-cats/mite-infestation-mange-acariasis-scabies-of-cats).

## What is implemented

### `traction.py`

- `Situation`: immutable, source-attributed chronological YES/NO observations. Inconvenient facts cannot be quietly overwritten, and UNKNOWN cannot be promoted to a guessed YES.
- `Hazard`: typed physical concern, severity, trigger, named independently observable clearing condition, attribution and minimum exposure where it matters.
- `Action`: purpose, prerequisites, proposed effects, reversible/controlled/high-exposure classification, source, intended probe. No effectful action can be executed.
- `assess()`: keeps low-exposure inquiry and cold fitting available even when fire material suitability is unresolved; blocks operation of an unsafe-hot proposal or carries named severe uncertainty forward for review. **It cannot certify actual real-world fire safety.**
- `Feedback`, `reenter()`: source-attributed WORKED, FAILED and INCONCLUSIVE witness. WORKED triggers ongoing safety checks and potential reusable capability; FAILED reopens only inspection and reversible alternatives, not arbitrary high-exposure actions; INCONCLUSIVE suggests a smaller/better-instrumented probe. No feedback silently changes the underlying scene facts.
- Synthetic first domain: material composition for a cooking apparatus; all original personal and site details anonymized and absent.
- Synthetic transfer domain: mechanical equipment repair, using the **same** state-evidence/action/reentry code.

### `anthropology.py`

- `HistoricalPattern` references the above literature with manually constructed source-description hashes.
- `ContemporaryProblem` carries a shared mechanism, actual unresolved material/situation properties and important differences.
- `compare()` can transfer abstract clues into a **feasibility hypothesis requiring observation**, and never into the claim that something is safe to operate.
- Synthetic analogies: material-reuse cooking project, equipment repair, unrelated claim that must return no useful shared mechanism.
- Includes both supportive and critical safety literature. Neither academic approval nor professional title has automatic authority over the trial outcome.

### Testing

`test_traction.py` (32 tests) and `test_anthropology.py` (13 tests) cover:

- No conventional appliance does not mean there are no possible exploratory actions.
- Cold/reversible material fitting remains a candidate despite severe unresolved hot-material questions.
- Known and unknown serious hazards still prevent unjustified high-exposure progression.
- Simulated success does not erase hazards; simulated failure opens new low-risk alternatives; ambiguous results trigger smaller probes.
- Real human observations must be sourced and preserve chronology.
- Historic material practices generate possible mechanisms, not automatic safety exemption.
- Unrelated domains cannot acquire invented relevance solely by word association.
- Repaired-equipment domain shares the core reasoning loop and source semantics.
- Zero real-world actions, local site data, physical tests or live survival outcomes.

Reproduce with Python 3.11:

```sh
cd experiments/quantumcode010
python -m unittest -v test_traction.py test_anthropology.py
python traction.py
python anthropology.py
```

CI: `.github/workflows/quantum-code-010.yml`.

## What remains unproven

- The hazard taxonomy is hand-curated, not validated by field engineers, tradespeople, or controlled trials. A severe failure mode not anticipated by the author can still be missed.
- The apparent observed success/failure is synthetic. There is no live physical sensor or independent verification.
- No historical material science has been demonstrated from these symbolic operations; anthropology gives conceptual analogies, not specifications for particular concrete, metal or pottery.
- Unknown facts are not automatically researched from live source records.
- Alternative candidates are still drawn from a declared inventory. MOTIF has not independently invented a physically tested machine.
- No independent baseline against standard planning, robust optimization or practical human experts has been performed.
- No real-world feedback loop has been run with a consenting contributor.

### The next hard test

Obtain **an opt-in, anonymized, real action history** and have a practitioner review what actually happened, including near misses, reasons for on-the-fly adjustments and unanticipated affordances. Blind-test the resulting decision model on physically safe, externally judged *cold/reversible* material-arrangement and repair tasks before considering any thermal, electrical, medical or other high-consequence experiment.

Distinguish **what worked**, **why it may have worked**, **what wasn't tested**, and **what would change if the environment changed**.

The goal is not a model that worships rules or one that celebrates risk. The goal is a model that learns **when to try, what to observe, when to revise, and when the evidence says to stop or ask for help**.
