"""One end-to-end synthetic pencil -> pen -> challenged -> withdrawn -> reopened demonstration."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ledger import ThoughtLedger, LedgerError


def run_demo() -> dict:
    with TemporaryDirectory(prefix='motif-thought006-') as d:
        path = Path(d) / 'thought-events.jsonl'
        l = ThoughtLedger(path)
        l.register_node('food-shelf', 'Food shelf')
        l.register_node('community-meal', 'Community meal')
        l.register_source('idea', 'root:idea', 'inference', 'Synthetic initial sketch')
        l.register_source('counterexample', 'root:missed-meal', 'validated_fixture',
                          'Synthetic missed meal despite stocked shelf')
        l.register_source('echo', 'root:storage', 'validated_fixture',
                          'Repetition of the same storage-origin witness')
        l.register_source('storage', 'root:storage', 'validated_fixture',
                          'Synthetic storage availability fixture')
        l.register_source('volunteer', 'root:staff', 'validated_fixture',
                          'Synthetic scheduled volunteer fixture')
        l.register_source('cancellation', 'root:closure', 'validated_fixture',
                          'Synthetic late closure fixture')
        l.sketch('universal', 'food-shelf', 'enables', 'community-meal',
                 'fixture:all-days', 'A stocked shelf always guarantees a meal', 'idea')
        l.challenge('universal', 'counterexample', 'One trial had no volunteers')
        blocked = False
        try:
            l.commit('universal', 'fixture-reviewer', 'A tempting but false broad conclusion')
        except LedgerError:
            blocked = True
        assert blocked
        l.sketch('scoped', 'food-shelf', 'enables', 'community-meal',
                 'fixture:Friday-with-volunteers',
                 'In this simulation the shelf can supply the meal when storage and staffing hold',
                 'idea')
        l.support('scoped', 'storage', 'Storage availability in the scoped fixture')
        l.support('scoped', 'echo', 'Copied storage evidence: NOT another independent root')
        rejected_echoes = False
        try:
            l.commit('scoped', 'fixture-reviewer', 'Only storage-origin echoes')
        except LedgerError:
            rejected_echoes = True
        assert rejected_echoes
        l.support('scoped', 'volunteer', 'Separate synthetic staffing fixture')
        l.commit('scoped', 'fixture-reviewer',
                 'Internal working interpretation only; separate fixture roots checked')
        pen_receipt = l.receipt('scoped')
        l.challenge('scoped', 'cancellation', 'Counterexample: an unexpected closure')
        challenged_receipt = l.receipt('scoped')
        l.withdraw('scoped', 'fixture-reviewer',
                   'Scoped conclusion no longer supported by the changed fixture')
        withdrawn_receipt = l.receipt('scoped')
        l.reopen('scoped', 'fixture-reviewer',
                 'Reconsider the idea as pencil; prior evidence must be reexamined')
        after_reopen = l.receipt('scoped')
        replay = ThoughtLedger(path)
        assert replay.snapshot() == l.snapshot()
        return {
            'experiment': 'MOTIF-THOUGHT-006',
            'initial_universal_promotion_rejected': blocked,
            'echoed_root_rejected': rejected_echoes,
            'pen_receipt': pen_receipt,
            'pen_challenged': challenged_receipt,
            'withdrawn_receipt': withdrawn_receipt,
            'reopened_receipt': after_reopen,
            'exact_replay': replay.snapshot() == l.snapshot(),
            'event_count': len(l.history()),
            'head_digest': l.head_digest,
            'outside_world_authority': 'NONE',
            'note': 'Synthetic fixtures and self-described reviewers, not real authenticated evidence.',
        }


if __name__ == '__main__':
    print(json.dumps(run_demo(), indent=2))
