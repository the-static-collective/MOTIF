# MOTIF Thought Fields — full-stack build plan
**RFC: THOUGHT-006–010 | 2026-11-06 | Design-only, not implemented**

**Intention.** Give MOTIF a *pencil* for exploring tentative arrangements, a *pen* for recording current commitments, and a non-fungible, multi-instance thought field in which one idea may appear in several places, interpretations and geometries simultaneously. Let MOTIF choose when to use these instruments, revisit the same ideas in later phases, and measure whether the extra representational freedom actually helps.

**Existing starting point (inspected).** `experiments/geometry-005/thought_space.py` currently has `Node(id,label,kind)`, `Edge(source,target,relation,origin,confidence,observed)`, typed paths/common-neighbor bridge proposals, and a deterministic `choose_thought_space()` router. It offers spring/radial/flower-hex projections and a CLI/SVG adapter. It is a local synthetic experiment; *coordinates are not evidence*. This RFC is a **child of the open GEOM-005 branch**, not a change to `main`, an existing deployed service, or confirmation of any future integration.

## First principle: a thought is not its location

```text
  sourced input / observation
       |
       v
  source graph + identity registry (stable, inspectable)
       |
       +---> Pencil sketch A (associations / exploratory geometry)
       +---> Pencil sketch B (causality / dependencies)
       +---> Pencil sketch C (alternative meanings / contradiction)
                    |
             critique / countermodels
                    |
             PEN COMMITMENT (scoped, revisable)
                    |
       +---> Concrete pencil: plans / affordances / possible moves
                    |
             critique + evidence checks
                    |
             PEN CONCLUSION (scoped, revisable; NOT action authority)
```

The layout layer must never grant identity, truth, causal direction, source independence or permission. A useful map can direct *which questions to ask next*, provided the proposed question is explicitly labeled a hypothesis and independently checked before any claim is promoted.

## Five separate identities (do not collapse them)

| Object | Meaning | Example |
|---|---|---|
| `Concept` | Persistent, immutable handle for a **particular interpreted referent**, never a word key. Its label and meaning can be revised by explicit version. | `c:home-as-shelter` |
| `Expression` | Sourced occurrence of text, claim, observation or symbol. One phrase can refer ambiguously to several concepts. | `e:message-14-span-3`: "home" |
| `Manifestation` | Non-fungible occurrence of a concept within a reasoning context/role/phase. Its **unique ID survives a layout change**. Several manifestations may reference one concept. | `m:shelter-in-logistics`; `m:shelter-in-values` |
| `Placement` | Optional occurrence of a manifestation within a particular view, with coordinates, layout version and purpose. **Many placements per manifestation** are allowed, even in a single view. | `p:map2:copyB` |
| `Assertion` | Typed proposition/relation between explicitly identified objects, with evidence, opposition, scope, phase and status. | `a:meal-requires-volunteers` |

A *word* does not uniquely identify a concept. A concept may appear as many noninterchangeable manifestations; one expression may propose several possible referents without asserting they are equivalent. Two manifestations that share a concept are **not necessarily interchangeable** in their local contexts. If two concepts are proposed to be the same, retain an `equivalence_candidate` assertion until independently reviewed; never union-find them automatically from word similarity or screen proximity.

## Pencil, pen, and authority are different axes

- **PENCIL** = an explicitly speculative model state, including alternate worlds, analogies, sketches and assumptions. May contradict a different pencil branch. Moves in space are reversible and non-evidentiary. Pencil is not "false."
- **PEN** = a versioned **working commitment** by MOTIF or the human, bound to a scope and a cited derivation or explicit human assertion. Pen is not "absolute truth"; it can be challenged, superseded, or revoked through new entries.
- **Assertion status** = `suggested | examined | adopted | challenged | withdrawn`. Status and instrument are separate; a pencil claim is not automatically adopted.
- **Epistemic source class** = `human_statement | document_excerpt | computation | validated_fixture | learned_hypothesis | analogy | inference`. Source class is not an automatic reliability score.
- **Support/opposition** = explicit supporting/rebutting assertion or source IDs, with dependency roots preserved (do not count reposts as independent corroboration).
- **Authority** = separate from both pencil and pen: *no external action permission* inherits from a pen commitment. A pen output can be internally held as a scoped model result while an action remains `HOLD`. Real-world promotion/admission requires an independent policy check and, when appropriate, human review.

