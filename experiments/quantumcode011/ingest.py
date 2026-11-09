"""QC-011: Human/vision-annotated JSON replay intake and read-only preview.

This is the *actual file intake* edge. It does NOT decode MP4, download
streaming gameplay, infer unseen states, run a model or transmit to reLATTE.

Only content the user has rights to supply should be annotated. The default
output is a read-only private preview; sending requires a different owner.
"""
from __future__ import annotations
from dataclasses import fields
from pathlib import Path
import json
import sys

from game_replay import (
    GameState,Episode,Replay,trajectory,relatte_preview,
)

MAX_BYTES=2_000_000
MAX_EPISODES=400
EVENT_KEYS={f.name for f in fields(Episode)}
STATE_KEYS={f.name for f in fields(GameState)}


def strict(expected,data):
    if not isinstance(data,dict) or set(data)!=expected:
        raise ValueError("Unexpected or incomplete annotated event keys")
    return data


def parse_state(payload):
    p=strict(STATE_KEYS,payload)
    if not (isinstance(p["resources"],list)
            and isinstance(p["capabilities"],list)
            and isinstance(p["hazards"],list)
            and all(isinstance(x,list) and len(x)==2
                    and isinstance(x[0],str) for x in p["resources"])):
        raise ValueError("Malformed resources or visibility lists")
    result=GameState(
        tuple((k,v) for k,v in p["resources"]),
        tuple(p["capabilities"]),tuple(p["hazards"]),
        p["location"],p["clock_tick"],
    )
    result.validate()
    return result


def parse_bundle(data):
    keys={"schema","game","provenance","consent_for_derived_research",
          "episodes"}
    strict(keys,data)
    if data["schema"]!="motif.annotated-gameplay/v0":
        raise ValueError("Unsupported trace schema")
    if not isinstance(data["episodes"],list) or not 0<len(data["episodes"])<=MAX_EPISODES:
        raise ValueError("Require bounded nonempty annotation list")
    events=[]
    for entry in data["episodes"]:
        p=strict(EVENT_KEYS,entry)
        result=Episode(
            **{k:v for k,v in p.items() if k not in ("before","after","tags")},
            before=parse_state(p["before"]),
            after=parse_state(p["after"]),
            tags=tuple(p["tags"]),
        )
        result.validate()
        events.append(result)
    replay=Replay(data["game"],tuple(events),data["provenance"],
                  data["consent_for_derived_research"])
    replay.validate()
    return replay


def read_bundle(path):
    p=Path(path)
    if p.stat().st_size>MAX_BYTES:
        raise ValueError("Too much unreviewed source data")
    raw=p.read_bytes()
    if len(raw)>MAX_BYTES:
        raise ValueError("Too much source data")
    return parse_bundle(json.loads(raw.decode("utf-8")))


def preview_bundle(path):
    replay=read_bundle(path)
    crossing=relatte_preview(replay)
    return {
        "source":str(Path(path).name),
        "replay_pin":replay.pin,
        "replay":trajectory(replay),
        "crossing_status":crossing["status"],
        "crossing_packet_sha256":crossing.get("packet_sha256"),
        "signed":False,
        "sent":False,
        "admitted":False,
        "actual_gameplay_video_decoded":False,
        "real_world_actions":0,
    }


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python ingest.py annotated-gameplay.json")
    print(json.dumps(preview_bundle(sys.argv[1]),sort_keys=True,indent=2))
