# MOTIF-026 — From human-approved *enough* to operator-authorized local work

MOTIF-025 can prepare exactly two domain-specific completion criteria and one typed alternative, but confirmation alone does not produce useful materials. The next step is a **separate, narrower capability grant**: `PREPARE_LOCAL_PACKET_ONLY`.

`experiments/026/prepare_work.py` **recomputes** the person's current MOTIF-025 contract from their text/choice/custom example and checks its exact SHA-256 `expected_contract_id`. It accepts no hand-supplied "confirmed goal" document. A second explicit `consent:true` and exact `action:"PREPARE_LOCAL_PACKET_ONLY"` is required. Mismatched and older hashes HOLD.

The result is a typed, bounded recipe for four local operator artifacts: an actionable checklist, a CSV tracker, an **unsent** contact draft and an HTML work page. Domain cartridges cover coffee donation, volunteers, events, local food exchange, website implementation and research, with a conservative generic fallback. The source-owned completion wording is preserved; arbitrary typed criteria are explicitly **HUMAN_TYPED_UNINTERPRETED**, not verified or implicitly delegated to an AI.

The source kernel **does not create files, contact donors, run public source queries, submit forms, request external credentials, record anything persistently, or claim success**. JAR;VIS must independently render the recipe into browser-downloadable local files, with a further explicit click for each download. There is no money/credit cost; electrical energy is unknown, never fabricated. No permission to perform real-world work follows from a local packet grant.

Example: Coffee donation for the fellowship produces a donor-contact tracker, pickup/quantity checklist, an unsent polite solicitation template, and a one-page printable work sheet. All contact and commitment fields are blank. Nothing is represented as an existing donation.

Reproduce from repo root:
```
python3 -m unittest discover -s experiments/026 -p test_*.py -v
printf '%s' '{"text":"Can we get free coffee donated for our fellowship event?","choice":"a","expected_contract_id":"<digest-from-025>","consent":true,"action":"PREPARE_LOCAL_PACKET_ONLY"}' | python3 experiments/026/prepare_work.py
```
The deliberately separate action is a test of a capability boundary, not proof that people would find the produced work packet useful. Follow-up human verification must compare time to actual task completion, donor/volunteer consent and factual proof versus the stated definition of done.
