"""Adversarial, source-grounded tests; all world truths are hypothetical fixtures."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from inquiry import InquiryCycle, InquiryError, information_gain
from fixtures import make_engine, possible_worlds, fixture_oracle
from human_talk import interpret, dialogue, question_utterance
from benchmark import main as benchmark
from demo import main as demo


class AdaptiveInquiryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.field,self.engine,_=make_engine(Path(self.tmp.name)/'field.jsonl')
        self.worlds=possible_worlds(self.engine)
        self.pair=('m:food','m:meal')
        self.original=self.field.snapshot()

    def make(self, **kwargs):
        return InquiryCycle(self.engine,self.worlds,seed_pair=self.pair,**kwargs)

    def test_catalog_comes_only_from_typed_authored_source(self):
        a=self.make()
        self.assertNotIn('r:hypothetical-direct',{q['atom'] for q in a.catalog})
        self.assertNotIn('r:disputed-home',{q['atom'] for q in a.catalog})
        self.assertTrue(all(q['status']=='QUESTION_ONLY' for q in a.catalog))
        self.assertEqual(len(a.catalog),8)

    def test_decision_relevance_replans_on_oracle_response(self):
        a=self.make()
        q=a.next_question()
        self.assertEqual(q['lens'],'dependency')
        self.assertEqual(q['atom'],'r:meal-needs-venue')
        self.assertFalse(q['geometry_used_for_evidence'])
        a.observe(q,False)
        self.assertIsNone(a.next_question())
        self.assertEqual(a.report()['proposed_decision'],'NO')
        self.assertEqual(a.report()['pen_status'],'UNCHANGED')

    def test_yes_world_can_test_two_dependencies_or_enablement(self):
        a=self.make()
        truth=self.worlds[11]
        output=a.run(fixture_oracle(truth),budget=3)
        self.assertEqual(output['proposed_decision'],'YES')
        self.assertGreaterEqual(len(output['question_steps']),2)
        self.assertTrue(all(s['external_authority']=='NONE' for s in output['question_steps']))

    def test_identical_adaptive_results_without_geometry(self):
        truth=self.worlds[11]
        p=self.make(geometry=True).run(fixture_oracle(truth),budget=3)
        n=self.make(geometry=False).run(fixture_oracle(truth),budget=3)
        self.assertEqual([s['question_id'] for s in p['question_steps']],
                         [s['question_id'] for s in n['question_steps']])
        self.assertEqual(p['proposed_decision'],n['proposed_decision'])
        self.assertEqual(p['source_digest'],n['source_digest'])
        self.assertTrue(all(s['coordinates_used_for_evidence'] is False for s in p['question_steps']))
        self.assertEqual(self.field.snapshot(),self.original)

    def test_unknown_answer_does_not_shrink_the_model(self):
        a=self.make()
        first=a.next_question()
        a.observe(first,'UNKNOWN')
        self.assertEqual(len(a.remaining),len(self.worlds))
        self.assertEqual(a.steps[0]['answer'],'UNKNOWN')
        self.assertNotEqual(a.next_question()['id'],first['id'])

    def test_inconsistent_answer_raises_model_mismatch_hold(self):
        a=self.make()
        first=a.next_question()
        a.observe(first,True)
        # Uninformative question not selected by a.next_question may still be
        # submitted from the typed catalog to test a contradiction with models.
        unvarying=next(q for q in a.catalog if q['atom']=='r:food-volunteers')
        a.observe(unvarying,False)
        self.assertEqual(a.report()['conclusion_status'],'HOLD_MODEL_MISMATCH')
        self.assertGreater(len(a.remaining),0)
        self.assertIsNone(a.next_question())

    def test_world_entropy_is_a_classical_matched_comparator(self):
        result=benchmark()
        self.assertEqual(result['trials'],16)
        self.assertTrue(result['no_geometry_parity_all'])
        self.assertGreaterEqual(result['decision_correct_under_model']['decision_no_map'],
                                result['decision_correct_under_model']['strong_world_entropy'])
        self.assertEqual(result['decision_correct_under_model']['decision_no_map'],
                         result['decision_correct_under_model']['decision_map'])

    def test_duplicate_manifestations_do_not_conflate_home(self):
        self.assertEqual(self.engine.concepts['c:home-shelter']['label'],
                         self.engine.concepts['c:home-belonging']['label'])
        self.assertNotEqual(self.engine.manifests['m:home-shelter']['concept_id'],
                            self.engine.manifests['m:home-belonging']['concept_id'])

    def test_untrusted_language_unknown_does_not_turn_into_operation(self):
        value=interpret('do something completely different',engine=self.engine,selected_pair=self.pair)
        self.assertEqual(value['status'],'HOLD')
        self.assertEqual(value['speech_act'],'UNKNOWN')
        self.assertFalse(value['can_execute'])
        for dangerous in ['deploy the network','delete the evidence','send this to my friends',
                          'merge the repositories','execute arbitrary code']:
            output=interpret(dangerous,engine=self.engine,selected_pair=self.pair)
            self.assertEqual(output['speech_act'],'HOLD_EFFECT_REQUEST')

    def test_full_measure_human_terminal_alias_does_not_inherit_authority(self):
        result=dialogue(self.engine,self.worlds,'Where am I?',None)
        self.assertEqual(result['status'],'SOURCE_ONLY_ORIENTATION')
        self.assertIsNone(result['inquiry'])
        self.assertEqual(result['pen'],'UNCHANGED')
        value=interpret('What can I safely do?',engine=self.engine)
        self.assertEqual(value['speech_act'],'INSPECT_MOVES')
        self.assertFalse(value['can_execute'])

    def test_ambiguous_natural_phrase_requires_explicit_referents(self):
        result=dialogue(self.engine,self.worlds,'What if home means belonging?',lambda x:True)
        self.assertEqual(result['status'],'CLARIFY_REFERENTS')
        self.assertIsNone(result['inquiry'])
        self.assertIn('exact manifestation IDs',result['utterances'][-1]['text'])
        with self.assertRaises(InquiryError):
            interpret('What if home?',engine=self.engine,selected_pair=('m:home','m:meal'))

    def test_spoken_questions_carry_claimed_original_source_ids(self):
        brain=self.make()
        q=brain.next_question()
        spoken=question_utterance(self.engine,q)
        self.assertEqual(spoken['status'],'QUESTION_ONLY')
        self.assertEqual(spoken['relation_id'],q['relation_id'])
        self.assertEqual(spoken['source_digest'],self.engine.input_digest)
        self.assertIn('Could we check whether',spoken['text'])

    def test_human_talk_is_operational_reasoning_turns_not_posthoc_caption(self):
        record=dialogue(self.engine,self.worlds,'How do we know this?',
                        fixture_oracle(self.worlds[11]),selected_pair=self.pair,budget=3)
        self.assertEqual(record['input']['speech_act'],'CHALLENGE')
        self.assertEqual(record['status'],'HOLD_FOR_REVIEW')
        self.assertEqual(len([x for x in record['utterances'] if x['speech_act']=='ASK']),
                         len(record['inquiry']['question_steps']))
        self.assertEqual(record['authority'],'NONE')
        self.assertEqual(record['pen'],'UNCHANGED')
        self.assertEqual(record['inquiry']['geometry_used_for_evidence'],False)
        self.assertEqual(self.field.snapshot(),self.original)

    def test_missing_oracle_means_hold_not_fabricated_observation(self):
        r=dialogue(self.engine,self.worlds,'What if these ideas connect?',None,
                   selected_pair=self.pair)
        self.assertEqual(r['status'],'HOLD_NO_TEST')
        self.assertEqual(len(r['utterances']),2)

    def test_invalid_sources_worlds_and_budget_fail_closed(self):
        with self.assertRaises(InquiryError):
            InquiryCycle(self.engine,self.worlds,seed_pair=None)
        bad=copy.deepcopy(self.worlds)
        bad[0]['atoms']['r:meal-needs-venue']='maybe'
        with self.assertRaises(InquiryError):
            InquiryCycle(self.engine,bad,seed_pair=self.pair)
        with self.assertRaises(InquiryError):
            self.make().run(lambda _:True,budget=100)
        with self.assertRaises(InquiryError):
            self.make().observe({'id':'not-current','atom':'wrong'},True)

    def test_replay_determinism_and_no_source_change(self):
        truth=self.worlds[11]
        x=self.make().run(fixture_oracle(truth),budget=3)
        y=self.make().run(fixture_oracle(truth),budget=3)
        self.assertEqual(x,y)
        self.assertEqual(self.field.snapshot(),self.original)
        self.assertEqual(x['receipt_digest'],x['receipt_digest'])
        self.assertEqual(x['world_model_digest'],y['world_model_digest'])

    def test_demo_is_executable_source_preserving(self):
        r=demo()
        self.assertTrue(r['source_unchanged'])
        self.assertTrue(r['oracle_is_synthetic'])
        self.assertEqual(r['dialogue']['authority'],'NONE')

if __name__ == '__main__':unittest.main()

class OptionalInterpreterGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        _,self.engine,_=make_engine(Path(self.tmp.name)/'field.jsonl')
        self.worlds=possible_worlds(self.engine)

    def frame(self,text, **changes):
        from hashlib import sha256
        base={'schema':'motif.human-talk.interpreter-proposal.v1',
              'input_digest':sha256(text.encode()).hexdigest(),
              'speech_act':'CHALLENGE', 'manifestation_ids':['m:food','m:meal'],
              'rationale':'candidate interpretation only'}
        base.update(changes)
        return base

    def test_optional_language_proposal_is_validated_and_first_class(self):
        text='I dunno mate, maybe probe the two here, eh?'
        proposal=self.frame(text)
        result=dialogue(self.engine,self.worlds,text,fixture_oracle(self.worlds[11]),
                        language_proposal=proposal,budget=2)
        self.assertEqual(result['input']['interpreter_origin'],'UNVERIFIED_EXTERNAL_PROPOSAL')
        self.assertEqual(result['input']['speech_act'],'CHALLENGE')
        self.assertTrue(result['inquiry']['question_steps'])
        self.assertEqual(result['authority'],'NONE')

    def test_untrusted_model_proposal_cannot_expand_authority_or_bind_stale_text(self):
        text='please investigate this'
        from human_talk import validate_language_proposal
        for altered in [self.frame(text,speech_act='EXECUTE'),
                        self.frame(text,input_digest='0'*64),
                        self.frame(text,manifestation_ids=['m:unknown','m:meal']),
                        self.frame(text,manifestation_ids=['m:food','m:food']),
                        self.frame(text,caller='root')]:
            with self.assertRaises(InquiryError):
                validate_language_proposal(altered,text,self.engine)

    def test_effect_request_beats_favorable_model_frame(self):
        text='deploy these results now'
        good=self.frame(text)
        result=dialogue(self.engine,self.worlds,text,fixture_oracle(self.worlds[11]),
                        language_proposal=good)
        self.assertEqual(result['status'],'HOLD')
        self.assertIsNone(result['inquiry'])
