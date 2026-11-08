"""Import prior MOTIF-026 reports as untrusted evidence, and independently recheck.

This accepts local JSON input from an operator. A report's alleged LLM backend,
status or digest is not trusted as a certificate: the source owner reruns the
mathematical oracle and fixed-template executable code. Invalid records HOLD.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from proof_memory import ProofLibrary,ProofError,retain_hypotheses,digest
from reuse import reuse
from specimens import BY_KEY

SCHEMA='motif.thought027.fragment-ingest.v1'

def ingest_report(obj):
    if type(obj) is not dict or obj.get('schema')!='motif.thought026.staged-experiment.v1':
        raise ProofError('not a recognized THOUGHT-026 local report')
    if type(obj.get('results')) is not dict or len(obj['results'])>40:
        raise ProofError('invalid or overbudget task result set')
    origin='DECLARED_'+str(obj.get('backend','unknown')).upper()[:30]+'_NOT_AUTHENTICATED'
    library=ProofLibrary();certified={};held={};errors={}
    for key,trial in obj['results'].items():
        if key not in BY_KEY or type(trial) is not dict or trial.get('task')!=key:
            errors[key]='HOLD_UNRECOGNIZED_TASK_OR_RESULT';continue
        if trial.get('status')=='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED':
            try:
                card=library.admit(BY_KEY[key],trial,origin=origin)
                certified[key]={'proof_digest':card['proof_digest'],
                                'binding_status':card['identifiability']['binding_status'],
                                'relation_status':card['identifiability']['relation_status']}
            except Exception as exc:
                errors[key]='HOLD_INDEPENDENT_REPROOF_FAILED_'+type(exc).__name__
        else:
            try:held[key]=retain_hypotheses(BY_KEY[key],trial)
            except Exception as exc:
                errors[key]='HOLD_INVALID_UNVERIFIED_HYPOTHESIS_'+type(exc).__name__
    output={'schema':SCHEMA,'declared_original_backend_untrusted':obj.get('backend'),
        'origin_cryptographically_authenticated':False,
        'source_results_never_promoted_without_rechecking':True,
        'certified':certified,'unverified_fragments':held,'rejected':errors,
        'proof_library':library.cards(),
        'language_meaning_globally_certified':False,
        'installed':False,'external_authority':'NONE'}
    output['digest']=digest(output)
    return output

def main(argv=None):
    p=argparse.ArgumentParser(description='Recheck and store scoped MOTIF-026 evidence; never install.')
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    if args.report.stat().st_size>2_000_000:p.error('report size budget exceeded')
    packet=json.loads(args.report.read_text(encoding='utf-8'))
    o=ingest_report(packet)
    args.output.write_text(json.dumps(o,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'certified':len(o['certified']),
        'unverified_held':len(o['unverified_fragments']),
        'rejected':len(o['rejected']),
        'origin_authenticated':False,
        'installed':False},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
