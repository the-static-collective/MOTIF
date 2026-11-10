"""CONFLUENCE-002: four real source modules in one typed, synthetic loop.

Calls canonical CONFLUENCE-001 -> original MOTIF-003, native MOTIF-006,
native FIELD-008 BlanchLedger, and native COLLECTIVE-001 proof re-entry.
Foreign modules are checked out to EXACT SHA pins at CI runtime.
This remains a fictional set/assembly task, not a claim about real fencing.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
FIELD_SHA = "581ed7cbc289f65f42949dd332476eb672467a7c"
COLLECTIVE_SHA = "269006b559dbc73766888bcd11f5f294b8e6aa64"
FIELD_ROOT = ROOT / "sources" / "field008"
COLLECTIVE_ROOT = ROOT / "sources" / "collective001"
for path in [ROOT / "experiments" / "confluence001",
             ROOT / "experiments" / "006",
             FIELD_ROOT / "experiments" / "field008",
             FIELD_ROOT / "experiments" / "field006",
             COLLECTIVE_ROOT / "experiments" / "collective001",
             *(COLLECTIVE_ROOT / "experiments" / ("thought-" + str(n))
               for n in (23, 25, 26, 27, 28))]:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.append(path_str)

from confluence import Confluence, SyntheticOwner, WORLDS, digest, plan_for


def exact_source_git_checkout(path, expected):
    if not path.is_dir():
        raise RuntimeError("PINNED_SOURCE_NOT_CHECKED_OUT " + path.name)
    head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    if head != expected:
        raise RuntimeError("SOURCE_COMMIT_DRIFT " + path.name + ":" + head)
    return head


def source_pins():
    return dict(field008=exact_source_git_checkout(FIELD_ROOT, FIELD_SHA),
                collective001=exact_source_git_checkout(COLLECTIVE_ROOT, COLLECTIVE_SHA))


def native_modules():
    """No lookalike reimplementation. Imports fail without pinned checkouts."""
    source_pins()
    return dict(operators=import_module("composition"),
                blanch=import_module("grounding"),
                answer=import_module("answer_weave"),
                specimens=import_module("specimens"),
                memory=import_module("memory_benchmark"),
                weave=import_module("weave"))


class FieldOwnerView:
    """Explicit normalized-view adapter: no new source origin is invented."""
    def __init__(self, owner):
        self.owner = owner

    def normalize(self, receipt):
        if not self.owner.verify(receipt):
            raise ValueError("UNVERIFIED_CANONICAL_SOURCE")
        return {**deepcopy(receipt), "provenance_origin": receipt["origin"]}

    def verify(self, normalized):
        if normalized.get("provenance_origin") != normalized.get("origin"):
            return False
        base = {k: v for k, v in normalized.items() if k != "provenance_origin"}
        return self.owner.verify(base)


def native_lineage(confluence_report, owner, modules):
    """Replay real FIELD-008/006 AND/OR selective-retraction code."""
    if not confluence_report["proof_chain"]:
        raise ValueError("EMPTY_FIELD")
    ledger = modules["blanch"].BlanchLedger()
    adapter = FieldOwnerView(owner)
    observed = {}
    active = None
    trails = []
    source_i = 0
    proposal_i = 0
    for event in confluence_report["proof_chain"]:
        if event["kind"] == "INK_OBSERVATION":
            raw = event["payload"]
            normalized = adapter.normalize(raw)
            ledger.ink("ink_" + str(source_i), normalized, adapter)
            observed[raw["key"]] = raw["value"]
            if active is not None:
                probe = active["probe"]
                for hypothesis, predicted, pred_key in active["predictions"]:
                    verdict = ("OBSERVED_MATCH" if predicted == raw["value"]
                               else "REFUTED_LOCAL_PREDICTION")
                    ledger.resolve(pred_key, verdict)
                    descendant = "after_" + pred_key
                    ground = ledger.blanch(descendant, [[pred_key]])
                    trails.append(dict(hypothesis=hypothesis, probe=probe,
                                       prediction=predicted, observed=raw["value"],
                                       verdict=verdict,
                                       grounding=ground))
                active = None
            source_i += 1
        elif event["kind"] == "PENCIL_PROPOSAL":
            if active is not None:
                raise ValueError("UNANSWERED_PROPOSAL")
            prop = event["payload"]
            probe = prop["query"]
            if probe not in ("measure_panel", "inspect_mesh"):
                raise ValueError("NO_NATIVE_LINEAGE_ADAPTER")
            if not source_i:
                raise ValueError("NO_ISSUED_SOURCE_ROOT")
            key = "panel_span" if probe == "measure_panel" else "mesh_safe"
            predictions = []
            for ident in prop["alternatives"]:
                kv = dict(part.split("=", 1) for part in ident.split(";"))
                if set(kv) != {"span", "mesh_safe"}:
                    raise ValueError("UNRECOGNIZED_CONDITIONAL_WORLD")
                predicted = int(kv["span"]) if key == "panel_span" else bool(int(kv["mesh_safe"]))
                h_key = "blanch_" + str(proposal_i) + "_" + ident
                p_key = "prediction_" + str(proposal_i) + "_" + ident
                grounded = ledger.blanch(h_key, [["ink_0"]])
                if grounded["state"] != "PENCIL_CONDITIONAL":
                    raise RuntimeError("PENCIL_ATTESTATION_FAILED")
                ledger.claim(p_key, [[h_key]], claim_kind="LOCAL_PREDICTION")
                predictions.append((ident, predicted, p_key))
            active = dict(probe=probe, predictions=predictions)
            proposal_i += 1
    if active is not None:
        raise ValueError("UNFINISHED_EVIDENCE_REQUEST")
    if any(x["grounding"]["independent_origin_count"] > 1 for x in trails):
        raise RuntimeError("SOURCE_COPY_INFLATION")
    if not ledger.nodes or any(x["grounding"]["state"] == "INK" for x in trails):
        raise RuntimeError("HYPOTHESIS_UPGRADED_TO_INK")
    return dict(native="FIELD008.BlanchLedger + FIELD006.Lineage",
                source_git_sha=FIELD_SHA,
                source_observation_nodes=source_i,
                proposed_branch_predictions=len(trails),
                matched_predictions=sum(x["verdict"] == "OBSERVED_MATCH" for x in trails),
                refuted_predictions=sum(x["verdict"] == "REFUTED_LOCAL_PREDICTION" for x in trails),
                independent_source_origins=1,
                retractions=trails,
                status="SOURCE_OWNED_INK_SEPARATE_FROM_NATIVE_PENCIL")


def _verb(mod, name, required, adds):
    return mod.Verb(name, ("bike", "person"), frozenset(required),
                    frozenset(adds), frozenset(), 2)


def _synthetic_start(plan, idx):
    person, assembly = "builder_" + str(idx), "assembly_" + str(idx)
    world = frozenset({
        ("person", person), ("bike", assembly),
        ("permits", person, person, assembly),
        ("selected", assembly, plan), ("ready", assembly),
        ("covered", assembly, "0"),  # One pre-existing segment in this fixture
    })
    return world, (assembly, person)


def native_macro(plan, modules):
    """Actually synthesize a guarded composite with MOTIF-006 and replay it."""
    if plan not in ("PANEL_AND_CHAIR", "MESH_AND_CHAIR"):
        raise ValueError("NO_APPROVED_PLAN")
    m = modules["operators"]
    common = {("permits", "?1", "?1", "?0"), ("selected", "?0", plan)}
    prep = "brace_panel" if plan == "PANEL_AND_CHAIR" else "prepare_mesh"
    install = "place_panel" if plan == "PANEL_AND_CHAIR" else "place_mesh"
    catalog = {
        prep: _verb(m, prep, common | {("ready", "?0")}, {("prepared", "?0")}),
        install: _verb(m, install, common | {("prepared", "?0")}, {("covered", "?0", "1")}),
        "place_chair": _verb(m, "place_chair",
                             common | {("covered", "?0", "1")}, {("covered", "?0", "2")})
    }
    traces = []
    for i in (0, 1):
        start, roles = _synthetic_start(plan, i)
        calls = tuple(m.Call(name, roles) for name in (prep, install, "place_chair"))
        result = m.replay(start, calls, catalog)
        traces.append(m.Trace(start, calls, result))
    macros = m.induce_macros(traces, catalog, min_support=2)
    if len(macros) != 1:
        raise RuntimeError("AMBIGUOUS_NATIVE_MACRO")
    candidate = next(iter(macros.values()))
    start, roles = _synthetic_start(plan, 2)
    admitted = dict(catalog)
    admitted[candidate.id] = candidate
    actual = m.checked_apply(start, candidate.id, roles, admitted)
    primitive = m.replay(start,
                         tuple(m.Call(name, roles) for name in (prep, install, "place_chair")),
                         catalog)
    if actual != primitive:
        raise RuntimeError("MACRO_PRIMITIVE_MISMATCH")
    # Typed graph-to-set interpretation is authored, not semantically inferred.
    covered = sum((1 << int(fact[2])) for fact in actual
                  if len(fact) == 3 and fact[0] == "covered" and fact[1] == roles[0])
    if covered != 7:
        raise RuntimeError("SYNTHETIC_GOAL_NOT_REACHED")
    try:
        no_permission = frozenset(f for f in start if f[0] != "permits")
        m.checked_apply(no_permission, candidate.id, roles, admitted)
    except m.Inapplicable:
        blocked = True
    else:
        blocked = False
    if not blocked:
        raise RuntimeError("NATIVE_GUARDS_BYPASSED")
    return dict(native="MOTIF006.induce_macros+checked_apply",
                source="CANONICAL_EXPERIMENTS_006",
                macro_id=candidate.id,
                macro_semantics_sha256=m.signature(candidate),
                demonstrations=candidate.demonstrations,
                expanded_primitive_steps=candidate.depth,
                recorded_coverage_mask=covered,
                primitive_replay_agrees=True,
                missing_permission_rejected=blocked,
                typed_bridge="AUTHOR_DEFINED_ASSEMBLY_AS_BIKE_PLACEHOLDER_NO_PHYSICAL_SEMANTICS",
                authority="SYNTHETIC_ONLY")


def native_proof(coverage_mask, modules, *, corrupted_packet=False):
    """Real COLLECTIVE-001 re-entry; exact 3-bit toggle task only."""
    task = modules["specimens"].BY_KEY["cancel_or_add"]
    store = modules["memory"].seeds()
    inquiry = modules["weave"].investigate(task, store, mode="compose")
    fields = tuple(name for name, _ in task.fields)
    masks = {fields[0]: 1, fields[1]: 6}  # 001 XOR 110 == 111
    node = modules["answer"].first_answer(task, store, inquiry, masks)
    from_copy = json.loads(json.dumps(node, sort_keys=True))
    if corrupted_packet:
        from_copy["answer"]["output_mask"] ^= 1
        # Rehashed output is still invalid against the owner oracle.
        from_copy["integrity_digest"] = modules["weave"].digest({
            k: v for k, v in from_copy.items() if k != "integrity_digest"
        })
    checked = modules["answer"].reenter(from_copy, store.registry)
    if checked["answer_node"]["answer"]["output_mask"] != coverage_mask:
        raise RuntimeError("COVERAGE_PROOF_BRIDGE_MISMATCH")
    if checked["answer_node"]["answer"]["owner_oracle_output_mask"] != coverage_mask:
        raise RuntimeError("SOURCE_OWNED_PROOF_MISMATCH")
    return dict(native="COLLECTIVE001.first_answer+reenter",
                source_git_sha=COLLECTIVE_SHA,
                exact_task_key=task.key,
                task_spec_sha256=node["task_spec_sha256"],
                proof_digest=node["answer"]["proof_digest"],
                proof_packet_integrity=node["integrity_digest"],
                verified_coverage_mask=coverage_mask,
                owner_truth_table_cases=node["answer"]["finite_oracle_cases_verified"],
                independent_template_cases=node["answer"]["independent_template_cases_verified"],
                initial_development_queries=inquiry["development_queries"],
                reentry_new_development_queries=checked["new_development_queries"],
                reentry_runs_full_verification=checked["full_owner_proof_recheck_still_required"],
                independent_worldly_witness=False,
                typed_bridge="EXPLICIT_3_BIT_MASK_MAPPING_NOT_AUTOMATIC_SEMANTIC_INFERENCE",
                authority="NONE", installed=False,
                full_proof_node=checked["answer_node"])


def coherent_trial(owner, *, budget=2, include_full_proof=False):
    modules = native_modules()
    control = Confluence(owner)
    base = control.run(budget)
    field = native_lineage(base, owner, modules)
    if base["status"] != "PLAN_SIMULATED":
        return dict(schema="motif.confluence002.v1",
                    status="HOLD", base=base, field=field,
                    macro=None, proof=None, authority="NONE",
                    source_pins=source_pins())
    if not base["proof_chain"][-1]["payload"]["motif003"]["goal_reached"]:
        raise RuntimeError("MOTIF003_GOAL_DISAGREEMENT")
    macro = native_macro(base["plan"], modules)
    proof = native_proof(macro["recorded_coverage_mask"], modules)
    if not include_full_proof:
        proof.pop("full_proof_node")
    result = dict(schema="motif.confluence002.v1",
                  status="REVIEW_ONLY_SYNTHETIC_PROOF",
                  base=base, field=field, macro=macro, proof=proof,
                  source_pins=source_pins(), authority="NONE",
                  no_physical_actions=True, model_calls=0,
                  value_proposition="NATIVE_METHOD_COMPOSITION_NOT_CLASSICAL_SUPERIORITY")
    result["packet_sha256"] = digest(result)
    return result
