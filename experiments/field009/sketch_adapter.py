"""Source-preserving adapter to FIELD-007 dashed ink.

A ratio of detected drawn-stroke spans is not a physical boundary length.
This adapter never auto-joins ink fragments into a dog fence.
"""
from pathlib import Path
from hashlib import sha256
import sys

def ink_ratios(sketch_path,source_id='paper',max_candidates=12):
    p7=Path(__file__).resolve().parents[1]/'field007'
    if str(p7) not in sys.path:sys.path.insert(0,str(p7))
    from ink import extract_dashes
    p=Path(sketch_path)
    groups=extract_dashes(p,max_candidates=max_candidates)
    largest=max([g.width_pixels for g in groups],default=0)
    return {'source_id':source_id,'original_sha256':sha256(p.read_bytes()).hexdigest(),
            'method':'FIELD-007 detected ink-group spans',
            'groups':[{'id':g.id,'axis':g.axis,'span_pixels':g.width_pixels,
                       'ink_support':g.ink_support,
                       'drawn_span_relative_to_longest':round(g.width_pixels/largest,3) if largest else None,
                       'status':'TENTATIVE_INK_ONLY'} for g in groups],
            'physical_length_inferred':False,'complete_fence_route_reconstructed':False,
            'required_next_input':'A labeled physical reference measurement, verified proportionality and connected route geometry'}
