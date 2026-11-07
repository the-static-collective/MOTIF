"""MATHAL-001: typed, receipt-bearing FIR crossings (experimental, local only).

Uses FIR-001 as a constitutional gate. A locally admitted warrant is NOT an
independently checked proof; all observations are limited to declared worlds.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path
from typing import Any
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fir001"))
from fir import Claim, FIRRefusal, FIRWorld, Relation, Warrant

OPERATIONS = frozenset({"propose", "admit", "reopen", "reify", "change_carrier", "refuse"})


def identity(item: Any) -> tuple:
    """A type-tagged structural identity. No repr or count aliasing."""
    if isinstance(item, Claim):
        return ("claim", item.text, item.scope)
    if isinstance(item, Relation):
        return ("relation", item.kind, item.participants)
    if isinstance(item, str):
        return ("address", item)
    raise FIRRefusal("mathal identity supports only Claim, Relation, and string addresses")


@dataclass(frozen=True)
class Mark:
    carrier: str
    decoder: str
    addressable: tuple
    ideas: tuple
    facts: tuple
    relations: tuple


def mark(world: FIRWorld) -> Mark:
    return Mark(
        world.carrier, world.decoder,
        tuple(sorted(identity(x) for x in world.addressable)),
        tuple(sorted(identity(x) for x in world.ideas)),
        tuple(sorted((identity(x), w.kind, w.evidence, w.scope)
                     for x, w in world.facts.items())),
        tuple(sorted(identity(x) for x in world.relations)),
    )


@dataclass(frozen=True)
class Step:
    op: str
    item: Claim | Relation | str
    warrant: Warrant | None = None
    reason: str = ""
    address: str = ""

    def __post_init__(self):
        if self.op not in OPERATIONS:
            raise FIRRefusal("unrecognized operation")
        identity(self.item)
        if self.op in {"admit", "reopen"} and not isinstance(self.item, (Claim, Relation)):
            raise FIRRefusal("only claims and typed relations can bear admissions")
        if self.op == "admit" and not isinstance(self.warrant, Warrant):
            raise FIRRefusal("admission requires declared warrant")
        if self.op != "admit" and self.warrant is not None:
            raise FIRRefusal("warrant must not silently attach to unrelated operation")
        if self.op in {"reopen", "refuse"} and not self.reason:
            raise FIRRefusal("reopening/refusal must have a reason")
        if self.op == "reify" and (not isinstance(self.item, Relation) or not self.address):
            raise FIRRefusal("reification requires relation and address")
        if self.op == "change_carrier" and not isinstance(self.item, str):
            raise FIRRefusal("carrier must be an address string")
        if self.op == "propose" and not isinstance(self.item, (Claim, Relation)):
            raise FIRRefusal("proposal must be a claim or typed relation")


@dataclass(frozen=True)
class Program:
    name: str
    steps: tuple[Step, ...]
    carrier: str
    decoder: str = "identity"

    def __post_init__(self):
        if not self.name or not self.carrier or not self.decoder:
            raise FIRRefusal("program requires name and declared source interface")
        if not self.steps:
            raise FIRRefusal("empty program: use a named identity crossing explicitly")


@dataclass
class Run:
    name: str
    source: Mark
    target: Mark
    receipts: tuple[dict, ...]
    status: str
    world: FIRWorld | None = field(repr=False)
    reason: str = ""

    @property
    def applied(self) -> bool:
        return self.status == "APPLIED"


def execute(source: FIRWorld, program: Program) -> Run:
    """Execute on a private copy. An aborted path never commits partial changes."""
    before = mark(source)
    if (source.carrier, source.decoder) != (program.carrier, program.decoder):
        return Run(program.name, before, before,
                   ({"operation": "refused_interface", "expected": (program.carrier, program.decoder),
                     "actual": (source.carrier, source.decoder)},),
                   "REFUSED", None, "source interface mismatch")
    work = deepcopy(source)
    start = len(work.receipts)
    try:
        for step in program.steps:
            if step.op == "propose":
                work.propose(step.item)
            elif step.op == "admit":
                work.admit(step.item, step.warrant)
            elif step.op == "reopen":
                work.reopen(step.item, step.reason)
            elif step.op == "reify":
                work.reify(step.item, step.address)
            elif step.op == "change_carrier":
                work.change_carrier(step.item)
            elif step.op == "refuse":
                work.refuse(step.item, step.reason)
    except FIRRefusal as exc:
        # Preserve attempt history as a separate receipt, not a committed state.
        trace = tuple(deepcopy(work.receipts[start:]))
        return Run(program.name, before, before,
                   trace + ({"operation": "aborted", "reason": str(exc)},),
                   "REFUSED", None, str(exc))
    return Run(program.name, before, mark(work), tuple(deepcopy(work.receipts[start:])),
               "APPLIED", work)


def compose_runs(first: Run, second: Run) -> Run:
    """A then B, only if the COMPLETE intermediate constitutional states match."""
    if not first.applied or not second.applied:
        raise FIRRefusal("cannot compose refused or uncommitted crossings")
    if mark(first.world) != first.target or mark(second.world) != second.target:
        raise FIRRefusal("run state changed after receipt; composite would be stale")
    if first.target != second.source:
        raise FIRRefusal("intermediate FIR worlds do not match")
    return Run(f"{second.name} ∘ {first.name}", first.source, second.target,
               first.receipts + second.receipts, "APPLIED", deepcopy(second.world))


def receipt_projection(run: Run, questions: set[str]) -> dict:
    """Exact for these declared inspection queries; NOT proven globally minimal."""
    supported = {"endpoints", "path", "warrants", "refusals"}
    if questions - supported:
        raise FIRRefusal("unknown future question class")
    out = {"question_class": tuple(sorted(questions)), "status": run.status}
    if "endpoints" in questions:
        out["source"] = run.source
        out["target"] = run.target
    if "path" in questions:
        out["path"] = tuple((r.get("operation"), r.get("item")) for r in run.receipts)
    if "warrants" in questions:
        out["warrants"] = tuple((r.get("item"), r.get("kind"), r.get("evidence"),
                                 r.get("scope")) for r in run.receipts
                                if r.get("operation") == "admit")
    if "refusals" in questions:
        out["refusals"] = tuple(r for r in run.receipts
                                 if r.get("operation") in {"refuse", "aborted", "refused_admission", "refused_interface"})
    return out


def nominate_motif003(rows: list[dict]) -> list[Run]:
    """Read-only adapter: a MOTIF-003 hypothetical future becomes I, never F."""
    result = []
    for row in rows:
        operator = row["operator"]
        roles = tuple(row["roles"])
        candidate = Claim(f"hypothetical move {operator!r} roles={roles!r}",
                          "MOTIF-003 synthetic preview")
        world = FIRWorld("MOTIF-003 synthetic graph", "counterfactual")
        result.append(execute(world, Program(
            f"nominate:{operator}", (Step("propose", candidate),),
            "MOTIF-003 synthetic graph", "counterfactual")))
    return result
