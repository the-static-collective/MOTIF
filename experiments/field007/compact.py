"""Deterministic reduced evidence ledger; time excluded from proof digests."""
from __future__ import annotations
import json
from pathlib import Path
from field007 import seal


def compact_packet(p):
 return {'source':p['source'],'seed':p['seed'],'policy':p['policy'],
         'archive_revision':p['archive_revision'],'packet_sha256':p['packet_sha256'],
         'acquired_row_ids_sha256':seal(p['acquired_row_ids']),
         'prequery_chain_sha256':seal(p['prequery_sha256s']),
         'source_receipt_chain_sha256':seal(p['source_receipt_sha256s']),
         'checkpoints':[{'labels':s['labels'],'evidence_sha256':s['evidence_sha256'],
            'models':{n:{'correct':v['correct'],'n':v['n'],'balanced_accuracy':v['balanced_accuracy']}
                      for n,v in s['models'].items() if v is not None}} for s in p['snapshots']],
         'local_refutations':p['local_refutations'],
         'surviving_local_alternatives':p['surviving_local_alternatives'],
         'committee_model_fits':p['committee_model_fits'],
         'lineage_sha256':p['lineage_sha256'],
         'bootstrap_oneclass_overflow':p['bootstrap_oneclass_overflow'],
         'query_budget':p['query_budget']}


def compact_report(r):
 summary={source:{policy:{k:v for k,v in metrics.items() if k!='seconds'}
                  for policy,metrics in entries.items()} for source,entries in r['summary'].items()}
 report={'schema':'motif.field007.compact.v1',
         'preregistered_protocol_commit':'dff01503ddd57492e49f29f7d1277fc10c2ad383',
         'cases':[compact_packet(p) for p in r['ordered_cases']],
         'summary':summary,'primary_verdict':r['primary_verdict'],
         'readme':'Every case can be reproduced offline from original source in repo; time excluded from content digests. Historical sources, not source-owner blind test.',
         'scoring_bug_note':'Initial local evaluation incorrectly omitted pool-fitted StandardScaler on heldout feature vectors (all SVC balanced accuracies 0.5). Fixed evaluation transform, reran all 30 cases without changing predeclared policies. Prior invalid run discarded but documented in README.'}
 report['sha256']=seal(report)
 return report

if __name__=='__main__':
 root=Path(__file__).parent
 r=json.loads((root/'experiment-results-full-local.json').read_text())
 (root/'experiment-results.json').write_text(json.dumps(compact_report(r),sort_keys=True,indent=2)+'\n')
