"""Human-language interface and selected adaptive query loop, local synthetic."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from inquiry import InquiryCycle
from fixtures import make_engine,possible_worlds,fixture_oracle
from human_talk import dialogue


def main():
    with TemporaryDirectory() as td:
        field,engine,_=make_engine(Path(td)/'e.jsonl')
        worlds=possible_worlds(engine)
        truth=worlds[11]  # supplied only to the toy oracle
        before=field.snapshot()
        talk=dialogue(engine,worlds,
                      'What if food and a community meal could connect?',
                      fixture_oracle(truth),
                      selected_pair=('m:food','m:meal'),
                      budget=3,geometry=True)
        assert before==field.snapshot()
        return {'experiment':'MOTIF-THOUGHT-013','human_terminal_inspiration':'Full Measure Human Terminal v0.1',
                'original_phrase':'What if food and a community meal could connect?',
                'dialogue':talk,'source_unchanged':before==field.snapshot(),
                'oracle_is_synthetic':True,'external_authority':'NONE'}

if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
