"""MOTIF GENIUS-010 — THE THREE-THREAD CONVERGENCE TRIAL.

Povenmire-style independent plots + Acaster's changed-meaning payoff +
the GENIUS-009 two-clock source ledger, with classical experimental
inference distinguishing an independent common mechanism from a shared
word, observational confounding, partial convergence, and duplicated
evidence.

Research-HOLD: all cases, randomized assignments, source roots, causes
and outcomes below are ENGINEER-AUTHORED synthetic fixtures.
Statistical results are *conditional on the declared experimental design*.
Neither a low p-value nor a literary analogy establishes a real-world
causal mechanism; no people, instruments or external systems are touched.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from math import comb
import json
import random
from pathlib import Path
import sys

# Reuses the previous, actual two-clock interface instead of quietly
# inventing incompatible "historical source" semantics in this experiment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genius009.two_clocks import (Assertion, Corpus, Reading, Witness,
                                 check_attribution, compose_readings)

THREADS = ("glasshouse", "broadcast", "parcel")
HYPOTHESES = ("blue_ribbon", "hinge_timing", "sunset_mark")
REGIMES = ("CONVERGENCE", "HIDDEN_MOTIF", "NULL", "CONFOUNDED",
           "PARTIAL", "REVERSED", "ECHO_SOURCE")
TRIALS_PER_ARM = 24
OBSERVATIONAL_TRIALS = 64
FAMILY_ALPHA = .05
MIN_EFFECT = .25
# Fixed in advance; if these were selected AFTER looking at data,
# the Bonferroni statement below would not apply.
REFERENCE_MOTIF_SCORE = {"blue_ribbon": 10, "hinge_timing": 0, "sunset_mark": 2}


@dataclass(frozen=True)
class Observation:
    hypothesis: str
    thread: str
    mode: str  # OBSERVATIONAL or RANDOMIZED
    assigned: bool
    outcome: bool
    evidence_id: str
    origin_root: str
    shareable: bool = True
    private_note: str = ""


def public_projection(records: tuple[Observation, ...]) -> tuple[Observation, ...]:
    """Reject missing disclosures; strip private note even on shared data."""
    return tuple(Observation(r.hypothesis, r.thread, r.mode, r.assigned,
                             r.outcome, r.evidence_id, r.origin_root, True, "")
                 for r in records if r.shareable)


def fisher_two_sided(yes_a: int, n_a: int, yes_b: int, n_b: int) -> float:
    """Classical conditional Fisher exact p-value, equal/larger tables included."""
    if min(n_a, n_b) <= 0 or not (0 <= yes_a <= n_a and 0 <= yes_b <= n_b):
        raise ValueError("Invalid 2 x 2 outcome table")
    total_yes = yes_a + yes_b
    lo = max(0, total_yes - n_b)
    hi = min(n_a, total_yes)
    denom = comb(n_a+n_b, total_yes)
    weights = {k: comb(n_a, k) * comb(n_b, total_yes-k)
               for k in range(lo, hi+1)}
    observed = weights[yes_a]
    return min(1.0, sum(v for v in weights.values() if v <= observed)/denom)


def _signal(regime: str, hypothesis: str, thread: str) -> float:
    """Simulator-only ground truth; NEVER supplied to evaluate_candidate()."""
    if hypothesis == "blue_ribbon":
        return 0.0                 # Shared phrase, confounded observational data.
    if hypothesis == "sunset_mark":
        return .84 if thread != "parcel" and regime in ("PARTIAL", "CONVERGENCE") else 0.0
    if hypothesis != "hinge_timing":
        return 0.0
    if regime in ("CONVERGENCE", "HIDDEN_MOTIF", "ECHO_SOURCE"):
        return .84
    if regime == "PARTIAL":
        return .84 if thread != "parcel" else 0.0
    if regime == "REVERSED":
        return -.84 if thread == "parcel" else .84
    return 0.0


def generate(seed: int, regime: str) -> tuple[Observation, ...]:
    """Generate randomized experiments and a deliberately confounded survey.

    Observational X is linked to latent Z; observational Y responds to Z.
    Randomized X is independent of Z and affects Y ONLY if the simulator
    has assigned a true effect. This is a finite *simulation*, not
    authenticated randomization by an external laboratory.
    """
    if regime not in REGIMES:
        raise ValueError("Unknown research scenario")
    rng = random.Random(seed * 1009 + REGIMES.index(regime) * 317)
    out = []
    for hypothesis in HYPOTHESES:
        for thread in THREADS:
            effect = _signal(regime, hypothesis, thread)
            for mode in ("OBSERVATIONAL", "RANDOMIZED"):
                n = OBSERVATIONAL_TRIALS if mode == "OBSERVATIONAL" else 2*TRIALS_PER_ARM
                assignments = ([False]*TRIALS_PER_ARM + [True]*TRIALS_PER_ARM
                               if mode == "RANDOMIZED" else None)
                if assignments is not None:
                    rng.shuffle(assignments)
                for i in range(n):
                    z = rng.random() < .5
                    if mode == "OBSERVATIONAL":
                        # The shared-word decoy is strongly associated under
                        # common cause but has NO direct causal effect.
                        x = z if rng.random() < .94 else not z
                        if hypothesis == "blue_ribbon":
                            p = .08 + .84*int(z)
                        else:
                            p = .08 + .84*int(z)
                    else:
                        x = assignments[i]
                        p = .5 + effect*(int(x)-.5)
                    y = rng.random() < p
                    # Prefixes distinguish separate source events in ordinary
                    # trials. ECHO_SOURCE makes three asserted "independent"
                    # threads share source roots (one repeated original event).
                    origin_thread = ("REPLAYED_SINGLE_EVENT"
                                     if regime == "ECHO_SOURCE"
                                     and hypothesis == "hinge_timing"
                                     and mode == "RANDOMIZED" else thread)
                    origin = (f"source://{seed}/{regime}/{hypothesis}/"
                              f"{mode}/{origin_thread}/{i}")
                    eid = (f"receipt://{seed}/{regime}/{hypothesis}/"
                           f"{thread}/{mode}/{i}")
                    # Entirely predeclared, independent of hidden outcome.
                    share = ((i + THREADS.index(thread)
                              + HYPOTHESES.index(hypothesis)) % 17 != 0)
                    out.append(Observation(
                        hypothesis, thread, mode, bool(x), bool(y), eid,
                        origin, share,
                        "PRIVATE_SIMULATOR_NOTE_NOT_TO_BE_EXPORTED",
                    ))
    return tuple(out)


def _classical_contrast(rows: list[Observation]) -> dict:
    active = [r for r in rows if r.assigned]
    control = [r for r in rows if not r.assigned]
    if len(active) < 10 or len(control) < 10:
        return {"status": "HOLD_TOO_FEW_PUBLIC_OBSERVATIONS"}
    yes_active = sum(r.outcome for r in active)
    yes_control = sum(r.outcome for r in control)
    p = fisher_two_sided(yes_control, len(control), yes_active, len(active))
    gap = yes_active/len(active) - yes_control/len(control)
    return {
        "status": "ESTIMATE_FROM_EXPLICITLY_SHARED_RECORDS",
        "n_active": len(active), "n_control": len(control),
        "success_active": yes_active, "success_control": yes_control,
        "risk_difference": round(gap, 6),
        "two_sided_fisher_p": round(p, 12),
        "exact_unrounded_p": p,
        "source_roots": sorted(r.origin_root for r in rows),
        "evidence_refs": sorted(r.evidence_id for r in rows),
    }


def evaluate_candidate(hypothesis: str,
                       public_rows: tuple[Observation, ...],
                       *, randomization_attested: bool,
                       causal_mechanism_claim: bool = False) -> dict:
    """Independent 3-thread convergence requires 3 supported interventions.

    A real deployment must VERIFY the preregistration/randomization,
    source independence and outcome measurement. This demo has only an
    engineer-authored attestation. No estimated p-value is causal *proof*.
    """
    if hypothesis not in HYPOTHESES:
        raise ValueError("Unknown predeclared hypothesis")
    if any(r.private_note or not r.shareable for r in public_rows):
        raise ValueError("Only redacted, explicitly public observations allowed")
    if not randomization_attested:
        return {"hypothesis": hypothesis,
                "status": "HOLD_NO_VERIFIED_RANDOMIZATION",
                "proposal_only": True}
    target = [r for r in public_rows if r.hypothesis == hypothesis]
    if any(r.thread not in THREADS or
           r.mode not in ("OBSERVATIONAL", "RANDOMIZED")
           or not r.evidence_id or not r.origin_root
           or type(r.assigned) is not bool or type(r.outcome) is not bool
           for r in target):
        raise ValueError("Invalid source-owned public observation")
    ids = [r.evidence_id for r in target]
    if len(set(ids)) != len(ids):
        return {"hypothesis": hypothesis, "status": "HOLD_REPLAYED_RECEIPT",
                "proposal_only": True}
    randomized = [r for r in target if r.mode == "RANDOMIZED"]
    roots = [r.origin_root for r in randomized]
    if len(set(roots)) != len(roots):
        return {"hypothesis": hypothesis,
                "status": "HOLD_NONINDEPENDENT_ORIGIN_ROOT",
                "repeat_root_count": len(roots)-len(set(roots)),
                "proposal_only": True}
    threshold = FAMILY_ALPHA/(len(HYPOTHESES)*len(THREADS))
    per_thread = []
    for thread in THREADS:
        r = [row for row in randomized if row.thread == thread]
        estimate = _classical_contrast(r)
        if estimate["status"].startswith("HOLD"):
            return {"hypothesis": hypothesis,
                    "status": "HOLD_MISSING_EVIDENCE", "thread": thread,
                    "proposal_only": True}
        estimate["thread"] = thread
        estimate["passes_direction_and_familywise_test"] = (
            estimate["risk_difference"] >= MIN_EFFECT
            and estimate["exact_unrounded_p"] <= threshold)
        # The estimate and source receipt IDs are inspectable, but the
        # hidden simulator parameters and unshared observations are absent.
        del estimate["exact_unrounded_p"]
        per_thread.append(estimate)
    all_pass = all(row["passes_direction_and_familywise_test"] for row in per_thread)
    # A preplanned observational comparison is supplied as a counterfactual
    # sanity check, not as evidence of a randomized treatment effect.
    observational = []
    for thread in THREADS:
        rows = [r for r in target if r.mode == "OBSERVATIONAL" and r.thread == thread]
        x = _classical_contrast(rows)
        observational.append({
            "thread": thread,
            "observational_risk_difference": x.get("risk_difference"),
            "not_randomized_not_a_causal_certificate": True,
        })
    return {
        "hypothesis": hypothesis,
        "status": ("CONDITIONAL_THREE_THREAD_CONVERGENCE"
                   if all_pass else "HOLD_CONVERGENCE_NOT_ESTABLISHED"),
        "randomization": "SIMULATOR_DECLARED_NOT_EXTERNALLY_VERIFIED",
        "causal_mechanism_claim_allowed": False,
        "request_to_infer_real_world_causal_mechanism": causal_mechanism_claim,
        "common_name_overlap_not_a_test": REFERENCE_MOTIF_SCORE[hypothesis],
        "per_comparison_alpha": threshold,
        "interventional_replicates": per_thread,
        "observational_associations": observational,
        "independent_source_roots_in_sample": True,
        "next_question": (
            "Does the same hypothesis survive independently administered "
            "interventions, distinct source owners, verified outcomes, and "
            "another blinded task distribution?"
        ),
        "no_external_action": True,
    }


def rank_convergences(public_rows: tuple[Observation, ...],
                      *, randomization_attested: bool) -> dict:
    """Track all 3 named hypotheses; never silently choose after peeking."""
    results = [
        evaluate_candidate(k, public_rows,
                           randomization_attested=randomization_attested)
        for k in HYPOTHESES
    ]
    confirmed = [
        r["hypothesis"] for r in results
        if r["status"] == "CONDITIONAL_THREE_THREAD_CONVERGENCE"
    ]
    return {
        "status": ("HOLD_MULTIPLE_COMPETING_BRIDGES" if len(confirmed)>1
                   else "SYNTHETIC_CONDITIONAL_CONVERGENCE_CANDIDATE"
                   if len(confirmed)==1 else "HOLD_NO_DEFENSIBLE_THREE_THREAD_BRIDGE"),
        "conditional_candidates": confirmed,
        "candidates": results,
        "lexical_only_baseline": max(
            HYPOTHESES, key=lambda k: (REFERENCE_MOTIF_SCORE[k], k)),
        "strong_classical_source_aware_baseline_candidates": confirmed[:],
        "strong_baseline_note": "Independent provenance-aware Fisher exact test is the same statistical engine as the proposed graph.",
        "no_real_world_causal_claim": True,
        "no_external_action": True,
    }


def two_clock_convergence_packet(public_rows: tuple[Observation, ...],
                                 verdict: dict) -> dict:
    """Use the actual GENIUS-009 interface for each of the three threads.

    A later confirmed statistical association can REINTERPRET all three
    earlier story-like observations, but is never inserted into those
    original source records. Rejected hypotheses get no invented callback.
    """
    initial = tuple(
        Witness(thread, i, "EMPIRICAL_INSTRUMENT",
                (Assertion(f"{thread} recorded a distinct unexplained anomaly"),),
                f"synthetic://three-thread/{thread}")
        for i, thread in enumerate(THREADS)
    )
    accepted = verdict["conditional_candidates"]
    if len(accepted)!=1:
        corpus = Corpus("no-unambiguous-bridge-two-clock", initial, ())
    else:
        bridge = accepted[0]
        bridge_source = Witness(
            "later_bridge_audit", 3, "EMPIRICAL_INSTRUMENT",
            (Assertion(f"statistical intervention convergence for {bridge}"),),
            "synthetic://three-thread/later-audit",
        )
        readings = tuple(
            Reading(
                f"reinterpret_{thread}", "later_bridge_audit", thread,
                f"Reconsider the {thread} anomaly as a possible instance of {bridge}, "
                "conditionally on the synthetic randomized intervention evidence",
                f"statistical intervention convergence for {bridge}",
            ) for thread in THREADS
        )
        corpus = Corpus("source-preserving-three-thread-weave",
                        initial+(bridge_source,), readings)
    order = tuple(w.witness_id for w in corpus.witnesses)
    result = compose_readings(corpus, order)
    original = {
        thread: [a.proposition for a in w.assertions]
        for thread in THREADS for w in initial if w.witness_id == thread
    }
    return {
        "status": ("RESEARCH_ONLY_SOURCE_OWNED_REINTERPRETATION"
                   if len(accepted)==1 else "HOLD_NO_UNAMBIGUOUS_BRIDGE"),
        "earlier_source_assertions": original,
        "original_witness_count": len(initial),
        "source_order": result["source_order"],
        "reveal_order": result["disclosure_order"],
        "retrospective_callbacks": [
            r for snap in result["snapshots"]
            for r in snap["new_reader_reinterpretations"]
            if r["reader_reception_mode"] == "RETROSPECTIVE_CALLBACK"
        ],
        "conditional_statistical_bridge_only": accepted,
        "no_original_record_edited": True,
        "no_external_action": True,
    }


def evaluate_world(seed: int, regime: str) -> dict:
    raw = generate(seed, regime)
    shared = public_projection(raw)
    verdict = rank_convergences(shared, randomization_attested=True)
    weave = two_clock_convergence_packet(shared, verdict)
    return {
        "seed": seed,
        "regime": regime,
        "synthetic_evaluator_ground_truth": {
            "positive_three_thread_bridges": (
                ["hinge_timing"] if regime in
                ("CONVERGENCE", "HIDDEN_MOTIF") else []),
            "source_independence_intentionally_broken": regime == "ECHO_SOURCE",
        },
        "public_records": len(shared),
        "withheld_not_scored_or_ingested": len(raw)-len(shared),
        "verdict": verdict,
        "weave": weave,
        "no_external_action": True,
    }
