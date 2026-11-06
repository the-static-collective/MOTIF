"""Demonstrate user-authored typed thoughts and optional mode self-selection."""
import json
from pathlib import Path
from thought_space import Node,Edge,ThoughtGraph,from_text,choose_thought_space
from display import render_svg


def synthetic_fellowship():
    # Imaginary planning facts. Not claims about any actual people or event.
    labels={
        'shelf':('Food shelf','activity'),'storage':('Cold storage','resource'),
        'volunteer':('Volunteers','resource'),'meal':('Community meal','activity'),
        'transport':('Transport','activity'),'fish':('Fresh food','resource'),
        'schedule':('Time window','constraint'),'neighbor':('Neighbors','people'),
        'music':('Music night','activity'),'room':('Gathering space','place'),
        'claim_yes':('Food available today','claim'),'claim_no':('Food availability unverified','claim')}
    nodes=[Node(k,*v) for k,v in labels.items()]
    edges=[
        Edge('shelf','storage','associated','mock-steward-A'),
        Edge('meal','storage','associated','mock-cook-B'),
        Edge('shelf','volunteer','associated','mock-steward-C'),
        Edge('meal','volunteer','associated','mock-cook-D'),
        Edge('fish','storage','requires','mock-note-E'),
        Edge('transport','schedule','requires','mock-note-F'),
        Edge('meal','room','requires','mock-note-G'),
        Edge('music','room','requires','mock-note-H'),
        Edge('neighbor','music','associated','mock-note-I'),
        Edge('neighbor','meal','associated','mock-note-J'),
        Edge('claim_yes','claim_no','contradicts','mock-review-K')]
    return ThoughtGraph(nodes,edges)


def main(write=True):
    graph=synthetic_fellowship()
    auto=choose_thought_space(graph,'explore what else relates to these ideas',anchors=('meal',))
    trace=choose_thought_space(graph,'how to connect the shelf to a meal',anchors=('shelf','meal'))
    contrast=choose_thought_space(graph,'what contradicts here?')
    free_text=from_text('Fish for dinner; neighbors bring fish, friends cook dinner.',origin='mock-text-1')
    no_geometry=choose_thought_space(graph,'explore',allow_geometry=False)
    output={
        'experiment':'MOTIF-GEOM-005',
        'geometry_invoked_by_choice':auto['projection'],
        'mode_selected':auto['thought_mode'],
        'projection_scores':auto.get('projection_scores'),
        'hypothetical_associations':auto['answer'].get('proposals',[]),
        'trace':trace['answer'],
        'contradictions':contrast['answer'],
        'free_text_terms':len(free_text.nodes),
        'free_text_edges':len(free_text.edges),
        'no_geometry_fallback':no_geometry['projection'],
        'authority':'HOLD',
        'remark':'Synthetic field. No genuine social, food, medical or other real-world claims.'}
    if write:
        root=Path(__file__).parent
        (root/'thought-space.svg').write_text(render_svg(graph,auto,title='MOTIF | A geometry of associations'),encoding='utf-8')
        (root/'demo-result.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
        (root/'thought-source.json').write_text(json.dumps(graph.as_data(),indent=2)+'\n',encoding='utf-8')
    return output

if __name__=='__main__':print(json.dumps(main(),indent=2))
