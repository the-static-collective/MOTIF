"""LEGIT-011: use MOTIF's own prior generated reasoning methods to rewrite
its next search kernel, and then feed that kernel back into its own CEGIS.

Generator is explicitly confined to a small *typed source-template DSL*:
READ_COLUMN, JOIN(AND|OR|XOR), PICK(FIRST|LAST), EMPTY(HOLD|FIRST).
Its independent counterexample oracle checks all 3**8 partial input states.
The resulting source is deterministically emitted, statically checked and
run in a restricted in-process namespace. It is NOT an unrestricted
self-editing agent. The new source remains a draft, unmerged artifact.

Second revision reuses LEGIT-009's actual NAND CEGIS to synthesize the
intersection operator needed for incrementally maintaining a search index;
the revised search kernel is itself used in subsequent synthesis cycles.
"""
from __future__ import annotations

from hashlib import sha256
import ast
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit010"))
sys.path.insert(0,str(HERE.parent/"legit009"))

from bootstrap import (
    library, invent_successor_search, _compressed_candidates,
    compose_circuit, _seal as previous_seal
)
from synthesizer import cegis as PREVIOUS_CEGIS,load_verified as PREVIOUS_LOAD
from search_reference import ScanOracle,StrongClassicalIndex,checked_query
from search_reference import independent_update_check

SCHEMA="motif.self-rewrite-search-source.v1"
TOKENS={
    "combine":("OR","XOR","AND"),
    "invert":(False,True),
    "pick":("FIRST","LAST"),
    "empty":("HOLD","FIRST"),
}
MAX_CEX=25

class HOLD(ValueError):pass


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()

def recipes():
    for combine in TOKENS["combine"]:
        for invert in TOKENS["invert"]:
            for pick in TOKENS["pick"]:
                for empty in TOKENS["empty"]:
                    yield {"combine":combine,"invert":invert,
                           "pick":pick,"empty":empty}

def validate_recipe(recipe):
    if (not isinstance(recipe,dict) or set(recipe)!=set(TOKENS)
        or any(recipe[k] not in values for k,values in TOKENS.items())):
        raise HOLD("Unsupported reasoning source transformation")


def build_columns(rows):
    """Execution-side index, NOT the independent gold reference."""
    if not rows:
        raise HOLD("No candidate algorithms")
    columns={}
    for row in range(8):
        for desired in (False,True):
            column=0
            for i,entry in enumerate(rows):
                if bool(entry["truth_mask"]&(1<<row)) is desired:
                    column |= 1<<i
            columns[row,desired]=column
    return columns


def apply_recipe(recipe,columns,size,observed):
    """Pre-source interpreter used ONLY during counterexample learning."""
    validate_recipe(recipe)
    checked_query(observed)
    if not observed:
        return 0
    bits=(1<<size)-1 if recipe["combine"]=="AND" else 0
    for row,flag in observed:
        column=columns[row,not flag if recipe["invert"] else flag]
        if recipe["combine"]=="AND":
            bits &= column
        elif recipe["combine"]=="OR":
            bits |= column
        else:
            bits ^= column
    if bits==0:
        return None if recipe["empty"]=="HOLD" else 0
    return ((bits&-bits).bit_length()-1 if recipe["pick"]=="FIRST"
            else bits.bit_length()-1)


def synthesize_rewrite(rows):
    """Actual CEGIS produces source-transform recipe from counterexamples."""
    reference=ScanOracle(rows)
    columns=build_columns(rows)
    known=[tuple()]
    transcript=[]
    for iteration in range(MAX_CEX):
        chosen=None
        for recipe in recipes():
            if all(apply_recipe(recipe,columns,len(rows),q)==reference.query(q)[0]
                   for q in known):
                chosen=recipe
                break
        if chosen is None:
            raise HOLD("No typed search-rewrite recipe covers counterexamples")
        # Critically this verifier is a SEPARATE, conventional full scan.
        challenge=reference.challenge(
            lambda q: apply_recipe(chosen,columns,len(rows),q))
        transcript.append({
            "iteration":iteration+1,"candidate_recipe":chosen,
            "counterexample":challenge,
            "known_cases_before":len(known),
        })
        if challenge is None:
            return {"program_recipe":chosen,
                    "counterexamples":len(transcript)-1,
                    "transcript":transcript,
                    "fully_checked_partial_states":3**8}
        q=tuple((row,bool(flag)) for row,flag in challenge["partial"])
        if q in known:
            raise HOLD("Verifier returned a previously known contradiction")
        if apply_recipe(chosen,columns,len(rows),q)==reference.query(q)[0]:
            raise HOLD("Not a real counterexample")
        known.append(q)
    raise HOLD("Search source compiler failed finite proof")


