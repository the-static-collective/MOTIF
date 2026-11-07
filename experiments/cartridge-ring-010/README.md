# MOTIF RING-010 — Source-Derived Semantic Graph Rewrites

**Research intent:** Go beyond RING-009's learned phrase-cue instances and attempt to induce **typed relational graph transformations** from changes in the *meaning graph* associated with contrasting utterances. This is a concrete experiment in relational structure induction, **not** the invention of a general semantic ontology from raw speech.

**Status:** GitHub Actions tested in a draft stacked experimental branch. No merges into main, external actions, credential use, outside authority, or automatic cartridge admission.

## The problem

Two utterances can mention exactly the same externally observed event but ascribe different meaning to it.

> Mara asks Sol to carry the parcel.

> Mara wonders whether Sol might carry the parcel.

A simple word classifier may view these as similar. An utterance graph can represent differences:

```text
          observed event (explicitly supplied)
         speaker=Mara, agent=Sol
            action=carry, patient=parcel
                       |
           +-----------+--------------+
           |                          |
         "asks"                    "wonders"
           |                          |
 UTTERANCE --FORCE--> DIRECTIVE   UTTERANCE --FORCE--> MENTION
 UTTERANCE --SCOPE--> ROOT        UTTERANCE --SCOPE--> IMAGINED
 EVENT     --POLARITY--> POS      EVENT     --POLARITY--> POS
```

A quote, negation or conditional phrase changes a different part of the graph. A useful language interpreter should not automatically turn a hypothetical or quoted event into an actual requested effect.

### What we supplied to the learner

Each synthetic training example includes a raw sentence, a separately declared source event with **speaker, agent, verb and patient**, and an **author-labeled semantic graph** with relation keys `FORCE`, `SCOPE` and `POLARITY`. These relation names and their allowed values were created by the experiment author; **MOTIF did not discover the ontology itself**. The separately declared source event is an explicit upstream source input. The program does **not** discover speaker, agent, verb or patient from arbitrary text.

Each training pair holds the source event constant but changes one or more semantic edges. Graph comparisons, not prewritten phrase/verb lists, drive the induction.

## What the program *actually derived*

`induce.py` reads the training pairs and computes directed graph differences. For each changed relation, it constructs **source-supported data-only typed graph rewrite operators** such as `REPLACE_TYPED_EDGE`, with derived source/target values. Independently it abstracts the externally declared actor/action/object words into variables and learns discriminating lexical cues **before or after** the declared action. Each resulting source cue can propose a specific graph relation value.

A newly generated rule can look like:

```json
{
  "opcode": "RELATIONAL_CUE_BEFORE_EVENT",
  "relation": "FORCE",
  "value": "DIRECTIVE",
  "cue": ["asks"],
  "support": 12,
  "derived_from": "PAIRED_TYPED_GRAPH_DIFF_AND_LEXICAL_CONTEXT"
}
```

This is illustrative, not a claim about the precise support count of the final generated rule. No arbitrary Python can be emitted by these ASTs. If the provided event variables cannot be uniquely grounded, the parser HOLDs.

`search.py` runs a finite program-derivation search on **different training vs development examples** and freezes its winner before evaluating new examples. The actual run evaluated **54 configurations**, selecting `min_support=3, max_cue=2, max_gap=20, purity=1.0`.

It produced **6 distinct graph-transition operator instances** and **74 learned source-contextual cue-to-graph operator instances**. This is new relational-program data automatically derived from supervised contrasts. It is not a new foundational graph rewrite opcode, mathematical principle or universal understanding of speaker intent.

## Source splits

- **Training:** 60 meaning contrast pairs / 120 utterances covering directive-vs-hypothetical, direct-vs-quoted, positive-vs-negative report, unconditional-vs-conditional, and assertion-vs-counterfactual forms.
- **Development:** 60 different contrast pairs / 120 utterances with altered adverbial construction. **Used for selecting** a candidate; the winning program produced 120/120 correct graphs on this set. **This is *not* independent testing.**
- **Post-freeze test, world A:** 120 utterances with **new verbs, people and objects**, but familiar relational surface structures. The learner had access to the same kind of externally supplied source event; unknown event lexemes transfer by replacing them with source-bound variables.
- **Post-freeze test, world B:** 120 utterances combining quotes, nested imagined requests, event negation, double negative, conditions inside quoted speech and unfamiliar action lexemes. These expose where cues in a subordinate clause are mistaken for the outer utterance's authority or polarity.
- Both heldout packets are **author-designed**. They were imported into the scorer only **after** freezing and validating the generated program. They were not authored or labeled by independent humans, and the two batches share the experimenter's conceptual assumptions.

## Measured results on the same 240 source-event cases

