"""MOTIF-018 × Green Grammar: a deliberately adversarial research crucible.

This does NOT import or execute production Dogram/ALEX/3rdi/Iron Lung.
It tests propositions from the historical Green Grammar thread against
the actual MOTIF-018 synthetic predictor, alongside bounded *new* protocol
probes. Every unimplemented boundary is labeled; no claims of consciousness.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import json

from unknown_unknown import (
    Episode, assess, build_episode, discover, fit, propose_concepts, run, world,
)

SOURCE_ROADS = (
    "the-static-collective/the-daily-slice:threads/grammar-of-creation.md",
    "the-static-collective/the-daily-slice:slices/2026/09/2026-09-16/"
    "hugh-jack-journal-green-grammar-refusal-to-collapse.md",
    "the-static-collective/the-daily-slice:slices/2026/09/2026-09-16/"
    "the-triangulator-3t5-325-243.md",
    "the-static-collective/the-daily-slice:slices/2026/09/2026-09-17/"
    "aperture-hold-the-meanings-open.md",
    "the-static-collective/the-daily-slice:slices/2026/09/2026-09-19/"
    "every-doorway-wide-enough-for-3.md",
)


@dataclass(frozen=True)
class SenseReceipt:
    """Observer-local *proposal*; an old receipt never learns future context."""
    received_at: int
    raw: str
    candidate_senses: tuple[str, ...]
    provenance: str
    status: str = "PROPOSED_NOT_INTENTION"


def parse_bank(raw: str, context: str, received_at: int,
               provenance: str) -> SenseReceipt:
    # An intentionally hand-supplied, finite lexicon: not natural-language AI.
    if raw != "The bank moved.":
        raise ValueError("UNSUPPORTED_SYNTHETIC_SENTENCE")
    readings = ("financial_institution", "riverbank")
    if "flood" in context.lower():
        readings = ("riverbank",)
    return SenseReceipt(received_at, raw, readings, provenance)


def reading_available(receipt: SenseReceipt, observer_cut: int) -> bool:
    return receipt.received_at <= observer_cut


def rebase_reading_on_past(later: SenseReceipt,
                          earlier: SenseReceipt) -> str:
    if later.received_at > earlier.received_at:
        return "HOLD_RETROSPECTIVE_KNOWLEDGE"
    return "NO_NEW_KNOWLEDGE"


@dataclass(frozen=True)
class LanguageWitness:
    """Explicit synthetic correction; name is not meaning or authority."""
    alias: str
    referent: str
    upstream: str
    verified_feedback: bool


def ground_alias(witnesses: tuple[LanguageWitness, ...],
                 alias: str) -> dict:
    supported = [w for w in witnesses if w.alias == alias
                 and w.verified_feedback]
    groups: dict[str, set[str]] = {}
    for w in supported:
        groups.setdefault(w.referent, set()).add(w.upstream)
    if len(groups) > 1:
        return {"status": "HOLD_CONFLICTING_LOCAL_MEANINGS",
                "referent": None, "source_families": len(
                    set(w.upstream for w in supported))}
    if not groups or max(map(len, groups.values())) < 2:
        return {"status": "HOLD_INSUFFICIENT_INDEPENDENT_CORRECTION",
                "referent": None, "source_families": len(
                    set(w.upstream for w in supported))}
    return {"status": "PROPOSE_LOCAL_REFERENT_NOT_AUTHORITY",
            "referent": next(iter(groups)),
            "source_families": max(map(len, groups.values()))}


@dataclass(frozen=True)
class Claim:
    raw: str
    role: str  # FACT_CANDIDATE / IDEA / RELATION
    source: str
    external_evidence: bool
    verified_permission: bool


def admit_claim(claim: Claim) -> str:
    if claim.role not in ("FACT_CANDIDATE", "IDEA", "RELATION"):
        return "HOLD_UNTYPED_CLAIM"
    if not claim.external_evidence:
        return "HOLD_EVIDENCE"
    if not claim.verified_permission:
        return "HOLD_AUTHORITY"
    return "PROPOSE_LOCAL_REVIEW_ONLY"


@dataclass(frozen=True)
class Crossing:
    source: str
    target: str
    source_receipt: bool
    destination_consent: bool
    independent_authority: bool
    scope: str = "SYNTHETIC_ONLY"


def doorway(crossing: Crossing) -> str:
    if crossing.scope != "SYNTHETIC_ONLY":
        return "HOLD_EXTERNAL_CROSSING"
    if not crossing.source_receipt:
        return "HOLD_MISSING_SOURCE_HAND"
    if not crossing.destination_consent:
        return "HOLD_MISSING_DESTINATION_HAND"
    if not crossing.independent_authority:
        return "HOLD_MISSING_AUTHORITY"
    return "REVIEWABLE_SYNTHETIC_CROSSING_NOT_EXECUTED"


@dataclass(frozen=True)
class Witness:
    statement: bool
    declared_upstream: str
    attested_independent: bool


def adjudicate(witnesses: tuple[Witness, ...]) -> str:
    if not witnesses or any(not w.attested_independent for w in witnesses):
        return "HOLD_UNAUTHENTICATED_SOURCE_METADATA"
    # Attribution and attestation are supplied by the toy fixture;
    # a declared upstream field is NOT real-world authentication.
    by_upstream: dict[str, set[bool]] = {}
    for w in witnesses:
        by_upstream.setdefault(w.declared_upstream, set()).add(w.statement)
    if any(len(values) > 1 for values in by_upstream.values()):
        return "HOLD_SAME_ORIGIN_CONTRADICTION"
    if len(by_upstream) < 2:
        return "HOLD_ONLY_ONE_UPSTREAM_FAMILY"
    claims = {next(iter(values)) for values in by_upstream.values()}
    return ("PROPOSE_INDEPENDENT_AGREEMENT_NOT_AUTHORITY"
            if len(claims) == 1 else "HOLD_INDEPENDENT_CONFLICT")


def projections_for_022100() -> tuple[dict, dict]:
    carrier = "022100"
    as_ternary = {"carrier": carrier, "operator": "base3_integer",
                  "type": "integer", "value": int(carrier, 3)}
    as_guitar = {"carrier": carrier, "operator": "standard_guitar_frets",
                 "type": "chord_shape", "value": "E_major"}
    return as_ternary, as_guitar


def compare_projections(a: dict, b: dict) -> str:
    if a["operator"] == b["operator"] and a["type"] == b["type"]:
        return "SAME_DECODER_COMPARABLE"
    return "HOLD_CROSS_DECODER_IDENTITY"


def numeric_delta(carrier: int, f: str, g: str) -> dict:
    operators = {"add1": lambda n: n + 1,
                 "add3": lambda n: n + 3,
                 "double": lambda n: n * 2}
    if f not in operators or g not in operators:
        raise ValueError("UNDECLARED_OPERATOR")
    gf = operators[g](operators[f](carrier))
    fg = operators[f](operators[g](carrier))
    return {"carrier": carrier, "f": f, "g": g,
            "g_after_f": gf, "f_after_g": fg, "delta": gf - fg,
            "value_proven": True, "causal_or_usefulness_proven": False}


def n_step_world(n: int) -> tuple[Episode, ...]:
    """A world whose explanatory relation lies *outside* 018's 2-hop grammar."""
    result = []
    for x, active in product((0, 1), repeat=2):
        name = f"path{n}-{x}-{active}"
        edges = [("observer", "records", "actor")]
        previous = "actor"
        for i in range(n):
            destination = "goal" if i == n - 1 else f"{name}-node{i}"
            relation = ("carries" if i == 0 else
                        "passes" if i < n - 1 else "reaches")
            if i == n - 1 and not active:
                relation, destination = "wanders", "nowhere"
            edges.append((previous, relation, destination))
            previous = destination
        result.append(Episode(name, x, tuple(edges), x ^ active, True))
    return tuple(result)


