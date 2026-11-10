"""Three REAL separate OS processes, three disjoint toy observations."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def build(tmp, *, with_c=True, conflict=False, withhold_b=False):
    ports = {i: free_port() for i in "abc"}
    secrets = {i: "research-only-secret-" + i for i in "abc"}
    data = {"a": [{"fact_id": "a1", "from": "A", "to": "B", "polarity": "edge"}],
            "b": [{"fact_id": "b1", "from": "B", "to": "C", "polarity": "edge"}],
            "c": [{"fact_id": "c1", "from": "C", "to": "D", "polarity": "edge"}]}
    if conflict:
        data["c"].append({"fact_id": "c2", "from": "B", "to": "C", "polarity": "not_edge"})
    paths = {}
    for i in "abc":
        config = {"id": i, "scope": "private-" + i, "secret": secrets[i],
                  "claims": data[i], "trusted_requesters": {j: secrets[j] for j in "abc" if j != i},
                  "grants": {"a": [x["fact_id"] for x in data[i]] if i != "b" or not withhold_b else []},
                  "peers": {j: {"url": f"http://127.0.0.1:{ports[j]}", "secret": secrets[j]}
                            for j in "bc" if i == "a" and (j != "c" or with_c)}}
        path = Path(tmp) / f"{i}.json"
        path.write_text(json.dumps(config))
        paths[i] = path
    return ports, paths


def execute(*, with_c=True, conflict=False, withhold_b=False):
    with tempfile.TemporaryDirectory(prefix="collective002-") as tmp:
        ports, paths = build(tmp, with_c=with_c, conflict=conflict, withhold_b=withhold_b)
        processes = []
        try:
            for i in "abc":
                processes.append(subprocess.Popen([sys.executable, str(HERE / "node.py"), "serve",
                                  "--config", str(paths[i]), "--port", str(ports[i])],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            for i in "abc":
                for attempt in range(60):
                    try:
                        with urlopen(f"http://127.0.0.1:{ports[i]}/health", timeout=.1) as r:
                            if json.load(r)["id"] == i:
                                break
                    except Exception:
                        time.sleep(.05)
                else:
                    raise RuntimeError("independent peer process failed to start")
            run = subprocess.run([sys.executable, str(HERE / "node.py"), "query",
                     "--config", str(paths["a"]), "--ledger", str(Path(tmp) / "a-events.jsonl"),
                     "--from", "A", "--to", "D"], capture_output=True, text=True, check=True, timeout=8)
            packet = json.loads(run.stdout)
            # Verify that storage persisted, is per-node and was independently replayed.
            from protocol import AppendOnlyLedger
            events = AppendOnlyLedger(Path(tmp) / "a-events.jsonl").replay()
            return {"processes": len(processes), "events_replayed": len(events),
                    "result": packet}
        finally:
            for proc in processes:
                proc.terminate()
            for proc in processes:
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)


if __name__ == "__main__":
    print(json.dumps(execute(), indent=2, sort_keys=True))
