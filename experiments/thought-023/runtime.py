"""Fixed, reviewed Python runtime for source-owned THOUGHT-023 typed expressions.

Model can select only a licensed extension label, never Python statements.
Running Python -I is NOT an OS security sandbox. Trusted static template only.
"""
from __future__ import annotations
import ast, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
from grammar import canonical,validate_expression, GrammarError

TRUSTED_RUNTIME='''"""MOTIF-023 fixed grammar runtime -- review-only; no model-origin code."""
import json, sys
PROGRAM = json.loads(__PROGRAM__)
EXTENSION = __EXTENSION__
COLORS = ("red", "blue", "green")
def calculate(expr, on, toggles):
    if "ref" in expr:
        sources = {"state.on": on, "arrival.toggles": toggles,
                   "universe": frozenset(COLORS), "empty": frozenset()}
        return sources[expr["ref"]]
    parts = [calculate(child,on,toggles) for child in expr["args"]]
    if expr["op"] == "union":return parts[0] | parts[1]
    if expr["op"] == "difference":return parts[0] - parts[1]
    if expr["op"] == "complement":return frozenset(COLORS) - parts[0]
    raise ValueError("unknown typed expression")
def mask(s):
    return sum(1 << i for i, c in enumerate(COLORS) if c in s)
def convert(z):
    return frozenset(c for i,c in enumerate(COLORS) if z & (1 << i))
request = json.load(sys.stdin)
if type(request) is not list or len(request)>64:raise ValueError("bounded trial only")
output=[]
for pair in request:
    if type(pair) is not list or len(pair)!=2 or any(type(x) is not int or x<0 or x>7 for x in pair):
        raise ValueError("invalid input pair")
    output.append(mask(calculate(PROGRAM,convert(pair[0]),convert(pair[1]))))
print(json.dumps(output,separators=(",", ":")))
'''

def compile_source(expression,extension):
    checked=validate_expression(expression,extension)
    s='\n# Model-origin source is never accepted.\n'+TRUSTED_RUNTIME.replace('__PROGRAM__',repr(canonical(checked))).replace('__EXTENSION__',repr(extension))
    parsed=ast.parse(s)
    imports={alias.name for node in ast.walk(parsed) if isinstance(node,ast.Import) for alias in node.names}
    if imports!={'json','sys'} or any(isinstance(x,(ast.ImportFrom,ast.AsyncFunctionDef,ast.Global,ast.Nonlocal)) for x in ast.walk(parsed)):
        raise GrammarError('trusted compiler policy violated')
    return s

def execute_source(expression,extension):
    s=compile_source(expression,extension)
    specimens=[[a,b] for a in range(8) for b in range(8)]
    with tempfile.TemporaryDirectory(prefix='motif023-source-only-') as d:
        path=Path(d)/'trusted_runtime.py'
        path.write_text(s,encoding='utf-8')
        proc=subprocess.run([sys.executable,'-I','-B',str(path)],input=json.dumps(specimens),
            capture_output=True,encoding='utf-8',timeout=4,cwd=d,
            env={'PYTHONNOUSERSITE':'1','PATH':os.environ.get('PATH','')},check=False)
    if proc.returncode!=0 or len(proc.stdout)>1024:
        raise GrammarError('bounded fixed runtime failed')
    try:results=json.loads(proc.stdout)
    except (ValueError,TypeError) as exc:raise GrammarError('fixed runtime invalid JSON') from exc
    if type(results) is not list or len(results)!=64 or any(type(x) is not int or not 0<=x<=7 for x in results):
        raise GrammarError('fixed runtime invalid output')
    return {'results':results,'source_sha256':hashlib.sha256(s.encode('utf-8')).hexdigest(),
            'execution':'TRUSTED_FIXED_TEMPLATE_SUBPROCESS_NOT_SECURITY_SANDBOX',
            'programs_from_untrusted_model':0,'external_authority':'NONE'}
