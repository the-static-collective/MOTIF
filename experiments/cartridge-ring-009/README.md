# MOTIF RING-009 — Contrastive Relational Operator Invention

**Research question:** Can MOTIF construct an executable new semantic **relation instance** from examples that contrast *requesting an action* against *merely discussing the same action*, rather than recombining a fixed list of phrase features?

**Verified result:** **Yes, for a bounded typed rule language and author-generated minimal pairs.** The system induced 25 previously unwritten relational-rule instances; it recovered 108 correct interpretations on 240 author-created unseen-to-selection text cases, made **zero incorrect decisive interpretations** on those test packets, and **abstained on the other 132**. It did **not** invent a new mathematical/computational primitive or achieve open-domain language understanding. The reviewed finite source operator family, semantic frame labels and synthetic examples were written by the experimenter.

Changes remain in a draft branch stacked on RING-008. Nothing is deployed to `main`; all source execution authority remains NONE.

## Mechanism: actually creating new typed relations from meaning contrasts

A conventional bag-of-words approach can learn the wrong rule that the word `send` means the statement is asking for a send operation. We intentionally construct paired examples containing **the identical action/event words** but expressing different speech acts:

```text
"please send the ledger to neighbors"
    ↔
"what if someone were to send the ledger to neighbors"

same shared action: "send the ledger to neighbors"
different speech act: ACT versus META
```

The model receives the *raw strings and target meaning triples*, never the action's word location, which template generated the examples, or prewritten keywords for `please`, `send`, `what if`, etc.

The **anti-unifier** searches the two sentences for their longest shared contiguous token span. It deduces which action/event words are common and which contextual cues are distinctive. These are converted into candidate typed **relation ASTs**:

```json
{
  "opcode": "CUE_PRECEDES_SHARED_EVENT",
  "cue": ["please"],
  "inferred_speech_act": "ACT",
  "contrast_support": 12
}
```

That particular example is illustrative of the shape of an induced rule; actual generated source ASTs include source support and competing-class discrimination counts. The learner also discovers the complementary *hypothetical mention* cues, the reverse **CUE_FOLLOWS_SHARED_EVENT** relation, and the event-anchor-to-topic/operator mapping from labels. Its core operation is thus relational: `cue phrase` → *ordered proximity to* → `shared action` → *semantic role*.

**What was invented, precisely:** 25 new **typed rule instances** and a selected composed program built from contrastive evidence. **What was not invented:** a novel generic Python opcode, a general theory of natural language, generalizable abstract scopes, a new external action permission, or an open-ended self-rewriting algorithm. The grammar that permits before/after-pivot relations was authored in advance.

## Source splits and honesty

The protocol enforces separate author-generated training, selection and post-freeze test samples.

- **Training:** 60 minimal pairs (120 utterances) with two distinct speech-act labels for the same event, from three source tasks spanning records and schedules.
- **Development/selection:** 60 other minimal pairs (120 utterances), with altered sentence patterns. **54 candidate induction configurations actually executed** here. The selected candidate scored **96 / 120 exact frames, zero wrong decisive answers** and abstained on the remainder. This is model-selection evidence and is *not independent accuracy verification*.
- **Heldout:** another **two separately seeded 60-pair challenge packets**, 240 total utterances, constructed with different sentence templates and cases such as `could you describe what would happen if ...`, `please explain why someone would ...`, or unfamiliar action verbs that the training data cannot ground.

The challenge module is **not imported** by the learner or the selector; it enters only when the candidate program is serialized, its source hashes are verified and its rules are **re-derived from the original train data**. Every post-freeze decision, wrong guess, mode misclassification and abstention is included in the downloadable GitHub Actions artifact.

All templates, contrast labels, domain frames and test text are **synthetic and experimenter-authored**. This is a test of compositional hypothesis-building under controlled data, not a blind independent human-language benchmark. Withholding labels from selection does not guarantee a conceptually independent test designer.

## Source-native measured outcomes

