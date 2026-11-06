"""Portable, local-HOLD geometry evidence, not authorization or source identity."""
import hashlib
import json
from math import isfinite

from geometry import flower, propose_centers


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def export_cartridge(observed, max_ring=2, radius=1.0) -> dict:
    """Create a reproducible evidence envelope. Integrity != authenticity."""
    if type(max_ring) is not int or not (0 <= max_ring <= 8):
        raise ValueError("bounded integer max_ring must be in 0..8")
    if not isinstance(radius, (float, int)) or not isfinite(radius) or radius <= 0:
        raise ValueError("finite positive circle radius required")
    original = list(observed)
    if any(not isinstance(p, (tuple, list)) or len(p) != 2 or
           any(type(n) is not int for n in p) for p in original):
        raise ValueError("observations must be pairs of exact integer coordinates")
    nodes = {tuple(p) for p in original}
    if not nodes <= set(flower(max_ring)):
        raise ValueError("observed center outside declared search field")
    payload = {
        "schema": "motif.geometry.flower.v1",
        "construction": "equal-radius-circle-intersections-on-anchored-axial-lattice",
        "max_ring": max_ring,
        "circle_radius": float(radius),
        "observed": [list(p) for p in sorted(nodes)],
        "proposals": propose_centers(nodes, max_ring, radius),
        "admission": "HOLD",
        "effective_authority": "NONE",
        "remark": "Checksum proves payload consistency only, not its author or worldly truth.",
    }
    return {"payload": payload, "sha256": hashlib.sha256(_canonical(payload)).hexdigest()}


def verify_cartridge(cartridge: dict) -> bool:
    """Re-derive proposed centers and checksum; never grant admission."""
    try:
        payload = cartridge["payload"]
        supplied = cartridge["sha256"]
        expected = export_cartridge(payload["observed"],
                                    payload["max_ring"],
                                    payload["circle_radius"])
        return isinstance(supplied, str) and supplied == expected["sha256"] \
            and _canonical(payload) == _canonical(expected["payload"])
    except (KeyError, ValueError, TypeError, OverflowError):
        return False
