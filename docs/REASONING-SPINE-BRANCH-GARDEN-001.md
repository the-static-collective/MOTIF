# MOTIF Reasoning Spine 001 × Branch Garden

**Status:** conservative local research prototype. Nonmerged source data can influence a planning question without the branch code landing on main. No external-source code execution, method admission, outbound contact, model-weight change, or automatic merge.

## Two distinct abilities

**Access every visible experimental branch.** Run:

    python -m motif.cli branches --query "reciprocal"
    python -m motif.cli branches --all > /tmp/motif-branch-leads.json

The tool calls git ls-remote --heads origin. It inventories all currently visible remote branches, not only open PRs. The existing MOTIF living branch census workflow independently indexes public branch pointers every six hours. An offline dated census can be supplied with --census file.json but cannot authorize a fresh source fetch.

**Use nonmerged experiments without merging.** Run:

    python -m motif.cli inspect \
      --ref experiment/reciprocal-004-ecosystem-crosswire-20261112 \
      --path experiments/reciprocal-004/capability-passport.v1.json \
      --case examples/reason-spine-001.json > /tmp/motif-held-branch-influence.json

Inspect discovers the exact remote SHA, fetches the named head only into FETCH_HEAD, detects a moved head, and reads the JSON from that immutable commit via git show SHA:path. There is no checkout, import, code execution or merge. The recognized RECIPROCAL-004 passport becomes a held question-planning lens: two-doors can propose an opt-in question; reason-field remains a source-scoped idea; method-foundry is marked as a candidate, not an installed operator.

The recorded path, branch, commit, and content SHA-256 make the observation traceable. Other JSON schemas remain HOLD until individually reviewed. Reading a branch label is not proof its name describes a working capability.

## Six phases and five roles

OBSERVE → HYPOTHESIZE → PROBE → REVISE → PLAN → VERIFY.

- Explorer: enumerates human-authored hypotheses.
- Skeptic: identifies competing reports, missing evidence and contradictions.
- Architect: identifies possible held methods; cannot install or execute them.
- Historian: preserves source revisions, without duplicate votes from one root.
- Governor: ranks possible experiments and decides when to stop or ask.

The finite question scorer uses classical Shannon information gain, subtracting synthetic cost and risk proxies. Units are not calibrated real-world utilities. A declared human review is not authenticated truth. The engine returns HOLD, proposed test, or verification-needed recommendations, never physical actions.

## Compare without inventing outcomes

    python -m unittest discover -s tests -v
    python -m motif.cli compare --case examples/reason-spine-001.json
    python -m motif.cli verdict --evidence examples/merge-evidence-held.json

The comparison executes fixed-order classical, strong classical information-gain, and MOTIF cost-sensitive policies on identical finite cases. The actual pretrained LLM-alone and LLM+MOTIF cases remain NOT_RUN pending controlled real-model evaluation. No claims of transfer superiority or improved human learning.

## Branch dispositions

1. **PENCIL SOURCE POINTER:** every visible branch can be discovered by name + SHA, with no presumed semantics.
2. **HELD SOURCE DATA:** an explicitly pinned JSON source can influence a limited local reasoning plan, without importing source code.
3. **RECOMMEND MERGE REVIEW:** only after independent testing, proper comparison against strong classical controls, no known regressions, positive measured transfer, and project-owner review. Even this recommendation cannot merge.

A branch can remain useful indefinitely without merging. Unknown contracts, changed heads, contested evidence, or claims of auto-authority fail closed to HOLD.

## Integration boundaries and next research gates

- Real branch algorithms require individually reviewed method contracts and a controlled, no-secrets execution sandbox. This v1 intentionally does not run arbitrary unmerged code.
- JAR;VIS currently has a held source-passport reader, not an operational MOTIF reasoning interface. A local question UI and limited adapter need their own integration and tests.
- GRAFT donor admission and CANNON selection remain independent owner decisions.
- Understory, MEMENTO, Free Graph and planZ need separately reviewed event, memory, and plan interfaces rather than uncontrolled shared state.
- Evaluate representative real tasks (for example HUMKIN distribution and safely calibrated fence geometry) only after creating independently verifiable task data and matched baseline budgets.
- Existing PR stacks remain separate. This slice is an unmerged-to-main core, not a wholesale import of the research branches.

**Boundary:** branch access is not runtime execution. A program's existence is not evidence that it works. A successful demonstration is not permission or automatic promotion.
