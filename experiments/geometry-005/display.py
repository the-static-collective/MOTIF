"""SVG thought map: visual witness, not stored geometry of semantic truth."""
from html import escape
from math import hypot
from thought_space import choose_thought_space


def render_svg(graph, plan, *, title='MOTIF thought space', width=1160, height=820):
    raw=plan['coordinates']
    if not raw:raise ValueError('cannot render a refused map')
    # Pack disconnected subgraphs into separate visual rooms. This is layout,
    # not a new inference that those groups ought to be independent.
    neighbors={k:set() for k in raw}
    for e in graph.edges:
        if e.observed:
            neighbors[e.source].add(e.target)
            neighbors[e.target].add(e.source)
    seen=set();components=[]
    for n in sorted(raw):
        if n in seen:continue
        group=[];stack=[n];seen.add(n)
        while stack:
            x=stack.pop();group.append(x)
            for y in sorted(neighbors[x]):
                if y not in seen:seen.add(y);stack.append(y)
        components.append(sorted(group))
    components.sort(key=lambda c:(-len(c),c))
    if len(components)==1:
        rooms=[(70,125,width-70,height-108)]
    else:
        rooms=[(70,120,width*0.61,height-115)]
        remaining=len(components)-1
        for i in range(remaining):
            top=122+i*(height-230)/remaining
            rooms.append((width*0.67,top,width-62,top+(height-240)/remaining))
    p={}
    for component,room in zip(components,rooms):
        left,top,right,bottom=room
        minx,maxx=min(raw[k][0] for k in component),max(raw[k][0] for k in component)
        miny,maxy=min(raw[k][1] for k in component),max(raw[k][1] for k in component)
        xwidth=max(maxx-minx,0.001);yheight=max(maxy-miny,0.001)
        spanx=right-left-140;spany=bottom-top-95
        factor=min(spanx/xwidth,spany/yheight)
        for node in component:
            xx=(left+right)/2+(raw[node][0]-(minx+maxx)/2)*factor
            yy=(top+bottom)/2+(raw[node][1]-(miny+maxy)/2)*factor
            p[node]=[xx,yy]
        # Label collision solver; ensure nodes within their allotted panel.
        for _ in range(45):
            changed=False
            for i,a in enumerate(component):
                for b in component[i+1:]:
                    dx=p[a][0]-p[b][0];dy=p[a][1]-p[b][1]
                    wa=max(96,min(182,12+len(graph.nodes[a].label)*7.5))
                    wb=max(96,min(182,12+len(graph.nodes[b].label)*7.5))
                    overlap_x=(wa+wb)/2+12-abs(dx)
                    overlap_y=46-abs(dy)
                    if overlap_x<=0 or overlap_y<=0:continue
                    changed=True
                    if overlap_x/(wa+wb)<overlap_y/46:
                        delta=overlap_x/2+1
                        direction=1 if dx>=0 else -1
                        p[a][0]+=direction*delta;p[b][0]-=direction*delta
                    else:
                        delta=overlap_y/2+1
                        direction=1 if dy>=0 else -1
                        p[a][1]+=direction*delta;p[b][1]-=direction*delta
            for node in component:
                p[node][0]=max(left+58,min(right-58,p[node][0]))
                p[node][1]=max(top+25,min(bottom-25,p[node][1]))
            if not changed:break
    output=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            'role="img" aria-label="Typed association thought map">',
            '<rect width="100%" height="100%" fill="#f8f5ec"/>',
            '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M 0 0 L 6 3 L 0 6" fill="none" stroke="#59626c"/></marker></defs>',
            f'<text x="58" y="49" font-size="24" font-family="sans-serif" fill="#182d34">{escape(title)}</text>',
            f'<text x="59" y="76" font-size="14" font-family="sans-serif" fill="#63717a">'
            f'Projection: {escape(plan["projection"])} | Mode: {escape(plan["thought_mode"])} | '
            'Coordinates are illustrative, not semantic evidence</text>']
    for e in graph.edges:
        x,y=p[e.source];u,v=p[e.target]
        if e.relation=='contradicts': color='#b63d3d';dash=' stroke-dasharray="6 4"';arrow=''
        elif not e.observed: color='#be7f36';dash=' stroke-dasharray="3 5"';arrow=''
        elif e.relation=='co_mentioned':color='#b5b3a5';dash=' stroke-dasharray="3 5"';arrow=''
        else:color='#70878a';dash='';arrow=' marker-end="url(#arrow)"' if e.relation in ('enables','requires') else ''
        output.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{u:.1f}" y2="{v:.1f}" stroke="{color}" stroke-width="{max(1,e.confidence*2.1):.1f}"{dash}{arrow}/>')
    # Proposals rendered as separate dashed edges, NEVER inserted into graph.
    proposals=plan['answer'].get('proposals',[])
    for h in proposals[:16]:
        a,b=h['nodes'];x,y=p[a];u,v=p[b]
        output.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{u:.1f}" y2="{v:.1f}" stroke="#cf9a25" stroke-width="3" stroke-dasharray="9 6"/>')
    for n in sorted(graph.nodes):
        x,y=p[n];label=escape(graph.nodes[n].label)
        # min-size box, word wrap is intentionally not automatic.
        boxw=max(96,min(182,12+len(label)*7.5))
        output.append(f'<rect x="{x-boxw/2:.1f}" y="{y-17:.1f}" width="{boxw:.1f}" height="34" rx="14" fill="#fffdfa" stroke="#2c666a" stroke-width="1.7"/>')
        output.append(f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#24414a">{label}</text>')
    output.extend([f'<text x="56" y="{height-58}" font-family="sans-serif" font-size="13" fill="#6c7272">'
                   'Solid: authored relationship | Dotted red: contradiction | Dashed gold: proposed association</text>',
                   f'<text x="56" y="{height-33}" font-family="sans-serif" font-size="12" fill="#6c7272">'
                   'HOLD: no new edge observed, no external action authorized</text>',
                   '</svg>'])
    return '\n'.join(output)+'\n'
