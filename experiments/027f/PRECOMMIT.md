# MOTIF-027F: Three specialized T5 nodes and a source-to-question relevance check

PREREGISTERED before running the actual 027F model experiment. This is a synthetic study, not a real event or permission record.

The user asks to test a stronger relevance gate and ask MOTIF whether three specialized tiny T5 nodes help it reason better than one, none, or a classical comparator.

## Source relevance contract

Before admitting a candidate to the actual 022F Question Machine, a separate literal source relevance check needs a note substring about the nominated gate and another substring about an unresolved problem. The exact supporting quote is recorded. Unsupported or ambiguous requests HOLD. This is **not** independently authenticated human testimony, and could still mistake negated or hypothetical notes for an actual issue. The source-anchor rule is tested as its own strong NO-MODEL competitor so that adding a hand-written dictionary is not misattributed to T5.

Only after this relevance gate can the actual 022F independently test the registered source, and the original 016 LivingForest plan a new *synthetic* question. Nothing is authorized or dispatched externally.

## Three correlated specializations

One 77-million-parameter public google/flan-t5-small checkpoint and three specialized **encoder calls**: SCOUT (one nearest known missing-gate example), SKEPTIC (task-prefixed three-neighbor retrieval including NONE examples), CARTRIDGE_FINDER (retrieval against separately declared question-purpose examples). No fine-tuning and no independent witness claims. All three run on the same frozen weights; agreement can reflect the same shared error.

Compare 2/3 vote and 3/3 unanimity with SINGLE_T5, a fixed native rule, source-anchored-only rule, and classical TF-IDF with exactly the same 12 original 025F reference examples.

The frozen 50-case corpus has 10 each FOOD, AUDIO, ACCESS, STAFF and NONE, including ten resolved/negated notes. It was committed before model evaluation: experiments/027f/frozen_cases.py Git blob 6b36dd47c9cc3e260ddb91d4e9900cad61a1245e. All cases are researcher-written, not independent real user messages or a transfer benchmark.

## Prospective scoring

Count correct classification, true/false held question offers, missed risks, irrelevant accepted synthetic questions, CPU time, number of model calls and differences from same-evidence native and lexical baselines.

A plainly artificial method-choice score is: +2 for a correct grounded review offer, -4 for a misleading review offer, -1 for missed real synthetic gate, -0.1 times measured model CPU seconds. These units do not represent real human welfare, real opportunity cost, energy, grant success or a calibrated cost of doing nothing.

MOTIF can recommend further SHADOW research if a T5 method exceeds the best non-model candidate in this toy score and makes zero misleading grounded offers. Its real-world execution and owner-approval policy remains NO_T5 until independently validated.

When the models fail, preserve the evidence and generate the next falsifiable question. Their generated output, even unanimous, is NOT a license to invent a source, action, contact, permission or fact.

Reproduce standard-library tests from experiments/027f with python -m unittest -v test_nodes.py. The real checkpoint workflow is .github/workflows/motif027f-three-nodes.yml, public revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab, local-only inference, no model weights stored in the repo.

Stacked on MOTIF-026F PR #52. Everything remains synthetic and draft.
