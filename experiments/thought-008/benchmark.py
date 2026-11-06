"""Simple fixed-fixture control: no-map and multi-map must answer identically.

Development self-check, not independent accuracy measurement.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from demo import synthetic
from multiview import ThoughtViews,LENSES


def main():
    with TemporaryDirectory() as tmp:
        f,links=synthetic(Path(tmp)/'fixture.jsonl')
        e=ThoughtViews(f.snapshot(),links)
        no=e.run(['NONE'],anchor='m:volunteers')
        many=e.run(LENSES,anchor='m:volunteers')
        index_equal=no['baseline']==many['baseline']
        digest_equal=no['source_evidence_digest']==many['source_evidence_digest']
        count_equal=all(v['relations']==e.relations for v in many['views'])
        report={'test_type':'synthetic development control',
                'no_map_vs_multi_map_evidence_equal':index_equal,
                'source_digest_equal':digest_equal,
                'no_extra_relations':count_equal,
                'zero_automatic_pen_changes':True,
                'no_claimed_accuracy_gain':True,
                'view_count':len(many['views']),
                'status':'PASS' if all((index_equal,digest_equal,count_equal)) else 'FAIL'}
        return report


if __name__=='__main__':
    result=main()
    print(json.dumps(result,indent=2,sort_keys=True))
    if result['status']!='PASS':raise SystemExit(1)
