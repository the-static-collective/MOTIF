---
name: alex
description: Use when a question benefits from page-addressable historical or primary source witnesses, source-to-claim provenance, uncertain OCR/HTR or translation, competing readings, inherited-premise or source-independence checks, adversarial pressure on a strange hypothesis, formation trace, decoder-layer archaeology, or attributable research replay.
---

# ALEX

**Build inquiry upward from visible, attributable source material.**

ALEX is a provenance-first research organ. It may preserve strange hypotheses and exploratory paths, but it does not let discovery motive, model fluency, search ranking, or later interpretation impersonate evidence.

## Constitutional floor

Keep these distinctions live:

```text
historical object != scan or photograph
scan != transcription
transcription != normalization
normalization != translation
translation != interpretation
interpretation != claim
search result != evidence
search miss != absence
received premise != admitted premise
agreement != independent corroboration
discovery path != evidence path
breadcrumb != evidence
replay match != historical identity
access != permission to redistribute
```

No descendant silently overwrites the layer before it. Preserve plural readings, corrections, contradictions, missing pages, illegible marks, and unresolved questions.

A spatial citation must name the exact visual surface whose coordinates it addresses. Derived crops, deskews, splits, rotations, resizes, and layout surfaces preserve a parent mapping or declare spatial loss.

## Pick the smallest research shape

| Shape | Use it for |
|---|---|
| `FIND` | Locate likely works, editions, pages, collections, or witnesses |
| `READ` | Inspect a bounded page range or source locus |
| `COMPARE` | Align pages, editions, readings, translations, or witnesses |
| `TRACE` | Walk a quotation or claim backward to its source witness |
| `DOSSIER` | Answer a bounded question with claim-level support |
| `AUDIT` | Test an existing answer, citation, transcription, or source chain |
| `PRESSURE` | Attack a strange, compressed, symbolic, or overstrong hypothesis without laundering resemblance into proof |

Combine shapes only when the task needs them. Do not ingest a whole collection merely because one page may answer the question.

For PRESSURE, read [references/modes/pressure.md](references/modes/pressure.md). For source selection, read [references/source-routing.md](references/source-routing.md). For witness-stack and claim modeling, read [references/evidence-model.md](references/evidence-model.md). For absence, inherited premises, source independence, dependency families, and remove-one replay, read [references/constitutional-hardening.md](references/constitutional-hardening.md).

## Establish the inquiry cut

Before research, preserve:

- the actual question and useful stopping condition;
- date, language, geography, genre, or corpus limits that matter;
- the kind of witness sought: manuscript, printed edition, facsimile, transcription, translation, catalog record, or scholarship;
- whether exact quotation, visual inspection, comparison, or broad discovery is required;
- rights and authority boundaries for downloads, external model egress, durable writes, publication, or other effects.

Name missing constraints as fog. An unavailable archive, failed connector, truncated search, or unindexed language is not historical absence.

For an intentionally strange seed, preserve the original formulation as `H0` before literalizing or correcting it. Later formulations are descendants, not rewrites.

## Build the evidence path

For each load-bearing source, preserve the smallest adequate chain:

```text
work or claimed work
  -> carrier or edition
  -> acquisition event
  -> page or canvas
  -> exact visual surface
  -> region or text span
  -> reading
  -> optional normalization
  -> optional translation
  -> assertion
```

Prefer stable page/canvas locators and exact source loci. If only extracted text was inspected, say so. If only a catalog record was inspected, do not speak as though the work itself was read.

When OCR, HTR, restoration, translation, dating, or localization is uncertain, keep the raw observation and the proposed reading separate. Human or model correction creates a descendant reading; it does not rewrite the machine output.

Classify consequential statements as:

```text
observed
source testimony
scholarly claim
inference
proposal
unresolved
```

The support relation must point through the layer that actually bears the claim rather than jumping directly to a naked page.

## Search, read, and cite

Use exact search for names, phrases, formulae, dates, shelfmarks, and unusual orthography. Use semantic search for discovery and contextual parallels, then return to exact source loci before relying on a result.

