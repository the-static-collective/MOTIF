"""Deterministic GEOM-007 synthetic demo, including an incompatible-world case."""
import json
from pathlib import Path
from contextual import ContextualAtlas,Context,Lens,run_document

HERE=Path(__file__).parent

def main():
    d=json.loads((HERE/'example-input.json').read_text(encoding='utf-8'))
    a=run_document(d)
    b=dict(d);b['display']=False
    ablated=run_document(b)
    a_without_coordinates=dict(a['inspection'])
    a_without_coordinates['coordinates']={}
    assert a_without_coordinates==ablated['inspection'], 'layout affected semantic result'
    c=dict(d);c['selected_lenses']=['appearance','causal']
    expanded=run_document(c)
    original=ContextualAtlas([Context(x['id'],x['scope'],tuple(x['variables']),tuple(x['alternatives']),x['source_root']) for x in d['contexts']],
                             [Lens(x['id'],tuple(x['variables']),x.get('layout','NONE')) for x in d['lenses']],[])
    held=original.filter_on_observation('origin','PRIMARY','simulation:sensor-output')
    report={'early_lens':a['inspection'],'question':a['inquiry'],
            'two_lenses':expanded['inspection'],'synthetic_observation_counterfactual':held,
            'no_geometry_semantics_identical':True,
            'experiment':'GEOM-007', 'authority':'NONE'}
    print(json.dumps(report,sort_keys=True,indent=2))
    return report

if __name__=='__main__':main()
