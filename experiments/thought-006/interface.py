"""Local JSON command doorway. Deliberately not an autonomous promotion agent.

  python interface.py /tmp/thought.jsonl command.json
  python interface.py /tmp/thought.jsonl        # read-only snapshot

Commands are one event at a time; failure is not a multi-operation rollback.
Only an explicit COMMIT command with a claimed actor can request PEN, under
STRICT_LOCAL_REVIEW_V1. No tool invokes a remote service or executes source code.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from adapter import import_geom005
from ledger import ThoughtLedger

_MUTATIONS = {
    'node': 'register_node', 'source': 'register_source',
    'sketch': 'sketch', 'support': 'support', 'challenge': 'challenge',
    'commit': 'commit', 'withdraw': 'withdraw', 'reopen': 'reopen',
}


def process(ledger: ThoughtLedger, command: dict) -> dict:
    if not isinstance(command, dict) or set(command) != {'action', 'args'}:
        raise ValueError('command must contain exactly action and args')
    action = command['action']
    args = command['args']
    if not isinstance(args, dict):
        raise ValueError('args must be a JSON object')
    if action == 'snapshot':
        if args:
            raise ValueError('snapshot has no arguments')
        return {'status': 'READ_ONLY', 'snapshot': ledger.snapshot()}
    if action == 'receipt':
        if set(args) != {'assertion_id'}:
            raise ValueError('receipt requires assertion_id')
        return {'status': 'READ_ONLY', 'receipt': ledger.receipt(args['assertion_id'])}
    if action == 'import_geom005':
        if set(args) != {'snapshot', 'scope'}:
            raise ValueError('import requires snapshot and scope')
        return {'status': 'PENCIL_ONLY',
                'assertions': import_geom005(args['snapshot'], ledger, scope=args['scope']),
                'authority': 'NONE'}
    if action not in _MUTATIONS:
        raise ValueError('unsupported command')
    result = getattr(ledger, _MUTATIONS[action])(**args)
    return {'status': 'LOCAL_LEDGER_EVENT', 'event_id': result['event_id'],
            'head_digest': result['digest'], 'external_authority': 'NONE'}


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit('usage: python interface.py ledger.jsonl [command.json]')
    ledger = ThoughtLedger(Path(sys.argv[1]))
    command = (json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
               if len(sys.argv) == 3 else {'action': 'snapshot', 'args': {}})
    print(json.dumps(process(ledger, command), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
