"""Load exact same source-owner 013 fixtures without shadowing local 014 fixtures."""
import importlib.util
from pathlib import Path
path=Path(__file__).resolve().parent.parent/'thought-013'/'fixtures.py'
if not path.is_file():path=Path(__file__).resolve().parent.parent/'thought013'/'fixtures.py'
spec=importlib.util.spec_from_file_location('motif_source_013_fixture',path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
make_engine=mod.make_engine
possible_worlds=mod.possible_worlds
