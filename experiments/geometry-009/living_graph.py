"""GEOM-008: persistent, resumable, grammar-directed PENCIL hypergraph.

No artificial lifetime node/edge/depth/arity ceiling. Every invocation has a finite
work budget; physical storage and time remain real limits. Grammar-generated
edges are hypotheses, never historical evidence or external action authority.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def stable_id(prefix: str, obj: object) -> str:
    return prefix + hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def nonempty(value: str, title: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{title} must be a non-empty string')
    return value


@dataclass(frozen=True)
class RewriteRule:
    """A fully declared, side-effect-free substring rewriting rule.

    The user can supply arbitrary rule names, find sequences and replacement
    sequences. No built-in vocabulary or fixed graph size is imposed. Empty
    patterns are allowed, creating insertion sites (including on empty seed).
    """
    name: str
    find: tuple[str, ...]
    replace: tuple[str, ...]

    def __post_init__(self) -> None:
        nonempty(self.name, 'rule name')
        for part in (*self.find, *self.replace):
            nonempty(part, 'token')
        if self.find == self.replace:
            raise ValueError('identity rewrite would add no information')

    def outcomes(self, tokens: tuple[str, ...]) -> Iterator[tuple[int, tuple[str, ...]]]:
        span = len(self.find)
        for index in range(len(tokens) - span + 1):
            if tokens[index:index + span] == self.find:
                rewritten = tokens[:index] + self.replace + tokens[index + span:]
                if rewritten != tokens:
                    yield index, rewritten


@dataclass(frozen=True)
class RewriteGrammar:
    scope: str
    rules: tuple[RewriteRule, ...]

    def __post_init__(self) -> None:
        nonempty(self.scope, 'scope')
        if not self.rules or len({x.name for x in self.rules}) != len(self.rules):
            raise ValueError('requires uniquely named rewrite rules')

    def data(self) -> dict:
        return {'scope': self.scope, 'rules': [
            {'name': r.name, 'find': list(r.find), 'replace': list(r.replace)}
            for r in self.rules]}

    @property
    def fingerprint(self) -> str:
        return stable_id('grammar:', self.data())


def grammar_from_document(doc: dict) -> RewriteGrammar:
    if set(doc) != {'scope', 'rules'} or not isinstance(doc['rules'], list):
        raise ValueError('grammar requires exactly scope and rules')
    rules = []
    for obj in doc['rules']:
        if not isinstance(obj, dict) or set(obj) != {'name', 'find', 'replace'}:
            raise ValueError('unknown rule field')
        if not isinstance(obj['find'], list) or not isinstance(obj['replace'], list):
            raise ValueError('find and replace must be arrays')
        rules.append(RewriteRule(obj['name'], tuple(obj['find']), tuple(obj['replace'])))
    return RewriteGrammar(doc['scope'], tuple(rules))


class LivingGraph:
    """SQLite-backed typed hypergraph, append-only PENCIL assertions.

    Schema uses arbitrary edge arity and edge kinds; it does not materialize an
    entire graph to query a small area. This is single-writer local prototype,
    not an authenticated, distributed or thread-safe ledger.
    """
    def __init__(self, filename: str | Path = ':memory:', *, scope: str):
        self.scope = nonempty(scope, 'scope')
        self.filename = str(filename)
        self.db = sqlite3.connect(self.filename, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA busy_timeout=5000')
        if self.filename != ':memory:':
            self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL,
                payload TEXT NOT NULL, source_root TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status='PENCIL'));
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, source_root TEXT NOT NULL,
                note TEXT NOT NULL, status TEXT NOT NULL CHECK(status='PENCIL'));
            CREATE TABLE IF NOT EXISTS participants (
                relation_id TEXT NOT NULL REFERENCES relations(id),
                ordinal INTEGER NOT NULL, node_id TEXT NOT NULL REFERENCES nodes(id),
                role TEXT NOT NULL, PRIMARY KEY(relation_id, ordinal));
            CREATE INDEX IF NOT EXISTS participants_by_node ON participants(node_id, relation_id);
            CREATE TABLE IF NOT EXISTS frontier (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL UNIQUE REFERENCES nodes(id),
                expanded INTEGER NOT NULL DEFAULT 0 CHECK(expanded IN (0, 1)));
            CREATE INDEX IF NOT EXISTS frontier_unexpanded ON frontier(expanded,sequence);
        ''')
        seen = self.db.execute("SELECT value FROM meta WHERE key='scope'").fetchone()
        if seen and seen['value'] != self.scope:
            self.db.close()
            raise ValueError('scope mismatch; no silent observer/decoder/cut crossing')
        self.db.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('scope',?)", (self.scope,))

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> LivingGraph:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _node(self, identity: str, kind: str, label: str,
              payload: object, root: str, *, enqueue: bool = False) -> bool:
        for val, title in ((identity, 'node id'), (kind, 'node kind'),
                           (label, 'node label'), (root, 'source root')):
            nonempty(val, title)
        data = canonical(payload)
        cursor = self.db.execute('INSERT OR IGNORE INTO nodes VALUES(?,?,?,?,?,?)',
                                 (identity, kind, label, data, root, 'PENCIL'))
        inserted = bool(cursor.rowcount)
        if not inserted:
            prior = self.db.execute('SELECT kind,label,payload FROM nodes WHERE id=?', (identity,)).fetchone()
            if (prior['kind'], prior['label'], prior['payload']) != (kind, label, data):
                raise ValueError('identity collision / changed node definition')
        if enqueue:
            self.db.execute('INSERT OR IGNORE INTO frontier(node_id) VALUES(?)', (identity,))
        return inserted

    def add_node(self, identity: str, *, kind: str, label: str, payload: object,
                 source_root: str) -> bool:
        return self._node(identity, kind, label, payload, source_root)

    @staticmethod
    def expression_id(tokens: Sequence[str]) -> str:
        return stable_id('expr:', list(tokens))

    def _expression(self, tokens: tuple[str, ...], root: str) -> tuple[str, bool]:
        if any(not isinstance(t, str) or not t.strip() for t in tokens):
            raise ValueError('expression tokens must be non-empty strings')
        identity = self.expression_id(tokens)
        # Label is only a readable preview; the complete expression is in payload.
        label = (' '.join(tokens) or '<empty>')[:240]
        inserted = self._node(identity, 'expression', label, list(tokens), root, enqueue=True)
        return identity, inserted

    def seed(self, tokens: Sequence[str], *, source_root: str = 'seed:declared') -> str:
        nonempty(source_root, 'source root')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            identity, _ = self._expression(tuple(tokens), source_root)
            self.db.execute('COMMIT')
            return identity
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def _relation(self, kind: str, participants: Sequence[tuple[str, str]],
                  root: str, note: object) -> bool:
        nonempty(kind, 'relation kind'); nonempty(root, 'source root')
        if not participants:
            raise ValueError('a relation needs at least one participant')
        for role, node in participants:
            nonempty(role, 'participant role'); nonempty(node, 'participant node')
            if not self.db.execute('SELECT 1 FROM nodes WHERE id=?', (node,)).fetchone():
                raise ValueError('relation references missing node')
        record = {'kind': kind, 'scope': self.scope, 'endpoints': list(participants),
                  'source_root': root, 'note': note}
        identity = stable_id('rel:', record)
        cursor = self.db.execute('INSERT OR IGNORE INTO relations VALUES(?,?,?,?,?)',
                                 (identity, kind, root, canonical(note), 'PENCIL'))
        if cursor.rowcount:
            self.db.executemany('INSERT INTO participants VALUES(?,?,?,?)',
                                ((identity, index, node, role)
                                 for index, (role, node) in enumerate(participants)))
            return True
        return False

    def add_relation(self, kind: str, participants: Sequence[tuple[str, str]],
                     *, source_root: str, note: object = None) -> bool:
        """Arbitrary typed, attributed N-ary relation, no hard arity ceiling."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            created = self._relation(kind, participants, source_root, note)
            self.db.execute('COMMIT')
            return created
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def bind_grammar(self, grammar: RewriteGrammar) -> None:
        if grammar.scope != self.scope:
            raise ValueError('grammar scope mismatch')
        row = self.db.execute("SELECT value FROM meta WHERE key='grammar'").fetchone()
        if row and row['value'] != grammar.fingerprint:
            raise ValueError('cannot silently replace the expansion grammar; fork the graph')
        self.db.execute("INSERT OR IGNORE INTO meta VALUES('grammar',?)", (grammar.fingerprint,))
        self.db.execute("INSERT OR IGNORE INTO meta VALUES('grammar_declaration',?)", (canonical(grammar.data()),))

    def grow(self, grammar: RewriteGrammar, *, work_budget: int,
             seconds: float | None = None) -> dict:
        """Resume a persistent frontier, processing at most work_budget nodes.

        Work budget is per invocation, not a graph size or depth limit. No
        inferred hypothesis becomes admitted evidence. Atomic per-node work.
        """
        if type(work_budget) is not int or work_budget <= 0:
            raise ValueError('positive integer work_budget required')
        if seconds is not None and (type(seconds) not in (int, float) or not 0 < seconds < float('inf')):
            raise ValueError('seconds must be a positive finite number')
        self.bind_grammar(grammar)
        deadline = time.monotonic() + seconds if seconds else None
        before = self.counts()
        expanded = 0
        stop = 'WORK_SLICE_COMPLETE'
        while expanded < work_budget:
            if deadline is not None and time.monotonic() >= deadline:
                stop = 'TIME_SLICE_COMPLETE'
                break
            row = self.db.execute('''SELECT frontier.sequence,frontier.node_id,nodes.payload
                    FROM frontier JOIN nodes ON frontier.node_id=nodes.id
                    WHERE expanded=0 ORDER BY sequence LIMIT 1''').fetchone()
            if row is None:
                stop = 'SATURATED_FOR_CURRENT_GRAMMAR'
                break
            tokens = tuple(json.loads(row['payload']))
            self.db.execute('BEGIN IMMEDIATE')
            try:
                children = set()
                for rule in grammar.rules:
                    for position, outcome in rule.outcomes(tokens):
                        child, _ = self._expression(outcome, f'grammar:{grammar.fingerprint}')
                        children.add(child)
                        self._relation('rewrite', [('from', row['node_id']), ('to', child)],
                                       f'grammar:{grammar.fingerprint}',
                                       {'rule': rule.name, 'position': position})
                # An n-ary sibling/fork relation: any number of children, not a
                # prewired 13-circle/2-edge hierarchy or flat binary-only graph.
                if len(children) > 1:
                    self._relation('branch', [('parent', row['node_id'])] +
                                   [('child', child) for child in sorted(children)],
                                   f'grammar:{grammar.fingerprint}',
                                   {'kind': 'co-produced', 'semantics': 'hypothetical'})
                self.db.execute('UPDATE frontier SET expanded=1 WHERE sequence=?', (row['sequence'],))
                self.db.execute('COMMIT')
            except BaseException:
                self.db.execute('ROLLBACK')
                raise
            expanded += 1
        after = self.counts()
        return {'status': stop, 'expanded_this_slice': expanded,
                'new_nodes': after['nodes'] - before['nodes'],
                'new_relations': after['relations'] - before['relations'],
                'totals': after, 'state': 'PENCIL', 'authority': 'NONE',
                'grammar': grammar.fingerprint}

    def counts(self) -> dict:
        nodes = self.db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
        relations = self.db.execute('SELECT COUNT(*) FROM relations').fetchone()[0]
        frontier = self.db.execute('SELECT COUNT(*) FROM frontier WHERE expanded=0').fetchone()[0]
        depth = self.db.execute('SELECT COUNT(*) FROM frontier WHERE expanded=1').fetchone()[0]
        pages = self.db.execute('PRAGMA page_count').fetchone()[0]
        page_size = self.db.execute('PRAGMA page_size').fetchone()[0]
        return {'nodes': nodes, 'relations': relations, 'unexpanded': frontier,
                'expanded': depth, 'db_bytes_allocated_approx': pages * page_size}

    def node_page(self, *, after: str = '', page_size: int = 32) -> dict:
        if type(page_size) is not int or page_size <= 0:
            raise ValueError('page_size must be positive integer')
        rows = self.db.execute('''SELECT id,kind,label,status FROM nodes
                                  WHERE id>? ORDER BY id LIMIT ?''',
                               (after, page_size + 1)).fetchall()
        batch = rows[:page_size]
        return {'nodes': [dict(r) for r in batch],
                'next_cursor': batch[-1]['id'] if len(rows) > page_size else None,
                'authority': 'NONE'}

    def relation_page(self, *, after: str = '', page_size: int = 32) -> dict:
        if type(page_size) is not int or page_size <= 0:
            raise ValueError('page_size must be positive integer')
        rows = self.db.execute('''SELECT id,kind,source_root,status FROM relations
                                  WHERE id>? ORDER BY id LIMIT ?''',
                               (after, page_size + 1)).fetchall()
        batch = rows[:page_size]
        return {'relations': [dict(r) for r in batch],
                'next_cursor': batch[-1]['id'] if len(rows) > page_size else None,
                'authority': 'NONE'}

    def neighborhood(self, center: str, *, hops: int = 1,
                     node_budget: int = 50, relation_budget: int = 100) -> dict:
        if type(hops) is not int or hops < 0 or type(node_budget) is not int or node_budget <= 0 \
                or type(relation_budget) is not int or relation_budget <= 0:
            raise ValueError('invalid display budgets')
        if not self.db.execute('SELECT 1 FROM nodes WHERE id=?', (center,)).fetchone():
            raise ValueError('unknown center node')
        chosen = {center}
        front = [center]
        relation_ids = set()
        truncated = False
        for _ in range(hops):
            nxt = []
            for node in front:
                ids = self.db.execute('''SELECT relation_id FROM participants
                        WHERE node_id=? ORDER BY relation_id LIMIT ?''',
                                      (node, relation_budget + 1)).fetchall()
                if len(ids) > relation_budget:
                    truncated = True
                for ridrow in ids:
                    rid = ridrow['relation_id']
                    if rid not in relation_ids and len(relation_ids) >= relation_budget:
                        truncated = True
                        break
                    participants = self.db.execute('''SELECT node_id FROM participants
                            WHERE relation_id=? ORDER BY ordinal''', (rid,)).fetchall()
                    endpoints = [r['node_id'] for r in participants]
                    if len(chosen | set(endpoints)) > node_budget:
                        truncated = True
                        continue
                    relation_ids.add(rid)
                    for endpoint in endpoints:
                        if endpoint not in chosen:
                            chosen.add(endpoint); nxt.append(endpoint)
            if not nxt:
                break
            front = nxt
        nodes = [dict(self.db.execute('''SELECT id,kind,label,status FROM nodes
                              WHERE id=?''', (n,)).fetchone()) for n in sorted(chosen)]
        relations = []
        for rid in sorted(relation_ids):
            relation = dict(self.db.execute('''SELECT id,kind,source_root,status
                            FROM relations WHERE id=?''', (rid,)).fetchone())
            relation['participants'] = [dict(r) for r in self.db.execute('''SELECT role,node_id
                             FROM participants WHERE relation_id=? ORDER BY ordinal''', (rid,))]
            relations.append(relation)
        return {'center': center, 'nodes': nodes, 'relations': relations,
                'partial_view': truncated or len(chosen) < self.db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
                or len(relation_ids) < self.db.execute('SELECT COUNT(*) FROM relations').fetchone()[0],
                'note': 'bounded view only; not a graph-size limit or evidence of proximity',
                'authority': 'NONE', 'state': 'PENCIL'}

    def verify(self) -> dict:
        checks = list(self.db.execute('PRAGMA foreign_key_check'))
        return {'foreign_key_errors': len(checks), 'integrity': self.db.execute('PRAGMA integrity_check').fetchone()[0]}


def run_document(data: dict, filename: str | Path = ':memory:') -> dict:
    """Explicit local-only machine interface; never invokes outside services."""
    allowed = {'grammar', 'seed', 'source_root', 'work_budget', 'seconds', 'view'}
    if not isinstance(data, dict) or set(data) - allowed:
        raise ValueError('unknown graph request field')
    grammar = grammar_from_document(data['grammar'])
    if not isinstance(data['seed'], list):
        raise ValueError('seed must be a list')
    with LivingGraph(filename, scope=grammar.scope) as graph:
        origin = graph.seed(data['seed'], source_root=data.get('source_root', 'seed:declared'))
        outcome = graph.grow(grammar, work_budget=data.get('work_budget', 128),
                             seconds=data.get('seconds'))
        view = data.get('view', {})
        if not isinstance(view, dict) or set(view) - {'hops', 'node_budget', 'relation_budget'}:
            raise ValueError('unknown view field')
        return {'seed_id': origin, 'growth': outcome,
                'local_view': graph.neighborhood(origin, **view), 'integrity': graph.verify()}