class IntersectionVerifier:
    """Independent two-input update oracle; no given answer *circuit*."""
    def truth(self,a,b):
        return a and b
    def label_initial(self,a,b):
        return self.truth(a,b)
    def check(self,gates,output):
        from independent_oracle import interpret
        for a in (False,True):
            for b in (False,True):
                outcome=interpret(gates,output,(a,b))
                expected=self.truth(a,b)
                if outcome is not expected:
                    return (a,b,expected)
        return None


def synthesize_update():
    """Actually invoke previous (LEGIT-009) CEGIS for search-state update."""
    verifier=IntersectionVerifier()
    result=PREVIOUS_CEGIS(verifier,"SearchIndexIntersection")
    cartridge=result["cartridge"]
    PREVIOUS_LOAD(cartridge,verifier)
    if cartridge["truth_mask"]!=8:
        raise HOLD("Generated operator is not a Boolean intersection")
    exact=independent_update_check(verifier.truth)
    if not exact["complete"]:
        raise HOLD("Search-update mathematical invariant fails")
    return {"operator":"AND_TWO_BOOLEAN_MEMBERSHIP_BITS",
            "emitted_python_primitive":"BITWISE_AND",
            "source_cartridge":cartridge,
            "previous_generation_synthesizer_used":True,
            "independent_four_case_verifier":exact,
            "counterexample_count":cartridge["counterexample_count"]}


def emit_source(recipe,update):
    """Source text is selected only from a finite trusted code-template DSL.

    It *does not* interpolate user text, field names, paths or arbitrary
    statements. Untrusted recipes are rejected before generation.
    """
    validate_recipe(recipe)
    if (update["operator"]!="AND_TWO_BOOLEAN_MEMBERSHIP_BITS" or
        update["source_cartridge"]["truth_mask"]!=8):
        raise HOLD("No finite update proof")
    init="(1 << size) - 1" if recipe["combine"]=="AND" else "0"
    merge={"AND":"&","OR":"|","XOR":"^"}[recipe["combine"]]
    flipped="not flag" if recipe["invert"] else "flag"
    first="(bits & -bits).bit_length() - 1" if recipe["pick"]=="FIRST" else "bits.bit_length() - 1"
    empty="None" if recipe["empty"]=="HOLD" else "0"
    return f'''"""Automatically generated LEGIT-011 search upgrade.
RESEARCH HOLD: needs source review; not a verified signature or production API.
Generator: experiments/legit011/rewrite.py, finite CEGIS template grammar.
"""
SCHEMA = "motif.generated-search-rewrite.v1"
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True

def build_index(candidates):
    size = len(candidates)
    if size == 0:
        raise ValueError("Empty candidate corpus")
    columns = {{}}
    for row in range(8):
        for flag in (False, True):
            bits = 0
            for i,program in enumerate(candidates):
                if bool(program["truth_mask"] & (1 << row)) == flag:
                    bits |= (1 << i)
            columns[row,flag] = bits
    return columns

def choose(columns,size,observed):
    if not observed:
        return (0,0)
    bits = {init}
    operations = 0
    for row,flag in observed:
        column = columns[row,{flipped}]
        bits = bits {merge} column
        operations += 1
        if not bits and "{recipe["combine"]}" == "AND":
            break
    if not bits:
        return ({empty},operations)
    return ({first},operations)

class IncrementalSearch:
    """A generated algorithm reuses verified intersection for every update."""
    def __init__(self,columns,size):
        self.columns=columns
        self.bits=(1 << size) - 1
        self.observed=set()
        self.operations=0

    def add(self,row,flag):
        if row in self.observed:
            raise ValueError("Repeated observation")
        if type(row) is not int or not 0 <= row < 8 or type(flag) is not bool:
            raise ValueError("Invalid observation")
        self.observed.add(row)
        self.bits &= self.columns[row,flag]
        self.operations += 1

    def first(self):
        return (self.bits & -self.bits).bit_length() - 1 if self.bits else None
'''

