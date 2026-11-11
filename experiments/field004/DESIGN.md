# FIELD-004 — THE UNSAID MOVE
## Autonomous reframing before conversational clarification

**Question:** Can a real-world helper rediscover the useful *unstated* reframes a skilled person might add after two or three dialogue turns, using only an initial goal and a set of images?

**What is implemented:** An evidence-preserving, rule-guided transformation engine with a typed photo/sketch observation interface. It proposes role reassignment (installed fence as possible inventory), environmental supports, networked panel assembly, shorter boundaries, and safety questions *without waiting for user hints*. A separate, explicitly opt-in Responses API adapter can present private photos to a multimodal model and validate the returned schema. Mocked model tests cover adapter plumbing; **no real-model image ingestion has been executed or validated**.

## Three different accomplishments; never conflate them

1. **Design rule:** We have encoded the specific reasoning move learned from the conversation as portable *hypothesis generators*. This is hand-authored knowledge, not a learned latent capability.
2. **Synthetic replay:** The rules generate these options from an anonymized evidence packet in zero conversational turns. The fixture was authored after seeing the example; it is **not independent or blind**.
3. **Future model test:** A multimodal intake could turn fresh, unseen photos into evidence packets with the same schema, but recognition quality, transfer to unprompted tasks and real-world feasibility are unproven.

## Evidence boundary

```
Human goal + photos/sketch
     |
  Perception adapter (local human observations OR optional consent-based model)
     |
  Attributed observation packet: observation / tentative interpretation
     |
  Separate current arrangement from intended boundary (hypothesis)
     |
  Role/function decomposition: rigid barrier, connection, support, access
     |
  Counterfactual operators:
     MOVE(existing segment)          [conditional on permission and physics]
     REUSE(old cage panel)           [conditional on physical suitability]
     JOIN(panel,panel)               [connection required; does not prove stability]
     ANCHOR(panel,existing object)   [candidate only; require check]
     SHIFT(goal boundary)            [conditional on permitted dog zone]
     |
  Several candidate strategies with explicit blocking assumptions
     |
  Highest-consequence observation/probe, not an automatic build
```

The diagram is an *explainable algorithm description*, not a model's hidden private reasoning.

## Synthetic result: first pass with no user's later correction

`fixtures/anonymous_visual_packet.json` contains generic observations for an abstract boundary task: a dotted intended line on a sketch, existing chain link, cage panels, a large frame, structures, mesh and an access route. This is an **anonymized representation**, not the private photographs or a survey of the actual yard.

Command:

```sh
cd experiments/field004
python -m unittest discover -v
python run.py --packet fixtures/anonymous_visual_packet.json > /tmp/field004.json
```

With zero follow-up user messages the **authored rules** already generate the five key concepts: treating dotted marks as a possible target, examining installed fence as movable inventory, exploring environmental support, testing mutual panel support, and considering rerouting the boundary. They do not guess tie strength, movement permission, measurements or a safe enclosure.

With a separate, *source-attributed user correction*, a later run could mark relocation permission and connector availability YES without changing the rule library. That changes missing checks, not pet-safety approval.

## Optional photo run (NOT performed in this experiment)

The optional adapter uses the standard Responses API image data URI form, validated at development time against the public OpenAI documentation. Requires an OpenAI API key and optional installed SDK, and sends the **actual photos off device only if the operator chooses the explicit opt-in flag**. No images or model transcripts are committed.

```sh
python run.py --photos /private/path/sketch.jpg /private/path/material.jpg \
  --goal 'Make a low-cost boundary from existing materials' \
  --model gpt-4.1-mini --consent-send-images
```

The program refuses transmission by default. API calls can cost money. A truly local model can implement the same `ingest_photos`/evidence contract without changing the planner. **One run does not verify correctness.** In an independent test, compare the visual packet against blind human labels before scoring hypothesis novelty.

## Baselines and next evaluation

Freeze 20+ unseen tasks with different materials, locations and *non-fencing* goals. Compare against (a) generic material inventory, (b) direct LLM answer, (c) rule engine + perception, and (d) matched-budget human brainstorming. Measure:

- coverage and usefulness of latent reframes without a user suggesting them;
- false assumptions about ownership, mobility, geometry, structural strength or safety;
- correctly attributed observations vs imagined facts;
- time/turn count and cost;
- whether field observations falsify the first plan and lead to a better next option.

The next conceptual engine improvement is a **general typed affordance grammar**, rather than the presently narrow boundary-focused rules. Connect with MOTIF-003 affordance frontier and QC-010 traction loop only by reviewed source-pinned adapters; those experiments are on separate unmerged branches.

## Safety and privacy limits

No photos are committed or bundled; only generic synthetic descriptions. A 200-lb tensile rating on a tie does not certify a dog fence joint or its anti-tip behavior. Trampoline frames and chairs might supply geometry but are not verified anchors. Loose mesh and exposed cage wires may entangle or injure pets. The program does not approve unsupervised dog use and executes no physical action. Actual permission, stable anchoring, safe aperture/ground-gap checks and traffic separation are independent requirements.