Suggested `promote(assertion_id, validation_context, actor)` gate:
1. Assertion exists and names resolvable identities; source/scope are retained.
2. Its typed premises are available; dependency roots and contradictory evidence checked.
3. For a theorem/computation: reproducible validator or explicit fixture evidence. For an empirical/semantic claim: source or human review; no automatic certainty from a model-derived drawing.
4. Attach the exact justification, validation version and counterexample search result (or `not_performed`).
5. Append `pen_committed` to immutable log; do **not** overwrite pencil history or retract contradictory witnesses.
6. Default `admission=HOLD`; later policy may enable clearly identified *internal-only* pen decisions without human sign-off. The policy must never silently authorize outside actions.

`uncommit()` appends a new `pen_superseded` or `pen_withdrawn` event. History remains reconstructible.

## Operations (typed; receipts for every mutation)

**Thought/identity:** `register_expression`, `propose_referent`, `register_concept`, `manifest`, `place`, `split_manifestation`, `fork_world`, `overlay_view`, `suggest_relation`, `compare_contexts`, `propose_equivalence`.

**Pencil:** `sketch`, `move_placement`, `branch`, `probe`, `critique`, `counterexample`, `retire_sketch`. All are bounded and reversible *through appended events*, rather than silently discarded.

**Pen:** `validate_assertion`, `commit`, `challenge`, `withdraw`, `reopen_as_pencil`, `snapshot`, `diff_snapshots`.

**Routing:** `select_lenses`, `score_lenses`, `run_parallel_views`, `propose_next_question`, `abstain`. All require a no-geometry alternative.

No `merge_concepts` side effect in the first vertical slice; identity consolidation is first **proposal + evidence + explicit review**, with reversible alias/redirect receipts rather than destructive deletion.

## Storage model and small API (stdlib-first; local-first)

Four append-only JSONL families, with canonical JSON, schema version and hashes for corruption detection (hashes do not prove an author or the truth of evidence):

```
events.jsonl       # event_id, parent_ids, actor, type, payload, clock, prev_digest
entities.json      # versioned Concepts, Expressions, Manifestations, Assertions
views.json         # View definitions, placements, geometry algorithm/version/seed
receipts.jsonl     # candidate, premises, opposing evidence, validator, disposition
```

The snapshot is a *derived cache*, not the authoritative history. Events should be deterministic given an explicit logical sequence number; do not assume wall-clock order proves causality. Idempotency keys prevent replay duplicates; replay verifies invariants. No user-supplied code execution, implicit network calls, or automatic remote uploads.

Candidate Python surface:

```python
field = ThoughtField.open_local(path)
expr = field.register_expression("home", source_ref="human:utterance-17")
field.propose_referent(expr.id, concept_id="c:home-shelter")
field.propose_referent(expr.id, concept_id="c:home-belonging")
a = field.manifest("c:home-shelter", context="logistics", instrument="PENCIL")
b = field.manifest("c:home-shelter", context="values", instrument="PENCIL")
maps = field.project(["dependency", "association", "tension", "flower_hex"],
                     allow_no_geometry=True)
field.suggest_relation(a.id, b.id, predicate="might_relate",
                       supporting_ids=[], status="suggested")
receipt = field.validate_and_commit(assertion_id, policy="internal_review_v1")
# committed working belief != verified world fact != external action permission
```

Public interchange: bounded JSON input / JSON result, with `schema_version`, `workspace_id`, identities, typed source/scope, requested reasoning phase, permissible lenses, explicit authority gate and an immutable `receipt_id`. Geometric SVG (and eventually an interactive viewer) is **optional output** of the same source state. The no-map CLI can compute the same typed reasoning results without any positions.

## Multiple simultaneous geometries

Each `View` stores `view_id`, `lens`, `input_snapshot_digest`, `placement_ids`, `layout_algorithm/version`, `seed`, `scale`, `meaning_of_distance`, `limitations`, `rendered_at_event`.

