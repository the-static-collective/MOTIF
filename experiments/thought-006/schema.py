"""MOTIF THOUGHT-006: conservative, typed ledger v1.

These declarations describe *working models*. A source label is not proof of
identity, evidence isn't ground truth, and PEN never authorizes outside action.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

SCHEMA = 'motif.thought-ledger.event.v1'
GENESIS = '0' * 64
SUPPORTED_SOURCE_CLASSES = frozenset({
    'human_statement', 'document_excerpt', 'validated_fixture',
    'computation', 'inference', 'analogy',
})
PEN_SUPPORT_CLASSES = frozenset({
    'human_statement', 'document_excerpt', 'validated_fixture', 'computation'
})
ALLOWED_PREDICATES = frozenset({
    'associated', 'enables', 'requires', 'contradicts',
    'co_mentioned', 'might_relate', 'different_from',
})
EVENT_TYPES = frozenset({
    'NODE', 'SOURCE', 'SKETCH', 'SUPPORT', 'CHALLENGE',
    'COMMIT', 'WITHDRAW', 'REOPEN',
})


def canonical(value: object) -> bytes:
    """Stable exact JSON, rejects NaNs and non-JSON values."""
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(',', ':')).encode('utf-8')


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    kind: str = 'concept'


@dataclass(frozen=True)
class Source:
    id: str
    root: str    # asserted origin/dependency root, NOT authenticated
    source_class: str
    note: str


@dataclass
class Assertion:
    id: str
    subject: str
    predicate: str
    object: str
    scope: str
    idea: str
    introduced_by: str
    observed_input: bool = False
    revision: int = 1
    mode: str = 'PENCIL'
    status: str = 'SKETCH'
    supports: dict[str, str] = field(default_factory=dict)    # source -> explanation
    challenges: dict[str, str] = field(default_factory=dict)  # source -> explanation
    dispositions: list[dict] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)


def nonempty_text(x: object, name: str, *, limit=400) -> str:
    if not isinstance(x, str) or not x.strip() or len(x) > limit:
        raise ValueError(f'{name}: required bounded text')
    return x


def identifier(x: object, name: str) -> str:
    s = nonempty_text(x, name, limit=120)
    if s.strip() != s or any(ch.isspace() for ch in s):
        raise ValueError(f'{name}: IDs cannot contain whitespace')
    return s
