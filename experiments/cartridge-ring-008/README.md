# MOTIF RING-008 — Language Algorithm Foundry: Attempted Invention, Honest Falsification

**Experimental question:** Can MOTIF search for a new algorithm that interprets unfamiliar human-language statements as typed meanings, rather than relying on the hand-written RING-007 phrase list? Can the resulting system survive truly new sentence constructions?

**Result:** We **automatically synthesized a new combination of pre-audited interpretation operators** and tested it. It improved exact structured-frame predictions over the strongest single-operator seed on two author-created novel challenge packs. **It did not invent general language understanding.** It made wrong interpretations, including false read-only interpretations of actual action requests in the synthetic scoring scheme.

This is a *research PR*, stacked on RING-007. All external authority remains NONE.

## What the system attempted

A text sentence does not map to one opaque label. It maps to a typed relational triple:

```text
Natural-language utterance
          |
          v
   generated algorithm AST
    ┌─────┴─────┐
    | features  |  ← selected via automatic search
    | decoder   |  ← selected via automatic search
    | binding   |  ← joint classes vs compositional slots
    | threshold |  ← margin / grounding abstention
    └─────┬─────┘
          v
    (MODE, TOPIC, OPERATOR)
          |
          v
    HYPOTHESIS or HOLD
```

The **MODE** is INQUIRE, ACT, META, or UNKNOWN. **TOPIC** is PATH, RECORD, SCHEDULE, or UNKNOWN. **OPERATOR** is REACH, INSPECT, TIME, TRANSFER, MODIFY, or UNKNOWN.

In particular, `could you share the document with friends` (an effectful request under this authored taxonomy) must be distinguished from `what if we share the document` (a hypothetical question), even if they contain overlapping tokens. A wrong `ACT → INQUIRE/META` prediction is logged as an **unsafe false-readonly interpretation**. Because the parser is nonauthoritative, no action is ever attempted.

This is deliberately a wider test than the RING-007 single read-only route-reachability frame. There are multiple content domains and separate request/mention distinctions.

## How it searched for an algorithm

`engine.py` defines an audited, **typed code-free executable DSL**. Its operators include:

- word and ordered bigram features;
- skip-distance token relations;
- character 3-grams and morphological prefix/suffix features;
- position and bounded token-order features;
- multinomial naïve Bayes or class-centroid decoding;
- **factorized semantic-role inference** versus joint frame classification;
- abstention using margin and learned-feature overlap.

`synthesizer.py` does not start with a predetermined final interpreter. It creates weak atomic programs, **mutates and recombines their feature extraction / decoder / role-binding structures**, executes candidates on author-labeled development examples, and freezes the best under a declared risk-penalized objective.

**Search actually executed 160 typed candidate programs.** The selected program was **not in its initial seed list**:

```json
{
  "ops": ["char3", "skip"],
  "decoder": "bayes",
  "binding": "factorized",
  "margin": 0.0,
  "overlap": 2
}
```

That means character-level three-letter features and skip-distance word relationships, with a separately learned classifier for each typed semantic role. **This composition was found by the system from its limited operator algebra.** It was not created by a generative code-writing model and did not introduce any new primitive interpreter operator beyond the developer-written DSL.

## Evidence isolation

- **Training:** 135 synthetic labeled text/frame examples generated from one authored template family.
- **Program-selection development:** 90 examples generated from *different* authored templates. These examples are allowed to influence the selected algorithm and abstention settings.
- **Post-freeze challenge:** 252 examples in **two fresh-seeded source packets**, with distinct *third-family* sentence constructions and additional out-of-vocabulary/safety-confusable phrases. The challenge module is imported **only by the evaluation script after the executable program artifact is serialized and its digest verified**.
- All source text and semantic frame labels are **experimenter-authored**. Different templates and seeds do not establish independently collected human language or independent test designers.
- The frozen program and evaluation both receive SHA256 content receipts. These identify and check content, not authenticity of real-world statements.

## Real measured outcomes

**On development data used to select the program:** 63 / 90 exact frame predictions, zero observed unsafe false-readonly classifications. This is development, **not independent evidence of generalization**.

