"""Local, dependency-free adapter for MOTIF MCP tools in a Responses function loop.

This is NOT an MCP client, an authentication provider, or a deployed mobile app.
The host supplies a trusted transport and keeps credentials out of model context.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

# Explicit source-reviewed allowlists. Newly indexed branches never gain tool authority.
READ_TOOLS = frozenset({
    "catalog_cartridges", "select_methods", "resume_session", "list_sessions",
    "reflect_session", "forest_goals", "forest_catalog", "forest_inspect_source",
    "forest_route", "forest_resume_trial", "forest_list_trials",
})
# These mutate server state (or may execute a native experiment). UI-only, never
# automatically surfaced as model-callable tools in ChatGPT plan-usage mode.
REVIEW_TOOLS = frozenset({
    "start_session", "record_feedback", "execute_reviewed", "reopen_session",
    "forest_start_trial", "forest_feedback", "forest_execute_reviewed",
})
ALL_TOOLS = READ_TOOLS | REVIEW_TOOLS
PREFIX = "motif__"
MAX_ARGUMENT_BYTES = 32_768


class BridgeError(ValueError):
    """Refused tool, invalid payload, or missing human review."""


def _canonical(value: Any) -> bytes:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise BridgeError("tool arguments must be JSON values") from exc
    if len(raw) > MAX_ARGUMENT_BYTES:
        raise BridgeError("tool arguments exceed the byte limit")
    return raw


def _args(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise BridgeError("invalid function argument JSON") from exc
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise BridgeError("tool arguments must be a JSON object")
    _canonical(value)
    return value


def _fingerprint(tool: str, args: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical({"tool": tool, "arguments": args})).hexdigest()


@dataclass
class _Ticket:
    tool: str
    digest: str
    expires_at: float
    approved: bool = False


class MotifFunctionBridge:
    """Adapter around an injected authenticated callable: (tool, args) -> result.

    `model_functions` / `call_from_model` grant read-only capabilities.
    `stage_review`, `approve_from_ui`, `call_from_ui` are a SEPARATE human UI path.
    No model-provided `approved` field can authorize a write.
    """

    def __init__(self, transport: Callable[[str, dict[str, Any]], Any],
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._transport = transport
        self._clock = clock
        self._tickets: dict[str, _Ticket] = {}

    def model_functions(self, mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        functions = []
        seen: set[str] = set()
        for item in mcp_tools:
            name = item.get("name")
            if name not in READ_TOOLS or name in seen:
                continue
            schema = item.get("inputSchema", {"type": "object", "properties": {}})
            if not isinstance(schema, dict) or schema.get("type") != "object":
                continue  # Fail closed on malformed / unsupported tool schemas.
            seen.add(name)
            functions.append({
                "type": "function",
                "name": PREFIX + name,
                "description": str(item.get("description", ""))[:512],
                "parameters": schema,
                "strict": False,
            })
        return functions

    def call_from_model(self, name: str, arguments: Any) -> Any:
        if not isinstance(name, str) or not name.startswith(PREFIX):
            raise BridgeError("unknown function name")
        tool = name[len(PREFIX):]
        if tool not in READ_TOOLS:
            raise BridgeError("model cannot invoke this tool")
        return self._transport(tool, _args(arguments))

    def stage_review(self, tool: str, arguments: Any, ttl_seconds: int = 120) -> str:
        if tool not in REVIEW_TOOLS or not 1 <= ttl_seconds <= 600:
            raise BridgeError("tool or review lifetime not permitted")
        args = _args(arguments)
        ticket_id = secrets.token_urlsafe(24)
        self._tickets[ticket_id] = _Ticket(
            tool=tool, digest=_fingerprint(tool, args),
            expires_at=self._clock() + ttl_seconds,
        )
        return ticket_id

    def approve_from_ui(self, ticket_id: str) -> None:
        """Call only from a trusted, explicit user-click UI handler, never the LLM."""
        ticket = self._tickets.get(ticket_id)
        if ticket is None or self._clock() >= ticket.expires_at:
            raise BridgeError("missing or expired review ticket")
        ticket.approved = True

    def call_from_ui(self, tool: str, arguments: Any, ticket_id: str) -> Any:
        if tool not in REVIEW_TOOLS:
            raise BridgeError("tool not available on review path")
        args = _args(arguments)
        ticket = self._tickets.get(ticket_id)
        if (ticket is None or not ticket.approved or ticket.tool != tool
                or self._clock() >= ticket.expires_at
                or ticket.digest != _fingerprint(tool, args)):
            raise BridgeError("fresh human approval required for exact tool arguments")
        del self._tickets[ticket_id]  # One-time approval, consumed before the call.
        return self._transport(tool, args)
