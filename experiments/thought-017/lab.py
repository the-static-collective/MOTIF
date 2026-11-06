"""Bounded MOTIF-017 model-candidate evaluator with independent bitmask oracle.

The model proposes a typed NEW macro. It does not write code, grade tests,
choose audit datasets, or install a patch. Only fixed-template Python runs.
"""
from __future__ import annotations
import difflib,json,os,subprocess,sys,tempfile
from pathlib import Path
from program import (CHAT_MODEL_PROPOSAL, MONOTONE_BASELINE, ProposalError,
                     digest, validate_proposal, evaluate_macro, generate_source)
from oracle import verify_answer,validate_problem,COLORS
from fixtures import DEV,SAFETY,AUDIT,STRESS,challenge_cases

class LabError(ValueError):pass

def truth_table(proposal):
    expr=validate_proposal(proposal)['expression']
    trials=[]
    for a in range(8):
        for b in range(8):
            left=frozenset(c for j,c in enumerate(COLORS) if a & (1<<j))
            right=frozenset(c for j,c in enumerate(COLORS) if b & (1<<j))
            result=evaluate_macro(expr,left,right)
            expected=frozenset(c for j,c in enumerate(COLORS) if (a^b) & (1<<j))
            trials.append({'a':a,'b':b,'passed':result==expected})
    return {'passed':sum(t['passed'] for t in trials),'total':len(trials),
            'first_failure':next((x for x in trials if not x['passed']),None)}

def evaluate_candidate(proposal,specimens):
    if type(specimens) not in (list,tuple) or len(specimens)>128:
        raise LabError('bounded specimen set required')
    checked=validate_proposal(proposal)
    problems=[s['problem'] for s in specimens]
    for p in problems:validate_problem(p)
    source=generate_source(checked)
    with tempfile.TemporaryDirectory(prefix='motif-017-trusted-') as d:
        path=Path(d)/'candidate.py';path.write_text(source,encoding='utf-8')
        try:
            result=subprocess.run([sys.executable,'-B','-I',str(path)],
               input=json.dumps(problems),cwd=d,encoding='utf-8',
               capture_output=True,timeout=6,check=False,
               env={'PATH':os.environ.get('PATH',''),'PYTHONNOUSERSITE':'1'})
        except subprocess.TimeoutExpired as exc:raise LabError('fixed-template runtime timeout') from exc
    if result.returncode or len(result.stdout.encode())>90000:
        raise LabError('fixed-template runtime failed or exceeded output bound')
    try:answers=json.loads(result.stdout)
    except json.JSONDecodeError as exc:raise LabError('invalid trusted runtime output') from exc
    if type(answers) is not list or len(answers)!=len(specimens):
        raise LabError('wrong number of candidate replies')
    cases=[]
    for item,reply in zip(specimens,answers):
        passed=verify_answer(item['problem'],reply)
        cases.append({'category':item.get('category'), 'passed':passed,
                      'candidate_answer':reply,'note':item.get('note')})
    return {'passed':sum(x['passed'] for x in cases), 'total':len(cases),
            'first_failure':next((x for x in cases if not x['passed']),None),
            'cases':cases}