def static_source_validation(source):
    """Strict source review: generated code stays within predefined sandbox."""
    if not isinstance(source,str) or len(source)>5000:
        raise HOLD("Bad source emission")
    tree=ast.parse(source)
    banned=(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,
            ast.Lambda,ast.Await,ast.AsyncFunctionDef,ast.With,
            ast.AsyncWith,ast.Try,ast.Delete,ast.Yield,ast.YieldFrom)
    for node in ast.walk(tree):
        if isinstance(node,banned):
            raise HOLD("Generated code contains forbidden source construct")
        if isinstance(node,ast.Name) and node.id in (
                "eval","exec","open","compile","__import__","input",
                "getattr","setattr","globals","locals","breakpoint",
                "exit","quit"):
            raise HOLD("Source attempted unrestricted runtime access")
        if isinstance(node,ast.Attribute) and node.attr.startswith("__"):
            raise HOLD("Source attempted reserved attribute access")
    return {"status":"STATIC_SOURCE_TEMPLATE_CHECK_PASSED",
            "ast_nodes_checked":sum(1 for _ in ast.walk(tree)),
            "source_sha256":sha256(source.encode()).hexdigest(),
            "not_a_general_security_sandbox":True}


def load_generated_source(source):
    """Run fixed compiler's output ONLY after matching known template shape.

    Restricted builtins are defense in depth, not general Python isolation.
    This trusted grammar can emit only a few search functions.
    """
    report=static_source_validation(source)
    if not source.startswith('"""Automatically generated LEGIT-011 search upgrade.'):
        raise HOLD("Not generated by registered template")
    safe={"__builtins__":{"len":len,"range":range,"enumerate":enumerate,
                          "bool":bool,"set":set,"ValueError":ValueError}}
    exec(compile(source,"<MOTIF-LEGIT011-VERIFIED-TEMPLATE>","exec"),safe,safe)
    return safe


def _hash_manifest(record):
    return digest(record)


def produce_upgrade():
    """Actual self-improvement: previous engine -> rewrite -> new engine."""
    base=invent_successor_search()["algorithm"]
    candidates=_compressed_candidates(base)
    rewrite=synthesize_rewrite(candidates)
    update=synthesize_update()
    source=emit_source(rewrite["program_recipe"],update)
    static=static_source_validation(source)
    raw={
        "schema":SCHEMA,
        "status":"DRAFT_SOURCE_TRANSFORMATION_ONLY",
        "parent_legit010_search_sha256":base["sha256"],
        "parent_legit009_update_sha256":update["source_cartridge"]["sha256"],
        "meta_counterexamples":rewrite["counterexamples"],
        "meta_transcript":rewrite["transcript"],
        "generated_recipe":rewrite["program_recipe"],
        "source_sha256":static["source_sha256"],
        "finite_verification_states":rewrite["fully_checked_partial_states"],
        "source_changes_production":False,
        "unrestricted_python_self_edit":False,
        "real_world_authority":False,
    }
    return {"manifest":dict(raw,sha256=_hash_manifest(raw)),
            "source":source,"candidate_rows":candidates,
            "source_checked":static,"update":update}


def verify_upgrade(manifest,source,rows):
    """Independent gold scan must agree on every partial specification."""
    if not isinstance(manifest,dict) or "sha256" not in manifest:
        raise HOLD("Missing generated provenance")
    raw={k:v for k,v in manifest.items() if k!="sha256"}
    if _hash_manifest(raw)!=manifest["sha256"]:
        raise HOLD("Generated reasoning program manifest altered")
    if (manifest["schema"]!=SCHEMA or
        manifest["status"]!="DRAFT_SOURCE_TRANSFORMATION_ONLY" or
        manifest["source_sha256"]!=sha256(source.encode()).hexdigest() or
        manifest["finite_verification_states"]!=6561 or
        manifest["real_world_authority"] is not False):
        raise HOLD("Unknown source rewrite authority")
    verified=static_source_validation(source)
    module=load_generated_source(source)
    reference=ScanOracle(rows)
    columns=module["build_index"](rows)
    checked=0
    from search_reference import states
    for partial in states():
        expected=reference.query(partial)[0]
        got=module["choose"](columns,len(rows),partial)[0]
        if got!=expected:
            raise HOLD("Generated source differs from 010 search on partial evidence")
        checked+=1
    if checked!=6561:
        raise HOLD("Incomplete finite semantic proof")
    return {"status":"VERIFIED_FULL_FINITE_SEARCH_REWRITE",
            "partial_truth_tables_checked":checked,
            "existing_legit010_search_behavior_preserved":True,
            "source_sha256":verified["source_sha256"],
            "independently_authored_examiner":False,
            "real_world_authority":False}
