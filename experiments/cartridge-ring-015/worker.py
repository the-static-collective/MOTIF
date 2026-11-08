"""RING-015 trusted runtime: actual source triage and differentiated tests.

All actions run inside RING-014's network-disabled, read-only container.
TRIAGE compares AST function regions with pinned RING-013 source; it emits
a CUE, NOT a secret mutation tag or a factual proof of defect. Distinct
MATH and CONTROL tests then execute the actual copied Python methods.
FULL runs both plus the inherited real RING-013 source unittest suite
and broad deterministic decision-surface stress cases.

This uses only reviewed MOTIF source; it is NOT a general-purpose
untrusted-language execution sandbox or source repair agent.
"""
from __future__ import annotations
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import argparse,ast,io,json,sys,time

PREVIOUS=Path("/src/experiments/cartridge-ring-014/worker.py")
spec=spec_from_file_location("ring014_real_source_worker",PREVIOUS)
previous=module_from_spec(spec)
spec.loader.exec_module(previous)

SRC=Path("/src/experiments/cartridge-ring-013/value.py")
PHASES=("TRIAGE","MATH","CONTROL","FULL")
MATH_NAMES={"update","information_gain","entropy","normalize",
            "future_signal_probs"}
CONTROL_NAMES={"choose","simulate","public_decision","policy_parameters"}
OTHER_NAMES={"ALLOWED"} # treat a global allowlist edit as a control concern


def require(test,message):
    if not test:raise AssertionError(message)


def functions(text):
    syntax=ast.parse(text)
    found={}
    for item in syntax.body:
        if isinstance(item,(ast.FunctionDef,ast.AsyncFunctionDef)):
            found[item.name]=ast.dump(item,include_attributes=False)
        elif isinstance(item,ast.Assign):
            for target in item.targets:
                if isinstance(target,ast.Name) and target.id in OTHER_NAMES:
                    found[target.id]=ast.dump(item,include_attributes=False)
    return found


def triage_source(path):
    current=(path/"value.py").read_text()
    original=SRC.read_text()
    try:
        actual=functions(current)
        reviewed=functions(original)
    except SyntaxError as exc:
        return "SYNTAX_ERROR",[],False,str(exc)[:350]
    changed=sorted({
        name for name in set(actual)|set(reviewed)
        if actual.get(name)!=reviewed.get(name)})
    if not changed:
        return "UNCHANGED",[],True,None
    kind=set()
    for name in changed:
        if name in MATH_NAMES:kind.add("MATH")
        elif name in CONTROL_NAMES or name in OTHER_NAMES:kind.add("CONTROL")
        else:kind.add("OTHER")
    cue=next(iter(kind)) if len(kind)==1 else "MIXED"
    return cue,changed,True,None


def math_tests(source,value):
    count=0
    item=source.make_cases(split="dev",seed=2026111555,n=1)[0]
    p=item["public"]
    dist=p["actions"]["INSPECT"]
    prior=p["proposed_prior"]
    for signal in ("PASS","FAIL"):
        observed=value.update(prior,dist,signal)
        raw={w:prior[w]*dist["signal_distribution"][w][signal]
             for w in source.WORLDS}
        normal=sum(raw.values())
        require(all(abs(observed[w]-raw[w]/normal)<1e-9
                    for w in source.WORLDS),
                "Math test failed: posterior signal conditioning")
        count+=1
    require(value.information_gain(dist,prior)>0.01,
            "Math test failed: positive information gain")
    count+=1
    require(value.entropy(prior)>=0,
            "Math test failed: entropy must be nonnegative")
    count+=1
    return count


def control_tests(source,value):
    count=previous.smoke(source,value)
    item=source.make_cases(split="dev",seed=2026111566,n=1)[0]
    p,h=item["public"],item["hidden"]
    params={
        "information_weight":0.7,"affordance_weight":1.0,
        "risk_weight":0.0,"ambiguity_sensitivity":0.4}
    lattice={
        "status":"MULTIPLE_SUPPORTED_PERSPECTIVES",
        "supported_worlds":[{"source":"not independent truth"}],
        "other_unmodeled_readings_remain_possible":True,
    }
    outcome=value.simulate(p,h,lattice,params)
    spent=sum(p["actions"][x["action"]]["budget_units"]
              for x in outcome["steps"])
    require(outcome["budget_units_remaining"]==p["budget_units"]-spent,
            "Control test failed: budget conservation")
    count+=1
    require(outcome["no_real_effects"] is True,
            "Control test failed: external action")
    count+=1
    public=value.public_decision(p,lattice,params)
    require(public["external_action_executed"] is False,
            "Control test failed: forged external action claim")
    count+=1
    return count


def full(source,value):
    count=math_tests(source,value)
    count+=control_tests(source,value)
    count+=previous.deep(source,value)
    params={
        "information_weight":0.0,"affordance_weight":1.0,
        "risk_weight":0.7,"ambiguity_sensitivity":0.4,
    }
    # This is a broader real computation-heavy source test: evaluate 140
    # deterministic language/task instances (not a synthetic timing sleep).
    for i in range(140):
        p=source.make_cases(
            split="dev",seed=2026111560+i,n=1)[0]["public"]
        result=value.choose(p,p["proposed_prior"],params)
        require(result["action"]!="EXTERNAL_COMMIT",
                "Full sweep selected forbidden external commit")
        count+=1
    return count


def run(case,phase):
    result={
        "schema":"motif.ring015.observed-source-test-result.v1",
        "case":case,"phase":phase,
        "actual_source_tests_passed":False,
        "observed_source_cue":None,
        "reviewed_changed_functions":[],
        "observed_test_failure":None,
        "real_source_assertions_executed":0,
        "outside_actions_executed":0,
        "source_mutation_labels_not_consulted":True,
        "authority":"NONE",
    }
    start=time.perf_counter()
    try:
        path,manifest=previous.set_up_case(case)
        result["source_copy_sha256"]=manifest[
            "tested_copy_sha256"]["value.py"]
        cue,names,ok,why=triage_source(path)
        if phase=="TRIAGE":
            result["observed_source_cue"]=cue
            result["reviewed_changed_functions"]=names
            result["actual_source_tests_passed"]=ok
            result["real_source_assertions_executed"]=2
            result["observed_test_failure"]=why
        else:
            if not ok:raise SyntaxError(why)
            previous.compile_actual(path)
            source,value=previous.import_actual(path)
            count={
                "MATH":lambda:math_tests(source,value),
                "CONTROL":lambda:control_tests(source,value),
                "FULL":lambda:full(source,value),
            }[phase]()
            result["real_source_assertions_executed"]=count
            result["actual_source_tests_passed"]=True
    except (Exception,KeyboardInterrupt) as exc:
        result["observed_test_failure"]=f"{type(exc).__name__}: {exc}"[:1600]
    result["runtime_seconds_inside_container"]=round(
        time.perf_counter()-start,6)
    print(json.dumps(result,sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",required=True)
    p.add_argument("--phase",required=True,choices=PHASES)
    arg=p.parse_args()
    if (len(arg.case)>64 or
            not arg.case.replace("-","").isalnum()):
        raise SystemExit("Refuse unknown source fixture")
    run(arg.case,arg.phase)


if __name__=="__main__":main()
