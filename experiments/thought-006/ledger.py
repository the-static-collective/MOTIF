"""Pencil -> pen as a fail-closed, deterministic, locally replayable event log.

Hash chaining catches accidental alteration and inconsistent replay, not a
malicious author able to rewrite the entire chain. No authenticated users,
remote actions, shared-service permissions or external tools are involved.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

from schema import (ALLOWED_PREDICATES, EVENT_TYPES, GENESIS,
                    PEN_SUPPORT_CLASSES, SCHEMA, SUPPORTED_SOURCE_CLASSES,
                    Assertion, Node, Source, canonical, digest, identifier,
                    nonempty_text)


class LedgerError(ValueError):
    """Invalid event, policy violation or corrupted/stale history."""


class ThoughtLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._events: list[dict] = []
        self.nodes: dict[str, Node] = {}
        self.sources: dict[str, Source] = {}
        self.assertions: dict[str, Assertion] = {}
        self._loaded_bytes = b''
        self.reload()

    def reload(self) -> None:
        data = self.path.read_bytes() if self.path.exists() else b''
        if len(data) > 4_000_000:
            raise LedgerError('log exceeds 4MB prototype ceiling')
        if data and not data.endswith(b'\n'):
            raise LedgerError('partial event line: refuse replay')
        self.nodes, self.sources, self.assertions = {}, {}, {}
        self._events = []
        previous = GENESIS
        for i, line in enumerate(data.splitlines(), 1):
            try:
                ev = json.loads(line)
            except (UnicodeDecodeError, ValueError) as e:
                raise LedgerError(f'non-JSON event at line {i}') from e
            if not isinstance(ev, dict) or set(ev) != {
                'schema', 'sequence', 'event_id', 'type', 'payload', 'previous', 'digest'
            }:
                raise LedgerError(f'bad event envelope at line {i}')
            body = {k: v for k, v in ev.items() if k != 'digest'}
            if (ev['schema'] != SCHEMA or type(ev['sequence']) is not int or
                ev['sequence'] != i or ev['event_id'] != f'e-{i:06d}' or
                ev['type'] not in EVENT_TYPES or ev['previous'] != previous or
                ev['digest'] != digest(body) or
                line != canonical(ev)):
                raise LedgerError(f'chain/schema violation at line {i}')
            self._apply(ev['type'], ev['payload'], ev['sequence'])
            previous = ev['digest']
            self._events.append(ev)
        self._loaded_bytes = data

    def _require_source(self, source_id: str) -> Source:
        if source_id not in self.sources:
            raise LedgerError('unknown source')
        return self.sources[source_id]

    def _require_assertion(self, assertion_id: str) -> Assertion:
        if assertion_id not in self.assertions:
            raise LedgerError('unknown assertion')
        return self.assertions[assertion_id]

    def _apply(self, event_type: str, payload: object, sequence: int) -> None:
        if not isinstance(payload, dict):
            raise LedgerError('event payload must be an object')
        spec = {
            'NODE': {'id', 'label', 'kind'},
            'SOURCE': {'id', 'root', 'source_class', 'note'},
            'SKETCH': {'id', 'subject', 'predicate', 'object', 'scope', 'idea',
                       'introduced_by', 'observed_input'},
            'SUPPORT': {'assertion_id', 'source_id', 'explanation'},
            'CHALLENGE': {'assertion_id', 'source_id', 'explanation'},
            'COMMIT': {'assertion_id', 'actor', 'justification', 'policy'},
            'WITHDRAW': {'assertion_id', 'actor', 'reason'},
            'REOPEN': {'assertion_id', 'actor', 'reason'},
        }
        if event_type not in spec or set(payload) != spec[event_type]:
            raise LedgerError('unknown event or exact payload field mismatch')
        p = payload
        try:
            if event_type == 'NODE':
                node = Node(identifier(p['id'], 'node id'),
                            nonempty_text(p['label'], 'label'),
                            identifier(p['kind'], 'kind'))
                if node.id in self.nodes:
                    raise LedgerError('duplicate node id')
                self.nodes[node.id] = node
            elif event_type == 'SOURCE':
                source = Source(identifier(p['id'], 'source id'),
                                identifier(p['root'], 'source root'),
                                identifier(p['source_class'], 'source_class'),
                                nonempty_text(p['note'], 'source note'))
                if source.source_class not in SUPPORTED_SOURCE_CLASSES:
                    raise LedgerError('unknown source class')
                if source.id in self.sources:
                    raise LedgerError('duplicate source id')
                self.sources[source.id] = source
            elif event_type == 'SKETCH':
                aid = identifier(p['id'], 'assertion id')
                if aid in self.assertions:
                    raise LedgerError('duplicate assertion id')
                sub, obj = identifier(p['subject'], 'subject'), identifier(p['object'], 'object')
                if sub not in self.nodes or obj not in self.nodes:
                    raise LedgerError('unknown concept endpoint')
                if sub == obj:
                    raise LedgerError('self-edge requires a separate future contract')
                pred = identifier(p['predicate'], 'predicate')
                if pred not in ALLOWED_PREDICATES:
                    raise LedgerError('unknown predicate')
                scope = nonempty_text(p['scope'], 'scope')
                if scope.lower() in ('*', 'global', 'universal', 'everything'):
                    raise LedgerError('unbounded scope cannot be adopted')
                introduced = identifier(p['introduced_by'], 'introduced_by')
                self._require_source(introduced)
                if type(p['observed_input']) is not bool:
                    raise LedgerError('observed_input must be boolean')
                self.assertions[aid] = Assertion(
                    id=aid, subject=sub, predicate=pred, object=obj,
                    scope=scope, idea=nonempty_text(p['idea'], 'idea', limit=1000),
                    introduced_by=introduced, observed_input=p['observed_input'])
            elif event_type in ('SUPPORT', 'CHALLENGE'):
                a = self._require_assertion(identifier(p['assertion_id'], 'assertion id'))
                source = self._require_source(identifier(p['source_id'], 'source id'))
                explanation = nonempty_text(p['explanation'], 'explanation', limit=1000)
                if a.mode != 'PENCIL' and event_type == 'SUPPORT':
                    raise LedgerError('support requires a pencil revision')
                bucket = a.supports if event_type == 'SUPPORT' else a.challenges
                if source.id in bucket:
                    raise LedgerError('duplicate evidence source on current revision')
                bucket[source.id] = explanation
                if event_type == 'CHALLENGE' and a.mode == 'PEN':
                    a.status = 'PEN_CHALLENGED'
                elif event_type == 'CHALLENGE' and a.mode == 'PENCIL':
                    a.status = 'PENCIL_CHALLENGED'
            elif event_type == 'COMMIT':
                a = self._require_assertion(identifier(p['assertion_id'], 'assertion id'))
                actor = identifier(p['actor'], 'reviewer')
                explanation = nonempty_text(p['justification'], 'review justification', limit=1000)
                if p['policy'] != 'STRICT_LOCAL_REVIEW_V1':
                    raise LedgerError('unrecognized pen policy')
                if a.mode != 'PENCIL':
                    raise LedgerError('only pencil can become pen')
                if a.challenges:
                    raise LedgerError('challenged sketch cannot be committed; revise, do not erase')
                eligible = {self.sources[sid].root for sid in a.supports
                            if self.sources[sid].source_class in PEN_SUPPORT_CLASSES}
                if len(eligible) < 2:
                    raise LedgerError('two independent claimed evidence roots required')
                # An actor string identifies a *claimed reviewer*, not authentication.
                a.mode, a.status = 'PEN', 'PEN_SCOPED'
                a.dispositions.append({
                    'event': sequence, 'revision': a.revision, 'decision': 'PEN_SCOPED',
                    'actor': actor, 'justification': explanation,
                    'evidence_roots': sorted(eligible), 'policy': p['policy'],
                    'external_authority': 'NONE',
                })
            elif event_type == 'WITHDRAW':
                a = self._require_assertion(identifier(p['assertion_id'], 'assertion id'))
                actor = identifier(p['actor'], 'actor')
                why = nonempty_text(p['reason'], 'reason')
                if a.mode != 'PEN':
                    raise LedgerError('only a pen commitment can be withdrawn')
                a.mode, a.status = 'RETIRED', 'WITHDRAWN'
                a.dispositions.append({
                    'event': sequence, 'revision': a.revision, 'decision': 'WITHDRAWN',
                    'actor': actor, 'justification': why, 'external_authority': 'NONE',
                })
            elif event_type == 'REOPEN':
                a = self._require_assertion(identifier(p['assertion_id'], 'assertion id'))
                actor = identifier(p['actor'], 'actor')
                why = nonempty_text(p['reason'], 'reason')
                if a.mode not in ('PEN', 'RETIRED'):
                    raise LedgerError('reopen needs a prior pen conclusion')
                a.dispositions.append({
                    'event': sequence, 'revision': a.revision, 'decision': 'REOPENED',
                    'actor': actor, 'justification': why, 'external_authority': 'NONE',
                })
                a.mode, a.status = 'PENCIL', 'REOPENED'
                a.revision += 1
                # Prior evidence lives in prior journal events and dispositions;
                # new revision must independently restate support and objections.
                a.supports, a.challenges = {}, {}
        except (KeyError, TypeError) as e:
            raise LedgerError(f'invalid {event_type} fields') from e

    def _append(self, kind: str, payload: dict) -> dict:
        # Optimistic single-writer guard: no stale append after an outside edit.
        current = self.path.read_bytes() if self.path.exists() else b''
        if current != self._loaded_bytes:
            raise LedgerError('disk ledger changed: reload before appending')
        sequence = len(self._events) + 1
        body = {'schema': SCHEMA, 'sequence': sequence,
                'event_id': f'e-{sequence:06d}', 'type': kind,
                'payload': payload, 'previous': self.head_digest}
        ev = {**body, 'digest': digest(body)}
        # Validate against an isolated copy before mutating/persisting anything.
        saved = self.nodes, self.sources, self.assertions
        self.nodes, self.sources, self.assertions = copy.deepcopy(saved)
        try:
            self._apply(kind, payload, sequence)
        except Exception:
            self.nodes, self.sources, self.assertions = saved
            raise
        if len(current) + len(canonical(ev)) + 1 > 4_000_000:
            self.nodes, self.sources, self.assertions = saved
            raise LedgerError('log size ceiling')
        record = canonical(ev) + b'\n'
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('ab') as fp:
                fp.write(record)
                fp.flush()
                os.fsync(fp.fileno())
        except Exception:
            self.nodes, self.sources, self.assertions = saved
            raise
        self._loaded_bytes += record
        self._events.append(ev)
        return ev

    @property
    def head_digest(self) -> str:
        return self._events[-1]['digest'] if self._events else GENESIS

    def register_node(self, id: str, label: str, kind='concept') -> dict:
        return self._append('NODE', dict(id=id, label=label, kind=kind))

    def register_source(self, id: str, root: str, source_class: str,
                        note: str) -> dict:
        return self._append('SOURCE', dict(id=id, root=root,
                                           source_class=source_class, note=note))

    def sketch(self, id: str, subject: str, predicate: str, object: str,
               scope: str, idea: str, introduced_by: str,
               *, observed_input=False) -> dict:
        return self._append('SKETCH', dict(id=id, subject=subject, predicate=predicate,
                                           object=object, scope=scope, idea=idea,
                                           introduced_by=introduced_by,
                                           observed_input=observed_input))

    def support(self, assertion_id: str, source_id: str, explanation: str) -> dict:
        return self._append('SUPPORT', dict(assertion_id=assertion_id,
                                           source_id=source_id, explanation=explanation))

    def challenge(self, assertion_id: str, source_id: str, explanation: str) -> dict:
        return self._append('CHALLENGE', dict(assertion_id=assertion_id,
                                             source_id=source_id, explanation=explanation))

    def commit(self, assertion_id: str, actor: str, justification: str,
               *, policy='STRICT_LOCAL_REVIEW_V1') -> dict:
        return self._append('COMMIT', dict(assertion_id=assertion_id, actor=actor,
                                          justification=justification, policy=policy))

    def withdraw(self, assertion_id: str, actor: str, reason: str) -> dict:
        return self._append('WITHDRAW', dict(assertion_id=assertion_id,
                                            actor=actor, reason=reason))

    def reopen(self, assertion_id: str, actor: str, reason: str) -> dict:
        return self._append('REOPEN', dict(assertion_id=assertion_id,
                                          actor=actor, reason=reason))

    def snapshot(self) -> dict:
        """One deterministic semantic snapshot, independent of drawings."""
        return {
            'schema': 'motif.thought-ledger.snapshot.v1',
            'head_digest': self.head_digest,
            'events': len(self._events),
            'nodes': [vars(self.nodes[k]).copy() for k in sorted(self.nodes)],
            'sources': [vars(self.sources[k]).copy() for k in sorted(self.sources)],
            'assertions': [self.assertions[k].to_json()
                           for k in sorted(self.assertions)],
            'effective_external_authority': 'NONE',
        }

    def receipt(self, assertion_id: str) -> dict:
        a = self._require_assertion(assertion_id)
        support_roots = {self.sources[x].root for x in a.supports}
        opposition_roots = {self.sources[x].root for x in a.challenges}
        return {
            'assertion_id': a.id, 'revision': a.revision,
            'instrument': a.mode, 'status': a.status, 'scope': a.scope,
            'supports': sorted(a.supports), 'support_roots': sorted(support_roots),
            'opposes': sorted(a.challenges), 'opposition_roots': sorted(opposition_roots),
            'dispositions': copy.deepcopy(a.dispositions),
            'chain_tip': self.head_digest, 'effective_external_authority': 'NONE',
        }

    def history(self) -> list[dict]:
        return copy.deepcopy(self._events)
