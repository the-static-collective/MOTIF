"""Synthetic independent held fixtures; truths never go into the inquiry engine."""
from __future__ import annotations
import importlib.util
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent / 'thought-012' / 'fixtures.py'
if not SOURCE.is_file():
    SOURCE=Path(__file__).resolve().parent.parent / 'thought012' / 'fixtures.py'
_spec=importlib.util.spec_from_file_location('motif_thought012_fixture_source', SOURCE)
_mod=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
make_engine=_mod.make_engine


def possible_worlds(engine):
    """16 hypothetical worlds: venue+enable decide; van+food-storage are noise.

    Completely predeclared model, NOT mined from public or real-world records.
    """
    from inquiry import InquiryCycle
    dummy=InquiryCycle.__new__(InquiryCycle)
    dummy.engine=engine
    dummy.seed_pair=('m:food','m:meal')
    catalog=dummy._build_catalog()
    atoms=[x['atom'] for x in catalog]
    assert 'r:meal-needs-venue' in atoms and 'r:volunteers-enable-meal' in atoms
    worlds=[]
    for i in range(16):
        venue=bool(i & 1)
        enables=bool(i & 2)
        van=bool(i & 4)
        food=bool(i & 8)
        values={atom:True for atom in atoms}
        values.update({'r:meal-needs-venue':venue,
                       'r:volunteers-enable-meal':enables,
                       'r:meal-needs-van':van,
                       'r:food-storage':food})
        worlds.append({'id':f'hypothesis:{i:02}',
                       'decision':'YES' if venue and enables else 'NO',
                       'atoms':values})
    return worlds


def fixture_oracle(world, *, unknown=()):
    def ask(atom):
        if atom in unknown:return 'UNKNOWN'
        return world['atoms'][atom]
    return ask
