# MOTIF RING-011 — Nested Voice, Document Carrier, and Uncertain Meaning

**Research status: successful execution; the proposed relational binder FAILED to beat strong classical controls or eliminate false operative interpretations.** This is a draft stacked experiment based on RING-010. Nothing was merged, deployed, given tool permissions, or connected to a real-world action system.

## Question

Can MOTIF infer **which voice owns a statement**, whether an event is actually requested or only nested in a quote / hypothetical / parentheses, and whether a text's *carrier* is a poem, a note, a memory, or a record?

The user proposed using intentionally cryptic material from a privately connected Google Drive book, *How to Live*. This was inspected along with its crosswalk/index. The book's reading instructions explicitly encourage multiple interpretation passes, distinguish narrative order from asserted chronology, use layered parentheses and self-commentary, and insist that different surviving textual carriers are not interchangeable evidence classes.

**Privacy boundary:** The public GitHub source and CI artifacts contain entirely fresh, source-authored synthetic text. They contain **no verbatim lines from the Google Drive book**, no private identities, allegations, notebook contents, court details, or private links. The book informed structural test categories only.

## Epistemic and linguistic distinction

The program begins with an **externally declared** observed event (speaker, agent, verb, patient) and an **externally declared document carrier**. It is **not** tasked with identifying people or verifying historical events from free text. That explicit external event binding is a major simplification and should not be confused with general natural-language understanding.

It tries to infer an output graph with typed relations:

```text
ROOT     -- FORCE             --> DIRECTIVE | ASSERTION | MENTION
EVENT    -- SCOPE             --> ROOT | QUOTED | IMAGINED | CONDITIONAL
EVENT    -- POLARITY          --> POS | NEG
EVENT    -- REQUESTED_BY_ROOT --> yes/no (derived from preceding three)
EVENT    -- VOICE_OWNER       --> externally bound root speaker or quoted agent
DOCUMENT -- CARRIER           --> SONG | NOTE | MEMORY | RECORD
DOCUMENT -- EVIDENCE_STATUS   --> source-category marker, NOT authenticated proof

ROOT_SCOPE_0 -- CONTAINS --> SCOPE_1 -- CONTAINS --> SCOPE_2
SCOPE_N -- BINDS --> EVENT
```

The source carrier and evidence status are **not inferred from the poem's voice**. A song does not become independent evidence that its narrative occurred, a note does not become corroboration, a memory does not become a contemporaneous record, and a named record does not authenticate itself merely by being a record.

The proposition

> A asks B to do C

is different from

> A asks B to quote someone else asking for C.

The outer utterance may be a genuine directive while **the quoted event C is not what the outer speaker requested to happen**. This distinction motivates a separate `REQUESTED_BY_ROOT` relation instead of naïvely treating every imperative or quoted request as operative.

## What the algorithm actually generated

`corpus.py` generates **30 three-way training contrasts** and **30 development contrasts** (90 utterances per split), across reported speech, negation, quotations, nested asides, conditions, and mixed root/embedded requests. All semantic labels are synthetic and authored by the developer.

`binder.py` tokenizes and abstracts the *externally supplied* event fields, builds a bracket-containment stack, compares source event-stable triples, finds which typed target graph relations differ, and derives new contextual lexical/structural rule **instances**. A post-falsifier repair derives one event-local polarity insertion cue directly from positive/negative meaning contrasts, instead of hardcoding an English negator. A separate developer-written conservative restriction attempts to hold apparent root directives located in a bracketed event. This restriction is **not** a generally valid interpretation of parentheses.

`search.py` tests **32 finite derivation configurations** on the development split and freezes the selected program **before loading** the test modules. It produced **9 derived semantic edge transitions** and **119 contextual relation rules** for the selected model. Its development accuracy was **75/90** (15 wrong, 5 incorrectly promoted root-action readings). Development results were used to select the configuration and are **not independent generalization evidence**.

**Crucial distinction:** The graph relation ontology, bracket parser, action/event fields, base rewrite runtime, candidate parameters, utility priorities and source truth labels were all written by the developer. The search discovered configurations and **data-only rule instances**, not a new graph primitive or a universal understanding algorithm.

## Real post-freeze evaluation and its limits

Three artificial challenge populations were run:

1. **OOV_CONTENT:** 90 utterances with unseen source-bound names, verbs and objects, but familiar semantic constructions.
2. **CRYPTIC_NESTED:** 90 utterances with nested, layered parentheses, quotations and editorial-style asides, inspired by the shape of the private work, not copied from it.
3. **COUNTEREXAMPLE_FOLLOWUP:** 108 newly generated utterances with unmarked quotations, double negation, a negation in an irrelevant aside, novel conditionals and different voice owners.

