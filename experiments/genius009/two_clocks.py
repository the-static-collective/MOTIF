"""MOTIF-GENIUS-009: TWO CLOCKS, ONE RECORD.

Investigate an unusual crossing:
    Enochic source stratification × Nolan presentation time ×
    Acaster reinterpretive callback × Bacon provenance audit ×
    Aquinas source-bounded objections.

A later witness can change how an earlier statement is *read* without
changing what the earlier source *said*. Keep source chronology and
reader revelation chronology separate; attach reinterpretation as an
explicit later annotation, never as an earlier quote or observation.

This is a transparent append-only event-log algorithm, not novel math,
evidence of revelation, human cognitive modeling or history verification.
All exercise corpora are engineered examples with illustrative dates.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
import json
from typing import Optional

LANES = ("TEXT_TRADITION", "NARRATIVE_FICTION", "EMPIRICAL_INSTRUMENT")
POLARITIES = ("AFFIRM", "DENY", "UNCERTAIN")


@dataclass(frozen=True)
class Assertion:
    proposition: str
    polarity: str = "AFFIRM"


@dataclass(frozen=True)
class Witness:
    witness_id: str
    layer: int                # source order within a declared corpus, not a CE date
    lane: str
    assertions: tuple[Assertion, ...]
    evidence_ref: str        # external verification of the pointer NOT attempted


@dataclass(frozen=True)
class Reading:
    """An interpretation offered in a later record ABOUT an earlier record.

    This is NOT an assertion that the earlier witness contained the later
    words, and does not modify the historical/source-owned assertions.
    """
    reading_id: str
    later_witness_id: str
    earlier_witness_id: str
    new_interpretation: str
    relevant_proposition: str
    certainty: str = "INTERPRETATION_NOT_TESTIMONY"


@dataclass(frozen=True)
class Corpus:
    corpus_id: str
    witnesses: tuple[Witness, ...]
    readings: tuple[Reading, ...]


def validate(corpus: Corpus) -> None:
    if not corpus.corpus_id or not corpus.witnesses:
        raise ValueError("Corpus identity and witnesses required")
    ids = [w.witness_id for w in corpus.witnesses]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        raise ValueError("Witness IDs must be unique and nonempty")
    layers = [w.layer for w in corpus.witnesses]
    if any(type(x) is not int or x < 0 for x in layers):
        raise ValueError("Layers must be nonnegative finite chronology indices")
    index = {w.witness_id: w for w in corpus.witnesses}
    for w in corpus.witnesses:
        if w.lane not in LANES or not w.evidence_ref:
            raise ValueError("Explicit lane and source pointer required")
        if not w.assertions:
            raise ValueError("Witness must have at least one explicit source assertion")
        names = [a.proposition for a in w.assertions]
        if len(set(names)) != len(names):
            raise ValueError("Repeated proposition within a witness")
        if any(not a.proposition or a.polarity not in POLARITIES for a in w.assertions):
            raise ValueError("Invalid source assertion")
    reading_ids = [r.reading_id for r in corpus.readings]
    if len(set(reading_ids)) != len(reading_ids):
        raise ValueError("Reading identities must be unique")
    for r in corpus.readings:
        a = index.get(r.earlier_witness_id)
        b = index.get(r.later_witness_id)
        if (a is None or b is None
            or not r.reading_id or not r.relevant_proposition or not r.new_interpretation
            or r.certainty != "INTERPRETATION_NOT_TESTIMONY"):
            raise ValueError("Unsupported provenance / interpretation metadata")
        if b.layer <= a.layer:
            raise ValueError("A later reading must refer to an earlier source layer")
        if b.lane != a.lane:
            raise ValueError("No silent promotion across epistemic lanes")
        if r.relevant_proposition not in [x.proposition for x in b.assertions]:
            raise ValueError("Interpretation must be grounded in a later explicit witness proposition")


def _literal_receipts(w: Witness) -> list[dict]:
    return [
        {"owner": w.witness_id, "layer": w.layer, "lane": w.lane,
         "proposition": x.proposition, "polarity": x.polarity,
         "source": w.evidence_ref, "certainty": "EXPLICIT_IN_THIS_WITNESS_ONLY"}
        for x in w.assertions
    ]


def compose_readings(corpus: Corpus, disclosure_order: tuple[str, ...]) -> dict:
    """Run an audience reading in any presentation order.

    The reveal order can differ from source order. Readings activate only
    after BOTH participating witnesses have been seen. The later source
    may *reinterpret* earlier material but cannot backdate its assertions.
    """
    validate(corpus)
    ids = tuple(w.witness_id for w in corpus.witnesses)
    if len(disclosure_order) != len(ids) or set(disclosure_order) != set(ids):
        raise ValueError("Disclosure order must contain each witness exactly once")
    witness_by_id = {w.witness_id: w for w in corpus.witnesses}
    seen: set[str] = set()
    activated: set[str] = set()
    snapshots = []
    for reveal_index, witness_id in enumerate(disclosure_order):
        seen.add(witness_id)
        present = sorted((witness_by_id[i] for i in seen),
                         key=lambda w: (w.layer, w.witness_id))
        activated_now = []
        for reading in corpus.readings:
            if (reading.reading_id not in activated and
                reading.later_witness_id in seen and
                reading.earlier_witness_id in seen):
                activated.add(reading.reading_id)
                activated_now.append({
                    "reading_id": reading.reading_id,
                    "about_earlier": reading.earlier_witness_id,
                    "from_later": reading.later_witness_id,
                    "interpretation": reading.new_interpretation,
                    "grounded_in_later_claim": reading.relevant_proposition,
                    "status": reading.certainty,
                })
        snapshots.append({
            "reveal_index": reveal_index,
            "new_witness": witness_id,
            "reader_knows_sources": sorted(seen),
            "literal_claims_visible": [
                rec for w in present for rec in _literal_receipts(w)
            ],
            "new_reader_reinterpretations": activated_now,
            "source_histories_never_edited": True,
        })
    all_receipts = [
        rec for w in sorted(corpus.witnesses,
                            key=lambda w: (w.layer, w.witness_id))
        for rec in _literal_receipts(w)
    ]
    all_readings = sorted(
        (r for snapshot in snapshots
         for r in snapshot["new_reader_reinterpretations"]),
        key=lambda r: r["reading_id"],
    )
    return {
        "status": "SOURCE_AND_READER_CLOCKS_SEPARATED",
        "corpus": corpus.corpus_id,
        "disclosure_order": list(disclosure_order),
        "source_order": [
            w.witness_id for w in sorted(corpus.witnesses,
                                         key=lambda w: (w.layer, w.witness_id))
        ],
        "snapshots": snapshots,
        "final_source_attributions": all_receipts,
        "final_reinterpretations": all_readings,
        "no_external_action": True,
        "no_historical_or_religious_facts_verified": True,
    }


def check_attribution(corpus: Corpus, proposition: str,
                      claimed_source: str, latest_source_layer: Optional[int] = None) -> dict:
    """Aquinas-style objection receipt against a disputed source attribution."""
    validate(corpus)
    index = {w.witness_id: w for w in corpus.witnesses}
    if claimed_source not in index:
        return {"status": "HOLD_UNKNOWN_SOURCE", "proposition": proposition,
                "source": claimed_source}
    w = index[claimed_source]
    if latest_source_layer is not None and w.layer > latest_source_layer:
        return {
            "status": "HOLD_SOURCE_OUTSIDE_REQUESTED_LAYER",
            "proposition": proposition,
            "source": claimed_source, "requested_max_layer": latest_source_layer,
        }
    own_claim = next((a for a in w.assertions if a.proposition == proposition), None)
    later = sorted(
        (other for other in corpus.witnesses
         if other.layer > w.layer and
         any(a.proposition == proposition and a.polarity == "AFFIRM"
             for a in other.assertions)),
        key=lambda x: x.layer,
    )
    return {
        "status": "EXPLICIT_SOURCE_ATTESTATION" if own_claim else
                  "HOLD_UNSUPPORTED_RETROJECTION",
        "source": claimed_source,
        "source_layer": w.layer,
        "proposition": proposition,
        "source_polairty": own_claim.polarity if own_claim else None,
        "source_evidence_ref": w.evidence_ref,
        "later_witnesses_with_explicit_affirmation": [
            {"source": other.witness_id, "layer": other.layer,
             "evidence_ref": other.evidence_ref}
            for other in later
        ],
        "objection": "A later witness need not be a direct statement of the earlier witness.",
        "reply": "Keep each assertion attached to its actual source and era.",
        "no_theological_or_historical_certification": True,
    }


def naive_flatten(corpus: Corpus) -> dict:
    """Intentionally weak control: falsely copy later claims into earlier source.

    This is a deliberate failure comparator, NOT a strong scholarly baseline.
    """
    validate(corpus)
    by_id = {w.witness_id: {a.proposition for a in w.assertions}
             for w in corpus.witnesses}
    for r in corpus.readings:
        by_id[r.earlier_witness_id].add(r.relevant_proposition)
    original = {w.witness_id: {a.proposition for a in w.assertions}
                for w in corpus.witnesses}
    false_attributions = {
        w.witness_id: sorted(by_id[w.witness_id] - original[w.witness_id])
        for w in corpus.witnesses
        if by_id[w.witness_id] != original[w.witness_id]
    }
    return {
        "method": "INTENTIONALLY_BAD_FLATTEN_LATER_MEANING_INTO_OLDER_TESTIMONY",
        "false_attributions": false_attributions,
        "false_attribution_count": sum(len(v) for v in false_attributions.values()),
    }


def plain_append_only(corpus: Corpus) -> dict:
    """A strong *classical* typed append-only source ledger: no innovation."""
    validate(corpus)
    source_claims = {
        w.witness_id: tuple(a.proposition for a in w.assertions)
        for w in corpus.witnesses
    }
    return {"source_claims": source_claims,
            "false_attribution_count": 0,
            "limitation": "Correct source retention without temporal reader model"}


def _c(wid: str, layer: int, lane: str, claim: str) -> Witness:
    return Witness(wid, layer, lane, (Assertion(claim),),
                   f"curated-synthetic:{wid}")


def fixtures() -> tuple[Corpus, ...]:
    """Three unrelated source domains; all authored for this experiment."""
    enoch = Corpus(
        "enochic-illustrative-layering",
        (
            _c("Genesis5", 0, "TEXT_TRADITION", "Enoch walks with God"),
            _c("1Enoch", 1, "TEXT_TRADITION", "Enochic visionary testimony"),
            _c("3Enoch", 3, "TEXT_TRADITION", "Enoch-Metatron identification"),
        ),
        (Reading("later_enochic_association", "3Enoch", "Genesis5",
                 "Read the Genesis Enoch figure through a later Metatron tradition",
                 "Enoch-Metatron identification"),),
    )
    narrative = Corpus(
        "fictional-callback-double-time",
        (
            _c("scene_first", 0, "NARRATIVE_FICTION", "A blue key is ordinary"),
            _c("scene_second", 1, "NARRATIVE_FICTION", "A cupboard is sealed"),
            _c("scene_final", 2, "NARRATIVE_FICTION", "The blue key opens a shared cupboard"),
        ),
        (Reading("revealed_key_purpose", "scene_final", "scene_first",
                 "The earlier key can now be read as a clue to cooperation",
                 "The blue key opens a shared cupboard"),),
    )
    science = Corpus(
        "hypothetical-instrument-reinterpretation",
        (
            _c("sensor_t0", 0, "EMPIRICAL_INSTRUMENT", "Instrument reading was 12"),
            _c("lab_t1", 1, "EMPIRICAL_INSTRUMENT", "Reference sample remained at 9"),
            _c("calibration_t2", 2, "EMPIRICAL_INSTRUMENT", "Calibration offset was 3"),
        ),
        (Reading("later_calibration", "calibration_t2", "sensor_t0",
                 "Later calibration suggests subtracting an offset from the original number",
                 "Calibration offset was 3"),),
    )
    for corpus in (enoch, narrative, science):
        validate(corpus)
    return enoch, narrative, science


def run() -> dict:
    """All 3! possible reader orders for each of three distinct domains."""
    report = {}
    for corpus in fixtures():
        run_orders = [
            compose_readings(corpus, tuple(order))
            for order in permutations(w.witness_id for w in corpus.witnesses)
        ]
        source_ledger_signatures = {
            json.dumps(r["final_source_attributions"], sort_keys=True)
            for r in run_orders
        }
        interpretation_signatures = {
            json.dumps(r["final_reinterpretations"], sort_keys=True)
            for r in run_orders
        }
        if len(source_ledger_signatures) != 1 or len(interpretation_signatures) != 1:
            raise AssertionError("Reordering disclosures changed source attribution")
        control = naive_flatten(corpus)
        append_only = plain_append_only(corpus)
        report[corpus.corpus_id] = {
            "presentations_evaluated": len(run_orders),
            "source_record_invariant_under_reordering": True,
            "final_reader_reinterpretations_invariant": True,
            "weak_flatten_false_attributions": control["false_attribution_count"],
            "strong_classical_append_only_false_attributions":
                append_only["false_attribution_count"],
            "two_clock_false_attributions": 0,  # by source ledger construction
            "example_chronological": run_orders[0],
            "example_reverse": run_orders[-1],
        }
    first = fixtures()[0]
    return {
        "status": "RESEARCH_HOLD_SYNTHETIC_INTERPRETATION_EXPERIMENT",
        "experiment": "GENIUS-009",
        "worlds": report,
        "textual_attribution_challenge": check_attribution(
            first, "Enoch-Metatron identification", "Genesis5", 0
        ),
        "positive_later_attribution": check_attribution(
            first, "Enoch-Metatron identification", "3Enoch", 3
        ),
        "classical_ledger_baseline_is_equally_source_correct": True,
        "not_new_math_or_empirical_research": True,
        "no_external_action": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
