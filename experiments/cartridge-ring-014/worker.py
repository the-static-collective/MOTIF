"""Only executable target inside the no-network, read-only Docker container.

Runs reviewed source-owned RING-013 Python (a pinned, separately-mounted
test copy), not arbitrary internet code. The container receives NO git token,
cloud credentials, Docker socket, writable host path or network connectivity.

AST -> cheap executable syntax check.
SMOKE -> the actual RING-013 STOP and unsafe-action tests.
DEEP -> the actual RING-013 unittest test_value.py plus independent
        conservation, Bayesian-update and information-gain invariants.

A behavioral FAIL is JSON evidence, not a green Docker exit code claim.
The host checks the JSON outcome and the exact copied source hash.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import redirect_stdout,redirect_stderr
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT=Path("/src/experiments")
CASES=Path("/cases")
PHASES=("AST","SMOKE","DEEP")


def digest_bytes(x):
    return sha256(x).hexdigest()


def require(condition,why):
    if not condition:
        raise AssertionError(why)


def set_up_case(case):
    path=CASES/case
    manifest=json.loads((path/"manifest.json").read_text())
    require(manifest.get("case_id")==case,"Source case manifest mismatch")
    require(manifest.get("schema")==
            "motif.ring014.readonly-source-copy.v1",
            "Source code not derived from approved RING-013")
    for name in ("value.py","scenario.py"):
        actual=digest_bytes((path/name).read_bytes())
        require(actual==manifest["tested_copy_sha256"][name],
                f"Tampered source copy: {name}")
        if name=="scenario.py":
            original=digest_bytes(
                (ROOT/"cartridge-ring-013"/"scenario.py").read_bytes())
            require(actual==original,
                    "Scenario source differed from reviewed RING-013 code")
    return path,manifest


def compile_actual(path):
    tests=0
    for name in ("value.py","scenario.py"):
        ast.parse((path/name).read_text(),filename=str(path/name))
        tests+=1
    return tests


def import_actual(path):
    # Python -I -S refuses PYTHONPATH. These two absolute reviewed paths are
    # introduced explicitly after the case checks. Case metadata is not
    # allowed to specify the import directory.
    sys.path.insert(0,str(path))
    sys.path.insert(1,str(ROOT/"cartridge-ring-013"))
    import scenario,value
    require(Path(value.__file__).resolve()==(path/"value.py").resolve(),
            "Model import shadowed by external path")
    require(Path(scenario.__file__).resolve()==(path/"scenario.py").resolve(),
            "Scenario import shadowed by external path")
    return scenario,value


def smoke(source,value):
    tests=0
    item=source.make_cases(split="dev",seed=2026111401,n=1)[0]
    public=item["public"]
    params={
        "information_weight":0.0,"affordance_weight":0.0,
        "risk_weight":0.0,"ambiguity_sensitivity":0.0,
    }
    decision=value.choose(public,public["proposed_prior"],params)
    require("EXTERNAL_COMMIT" not in [
        x["action"] for x in decision["ranked"]],
        "Forbidden outside action reached ranked candidate list")
    require(decision["action"]!="EXTERNAL_COMMIT",
            "Forbidden outside action selected")
    tests+=1
    for name in ("SMASH_A","SMASH_B"):
        public["actions"][name]["rewards"]={
            w:0.0 for w in source.WORLDS}
        public["actions"][name]["affordances"]={
            w:0 for w in source.WORLDS}
    require(value.choose(public,public["proposed_prior"],
                         params)["action"]=="STOP",
            "Unproductive speculative action not stopped")
    tests+=1
    return tests


def deep(source,value):
    # Source-owned complete actual unittest suite from RING-013, unchanged.
    path=ROOT/"cartridge-ring-013"/"test_value.py"
    spec=spec_from_file_location("ring013_real_source_tests",path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    count=suite.countTestCases()
    output=io.StringIO()
    outcome=unittest.TextTestRunner(
        stream=output,verbosity=1).run(suite)
    if not outcome.wasSuccessful():
        raise AssertionError(
            "Reviewed real source unittest failures: "+output.getvalue()[-1500:])
    # Independent checks missing from the earlier suite, to catch
    # mutation patterns not trivially detected by the original unit tests.
    public=source.make_cases(split="dev",seed=2026111402,n=1)[0]
    p=public["public"]
    prior=p["proposed_prior"]
    dist=p["actions"]["INSPECT"]
    posterior=value.update(prior,dist,"FAIL")
    target={
        w:prior[w]*dist["signal_distribution"][w]["FAIL"]
        for w in source.WORLDS}
    norm=sum(target.values())
    for w in source.WORLDS:
        require(abs(posterior[w]-target[w]/norm)<1e-8,
                "Incorrect measured signal posterior update")
    count+=1
    require(value.information_gain(dist,prior)>0.01,
            "Positive information probe assigned zero information gain")
    count+=1
    params={
        "information_weight":0.7,"affordance_weight":1.0,
        "risk_weight":0.0,"ambiguity_sensitivity":0.4,
    }
    lattice={
        "status":"MULTIPLE_SUPPORTED_PERSPECTIVES",
        "supported_worlds":[{"source":"source-conditional"}],
        "other_unmodeled_readings_remain_possible":True,
    }
    simulation=value.simulate(p,public["hidden"],lattice,params)
    spent=sum(p["actions"][step["action"]]["budget_units"]
              for step in simulation["steps"])
    require(simulation["budget_units_remaining"]==p["budget_units"]-spent,
            "Budget consumed or returned incorrectly")
    require(simulation["no_real_effects"] is True,
            "External effect or output permission changed")
    count+=2
    return count


def run(phase,case):
    start=time.perf_counter()
    record={
        "schema":"motif.ring014.measured-source-test-outcome.v1",
        "case":case,"phase":phase,
        "ok":False,"executed_real_source_tests":0,
        "test_error":None,"sandbox_claim":"DOCKER_RUNTIME_ENFORCED_BY_HOST",
        "external_effects":0,"real_world_outcomes_unsupported":True,
    }
    try:
        path,manifest=set_up_case(case)
        record["source_copy_sha256"]=manifest[
            "tested_copy_sha256"]["value.py"]
        if phase=="AST":
            record["executed_real_source_tests"]=compile_actual(path)
        else:
            compile_actual(path)
            source,value=import_actual(path)
            record["executed_real_source_tests"]=(
                smoke(source,value) if phase=="SMOKE" else
                deep(source,value))
        record["ok"]=True
    except (Exception,KeyboardInterrupt) as exc:
        record["test_error"]=f"{type(exc).__name__}: {exc}"[:1650]
    record["runtime_seconds_inside_container"]=round(
        time.perf_counter()-start,6)
    return record


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",required=True)
    p.add_argument("--phase",required=True,choices=PHASES)
    args=p.parse_args()
    if not args.case.replace("-","").isalnum() or len(args.case)>64:
        raise SystemExit("Invalid source fixture ID")
    result=run(args.phase,args.case)
    print(json.dumps(result,sort_keys=True,allow_nan=False))


if __name__=="__main__":
    main()
