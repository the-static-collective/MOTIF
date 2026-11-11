"""FIRE-003: epistemic smoke detector for evidence-lineage and feedback inflation.

A deliberately finite synthetic research protocol. Independent *claim IDs* are
not independent *source origins*. Only a separately queried synthetic auditor
can attest origins; a compromised auditor can still mislead this design.
Outcome truth is never available to the scheduler until explicit verification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import log, exp
from random import Random
from typing import Optional

REGIMES = ("independent", "copied", "unverifiable", "compromised", "drift")
POLICIES = ("naive_frozen", "naive_online", "guarded_frozen", "guarded_online")
AUDIT_COST = 1
BUDGET = 32


@dataclass(frozen=True)
class Task:
    key: str
    value: int
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class Report:
    task: str
    claim_id: str
    answer: bool


@dataclass(frozen=True)
class Attestation:
    status: str
    origins: tuple[str, ...] = ()
    issuer: str = "synthetic-owner-auditor"


@dataclass(frozen=True)
class World:
    tasks: dict[str, Task]
    truth: dict[str, bool]
    reports: dict[str, tuple[Report, ...]]
    origins: dict[str, tuple[str, ...]]
    regime: str

    def observe(self, key: str, index: int) -> Report:
        return self.reports[key][index]

    def attest(self, key: str, reports: tuple[Report, ...]) -> Attestation:
        # In reality, this function requires an independent *trusted* owner.
        # If no trusted provenance is available, HOLD is the right answer.
        if self.regime == "unverifiable":
            return Attestation("UNVERIFIABLE")
        if self.regime == "compromised":
            # Intentionally compromised auditor; identical copies appear unique.
            return Attestation("VERIFIED", tuple(r.claim_id for r in reports))
        return Attestation("VERIFIED", self.origins[key][:len(reports)])

    def verify(self, key: str, predicted: bool) -> dict:
        actual = self.truth[key]
        return {"task": key, "guess": predicted, "certified": actual is predicted,
                "actual": actual, "authority": "synthetic-verification-only"}


def world(seed: int, regime: str) -> World:
    if regime not in REGIMES:
        raise ValueError("Unknown synthetic regime")
    rng = Random(seed)
    children = {f"Q{i}": [] for i in range(8)}
    for i in range(4, 8):
        children[f"Q{rng.randrange(4)}"].append(f"Q{i}")
    tasks = {f"Q{i}": Task(f"Q{i}", rng.randint(3, 12), tuple(children[f"Q{i}"]))
             for i in range(8)}
    truth, records, origins = {}, {}, {}
    for i in range(8):
        key = f"Q{i}"
        actual = bool(rng.getrandbits(1))
        truth[key] = actual
        if regime in ("copied", "unverifiable", "compromised"):
            roots = (f"{key}-root-A",) * 3 + (f"{key}-root-B", f"{key}-root-C")
        else:
            roots = tuple(f"{key}-root-{j}" for j in range(5))
        fidelity = (.90 if i < 4 else .54) if regime == "drift" else .76
        values_by_root = {root: (actual if rng.random() < fidelity else not actual)
                          for root in sorted(set(roots))}
        records[key] = tuple(Report(key, f"{key}-witness-{j}", values_by_root[root])
                             for j, root in enumerate(roots))
        origins[key] = roots
    return World(tasks, truth, records, origins, regime)


def forecast(reports: tuple[Report, ...], attestation: Optional[Attestation],
             accuracy: float) -> dict:
    """Independence-sensitive symmetric binary Bayes, no truth lookup.

    Accuracy prior is explicitly assumed, not objectively established.
    Unverified ancestry forces an uninformative forecast and a HOLD marker.
    """
    if not reports or len({r.claim_id for r in reports}) != len(reports):
        raise ValueError("Missing or duplicated claim IDs")
    p = min(.98, max(.52, accuracy))
    claim_count = len(reports)
    if attestation is not None and attestation.status != "VERIFIED":
        return {"p_true": .5, "effective_roots": 0, "claimed": claim_count,
                "signal": "UNVERIFIABLE_LINEAGE", "eligible": False,
                "source_votes": ()}
    if attestation is None:
        roots = tuple(r.claim_id for r in reports)
    else:
        if len(attestation.origins) != claim_count:
            raise ValueError("Auditor omitted lineage receipts")
        roots = attestation.origins
    grouped = {}
    for record, root in zip(reports, roots):
        if root in grouped and grouped[root] is not record.answer:
            return {"p_true": .5, "effective_roots": 0, "claimed": claim_count,
                    "signal": "INTRAROOT_CONTRADICTION", "eligible": False,
                    "source_votes": ()}
        grouped[root] = record.answer
    votes = tuple(grouped[root] for root in sorted(grouped))
    logodds = (2 * sum(votes) - len(votes)) * log(p / (1 - p))
    prob = 1. / (1. + exp(-logodds))
    signal = "DEPENDENCE_DISCOVERED" if len(votes) < claim_count else "CLEAR"
    return {"p_true": prob, "effective_roots": len(votes),
            "claimed": claim_count, "signal": signal,
            "eligible": attestation is None or len(votes) >= 3,
            "source_votes": votes}


@dataclass
class Learner:
    correct: int = 4
    incorrect: int = 1
    verified_events: int = 0
    confident_failures: int = 0
    contradictions: int = 0
    alerts: list[dict] = field(default_factory=list)

    @property
    def reliability(self) -> float:
        return self.correct / (self.correct + self.incorrect)

    def accept(self, result: dict, probability: float,
               evidence: dict, allow_update: bool) -> None:
        if result.get("authority") != "synthetic-verification-only":
            raise ValueError("Feedback lacks trusted synthetic verification")
        if type(result.get("actual")) is not bool or type(result.get("certified")) is not bool:
            raise ValueError("Malformed verification receipt")
        if result["certified"] is not (result["actual"] is result["guess"]):
            raise ValueError("Contradictory verification receipt")
        self.verified_events += 1
        confidence = max(probability, 1. - probability)
        if confidence >= .95 and not result["certified"]:
            self.confident_failures += 1
            self.alerts.append({"task": result["task"], "alert": "CONFIDENTLY_FALSIFIED",
                                "prior_confidence": round(confidence, 5)})
        if not allow_update:
            return
        for report in evidence["source_votes"]:
            self.correct += int(report is result["actual"])
            self.incorrect += int(report is not result["actual"])


def run(seed: int, regime: str, policy: str, budget: int = BUDGET) -> dict:
    """Bounded staged simulator; all policies have same synthetic world and budget.

    Each task requires 5 observations, one reasoning operation, and a verification.
    Guarded policies also spend one operation on a separately issued attestation.
    A HOLD is not verified and earns no knowledge or discovery credit.
    """
    if policy not in POLICIES or budget < 0:
        raise ValueError("Invalid protocol or budget")
    owner = world(seed, regime)
    guarded = policy.startswith("guarded")
    online = policy.endswith("online")
    ledger = Learner()
    remaining = budget
    unlocked = {f"Q{i}" for i in range(4)}
    seen, certified, failures, holds, dependence, unavailable = set(), set(), 0, 0, 0, 0
    brier_sum, forecasts, source_steps = 0., 0, 0
    trace: list[dict] = []
    while True:
        todo = sorted((k for k in unlocked if k not in seen),
                      key=lambda k: (-owner.tasks[k].value, k))
        if not todo or remaining < 6 + int(guarded):
            break
        key = todo[0]
        seen.add(key)
        collected = tuple(owner.observe(key, j) for j in range(5))
        remaining -= 5
        source_steps += 5
        audit = owner.attest(key, collected) if guarded else None
        if guarded:
            remaining -= AUDIT_COST
            source_steps += AUDIT_COST
        state = forecast(collected, audit, ledger.reliability)
        if state["signal"] == "DEPENDENCE_DISCOVERED":
            dependence += 1
        if state["signal"] == "UNVERIFIABLE_LINEAGE":
            unavailable += 1
        # Non-permissioned guess remains a provisional belief, not evidence.
        brier_sum += (state["p_true"] - int(owner.truth[key])) ** 2
        forecasts += 1
        step = {"task": key, "claimed": state["claimed"],
                "roots": state["effective_roots"], "signal": state["signal"],
                "forecast": round(state["p_true"], 6),
                "status": "PENCIL"}
        if not state["eligible"]:
            holds += 1
            step["status"] = "HOLD"
            trace.append(step)
            continue
        if remaining < 2:
            step["status"] = "BUDGET_HOLD"
            holds += 1
            trace.append(step)
            break
        remaining -= 2  # one reasoning step + one external synthetic verification
        prediction = state["p_true"] >= .5
        checked = owner.verify(key, prediction)
        ledger.accept(checked, state["p_true"], state, online)
        step.update({"status": "CERTIFIED" if checked["certified"] else "FALSIFIED",
                     "verifier": checked["authority"],
                     "actual_after_verification": checked["actual"]})
        if checked["certified"]:
            certified.add(key)
            unlocked.update(owner.tasks[key].children)
        else:
            failures += 1
        trace.append(step)
    return {"seed": seed, "regime": regime, "policy": policy,
            "certified_value": sum(owner.tasks[k].value for k in certified),
            "certified_count": len(certified), "failed_verifications": failures,
            "holds": holds, "dependence_alerts": dependence,
            "unverifiable_alerts": unavailable,
            "confident_failures": ledger.confident_failures,
            "verified_learning_events": ledger.verified_events if online else 0,
            "reliability_final": round(ledger.reliability, 5),
            "questions_unlocked": len(unlocked),
            "operations_spent": budget - remaining,
            "audit_steps": source_steps - 5 * len(seen),
            "forecast_brier": round(brier_sum / forecasts, 6) if forecasts else None,
            "net_value": sum(owner.tasks[k].value for k in certified) - 5 * failures,
            "trace": trace}


def fixed_forecast_audit(seed: int, regime: str) -> dict:
    """Fixed same eight exposures: prevents selective-abstention Brier illusion."""
    owner = world(seed, regime)
    result = {"naive": [], "guarded": [], "oracle_roots": []}
    for key in sorted(owner.tasks):
        reports = owner.reports[key]
        verified = owner.attest(key, reports)
        oracle = Attestation("VERIFIED", owner.origins[key])
        for method, att in (("naive", None), ("guarded", verified),
                            ("oracle_roots", oracle)):
            state = forecast(reports, att, .8)
            result[method].append({
                "squared_error": (state["p_true"] - int(owner.truth[key])) ** 2,
                "high_confidence_wrong": (max(state["p_true"], 1 - state["p_true"]) >= .95
                    and (state["p_true"] >= .5) is not owner.truth[key]),
                "hold": not state["eligible"],
                "dependence_detected": state["signal"] == "DEPENDENCE_DISCOVERED"
            })
    return {name: {"brier": sum(x["squared_error"] for x in rows) / len(rows),
                   "overconfident_errors": sum(x["high_confidence_wrong"] for x in rows),
                   "held": sum(x["hold"] for x in rows),
                   "dependence_detected": sum(x["dependence_detected"] for x in rows)}
            for name, rows in result.items()}
