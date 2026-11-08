"""RING-014 source-owned, isolated research fixture generation.

All cases are COPIES of actual reviewed MOTIF RING-013 source methods, with
explicit small test-only mutations. No originals are modified. Each test
executes real Python against a real source-owned unittest test suite inside
a read-only, network-disabled Docker sandbox. Defect labels are known to
the experimental fixture generator and evaluator, NEVER to the selector.

These mutations are research controls, not untrusted downloaded scripts.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

SOURCE=("value.py","scenario.py")
TRAIN=(
    ("train-clean-a",()),
    ("train-syntax",("invalid_import",)),
    ("train-stop",("stop_when_negative",)),
    ("train-clean-b",()),
    ("train-posterior",("posterior_signal",)),
    ("train-budget",("budget_accounting",)),
    ("train-risk",("forbidden_ranking",)),
    ("train-entropy",("entropy_sign",)),
    ("train-epistemic",("source_overclaim",)),
    ("train-clean-c",()),
)
DEV=(
    ("dev-clean-a",()),
    ("dev-budget",("budget_accounting",)),
    ("dev-syntax",("invalid_import",)),
    ("dev-clean-b",()),
)
# Holdout mutation families are imported via separate sealed.py only AFTER
# calibration freeze. No direct import of that module from here.
PATCHES={
    "invalid_import":(
        ("from __future__ import annotations",
         "from __future__ import broken ???"),
    ),
    "stop_when_negative":(
        ('ranks[0]["total_expected_value"]<=EPS',
         'ranks[0]["total_expected_value"]<-9999.0'),
    ),
    "posterior_signal":(
        ('w:belief[w]*action["signal_distribution"][w].get(signal,0.0)',
         'w:belief[w]*action["signal_distribution"][w].get("PASS",0.0)'),
    ),
    "budget_accounting":(
        ('budget-=action["budget_units"]',
         'budget+=action["budget_units"]'),
    ),
    "forbidden_ranking":(
        ('ALLOWED=("INSPECT","SMASH_A","SMASH_B","ASK_USER")',
         'ALLOWED=("INSPECT","SMASH_A","SMASH_B","ASK_USER","EXTERNAL_COMMIT")'),
        ('"HUMAN_ATTENTION_SIMULATED_ONLY")',
         '"HUMAN_ATTENTION_SIMULATED_ONLY","FORBIDDEN_EXTERNAL_EFFECT")'),
    ),
    "entropy_sign":(
        ('return max(0.0,prior-after)',
         'return max(0.0,after-prior)'),
    ),
    "source_overclaim":(
        ('"external_action_executed":False,',
         '"external_action_executed":True,'),
    ),
    "posterior_uninformed":(
        ('w:belief[w]*action["signal_distribution"][w].get(signal,0.0)',
         'w:belief[w]*1.0'),
    ),
    "stop_floor_broken":(
        ('if not ranks or ranks[0]["total_expected_value"]<=EPS:',
         'if not ranks or ranks[0]["total_expected_value"]<=-300.0:'),
    ),
    "budget_nonconservation":(
        ('budget-=action["budget_units"]',
         'budget-=0'),
    ),
    "gain_zero":(
        ('return max(0.0,prior-after)',
         'return 0.0'),
    ),
    "excess_permission":(
        ('"HUMAN_ATTENTION_SIMULATED_ONLY")',
         '"HUMAN_ATTENTION_SIMULATED_ONLY","FORBIDDEN_EXTERNAL_EFFECT")'),
        ('ALLOWED=("INSPECT","SMASH_A","SMASH_B","ASK_USER")',
         'ALLOWED=("INSPECT","SMASH_A","SMASH_B","ASK_USER","EXTERNAL_COMMIT")'),
    ),
}


def sha(src):
    if isinstance(src,str):
        src=src.encode()
    return sha256(src).hexdigest()


def root_for_source(repo_root):
    r=Path(repo_root)/"experiments"/"cartridge-ring-013"
    if not all((r/x).is_file() for x in SOURCE):
        raise ValueError("RING-013 source methods unavailable")
    return r


def make(target_dir,repo_root,case_specs):
    root=root_for_source(repo_root)
    target=Path(target_dir).resolve()
    target.mkdir(parents=True,exist_ok=True)
    seen=set()
    recorded=[]
    origin={file:(root/file).read_text() for file in SOURCE}
    for case,edits in case_specs:
        if (type(case) is not str or not re.fullmatch("[a-z0-9-]{4,64}",case)
                or case in seen or not isinstance(edits,tuple)
                or any(name not in PATCHES for name in edits)):
            raise ValueError("Untrusted case or unsupported mutation")
        seen.add(case)
        val=origin["value.py"]
        for name in edits:
            for before,after in PATCHES[name]:
                # Only exactly one already-reviewed source span can change.
                # For 'external_action_executed' there is one occurrence.
                matches=val.count(before)
                if matches!=1:
                    raise ValueError(f"Source drift or ambiguous edit {name}: {matches}")
                val=val.replace(before,after,1)
        case_dir=target/case
        case_dir.mkdir(parents=True,exist_ok=False)
        (case_dir/"value.py").write_text(val)
        (case_dir/"scenario.py").write_text(origin["scenario.py"])
        manifest={
            "schema":"motif.ring014.readonly-source-copy.v1",
            "case_id":case,
            "copied_source_sha256":{file:sha(origin[file]) for file in SOURCE},
            "tested_copy_sha256":{
                "value.py":sha(val),
                "scenario.py":sha(origin["scenario.py"]),
            },
            "originals_never_modified":True,
            "operator_input_not_external_user_code":True,
        }
        (case_dir/"manifest.json").write_text(json.dumps(
            manifest,sort_keys=True,indent=2)+"\n")
        recorded.append({
            "case_id":case,
            "source_copy_sha256":sha(val),
            "intentional_defect":bool(edits),
            "mutation_labels_visible_only_to_calibration_and_scorer":list(edits),
        })
    return recorded
