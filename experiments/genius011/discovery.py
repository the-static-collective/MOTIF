"""MOTIF GENIUS-011 — THE UNSUSPECTED RELATION.

Experimental cycle: independently named source graphs -> canonical two-edge
patterns -> GENERATED cross-thread conjectures -> frozen query receipt ->
separate randomized synthetic measurements -> source-audited refusal or
conditional convergence -> GENIUS-010/009 two-clock reinterpretation.

No candidate "answer names" supplied to synthesis. Classical connected
subgraph enumeration and Fisher testing; NOT a new discovery algorithm,
new physical causal mechanism, or independently validated real-world result.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, permutations
from math import isfinite
import json
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genius010.convergence import fisher_two_sided, two_clock_convergence_packet

THREADS = ("glasshouse", "broadcast", "parcel")
REGIMES = ("TRUE", "TRUE_RENAMED", "NULL", "CONFOUNDED",
           "PARTIAL", "OPPOSED", "ECHO_ROOT", "RIVAL", "NO_SHARED")
ALPHA = .05
PATTERN_FAMILY_BUDGET = 24  # fixed upper bound, not number chosen after inspecting outcomes
N_PER_ARM = 40
MIN_RISK_DIFFERENCE = .25

# Source-world template *constructor*, NOT a question menu or candidate
# identity revealed to the synthesizer. All candidates must instead be
# derived from the three separately labeled public graph descriptions.
TEMPLATES = (
    ((0, 1, "+"), (1, 2, "-")),
    ((0, 1, "+"), (0, 2, "+")),
    ((0, 1, "-"), (2, 1, "+")),
    ((0, 1, "+"), (1, 0, "-")),
)


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    sign: str
    evidence_id: str
    shareable: bool = True
    private_note: str = ""


@dataclass(frozen=True)
class Strand:
    name: str
    origin_root: str
    edges: tuple[Edge, ...]
    common_words: tuple[str, ...]


@dataclass(frozen=True)
class Candidate:
    signature: str
    source_witnesses: tuple[tuple[str, tuple[str, ...]], ...]
    question: str
    observation_contract: str
    digest: str


@dataclass(frozen=True)
class Trial:
    signature: str
    thread: str
    treated: bool
    success: bool
    evidence_id: str
    origin_root: str
    shareable: bool = True
    private_note: str = ""
    measurement_kind: str = "SIMULATED_RANDOMIZED"


@dataclass(frozen=True)
class SimulatorWorld:
    regime: str
    seed: int
    strands: tuple[Strand, ...]
    # Latent parameters must never be passed to question_synthesis or
    # the analyzer. Only the *simulator* and final scoring may read these.
    secret_active_signature: str | None
    secret_secondary_signature: str | None


def digest(items) -> str:
    """Stable pointer fingerprint; cryptographic hash != authenticated author."""
    return sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()


def canonical_pair(pair: tuple[Edge, Edge]) -> str | None:
    """Exact small-graph isomorphism code; directed edges and signs matter."""
    if any(e.sign not in ("+", "-") or not e.src or not e.dst or e.src == e.dst
           for e in pair):
        raise ValueError("Invalid signed directed edge")
    nodes = {e.src for e in pair} | {e.dst for e in pair}
    if len(nodes) > 3 or len(nodes) < 2:
        return None  # two disconnected edges cannot form a two-edge motif
    if not ({pair[0].src, pair[0].dst} &
            {pair[1].src, pair[1].dst}):
        return None
    variants = []
    for ordering in permutations(sorted(nodes)):
        translate = {v: str(i) for i, v in enumerate(ordering)}
        variants.append("|".join(sorted(
            translate[e.src] + e.sign + translate[e.dst] for e in pair
        )))
    return min(variants)


def mine_strand(s: Strand) -> dict[str, tuple[str, ...]]:
    if s.name not in THREADS or not s.origin_root:
        raise ValueError("Source strand and provenance required")
    if any(not e.evidence_id for e in s.edges):
        raise ValueError("Evidence source pointer required")
    seen = [e.evidence_id for e in s.edges]
    if len(set(seen)) != len(seen):
        raise ValueError("Replayed graph-edge evidence")
    # Graph source records enter the model only by explicit publication.
    public = [Edge(e.src, e.dst, e.sign, e.evidence_id, True, "")
              for e in s.edges if e.shareable]
    out: dict[str, set[str]] = {}
    for a, b in combinations(public, 2):
        key = canonical_pair((a, b))
        if key:
            out.setdefault(key, set()).update((a.evidence_id, b.evidence_id))
    return {key: tuple(sorted(refs)) for key, refs in sorted(out.items())}


def question_synthesis(strands: tuple[Strand, ...]) -> dict:
    """Only observed graph structure; no secret mechanism or trial outcomes.

    No hypothesis names or humanly supplied cross-thread candidate menu.
    Two-edge signed directed motifs are invented as new *expressions*
    via canonical enumerative graph substructure mining.
    """
    if len(strands) != len(THREADS) or set(s.name for s in strands) != set(THREADS):
        raise ValueError("Exactly three distinct named research strands")
    if len({s.origin_root for s in strands}) != 3:
        return {"status": "HOLD_DUPLICATE_INQUIRY_ORIGINS", "candidates": [],
                "no_measurement_taken": True}
    mines = {s.name: mine_strand(s) for s in strands}
    common = set.intersection(*(set(m) for m in mines.values()))
    if not common:
        return {"status": "HOLD_NO_SHARED_TYPED_STRUCTURE",
                "candidates": [], "no_measurement_taken": True,
                "lexical_overlap_is_not_justification": True}
    if len(common) > PATTERN_FAMILY_BUDGET:
        return {"status": "HOLD_SEARCH_FAMILY_EXCEEDS_BUDGET",
                "candidates": [], "no_measurement_taken": True}
    candidates = []
    for signature in sorted(common):
        witnesses = tuple(
            (name, mines[name][signature]) for name in THREADS
        )
        qtext = (f"Does intervening on signed directed two-edge pattern "
                 f"{signature} improve an independently measured outcome "
                 "in each of glasshouse, broadcast and parcel?")
        certificate = digest({"signature": signature, "witnesses": witnesses,
                              "operator": "TWO_EDGE_SIGNED_SUBGRAPH"})
        candidates.append(Candidate(
            signature, witnesses, qtext,
            "PREDECLARED_SYNTHETIC_RANDOMIZED_TWO_ARM_TEST",
            certificate,
        ))
    return {"status": "GENERATED_FALSIFIABLE_RELATION_QUESTIONS",
            "candidates": candidates,
            "lexical_overlap_is_not_justification": True,
            "hypothetical_questions_not_verified": True,
            "no_measurement_taken": True}


def _signed_edges(prefix: str, shape) -> tuple[Edge, Edge]:
    names = [f"{prefix}_role_{x}" for x in ("fawn", "river", "tower")]
    return tuple(Edge(names[a], names[b], sign,
                      f"synthetic://graph/{prefix}/{i}")
                 for i, (a, b, sign) in enumerate(shape))


def make_world(seed: int, regime: str) -> SimulatorWorld:
    if regime not in REGIMES:
        raise ValueError("Unknown regime")
    # Layout change per seed: which of two formerly unnamed structures is
    # truly operative varies. The question generator must not have access
    # to this variable or to this simulator's generation code.
    rng = random.Random(seed * 1607 + REGIMES.index(regime) * 311)
    if regime == "NO_SHARED":
        combos = ((0, 1), (2, 3), (0, 2))
    else:
        combos = ((0, 1), (0, 1), (0, 1))
    strands = []
    for i, name in enumerate(THREADS):
        prefix = f"{name}_{seed}_{rng.randrange(1_000_000)}"
        edge_sets = [_signed_edges(f"{prefix}_{slot}", TEMPLATES[j])
                     for slot, j in enumerate(combos[i])]
        edges = tuple(e for pair in edge_sets for e in pair)
        # Surface vocabulary is deliberately identical across unrelated
        # strands; the lexical baseline will always prefer it.
        origin = ("synthetic://REUSED_ONE_ORIGIN" if regime=="ECHO_ROOT"
                  else f"synthetic://authored/{seed}/{name}")
        strands.append(Strand(name, origin, edges,
                              ("blue", "ribbon", "clock")))
    a = canonical_pair(_signed_edges("latent_a", TEMPLATES[0]))
    b = canonical_pair(_signed_edges("latent_b", TEMPLATES[1]))
    assert a != b
    active = (a if seed % 2 == 0 else b)
    if regime in ("NULL", "CONFOUNDED", "NO_SHARED"):
        active = None
    secondary = (b if active == a else a) if regime == "RIVAL" else None
    return SimulatorWorld(regime, seed, tuple(strands), active, secondary)


def _effect(world: SimulatorWorld, signature: str, thread: str) -> float:
    if world.secret_active_signature != signature and (
        world.secret_secondary_signature != signature):
        return 0.0
    if world.regime == "PARTIAL" and thread == "parcel":
        return 0.0
    if world.regime == "OPPOSED" and thread == "parcel":
        return -.80
    return .80


def simulate_test(world: SimulatorWorld, question: Candidate
                 ) -> tuple[Trial, ...]:
    """Synthetic sensor oracle called ONLY after a question is committed."""
    rng = random.Random(int(digest(
        [world.seed, world.regime, question.signature])[:15], 16))
    rows = []
    for thread in THREADS:
        effect = _effect(world, question.signature, thread)
        assignments = [True]*N_PER_ARM + [False]*N_PER_ARM
        rng.shuffle(assignments)
        for j, exposed in enumerate(assignments):
            probability = .5 + effect*(int(exposed)-.5)
            success = rng.random() < probability
            eid = (f"synthetic://trial/{world.seed}/{world.regime}/"
                   f"{question.digest}/{thread}/{j}")
            shared = ((j + THREADS.index(thread)) % 29 != 0)
            rows.append(Trial(question.signature, thread, exposed, success,
                              eid, eid, shared,
                              "NEVER_EXPORT_PRIVATE_SYNTHETIC_CONTENT"))
    return tuple(rows)


def public_trials(rows: tuple[Trial, ...]) -> tuple[Trial, ...]:
    return tuple(Trial(x.signature, x.thread, x.treated, x.success,
                       x.evidence_id, x.origin_root, True, "",
                       x.measurement_kind)
                 for x in rows if x.shareable)


def analyze(question: Candidate, trials: tuple[Trial, ...],
            *, purported_randomization_attested: bool,
            full_evidence: bool = False) -> dict:
    if not purported_randomization_attested:
        return {"signature": question.signature,
                "status": "HOLD_UNVERIFIED_EXPERIMENT_DESIGN",
                "no_external_action": True}
    if any(not x.shareable or x.private_note for x in trials):
        raise ValueError("Unshared/private test results cannot be analyzed")
    if any(x.measurement_kind != "SIMULATED_RANDOMIZED" for x in trials):
        return {"signature": question.signature,
                "status": "HOLD_OBSERVATIONAL_DATA_NOT_AN_INTERVENTION",
                "no_external_action": True}
    if any(x.signature != question.signature or x.thread not in THREADS
           or not x.evidence_id or not x.origin_root
           or type(x.treated) is not bool or type(x.success) is not bool
           for x in trials):
        raise ValueError("Malformed source-owned measurement")
    if len({r.evidence_id for r in trials}) != len(trials):
        return {"signature": question.signature, "status": "HOLD_REPLAYED_EVIDENCE",
                "no_external_action": True}
    if len({r.origin_root for r in trials}) != len(trials):
        return {"signature": question.signature, "status": "HOLD_SHARED_EXPERIMENT_ORIGIN",
                "no_external_action": True}
    p_cutoff = ALPHA/(PATTERN_FAMILY_BUDGET*len(THREADS))
    estimates = []
    for thread in THREADS:
        records = [x for x in trials if x.thread == thread]
        yes = [x for x in records if x.treated]
        no = [x for x in records if not x.treated]
        if min(len(yes), len(no)) < 20:
            return {"signature": question.signature,
                    "status": "HOLD_UNDERPOWERED_EVIDENCE",
                    "thread": thread, "no_external_action": True}
        p = fisher_two_sided(sum(x.success for x in no), len(no),
                             sum(x.success for x in yes), len(yes))
        gap = sum(x.success for x in yes)/len(yes) - (
              sum(x.success for x in no)/len(no))
        refs = sorted(x.evidence_id for x in records)
        estimates.append({
            "thread": thread, "active_n": len(yes), "control_n": len(no),
            "active_successes": sum(x.success for x in yes),
            "control_successes": sum(x.success for x in no),
            "risk_difference": round(gap, 6),
            "exact_fisher_two_sided_p": round(p, 12),
            "passes_precommitted_rule": p<=p_cutoff and gap>=MIN_RISK_DIFFERENCE,
            "all_public_evidence_sha256": digest(refs),
            "public_evidence_refs": refs if full_evidence else refs[:3],
            "reference_policy": "FULL_ID_LIST_IN_DETAILED_CASES_ELSE_3_EXAMPLES",
        })
    return {
        "signature": question.signature,
        "status": ("CONDITIONAL_SYNTHESIZED_BRIDGE"
                   if all(x["passes_precommitted_rule"] for x in estimates)
                   else "HOLD_BRIDGE_NOT_SUPPORTED"),
        "source_witnesses": [
            {"thread": t, "edge_evidence": list(ref)}
            for t, ref in question.source_witnesses
        ],
        "generated_question": question.question,
        "question_origin_sha256": question.digest,
        "per_comparison_alpha": p_cutoff,
        "instrument": question.observation_contract,
        "intervention_design_declared_not_authenticated": True,
        "causal_or_real_world_inference_authorized": False,
        "per_thread": estimates,
        "no_external_action": True,
    }


def evaluate_case(seed: int, regime: str, *, detailed: bool=False) -> dict:
    world = make_world(seed, regime)
    proposals = question_synthesis(world.strands)
    if proposals["status"] != "GENERATED_FALSIFIABLE_RELATION_QUESTIONS":
        return {
            "seed": seed, "regime": regime, "synthesis_status": proposals["status"],
            "candidate_signatures": [],
            "conditionally_supported": [],
            "actual_secret_for_evaluator_only": world.secret_active_signature,
            "tests_performed": 0,
            "two_clock": None,
            "no_external_action": True,
        }
    candidates: list[Candidate] = proposals["candidates"]
    # The new conjectures and query budget are committed before the lab's
    # separate synthetic measurements are generated or accessed.
    pre_measurement_commit = digest({
        "candidate_order": [c.digest for c in candidates],
        "seeds": [seed, regime],
        "planned_test": [N_PER_ARM, ALPHA, PATTERN_FAMILY_BUDGET,
                         MIN_RISK_DIFFERENCE],
    })
    results = []
    outcomes = []
    for q in candidates:
        trials = public_trials(simulate_test(world, q))
        outcomes.extend(trials)
        results.append(analyze(q, trials,
                               purported_randomization_attested=True,
                               full_evidence=detailed))
    accepted = [r for r in results
                if r["status"] == "CONDITIONAL_SYNTHESIZED_BRIDGE"]
    if len(accepted)==1:
        outcome_status = "ONE_CONDITIONAL_SYNTHESIZED_BRIDGE"
    elif len(accepted)>1:
        outcome_status = "HOLD_MULTIPLE_COMPETING_EXPLANATIONS"
    else:
        outcome_status = "HOLD_NONE_SURVIVED_INDEPENDENT_TESTS"
    # Adapter to prior GENIUS-010/009 source-preserving code. Its requested
    # "interventional_replicates" are public receipt ID arrays.
    legacy_verdict = {
        "conditional_candidates": (
            [accepted[0]["signature"]] if len(accepted)==1 else []),
        "candidates": [
            {"hypothesis": r["signature"], "interventional_replicates":
                [{"evidence_refs": (
                    d["public_evidence_refs"] if detailed else
                    # Reconstruct full public source refs from the immutable
                    # trial record, not from the hidden truth.
                    sorted(x.evidence_id for x in outcomes
                           if x.signature==r["signature"] and
                           x.thread == d["thread"])
                )} for d in r["per_thread"]]}
            for r in results
        ],
    }
    # Legacy code validates only the *structural* interpretive relation;
    # GENIUS-011's conditional test is still not authenticated causation.
    # This adapter's source evidence is public and source-indexed.
    from genius010.convergence import Observation
    bridge_rows = tuple(Observation(
        x.signature, x.thread, "RANDOMIZED", x.treated, x.success,
        x.evidence_id, x.origin_root)
        for x in outcomes)
    weave = two_clock_convergence_packet(bridge_rows, legacy_verdict)
    return {
        "seed": seed, "regime": regime,
        "synthesis_status": proposals["status"],
        "candidate_signatures": [c.signature for c in candidates],
        "pre_measurement_sha256": pre_measurement_commit,
        "tests_performed": len(results),
        "results": results,
        "bridge_status": outcome_status,
        "conditionally_supported": (
            [accepted[0]["signature"]] if len(accepted)==1 else []),
        "actual_secret_for_evaluator_only": world.secret_active_signature,
        "synthetic_secondary_for_evaluator_only": world.secret_secondary_signature,
        "two_clock": weave,
        "lexical_baseline": "blue ribbon",
        "no_external_action": True,
    }
