"""FIR-001: an executable, deliberately small admissive-reasoning cartridge.

Claims admitted here are *locally warranted*, not automatically true. Warrant
validity outside the machine-checkable scope gate remains a human/test obligation.
"""
from dataclasses import dataclass, field
from typing import Any, Optional


class FIRRefusal(ValueError):
    """A proposed crossing is not licensed in this declared world."""


@dataclass(frozen=True)
class Warrant:
    kind: str
    evidence: str
    scope: str = ""

    def __post_init__(self):
        if self.kind not in {"proof", "finite_computation", "assumption", "external"}:
            raise ValueError("unsupported warrant type")
        if not self.evidence:
            raise ValueError("warrant must identify evidence")
        if self.kind == "finite_computation" and not self.scope:
            raise ValueError("finite computation must declare its covered scope")


@dataclass(frozen=True)
class Claim:
    text: str
    scope: str = ""

    def __post_init__(self):
        if not self.text:
            raise ValueError("empty claim")


@dataclass(frozen=True)
class Relation:
    kind: str
    participants: tuple[str, ...]

    def __post_init__(self):
        if not self.kind or not self.participants:
            raise ValueError("relation must have a type and participants")


@dataclass(frozen=True)
class Crossing:
    name: str
    source: str
    target: str
    mechanism: str
    numerical_index: Optional[tuple[int, int]] = None
    invariant: str = ""


def compose(a: Crossing, b: Crossing) -> Crossing:
    """Compose a then b, only if declared intermediate carriers match."""
    if a.target != b.source:
        raise FIRRefusal(f"composition requires {a.target!r} -> {b.source!r} bridge")
    return Crossing(f"{b.name} ∘ {a.name}", a.source, b.target,
                    f"{a.mechanism}; {b.mechanism}")


def relation_between_transitions(a: Crossing, b: Crossing, relation_type: str) -> dict:
    """Nominate a second-order comparison; do not assert shared mechanism."""
    if relation_type == "same_index":
        if a.numerical_index is None or a.numerical_index != b.numerical_index:
            raise FIRRefusal("indices are not equal")
        return {"role": "F", "relation": relation_type,
                "index": a.numerical_index, "mechanism_equal": a.mechanism == b.mechanism}
    if relation_type == "same_mechanism":
        # This is a comparison of labels, not a proof of mechanism identity.
        return {"role": "I", "relation": relation_type,
                "numeral_removal_survived": bool(a.invariant and a.invariant == b.invariant),
                "requires_independent_warrant": True}
    raise FIRRefusal("unknown second-order comparison")


@dataclass
class FIRWorld:
    carrier: str
    decoder: str = "identity"
    addressable: set[Any] = field(default_factory=set)
    ideas: set[Any] = field(default_factory=set)
    facts: dict[Any, Warrant] = field(default_factory=dict)
    relations: set[Relation] = field(default_factory=set)
    receipts: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.carrier or not self.decoder:
            raise ValueError("world must declare carrier and decoder")

    def _receipt(self, operation: str, item: Any, **metadata: Any) -> dict:
        receipt = {"operation": operation, "item": str(item),
                   "carrier": self.carrier, "decoder": self.decoder, **metadata}
        self.receipts.append(receipt)
        return receipt

    def address(self, item: Any) -> None:
        self.addressable.add(item)

    def propose(self, item: Any) -> None:
        self.address(item)
        if item not in self.facts:
            self.ideas.add(item)
        self._receipt("propose", item, admitted=item in self.facts)

    def admit(self, item: Any, warrant: Warrant) -> None:
        if item not in self.ideas:
            self._receipt("refused_admission", item, reason="proposal missing")
            raise FIRRefusal("claim must be proposed before admission")
        # A finite computation covers exactly its declared domain, never more.
        if warrant.kind == "finite_computation":
            if not isinstance(item, Claim) or item.scope != warrant.scope:
                self._receipt("refused_admission", item, reason="finite scope mismatch")
                raise FIRRefusal("finite computation cannot establish a wider claim")
        self.facts[item] = warrant
        self.ideas.discard(item)
        if isinstance(item, Relation):
            self.relations.add(item)
        self._receipt("admit", item, kind=warrant.kind,
                      evidence=warrant.evidence, scope=warrant.scope)

    def propose_relation(self, relation: Relation) -> None:
        # Does NOT infer a relation merely from admitted endpoints.
        self.propose(relation)

    def reify(self, relation: Relation, address: str) -> str:
        if relation not in self.relations:
            raise FIRRefusal("cannot reify a relation that has not been admitted")
        self.address(address)
        self._receipt("reify", relation, address=address)
        return address

    def reopen(self, item: Any, reason: str) -> None:
        if item not in self.facts:
            raise FIRRefusal("nothing admitted to reopen")
        del self.facts[item]
        self.ideas.add(item)
        if isinstance(item, Relation):
            self.relations.discard(item)
        self._receipt("reopen", item, reason=reason)

    def change_carrier(self, carrier: str) -> None:
        if not carrier:
            raise ValueError("empty carrier")
        if carrier == self.carrier:
            return
        old = self.carrier
        # Conservative: nothing admitted in the old carrier is automatically
        # admitted in the new one. Preserve all prior receipts for provenance.
        previous_facts = list(self.facts)
        for item in previous_facts:
            self.reopen(item, f"carrier changed from {old} to {carrier}")
        self.carrier = carrier
        self._receipt("change_carrier", carrier, old=old,
                      reopened=len(previous_facts))

    def refuse(self, item: Any, reason: str) -> None:
        self._receipt("refuse", item, reason=reason)

    def record_path(self, label: str, start: Any, steps: list[str], end: Any) -> None:
        self._receipt("path", label, start=repr(start), steps=steps[:], end=repr(end))

    def observe(self, value: Any, decoder_fn) -> Any:
        observation = decoder_fn(value)
        self._receipt("observe", value, observation=repr(observation))
        return observation

    def snapshot(self) -> dict:
        return {"carrier": self.carrier, "decoder": self.decoder,
                "addressable": len(self.addressable), "facts": len(self.facts),
                "ideas": len(self.ideas), "relations": len(self.relations),
                "receipts": len(self.receipts)}
