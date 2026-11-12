"""LLM-002 falsifiers. No real model weights or owner effects."""
from dataclasses import replace
import unittest
from engine import (TinyCausal,LowRankGraph,Cache,PREFIX,D,seal,context,prefill,
                    branch,full,graph_features,truth,train,evaluate,examples,demo)
class ForkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=TinyCausal()
        cls.adapter=LowRankGraph()
        cls.ctx=context(tenant="t-one",authority="independent-fixture",root="source-7",
                        model=cls.model,adapter=cls.adapter.version)
        cls.cache=prefill(cls.model,PREFIX,cls.ctx)
    def fork(self,*,ctx=None,cache=None,token="use",tool=1,permission=1,adapter=None):
        f=graph_features(tool=tool,permission=permission,action=token)
        return branch(self.model,cache or self.cache,ctx or self.ctx,token,f,
                      self.adapter if adapter is None else adapter)
    def test_01_actual_qk_not_mocked(self):
        self.assertEqual(self.cache.qk_ops, sum(range(1,len(PREFIX)+1)))
        self.assertEqual(len(self.cache.keys),len(PREFIX))
        self.assertTrue(all(len(k)==D for k in self.cache.keys))
    def test_02_cached_uncached_equivalence_5_forks(self):
        for tool,permission,action in [(0,0,"probe"),(0,0,"use"),(1,1,"use"),(1,0,"use"),(0,0,"publish")]:
            f=graph_features(tool=tool,permission=permission,action=action)
            a=branch(self.model,self.cache,self.ctx,action,f,self.adapter)
            b=full(self.model,PREFIX,self.ctx,action,f,self.adapter)
            self.assertAlmostEqual(a["logit"],b["logit"],places=12)
            self.assertEqual(a["state"],"PENCIL")
    def test_03_suffix_graph_changes_hidden_logit(self):
        lo=self.fork(tool=0,permission=0)["logit"]
        hi=self.fork(tool=1,permission=1)["logit"]
        self.assertNotEqual(lo,hi)
    def test_04_no_prefix_kv_mutation_between_forks(self):
        before=self.cache.cache_seal
        self.fork(token="probe",tool=0); self.fork(token="publish",permission=0)
        self.assertEqual(before,self.cache.cache_seal)
    def test_05_tenant_scope_rejected(self):
        other=context(tenant="other",authority="independent-fixture",root="source-7",model=self.model)
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):self.fork(ctx=other)
    def test_06_source_authority_rejected(self):
        other=dict(self.ctx,authority="untrusted")
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):self.fork(ctx=other)
    def test_07_source_root_rejected(self):
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            self.fork(ctx=dict(self.ctx,source_root="unrelated"))
    def test_08_model_weight_change_rejected(self):
        m2=TinyCausal(seed=42)
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            branch(m2,self.cache,self.ctx,"probe",graph_features(tool=0,permission=0,action="probe"),self.adapter)
    def test_09_tokenizer_change_rejected(self):
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            self.fork(ctx=dict(self.ctx,tokenizer="different"))
    def test_10_adapter_version_change_rejected(self):
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            self.fork(ctx=dict(self.ctx,adapter="other-v1"))
    def test_11_graph_conditioned_prefix_requires_new_prefill(self):
        with self.assertRaisesRegex(ValueError,"CONTROLLED_PREFIX_CANNOT_USE_SHARED_CACHE"):
            prefill(self.model,PREFIX,dict(self.ctx,prefix_graph="different-state"))
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            self.fork(ctx=dict(self.ctx,prefix_graph="different-state"))
    def test_12_mutated_kv_cannot_be_used(self):
        broken=replace(self.cache,keys=(tuple([3.0]*D),)+self.cache.keys[1:])
        with self.assertRaisesRegex(ValueError,"CACHE_TAMPERED"):self.fork(cache=broken)
    def test_13_cache_shape_mismatch(self):
        broken=replace(self.cache,keys=self.cache.keys[:-1])
        with self.assertRaisesRegex(ValueError,"CACHE_SHAPE_MISMATCH"):self.fork(cache=broken)
    def test_14_scope_metadata_tamper(self):
        with self.assertRaisesRegex(ValueError,"CACHE_SCOPE_MISMATCH"):
            self.fork(cache=replace(self.cache,scope_hash="bad"))
    def test_15_position_mismatch_changes_result(self):
        f=graph_features(tool=1,permission=1,action="use")
        lat=self.adapter.project(f)[0]
        good=self.model.step("use",len(PREFIX),self.cache.keys,self.cache.values,lat)[0]
        wrong=self.model.step("use",len(PREFIX)+1,self.cache.keys,self.cache.values,lat)[0]
        self.assertNotAlmostEqual(good,wrong,places=12)
    def test_16_wrong_graph_dim_and_actions_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_GRAPH_FEATURES"):self.adapter.project([1,0])
        with self.assertRaisesRegex(ValueError,"BAD_GRAPH"):graph_features(tool=2,permission=0,action="use")
        with self.assertRaisesRegex(ValueError,"UNKNOWN_TOKEN"):
            self.model.step("new_unregistered_token",0,(),())
    def test_17_prefix_computation_reduction_not_decode(self):
        forks=5;n=len(PREFIX)
        flat=forks*(n*(n+1)//2+(n+1))
        shared=n*(n+1)//2+forks*(n+1)
        self.assertLess(shared,flat)
        self.assertEqual(shared, self.cache.qk_ops+forks*(n+1))
    def test_18_single_fork_no_compute_savings(self):
        n=len(PREFIX)
        self.assertEqual(n*(n+1)//2+n+1,n*(n+1)//2+1*(n+1))
    def test_19_source_fact_not_promoted_by_classification(self):
        before=dict(self.ctx)
        r=self.fork(token="use",tool=1,permission=1)
        self.assertEqual(r["state"],"PENCIL")
        self.assertTrue(r["model_proposal_only"])
        self.assertEqual(before,self.ctx)
    def test_20_classical_owner_is_explicit_per_fixture(self):
        self.assertEqual(truth(tool=1,permission=1,action="use"),1)
        self.assertEqual(truth(tool=1,permission=0,action="use"),0)
        self.assertEqual(truth(tool=0,permission=0,action="probe"),1)
        self.assertEqual(truth(tool=1,permission=1,action="publish"),0)
    def test_21_model_train_and_holdout_report(self):
        a=LowRankGraph()
        before=evaluate(self.model,None,"test")
        train(self.model,a,epochs=50)
        after=evaluate(self.model,a,"test")
        self.assertEqual(after["n"],48)
        self.assertGreaterEqual(after["accuracy"],0)
        self.assertLessEqual(after["accuracy"],1)
        self.assertNotEqual(before["loss"],after["loss"])
        self.assertEqual(a.version,"synthetic-trained-v1")
    def test_22_demo_records_classical_and_all_fork_deltas(self):
        m=demo()
        self.assertEqual(len(m["branches"]),5)
        self.assertEqual(m["strong_classical_accuracy"],1.0)
        self.assertLess(max(x["logit_difference"] for x in m["branches"]),1e-11)
        self.assertLess(m["qk_dot_products_shared"],m["qk_dot_products_full"])
        self.assertEqual(m["real_llm_or_external_benchmark"],"NOT_RUN")

if __name__=="__main__":unittest.main()
