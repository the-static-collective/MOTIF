"""Deterministic six-panel SVG board; diagram is an instrument, not evidence."""
from __future__ import annotations
from html import escape
from math import isfinite

COLS = 3
PW, PH = 500, 375
PALETTE = {"associated": "#416a6f", "requires": "#2c5d93",
           "enables": "#408259", "contradicts": "#ad4c4c", "precedes": "#8969a7"}


def render_board(result, field_snapshot, *, title="MOTIF | Parallel Thought Fields"):
    if result.get("external_authority") != "NONE":
        raise ValueError("renderer demands non-authoritative view")
    concepts={c["id"]:c for c in field_snapshot["semantic"]["concepts"]}
    manifests={m["id"]:m for m in field_snapshot["semantic"]["manifestations"]}
    views=result["views"]
    rows=(len(views)+COLS-1)//COLS
    width,height=COLS*PW,70+rows*PH+44
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Parallel non-authoritative concept views">',
         f'<rect width="100%" height="100%" fill="#f3efe5"/>',
         f'<text x="30" y="37" font-family="serif" font-size="28" fill="#233840">{escape(title)}</text>',
         '<text x="30" y="56" font-family="sans-serif" font-size="12" fill="#576b70">Same authored graph • independent geometries • locations are not evidence</text>']
    for idx,v in enumerate(views):
        ox,oy=(idx%COLS)*PW,70+(idx//COLS)*PH
        out.append(f'<rect x="{ox+10}" y="{oy+10}" width="{PW-20}" height="{PH-20}" rx="13" fill="#fffdf7" stroke="#a8afa9"/>')
        out.append(f'<text x="{ox+26}" y="{oy+40}" font-family="sans-serif" font-size="19" fill="#23414c">{escape(v["lens"].replace("_"," ").upper())}</text>')
        out.append(f'<text x="{ox+26}" y="{oy+57}" font-family="sans-serif" font-size="10" fill="#667981">{escape(v["source_evidence_digest"][:16])} | source evidence fingerprint</text>')
        if v["lens"] == "NONE":
            n=len(v["relations"])
            lines=[f"{len(manifests)} distinct manifestations", f"{n} attributed relations", "No spatial coordinates created", "Same source questions &amp; typed relations"]
            for j,line in enumerate(lines):
                out.append(f'<text x="{ox+36}" y="{oy+110+34*j}" font-family="sans-serif" font-size="15" fill="#3e5962">{line}</text>')
            continue
        placements=v["placements"]
        xs=[p["x"] for p in placements];ys=[p["y"] for p in placements]
        if not placements or not all(isfinite(x) for x in xs+ys):
            continue
        minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys)
        spanx=max(maxx-minx,1.0);spany=max(maxy-miny,1.0)
        def tr(p):
            return (ox+77+ (p["x"]-minx)/spanx*(PW-155),
                    oy+93+(p["y"]-miny)/spany*(PH-165))
        by_manifest={}
        for p in placements:
            by_manifest.setdefault(p["manifestation_id"],[]).append((p,tr(p)))
        for edge in v["relations"]:
            a,b=edge["source"],edge["target"]
            if a not in by_manifest or b not in by_manifest:continue
            x,y=by_manifest[a][0][1];u,w=by_manifest[b][0][1]
            color=PALETTE[edge["predicate"]]
            dash=' stroke-dasharray="4 5"' if edge["status"]!="AUTHORED" else ''
            out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{u:.1f}" y2="{w:.1f}" stroke="{color}" stroke-width="1.7"{dash} opacity=".67"/>')
        for p in placements:
            x,y=tr(p)
            m=manifests[p["manifestation_id"]]
            c=concepts[m["concept_id"]]
            label=escape(str(c["label"])[:15])
            color="#d5a14b" if p["appearance"]=="preserved_007" else "#4b7781"
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#fffdf7" stroke="{color}" stroke-width="2.5"/>')
            out.append(f'<text x="{x:.1f}" y="{y-13:.1f}" font-family="sans-serif" font-size="10" fill="#23404a" text-anchor="middle">{label}</text>')
        out.append(f'<text x="{ox+27}" y="{oy+PH-26}" font-family="sans-serif" font-size="11" fill="#6b7779">{len(placements)} placements • {len(manifests)} manifestations • HOLD</text>')
    out.append(f'<text x="30" y="{height-15}" font-family="sans-serif" font-size="12" fill="#586b70">Gold rings = preserved source placements | dashed lines = hypothetical authored input | no PEN or external authority</text>')
    out.append('</svg>')
    return '\n'.join(out)+'\n'
