# COLLECTIVE-002 — Three Independent TranchNode-Inspired MOTIF App Nodes

**Status: research-only executable seam.** This is not a released mobile app, a production peer-to-peer network, or an implementation of the TranchNode kernel. The server/CLI pair is a replaceable app-node sketch written in Python 3.10+ standard library.

## Research question

Can three independently running processes with disjoint private evidence answer a bounded graph-reachability question that none of their isolated local knowledge bases can answer, while refusing forbidden disclosures, unverifiable substitutions, forged messages, and unresolved contradictions? Does the network beat classical inference given the same combined evidence?

## Concrete trial

A privately asserts A→B and asks whether A→D is reachable. B privately asserts B→C; C privately asserts C→D. Each node runs as an independent operating-system process on its own loopback HTTP port and with its own private assertions. No pooled mock reasoning model substitutes for communication.

A separately requests evidence from B and C. Donors evaluate named-recipient, fact-by-fact grants, then transmit HMAC-protected, nonce-bound statements. A imports each statement into its own local scope as a new source-shaped projection with explicit original scope and origin. It does not create cross-scope TranchNode edges or inherit the donor's witness status.

A performs deterministic classical BFS, emits an inference *proposal* with three specific supporting evidence IDs, and saves an experimental append-only hash-chain receipt. No external action, automatic admission, or silent overwrite.

## Reproduction

From experiments/collective002:

    python -m unittest discover -s . -p 'test_*.py' -v
    python demo.py
    python benchmark.py

All tests require only local Python; no API credentials, paid services, or mobile device.

## Acceptance and falsification matrix

| Control | Expected |
|---|---|
| Three separate processes and all three granted facts | PATH_SUPPORTED_BY_ASSERTIONS; A→B→C→D |
| Isolated A with its private assertions | UNKNOWN_INSUFFICIENT_EVIDENCE |
| C excluded from request set | UNKNOWN_INSUFFICIENT_EVIDENCE |
| B grants no access to its assertion | UNKNOWN_INSUFFICIENT_EVIDENCE |
| C contradicts B→C | HOLD_CONTRADICTION; contested sources retained |
| Wrong HMAC, misrouted reply, wrong peer or request ID | Refused |
| Duplicate forwarded card | One source ID, not duplicated evidence |
| Tampered local event log | Replay integrity failure |
| Strong classical BFS with the *same* pooled transmitted facts | **Ties the network** |

## Source-owned architectural guardrails

Read the canonical source: the-static-collective/tranchnode INVARIANTS.md, ONTOLOGY.md, PROJECTION_COVENANT.md. This research seam does not implement its event kernel, RFC 8785 canonicalization, globally authoritative provenance, authenticated peer public keys, revocation, full privacy semantics, or a real consent UI. There is no claim of compatibility with canonical TranchNode accepted events. These source-shaped projections are experiments only.

SHA-256 packet digests do not verify a source's truth. HMAC with pre-shared toy secrets does not give independent asymmetric signatures: a verifier holding the key can impersonate its peer. The donor does not store a replay-prevention cache. Loopback-only HTTP is not a production secure transport. Do not deploy on an untrusted network or use it to exchange personal information.

This is an infrastructure-feasibility result, not emergent general intelligence. The synthetic world and participant configurations are prepared by an orchestration harness. Local A fails for lack of distributed evidence; the network succeeds only with authorized additional evidence. Classical central BFS with identical pooled facts succeeds too. No information-theoretic or reasoning advantage over equal-information controls is demonstrated.

## Next falsifier — COLLECTIVE-003

Integrate a real TranchNode validated event kernel and COLLECTIVE-001 proof-carrying answer format, with durable peer identity, asymmetric signatures, revocation, capability-scoped disclosures, independently authored hidden-information tasks, transport fault injection, and many frozen held-out trials. Compare network cost, accuracy, and privacy versus equally resourced centralized and classical distributed algorithms before claiming an intelligence gain.