def run_experiment(candidate=CHAT_MODEL_PROPOSAL,*,audits=None,stresses=None):
    """Proposer supplies a candidate; benchmark remains evaluator-owned and frozen.

    Candidate may be GPT-6 conversation-authored or an explicit local Ollama
    response. Neither can run arbitrary source: evaluator compiles only typed
    expressions into a fixed template and independently grades outcomes.
    """
    checked=validate_proposal(candidate)
    audits=AUDIT if audits is None else audits
    stresses=STRESS if stresses is None else stresses
    before_truth=truth_table(MONOTONE_BASELINE)
    after_truth=truth_table(checked)
    dev_before=evaluate_candidate(MONOTONE_BASELINE,DEV)
    dev_after=evaluate_candidate(checked,DEV)
    guards=evaluate_candidate(checked,SAFETY)
    probes=evaluate_candidate(checked,challenge_cases())
    # Stage only if change distinguishes at least one case, passes **all**
    # developer-owned gates and has zero known dev/safety regressions.
    acceptable=(after_truth['passed']==64 and
        dev_after['passed']==dev_after['total'] and
        guards['passed']==guards['total'] and
        probes['passed']==probes['total'] and
        dev_after['passed']>=dev_before['passed'])
    receipts=[{'stage':'DEVELOPMENT','baseline':dev_before['passed'],
               'candidate':dev_after['passed'],'total':dev_after['total']},
              {'stage':'NEW_PRIMITIVE_TRUTH_TABLE','baseline':before_truth['passed'],
               'candidate':after_truth['passed'],'total':64},
              {'stage':'MODEL_CANDIDATE_GATE','disposition':'STAGED_FOR_FROZEN_AUDIT' if acceptable else 'HOLD_DEVELOPMENT_FAILURE'}]
    # Only after development selection is fixed, run independent frozen audit.
    if acceptable:
        audit_old=evaluate_candidate(MONOTONE_BASELINE,audits)
        audit_new=evaluate_candidate(checked,audits)
        stress_new=evaluate_candidate(checked,stresses)
        final=(audit_new['passed']==audit_new['total'] and
               stress_new['passed']==stress_new['total'] and
               audit_new['passed']>=audit_old['passed'])
    else:
        audit_old=audit_new=stress_new=None;final=False
    status=('PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED' if final else
            'HOLD_FROZEN_AUDIT_FAILURE' if acceptable else 'HOLD_DEVELOPMENT_FAILURE')
    baseline_source=generate_source(MONOTONE_BASELINE)
    candidate_source=generate_source(checked)
    diff=''.join(difflib.unified_diff(baseline_source.splitlines(True),candidate_source.splitlines(True),
        fromfile='experiments/thought-017/monotone_reference.py',
        tofile='experiments/thought-017/candidate_solver.py')) if final else ''
    report={'schema':'motif.thought017.algorithm-inventor-trial.v1',
            'status':status,'model_proposer':checked['proposer'],
            'trained_local_llm_executed':False, # override only via CLI when real run confirmed
            'proposer_seen_frozen_audit':False,
            'new_primitive':'set_difference composing bidirectional differences and union',
            'old_016_grammar_can_express_deletion':False,
            'truth_table':{'baseline':before_truth['passed'],
                           'candidate':after_truth['passed'],'total':64},
            'development':{'baseline':dev_before['passed'],
                           'candidate':dev_after['passed'],'total':len(DEV)},
            'safety':{'candidate':guards['passed'],'total':len(SAFETY)},
            'developer_probes':{'candidate':probes['passed'],'total':len(challenge_cases())},
            'frozen_audit':(None if audit_new is None else
                            {'baseline':audit_old['passed'],'candidate':audit_new['passed'],'total':len(audits)}),
            'stress':(None if stress_new is None else {'candidate':stress_new['passed'],'total':len(stresses)}),
            'first_counterexample':next((x for x in [after_truth['first_failure'],dev_after['first_failure'],
                    guards['first_failure'],probes['first_failure'],
                    audit_new['first_failure'] if audit_new else None,
                    stress_new['first_failure'] if stress_new else None] if x is not None),None),
            'development_receipts':receipts,'frozen_evaluated_after_staging':acceptable,
            'candidate_proposal_digest':digest(checked),
            'generated_source_sha256':__import__('hashlib').sha256(candidate_source.encode()).hexdigest(),
            'generated_source_is_fixed_template':True,'model_wrote_python':False,
            'execution_is_os_isolated':False,'python_I_is_not_security_sandbox':True,
            'installed':False,'pen_unchanged':True,'external_authority':'NONE',
            'limitations':'A GPT-6 conversationally supplied typed proposal, not MOTIF autonomously running an LLM. New macro from trusted difference/union primitives; deliberately constructed cases. No claims of novel computer science or held-out independent real-world validation.'}
    report['receipt_digest']=digest(report)
    return report,candidate_source,diff
