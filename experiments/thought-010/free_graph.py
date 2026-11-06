"""Optional Free Graph v0 *seed* packet, only from explicitly public fixtures.

Canonical hashing and record types follow the source-owned Free Graph v0
packet contract, inspected at the-static-collective/Free-Graph:
  docs/contract-v0.md
  schema/free-graph-v0.schema.json
  scripts/fg_core.py
This is a portable held proposal. It never constitutes an owner's decision.
"""
from __future__ import annotations
import copy
import hashlib
import json


def canonical(value, omit_key=None):
    value = copy.deepcopy(value)
    if omit_key and isinstance(value, dict):
        value.pop(omit_key, None)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def record(kind, payload):
    prefix = {'source': 'fgs', 'node': 'fgn', 'link': 'fgl'}[kind]
    payload = copy.deepcopy(payload)
    payload['id'] = f'{prefix}:sha256:{hashlib.sha256(canonical(payload, "id")).hexdigest()}'
    return payload


def export_seed_packet(engine, purpose: str, request_id: str):
    """Safe only after gateway confirms explicit PUBLIC_FIXTURE + allow_export.

    A user-supplied AUTHORED relation is not promoted to an observed Free Graph
    claim. Distinct manifestations remain distinct Free Graph nodes. Its labels
    may be included in the portable packet: never call on private input.
    """
    source = record('source', {
        'source_class': 'graph-packet',
        'locator': {'system': 'MOTIF local thought-door',
                    'coordinate': request_id,
                    'revision': engine.input_digest,
                    'resolution': 'declared public synthetic input; not owner-authenticated'},
        'observed_at': 'not independently time-attested',
        'acquisition': 'explicit local PUBLIC_FIXTURE export request',
        'digest': f'sha256:{engine.input_digest}',
        'access': 'public', 'export': 'portable', 'authority': 'none',
        'excerpt': 'Source is an explicitly designated synthetic MOTIF thought field; neither the witness nor any relation is independently validated.',
    })
    nodes, mappings = [], {}
    for mid, manifestation in sorted(engine.manifests.items()):
        c = engine.concepts[manifestation['concept_id']]
        node = record('node', {
            'kind': 'claim',
            'label': c['label'] + ' [' + mid + ']',
            'status': 'proposed',
            'source_ids': [source['id']],
            'claim_class': 'design',
            'witness_requirement': 'owner-defined',
            'extensions': {
                'motif_manifestation_id': mid,
                'motif_concept_id': manifestation['concept_id'],
                'meaning': 'representation of one context-specific thought; not an adopted fact',
            },
        })
        nodes.append(node)
        mappings[mid] = node['id']
    links = []
    for rel in engine.relations:
        links.append(record('link', {
            'from': mappings[rel['source']], 'to': mappings[rel['target']],
            'verb': 'connects', 'qualifier': rel['predicate'], 'status': 'proposed',
            'source_ids': [source['id']], 'authority': 'none',
            'extensions': {
                'motif_relation_id': rel['id'],
                'original_input_status': rel['status'],
                'claimed_origin': rel['origin'],
                'upstream_authentication': 'NOT_VERIFIED',
            },
        }))
    packet = {
        'schema': 'free-graph.packet/v0',
        'purpose': purpose,
        'modes': ['seed', 're-enter'],
        'scope': {'task': purpose, 'worlds': ['MOTIF synthetic thought field']},
        'task_world_cut': {
            'status': 'unresolved',
            'selected_ids': [source['id'], *[n['id'] for n in nodes], *[l['id'] for l in links]],
            'owner_head_source_ids': [],
            'omitted': [{
                'door': 'Owning-world review, source identity and actual field evidence',
                'reason': 'Local synthetic packet provides no authenticated owner head, consent or gate receipt',
            }],
            'rationale': 'Sufficient to record proposed concepts and traversals, insufficient to prove or adopt them',
        },
        'sources': [source], 'nodes': nodes, 'links': links,
        'residual_fog': [
            'MOTIF local concept meanings are caller-defined, not externally verified.',
            'Source-origin strings are self-asserted and not independent authentication.',
            'No receiving owner has admitted or adopted any claim.',
        ],
        'non_imports': [
            'Coordinates, concept-label equality and geometric proximity do not establish facts.',
            'PEN working commitments do not transfer to Free Graph owner-local authority.',
            'No constitutes/test/bears-on event is inferred from a thought-field export.',
        ],
        'extensions': {'from': 'motif.thought-door.reply.v1',
                       'source_evidence_digest': engine.input_digest,
                       'external_authority': 'NONE'},
    }
    packet['packet_id'] = 'fgp:sha256:' + hashlib.sha256(canonical(packet, 'packet_id')).hexdigest()
    return packet
