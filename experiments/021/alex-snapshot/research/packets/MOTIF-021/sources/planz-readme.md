# planZ

**Global plan census, archaeology, and disposition for the Static Collective.**

planZ exists to answer one bounded question:

> **What did we say we would do, what became of it, and what—if anything—still remains?**

This repository is not a master authority over project-local plans. It is a provenance-preserving index and recovery surface.

The first full census is being developed as **PLANZ-001**.

## JAR;VIS read-only attention feed

A bounded, [machine-readable editorial plan index](public/attention-v1.json) now exposes selected cross-project OPEN plans, source issue pointers, blockers, and the next human review gate to JAR;VIS. It is **not** the completed global census, a live provider network, a task executor or any project’s authority. See [Attention 001](docs/ATTENTION-001.md); `npm test` validates the public contract.

## Offline JAR;VIS return triage

A locally exported, manually inspected JAR;VIS plan-origin candidate can be checked using `npm run triage -- /path/to/packet.json`. This validates format, source plan, exact snapshot, and explicit HOLD boundaries. It does **not** make a field claim or update any issues. See [receiver protocol](docs/RETURN-TRIAGE-001.md).