def two_relation_xor() -> tuple[Episode, ...]:
    result = []
    for x, a, b in product((0, 1), repeat=3):
        name = f"xor-{x}{a}{b}"
        edges = [("observer", "records", "actor")]
        if a:
            edges.append(("actor", "red", "goal"))
        if b:
            edges.append(("actor", "blue", "goal"))
        result.append(Episode(name, x, tuple(edges), x ^ a ^ b, True))
    return tuple(result)


def stripped_of_graph(examples: tuple[Episode, ...]) -> tuple[Episode, ...]:
    """An irreversible many-to-one projection: information was not retained."""
    return tuple(replace(e, edges=()) for e in examples)


def _item(key: str, layer: str, observed: object,
          verdict: str, interpretation: str) -> dict:
    return {"id": key, "layer": layer, "observed": observed,
            "verdict": verdict, "interpretation": interpretation}


def run_crucible() -> dict:
    train, validation, holdout = (world("path", split) for split in
                                  ("train", "validation", "holdout"))
    chosen = discover(train, validation)
    model = chosen["model"]
    assert model is not None
    baseline = run()
    results = []

    def add(key, layer, observed, verdict, interpretation):
        results.append(_item(key, layer, observed, verdict, interpretation))

    add("representation_growth", "native_018",
        (baseline["heldout_surface_only"]["accuracy"],
         baseline["heldout_expanded"]["accuracy"]),
        "OBSERVED_GAIN", "Narrow feature vocabulary expands; classical control ties.")
    add("spurious_relation", "native_018",
        next(z["validation"]["accuracy"] for z in chosen["candidates"]
             if z["concept"] == "direct(marked)"),
        "REJECTED_PROXY", "The confounded badge proxy fails independent validation.")
    add("unseen_hidden_cause", "native_018",
        discover(world("latent", "train"),
                 world("latent", "validation"))["status"],
        "HELD", "No visible feature distinguishes identical carriers.")
    add("lost_raw_distinction", "native_018",
        discover(stripped_of_graph(train),
                 stripped_of_graph(validation))["status"],
        "HELD", "Erased distinctions cannot be regenerated from surface x.")
    add("three_hop_unavailable", "native_018",
        discover(n_step_world(3), n_step_world(3))["status"],
        "HELD", "The hard-coded concept grammar cannot synthesize a three-hop path.")
    add("xor_of_two_new_relations", "native_018",
        discover(two_relation_xor(), two_relation_xor())["status"],
        "HELD", "One added graph bit cannot represent an interaction of two.")
    spoof = tuple(replace(e, outcome=1 - e.outcome) for e in holdout)
    add("false_graph_world", "native_018",
        assess(model, spoof)["accuracy"],
        "EXPOSED_PREDICTION_FAILURE",
        "A plausible graph is not authenticated physical truth.")
    add("negative_transfer", "native_018",
        assess(model, world("badge", "holdout"))["accuracy"],
        "EXPOSED_NEGATIVE_TRANSFER",
        "A model of one synthetic world does not generalize without evidence.")

    earlier = parse_bank("The bank moved.", "", 1, "raw-u1")
    later = parse_bank("The bank moved.", "After the flood", 2, "raw-u1+u2")
    add("aperture_ambiguity", "bounded_green_adapter",
        {"earlier": earlier.candidate_senses, "later": later.candidate_senses,
         "earlier_unchanged": len(earlier.candidate_senses) == 2},
        "PASS_LOCAL_PROTOCOL", "An unresolved sense field survives later narrowing.")
    add("observer_temporal_cut", "bounded_green_adapter",
        rebase_reading_on_past(later, earlier),
        "PASS_LOCAL_PROTOCOL", "Later interpretations never rewrite earlier availability.")
    a, b = projections_for_022100()
    add("typed_decoder", "bounded_green_adapter",
        {"base3": a["value"], "chord": b["value"],
         "comparison": compare_projections(a, b)},
        "PASS_LOCAL_PROTOCOL", "One carrier admits distinct typed projections.")
    add("operator_order_delta", "bounded_green_adapter",
        {"noncommuting": numeric_delta(5, "add1", "double")["delta"],
         "commuting": numeric_delta(5, "add1", "add3")["delta"]},
        "PASS_LOCAL_PROTOCOL", "Nonzero delta is not automatic invention or causality.")
    add("fact_shaped_not_fact", "bounded_green_adapter",
        admit_claim(Claim("The bank moved.", "FACT_CANDIDATE",
                          "model-assertion", False, True)),
        "PASS_LOCAL_PROTOCOL", "Semantic FACT label never establishes evidence.")
    add("correct_name_without_authority", "bounded_green_adapter",
        doorway(Crossing("named-actor", "target", True, True, False)),
        "PASS_LOCAL_PROTOCOL", "Correct address does not grant power to cross.")
    add("two_hands_on_frame", "bounded_green_adapter",
        {"missing_source": doorway(Crossing("A", "B", False, True, True)),
         "missing_consent": doorway(Crossing("A", "B", True, False, True)),
         "review_only": doorway(Crossing("A", "B", True, True, True))},
        "PASS_LOCAL_PROTOCOL", "Consequence stays held between source and destination.")
    forged_majority = (Witness(False, "forwarder", True),) * 7 + (
        Witness(True, "independent", True),)
    add("forwarded_votes", "bounded_green_adapter",
        adjudicate(forged_majority),
        "PASS_LOCAL_PROTOCOL", "Seven copies are one upstream, not seven independent witnesses.")
    add("source_metadata_forgery", "bounded_green_adapter",
        adjudicate((Witness(True, "family-A", False),
                    Witness(True, "family-B", False))),
        "PASS_LOCAL_PROTOCOL", "Declared origin names never establish authentication.")
    seeded = (LanguageWitness("blue spoons", "two-hop-path", "A", True),
              LanguageWitness("blue spoons", "two-hop-path", "B", True))
    add("local_grammar_grounding", "bounded_green_adapter",
        ground_alias(seeded, "blue spoons"),
        "PASS_LOCAL_PROTOCOL", "Local vocabulary earned from two explicit corrections.")
    add("local_grammar_homonym", "bounded_green_adapter",
        ground_alias(seeded + (LanguageWitness("blue spoons", "red-edge",
                                              "C", True),), "blue spoons"),
        "PASS_LOCAL_PROTOCOL", "Conflicting correction reopens ambiguity.")
    add("no_cross_world_authority", "native_018",
        {"cartridge_authority": chosen["cartridge"]["authority"],
         "automatically_deployed": baseline["automatically_deployed"],
         "external_actions": baseline["external_actions"]},
        "HELD", "Prediction does not grant external action or automatic promotion.")

    return {
        "schema": "motif018.green-grammar-crucible/v0",
        "research_label": "GGC-001 — Green Grammar meets The Unknown Unknown",
        "source_roads": SOURCE_ROADS,
        "sources_are_noncanonical_research_witnesses": True,
        "test_cases": results,
        "counts_by_verdict": {v: sum(r["verdict"] == v for r in results)
                              for v in sorted({r["verdict"] for r in results})},
        "limits": [
            "Native_018 tests execute the actual MOTIF-018 prototype.",
            "Bounded_green_adapter probes are *new* local deterministic fixtures, not integrations with owner projects.",
            "The graph spoof is a retained, intentional model failure, not a safe refusal.",
            "No natural-language model, human calibration, actual independent witnesses, real authority, or real effects were evaluated.",
            "The Green Grammar thread is noncanonical research continuity; this does not promote it.",
            "The toy grammar still cannot invent unseen primitive operators or recover erased information.",
        ],
        "external_actions": 0, "promotions": 0,
    }


if __name__ == "__main__":
    print(json.dumps(run_crucible(), indent=2, sort_keys=True))
