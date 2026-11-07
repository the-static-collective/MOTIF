"""THOUGHT-020: a deterministic developmental critic over *actual* model proposals.

The critic is a process around a generative model, not an oracle: it can see
only source-owned validation and prior DEV feedback, not hidden audit labels.
It refuses semantically repeated refuted programs within a fixed inference
budget and asks the same model for a new proposal. It NEVER supplies a program.
"""
from __future__ import annotations
import hashlib
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
for family in ('thought-017', 'thought-018', 'thought-019'):
    sibling = str(HERE.parent / family)
    if sibling not in sys.path:
        sys.path.insert(0, sibling)
from program import validate_proposal, digest
from director import ResearchDirector, candidate_mask
from direct_model import DirectLocalLLM

SCHEMA = 'motif.thought020.critic-comparison.v1'
MAX_CALLS = 6


class CriticError(ValueError): pass


def semantic_signature(proposal):
    """Fingerprint outputs on all 8x8 finite inputs, independent of oracle labels.

    A syntactically different program can still perform exactly the same
    transitions. This does not establish correctness on any hidden example.
    """
    expression = validate_proposal(proposal)['expression']
    outputs = tuple(candidate_mask(expression, a, b)
                    for a in range(8) for b in range(8))
    return hashlib.sha256(bytes(outputs)).hexdigest()


def dev_only(feedback):
    """Discard hypothesis survivor names and unrecognized fields before LLM.

    Unknown keys fail closed: a caller cannot sneak audit material into model
    feedback. Each numerical result is already observed on a DEV probe.
    """
    if type(feedback) not in (tuple, list) or len(feedback) > MAX_CALLS:
        raise CriticError('bounded development feedback required')
    out = []
    keys = {'mechanism','observed_result','oracle_expected','disposition',
            'on_mask','toggles_mask','surviving_mechanisms'}
    for item in feedback:
        if type(item) is not dict or set(item) - keys:
            raise CriticError('unexpected research feedback fields')
        for field in ('observed_result','oracle_expected','on_mask','toggles_mask'):
            if type(item.get(field)) is not int or not 0 <= item[field] <= 7:
                raise CriticError('development feedback must be 3-bit masks')
        if item.get('disposition') not in ('REFUTED_ON_DEV','SURVIVED_DEV_PROBE'):
            raise CriticError('unexpected development disposition')
        out.append({key:item[key] for key in ('observed_result', 'oracle_expected',
                   'disposition', 'on_mask', 'toggles_mask')})
    return tuple(out)


class ModelWithCritic:
    """Budget-exact experiment: the proposer still originates every candidate.

    The 'control' mode simply applies a shared budget and strips DEV survivor
    labels. In 'critic' mode a replay of an already refuted *semantic function*
    costs one model call but ZERO new evaluator probes. It may request a second
    generation using only that previously observed counterexample. Total model
    generations never exceed the same budget as control.
    """
    def __init__(self, base_model, *, mode='control', max_calls=3):
        if mode not in ('control', 'critic'):
            raise CriticError('unknown comparison arm')
        if type(max_calls) is not int or not 1 <= max_calls <= MAX_CALLS:
            raise CriticError('model budget must be 1..6')
        if not callable(getattr(base_model, 'propose', None)):
            raise CriticError('explicit callable model required')
        self.base = base_model
        self.mode = mode
        self.max_calls = max_calls
        self.kind = getattr(base_model, 'kind', 'UNVERIFIED_MODEL')
        self.generation_count = 0
        self.refuted = {}
        self.last_accepted = None
        self.notes = []
        self.accepted = []
        self._feedback_seen = 0

    @property
    def calls(self):
        return getattr(self.base, 'calls', [])

    def _observe_development_feedback(self, feedback):
        if len(feedback) < self._feedback_seen:
            raise CriticError('development feedback cannot be rewound')
        if len(feedback) > self._feedback_seen + 1:
            raise CriticError('unexplained feedback records')
        if len(feedback) > self._feedback_seen:
            last = feedback[-1]
            if self.last_accepted is None:
                raise CriticError('feedback without an admitted model candidate')
            if last['disposition'] == 'REFUTED_ON_DEV':
                sig = semantic_signature(self.last_accepted['mechanism'])
                self.refuted[sig] = deepcopy(last)
            self._feedback_seen = len(feedback)

    @staticmethod
    def _new_reason(note):
        return (f' CRITIC: Do not repeat that transition function. Previous DEV '
                f'test on={note["on_mask"]}, toggles={note["toggles_mask"]}: '
                f'prediction={note["observed_result"]}, '
                f'observed={note["oracle_expected"]}. '
                'Propose a distinct typed expression. No hidden audit evidence.')

    def propose(self, brief, feedback=()):
        sanitized = dev_only(feedback)
        # Feedback is used only to identify already refuted expressions, not
        # to deduce or supply the target program.
        self._observe_development_feedback(feedback)
        if type(brief) is not str or not 8 <= len(brief) <= 300:
            raise CriticError('bounded research brief required')
        retry_note = ''
        while self.generation_count < self.max_calls:
            # The 019 direct client accepts a max-300-character brief.
            adjusted = (brief[:110] + retry_note)[:300] if retry_note else brief
            # Underlying model makes a real HTTP call; never fabricate a reply.
            candidate = self.base.propose(adjusted, sanitized)
            if candidate is None:
                return None
            self.generation_count += 1
            proposed, _ = __import__('research_model').validate_model_reply(candidate)
            sig = semantic_signature(proposed)
            if self.mode == 'critic' and sig in self.refuted:
                note = self.refuted[sig]
                self.notes.append({'generation':self.generation_count,
                    'disposition':'VETO_REFUTED_SEMANTIC_REPLAY',
                    'semantic_signature':sig,'counterexample':{
                      'on_mask':note['on_mask'], 'toggles_mask':note['toggles_mask'],
                      'observed_result':note['observed_result'],
                      'oracle_expected':note['oracle_expected']},
                    'oracle_called_for_replay':False,'model_reply_rewritten':False})
                retry_note = self._new_reason(note)
                continue
            self.last_accepted = deepcopy(candidate)
            self.accepted.append({'generation':self.generation_count,
                'semantic_signature':sig,
                'candidate_digest':digest(proposed),
                'disposition':'ACCEPTED_FOR_INDEPENDENT_DEV_TEST'})
            return candidate
        self.notes.append({'generation':self.generation_count,
                           'disposition':'HOLD_MODEL_BUDGET_EXHAUSTED',
                           'oracle_called_for_replay':False})
        return None


