"""VOID-001: bounded inquiry-to-outcome experiment. Engineer-authored worlds only.

Original MOTIF-003 is loaded as-is; its affordance operation scores hypothetical
question outcomes. All real outcomes and verification are simulated by Owner.
"""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
FACTS = ("permission", "primary", "alternative")
WORLDS = tuple(tuple(int(x) for x in row) for row in product((0, 1), repeat=3))
EVENTS = ("steady", "source_drift", "forged_report", "revoked_permission", "actuator_noop")
POLICIES = ("exact_dp", "entropy", "motif_mesh")


def native003():
    path = HERE.parent / "003" / "affordance.py"
    spec = importlib.util.spec_from_file_location("void001_native_motif003", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("MISSING_CANONICAL_MOTIF_003")
    import sys
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def filter_worlds(observations):
    return tuple(w for w in WORLDS if all(w[FACTS.index(k)] == v for k, v in observations.items()))


def safe_action(worlds):
    """An action is previewable only if allowed in every surviving hypothesis."""
    if not worlds or not all(w[0] for w in worlds):
        return None
    if all(w[1] for w in worlds):
        return "use_primary"
    if all(w[2] for w in worlds):
        return "use_alternative"
    return None


def posterior_split(worlds, sensor):
    i = FACTS.index(sensor)
    return {v: tuple(w for w in worlds if w[i] == v) for v in (0, 1)}


def exact_value(worlds, available, depth):
    """Strong finite exact classical active sensing under a shared uniform prior."""
    if safe_action(worlds):
        return 1.0
    if depth == 0 or not available:
        return 0.0
    return max(sum(len(child) / len(worlds) * exact_value(child, tuple(
        s for s in available if s != sensor), depth - 1)
        for child in posterior_split(worlds, sensor).values() if child)
        for sensor in available)


def pick_exact(worlds, available, depth):
    return max(available, key=lambda s: (sum(
        len(child) / len(worlds) * exact_value(child,
            tuple(t for t in available if t != s), depth - 1)
        for child in posterior_split(worlds, s).values() if child), -FACTS.index(s)))


def pick_entropy(worlds, available):
    return max(available, key=lambda s: (
        1 - sum((len(child) / len(worlds)) ** 2
                for child in posterior_split(worlds, s).values()), -FACTS.index(s)))


def pick_mesh(worlds, available, observations):
    """Actual MOTIF-003 analyzes hypothetical inquiry successors, not hidden truth."""
    native = native003()
    initial = frozenset(("seen", k, str(v)) for k, v in observations.items())

    def possibilities(state, verbs):
        obs = {key: int(v) for _, key, v in state if _ == "seen"}
        candidates = filter_worlds(obs)
        for sensor in verbs:
            if sensor in obs:
                continue
            for value, child in posterior_split(candidates, sensor).items():
                if child:
                    future = state | frozenset({("seen", sensor, str(value))})
                    yield (f"observe:{sensor}", (str(value),), future)
        action = safe_action(candidates)
        if action:
            yield (action, (), state | frozenset({("preview", action, "1")}))

    rows = native.analyze_first_moves(
        initial, available, possibilities,
        lambda state, _: 1 if safe_action(filter_worlds(
            {k: int(v) for tag, k, v in state if tag == "seen"})) else 0,
        horizon=2, max_worlds=128)
    by_sensor = Counter()
    for row in rows:
        if not row["operator"].startswith("observe:"):
            continue
        sensor = row["operator"].split(":", 1)[1]
        child = filter_worlds({**observations, sensor: int(row["roles"][0])})
        by_sensor[sensor] += len(child) / len(worlds) * (
            2 * row["immediate_delta"] + len([x for x in row["new_affordances"]
                            if x[0].startswith("use_")])
        )
    return max(available, key=lambda s: (by_sensor[s], -FACTS.index(s)))


class Owner:
    """Independent synthetic outcome gate; policies never receive hidden truth."""
    def __init__(self, world, event):
        self.truth = list(world)
        self.event = event
        self.epoch = 0
        self.queries = 0
        self.applied = False

    def observe(self, sensor):
        self.queries += 1
        if self.event == "source_drift" and self.queries == 2:
            self.truth[1] = 1 - self.truth[1]
            self.epoch += 1
        value = self.truth[FACTS.index(sensor)]
        receipt = {"source": "synthetic-owner", "sensor": sensor,
                   "value": value, "epoch": self.epoch, "query": self.queries}
        receipt["seal"] = digest(receipt)
        if self.event == "forged_report" and sensor == "permission":
            receipt["value"] = 1 - value  # seal NOT updated: detected tamper
        return receipt

    @staticmethod
    def verify(receipt):
        actual = {k: v for k, v in receipt.items() if k != "seal"}
        return receipt["seal"] == digest(actual) and receipt["source"] == "synthetic-owner"

    def perform(self, action):
        if self.event == "revoked_permission":
            self.truth[0] = 0
            self.epoch += 1
        permitted = bool(self.truth[0])
        available = bool(self.truth[1 if action == "use_primary" else 2])
        success = permitted and available and self.event != "actuator_noop"
        self.applied = success
        outcome = {"action": action, "success": success, "permission_at_attempt": permitted,
                   "resource_at_attempt": available, "owner_epoch": self.epoch,
                   "synthetic_verified": True}
        outcome["seal"] = digest(outcome)
        return outcome


def run(world, event, policy, budget=2):
    if policy not in POLICIES or world not in WORLDS or event not in EVENTS:
        raise ValueError("UNREGISTERED_POLICY_OR_FIXTURE")
    owner = Owner(world, event)
    observations, ledger, active_epoch = {}, [], 0
    for left in range(budget, 0, -1):
        candidates = filter_worlds(observations)
        if safe_action(candidates):
            break
        available = tuple(s for s in FACTS if s not in observations)
        if not available:
            break
        if policy == "exact_dp":
            sensor = pick_exact(candidates, available, left)
        elif policy == "entropy":
            sensor = pick_entropy(candidates, available)
        else:
            sensor = pick_mesh(candidates, available, observations)
        receipt = owner.observe(sensor)
        verified = owner.verify(receipt)
        ledger.append({**receipt, "accepted": verified})
        if not verified:
            continue
        if receipt["epoch"] > active_epoch:
            observations = {}  # old INK history remains in ledger, not in current truth
            active_epoch = receipt["epoch"]
        observations[sensor] = receipt["value"]
    plan = safe_action(filter_worlds(observations))
    result = owner.perform(plan) if plan else None
    verified_success = bool(result and result["success"] and
                            result["seal"] == digest({k: v for k, v in result.items()
                                                      if k != "seal"}))
    return {"policy": policy, "event": event, "world_id": "".join(map(str, world)),
            "queries": owner.queries, "plan": plan, "observations": observations,
            "ledger": ledger, "outcome": result, "verified_success": verified_success,
            "status": "VERIFIED_GOAL" if verified_success else
                      "VERIFIED_NO_EFFECT" if result else "HOLD_UNCERTAIN_OR_DENIED",
            "source_is_independent": False, "world_is_synthetic": True,
            "external_actions": 0}


def external_replay():
    """Read the existing CONFLUENCE-003 third-party map trial, if source checkouts exist.

    This is an evidence adapter, not a newly run VOID question-selection policy.
    """
    import sys
    location = HERE.parent / "confluence003"
    sys.path.insert(0, str(location))
    from trial import benchmark as confluence_benchmark
    original = confluence_benchmark()
    if original["cohort_size"] != 16 or original["source_git_revision"] != "ffa02393942e649d4da82d5647d3159e7a7dd572":
        raise RuntimeError("EXTERNAL_REPLAY_PROVENANCE_MISMATCH")
    return {"source": "MovingAI pathfinding via existing CONFLUENCE-003",
            "source_git_revision": original["source_git_revision"],
            "source_origin_count": original["independent_source_origins"],
            "actual_external_map_cases_replayed": original["cohort_size"],
            "published_optimal_length_checks": original["independently_published_lengths_matched"],
            "classical_astar_dijkstra_parity": original["competitive_classical_astar_and_dijkstra_same_cost"],
            "native_motif003_executed": original["native_003_executed"],
            "native_motif006_executed": original["native_006_executed"],
            "native_field008_evidence": original["native_008_controlled_shift_evidence"],
            "source_sha256": original["sha256"],
            "actual_planning_comparator_gain": 0,
            "note": "External maps are real; synthetic changes are engineered; FULL and classical A* route costs tie."}


def benchmark(*, include_external=False):
    catalog = json.loads((HERE / "sources.json").read_text())
    challenges = json.loads((HERE / "challenges.json").read_text())
    if any(card["reference"] not in {x["id"] for x in catalog["sources"]}
           for card in challenges["cards"]):
        raise RuntimeError("UNRESOLVED_SOURCE_REFERENCE")
    rows = [run(world, event, policy) for world in WORLDS
            for event in EVENTS for policy in POLICIES]
    metrics = {p: {"verified_success": sum(x["verified_success"] for x in rows
                                         if x["policy"] == p),
                   "total_queries": sum(x["queries"] for x in rows if x["policy"] == p),
                   "attempts": sum(x["outcome"] is not None for x in rows
                                   if x["policy"] == p)} for p in POLICIES}
    report = {"experiment": "VOID-001", "worlds": len(WORLDS),
              "event_classes": len(EVENTS), "cases_per_policy": len(WORLDS)*len(EVENTS),
              "policy_metrics": metrics, "sources_in_catalog": len(catalog["sources"]),
              "research_challenge_cards": len(challenges["cards"]),
              "external_benchmark_cases_executed": 0,
              "synthetic_action_attempts_only": True,
              "native_motif003_executed": True,
              "no_model_or_external_service_calls": True,
              "limits": "Engineered development fixtures, not blind real-world results. Exact DP has same prior and budget; outcomes are only synthetic-owner attested.",
              "rows": rows}
    if include_external:
        report["external_replay"] = external_replay()
        report["external_benchmark_cases_executed"] = report["external_replay"]["actual_external_map_cases_replayed"]
    report["sha256"] = digest(report)
    return report


if __name__ == "__main__":
    import sys
    if set(sys.argv[1:]) - {"--external"}:
        raise SystemExit("Allowed flag: --external")
    print(json.dumps(benchmark(include_external="--external" in sys.argv), sort_keys=True, indent=2))
