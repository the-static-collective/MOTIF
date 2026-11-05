"""LAW-FORGE-009: a finite, inspectable grammar-inadequacy certificate.

When NO program in the frozen 650-rule hypothesis language agrees with all
witnessed outcomes, reduce the contradictory evidence to an irreducible
unsatisfiable core. This is a proof relative to the *declared rule library*,
not proof that natural reality is inconsistent or that an operator is new.

The core contains only actual owner-provided source observations and cannot
independently authorize new source APIs, Python code, network or GRAFT intake.
"""
from __future__ import annotations
from dataclasses import dataclass
from entropy_cartridge import EntropyCartridge, SCHEMA as CARTRIDGE_SCHEMA
from learner import fitted_indices, digest, controls


@dataclass(frozen=True)
class GrammarGap:
    cartridge_id: str
    language_digest: str
    source_digest: str
    witness_core: tuple[tuple[tuple[int, ...], int], ...]
    rule_library_size: int
    full_evidence_count: int

    @property
    def id(self):
        return "grammar-gap-" + digest({
            "cartridge": self.cartridge_id,
            "language": self.language_digest,
            "source": self.source_digest,
            "core": [[list(x), y] for x, y in self.witness_core]
        })[:24]

    def packet(self):
        return {
            "schema": "motif.reason-cartridge.grammar-gap.v1",
            "id": self.id,
            "cartridge_id": self.cartridge_id,
            "hypothesis_language_digest": self.language_digest,
            "source_evidence_digest": self.source_digest,
            "witness_core": [[list(x), y] for x, y in self.witness_core],
            "candidate_rule_count": self.rule_library_size,
            "full_evidence_count": self.full_evidence_count,
            "status": "HOLD_NO_RULE_IN_DECLARED_GRAMMAR",
            "proposal": "REQUEST_SOURCE_OWNED_GRAMMAR_REVIEW_ONLY",
            "real_world_authority": False
        }


def diagnose(cartridge):
    if not isinstance(cartridge, EntropyCartridge):
        raise ValueError("Only a typed frozen entropy cartridge may be diagnosed")
    from entropy_cartridge import hypothesis_digest
    from learner import rule_library
    if cartridge.survivor_indices:
        return None
    core = list(cartridge.snapshot)
    if not core:
        raise AssertionError("Snapshot not allowed empty")
    # Removing any row would leave at least one candidate if a minimal
    # unsatisfiable core is reached. Deterministic order ensures reproducibility.
    changed = True
    while changed:
        changed = False
        for sample in tuple(core):
            trial = [row for row in core if row != sample]
            if trial and not fitted_indices(trial):
                core = trial
                changed = True
    assert not fitted_indices(core)
    assert all(fitted_indices([row for row in core if row != witness])
               for witness in core)
    return GrammarGap(
        cartridge_id=cartridge.id,
        language_digest=hypothesis_digest(),
        source_digest=cartridge.source_digest,
        witness_core=tuple(core),
        rule_library_size=len(rule_library()),
        full_evidence_count=len(cartridge.snapshot)
    )


def independent_core_check(cartridge, receipt):
    """No claim of owner signature; check mathematical entailment of gap."""
    if not isinstance(cartridge, EntropyCartridge) or not isinstance(receipt, GrammarGap):
        return False
    if (receipt.cartridge_id != cartridge.id or
            receipt.source_digest != cartridge.source_digest or
            not set(receipt.witness_core) <= set(cartridge.snapshot)):
        return False
    return (len(fitted_indices(receipt.witness_core)) == 0 and
            all(bool(fitted_indices([
                row for row in receipt.witness_core if row != witness
            ])) for witness in receipt.witness_core))
