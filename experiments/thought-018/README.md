# THOUGHT-018 — Model Research Director (staging)

This branch is a **source-owned staging slice**, stacked on THOUGHT-017. It currently commits an executable *source-only active-probe director* and six unit tests, plus CI. The complete model-assisted local prototype (trained Naive Bayes proposer, model-suggested test, independently chosen informative tests, actual THOUGHT-017 Python compilation + graph audit, optional local Ollama and 18 unit tests) exists as a separate downloadable research bundle in the originating conversation, **not yet committed into this branch**. Do not claim that this limited GitHub workflow verifies the complete local prototype.

The committed smoke has five explicitly authored switch-set candidate mechanisms. It chooses an informative 3-bit probe based on candidate disagreement, asks the independent finite oracle, and filters hypotheses. It compares against a predeclared fixed probe sequence. Both methods resolve 5/5 author-designed toy tasks; the active policy uses 5 queries and the fixed policy uses 12. That measures finite lookup queries, not a general reasoning advantage.

Run: `cd experiments/thought-018 && python -m unittest -v test_smoke.py`.

All results remain `QUESTION_ONLY`, `PEN UNCHANGED`, and `external_authority: NONE`. No live language model, code rewriting, external connections or source commits are triggered by this smoke. This is not ready to merge as the full THOUGHT-018 implementation; review the complete local bundle first.
