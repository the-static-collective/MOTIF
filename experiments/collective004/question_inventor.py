"""COLLECTIVE-004: Invent the *missing question type* from typed graph primitives.

This tests failure of a previously available measurement vocabulary, synthesizes
a previously unlisted executable predicate, asks a synthetic source owner, and
carries re-verifiable evidence forward. NO unrestricted mathematical discovery,
authenticated external source, real LLM inference, or real-world claims.

National Treasure's original 'Same State, Different World' question remains a
separately source-pinned, unanswered research question.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

SCHEMA = "motif.collective004.invented-question-proof.v1"
AST_SCHEMA = "motif.collective004.graph-question-ast.v1"
OBS_SCHEMA = "motif.collective004.synthetic-owner-evidence.v1"
SOURCE_NOTE = "same-state-different-world"
OLD = ("max_degree", "component_count", "triangle_count", "degree_multiset")
OPEN = (
    "Only developer-authored finite connected tree possibilities were used",
    "Question synthesis is bounded to a human-written typed primitive grammar",
    "The classical enumerator using the same primitive grammar is not surpassed",
    "A local synthetic owner is not an authenticated independent participant",
    "No historical, spiritual, scientific or physical-world claim is proven",
    "Digest integrity is not source authentication or authorization",
)


class HOLD(ValueError):
    pass


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def graph(n, edges):
    """Immutable simple, undirected, connected tree; only 6-7 vertices."""
    if type(n) is not int or n not in (6, 7):
        raise HOLD("Only defined six/seven-vertex synthetic graph experiments")
    if type(edges) not in (list, tuple, set):
        raise HOLD("Graph edge collection required")
    canonical_edges = set()
    for edge in edges:
        if type(edge) not in (tuple, list) or len(edge) != 2:
            raise HOLD("Malformed edge")
        a, b = edge
        if type(a) is not int or type(b) is not int or not 0 <= a < n or not 0 <= b < n or a == b:
            raise HOLD("Edge outside declared graph")
        canonical_edges.add(tuple(sorted((a, b))))
    if len(canonical_edges) != n - 1:
        raise HOLD("Expected a connected tree with n-1 edges")
    seen = {0}
    while True:
        next_seen = seen | {v for u, v in canonical_edges if u in seen} | {
            u for u, v in canonical_edges if v in seen
        }
        if next_seen == seen:
            break
        seen = next_seen
    if len(seen) != n:
        raise HOLD("Disconnected or cyclic candidate not allowed")
    return {"n": n, "edges": [list(e) for e in sorted(canonical_edges)]}


def base_worlds():
    # Both are nonisomorphic trees with the SAME four old measurements.
    # A: arms 2,2,1 from a degree-three hub.
    # B: arms 3,1,1 from a degree-three hub.
    return (
        graph(6, [(0,1),(0,2),(0,3),(1,4),(2,5)]),
        graph(6, [(0,1),(0,2),(0,3),(1,4),(4,5)]),
    )


def extended_worlds():
    a, b = base_worlds()
    return (graph(7, a["edges"] + [[0,6]]),
            graph(7, b["edges"] + [[0,6]]))


def degrees(g):
    d = [0] * g["n"]
    for a, b in g["edges"]:
        d[a] += 1
        d[b] += 1
    return tuple(d)


def old_measurements(g):
    """Reproduce exactly the old COLLECTIVE-003 feature menu."""
    d = degrees(g)
    edges = {tuple(edge) for edge in g["edges"]}
    seen = set()
    cc = 0
    for start in range(g["n"]):
        if start in seen:
            continue
        cc += 1
        pending = [start]
        while pending:
            u = pending.pop()
            if u in seen:
                continue
            seen.add(u)
            pending += [v if a == u else a for a,v in edges
                        if a == u or v == u]
    triangle = sum(
        {(u,v),(u,w),(v,w)} <= edges
        for u,v,w in combinations(range(g["n"]), 3)
    )
    return {
        "vertices": g["n"],
        "edges": len(edges),
        "max_degree": max(d),
        "component_count": cc,
        "triangle_count": triangle,
        "degree_multiset": sorted(d),
    }


def _typecheck(ast):
    if type(ast) is not dict or set(ast) != {"schema", "quantifier", "edge",
                                               "endpoints"}:
        raise HOLD("Wrong program grammar")
    if ast["schema"] != AST_SCHEMA or ast["quantifier"] != "EXISTS":
        raise HOLD("Only approved finite existential question")
    if ast["edge"] != ["u", "v"]:
        raise HOLD("Question must traverse an actual edge")
    clauses = ast["endpoints"]
    if type(clauses) is not list or len(clauses) != 2:
        raise HOLD("Two degree constraints required for new graph predicate")
    if any(type(x) is not dict or set(x) != {"vertex", "degree_equals"}
           or type(x["degree_equals"]) is not int
           or x["degree_equals"] not in range(1, 7)
           for x in clauses):
        raise HOLD("Invalid primitive degree predicate")
    if [x["vertex"] for x in clauses] != ["u", "v"]:
        raise HOLD("Unknown binder in synthesized program")
    if clauses[0]["degree_equals"] > clauses[1]["degree_equals"]:
        raise HOLD("Noncanonical orientation")
    return tuple(x["degree_equals"] for x in clauses)


def emit_program(k, j):
    """A NEW typed AST emitted by Cartesian composition of *generic primitives*.

    No particular DEGREE2_EDGE method is prewritten in the old operator menu.
    Both degree constants are discovered from the candidate graph inventory.
    """
    if type(k) is not int or type(j) is not int or not 1 <= k <= j <= 6:
        raise HOLD("Invalid generated degree constants")
    ast = {"schema": AST_SCHEMA, "quantifier": "EXISTS",
           "edge": ["u", "v"],
           "endpoints": [{"vertex": "u", "degree_equals": k},
                         {"vertex": "v", "degree_equals": j}]}
    _typecheck(ast)
    return ast


def execute(ast, g):
    """Generic interpreter of synthesized AST; no case-specific question."""
    k, j = _typecheck(ast)
    d = degrees(g)
    for u, v in g["edges"]:
        if (d[u] == k and d[v] == j) or (d[u] == j and d[v] == k):
            return True
    return False


def independent_execute(ast, g):
    """Separately implemented adjacency-matrix oracle for AST semantics."""
    k, j = _typecheck(ast)
    n = g["n"]
    adj = [[0] * n for _ in range(n)]
    for u, v in g["edges"]:
        adj[u][v] = adj[v][u] = 1
    deg = [sum(row) for row in adj]
    return any(
        adj[u][v] and (
            (deg[u] == k and deg[v] == j)
            or (deg[u] == j and deg[v] == k)
        )
        for u in range(n) for v in range(u+1,n)
    )


def candidate_programs(worlds, *, enable_extension=True):
    """Enumerate new typed questions WITHOUT consulting hidden realized world."""
    if type(worlds) not in (list, tuple) or len(worlds) != 2:
        raise HOLD("Two possible worlds required")
    a, b = worlds
    if a["n"] != b["n"]:
        raise HOLD("Possibilities must share the same declared universe")
    # Check graph syntax rather than trusting serialized source-owner objects.
    if graph(a["n"], a["edges"]) != a or graph(b["n"], b["edges"]) != b:
        raise HOLD("Noncanonical or altered graph")
    if not enable_extension:
        return []
    observable_degrees = sorted(set(degrees(a)) | set(degrees(b)))
    return [emit_program(k, j) for k, j in combinations(observable_degrees, 2)] + [
        emit_program(k, k) for k in observable_degrees
    ]


def find_missing_question(worlds, *, enable_extension=True):
    """Find old-language incompleteness, then synthesize a new discriminator."""
    a, b = worlds
    first, second = old_measurements(a), old_measurements(b)
    if first != second:
        return {"status": "HOLD_OLD_GRAMMAR_ALREADY_DISTINGUISHES",
                "old_measurements": [first,second],
                "generated_candidates": 0}
    candidates = candidate_programs(worlds, enable_extension=enable_extension)
    catalog = []
    for ast in candidates:
        signatures = [execute(ast,a), execute(ast,b)]
        if any(signatures[i] != independent_execute(ast,worlds[i]) for i in (0,1)):
            raise HOLD("Program interpreter disagrees with independent oracle")
        catalog.append({"ast": ast, "signature": signatures,
                        "separates": signatures[0] != signatures[1],
                        "ast_nodes": 5})
    separators = [x for x in catalog if x["separates"]]
    if not separators:
        return {"status": "HOLD_NO_ALLOWED_NEW_QUESTION",
                "old_measurements": [first,second],
                "generated_candidates": len(catalog),
                "catalog": catalog}
    # No access to which world is *true*, only which programs separate them.
    # Equal-cost candidates are ordered by canonical program.
    chosen = min(separators, key=lambda x: (x["ast_nodes"],canonical(x["ast"])))
    return {"status": "QUESTION_GRAMMAR_EXPANDED_REVIEW_ONLY",
            "old_measurements": [first,second],
            "generated_candidates": len(catalog),
            "catalog": catalog,
            "selected_program": chosen["ast"],
            "selected_signatures": chosen["signature"],
            "old_language_saturated": True,
            "new_question_from_composed_primitives": True,
            "arbitrary_open_ended_grammar_invention": False}


def classical_exhaustive_reference(worlds):
    """Strong same-information control, independent matrix evaluator."""
    options = candidate_programs(worlds)
    found = sorted((canonical(ast), ast) for ast in options
                   if independent_execute(ast,worlds[0]) != independent_execute(ast,worlds[1]))
    return found[0][1] if found else None


class SyntheticWorldOwner:
    """Explicitly synthetic source owner. Query return is a *real method call*
    within a process, not an externally authenticated observation.
    """
    def __init__(self, world, *, identifier="fixture:anonymous-tree",
                 revision=1):
        self._world = graph(world["n"], world["edges"])
        self._identifier = identifier
        self._revision = revision
        self.questions_asked = 0
        self.rechecks = 0

    def contract(self):
        return {"kind": "SYNTHETIC_GRAPH_OWNER",
                "identity": self._identifier, "revision": self._revision,
                "graph_vertices": self._world["n"], "authenticated": False,
                "external_authority": "NONE"}

    def ask(self, ast):
        _typecheck(ast)
        self.questions_asked += 1
        receipt = {
            "schema": OBS_SCHEMA, "contract": self.contract(),
            "typed_question_ast": deepcopy(ast),
            "observed_boolean": execute(ast, self._world),
            "source_real_world_authenticated": False,
        }
        receipt["integrity_digest"] = digest(receipt)
        return receipt

    def recheck(self, receipt):
        self.rechecks += 1
        if type(receipt) is not dict or set(receipt) != {
            "schema", "contract", "typed_question_ast", "observed_boolean",
            "source_real_world_authenticated", "integrity_digest"
        }:
            raise HOLD("Malformed owner reply")
        if receipt["integrity_digest"] != digest({
            k:v for k,v in receipt.items() if k!="integrity_digest"
        }):
            raise HOLD("Checksum of owner reply changed")
        if (receipt["schema"] != OBS_SCHEMA
                or receipt["contract"] != self.contract()
                or receipt["source_real_world_authenticated"] is not False
                or type(receipt["observed_boolean"]) is not bool
                or receipt["observed_boolean"] != execute(
                    receipt["typed_question_ast"],self._world)
                or receipt["observed_boolean"] != independent_execute(
                    receipt["typed_question_ast"],self._world)):
            raise HOLD("Source owner no longer supports this receipt")
        return True


def _question_gloss(ast):
    k,j = _typecheck(ast)
    return ("Does the source graph contain an edge whose endpoint degrees "
            f"are {k} and {j}, in either orientation?")


def investigate(original_nt_question_node, worlds, owner, *, extension=True):
    """Compose a query unavailable in old menu and actually ask source owner."""
    if (type(original_nt_question_node) is not dict
            or original_nt_question_node.get("case_id") != SOURCE_NOTE
            or original_nt_question_node.get("world_claim_verified") is not False
            or original_nt_question_node.get("knowledge_status") !=
               "SOURCE_TEXT_VERIFIED_QUESTION_UNRESOLVED"):
        raise HOLD("No verified project-owned unanswered question parent")
    if not isinstance(owner, SyntheticWorldOwner):
        raise HOLD("Only declared synthetic source owner")
    if owner.contract()["graph_vertices"] != worlds[0]["n"]:
        raise HOLD("Source owner and hypothesis universe differ")
    result = find_missing_question(worlds, enable_extension=extension)
    if result["status"] != "QUESTION_GRAMMAR_EXPANDED_REVIEW_ONLY":
        return {"status":result["status"],"reasoning_evidence":result,
                "source_questions_asked":0,"external_authority":"NONE"}
    ast = result["selected_program"]
    observation = owner.ask(ast)
    owner.recheck(observation)
    if observation["observed_boolean"] not in result["selected_signatures"]:
        raise HOLD("Owner observation incompatible with proposed worlds")
    survivors = [i for i, prediction in enumerate(result["selected_signatures"])
                 if prediction == observation["observed_boolean"]]
    if len(survivors) != 1:
        raise HOLD("Experiment did not uniquely identify declared world")
    packet = {
        "schema": SCHEMA,
        "source_question_node": deepcopy(original_nt_question_node),
        "possible_worlds": deepcopy(list(worlds)),
        "old_language_readings": deepcopy(result["old_measurements"]),
        "old_language_nonidentifiable": True,
        "invented_question": {
            "text": _question_gloss(ast),
            "typed_program": ast,
            "programs_tested": result["generated_candidates"],
            "candidate_space": result["catalog"],
            "selected_predicted_outcomes": result["selected_signatures"],
            "synthesized_with_realized_world_hidden": True,
        },
        "source_owner_observation": observation,
        "remaining_possible_world_indices": survivors,
        "status": "SCOPED_SYNTHETIC_WORLD_IDENTIFIED",
        "question_grammar_enlargement_research_only": True,
        "source_new_questions": owner.questions_asked,
        "original_NT_question_unanswered_in_external_world": True,
        "provenance_limits": list(OPEN),
        "automatic_admission": False,"installed": False,
        "external_authority": "NONE",
    }
    packet["integrity_digest"] = digest(packet)
    return packet


def verify_packet(packet, original_nt_question_node, owner):
    """Reconstruct source text/question externally before calling this verifier."""
    if type(packet) is not dict or packet.get("schema") != SCHEMA:
        raise HOLD("Unrecognized evidence packet")
    if packet.get("integrity_digest") != digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Evidence packet altered")
    if (packet["source_question_node"] != original_nt_question_node
            or packet["original_NT_question_unanswered_in_external_world"] is not True
            or packet["provenance_limits"] != list(OPEN)
            or packet["automatic_admission"] is not False
            or packet["installed"] is not False
            or packet["external_authority"] != "NONE"
            or packet["old_language_nonidentifiable"] is not True
            or packet["question_grammar_enlargement_research_only"] is not True
            or packet["status"] != "SCOPED_SYNTHETIC_WORLD_IDENTIFIED"):
        raise HOLD("Authority, scope, or source question tampered")
    worlds = packet["possible_worlds"]
    fresh = find_missing_question(worlds)
    if fresh["status"] != "QUESTION_GRAMMAR_EXPANDED_REVIEW_ONLY":
        raise HOLD("Generated language no longer distinguishes source worlds")
    if (packet["old_language_readings"] != fresh["old_measurements"]
            or packet["invented_question"] != {
                "text": _question_gloss(fresh["selected_program"]),
                "typed_program": fresh["selected_program"],
                "programs_tested": fresh["generated_candidates"],
                "candidate_space": fresh["catalog"],
                "selected_predicted_outcomes": fresh["selected_signatures"],
                "synthesized_with_realized_world_hidden": True,
            }):
        raise HOLD("Invented question differs from independent replay")
    owner.recheck(packet["source_owner_observation"])
    if (packet["source_owner_observation"]["typed_question_ast"]
            != fresh["selected_program"]):
        raise HOLD("Source answered a different question")
    observed = packet["source_owner_observation"]["observed_boolean"]
    survivors = [i for i,v in enumerate(fresh["selected_signatures"])
                 if v == observed]
    if survivors != packet["remaining_possible_world_indices"] or len(survivors) != 1:
        raise HOLD("World classification not supported by source")
    return True


def reenter(packet, original_nt_question_node, owner):
    before = owner.questions_asked
    verify_packet(packet,original_nt_question_node,owner)
    if before != owner.questions_asked:
        raise HOLD("Reentry accidentally issued a new source question")
    return {"status":"SCOPED_QUESTION_AND_OBSERVATION_REVERIFIED",
            "new_discovery_questions":0,
            "source_owner_rechecks_performed":True,
            "answer_node":deepcopy(packet)}


def permute_world(g, perm):
    if len(perm)!=g["n"] or set(perm)!=set(range(g["n"])):
        raise HOLD("Not a complete vertex relabeling")
    return graph(g["n"], [(perm[a],perm[b]) for a,b in g["edges"]])


def run(original_nt_question_node):
    """Author-designed base and held-out *relabeling*, plus 7-node extension."""
    a,b = base_worlds()
    old = find_missing_question((a,b),enable_extension=False)
    if old["status"]!="HOLD_NO_ALLOWED_NEW_QUESTION":
        raise HOLD("Old vocabulary inadequacy not reproduced")
    first=find_missing_question((a,b))
    classical=classical_exhaustive_reference((a,b))
    if canonical(classical)!=canonical(first["selected_program"]):
        raise HOLD("Classical exhaustive baseline and synthesis disagree")
    owner = SyntheticWorldOwner(b,identifier="fixture:tree-B")
    packet=investigate(original_nt_question_node,(a,b),owner)
    verify_packet(packet,original_nt_question_node,owner)
    restart=reenter(json.loads(json.dumps(packet)),original_nt_question_node,owner)

    # Frozen question must transfer under every 6-vertex relabeling of either
    # existing structure. This tests invariance, not unseen graph families.
    total = 0
    for perm in permutations(range(6)):
        for i,g in enumerate((a,b)):
            x=permute_world(g,perm)
            if execute(first["selected_program"],x)!=first["selected_signatures"][i]:
                raise HOLD("Synthesized question fails vertex relabeling")
            if execute(first["selected_program"],x)!=independent_execute(first["selected_program"],x):
                raise HOLD("Independent heldout adjacency checker disagrees")
            total+=1

    a7,b7=extended_worlds()
    if old_measurements(a7)!=old_measurements(b7):
        raise HOLD("Larger-world base vocabulary no longer ambiguous")
    large_results = [
        execute(first["selected_program"],g) for g in (a7,b7)
    ]
    if large_results!=first["selected_signatures"]:
        raise HOLD("Frozen typed question does not transfer to larger graph")
    if any(execute(first["selected_program"],g)!=independent_execute(first["selected_program"],g)
           for g in (a7,b7)):
        raise HOLD("Larger-world independent check disagreement")
    return {
        "schema":"motif.collective004.research-benchmark.v1",
        "first_grammar_status":old["status"],
        "new_grammar_status":first["status"],
        "old_measurement_values":first["old_measurements"],
        "programs_enumerated":first["generated_candidates"],
        "invented_typed_question":first["selected_program"],
        "selected_predictions":first["selected_signatures"],
        "classical_exhaustive_exact_tie":True,
        "heldout_vertex_relabeling_checks":total,
        "larger_seven_node_same_menu_collision":True,
        "larger_seven_node_invented_question_predictions":large_results,
        "fresh_source_questions":owner.questions_asked,
        "reentry_new_source_questions":restart["new_discovery_questions"],
        "complete_answer_packet":packet,
        "tests_not_independent_source_authorship":True,
        "genuine_general_new_grammar_invention_unproved":True,
        "world_claims_not_proven":True,
        "status":"REVIEW_SCOPED_PROGRAM_SYNTHESIS_NO_PRODUCTION_AUTHORITY",
    }