| Parser | Exact complete semantic graphs | Wrong decisive graphs | False `DIRECTIVE` when meaning isn't a directive |
| --- | ---: | ---: | ---: |
| **RING-010 derived graph rewrite program** | **220 / 240** | **20** | **10** |
| Same-data, variable-masked word Bayes | 190 / 240 | 50 | 20 |
| Same-data, variable-masked word+bigram Bayes | 176 / 240 | 64 | **0** |
| Always HOLD | 0 | 0 | 0 |

There is no zero-risk victory. The new program performed best by exact whole-graph accuracy on this author-generated test, **but it made 10 high-consequence classification errors** where a hypothetical or quoted context was classified as a directive. The word+bigram Bayes baseline had *lower accuracy* but **zero** such false-directive errors in this authored suite. None of these are safe to connect directly to effectful tools.

The breakdown matters:

| Evaluation family | RING-010 correct / total | RING-010 false directive readings |
| --- | ---: | ---: |
| New event vocabulary with familiar semantic constructions | **120 / 120** | 0 |
| Nested scope, quotation and negation | **100 / 120** | **10** |

The graph representation itself therefore transfers when the observed event is known and the syntax is familiar. **Scope composition is still insufficient**. The system has not reliably learned the difference between an outer request and an inner quoted/hypothetical request. Nor has it proven general negation scope.

### Limits of the result

This experiment tests **graph interpretation under explicitly supplied event bindings**, not speaker recognition, real-world truth verification, spontaneous linguistic ontology invention, universal algorithm discovery, independently blind natural-language understanding, or secure instruction execution. A good synthetic classification rate does not confer authority to send messages, modify files or perform any external actions.

Learning labels `FORCE`, `SCOPE` and `POLARITY` were author-provided; the program **derived rule instances and transition operators between those relations**. The general `REPLACE_TYPED_EDGE` computational primitive was implemented by the developer.

In particular, the apparently perfect 120/120 development result was a *selection* metric; it did not survive nested-scope challenge unchanged. A high scoring system can still be unacceptable if it incorrectly interprets a quoted instruction as a real directive.

## Hypergraph evidence

`evidence_graph.py` verifies source and frozen program identities and reconciles **every** per-case exact, incorrect, false directive and abstention score against the totals. It produces two evidence-scoped, many-tail/many-head relations:

1. Source-labeled training graphs plus development graphs → **six data-derived graph transitions and 74 contextual operator instances**, **not** a newly discovered relation ontology.
2. Frozen program plus the two new test worlds → **220 correct graphs**, **20 wrong graphs**, including **10 false directives**, and a named unresolved frontier: *scope precedence in nested quotations, hypothetical reported requests and negation*.

This does not automatically promote source-derived graph operators into an executable tool registry or claim real-world certainty.

## Use of unusual prior human language

The user explicitly offered past unconventional messages for language testing. Some prior invented-language and highly metaphorical messages informed the **category of stress cases** we should consider. **The public GitHub experiment contains only freshly invented synthetic text**; raw prior private messages, any personal facts, and original conversation transcripts were **not** copied into this source branch, the test artifacts or GitHub Actions logs.

These prior messages are *not* counted as independently labeled evaluation cases. Most do not even carry the explicit source-event schema required by this prototype. Treating them as successful parsed language without genuine ground truth would be a false generalization claim.

## Reproduce

```sh
python -m unittest discover -s experiments/cartridge-ring-009 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-010 -p 'test_*.py' -v

python experiments/cartridge-ring-010/search.py \
  --out /tmp/ring010-frozen.json

python experiments/cartridge-ring-010/benchmark.py \
  --frozen /tmp/ring010-frozen.json \
  --out /tmp/ring010-heldout.json

python experiments/cartridge-ring-010/evidence_graph.py \
  --frozen /tmp/ring010-frozen.json \
  --benchmark /tmp/ring010-heldout.json \
  --out /tmp/ring010-evidence-hypergraph.json
```

The GitHub Actions job runs all 28 inherited/current tests, 54 candidate derivations, the 240-case post-freeze evaluation and the measured hypergraph evidence audit. The workflow uploads the generated rule AST, complete per-case source receipts and reconciled evidence hypergraph. **The source training/test code is deterministic.**

## What to try next

**The specific missing operator is likely a *nested-scope binder*, not another bag of lexical cues.** Test an automatically induced mechanism that identifies which clause owns an embedded instruction and which negation attaches to which event. The graph itself needs local scopes with parent–child containment, source-of-quotation and explicit event identity across embedded worlds.

The new hypothesis should be generated **from graph counterexamples** and implemented as a reviewable typed DSL operation rather than a string of manually patched English keywords. Model-selection failures used to invent it cannot be reused as independent proof of success. A genuinely fresh, independently authored nested-utterance challenge, ideally using consented human examples with independent semantic annotation, would be necessary to measure generalization.

**Bottom line:** We derived executable *data-only relational graph rewrites* from contrasting meanings and demonstrated useful transfer, but nested pragmatic scope still breaks the model. That failure is now an inspectable, precise engineering target.
