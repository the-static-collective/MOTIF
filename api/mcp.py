"""MOTIF native read-only MCP aperture.
A stateless HTTP adapter around the *original* MOTIF main Python modules.
It is NOT the unmerged Forest MCP v0.3/OAuth gateway, not a self-trained LLM,
and does not expose private sessions, arbitrary files, branch execution or writes.

Vercel: api/mcp.py is mounted at /api/mcp and rewritten as /mcp.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

from motif.reason_spine import CaseError, analyze, comparison, information_gain, validate_case
from motif.branch_garden import HoldError, Pointer, suggest, valid_ref, merge_verdict

PROTOCOLS = ("2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26")
DEFAULT_PROTOCOL = "2025-06-18"
MAX_BODY = 40_000
MAX_OUTPUT = 220_000
SERVICE = "motif-native-spine-readonly"
VERSION = "0.2.1"
GITHUB_BRANCHES = "https://api.github.com/repos/the-static-collective/MOTIF/branches"
CANONICAL_REPO = "the-static-collective/MOTIF"

CASE_SCHEMA = {
    "type": "object",
    "description": "MOTIF reason-case/v1: authored hypotheses and tests, not verified facts. Do not include secrets, personally identifying details or private records in public read-only service calls.",
    "additionalProperties": True,
}
TOOL_SPECS = [
    {
        "name": "motif_analyze_case",
        "description": "Run the ORIGINAL motif.reason_spine.analyze on a supplied bounded reason-case. Returns observed/declared witness contradictions, role receipts, rival models and an informative voluntary next probe, not factual truth. No live experiments, code execution or external actions.",
        "inputSchema": {
            "type": "object", "properties": {"case": CASE_SCHEMA},
            "required": ["case"], "additionalProperties": False,
        },
    },
    {
        "name": "motif_compare_policies",
        "description": "Actually execute three native MOTIF main policies on the SAME supplied synthetic/author-declared case: fixed-order classical, strong classical information gain, and MOTIF cost-sensitive spine. The real-LLM performance cells are NOT_RUN. No superiority is implied.",
        "inputSchema": {
            "type": "object", "properties": {"case": CASE_SCHEMA},
            "required": ["case"], "additionalProperties": False,
        },
    },
    {
        "name": "motif_information_gain",
        "description": "Calculate native classical Shannon information gain for one authored test over 1–32 bounded hypothesis predictions. This is a real computation, not a validation of those hypotheses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hypotheses": {"type": "array", "minItems": 1, "maxItems": 32, "items": {"type": "object"}},
                "test_id": {"type": "string", "minLength": 1, "maxLength": 100},
            },
            "required": ["hypotheses", "test_id"], "additionalProperties": False,
        },
    },
    {
        "name": "motif_merge_review",
        "description": "Execute original motif.branch_garden.merge_verdict against owner-supplied evidence gates; it can only recommend review. Never creates a PR, merges, promotes, writes or executes a branch.",
        "inputSchema": {
            "type": "object",
            "properties": {"evidence": {"type": "object"}},
            "required": ["evidence"], "additionalProperties": False,
        },
    },
    {
        "name": "motif_public_branch_leads",
        "description": "Read a SINGLE page of public MOTIF GitHub branch names and pinned head SHAs, then use native Branch Garden lexical source-lead selection. Branch name and source pointer never establish execution, correctness or merge authority. Pages are not automatically exhaustive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "maxLength": 100, "description": "Optional lexical search for branch names"},
                "page": {"type": "integer", "minimum": 1, "maximum": 50},
                "limit": {"type": "integer", "minimum": 1, "maximum": 30},
            },
            "additionalProperties": False,
        },
    },
]
for spec in TOOL_SPECS:
    spec["annotations"] = {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": spec["name"] == "motif_public_branch_leads",
    }
TOOLS_BY_NAME = {x["name"]: x for x in TOOL_SPECS}


def rpc_error(id_, code, message):
    return {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}


def result(id_, payload):
    return {"jsonrpc": "2.0", "id": id_, "result": payload}


def bounded_case(args):
    case = args.get("case")
    if not isinstance(case, dict):
        raise ValueError("'case' must be an object")
    if case.get("schema", "motif.reason-case/v1") != "motif.reason-case/v1":
        raise ValueError("Unknown case schema; use motif.reason-case/v1")
    validate_case(case)
    # Avoid extremely lengthy caller-provided witness labels and messages.
    # A source field in a model is not proof of that source's real identity.
    return case


def public_branch_leads(args):
    query = args.get("query", "")
    page = args.get("page", 1)
    limit = args.get("limit", 12)
    if not isinstance(query, str) or len(query) > 100:
        raise ValueError("query must be a short string")
    if type(page) is not int or not 1 <= page <= 50:
        raise ValueError("page must be 1–50")
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError("limit must be 1–30")
    url = GITHUB_BRANCHES + "?per_page=100&page=" + str(page)
    req = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json",
                      "User-Agent": "MOTIF-Native-Readonly-MCP/0.2"}
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            rows = json.loads(response.read(110_001))
    except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError) as exc:
        raise HoldError("Public GitHub branch source unavailable or rate limited: HOLD") from exc
    if not isinstance(rows, list) or len(rows) > 100:
        raise HoldError("Unexpected or excessive branch page: HOLD")
    heads = []
    seen = set()
    for row in rows:
        ref = row.get("name") if isinstance(row, dict) else None
        sha = row.get("commit", {}).get("sha") if isinstance(row, dict) and isinstance(row.get("commit"), dict) else None
        if not valid_ref(ref) or not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise HoldError("Invalid source pointer returned by remote: HOLD")
        if ref in seen:
            raise HoldError("Duplicate source pointer returned: HOLD")
        seen.add(ref)
        heads.append(Pointer(ref, sha, "github-public-api"))
    leads = (suggest(query, heads, limit=limit) if query.strip() else
             [p.as_dict() for p in sorted(heads, key=lambda p: p.ref)[:limit]])
    return {
        "schema": "motif.native-mcp.public-branch-leads/v1",
        "repository": CANONICAL_REPO,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "page": page,
        "page_size": len(rows),
        "possible_next_page": len(rows) == 100,
        "completeness": "SINGLE_GITHUB_PAGE_NOT_WHOLE_FOREST",
        "leads": leads,
        "source_only": True,
        "execution": "NONE",
        "merge": "NONE",
        "authority": "NONE",
        "note": "Public pointer discovery only. Query is lexical; no branches were read, executed, imported or promoted.",
    }


def call_tool(name, args):
    if not isinstance(args, dict):
        raise ValueError("MCP tool arguments must be an object")
    if name == "motif_analyze_case":
        if set(args) != {"case"}:
            raise ValueError("Expected only case")
        payload = analyze(bounded_case(args))
    elif name == "motif_compare_policies":
        if set(args) != {"case"}:
            raise ValueError("Expected only case")
        payload = comparison(bounded_case(args))
    elif name == "motif_information_gain":
        if set(args) != {"hypotheses", "test_id"}:
            raise ValueError("Expected hypotheses and test_id")
        test_id = args["test_id"]
        hypotheses = args["hypotheses"]
        if not isinstance(test_id, str) or not 1 <= len(test_id) <= 100:
            raise ValueError("test_id required (max 100 characters)")
        case = {"question": "Authored information-gain calculation",
                "goal": "Compare purely hypothetical test outcomes",
                "hypotheses": hypotheses, "tests": [{"id": test_id}]}
        validate_case(case)
        payload = {
            "schema": "motif.information-gain/v1",
            "test_id": test_id,
            "bits": round(information_gain(hypotheses, test_id), 8),
            "truth_status": "ASSUMED_EQUAL_PRIORS_AUTHOR_SUPPLIED_PREDICTIONS",
        }
    elif name == "motif_merge_review":
        if set(args) != {"evidence"} or not isinstance(args["evidence"], dict):
            raise ValueError("Expected evidence object")
        ev = args["evidence"]
        if len(ev) > 30:
            raise ValueError("Too many evidence gates")
        payload = merge_verdict(ev)
        payload["schema"] = "motif.merge-verdict/v1"
        payload["source_execution"] = "NONE"
    elif name == "motif_public_branch_leads":
        if set(args) - {"query", "page", "limit"}:
            raise ValueError("Unknown branch-leads arguments")
        payload = public_branch_leads(args)
    else:
        raise ValueError("Tool is not exposed; no execution or writes permitted")
    return payload


def tool_response(payload, error=False):
    # Include structuredContent for capable clients plus standard text content.
    # Vercel request metadata may be logged; no server-side transcript/session
    # storage or third-party user-data routing occurs for local computation.
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False)
    if len(text.encode("utf-8")) > MAX_OUTPUT:
        raise ValueError("Response would exceed bounded output size")
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": payload,
        "isError": error,
    }


def dispatch(envelope):
    if not isinstance(envelope, dict) or envelope.get("jsonrpc") != "2.0":
        return rpc_error(None, -32600, "Invalid JSON-RPC request")
    method = envelope.get("method")
    id_ = envelope.get("id")
    if "id" in envelope and (isinstance(id_, bool) or not isinstance(id_, (int, str))):
        return rpc_error(None, -32600, "Invalid request id")
    if not isinstance(method, str):
        return rpc_error(id_, -32600, "Invalid method")
    # Notifications are accepted only for the explicit lifecycle event.
    if "id" not in envelope:
        if method in {"notifications/initialized", "notifications/cancelled"}:
            return None
        return rpc_error(None, -32600, "Unexpected notification")
    params = envelope.get("params", {})
    if not isinstance(params, dict):
        return rpc_error(id_, -32602, "Parameters must be an object")
    if method == "initialize":
        proposal = params.get("protocolVersion", DEFAULT_PROTOCOL)
        chosen = proposal if proposal in PROTOCOLS else DEFAULT_PROTOCOL
        return result(id_, {
            "protocolVersion": chosen,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {
                "name": SERVICE,
                "version": VERSION,
                "description": "Native MOTIF main Reasoning Spine (read-only) + public source-only branch leads. No Forest sessions or code execution.",
            },
            "instructions": "This endpoint executes original MOTIF main Python reasoning policies on author-supplied cases. It provides no true causal verification, no personalized storage, no native branch execution and no merge authority. Do not send private data.",
        })
    if method == "ping":
        return result(id_, {})
    if method == "tools/list":
        return result(id_, {"tools": TOOL_SPECS})
    if method == "tools/call":
        name = params.get("name")
        if name not in TOOLS_BY_NAME:
            return rpc_error(id_, -32602, "Tool is unavailable: no writes or unreviewed execution")
        try:
            payload = call_tool(name, params.get("arguments", {}))
            return result(id_, tool_response(payload))
        except (CaseError, HoldError, ValueError, TypeError, KeyError) as exc:
            return result(id_, tool_response(
                {"status": "HOLD", "reason": str(exc)[:240], "tool": name,
                 "no_external_action": True}, error=True
            ))
    return rpc_error(id_, -32601, "Method not found")


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless HTTP adapter; no session, cookies or auth tokens."""
    server_version = "MotifNativeReadonly/0.2"
    sys_version = ""

    def log_message(self, fmt, *args):
        # Do not log caller-supplied hypotheses, report contents, remote query,
        # authorization headers, or tool request bodies.
        pass

    def _send(self, status, body, headers=None):
        raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/api/health", "/health"):
            return self._send(200, {
                "service": SERVICE, "version": VERSION, "status": "READY_READONLY",
                "mcp": "/mcp", "tools": len(TOOL_SPECS),
                "native_main_imports": True, "read_only": True, "sessions": False,
                "forest_oauth_gateway": "NOT_CONNECTED", "method_executor": "NOT_CONNECTED",
            })
        if path in ("/api/mcp", "/mcp"):
            return self._send(405, {"error": "POST_JSON_RPC_REQUIRED"}, {"Allow": "POST"})
        return self._send(404, {"error": "NOT_FOUND"})

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ("/api/mcp", "/mcp"):
            return self._send(404, {"error": "NOT_FOUND"})
        if "application/json" not in self.headers.get("Content-Type", "").lower():
            return self._send(415, {"error": "JSON_REQUIRED"})
        length = self.headers.get("Content-Length", "")
        if not length.isdigit() or not 1 <= int(length) <= MAX_BODY:
            return self._send(413, {"error": "BODY_LIMIT_40KB"})
        try:
            message = json.loads(self.rfile.read(int(length)))
            response = dispatch(message)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            response = rpc_error(None, -32700, "Invalid JSON")
        if response is None:
            return self._send(202, b"")
        return self._send(200, response)

    def do_DELETE(self):
        self._send(405, {"error": "STATELESS_NO_SESSION"}, {"Allow": "POST"})

    def do_OPTIONS(self):
        self._send(405, {"error": "NO_BROWSER_CORS"}, {"Allow": "GET, POST"})
