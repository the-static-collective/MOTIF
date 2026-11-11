# MOTIF FIELD-004 — THE UNSAID MOVE

A testable experimental kernel for **proposing the user's missing ideas before asking them to supply those ideas**. It operates on attributed image/sketch observations and an initial goal, and automatically infers alternative material roles, move-the-problem strategies, and compound support hypotheses.

- `engine.py` — deterministic, explainable hypothesis/strategy/probe generator.
- `vision_adapter.py` — **optional opt-in external** multimodal model intake; no image transfer by default and no real-model test performed.
- `run.py` — CLI using an offline anonymized fixture or (with consent) actual photos.
- `fixtures/anonymous_visual_packet.json` — generic synthetic descriptions, **no real photos, names, location or measurements**.
- `test_engine.py`, `test_vision_adapter.py` — authored scenario and mocked multimodal interface tests.
- `DESIGN.md` — experiment methods, limitations, safety and proposed blind study.

```sh
python -m unittest discover -v
python run.py --packet fixtures/anonymous_visual_packet.json
```

**Scientific status:** Authored reasoning rules on an authored fixture, **not** independently discovered affordances, autonomous image understanding, field-tested physics or a production MOTIF MCP skill. No automatic physical action.