Initial lenses:
- **Association/spring:** explore shared edges, common neighbors and tentative clusters; similarity is a *task-specific question*, not a discovered truth.
- **Radial/dependency:** relative steps outward from an anchor; directed dependencies remain directed in the source graph.
- **Tension/contrast:** contradictory and incompatible claims; red disagreement connectors need supporting/rebutting witnesses.
- **Timeline/causal:** order and hypothetical transitions with explicit before/after provenance; spatial order does not prove cause.
- **Affordance:** what a candidate move could enable under declared synthetic rules; estimates are conditional.
- **Flower-of-Life/hex:** optional sixfold structural arrangement for alternative neighborhoods and symmetry experiments; *not evidence that meaning follows sacred geometry*.
- **NONE:** typed reasoning without a spatial projection, always available.

A concept's manifestations may have multiple placements with distinct IDs **in one or several views at once**. View movement updates placements only. Claims, identity and confidence are not recomputed from screen distance. To generate a new potential relation, use *typed evidence* from the source graph and clearly report the inferred rule; layout distance may only nominate a question for independent testing in a separately marked experimental policy.

## Thought cycle: not one draft/final pass

```
INPUT → abstract PENCIL → competing maps → question generation
     → test/compare/countermodel → scoped PEN working conclusion
     → concrete PENCIL plans/affordances → independent validation
     → scoped PEN decision or HOLD → new evidence → reopen pencil
```

At each phase MOTIF may select **zero, one, or several** views. A router records alternatives considered, reason for choosing each, compute cost, and expected/actual task benefit; avoid "I chose X because it looks good." Multiple maps can disagree without a requirement to fuse them. A different representation may expose a useful *question* that is then verified against the unchanged typed graph.

A recursive pen-to-pencil move is first class: adopted commitments may become assumptions inside a new sandbox but retain their source, confidence limitations, objections and revocation lineage.

## Implementation sequence (separate PRs, each tests itself)

| Milestone | Concrete deliverable | Exit gate |
|---|---|---|
| **THOUGHT-006: Pencil/Pen ledger** | Typed assertions, revision-safe append-only events, working commitments, objections and immutable receipts; adapter from GEOM-005 Node/Edge | Can sketch, promote under stated policy, challenge and undo by supersession; replay deterministic; unverified claim cannot become pen by layout alone |
| **THOUGHT-007: Non-fungible thought instances** | Concepts vs Expressions vs Manifestations vs Placements; ambiguity/equivalence proposals; split/overlay operations | One word can refer to several concepts; one concept has simultaneous non-fungible appearances; no automatic merger; IDs stable under reprojection |
| **THOUGHT-008: Multi-view field** | At least association, dependency, contradiction, optional hex and NONE views from one immutable snapshot; SVG + JSON diff | Changing view/coordinates leaves identities, edge semantics and pen state **bit-for-bit invariant** |
| **THOUGHT-009: Metareasoner / cycles** | Route/select zero-to-many views by task, revisit pencil after pen, preserve alternatives, attach explanation and budgets | Matched no-map and single-map baselines; frozen holdouts; report improvement **or failure** and cost |
| **THOUGHT-010: Integration doorway** | Versioned local JSON protocol and bounded adapters for existing thought_space and a hypothetical JAR;VIS/Free Graph interface; receipts + access controls | Offline/preview first; no remote writes or live third-party authority; explicit human opt-in before any real connector crossing |

**Stacking rule.** Keep this RFC as a docs-only child of GEOM-005 (currently open, not merged). Each milestone should branch from the preceding reviewed milestone, with CI/test evidence and no forced merge of other experimental families. There are already many independent open MOTIF branch families; do not silently import them.

## Concrete first demonstration: "home"

A source expression `home` creates **two proposed referents**: shelter, belonging. Another `home` in a different context might resolve to a project goal; it is not automatically the same referent. In one thought cycle:
1. Sketch two concept interpretations in PENCIL; generate logistics and emotional association maps.
2. Give `home-as-shelter` two distinct manifestations: resource requirement and relational value. Both may be positioned twice on screen.
3. A relation candidate suggests shelter may enable belonging. Preserve as `suggested` unless a supporting witness/reason is present.
4. Test contradictory evidence, show an alternate map where the association is absent.
5. Commit only a *scoped* conclusion like "this project currently defines home as physical shelter for this specific logistical task," with its authored source and an independent validation/review receipt. Not "home is shelter" universally.
6. A concrete planning pencil may use that scoped conclusion as an assumption; withdrawing it flags downstream plans as needing revalidation.

## Adversarial fixtures and acceptance tests

