# QC-011 — SURVIVAL RPG REPLAY GRAMMAR
## Teach MOTIF to interpret gameplay as sequences of consequential action

**Research-only draft, stacked on QC-010.** This implementation does not download, decode, or watch a gameplay video, run a vision model, produce an AI-trained policy, operate a game, send a reLATTE crossing, or provide real-world survival guidance. It implements the *trace ingestion and semantic replay seam* that those later actions would require.

## Why use survival games?

They are useful **instrumented fictional laboratories**. A game repeatedly exposes states, resource constraints, actions, outcomes and delayed costs. People can fail, improvise, retry, craft capabilities, preserve scarce supplies, trade between immediate and future needs and learn policies with a comparatively low real-world cost.

The lesson is not "game health mechanics describe a human body." The useful knowledge is **action-network grammar**: how a choice changes resources and the set of future choices. Game data must retain the *game-only* domain label and cannot silently become medical, fire, cold-weather or food safety advice.

The Last of Us offers dramatic tradeoffs, scarcity, human relations and consequential story choices, but it is not a deep general physical simulator. PlayStation describes the series as action-adventure, rather than a traditional survival RPG. [PlayStation official](https://www.playstation.com/en-gb/the-last-of-us/).

For controlled survival mechanics, **The Long Dark** explicitly tracks cold, hunger, thirst, fatigue, consumption of calories and time: [official Survival Mode](https://www.thelongdark.com/survival-mode/). **Project Zomboid** offers deeper systems for long-term resource, skills and environment simulation, with documented Lua modding support: [Steam overview](https://store.steampowered.com/app/108600/Project_Zomboid/). Minecraft is especially useful for instrumentation of crafting, acquisition and constructing persistent new capabilities; prior Static Collective experiments have reportedly explored real Minecraft gameplay crossing, but no such run was independently fetched or revalidated for this prototype.

The best curriculum mixes:
1. **Mechanics-first:** The Long Dark or Project Zomboid for visible, falsifiable resource and environment transitions.
2. **Capability composition:** Minecraft for tools, shelter and future affordances, ideally from game telemetry rather than inferred video frames.
3. **Human-scale narrative:** The Last of Us for scarce-component tradeoffs, relationships, risk, sacrifice and priority changes, treating author-scripted outcomes differently from open-ended world mechanics.
4. **Real-world reality cuts:** separate consented practical experiences such as resource reuse and offline improvisation; game claims remain analogies until independently verified for relevant physical conditions.

## Concrete architecture

```text
USER-SUPPLIED CLIP or LIVE GAME TELEMETRY
        │
  annotation/vision subsystem (NOT BUILT)
        │
 timecoded before/action/after observations
        │
  local, bounded annotated JSON input (BUILT)
        │
 validate rights, game scope, time and contiguous transitions
        │
 game-local event and capability graph (BUILT)
        │
 compare before/after:
   what was spent?
   what capability was gained/lost?
   what hazard appeared or disappeared in the game?
   which causal explanations remain hypothetical?
        │
 preserve conflicting outcomes and next questions (BUILT)
        │
 reLATTE HOLD-only packet PREVIEW (BUILT)
        │
 FUTURE receiver verifies foreign provenance & admission (NOT BUILT)
        │
 optional reviewed MOTIF game-specific cartridge (NOT BUILT)
        │
 cross-domain real-world validation gate (NOT BUILT)
```

This order is deliberate: **reLATTE is a sovereign crossing substrate, not an all-purpose video decoder or a machine for automatically certifying interpretations.** MOTIF owns its source-domain interpretation. reLATTE owns any actual transport/verification/admission, when separately implemented and explicitly approved.

### What the prototype has

**`game_replay.py`**
- Strict, source-identified `Episode` of `before → action → after`, clip-second cut, outcome, source class, certainty, rights/annotation status, tags and claimed reason.
- `GameState` tracks *observed game* resources, capabilities, hazards, location and tick. The data model does not represent an observed transition as a proven causal mechanism.
- `Replay` requires one declared game per stream, unique IDs, non-backdated time and contiguous verified state transitions. Hidden or missing event boundaries refuse ingestion rather than inventing state.
- `interpret()` computes factual **game-only** inventory expenditure, resource gains, created/lost capabilities and introduced/resolved in-game hazards. It never asserts how safe a similar act is outside the game.
- `derive_rules()` preserves *both* success and failure and contradictory outcomes for the same named action. Proposes **candidate game correlations**, not reliable causal policy.
- `next_questions()` turns new capabilities, failed actions, uncertain vision evidence and conflicting traces into useful follow-up questions.
- `relatte_preview()` generates a SHA256-pinned proposal with an explicit `HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW`. It is **unsigned, unsent, unadmitted and has no effects**. If derived-research consent is absent, it refuses even to form the derived packet. It is **not a native signed reLATTE envelope**.
- Three researcher-authored, **entirely fictional** demos: Minecraft-like crafting/shelter, Last-of-Us-like first-aid resource tradeoff, Long-Dark-like clothing and cold-indicator change with inconclusive causal attribution. None are scraped from actual playthroughs.

**`ingest.py`**
- Accepts an actual local **annotated JSON file**, size capped at 2 MB and 400 annotated episodes, with explicit schema, rights status and consent.
- Strictly refuses unknown keys, malformed state, unsupported status, mixed-game mechanics and discontinuous event chains. Never downloads a video URL, runs external commands, reads user account data or sends a crossing.
- Returns a readable local preview with source hash, capabilities, resource flow, follow-up questions and separate reLATTE owner-review status.

**`example_annotation.json`**
- A deliberately **fictional** two-step Last-of-Us-style resource-choice trace. The game title is a reference to a style of play, not a claim to contain actual gameplay data, narrative, frames or licensed footage.

**`test_game_replay.py`, `test_ingest.py`**
- 47 tests covering game-only domain isolation, capability gains, inventory expenditure, causal uncertainty, alternative explanations, rights/consent, replay integrity, conflicting outcomes, refusal of unapproved video/URL claims and reLATTE HOLD-only packets.

### Reproduce

Python 3.11, standard library only:

```sh
cd experiments/quantumcode011
python -m unittest -v test_game_replay.py test_ingest.py
python game_replay.py
python ingest.py example_annotation.json
```

GitHub workflow: `.github/workflows/quantum-code-011.yml`.

## Next proof with *actual* gameplay

A real playthrough must be provided or accessed with appropriate rights and adequate provenance. Ideally the first source is **native game telemetry**, because it already records state transitions. For a Last-of-Us playthrough, a later multimedia/vision subsystem would have to segment a user-supplied recording, identify action intervals, distinguish confirmed visible facts from unreliable interpretation, and have a human verify ambiguities. The full video need not be copied into reLATTE; transport a small consented, source-pinned event graph or derived cartridge rather than publishing someone else's game footage.

Only then can MOTIF attempt **prediction from partial state**, propose a missing relevant question, and compare to held-out gameplay with competent controls. The first real benchmark should include at least one outcome the agent predicted incorrectly, rather than cherry-picked success clips.

Do not treat gameplay rule knowledge as transferable physiological/clinical truth. A game may approximate temperature, time, calorie budgets or crafting costs, but **real humans, weather, water, animals and construction materials are not governed by those game equations**.

## Bounded research results and missing capabilities

This stage demonstrates deterministic conversion of **explicitly annotated** before/action/after game episodes into a source-scoped capability ledger and a reviewed crossing proposal. It does not demonstrate automatic video understanding, experience replay from actual games, a trained policy, semantic generalization to new games, stronger-than-classical planning, reliable survival coaching, a real crossing, or real-world environmental action.
