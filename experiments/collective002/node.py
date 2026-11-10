"""Loopback-only, independently running MOTIF + TranchNode-inspired trial nodes."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from urllib.request import Request, urlopen

from protocol import (MAX_BYTES, MAX_CARDS, AppendOnlyLedger, canonical, digest,
                      import_cards, infer_path, sign, validate_card, verify)


def load_config(path):
    config = json.loads(Path(path).read_text())
    if not all(isinstance(config.get(x), str) and config[x] for x in ("id", "scope", "secret")):
        raise ValueError("missing node identity, scope, or demo secret")
    return config


def local_cards(config):
    cards = []
    for raw in config.get("claims", []):
        card = {"kind": "source", "source_scope": config["scope"], "origin": config["id"],
                "fact_id": raw["fact_id"], "from": raw["from"], "to": raw["to"],
                "polarity": raw["polarity"], "epistemic_state": "asserted"}
        cards.append(validate_card(card, config["id"]))
    return cards


def export(config, request_envelope):
    req = request_envelope.get("body", {})
    requester = req.get("requester") if isinstance(req, dict) else None
    key = config.get("trusted_requesters", {}).get(requester)
    if not isinstance(key, str):
        raise ValueError("untrusted requester")
    req = verify(request_envelope, key)
    if (set(req) != {"schema", "requester", "recipient", "request_id", "purpose"}
        or req["schema"] != "motif.collective002.request.v1"
        or req["recipient"] != config["id"] or req["purpose"] != "source-export"
        or not isinstance(req["request_id"], str) or len(req["request_id"]) != 32):
        raise ValueError("invalid or misrouted request")
    allowed = config.get("grants", {}).get(requester, [])
    disclosed = [card for card in local_cards(config) if card["fact_id"] in allowed]
    if len(disclosed) > MAX_CARDS:
        raise ValueError("too many exported cards")
    # No transfer of ungranted cards, identifiers, existence, or counts.
    return sign({"schema": "motif.collective002.reply.v1", "issuer": config["id"],
                 "recipient": requester, "request_id": req["request_id"],
                 "disclosure": "named-recipient", "cards": disclosed}, config["secret"])


def request_peer(config, peer_id):
    peer = config["peers"][peer_id]
    address = peer["url"]
    if not address.startswith("http://127.0.0.1:"):
        raise ValueError("trial transport restricted to loopback")
    nonce = secrets.token_hex(16)
    req = sign({"schema": "motif.collective002.request.v1", "requester": config["id"],
                "recipient": peer_id, "request_id": nonce, "purpose": "source-export"}, config["secret"])
    payload = canonical(req)
    with urlopen(Request(address + "/export", data=payload,
                         headers={"Content-Type": "application/json"}, method="POST"), timeout=2) as response:
        if response.status != 200:
            raise ValueError("peer refused request")
        wire = response.read(MAX_BYTES + 1)
    if len(wire) > MAX_BYTES:
        raise ValueError("oversized response")
    reply = verify(json.loads(wire), peer["secret"])
    if (set(reply) != {"schema", "issuer", "recipient", "request_id", "disclosure", "cards"}
        or reply["schema"] != "motif.collective002.reply.v1"
        or reply["issuer"] != peer_id or reply["recipient"] != config["id"]
        or reply["request_id"] != nonce or reply["disclosure"] != "named-recipient"
        or not isinstance(reply["cards"], list) or len(reply["cards"]) > MAX_CARDS):
        raise ValueError("response substitution or invalid schema")
    cards = [validate_card(card, peer_id) for card in reply["cards"]]
    # We attest only the peer's statement + toy MAC, not real-world provenance.
    return cards, {"peer": peer_id, "message_digest": digest(reply), "cards": len(cards)}


def query(config, start, goal, ledger_path, *, peers=True):
    ledger = AppendOnlyLedger(ledger_path)
    ledger.replay()
    cards = local_cards(config)
    routes = []
    if peers:
        for peer_id in sorted(config.get("peers", {})):
            received, route = request_peer(config, peer_id)
            cards.extend(received)
            routes.append(route)
    nodes = import_cards(cards, config["scope"])
    local_only = infer_path(import_cards(local_cards(config), config["scope"]),
                            start, goal, config["scope"])
    result = infer_path(nodes, start, goal, config["scope"])
    # No claim of direct observation or independent signature; proof-by-links is
    # conditional on admitted, asserted toy statements.
    packet = {"schema": "motif.collective002.answer.v1", "node": config["id"],
              "local_scope": config["scope"], "question": {"from": start, "to": goal},
              "local_isolated_status": local_only["status"],
              "outcome": result, "source_nodes": nodes, "source_count": len(nodes),
              "network_receipts": routes, "external_authority": "NONE",
              "real_world_claim": False, "tranch_kernel_accepted": False,
              "source_authentication": "PRE_SHARED_TOY_HMAC_NOT_PUBLIC_SIGNATURE"}
    packet["packet_digest"] = digest(packet)
    ledger.append("source_reception", {"question": packet["question"],
             "sources": [{"id": n["id"], "source_origin": n["content"]["transmitted_statement"]["origin"]} for n in nodes]})
    ledger.append("inference_proposal", {"packet_digest": packet["packet_digest"],
            "status": result["status"], "evidence_ids": result["evidence_ids"],
            "tensions": result["tensions"], "adopted": False})
    return packet


def make_handler(config):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path != "/health":
                self.send_error(404)
                return
            raw = canonical({"status": "up", "id": config["id"]})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            if self.path != "/export":
                self.send_error(404)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 1 or size > MAX_BYTES:
                    raise ValueError("bad message size")
                envelope = json.loads(self.rfile.read(size))
                result = export(config, envelope)
                raw = canonical(result)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                self.send_error(403, "unauthorized or malformed request")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
    return Handler


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    server = sub.add_parser("serve")
    server.add_argument("--config", required=True)
    server.add_argument("--port", required=True, type=int)
    client = sub.add_parser("query")
    client.add_argument("--config", required=True)
    client.add_argument("--ledger", required=True)
    client.add_argument("--from", dest="start", required=True)
    client.add_argument("--to", dest="goal", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.command == "serve":
        ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(config)).serve_forever()
    else:
        print(json.dumps(query(config, args.start, args.goal, args.ledger), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
