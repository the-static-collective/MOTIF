"""MOTIF-026F: cached passive T5 encoder behind a native-first gate.

The encoder produces a *semantic hint*, not a witness. Only public-safe,
operator-projected synthetic text is accepted. Models are loaded explicitly
from an existing offline cache; no remote inference or downloads.

Reuses 025F's real T5 encoder and frozen 12-case missing-gate references.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import time
from typing import Protocol

ROOT = Path(__file__).resolve().parents[1]
for folder in ("021f", "025f"):
    path = str(ROOT / folder)
    if path not in sys.path:
        sys.path.append(path)

from chorus import PublicProjection
from encoder_interview import dense_embeddings, choose_nearest, sparse_reference_vectors, sparse_sim
from frozen_jobs import CASES, JOBS, frozen_digest
from native_careers import native_rule
from semantic_sentinel import GATES


class SemanticClassifier(Protocol):
    name: str
    def classify(self, text: str) -> tuple[str, float]: ...


def operator_projection(text: str) -> PublicProjection:
    return PublicProjection(
        problem="SIMULATED human planning note; bounded semantic review only.",
        facts=(text,),
        uncertainties=("No actual field source or permission has been verified by this note.",),
        proposed_next="Find a possible missing requirement for independent review, or HOLD.",
    )


REFERENCES = tuple(c for c in CASES if c.job == "MISSING_GATE")
LABELS = tuple(c.gold for c in REFERENCES)
NATIVE_JOB = next(j for j in JOBS if j.id == "MISSING_GATE")


class CachedT5GateClassifier:
    """One real T5 encoder, cached synthetic prototypes, query embeddings only."""
    name = "REAL_FLAN_T5_ENCODER_CACHED_1NN"

    def __init__(self, model):
        self.model = model
        self.vectors, self.build_seconds = dense_embeddings(
            model, [c.note for c in REFERENCES]
        )
        self.total_queries = 0
        self.total_query_seconds = 0.0
        self.reference_digest = frozen_digest()

    def classify(self, text: str) -> tuple[str, float]:
        vectors, seconds = dense_embeddings(self.model, [text])
        self.total_queries += 1
        self.total_query_seconds += seconds
        scores = [sum(a * b for a, b in zip(row, vectors[0])) for row in self.vectors]
        return choose_nearest(scores, LABELS, k=1), max(scores)


class ClassicalGateClassifier:
    """Equal-source classical TF-IDF comparator, no paid or model inference."""
    name = "CLASSICAL_TFIDF_1NN"

    def __init__(self):
        self.queries = 0

    def classify(self, text: str) -> tuple[str, float]:
        source, target = sparse_reference_vectors(
            [c.note for c in REFERENCES], [text],
        )
        self.queries += 1
        scores = [sparse_sim(row, target[0]) for row in source]
        return choose_nearest(scores, LABELS, k=1), max(scores)


@dataclass(frozen=True)
class GateHint:
    status: str
    possible_gate: str | None
    text_question: str | None
    similarity: float | None
    origin: str
    note_sha256: str
    source_corpus_digest: str = frozen_digest()
    audience: str = "LOCAL_OPERATOR_REVIEW_ONLY"
    evidence_authority: str = "NONE"
    may_contact_or_dispatch: bool = False


def route_semantic_hint(
    text: str, classifier: SemanticClassifier | None,
) -> GateHint:
    """Native-first route; never convert a semantic label into a field fact."""
    projected = operator_projection(text)  # size/privacy rejection happens first
    digest = projected.digest()
    first = native_rule(NATIVE_JOB, text)
    if first not in GATES:
        raise ValueError("HOLD_NATIVE_OUT_OF_KNOWN_GRAMMAR")
    if first != "NONE":
        return GateHint(
            "NATIVE_REVIEW_QUESTION", first, GATES[first], None,
            "NATIVE_LEXICAL_RULE", digest,
        )
    if classifier is None:
        return GateHint(
            "HOLD_MODEL_UNAVAILABLE", None, None, None,
            "NO_MODEL", digest,
        )
    label, similarity = classifier.classify(text)
    if label not in GATES:
        return GateHint(
            "HOLD_UNREGISTERED_SEMANTIC_LABEL", None, None, similarity,
            classifier.name, digest,
        )
    if label == "NONE":
        return GateHint(
            "HOLD_NO_MISSING_GATE_SUGGESTED", None, None, similarity,
            classifier.name, digest,
        )
    return GateHint(
        "UNVERIFIED_SEMANTIC_QUESTION", label, GATES[label],
        round(similarity, 6), classifier.name, digest,
    )
