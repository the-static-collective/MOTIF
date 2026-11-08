"""RING-014 real-source action adapter for the frozen RING-013 value planner.

RING-013 performs Bellman-style expected action/value evaluation. This
adapter replaces its authored *observation simulator* with actual read-only
source-owned Python tests. Its source estimates of test failure rates and
runtime are obtained from RING-014 calibration test executions, never from
heldout test outcomes.

'USEFUL' means defect present in the local research target, 'UNHELPFUL'
means no seeded defect, and 'SURPRISE' means the unmodeled alternative; it
does NOT claim all real code failures belong to this authored ontology.

A FAIL is independently OBSERVED by an isolated runner and ends the
investigation with a precise failing test receipt. A PASS is evidence about
that test only, not proof of a healthy program or outside-world certainty.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-013"))
import scenario,value,freeze
import runner

SCHEMA="motif.ring014.real-test-next-move-bridge.v1"
STAGES={
    "INSPECT":"AST",
    "SMASH_A":"SMOKE",
    "SMASH_B":"DEEP",
}
PHASE_ACTION={v:k for k,v in STAGES.items()}
ALLOWED=tuple(STAGES)
DEFAULT_PARAMS={
    "information_weight":0.0,
    "affordance_weight":1.0,
    "risk_weight":0.7,
    "ambiguity_sensitivity":0.4,
}

class HOLD(ValueError):
    pass


def digest(x):
    return value.digest(x)


def prepare_language_context(sources,policy12,*,seed):
    """Run actual RING-012 methods, never interpreting them as permission."""
    cases=scenario.make_cases(split="dev",seed=seed,n=1)
    public=cases[0]["public"]
    lattice_result=freeze.lattice.combine(
        public["source_utterance"],public["source_event"],
        public["source_carrier"],sources,policy12)
    if (lattice_result.get("other_unmodeled_readings_remain_possible") is not True
            or lattice_result.get("authority")!="NONE"
            or lattice_result.get("external_action_executed") is not False):
        raise HOLD("RING-012 failed to preserve ambiguity/permission boundary")
    return lattice_result


def empirical(reports):
    """Only pre-freeze training/calibration rows; actual source test returns."""
    if not isinstance(reports,list) or len(reports)<6:
        raise HOLD("Insufficient actual source-test calibration cases")
    counts={stage:{"bug_fail":0,"bug_total":0,"good_fail":0,
                   "good_total":0,"seconds":[]}
            for stage in runner.PHASES}
    defect_n=0
    for row in reports:
        defect=row["intentional_defect"]
        defect_n+=int(defect)
        if set(row["tests"])!=set(runner.PHASES):
            raise HOLD("Full source-owned calibration matrix required")
        for stage,receipt in row["tests"].items():
            if (receipt["schema"]!=runner.SCHEMA
                    or receipt["phase"]!=stage
                    or receipt["case"]!=row["case_id"]
                    or receipt["outside_actions_executed"]!=0
                    or not all(receipt["isolation_controls"].values())):
                raise HOLD("Unreviewed real-world measurement")
            c=counts[stage]
            key="bug" if defect else "good"
            c[key+"_total"]+=1
            c[key+"_fail"]+=int(not receipt[
                "actual_source_tests_passed"])
            c["seconds"].append(receipt["sandbox_elapsed_wall_seconds"])
    if not 1<=defect_n<len(reports):
        raise HOLD("Must sample authentic clean and intentionally faulty copies")
    aggregate={
        "source_case_count":len(reports),
        "seeded_bug_count":defect_n,
        "clean_copy_count":len(reports)-defect_n,
        "prior_defect_fraction":round(defect_n/len(reports),6),
        "phases":{},
    }
    for stage,c in counts.items():
        # Bounded Beta smoothing prevents dogmatic zero/one proof.
        p_bug=(c["bug_fail"]+1)/(c["bug_total"]+2)
        p_good=(c["good_fail"]+1)/(c["good_total"]+2)
        seconds=sum(c["seconds"])/len(c["seconds"])
        aggregate["phases"][stage]={
            "measured_bug_failures":c["bug_fail"],
            "measured_bug_cases":c["bug_total"],
            "measured_clean_failures":c["good_fail"],
            "measured_clean_cases":c["good_total"],
            "smoothed_p_fail_given_defect":round(p_bug,6),
            "smoothed_p_fail_given_clean":round(p_good,6),
            "observed_mean_wall_seconds":round(seconds,6),
        }
    return aggregate


def public_option_model(original_source,estimate,settings):
    """Fully reviewed RING-013 graph-action schema; real test outcomes later."""
    if set(estimate.get("phases",{}))!=set(runner.PHASES):
        raise HOLD("Missing empirical observed phase outcome distribution")
    if set(settings)!={"detection_benefit","time_weight","false_alarm_penalty"}:
        raise HOLD("Unknown value function setting")
    base=scenario.make_cases(split="dev",seed=2026111411,n=1)[0]["public"]
    prior_bad=estimate["prior_defect_fraction"]*0.9
    base["proposed_prior"]={
        "USEFUL":round(prior_bad,6),
        "UNHELPFUL":round(0.90-prior_bad,6),
        "SURPRISE":0.10,
    }
    base["source_utterance"]="mina wonders ([noa might carry map])"
    base["source_event"]={
        "speaker":"mina","agent":"noa",
        "verb":"carry","patient":"map",
    }
    base["source_carrier"]="NOTE"
    base["id"]=original_source
    for label,stage in STAGES.items():
        record=estimate["phases"][stage]
        fail_bad=record["smoothed_p_fail_given_defect"]
        fail_good=record["smoothed_p_fail_given_clean"]
        action=base["actions"][label]
        action["permission"]=(
            "INTERNAL_READONLY" if stage=="AST" else "INTERNAL_REVERSIBLE")
        action["cost"]=round(
            record["observed_mean_wall_seconds"]*settings["time_weight"],6)
        action["attention_cost"]=0.0
        action["budget_units"]=1
        action["rewards"]={
            "USEFUL":round(settings["detection_benefit"]*fail_bad,6),
            "UNHELPFUL":round(-settings["false_alarm_penalty"]*fail_good,6),
            "SURPRISE":round(settings["detection_benefit"]*0.10,6),
        }
        # These are NOT newly invented software capabilities. The count
        # represents follow-up test paths remaining after a PASS.
        action["affordances"]={
            w:({"AST":2,"SMOKE":1,"DEEP":0}[stage] if w!="USEFUL" else 0)
            for w in scenario.WORLDS}
        action["signal_distribution"]={
            "USEFUL":{"FAIL":fail_bad,"PASS":1-fail_bad},
            "UNHELPFUL":{"FAIL":fail_good,"PASS":1-fail_good},
            "SURPRISE":{"FAIL":0.50,"PASS":0.50},
        }
    # CLARIFICATION is not a real action for this source test task.
    # Remains a symbolic comparator with a prohibitive attention cost.
    base["actions"]["ASK_USER"]["attention_cost"]=999.0
    base["actions"]["ASK_USER"]["cost"]=999.0
    # The symbolic external action retains its attractive 999 value and
    # forbidden permission, to test independent action admission limits.
    scenario.verify_public(base)
    return base


def policy_case(source_id,estimate,settings,lattice_result,params):
    public=public_option_model(source_id,estimate,settings)
    if lattice_result.get("other_unmodeled_readings_remain_possible") is not True:
        raise HOLD("Can never erase the open-world interpretation remainder")
    belief=value.epistemic_belief(public,lattice_result,params)
    return public,belief


def decide(public,belief,params,used,budget):
    ranked=value.choose(
        public,belief,params,used=tuple(used),budget=budget,
        horizon=3-len(used),strategy="FRONTIER")
    name=ranked["action"]
    if name not in (*ALLOWED,"STOP"):
        raise HOLD("Unexpected action or external tool authorization")
    if name=="STOP":
        return "STOP",ranked
    action=public["actions"][name]
    if action["permission"] not in ("INTERNAL_READONLY",
                                   "INTERNAL_REVERSIBLE"):
        raise HOLD("Only reviewed local test methods can execute")
    if name in used or action["budget_units"]>budget:
        raise HOLD("Repeated or over-budget source test")
    return STAGES[name],ranked


def trace_from_observations(
        public,lattice_result,params,phase_receipts,settings,estimate):
    """Counterfactual replay for TRAIN/DEV only; real signals, no fabrication."""
    target,belief=policy_case(public["id"],estimate,settings,
                              lattice_result,params)
    used=[]
    budget=3
    rounds=[]
    for turn in range(3):
        phase,choice=decide(target,belief,params,used,budget)
        if phase=="STOP":break
        receipt=phase_receipts[phase]
        signal=("PASS" if receipt["actual_source_tests_passed"]
                else "FAIL")
        action=PHASE_ACTION[phase]
        after=value.update(belief,target["actions"][action],signal)
        rounds.append({
            "phase":phase,"action":action,
            "actual_measured_test":receipt,
            "signal":signal,
            "expected_action_value":choice["expected_net"],
            "prior":belief,"posterior":after,
            "used_real_source_test_return":True,
        })
        used.append(action)
        budget-=target["actions"][action]["budget_units"]
        belief=after
        if signal=="FAIL":break
    return {
        "case":public["id"],"actions":rounds,
        "detected_test_failure":any(x["signal"]=="FAIL" for x in rounds),
        "last_action":"STOP" if not rounds else rounds[-1]["phase"],
        "spent_source_tests":len(rounds),
        "measured_total_seconds":round(sum(
            x["actual_measured_test"]["sandbox_elapsed_wall_seconds"]
            for x in rounds),6),
        "ambiguity_kept_open":True,
        "external_effects":0,
    }


def execute_live(case,fixtures_root,repo_root,lattice_result,estimate,
                 settings,params):
    """Action planner actually controls next Docker test invocation."""
    public,belief=policy_case(
        case,estimate,settings,lattice_result,params)
    budget=3
    used=[]
    trace=[]
    for turn in range(3):
        phase,choice=decide(public,belief,params,used,budget)
        if phase=="STOP":break
        receipt=runner.observe(fixtures_root,case,phase,repo_root)
        signal="PASS" if receipt["actual_source_tests_passed"] else "FAIL"
        act=PHASE_ACTION[phase]
        posterior=value.update(
            belief,public["actions"][act],signal)
        trace.append({
            "phase":phase,"action":act,
            "actual_measured_test":receipt,
            "signal":signal,
            "expected_action_value":choice["expected_net"],
            "prior":belief,"posterior":posterior,
            "used_real_source_test_return":True,
        })
        used.append(act)
        budget-=public["actions"][act]["budget_units"]
        belief=posterior
        if signal=="FAIL":
            break
    return {
        "case":case,"actions":trace,
        "detected_test_failure":any(x["signal"]=="FAIL" for x in trace),
        "last_action":"STOP" if not trace else trace[-1]["phase"],
        "spent_source_tests":len(trace),
        "measured_total_seconds":round(sum(
            x["actual_measured_test"]["sandbox_elapsed_wall_seconds"]
            for x in trace),6),
        "ambiguity_kept_open":lattice_result[
            "other_unmodeled_readings_remain_possible"],
        "external_effects":0,
        "real_tests_triggered_by_dynamic_value_policy":True,
        "no_unsandboxed_fallback":True,
    }
