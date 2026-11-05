#!/usr/bin/env python3
"""MOTIF-020 — reason from real GHoT resource receipts, not invented credits.

This code does not infer electrical joules from CPU time, pretend a dry-run
offer is real execution, or reward source mutation. It proposes one testable
resource-reuse question using a *source-pinned*, Git-checked GHoT witness.
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import json
import math
from pathlib import Path
import sys

SCHEMA="motif.embodied-question/v1"
SOURCE_SCHEMA="ghot.resource-witness/v1"
GHOT_SHA="0cbd111a1f7d58a3e4d1dacaeb6be067cbffe9ad"
GHOT_GIT_BLOB="4c46c92b0529920f4b990d45b64a855abdb7d385"
GHOT_RUN="https://github.com/the-static-collective/GHoT/actions/runs/42043913470"
SOURCE_MOTIF_019="1bb4028141eb20a8798bed338dcb3d851284de22"
MAX_BYTES=120_000
SOURCE=Path(__file__).resolve().parent/"evidence"/"ghot-resource-witness-2026-11-05.json"

class HOLD(ValueError):
    pass

def require(ok,reason):
    if not ok:raise HOLD(reason)

def value(x):
    require(type(x) in (int,float) and math.isfinite(x) and x>=0,
            "RESOURCE_COUNTER_MISSING_OR_NONFINITE")
    return x

def githash(raw):
    return sha1(b"blob "+str(len(raw)).encode("ascii")+bytes([0])+raw).hexdigest()

def read_pinned(path=SOURCE):
    require(type(path) is Path and path.is_file() and not path.is_symlink(),
            "LOCAL_PINNED_SOURCE_NOT_FOUND")
    require(0<path.stat().st_size<=MAX_BYTES,
            "RESOURCE_WITNESS_OVERSIZE_OR_EMPTY")
    content=path.read_bytes()
    require(githash(content)==GHOT_GIT_BLOB,
            "GHOT_SOURCE_RECEIPT_BYTES_CHANGED")
    try:return json.loads(content)
    except (ValueError,UnicodeError) as exc:
        raise HOLD("RESOURCE_WITNESS_JSON_INVALID") from exc

def inspect(report):
    require(type(report) is dict and report.get("schema")==SOURCE_SCHEMA,
            "INVALID_GHOT_RECEIPT")
    require(report.get("authority") is False and
            report.get("automatic_model_promotion") is False and
            report.get("source_code_self_modified") is False and
            report.get("model_weights_modified") is False and
            report.get("real_remote_tasks_executed")==0,
            "GHOT_RECEIPT_HAS_UNADMITTED_EFFECTS")
    source=report.get("source",{})
    require(type(source) is dict and source.get("source_commit")==SOURCE_MOTIF_019
            and source.get("git_blob_sha1_expected")=="0cf1303cdeb83d9c29fe417ac19c66c217ddf63d"
            and source.get("source_kind")=="motif.question-kind-physical-test/v1",
            "GHOT_SOURCE_WITNESS_NOT_EXPECTED_MOTIF")
    benchmark=report.get("benchmark",{})
    observed=benchmark.get("observed",{})
    original=observed.get("reparse",{})
    reused=observed.get("reuse",{})
    require(benchmark.get("all_answers_bitwise_equal") is True and
            benchmark.get("shape")=="same-answer-parse-every-time-vs-content-verified-reuse"
            and benchmark.get("status")=="OBSERVED_LOCAL_CPU_REUSE_ADVANTAGE_NOT_POWER_SAVINGS_PROOF",
            "RESOURCE_QUALITY_OR_BENCHMARK_NOT_COMPARABLE")
    trials=benchmark.get("trials_each")
    repeats=benchmark.get("repetitions_per_trial")
    require(type(trials) is int and 2<=trials<=11 and
            type(repeats) is int and 10<=repeats<=2000,
            "SAMPLE_SIZE_OUTSIDE_EXPERIMENT_ENVELOPE")
    raw=benchmark.get("raw_trials")
    require(type(raw) is list and len(raw)==2*trials,"MISSING_TRIAL_RECEIPTS")
    groups={"reparse":[],"reuse":[]}
    answers=set()
    for t in raw:
        require(type(t) is dict and t.get("mode") in groups and
                t.get("repetitions")==repeats and
                type(t.get("answer_sha256")) is str and
                len(t["answer_sha256"])==64 and
                all(ch in "0123456789abcdef" for ch in t["answer_sha256"]),
                "BAD_RESOURCE_TRIAL")
        answers.add(t["answer_sha256"])
        for key in ("cpu_time_ns","wall_time_ns","python_tracemalloc_peak_bytes",
                    "actual_bytes_read","local_sha256_hash_operations",
                    "json_validation_parses"):
            value(t.get(key))
        require(t["actual_bytes_read"]==repeats*source.get("source_length_bytes",0) and
                t["local_sha256_hash_operations"]==repeats and
                t["json_validation_parses"]==(repeats if t["mode"]=="reparse" else 1),
                "TRIAL_WORK_ACCOUNTING_INCONSISTENT")
        require(t.get("package_rapl_joules_IF_VISIBLE") is None,
                "UNEXPECTED_ENERGY_SENSOR_REQUIRES_NEW_REVIEW")
        groups[t["mode"]].append(t)
    require(len(answers)==1 and all(len(a)==trials for a in groups.values()),
            "PHYSICAL_TASK_OUTPUT_OR_TRIAL_PAIR_DIFFERS")
    # Cross-check summaries rather than simply trusting the claimed gain.
    from statistics import median
    for mode,records in groups.items():
        s=original if mode=="reparse" else reused
        require(value(s.get("median_cpu_time_ns"))==median(
                    r["cpu_time_ns"] for r in records) and
                value(s.get("median_wall_time_ns"))==median(
                    r["wall_time_ns"] for r in records) and
                value(s.get("median_python_tracemalloc_peak_bytes"))==median(
                    r["python_tracemalloc_peak_bytes"] for r in records) and
                s.get("bytes_read_per_trial")==repeats*source.get("source_length_bytes") and
                s.get("hashes_per_trial")==repeats and
                s.get("parses_per_trial")==(repeats if mode=="reparse" else 1) and
                s.get("rapl_package_joules_median_if_measured") is None,
                "METER_SUMMARY_DISAGREES_WITH_RAW_TRIALS")
    cpu_gain=round(original["median_cpu_time_ns"]-reused["median_cpu_time_ns"])
    wall_gain=round(original["median_wall_time_ns"]-reused["median_wall_time_ns"])
    require(cpu_gain==observed.get("cpu_time_delta_ns_reparse_minus_reuse"),
            "CPU_SAVINGS_CLAIM_NOT_RECOMPUTED")
    require(observed.get("energy_joules_comparison_claim_available") is False,
            "FALSE_POWER_INFERENCE")
    accounting=report.get("resource_accounting",{})
    require(accounting.get("no_arbitrary_credit_prices") is True and
            accounting.get("actual_energy_usage_attributed_to_this_task") is False and
            accounting.get("real_energy_joules_measured") is False and
            accounting.get("grid_co2_kg_measured") is False,
            "UNMEASURED_ENERGY_OR_CREDIT_CLAIM")
    power=report.get("power",{})
    require(power.get("type")=="HYPOTHETICAL_NATIVE_DRY_RUN_NOT_REAL_OFFER" and
            power.get("real_task_dispatched") is False and
            power.get("real_energy_budget_reserved") is False and
            power.get("native_ghot_scheduler_action") in ("run_here","hold","no_eligible_body"),
            "FAKE_GHOT_REAL_SCHEDULE")
    # The decision is intentionally not a scalar utility maximum: time, RAM,
    # electrical energy, source freshness and user urgency are different units.
    if cpu_gain>0 and wall_gain>0:
        proposed="HELD_REUSE_CANDIDATE_FOR_MORE_BODIES"
        question=("Can verified evidence reuse reduce compute on the operator's "
                  "actual device while preserving freshness and usefulness, "
                  "especially when GHoT reports scarce battery or thermal pressure?")
    else:
        proposed="HOLD_NO_STABLE_LOCAL_WORK_REDUCTION"
        question=("Which part of the measured answer path actually consumes "
                  "resources, and is evidence reuse worth its correctness risk?")
    result={
        "schema":SCHEMA,
        "state":"OBSERVED_PHYSICAL_COMPUTE_PROXY_NOT_MEASURED_JOULES",
        "source":{"GHOT_commit":GHOT_SHA,
                  "GHOT_git_blob":GHOT_GIT_BLOB,
                  "GHOT_resource_run":GHOT_RUN,
                  "local_receipt_sha256":sha256(json.dumps(report,sort_keys=True,
                               separators=(",",":"),ensure_ascii=True).encode()).hexdigest(),
                  "source_evidence":"ACTUAL_RUNNER_BENCHMARK_OF_ARCHIVED_PUBLIC_RESEARCH_REPORT"},
        "identical_evidence_derived_answer":True,
        "repeated_questions_per_trial":repeats,
        "trial_count_each":trials,
        "measured_work":{
           "reparse_median_cpu_ns":original["median_cpu_time_ns"],
           "reuse_median_cpu_ns":reused["median_cpu_time_ns"],
           "median_cpu_ns_reduction_per_batch":cpu_gain,
           "median_wall_ns_reduction_per_batch":wall_gain,
           "actual_source_bytes_read_per_batch":original["bytes_read_per_trial"],
           "bytes_read_saved":0,
           "json_validations_reparse":repeats,
           "json_validations_reuse":1,
           "process_cpu_time_is_not_joules":True,
           "electrical_energy_joules":None,
           "measured_power_draw_watts":None,
           "total_CO2_kg":None,
        },
        "GHOT_observed_power_willingness":power.get("native_power_willingness"),
        "GHOT_scheduler_hypothetical_action":power.get("native_ghot_scheduler_action"),
        "GHOT_actual_execution":False,
        "next_question":question,
        "disposition":proposed,
        "operator_defined_constraints_required":[
          "answer_freshness_requirement","actual_device_capabilities",
          "urgency_and_deferrability","acceptable_response_latency",
          "battery_or_thermal_budget_if_physically_measured",
          "correctness_and_data_provenance_requirements"
        ],
        "future_real_energy_adapter":{
          "target":"ghot.power_field / hardware-specific energy meter",
          "measurement_units":"joules, watts, bytes, nanoseconds",
          "available_now":False,
          "missing_source_behavior":"UNKNOWN_NOT_ZERO",
          "promotion_gate":"INDIVIDUAL_BODY_ENERGY_CALIBRATION_AND_INDEPENDENT_TASK_REPLICATION"
        },
        "limits":[
          "Five matched local GitHub Actions trials are not a cross-hardware, cross-load energy study.",
          "CPU time excludes direct calibrated electrical power; the runner exposed no usable Joules meter.",
          "The experimental GHoT scheduler decision used an explicitly hypothetical single local offer, never real dispatch.",
          "Original public river measurements were retrieved retrospectively; this resource measurement is about computation, not river prediction improvement.",
          "A cryptographic source hash supports cache invalidation; it does not independently authenticate underlying river measurements.",
          "A faster cached answer may still be wrong, outdated or inappropriate for a different task; operator constraints come first."
        ],
        "independent_Joules_verified":False,
        "model_retrained":False,"automatic_promotion":False,
        "remote_execution":False,"authority":False
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        if args.source!=SOURCE:
            require(args.source.resolve()==SOURCE.resolve(),"CANNOT_OVERRIDE_PINNED_SOURCE")
        result=inspect(read_pinned(args.source))
        j=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.out:args.out.write_text(j,encoding="utf8")
        print(j)
        return 0
    except (OSError,ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
        print("HOLD: "+str(exc)[:140],file=sys.stderr)
        return 2

if __name__=="__main__":raise SystemExit(main())