**Frozen post-selection challenge: 240 utterances total.**

| Parser / control | Correct semantic triples | Wrong decisive semantic triples | Total decisive outputs | False read-only interpretations of ACT |
| --- | ---: | ---: | ---: | ---: |
| **RING-009 contrast-induced ordered relations** | **108** | **0** | **108** | **0** |
| RING-008 char3+skip Bayes, *trained on the same 009 examples* | 180 | 60 | 240 | 0 |
| Word-only Bayes, *trained on the same 009 examples* | **184** | 52 | 236 | 0 |
| RING-008 char3+skip Bayes, trained on its original 008 examples | 73 | 96 | 169 | **11** |
| Always HOLD | 0 | 0 | 0 | 0 |

**Interpretation:**

- The automatically generated rule program achieved **100% observed precision among its 108 decisive interpretations in these author-generated test cases**; it deliberately *withheld the other 132*. This is not evidence of universal 100% precision.
- Same-data word-based Bayes recovered substantially **more correct meaning frames** (184 vs 108), but produced **52 wrong decisive meanings**. Those 52 are not all unsafe effect misclassifications: they include mode/topic/operator errors in the authored taxonomy.
- A previously frozen RING-008 model learned from a different corpus was much weaker under this new shift and made **11 unsafe ACT-as-read-only** predictions. Its result is not a fair same-training comparator; the two same-data baselines are.
- This is a **precision/coverage** experiment, not a measured runtime/energy gain, proof of real intent inference, or justification to authorize execution from generated interpretations. Even a correct frame is only a nonauthoritative PENCIL hypothesis.

## Hypergraph evidence

`evidence_graph.py` validates frozen source AST identity against actual training data, checks per-case outcomes and model totals, and records **two multi-tail/multi-head evidence relations**:

1. The 60 training contrast pairs + 60 selection contrast pairs → newly induced typed operator instances + question of discovering novel **computational** primitives.
2. The frozen program + training + selection + two test packets → both the observed correct interpretations and **132 unresolved cases**, plus explicit comparative wrong-decision and safety classifications.

These observations **do not install** new methods or automatically promote simulated success to real-world general ability. The source receipts provide mutation detection, not independent authentication of the experimenter's truth labels.

## Reproduction

```bash
python -m unittest discover -s experiments/cartridge-ring-008 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-009 -p 'test_*.py' -v

# Learn operator ASTs from paired text, with no access to test templates:
python experiments/cartridge-ring-009/search.py --out /tmp/ring009-frozen.json

# Only after freezing, import and evaluate the novel heldout grammar:
python experiments/cartridge-ring-009/benchmark.py \
  --frozen /tmp/ring009-frozen.json --out /tmp/ring009-eval.json

python experiments/cartridge-ring-009/evidence_graph.py \
  --frozen /tmp/ring009-frozen.json --benchmark /tmp/ring009-eval.json \
  --out /tmp/ring009-hypergraph.json
```

No Docker or GPUs are required for these **offline safe-data DSL evaluations**. This RING-009 does **not** invoke arbitrary pinned branches as runtime plugins; it uses source code from the stacked review branch and remains a separate experimental layer.

## Next falsification frontier

- Try independently human-authored and independently labeled text, including nested negation, indirect imperatives and idioms.
- Replace the current *longest common contiguous action span* with a generated compositional graph of predicate, agent, speaker, scope and negation; the learner must infer the graph from contrasts rather than receive prewritten cue lists.
- Introduce truly unseen action **verbs** with learned transfer via structural variables, not exact observed verb anchors. Do not accept a zero-error score achieved by always abstaining.
- Establish a well-defined review-gated contract for promoting a learned relation to the MOTIF cartridge registry, with evidence of lower error and adequate coverage against strong same-data controls.
- Compare proof value and resource cost; mere number of induced rules is not a measure of intelligence.

**Result: a genuine new automatically inferred relational-rule family instance within a known DSL, with a reproducible and very significant remaining frontier.**