**On the post-freeze authored challenge:** 252 examples total.

| Model / control | Exact typed frames | Wrong decisive frames | Unsafe false-readonly predictions |
| --- | ---: | ---: | ---: |
| **Auto-composed char3 + skip, factorized Bayes** | **98 / 252** | **39** | **4** |
| Strongest single-feature seed (selected on dev) | 75 / 252 | 30 | 6 |
| Prior RING-007 hardcoded route-query grammar | 0 / 252 | 0 | 0 |
| Always abstain | 0 / 252 | 0 | 0 |
| Overconfident fixed-path foil | 24 / 252 | 228 | 92 |

The 0/252 old grammar result reflects its **much narrower scope**: it only recognizes the original authored path question grammar, not the varied text structures in this new challenge. It is not a fair replacement for a multi-domain text interpreter, but is included to show the change in coverage.

**Findings:**

1. The new, searched composition made **23 more exact predictions** than its best initial atomic seed and two fewer unsafe false-readonly mistakes, under these authored examples.
2. It also made **9 more wrong decisive predictions**, showing how expanded coverage can increase confidently incorrect outputs.
3. Despite zero unsafe false-readonly errors in the model-selection set, it made **4 in the previously unseen-to-selection challenge**. The observed safety criterion did *not* transfer.
4. Accurate frame interpretation was only **98/252 (38.9%)**. That is nowhere near a general language-understanding algorithm.
5. A safe-mode output is always just a **PENCIL hypothesis**. The program cannot authorize source changes, outside actions, network calls, or newly discovered GitHub methods.

The world labels, scope distinctions, semantic classes, search operators and utility weights were all chosen by the experiment author. This is a meaningful **automated algorithm-composition and falsification** result, not a breakthrough in universal semantics.

## Hypergraph feedback

`evidence_graph.py` binds the **training source, development source, selected program and two unseen-to-selection test packets** into a typed many-tail evidence hyperedge with *multiple simultaneous consequences*:

- improved exact structured semantic interpretations;
- still-present unsafe false-readonly classifications;
- additional wrong decisive interpretations and abstentions;
- no external-world evidence to generalize from;
- a concrete next research question: whether the algorithm can synthesize **new relational primitives**, not just recombine our fixed ones.

Failures are never silently omitted to improve apparent usefulness. No new real-world ability or executable source branch is automatically admitted.

## Reproduce

```sh
python -m unittest discover -s experiments/cartridge-ring-008 -p 'test_*.py' -v

# This first command imports only train and development code, not the heldout.
python experiments/cartridge-ring-008/synthesizer.py \
  --out /tmp/ring008-program.json

# Only after program freeze is the novel-world challenge imported and scored.
python experiments/cartridge-ring-008/benchmark.py \
  --artifact /tmp/ring008-program.json \
  --out /tmp/ring008-new-language.json

python experiments/cartridge-ring-008/evidence_graph.py \
  --artifact /tmp/ring008-program.json \
  --benchmark /tmp/ring008-new-language.json \
  --out /tmp/ring008-evidence-hypergraph.json
```

GitHub Actions uploads all three machine-readable artifacts, including **every** heldout case prediction and error, so the reported totals can be independently inspected from source receipts.

## What would constitute a stronger next attempt?

The next frontier should test **counterexample-guided creation of new semantic operators**, not only choosing existing feature combinations. For example:

- Discover a typed distinction between *mentioning* an external action and *requesting* one, from contrasting pairs rather than a manually compiled list.
- Learn nested compositional scope and negation over multiple domains, with a source graph of who requested what from whom.
- Propose one new typed DSL primitive from development failures, prove it stays code-free and review-gated, and then evaluate it on an **untouched, separately authored** holdout suite.
- Include independently written real utterances and independent human task-meaning annotations, which synthetic source generators cannot replace.

The result may be a useful emerging architecture, or a further falsification. Neither should be called universal language understanding without extensive unseen evidence.

**No unrestricted program generation, automatic GitHub merge, new external connection, source registry admission, or real-world authority.**
