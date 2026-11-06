"""End-to-end, synthetic local JAR;VIS and Free Graph source-contract exercise."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from door import handle
from fixtures import make_engine

HERE=Path(__file__).resolve().parent


def main():
    request=json.loads((HERE/'example-ideas.json').read_text(encoding='utf-8'))
    held=handle(request)
    assert held['export']['status']=='HOLD'
    no_map=handle({**request,'max_views':0})
    assert held['source_only_answers']==no_map['source_only_answers']
    assert held['questions']==no_map['questions']
    assert held['source_evidence_digest']==no_map['source_evidence_digest']
    assert held['external_authority']=='NONE'

    public={**request,'request_id':'example:public-synthetic-002',
            'privacy':'PUBLIC_FIXTURE','allow_export':True}
    exported=handle(public)
    packet=exported['export']['packet']
    assert all(l['status']=='proposed' for l in packet['links'])
    assert packet['task_world_cut']['status']=='unresolved'
    with TemporaryDirectory() as temp:
        engine=make_engine(Path(temp)/'field.jsonl')
        snap=copy.deepcopy(engine._original)
        snapshot_req={
            'schema':request['schema'], 'request_id':'example:source-snapshot-003',
            'caller':'operator-local', 'mode':'snapshot',
            'purpose':'Compare typed dependencies, affordances and associations',
            'question':'What does the source graph support?',
            'field_snapshot':snap, 'relations':copy.deepcopy(engine.relations),
            'anchor':'m:volunteers', 'goals':['dependency','affordance','association'],
            'max_views':2, 'privacy':'PRIVATE_LOCAL', 'include_views':False,
        }
        actual=handle(snapshot_req)
        assert actual['source_evidence_digest']==engine.input_digest
        assert actual['external_authority']=='NONE'

    return {
        'experiment':'THOUGHT-010', 'status':'PROPOSAL_ONLY',
        'synthetic_jarvis_local_request':'PASS',
        'local_private_export_blocked':held['export']['status']=='HOLD',
        'source_only_vs_geometric_answers_identical':held['source_only_answers']==no_map['source_only_answers'],
        'source_only_vs_geometric_questions_identical':held['questions']==no_map['questions'],
        'selected_views_for_ideas':held['selected_lenses'],
        'questions_from_authored_relations':len(held['questions']),
        'explicit_public_fixture_export':exported['export']['status'],
        'free_graph_schema':packet['schema'],
        'free_graph_nodes':len(packet['nodes']),
        'free_graph_links':len(packet['links']),
        'free_graph_cut':packet['task_world_cut']['status'],
        'snapshot_crossing_source_digest_matches':actual['source_evidence_digest']==engine.input_digest,
        'snapshot_selected_views':actual['selected_lenses'],
        'source_labels_authenticated':False,
        'pen_commitments_changed':False,
        'external_authority':'NONE',
        'live_jarvis_runtime_wired':False,
        'live_free_graph_owner_admission':False,
    }


if __name__=='__main__':
    report=main()
    print(json.dumps(report, sort_keys=True, indent=2))