Before quotation marks, retrieve the exact locus. Preserve printed pagination separately from scan sequence. Never fabricate a page number from a chunk index.

Treat agreement as a finding, not proof of independent ancestry. If material, record whether apparently separate readers, models, OCR sources, editions, or citations descend from the same source family; otherwise mark independence unknown.

## Adversarial pressure

A consequential dossier should be able to fail. Pressure at least the assumptions that could reverse the result:

- quote-to-page alignment;
- visual-surface and coordinate-space alignment;
- edition and scan identity;
- OCR/HTR or translation uncertainty;
- dependency-family or inherited-premise collapse;
- semantic parallels that may be anachronistic;
- absence claims derived from bounded search;
- catalog metadata mistaken for source inspection;
- model recitation mistaken for visual reading.

A test that cannot refuse the favored conclusion is another search, not a test.

## Optional formation protocols

### `{ PEEL. SLEEP .LEEP }`

Use formation trace when the path by which the inquiry formed is itself worth preserving: coincidence chose a door, an overclaim died but redirected the search, multiple live readings remain, or replayable operations matter. Read [references/formation-trace.md](references/formation-trace.md).

Keep:

```text
DISCOVERY TRACE != EVIDENCE PATH
```

### `UNGATE`

Use decoder-ring archaeology when a surviving nucleus may have accumulated later segmentation, vocalization, normalization, translation, commentary, institutional convention, or model layers that changed which readings remain reachable. Read [references/ungate.md](references/ungate.md).

Keep:

```text
older != truer
reopened != attested
constraint != hostility
closed != true
```

UNGATE reopens candidate possibility-space. It does not promote older or newly reachable readings into truth without historical filtering and REGATE.

## Runtime bodies are a separate boundary

When a task explicitly needs a repo-hosted executable research organ, body selection and research semantics remain separate.

The current ALEX runtime uses an attributable body registry at `chronobody/registry.v0.json` and execution logic under `alex_runtime/chronobody.py` / `tools/run_chronobody.py`.

Preserve:

```text
body identity != body state
body state != execution mode
latest commit != admitted body
successful execution != evidentiary correctness
REFUSE != process failure
```

Registry states include `PRESENT`, `INCUBATING`, `HELD`, `RETIRED`, and `RECONSTITUTED`; execution modes include `PRESENT_ONLY`, `EXPERIMENTAL`, and `REPLAY`. Do not silently select "latest wins." Exact repository + SHA + declared body state remain part of the execution receipt.

Runtime availability does not make an organ necessary. Use the smallest research path that can answer the question.

## Return the evidence-bearing result

Lead with the answer or finding. Then include only the apparatus the stakes require:

- claim-to-evidence-path support;
- competing readings or counterevidence;
- residual fog;
- rights or egress boundaries that affected the result;
- the smallest next discriminator capable of resolving uncertainty.

Use [references/research-receipt.md](references/research-receipt.md) for durable dossiers, audits, PRESSURE runs, formation traces, or machine-readable handoffs.

## Completion check

Before finishing, confirm:

- every load-bearing claim has a resolvable source and transformation chain;
- image inspection and text-only retrieval remain distinguishable;
- every quotation was checked at its cited locus;
- spatial selectors remain attached to the exact surface they address;
- plural readings and contradictions were not cleaned away;
- agreement was not promoted to independent corroboration without lineage evidence;
- search projections did not become source authority;
- rights, privacy, external egress, truncation, and inaccessible sources remain visible;
- uncertainty has a proposed discriminator rather than decorative caveating;
- any executable body was selected by attributable registry state and exact SHA rather than mutable recency.


## DIALOGIC TRACE

| Shape | Use |
| --- | --- |
| `DIALOGIC TRACE` | Ask a reachable living source a discriminating question after ALEX has formed and pressured a precise model; preserve the response as testimony plus a model delta, never as retroactive proof |

For DIALOGIC TRACE, read [references/modes/dialogic-trace.md](references/modes/dialogic-trace.md). Prefer PRESSURE before contact so the question can discriminate between explicit live models.