The first two populations **were inspected during the algorithm repair process**. They are now **debugging regressions**, not clean independent evidence of the repaired system. The third population was written after that change and evaluated later, but it too was authored by the same experimenter and is not independently annotated speech.

### Results, all 288 author-created texts

| Interpreter | Exact full semantic graphs | Wrong decisive graphs | Wrongly treats event as operative root request | Bound test cases held |
| --- | ---: | ---: | ---: | ---: |
| **RING-011 generated nested binder** | **228 / 288** | 60 | **16** | 0 |
| Same-training simple word Bayes | **244 / 288** | 44 | 0 | 0 |
| Same-training word+bigram Bayes | **242 / 288** | 46 | 0 | 0 |
| Always HOLD | 0 | 0 | 0 | 288 |

The binder **performed worse than both classical controls**, on this designed problem and source distribution. It still produced 16 incorrect operative-root interpretations, despite the source-based polarity repair and a conservative embedded-bracket rule. None of these decisions authorized or attempted any action.

The zero false-root-action results for the two classical methods apply **only to this particular authored suite**. They do not establish that those methods are safer on actual human language.

Separately, **6/6 cryptic, unbound synthetic utterances were held** rather than being assigned a fabricated event graph. This is the strongest demonstrated refusal boundary in this stage. It is not proof that the system reliably refuses all ambiguities.

## Why this is useful despite the negative result

RING-010 showed that source-trained flat graph rewrite instances could reach 220/240 exact on an earlier synthetic set but mislabeled some quoted/hypothetical events as directives. RING-011 tested a proposed hierarchical response, instead of silently claiming nesting was solved.

We learned:

- A graph representation **does not** itself confer reliable compositional understanding.
- Recovering nested parentheses and source-event anchors is easier than learning **which outer speaker owns an embedded instruction**.
- More semantic rule instances do not guarantee fewer false root-action inferences.
- Text carrier (song, note, memory, record) must remain orthogonal to the statement's apparent truth or authority.
- The tested 32-config source-derived binder is **not ready for admission as an operative cartridge**. The stronger same-source classical controls remain indispensable.
- Retrospective debugging on inspected test cases must be identified as debugging, not hidden as independent test success.

## Evidence and tampering checks

`evidence_graph.py` reconciles all per-case outputs against aggregate exact/wrong/false-action/abstention tallies, preserves **three separately scoped packet identities**, rejects forged carrier truth even with a recomputed hash, and records the **benefit and harms in the SAME many-tail hypergraph**:

```text
Source train + development → learned 9 graph deltas + 119 cue instances
                    |
                    v
   OOV + nested + followup source packets
         |                      |
         v                      v
    228 exact graphs     60 wrong decisive graphs
                        including 16 false root requests
         |                      |
         +----------+-----------+
                    v
        NOT automatically promoted
        into executable source methods
```

The receipt hashes establish file consistency, not that a person, poem, note, or record is truthful in the outside world. Six additional unbound cryptic prompts produce HOLD without invented events.

## Reproduce

```bash
python -m unittest discover -s experiments/cartridge-ring-010 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-011 -p 'test_*.py' -v

python experiments/cartridge-ring-011/search.py --out /tmp/ring011-frozen.json
python experiments/cartridge-ring-011/benchmark.py \
    --frozen /tmp/ring011-frozen.json --out /tmp/ring011-trials.json
python experiments/cartridge-ring-011/evidence_graph.py \
    --frozen /tmp/ring011-frozen.json \
    --benchmark /tmp/ring011-trials.json --out /tmp/ring011-hypergraph.json
```

GitHub Actions runs **31 tests** (14 inherited RING-010 plus 17 new RING-011), all 32 candidate derivations, all 288 authored post-selection cases, and the source-reconciliation audit. It uploads the generated program, all per-case source hashes/results, and conditional graph evidence.

## Next falsifier

Try a **learned parse/scope tree with explicit clause boundaries**, event arguments, embedding verbs, and negation attachment—plus an **independent disagreement gate against word/bigram controls**. Its source graph must distinguish *who says that somebody else requested an action*, from a request addressed to the current system. Evaluate with human-authored ambiguity and independent semantic annotations; the private source should remain private unless explicitly approved for public release.

**Research conclusion:** A valid negative experimental result. A harder semantic operator is still needed. The graph binder was source-induced and executable as data; its semantics were not reliable enough to replace simpler baselines or safely issue instructions.
