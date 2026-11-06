"""Read-only bridge from THOUGHT-006 snapshots; no status or authority promotion."""
from field import FieldError, ThoughtField, ident, label


def import_ledger_nodes(snapshot: dict, field: ThoughtField, *, origin="legacy-ledger-snapshot") -> list[str]:
    """Import only named concepts, not unsupported inferred relations/pen claims.

    Refuses to mutate field on invalid input. Caller must supply an empty field.
    Existing 006 nodes are identifiers, *not* proof of distinct real referents.
    """
    if not isinstance(snapshot, dict) or snapshot.get("schema") != "motif.thought-ledger.snapshot.v1":
        raise FieldError("incompatible legacy snapshot")
    if field.concepts or field.expressions or field.manifestations:
        raise FieldError("import demands an empty thought field")
    nodes = snapshot.get("nodes")
    if not isinstance(nodes, list) or len(nodes) > 100:
        raise FieldError("invalid or oversized legacy node list")
    seen = set()
    for n in nodes:
        if not isinstance(n, dict) or set(n) != {"id", "label", "kind"}:
            raise FieldError("unexpected legacy node")
        ident(n["id"], "legacy node")
        label(n["label"], "legacy label")
        ident(n["kind"], "legacy kind")
        if n["id"] in seen:
            raise FieldError("duplicate legacy node")
        seen.add(n["id"])
    ident(origin, "import origin")
    for n in nodes:
        field.concept("legacy:" + n["id"], n["label"],
                      "Imported as a distinct legacy node; semantic equivalence not inferred", origin)
    return ["legacy:" + n["id"] for n in nodes]
