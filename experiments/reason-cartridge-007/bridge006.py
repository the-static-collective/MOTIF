"""Bridge verified new method into original REASON-006 evidence ledger."""
from __future__ import annotations
import sys
from pathlib import Path
from hashlib import sha1
from market import validate_packet
from compiler import HOLD, digest

PATH = Path(__file__).resolve().parents[1] / "reason-cartridge-006" / "commonwealth.py"
PIN = "4f0e897b19e658f5f01a0a2e91a472ad023e1b8f"

def current_pin():
    raw = PATH.read_bytes()
    value = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if value != PIN:
        raise HOLD("Commonwealth code changed")
    return value

current_pin()
sys.path.append(str(PATH.parent))
from commonwealth import Ledger

def transfer(raw, receiver):
    document = validate_packet(raw,receiver)
    report = document["receipt"]
    if report["winning_kind"] != "COMPILE_SENSOR" or (
        report["incorrect_or_abstained"] != 0 or
        report["marginal_verified_savings_points"] <= 0
    ):
        raise HOLD("No positively verified new method")
    proof = {"method":document["source_method"]["checksum_sha256"],
             "review":report["independent_certification_digest"],
             "portfolio":digest(document["portfolio"])}
    ledger = Ledger()
    original = ledger.add("DISCOVERY","READ_ONLY_METHOD",proof,"SYNTHETIC_GAIN",True)
    duplicate = ledger.repeat(original)
    if duplicate["score"] != 0:
        raise HOLD("Repeated method received new credit")
    return {"prior_owner":current_pin(),"new_credit":original["score"],
            "repeated_credit":duplicate["score"],
            "world_facts":ledger.summary()["new_source_facts"],
            "external_execution":False}
