"""CLI tool/adapter: JSON source graph (or a string of raw words) to reasoning and SVG.

Usage: python interface.py input.json [output.svg]
No network or side effects other than writing the requested local SVG.
"""
import json,sys
from pathlib import Path
from thought_space import Node,Edge,ThoughtGraph,from_text,choose_thought_space
from display import render_svg


def process(data):
    if not isinstance(data,dict):raise ValueError('JSON object required')
    if 'text' in data:
        if not isinstance(data['text'],str) or len(data['text'])>16000:raise ValueError('text too long')
        graph=from_text(data['text'],data.get('origin','operator-provided-text'))
    else:
        nodes=data.get('nodes',[]); edges=data.get('edges',[])
        if len(nodes)>100 or len(edges)>500:raise ValueError('bounded experiment: maximum 100 nodes and 500 edges')
        graph=ThoughtGraph([Node(**n) for n in nodes],[Edge(**e) for e in edges])
    question=data.get('question','explore')
    if not isinstance(question,str):raise ValueError('question must be a string')
    anchors=data.get('anchors',[])
    if not isinstance(anchors,list):raise ValueError('anchors must be a list')
    plan=choose_thought_space(graph,question,anchors,
        allow_geometry=data.get('allow_geometry',True),
        geometry_preference=data.get('geometry_preference','auto'))
    # JSON type adaptation; tuples naturally encode as lists.
    output={'status':'PROPOSAL_ONLY','graph':graph.as_data(),'plan':plan,
            'epistemic_boundary':'geometric coordinates and co-mentions are not facts',
            'authority':'HOLD'}
    return graph,plan,output


def main():
    if len(sys.argv) not in (2,3):raise SystemExit('usage: python interface.py input.json [out.svg]')
    data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    graph,plan,output=process(data)
    if len(sys.argv)==3:
        if plan['projection']=='NONE':raise ValueError('geometry was refused; no SVG produced')
        Path(sys.argv[2]).write_text(render_svg(graph,plan),encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__=='__main__': main()
