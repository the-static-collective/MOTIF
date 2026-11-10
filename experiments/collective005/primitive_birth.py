"""COLLECTIVE-005 — primitive birth from raw graph observations.

This is a *bounded* scientific trial: the previous question vocabularies are
proven insufficient on a previously authored, independent-origin Atlas pair.
The new system is NOT handed an operator named "count simple four-edge paths".
It can assemble longer queries from generic vertex-binding, adjacency,
injectivity, and counting primitives, testing lengths in increasing order.

The atomic primitives, program grammar, maximum depth, world hypotheses and
source-owner callback are engineer supplied. No general algorithm invention,
unrestricted grammar growth, or externally autonomous world access is claimed.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import permutations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "collective004"))

from question_inventor import HOLD, canonical, digest, old_measurements
from external_atlas import external_queries, native_nx_eval

SCHEMA = "motif.collective005.primitive-birth-proof.v1"
QUESTION_SCHEMA = "motif.collective005.raw-graph-question-program.v1"
OBS_SCHEMA = "motif.collective005.source-owned-measurement.v1"
GRAMMAR = {
    "base_atoms": ["BIND_VERTEX", "ADJACENT", "ALL_DISTINCT", "COUNT"],
    "initial_old_query_family": "COLLECTIVE004_DEGREE_PAIR_EXISTENTIAL",
    "growth_rule": "APPEND_ONE_BOUND_VERTEX_AND_ONE_ADJACENCY",
    "max_edges": 4,
    "maximum_graph_vertices": 7,
    "minimum_graph_vertices": 5,
    "unrestricted_primitive_invention": False,
}
OPEN = [
    "The original source is independently authored mathematical data, not a live external agent",
    "Model selection and generic primitive grammar are human supplied",
    "All hypothesis graphs and possible measurements are available to the planner",
    "The realized-world choice stays hidden only inside a local simulated source owner",
    "A synthesized program is not historically novel mathematics",
    "Git digests establish byte integrity, not external human identity or authority",
    "Only exact finite graphs and identical declared source scope are certified",
]


def _graph(value):
    if type(value) is not dict or set(value) != {"n", "edges"}:
        raise HOLD("Unexpected graph carrier shape")
    n = value["n"]
    if type(n) is not int or not 5 <= n <= 7:
        raise HOLD("Graph vertex count outside declared bound")
    if type(value["edges"]) is not list:
        raise HOLD("Graph edge list missing")
    edges = set()
    for entry in value["edges"]:
        if type(entry) is not list or len(entry) != 2:
            raise HOLD("Bad adjacency tuple")
        u, v = entry
        if (type(u) is not int or type(v) is not int or
                not 0 <= u < v < n):
            raise HOLD("Noncanonical edge or invalid vertex")
        edges.add((u, v))
    if len(edges) != len(value["edges"]):
        raise HOLD("Duplicate adjacency")
    normalized = {"n": n, "edges": [list(x) for x in sorted(edges)]}
    if normalized != value:
        raise HOLD("Graph ordering is not canonical")
    return n, edges


def emit_ast(edge_depth):
    """Grow a previously absent question type from four generic atoms."""
    if type(edge_depth) is not int or not 1 <= edge_depth <= GRAMMAR["max_edges"]:
        raise HOLD("Question grammar bound exceeded")
    symbols = [f"v{i}" for i in range(edge_depth + 1)]
    return {
        "schema": QUESTION_SCHEMA,
        "bind_vertices": symbols,
        "adjacency_constraints": [
            [symbols[i], symbols[i+1]] for i in range(edge_depth)
        ],
        "injective": True,
        "aggregate": "COUNT_UNDIRECTED_UNORDERED",
        "question_origin": "SYNTHESIZED_BY_REPEATED_BIND_AND_ADJACENCY",
    }


def _typecheck(program):
    if type(program) is not dict or set(program) != {
        "schema", "bind_vertices", "adjacency_constraints",
        "injective", "aggregate", "question_origin"
    }:
        raise HOLD("Unknown program structure")
    if program.get("schema") != QUESTION_SCHEMA:
        raise HOLD("Wrong question program version")
    path_len = len(program["adjacency_constraints"])
    if program != emit_ast(path_len):
        raise HOLD("Tampered primitive composition or unsafe binder")
    return path_len


def generate_python(program):
    """Emit literal executable nested loops, *not* a prewritten PATH4."""
    depth = _typecheck(program)
    lines = [
        "def composed_observation(n, edges):",
        "    adjacent = {tuple(sorted((u, v))) for u, v in edges}",
        "    count = 0",
    ]
    for i in range(depth + 1):
        lines.append("    " * (i+1) + f"for v{i} in range(n):")
    names = [f"v{i}" for i in range(depth + 1)]
    unique = "len({" + ", ".join(names) + "}) == " + str(depth+1)
    adjacent = " and ".join(
        f"tuple(sorted((v{i}, v{i+1}))) in adjacent"
        for i in range(depth)
    )
    lines.extend([
        "    " * (depth+2) + f"if {unique} and {adjacent}:",
        "    " * (depth+3) + "count += 1",
        "    return count // 2",
    ])
    return "\n".join(lines) + "\n"


def execute_generated(program, graph):
    """Run code generated from a finite fully checked AST, NOT a sandbox."""
    n, edges = _graph(graph)
    src = generate_python(program)
    namespace = {"__builtins__": {"range": range, "len": len,
                                  "set": set, "tuple": tuple, "sorted": sorted}}
    exec(compile(src, "<bounded-composed-graph-question>", "exec"), namespace)
    answer = namespace["composed_observation"](n, tuple(edges))
    if type(answer) is not int or answer < 0:
        raise HOLD("Generated mathematical observation malformed")
    return answer


def independent_permutation_count(program, graph):
    """Separate brute-force vertex assignment reference, no generated code."""
    depth = _typecheck(program)
    n, edges = _graph(graph)
    count = 0
    for seq in permutations(range(n), depth+1):
        if all((min(seq[i],seq[i+1]), max(seq[i],seq[i+1])) in edges
               for i in range(depth)):
            count += 1
    if count % 2:
        raise HOLD("Odd oriented path count invalid")
    return count // 2


def networkx_reference(program, graph):
    """Source-independent NetworkX all_simple_paths oracle."""
    import networkx as nx
    depth = _typecheck(program)
    n, edges = _graph(graph)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    count = 0
    for source in range(n):
        for target in range(n):
            if target == source:
                continue
            for p in nx.all_simple_paths(g, source, target, cutoff=depth):
                if len(p) - 1 == depth:
                    count += 1
    if count % 2:
        raise HOLD("Independent oracle returned odd oriented path count")
    return count // 2


def old_question_fingerprint(graph_pair):
    """Full old menu + COLLECTIVE004 allowed degree-pair *existence* probes."""
    a,b = graph_pair
    if _graph(a)[0] != _graph(b)[0]:
        raise HOLD("Candidate models disagree on universe size")
    old = [old_measurements(g) for g in graph_pair]
    queries = external_queries(graph_pair)
    signatures = [
        [native_nx_eval(q, g) for q in queries] for g in graph_pair
    ]
    return {
        "old_measurements": old,
        "degree_pair_question_count": len(queries),
        "degree_pair_existence_signatures": signatures,
        "previous_two_question_grammars_saturated": (
            old[0] == old[1] and signatures[0] == signatures[1]
        ),
    }


def invent_question(graph_pair, *, max_edges=None):
    """Iterative deepening from raw atoms. No handwritten winning depth."""
    if type(graph_pair) not in (tuple, list) or len(graph_pair) != 2:
        raise HOLD("Two hypothesized worlds are required")
    _graph(graph_pair[0]); _graph(graph_pair[1])
    old = old_question_fingerprint(graph_pair)
    if not old["previous_two_question_grammars_saturated"]:
        return {"status": "HOLD_OLD_QUESTION_LANGUAGE_ALREADY_SUFFICIENT",
                "old": old, "search_history": [],
                "new_query_witnessed": False}
    if max_edges is None:
        max_edges = GRAMMAR["max_edges"]
    if type(max_edges) is not int or not 0 <= max_edges <= GRAMMAR["max_edges"]:
        raise HOLD("Max search budget outside frozen grammar")

    search_history = []
    for depth in range(1,max_edges+1):
        candidate = emit_ast(depth)
        values = [
            execute_generated(candidate,g) for g in graph_pair
        ]
        independent = [
            independent_permutation_count(candidate,g) for g in graph_pair
        ]
        nx_answer = [
            networkx_reference(candidate,g) for g in graph_pair
        ]
        if values != independent or values != nx_answer:
            raise HOLD("Generated observation disagrees with independent oracles")
        item = {
            "depth":depth,
            "ast":candidate,
            "generated_python_sha256":sha256(generate_python(candidate).encode()).hexdigest(),
            "observations":values,
            "independent_oracles_agree": True,
            "separates":values[0]!=values[1],
        }
        search_history.append(item)
        if item["separates"]:
            return {
                "status":"COMPOSED_NEW_QUESTION_PRIMITIVE_REVIEW_ONLY",
                "old":old,
                "search_history":search_history,
                "selected_ast":candidate,
                "generated_python_source":generate_python(candidate),
                "selected_predictions":values,
                "new_query_witnessed":True,
                "question_generated_without_realized_world_selection":True,
                "closed_form_primitive_supplied_in_advance":False,
                "low_level_primitives_supplied_by_engineer":True,
            }
    return {
        "status":"HOLD_NO_SEPARATING_COMPOSITION_WITHIN_BUDGET",
        "old":old,"search_history":search_history,"new_query_witnessed":False,
    }


def classical_fair_reference(graph_pair):
    """Equal-primitives brute force depth-ordered classical synthesis baseline."""
    for depth in range(1,GRAMMAR["max_edges"]+1):
        query = emit_ast(depth)
        vals = [networkx_reference(query,g) for g in graph_pair]
        if vals[0] != vals[1]:
            return query
    return None


class SimulatedAtlasSourceOwner:
    def __init__(self, graph, pair_ids, *, revision=1):
        self._graph=deepcopy(graph)
        _graph(self._graph)
        if (type(pair_ids) not in (list,tuple) or len(pair_ids)!=2
            or any(type(v) is not int or v<0 for v in pair_ids)):
            raise HOLD("Only public exact Atlas identity pairs")
        if type(revision) is not int or revision < 1:
            raise HOLD("Bad fixture revision")
        self._pair_ids=list(pair_ids)
        self._revision=revision
        self.questions=0
        self.rechecks=0

    def contract(self):
        return {
            "kind":"SIMULATED_ATLAS_ORIGINAL_GRAPH_SOURCE",
            "pair_ids":self._pair_ids,
            "revision":self._revision,
            "realized_candidate_identity_omitted":True,
            "source_authenticated_as_human":False,
            "external_authority":"NONE",
        }

    def ask(self,program):
        _typecheck(program)
        self.questions+=1
        measurement = networkx_reference(program,self._graph)
        observation = {
            "schema":OBS_SCHEMA,
            "owner_contract":self.contract(),
            "question_program":deepcopy(program),
            "measured_count":measurement,
            "simulated_source_not_live_external_agent":True,
        }
        observation["integrity_digest"]=digest(observation)
        return observation

    def recheck(self,observation):
        self.rechecks+=1
        if (type(observation) is not dict or set(observation) != {
            "schema","owner_contract","question_program","measured_count",
            "simulated_source_not_live_external_agent","integrity_digest"
        } or observation["integrity_digest"]!=digest({
            k:v for k,v in observation.items() if k!="integrity_digest"
        })):
            raise HOLD("Broken source observation receipt")
        if (observation["schema"]!=OBS_SCHEMA
            or observation["owner_contract"]!=self.contract()
            or observation["simulated_source_not_live_external_agent"] is not True
            or type(observation["measured_count"]) is not int
            or observation["measured_count"]!=networkx_reference(
                observation["question_program"],self._graph)
            or observation["measured_count"]!=independent_permutation_count(
                observation["question_program"],self._graph)):
            raise HOLD("Receipt cannot be verified against current source")
        return True


def research_packet(source_nt_node, graph_pair, owner, *, source_atlas_proof,
                    max_edges=None):
    """Produce result with old failure, new executable question and source proof."""
    if (type(source_nt_node) is not dict
            or source_nt_node.get("case_id")!="same-state-different-world"
            or source_nt_node.get("world_claim_verified") is not False
            or source_nt_node.get("original_question_receipt",{}).get("schema") !=
               "national-treasure.question-receipt/v0"):
        raise HOLD("No original unpromoted National Treasure question")
    if not isinstance(owner,SimulatedAtlasSourceOwner):
        raise HOLD("Source is not an approved bounded fixture owner")
    if type(source_atlas_proof) is not dict or not (
            source_atlas_proof.get("source")=="Read/Wilson 1998 Graph Atlas"
            and source_atlas_proof.get("original_atlas_data_pinned") is True):
        raise HOLD("No declared independent-origin source proof")
    result=invent_question(graph_pair,max_edges=max_edges)
    if result["status"] != "COMPOSED_NEW_QUESTION_PRIMITIVE_REVIEW_ONLY":
        return {"status":result["status"],"reasoning_evidence":result,
                "source_questions_asked":0,"installed":False}
    ast = result["selected_ast"]
    before=owner.questions
    evidence=owner.ask(ast)
    owner.recheck(evidence)
    survivors=[
        i for i,v in enumerate(result["selected_predictions"])
        if v==evidence["measured_count"]
    ]
    if len(survivors)!=1:
        raise HOLD("No unique authorized finite hypothesis survives source check")
    packet={
        "schema":SCHEMA,
        "national_treasure_question_node":deepcopy(source_nt_node),
        "atlas_provenance":deepcopy(source_atlas_proof),
        "possible_worlds":deepcopy(list(graph_pair)),
        "old_language_failure":deepcopy(result["old"]),
        "growth_history":deepcopy(result["search_history"]),
        "new_program_ast":deepcopy(ast),
        "generated_python_source":result["generated_python_source"],
        "predicted_observations":list(result["selected_predictions"]),
        "new_question_reason":"COMPOSED_RAW_BIND_ADJACENCY_INJECTIVITY_COUNT_AFTER_OLD_HOLD",
        "source_owned_observation":evidence,
        "remaining_possible_world_indices":survivors,
        "source_questions_asked":owner.questions-before,
        "result":"SCOPED_SYNTHETIC_ATLAS_WORLD_IDENTIFIED",
        "public_domain_original_atlas_is_not_live_source":True,
        "program_grammar_engineer_authored":True,
        "original_national_treasure_history_unanswered":True,
        "open_questions":list(OPEN),
        "automatic_admission":False,
        "installed":False,
        "external_authority":"NONE",
    }
    packet["integrity_digest"]=digest(packet)
    return packet


def verify_packet(packet,source_nt_node,owner,*,source_atlas_proof):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown answer packet schema")
    required={
        "schema","national_treasure_question_node","atlas_provenance",
        "possible_worlds","old_language_failure","growth_history",
        "new_program_ast","generated_python_source","predicted_observations",
        "new_question_reason","source_owned_observation",
        "remaining_possible_world_indices","source_questions_asked","result",
        "public_domain_original_atlas_is_not_live_source",
        "program_grammar_engineer_authored",
        "original_national_treasure_history_unanswered","open_questions",
        "automatic_admission","installed","external_authority","integrity_digest",
    }
    if (set(packet)!=required or packet["integrity_digest"]!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    })):
        raise HOLD("Answer packet altered")
    if (packet["national_treasure_question_node"]!=source_nt_node
        or packet["atlas_provenance"]!=source_atlas_proof
        or packet["result"]!="SCOPED_SYNTHETIC_ATLAS_WORLD_IDENTIFIED"
        or packet["new_question_reason"]!="COMPOSED_RAW_BIND_ADJACENCY_INJECTIVITY_COUNT_AFTER_OLD_HOLD"
        or packet["source_questions_asked"]!=1
        or packet["public_domain_original_atlas_is_not_live_source"] is not True
        or packet["program_grammar_engineer_authored"] is not True
        or packet["original_national_treasure_history_unanswered"] is not True
        or packet["open_questions"]!=list(OPEN)
        or packet["automatic_admission"] is not False
        or packet["installed"] is not False
        or packet["external_authority"]!="NONE"):
        raise HOLD("Authority or question source scope changed")
    frozen=invent_question(packet["possible_worlds"])
    if frozen["status"]!="COMPOSED_NEW_QUESTION_PRIMITIVE_REVIEW_ONLY":
        raise HOLD("Old data insufficient to reconstruct result")
    if (packet["old_language_failure"]!=frozen["old"]
        or packet["growth_history"]!=frozen["search_history"]
        or packet["new_program_ast"]!=frozen["selected_ast"]
        or packet["generated_python_source"]!=frozen["generated_python_source"]
        or packet["predicted_observations"]!=frozen["selected_predictions"]):
        raise HOLD("Generated program or exploration history differs")
    owner.recheck(packet["source_owned_observation"])
    reply=packet["source_owned_observation"]
    if reply["question_program"]!=packet["new_program_ast"]:
        raise HOLD("Owner answered another question")
    survivors=[
        i for i,v in enumerate(frozen["selected_predictions"])
        if v==reply["measured_count"]
    ]
    if survivors!=packet["remaining_possible_world_indices"] or len(survivors)!=1:
        raise HOLD("Predicted world disagrees with source")
    return True


def reenter(packet,source_nt_node,owner,*,source_atlas_proof):
    before=owner.questions
    verify_packet(packet,source_nt_node,owner,
                  source_atlas_proof=source_atlas_proof)
    if before!=owner.questions:
        raise HOLD("Reentry issued new inquiry")
    return {
        "status":"SCOPED_SYNTHETIC_QUESTION_GRAMMAR_REVERIFIED",
        "new_discovery_questions":0,
        "source_reverification_performed":True,
        "answer_node":deepcopy(packet),
    }
