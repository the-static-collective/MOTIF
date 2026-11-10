"""COLLECTIVE-003: Native National Treasure Question Box -> MOTIF proof-carrying frontier.

Runs the ORIGINAL National Treasure Question Box engine, version pinned by
Git commit and blob, on ORIGINAL National Treasure case texts pinned to a
different commit. The case notes are research documents, *not historical
primary sources*. Questions are not answers.

No models, remote web research, private data, unreviewed external action,
true independent agents, or live physical evidence.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
from pathlib import Path

NT_CASES_COMMIT = "a6f1533537f88e837ba1560731d23645676a5b52"
NT_BOX_COMMIT = "28fbf9b10d003f7c577143550d17cc17f8109cb1"
NT_ENGINE_BLOB = "83574ed0a927fdefe1a53b3ece0960f011b875d0"
SCHEMA = "motif.collective003.national-treasure-question-node.v1"
PACKET_SCHEMA = "motif.collective003.question-frontier-packet.v1"

# This is a declared, reviewable selection of original source texts. Anchors
# must occur exactly in the pinned original bytes. No generated histories.
CASES = (
    {
        "id": "same-state-different-world",
        "path": "cases/same-state-different-world/README.md",
        "blob": "9ea4beb2ccbcd52a8909cee4cb105e4e45f0f500",
        "anchor": "When the same observed state is compatible with multiple underlying worlds",
        "clue": "Two possible worlds have the same observed state. What minimal lawful measurement separates them?",
        "claim": "An observation need not identify a unique world.",
        "provenance_class": "inference", "support_confidence": "possible",
        "source_locator": "Research case text, not an external-world primary source.",
        "chronology": "", "counterevidence": "", "falsifier": "",
        "competing_explanations": [],
        "source_families": [],
        "source_object_missing_in_reality": False,
    },
    {
        "id": "cicada-overfit",
        "path": "cases/cicada-overfit/README.md",
        "blob": "dd32be7bd9311733c4dd5eac29e76129a212ce0a",
        "anchor": "mixed descent versus independent recurrence",
        "clue": "Two symbols are uncannily alike: shared ancestor, copied transmission, or independent recurrence?",
        "claim": "Visual resemblance alone is insufficient evidence of common ancestry.",
        "provenance_class": "inference", "support_confidence": "possible",
        "source_locator": "Synthetic National Treasure case corpus; not documented Cicada history.",
        "chronology": "", "counterevidence": "", "falsifier": "",
        "competing_explanations": ["direct copying", "independent recurrence"],
        "source_families": [],
        "source_object_missing_in_reality": False,
    },
    {
        "id": "time-artifact-that-wasnt-there",
        "path": "cases/time-artifact-that-wasnt-there/README.md",
        "blob": "22afa9c54b5d72b71e6dd28d2f30481f3be9f4da",
        "anchor": "No artifact had actually been named.",
        "clue": "A mysterious museum artifact with anomalous clocks and a nineteenth-century history.",
        "claim": "The generated anomalous museum object was a real, documented artifact.",
        "provenance_class": "failed", "support_confidence": "unsupported",
        # Research note exists; alleged external artifact source does not.
        "source_locator": "", "chronology": "", "counterevidence": "",
        "falsifier": "", "competing_explanations": [],
        "source_families": [], "source_object_missing_in_reality": True,
    },
    {
        "id": "numatherology",
        "path": "threads/numatherology.md",
        "blob": "af334733d92a1d89a554753789315ca778146f91",
        "anchor": "In which mathematical worlds does moving from 4 to 5 force a change of grammar",
        "clue": "Why do 3, 4, and 5 repeatedly feel like thresholds across unrelated mathematical worlds?",
        "claim": "A shared numeric pattern does not establish a single shared mechanism.",
        "provenance_class": "speculation", "support_confidence": "possible",
        "source_locator": "National Treasure open number-grammar research note.",
        "chronology": "", "counterevidence": "", "falsifier": "",
        "competing_explanations": [],
        "source_families": [], "source_object_missing_in_reality": False,
    },
    {
        "id": "particular-treasure",
        "path": "cases/particular-treasure/README.md",
        "blob": "20e33beae6fb4d351d176a828424f61c79729851",
        "anchor": "RETROJECTION IS NOT ANCESTRY.",
        "clue": "Can a later decoder make an earlier conversation reveal structure without rewriting its formation history?",
        "claim": "Later interpretation does not prove earlier knowledge.",
        "provenance_class": "inference", "support_confidence": "possible",
        "source_locator": "Project-local chronological formation note; not a general scientific result.",
        "chronology": "Conversation formation documented for 2026-08-29 and 2026-08-30.",
        "counterevidence": "", "falsifier": "",
        "competing_explanations": [],
        "source_families": [], "source_object_missing_in_reality": False,
    },
    {
        "id": "strange-nature-of-time",
        "path": "cases/strange-nature-of-time/README.md",
        "blob": "ac6326e36c7f1bc30562bc5025b6e66f0b35dc25",
        "anchor": "What is time, and why does our best physics repeatedly make it stranger",
        "clue": "If relativity rejects one universal NOW, are time machines physically real?",
        "claim": "Mathematical time-travel solutions prove macroscopic time machines exist.",
        "provenance_class": "speculation", "support_confidence": "unsupported",
        "source_locator": "National Treasure research frontier, not experimental time-machine evidence.",
        "chronology": "", "counterevidence": (
            "Case note separates mathematical permission from realized physical evidence."
        ), "falsifier": "", "competing_explanations": [],
        "source_families": [], "source_object_missing_in_reality": False,
    },
)
SPEC_BY_ID = {case["id"]: case for case in CASES}
APERTURE_ACTION = {
    "source-object": "RECOVER_ORIGINAL_SOURCE_BEFORE_EXPLANATION",
    "chronology": "ESTABLISH_EARLIEST_ATTESTED_SEQUENCE",
    "counterevidence": "INVESTIGATE_ORDINARY_ALTERNATIVE",
    "falsifier": "SPECIFY_DISCONFIRMING_OBSERVATION",
    "rival-models": "FORM_COMPETING_TESTABLE_MODELS",
    "independent-convergence": "AUDIT_SOURCE_ANCESTRY_AND_DEPENDENCE",
    "discriminator": "FIND_MINIMUM_SEPARATING_TEST",
    "relation": "SEPARATE_OBSERVED_RELATION_FROM_PROJECTED_PATTERN",
}


class HOLD(ValueError):
    pass


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(data):
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def command(*args, cwd=None, input_data=None):
    result = subprocess.run(args, input=input_data, text=True, capture_output=True,
                            cwd=cwd, check=False, timeout=30)
    if result.returncode != 0:
        raise HOLD("Source-native command failed: " + (result.stderr[:450] or str(args)))
    return result.stdout.strip()


def source_checkout(root, expected):
    root = Path(root).resolve()
    if command("git", "rev-parse", "HEAD", cwd=root) != expected:
        raise HOLD("Source revision changed or wrong checkout")
    return root


def proof_of_source(root, relative, expected_blob, anchor):
    target = root / relative
    if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(root):
        raise HOLD("Original source path not available within pinned checkout")
    if command("git", "hash-object", relative, cwd=root) != expected_blob:
        raise HOLD("Source bytes changed from pinned Git blob")
    raw = target.read_bytes()
    body = raw.decode("utf8")
    offset = body.find(anchor)
    if offset < 0:
        raise HOLD("Original source anchor lost: " + relative)
    return {
        "repository": "the-static-collective/national-treasure",
        "commit": NT_CASES_COMMIT,
        "path": relative, "git_blob": expected_blob,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "exact_source_excerpt": anchor,
        "excerpt_location": offset,
        "locator": "https://github.com/the-static-collective/national-treasure/blob/"
                   + NT_CASES_COMMIT + "/" + relative,
        "source_kind": "PROJECT_OWNED_RESEARCH_OR_SYNTHETIC_CASE",
        "historical_primary_source_authenticated": False,
    }


def native_question_box(box_root, record):
    root = source_checkout(box_root, NT_BOX_COMMIT)
    proof_of_source(root, "tools/question-box/engine.mjs",
                    NT_ENGINE_BLOB, "export function buildQuestionFrontier")
    js = (
        'import fs from "node:fs";\n'
        'import { buildQuestionFrontier } from "./tools/question-box/engine.mjs";\n'
        'const input = JSON.parse(fs.readFileSync(0, "utf8"));\n'
        'process.stdout.write(JSON.stringify(buildQuestionFrontier(input)));\n'
    )
    try:
        receipt = json.loads(command("node", "--input-type=module", "--eval", js,
                                     cwd=root, input_data=canonical(record)))
    except json.JSONDecodeError as exc:
        raise HOLD("Native question tool returned no valid JSON") from exc
    return receipt


def native_record(case):
    # Source locator is a claim-specific source, not proof that the case README
    # itself establishes an alleged artifact or historical transmission.
    record = {key: case[key] for key in (
        "clue", "claim", "provenance_class", "support_confidence",
        "source_locator", "source_families", "chronology",
        "counterevidence", "falsifier", "competing_explanations"
    )}
    if record["source_locator"] and not case["source_object_missing_in_reality"]:
        # This URL recovers the *research question's* source note only.
        # It cannot license the historical/physical claim as witnessed.
        record["source_locator"] = (
            "https://github.com/the-static-collective/national-treasure/blob/"
            + NT_CASES_COMMIT + "/" + case["path"]
        )
    return record


def build_node(case_id, case_root, box_root):
    case = SPEC_BY_ID.get(case_id)
    if case is None:
        raise HOLD("Unknown source-owned National Treasure case")
    case_root = source_checkout(case_root, NT_CASES_COMMIT)
    source = proof_of_source(case_root, case["path"], case["blob"], case["anchor"])
    record = native_record(case)
    receipt = native_question_box(box_root, record)
    expected_keys = {"schema", "kind", "input", "evidence",
                     "aperture", "question", "other_doors", "non_claims"}
    if (type(receipt) is not dict or set(receipt) != expected_keys
            or receipt["schema"] != "national-treasure.question-receipt/v0"
            or receipt["kind"] != "question_frontier"
            or any(x in receipt for x in ("answer", "conclusion"))
            or receipt["input"] != {"clue": record["clue"], "claim": record["claim"]}
            or receipt["evidence"]["provenance_class"] != record["provenance_class"]
            or receipt["evidence"]["support_confidence"] != record["support_confidence"]
            or receipt["evidence"]["source_locator"] != record["source_locator"]
            or receipt["question"].strip() == ""):
        raise HOLD("Original native question contract was unexpectedly promoted")
    aperture = receipt["aperture"]["id"]
    if aperture not in APERTURE_ACTION:
        raise HOLD("Unknown native question aperture")
    if case["source_object_missing_in_reality"] and aperture != "source-object":
        raise HOLD("Synthetic artifact was promoted as a recovered object")
    # Distinguish mathematical inquiry from generic historical chronology.
    # This critic is a human-authored typed policy, NOT an LLM or learned
    # semantic judge. Crucially it NEVER modifies the original NT receipt.
    if case["id"] == "same-state-different-world" and aperture == "chronology":
        critic = {
            "status": "HOLD_NATIVE_CHRONOLOGY_NOT_SUFFICIENT_FOR_FORMAL_TASK",
            "reason": "Chronology cannot distinguish two mathematical objects "
                      "that have the same declared coarse observation.",
            "suggested_next_question": "What minimum-cost extra observable "
                                       "separates the constructed possible worlds?",
            "suggestion_origin": "ENGINEER_AUTHORED_TYPED_FORMAL_TASK_POLICY",
            "native_question_unchanged": True,
        }
    elif case["id"] == "numatherology" and aperture == "chronology":
        critic = {
            "status": "HOLD_MISSING_FORMAL_NUMBER_GRAMMAR_MODEL",
            "reason": "A historical date does not establish a general numeric "
                      "threshold law without a defined mathematical system.",
            "suggested_next_question": "Which mathematical objects, invariant "
                                       "and counterexample test make 4-to-5 "
                                       "a falsifiable transition?",
            "suggestion_origin": "ENGINEER_AUTHORED_TYPED_FORMAL_TASK_POLICY",
            "native_question_unchanged": True,
        }
    else:
        critic = {
            "status": "NATIVE_APERTURE_PRESERVED",
            "reason": "No bounded source-owned alternative independently tested.",
            "suggested_next_question": receipt["question"],
            "suggestion_origin": "ORIGINAL_NATIONAL_TREASURE_QUESTION_BOX",
            "native_question_unchanged": True,
        }
    node = {
        "schema": SCHEMA, "case_id": case["id"],
        "source_witness": source,
        "question_box_source": {"commit": NT_BOX_COMMIT,
                                "engine_git_blob": NT_ENGINE_BLOB},
        "original_question_receipt": receipt,
        "motif_recommended_action": APERTURE_ACTION[aperture],
        "motif_task_relevance_critic": critic,
        "action_authorized_or_executed": False,
        "world_claim_verified": False,
        "knowledge_status": "SOURCE_TEXT_VERIFIED_QUESTION_UNRESOLVED",
        "source_document_is_not_historical_proof": True,
        "source_object_missing_in_reality": case["source_object_missing_in_reality"],
        "unresolved": [
            "External original sources not independently recovered or authenticated",
            "No natural-language truth verification or independent human testimony",
            "No historical or metaphysical conclusion inferred from resemblance",
        ],
    }
    node["integrity_digest"] = digest(node)
    return node


def verify_node(node, case_root, box_root):
    if type(node) is not dict or node.get("schema") != SCHEMA:
        raise HOLD("Wrong question node schema")
    if node.get("integrity_digest") != digest({
        k: v for k, v in node.items() if k != "integrity_digest"
    }):
        raise HOLD("Question node integrity damaged")
    actual = build_node(node["case_id"], case_root, box_root)
    if node != actual:
        raise HOLD("Rehashed question or witness does not reproduce")
    return True


def graph_identifiability_certificate(source_node):
    """Exact three-world graph construction inspired by SAME STATE case.

    Search the minimum cost subset of *author-provided* feature operators.
    Graph data and tests are newly authored toy examples, not supplied by NT.
    """
    if source_node["case_id"] != "same-state-different-world":
        raise HOLD("Finite graph experiment attached to unrelated case")
    worlds = {
        "path4": {(0, 1), (1, 2), (2, 3)},
        "star4": {(0, 1), (0, 2), (0, 3)},
        "triangle_plus_isolated": {(0, 1), (0, 2), (1, 2)},
    }
    def degrees(edges):
        return tuple(sum(v in edge for edge in edges) for v in range(4))
    def components(edges):
        # Union-find, separate from the degree calculation.
        p = list(range(4))
        def root(x):
            while p[x] != x:
                x = p[x]
            return x
        for a, b in edges:
            ra, rb = root(a), root(b)
            p[ra] = rb
        return len({root(i) for i in range(4)})
    def triangles(edges):
        return sum(
            {(a, b), (a, c), (b, c)} <= edges
            for a, b, c in itertools.combinations(range(4), 3)
        )
    operators = {
        "max_degree": (1, lambda edges: max(degrees(edges))),
        "component_count": (1, components),
        "triangle_count": (2, triangles),
        "degree_multiset": (3, lambda edges: sorted(degrees(edges))),
    }
    primary = {name: {"vertices": 4, "edges": len(edges)}
               for name, edges in worlds.items()}
    if len({canonical(v) for v in primary.values()}) != 1:
        raise HOLD("Declared observation should not distinguish worlds")
    matrix = {
        op: {world: fn(edges) for world, edges in worlds.items()}
        for op, (_, fn) in operators.items()
    }
    choices = []
    for count in range(1, len(operators) + 1):
        for names in itertools.combinations(sorted(operators), count):
            codes = [canonical([matrix[op][world] for op in names])
                     for world in worlds]
            if len(set(codes)) == len(worlds):
                cost = sum(operators[op][0] for op in names)
                choices.append((cost, len(names), names))
    if not choices:
        raise HOLD("No allowed operator distinguishes these possible worlds")
    selected = min(choices)
    best = list(selected[2])
    # The compact checker is independent of code-generated labels: recompute
    # the values from the original graphs with a second direct loop formulation.
    independent = {}
    for name, edges in worlds.items():
        adjacency = [[False] * 4 for _ in range(4)]
        for a, b in edges:
            adjacency[a][b] = adjacency[b][a] = True
        direct_degree = [sum(row) for row in adjacency]
        seen = set()
        cnt = 0
        for start in range(4):
            if start in seen:
                continue
            cnt += 1
            pending = [start]
            while pending:
                v = pending.pop()
                if v in seen:
                    continue
                seen.add(v)
                pending.extend(i for i in range(4) if adjacency[v][i] and i not in seen)
        independent[name] = {
            "max_degree": max(direct_degree),
            "component_count": cnt,
            "triangle_count": sum(
                adjacency[a][b] and adjacency[a][c] and adjacency[b][c]
                for a, b, c in itertools.combinations(range(4), 3)
            ),
            "degree_multiset": sorted(direct_degree),
        }
    if any(matrix[op][world] != independent[world][op]
           for op in operators for world in worlds):
        raise HOLD("Independent mathematical enumerator disagrees")
    if any(cost < selected[0] for cost, _, _ in choices):
        raise HOLD("Minimum-cost certificate contradicted")
    card = {
        "schema": "motif.collective003.finite-discriminator-proof.v1",
        "source_question_node_digest": source_node["integrity_digest"],
        "research_question": "Which least-cost allowed measurements distinguish "
                             "three different worlds with four vertices and three edges?",
        "inherited_observation": primary,
        "candidate_feature_values": matrix,
        "feature_query_costs": {op: cost for op, (cost, _) in operators.items()},
        "selected_question_operations": best,
        "selected_total_cost": selected[0],
        "alternative_operators_evaluated": len(operators),
        "all_subsets_exhausted": 2 ** len(operators) - 1,
        "independent_direct_adjacency_check": True,
        "result": "THREE_SYNTHETIC_WORLDS_SEPARATED_BY_TWO_MEASUREMENTS",
        "explanation": "The original coarse observation (n=4,m=3) identifies "
                       "only an equivalence class, not the hidden graph.",
        "synthetic_only": True,
        "new_general_mathematics_discovered": False,
        "claim_about_original_NT_history": False,
        "tool_grammar_human_authored": True,
    }
    card["integrity_digest"] = digest(card)
    return card


FIXTURE_PINS = {
    "co-013": "46980e4d6f19c2fb82d0d4a904f8c187b5db5ad2",
    "co-014": "30405aaf32edb1ba791adc588903a0d06c44bbf8",
}


def cicada_contrast_certificate(source_node, case_root):
    """Recover exact author-fixture labels, not inferred Cicada history."""
    if source_node["case_id"] != "cicada-overfit":
        raise HOLD("Cicada specimen attached to unrelated question")
    root = source_checkout(case_root, NT_CASES_COMMIT)
    pairs = {}
    for fid, blob in FIXTURE_PINS.items():
        path = f"cases/cicada-overfit/fixtures/{fid}.json"
        witness = proof_of_source(root, path, blob, f'"id": "{fid}"')
        body = json.loads((root / path).read_text("utf8"))
        # Fixture labels are evaluator-owned. Do NOT expose them as independent
        # fact about actual Cicada authorship.
        pairs[fid] = {
            "source": witness, "fixture_id": body["id"],
            "fixture_family": body["family"],
            "author_declared_edges": [
                {"from": e["from"], "to": e["to"],
                 "fixture_expected": e["expectedRelation"]}
                for e in body["edges"]
            ],
            "historical_authority": False,
        }
    a = [e["fixture_expected"] for e in pairs["co-013"]["author_declared_edges"]]
    b = [e["fixture_expected"] for e in pairs["co-014"]["author_declared_edges"]]
    if (a != ["DEMONSTRATED_ANCESTRY", "DEMONSTRATED_ANCESTRY"]
            or b != ["CONTEXTUAL_ASSOCIATION", "CONTEXTUAL_ASSOCIATION",
                     "FORMAL_RESEMBLANCE", "REFUSED_ANCESTRY"]):
        raise HOLD("Changed author-declared matched family")
    return {
        "schema": "motif.collective003.cicada-refusal-pair.v1",
        "source_question_node_digest": source_node["integrity_digest"],
        "source_fixture_pair": pairs,
        "proves_only": "SYNTHETIC_RELATION_GRAMMAR_CAN_RETAIN_BOTH_SUPPORTED_"
                       "ANCESTRY_AND_REFUSED_ANCESTRY_WITHOUT_COLLAPSE",
        "no_actual_cicada_authorship_conclusion": True,
        "no_external_source_identity_authenticated": True,
    }


def run(case_root, box_root):
    ids = [case["id"] for case in CASES]
    nodes = [build_node(cid, case_root, box_root) for cid in ids]
    for node in nodes:
        verify_node(node, case_root, box_root)
    by_id = {node["case_id"]: node for node in nodes}
    result = {
        "schema": PACKET_SCHEMA,
        "source_repo_commit": NT_CASES_COMMIT,
        "native_question_box_commit": NT_BOX_COMMIT,
        "native_question_box_engine_blob": NT_ENGINE_BLOB,
        "question_nodes": nodes,
        "finite_graph_probe": graph_identifiability_certificate(
            by_id["same-state-different-world"]),
        "matched_cicada_synthetic_fixture": cicada_contrast_certificate(
            by_id["cicada-overfit"], case_root),
        "native_question_count": len(nodes),
        "new_external_research_queries": 0,
        "new_model_calls": 0,
        "original_case_source_claims_are_not_verified_world_facts": True,
        "status": "RESEARCH_HOLD_NATIONAL_TREASURE_APERTURES_NOT_HISTORY_PROOFS",
        "automatic_admission": False,
        "installed": False,
        "external_authority": "NONE",
    }
    result["integrity_digest"] = digest(result)
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-root", required=True)
    parser.add_argument("--box-root", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.case_root, args.box_root), indent=2,
                     ensure_ascii=False, sort_keys=True))