- **Nonfungibility:** duplicate label with different referents does not unify; one referent with 3 manifestations in 4 views keeps independent placement IDs; deleting one placement never deletes its concept.
- **Non-evidentiary geometry:** swapping spring and hex layouts does not change recorded assertions, commitment status, typed routes or confidence; no pen promotion by proximity.
- **Epistemic discipline:** a sketched assertion with no sources cannot auto-commit under strict policy; contradictory evidence remains visible; pen supersession preserves prior trace; no external authority from pen.
- **Provenance:** multiple echoes from same upstream root do not count as independent support; source metadata is treated as a claim until independently authenticated.
- **Replay:** fresh replay and incremental replay yield identical semantic snapshots; duplicate event IDs refused; tampered hashes detected as integrity faults, not proof of malicious authorship.
- **Router:** no-map baseline is always runnable; deterministic task under fixed seed/budget; can choose several lenses; trace records rejected layouts, observed score and outcome.
- **Security:** invalid references fail closed; arbitrary input sizes bounded; display escapes labels; private notes are local-only; no remote calls or PII in exported demo fixtures.
- **Causality:** causal arrows need explicit predicates and support; geometrical positions or closeness never create causal facts.
- **Regression:** GEOM-005's 16 existing tests continue unchanged; no mutation of its source graph from a suggested bridge; old CLI contracts preserved or versioned.

## Scientific trial (before claiming improvement)

Freeze a held-out suite of relational problems *before* adapting routing heuristics: ambiguous words, conflicting witness claims, missing dependency links, misleadingly close concepts, two context-dependent placements, and one task where **no geometry helps**. Independently specify correct answers/acceptable abstentions. Compare with the same observations and compute budget:

1. GEOM-005 source graph + no layout + BFS/common-neighbor.
2. Single fixed spring projection.
3. Single fixed hex projection.
4. Multi-view without pencil/pen ledger.
5. Full ledger + multiple views + router.

Measure relation precision/recall **against separately judged fixtures**, incorrect pen commitments per case, abstention calibration, quality of next questions (expected vs realized information gain), latency/memory cost, replay correctness and source-root independence. Add view-swap invariance and blind conflict fixtures. Do not optimize on held-out outcomes after looking; distinguish development vs independent tests.

**Mandatory acceptance:** no geometrically generated fact/identity/authorization, zero silent pen-promotion paths in strict-policy adversarial tests, stable provenance and replay, and honest comparison including negative findings. A useful router should beat no-map on *some predefined tasks* without increasing bad commitments; if it does not, the default should remain NONE or single-view.

## Integration boundaries / future capability doors

- **GEOM-005:** adapt existing Node/Edge without reinterpreting `observed=True` as verified ground truth; current origin IDs are unauthenticated labels.
- **Reason cartridges / Dogram:** optionally receive a structured reasoning method as a *proposal*, with pinned source and local validation. Never call a shared-name project by assuming interface compatibility.
- **Free Graph:** future typed graph read/import/export with IDs and provenance; no undocumented direct writes.
- **ALEX/3rdi:** future research/evidence packet *references* for claim validation; evidence package != independent truth.
- **planZ / affordance frontier:** consume committed scoped premises as conditional planning assumptions, forward withdrawal notifications; never equate plan with execution.
- **GRAFT/CANNON:** potential code synthesis/verification door only after capability handshake, tests, explicit human approval and sandbox restrictions.
- **JAR;VIS:** human-first optional thought-map control ("Sketch this", "Commit a working conclusion", "Show other interpretations") without making users complete worksheets, and with permissioned storage only.

**Non-goals for this plan:** autonomous consciousness, newly verified world facts from word geometry, unrestricted memory ingestion, web browsing or live permissions, unreviewed concept merges, a single universal ontology, real-time multiuser synchronization, and a compulsory visualization.

## The first hammer strike

Implement **THOUGHT-006** as a small, vertical, *independently testable* `experiments/thought-006/` package with `schema.py`, `ledger.py`, `promote.py`, `demo.py`, `test_ledger.py`, `DESIGN.md`, a frozen sample JSON and a CI job. Write one real end-to-end synthetic test: sketch association -> expose counterexample -> decline promotion -> add independent source -> issue scoped pen -> withdraw -> replay and compare snapshots. Only after that implement identity/multiplicity in THOUGHT-007. **Do not turn this RFC into an assertion that the code already exists.**
