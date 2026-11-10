"""An exact, fully conditional evidence packet from the atlas experiment."""
import json
from blanch import run_case

if __name__=='__main__':
    print(json.dumps(run_case(608,'blanch',full_trace=True),sort_keys=True,indent=2))