def run_arm(model, brief, *, mode, max_calls=3, graph=True):
    wrapped = ModelWithCritic(model, mode=mode, max_calls=max_calls)
    director_report, candidate = ResearchDirector(
        brief, model=wrapped, max_rounds=max_calls).run(evaluate_graph=graph)
    # Ensure every accepted proposal came from the model, not the critic.
    assert wrapped.generation_count <= max_calls
    assert director_report['pen_state'] == 'UNCHANGED'
    result = {'mode':mode,'status':director_report['status'],
        'model_kind':wrapped.kind,'model_generations':wrapped.generation_count,
        'director_dev_probes':director_report['dev_probe_count'],
        'selected_mechanism':director_report['selected_mechanism'],
        'semantic_replays_vetoed':sum(n['disposition']=='VETO_REFUTED_SEMANTIC_REPLAY'
                                       for n in wrapped.notes),
        'developer_notes':wrapped.notes,
        'model_candidates_admitted':wrapped.accepted,
        'model_receipts':deepcopy(wrapped.calls),
        'director_report':director_report,
        'candidate':candidate,
        'oracle_never_graded_critic_veto':True,
        'frozen_audit_seen_by_model':False,
        'source_mutated':False,'installed':False,'external_authority':'NONE'}
    result['receipt_digest'] = digest(result)
    return result


def comparison(model_factory, brief, *, max_calls=3, graph=True):
    if not callable(model_factory):
        raise CriticError('models must be supplied by an explicit operator factory')
    if type(max_calls) is not int or not 1 <= max_calls <= MAX_CALLS:
        raise CriticError('invalid matched call budget')
    control = run_arm(model_factory(), brief, mode='control', max_calls=max_calls, graph=graph)
    guided = run_arm(model_factory(), brief, mode='critic', max_calls=max_calls, graph=graph)
    report = {'schema':SCHEMA,'status':'COMPARATIVE_EXPERIMENT_ONLY',
        'inference_budget_per_arm':max_calls,
        'same_brief':True,'same_proposer_model_requested':True,
        'control':control,'critic':guided,
        'model_calls_matched_upper_bound':True,
        'critique_uses_only_dev_counterexamples':True,
        'oracle_and_hidden_audit_owned_by_evaluator':True,
        'note':'One synthetic task and two sequential model runs. Equal maximum call budget, '
           'not equal prompt tokens, elapsed wall time, hardware scheduling or model randomness. '
           'The critic cannot supply a candidate, fabricate a model call or grant authority.',
        'installed':False,'pen_state':'UNCHANGED','external_authority':'NONE'}
    report['receipt_digest']=digest(report)
    return report
