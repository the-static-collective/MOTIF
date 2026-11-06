"""Reproduce non-fungible 'home' meanings and simultaneous geometric appearances."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from field import ThoughtField, canonical


def build(path):
    f = ThoughtField(path)
    f.expression("expr:home", "home", "example:human-utterance", "Ambiguous word in discussion")
    f.concept("concept:shelter", "Home", "Home as physical shelter", "example:concept-author")
    f.concept("concept:belonging", "Home", "Home as belonging or shared care", "example:concept-author")
    f.propose_referent("ref:shelter", "expr:home", "concept:shelter",
                       "Word could mean physical shelter", "example:hypothesis")
    f.propose_referent("ref:belonging", "expr:home", "concept:belonging",
                       "Word could mean emotional belonging", "example:hypothesis")
    f.manifest("m:shelter-logistics", "concept:shelter", "housing logistics", "resource")
    f.manifest("m:shelter-values", "concept:shelter", "community values", "condition")
    f.manifest("m:belonging-values", "concept:belonging", "community values", "goal")
    f.manifest("m:shelter-next", "concept:shelter", "future concrete planning",
               "requirement", "CONCRETE_PENCIL", parent_id="m:shelter-logistics")
    f.view("v:association", "association", "Exploratory associations")
    f.view("v:dependency", "dependency", "Different geometry over same concepts")
    f.view("v:hex", "flower_hex", "Optional lattice as drawing, not evidence")
    f.view("v:nolayout", "NONE", "Semantic-only reasoning")
    f.place("p:assoc-a", "m:shelter-logistics", "v:association", -1, 1, "appearance A")
    f.place("p:assoc-b", "m:shelter-logistics", "v:association", 2, -0.5, "same manifestation second appearance")
    f.place("p:dep", "m:shelter-logistics", "v:dependency", 0, 2, "dependency viewpoint")
    f.place("p:hex", "m:shelter-values", "v:hex", 0.5, 0.866, "flower lattice sketch")
    f.place("p:none", "m:belonging-values", "v:nolayout", None, None, "no geometry needed")
    f.propose_equivalence("eq:home-meanings", "concept:shelter", "concept:belonging",
                          "example:analogy", "The two senses might overlap; they remain distinct")
    before = f.semantic_snapshot()
    f.move("p:assoc-a", 1000, -500, "Reproject geometry without changing beliefs", expected_revision=1)
    f.remove_placement("p:hex", "Alternative map no longer useful")
    assert canonical(before) == canonical(f.semantic_snapshot())
    replay = ThoughtField(path)
    assert replay.snapshot() == f.snapshot()
    return {
        "status": "PROPOSAL_ONLY", "events": len(f.history()),
        "distinct_concepts_with_same_label": len([c for c in f.concepts.values() if c["label"] == "Home"]),
        "ambiguous_word_referent_candidates": len(f.referents),
        "shelter_manifestations": len(f.occurrences("concept:shelter")["manifestation_ids"]),
        "shelter_active_placements": len(f.occurrences("concept:shelter")["placements"]),
        "semantic_invariant_under_layout_change": canonical(before) == canonical(f.semantic_snapshot()),
        "exact_replay": replay.snapshot() == f.snapshot(),
        "equivalence_status": f.equivalence_proposals["eq:home-meanings"]["status"],
        "effective_external_authority": "NONE",
        "semantic_snapshot": f.semantic_snapshot(),
        "placement_snapshot": f.snapshot()["placements"],
    }


def main():
    with TemporaryDirectory() as d:
        result = build(Path(d) / "thought-events.jsonl")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2))
