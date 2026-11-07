
# Model-origin source is never accepted.
"""MOTIF-023 fixed grammar runtime -- review-only; no model-origin code."""
import json, sys
PROGRAM = json.loads('{"args":[{"ref":"universe"},{"ref":"state.on"}],"op":"difference"}')
EXTENSION = 'universe_constant'
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
