"""OAuth-protected, single-owner Streamable HTTP front door for the pinned MOTIF v0.3 app.

Only 11 source-reviewed read tools are exposed. A legacy fixed bearer secret is
never accepted from the internet: after validating an OAuth access token, this
ASGI boundary inserts the secret when calling the in-process original app.
This is not an authorization server. Configure a real OIDC/OAuth 2.1 provider.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit
from typing import Any

import jwt
from jwt import PyJWKClient, PyJWTError

READ_TOOLS = frozenset({
    "catalog_cartridges", "select_methods", "resume_session", "list_sessions",
    "reflect_session", "forest_goals", "forest_catalog", "forest_inspect_source",
    "forest_route", "forest_resume_trial", "forest_list_trials",
})
MAX_REQUEST = 64 * 1024
MAX_LIST_RESPONSE = 2 * 1024 * 1024


class TokenRejected(Exception):
    pass


def _https_url(value: str, label: str) -> str:
    parts = urlsplit(value)
    if (parts.scheme != "https" or not parts.hostname or parts.username or
            parts.password or parts.fragment or not value or parts.query):
        raise ValueError(f"{label} must be an HTTPS URL without userinfo, query, or fragment")
    return value


@dataclass(frozen=True)
class Settings:
    resource: str
    issuer: str
    jwks_url: str
    allowed_sub: str
    internal_secret: str

    @classmethod
    def environment(cls) -> "Settings":
        resource = _https_url(os.environ.get("MOTIF_OAUTH_RESOURCE", ""), "resource")
        issuer = _https_url(os.environ.get("MOTIF_OAUTH_ISSUER", ""), "issuer")
        jwks_url = _https_url(os.environ.get("MOTIF_OAUTH_JWKS_URL", ""), "JWKS URL")
        sub = os.environ.get("MOTIF_OAUTH_ALLOWED_SUB", "")
        secret = os.environ.get("MOTIF_MCP_API_KEY", "")
        if (not sub or sub.isspace() or len(sub) > 256 or len(secret) < 32 or
                any(c in sub for c in "\r\n")):
            raise ValueError("single-owner OAuth subject and internal 32+ character key required")
        resource = resource.rstrip("/")\n        if urlsplit(resource).path not in ("", "/"):
            raise ValueError("resource must be the HTTPS origin (do not include /mcp)")
        return cls(resource, issuer, jwks_url, sub, secret)


class JWTVerifier:
    """Verify a signed JWT access token using configured issuer JWKS, never ID tokens.

    Use an IDP that issues signed audience-bound JWT access tokens. An opaque
    access token needs a DIFFERENT provider-supported introspection verifier.
    """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.keys = PyJWKClient(settings.jwks_url, cache_jwk_set=True,
                                lifespan=300, timeout=5)

    def verify(self, token: str) -> dict[str, Any]:
        if not isinstance(token, str) or len(token) > 16384 or not token:
            raise TokenRejected("invalid access token")
        try:
            signing_key = self.keys.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=self.settings.resource,
                issuer=self.settings.issuer,
                options={"require": ["exp", "iat", "aud", "iss", "sub"]},
                leeway=15,
            )
        except (PyJWTError, ValueError, KeyError, TypeError) as exc:
            raise TokenRejected("invalid token signature or claims") from exc
        if claims.get("sub") != self.settings.allowed_sub:
            raise TokenRejected("this is a single-owner service")
        scope = claims.get("scope")
        if not isinstance(scope, str) or "motif:read" not in scope.split():
            raise TokenRejected("missing motif:read scope")
        return claims


async def _send_json(send: Any, status: int, body: dict[str, Any],
                     headers: list[tuple[bytes, bytes]] | None = None) -> None:
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    head = [(b"content-type", b"application/json"),
            (b"content-length", str(len(raw)).encode("ascii")),
            (b"cache-control", b"no-store")]
    if headers:
        head.extend(headers)
    await send({"type": "http.response.start", "status": status, "headers": head})
    await send({"type": "http.response.body", "body": raw})


class OAuthMCPGateway:
    def __init__(self, inner: Any, settings: Settings, verifier: Any | None = None) -> None:
        self.inner = inner
        self.settings = settings
        self.verifier = verifier if verifier is not None else JWTVerifier(settings)
        self.resource_metadata_url = settings.resource + "/.well-known/oauth-protected-resource"

    async def _deny(self, send: Any, reason: str = "invalid_token") -> None:
        challenge = ('Bearer resource_metadata="' + self.resource_metadata_url +
                     '", scope="motif:read", error="' + reason +
                     '", error_description="MOTIF authorization required"')
        await _send_json(send, 401, {"error": "unauthorized"},
                         [(b"www-authenticate", challenge.encode("ascii"))])

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            # The public plugin transport is HTTP only; no open websocket seam.
            if scope.get("type") == "lifespan":
                await self.inner(scope, receive, send)
            return
        path, method = scope.get("path"), scope.get("method")
        if path == "/healthz" and method == "GET":
            await _send_json(send, 200, {"status": "running", "gateway": "oauth"})
            return
        if path == "/.well-known/oauth-protected-resource" and method == "GET":
            await _send_json(send, 200, {
                "resource": self.settings.resource,
                "authorization_servers": [self.settings.issuer],
                "scopes_supported": ["motif:read"],
            })
            return
        # Never expose any other path of the legacy app (including debug/docs).
        if path != "/mcp" or method not in ("POST", "GET"):
            await _send_json(send, 404, {"error": "not_found"})
            return

        original_headers = list(scope.get("headers", []))
        auth_values = [v for k, v in original_headers if k.lower() == b"authorization"]
        if len(auth_values) != 1 or not auth_values[0].startswith(b"Bearer "):
            await self._deny(send)
            return
        try:
            token = auth_values[0][7:].decode("ascii")
            self.verifier.verify(token)
        except (UnicodeDecodeError, TokenRejected):
            await self._deny(send)
            return

        # The legacy app rejects GET /mcp with 405; keep that behavior.
        request_method = None
        request_body = b""
        if method == "POST":
            while True:
                msg = await receive()
                if msg.get("type") == "http.disconnect":
                    return
                if msg.get("type") != "http.request":
                    await _send_json(send, 400, {"error": "invalid_request"})
                    return
                request_body += msg.get("body", b"")
                if len(request_body) > MAX_REQUEST:
                    await _send_json(send, 413, {"error": "too_large"})
                    return
                if not msg.get("more_body", False):
                    break
            try:
                req = json.loads(request_body)
            except (ValueError, UnicodeDecodeError):
                await _send_json(send, 400, {"error": "invalid_json"})
                return
            if not isinstance(req, dict):
                await _send_json(send, 400, {"error": "batch_not_supported"})
                return
            request_method = req.get("method")
            if request_method == "tools/call":
                params = req.get("params")
                if (not isinstance(params, dict) or
                        params.get("name") not in READ_TOOLS):
                    await _send_json(send, 403, {"error": "tool_not_available"})
                    return
            elif request_method not in (
                    "initialize", "notifications/initialized", "ping", "tools/list"):
                await _send_json(send, 403, {"error": "method_not_available"})
                return

        # No external caller can supply the internal bearer secret. The inner
        # app is called directly, never over a publicly routable internal port.
        forwarded = dict(scope)
        forwarded["headers"] = [
            (k, v) for k, v in original_headers if k.lower() != b"authorization"
        ] + [(b"authorization", b"Bearer " + self.settings.internal_secret.encode("ascii"))]
        dispatched = False

        async def replay_receive() -> dict[str, Any]:
            nonlocal dispatched
            if not dispatched:
                dispatched = True
                return {"type": "http.request", "body": request_body, "more_body": False}
            return {"type": "http.disconnect"}

        if request_method != "tools/list":
            await self.inner(forwarded, replay_receive if method == "POST" else receive, send)
            return

        # A source-only branch appearing in the forest never advertises new
        # execution privileges to ChatGPT; only curated read tools are listed.
        response_start: dict[str, Any] | None = None
        chunks: list[bytes] = []
        size = 0

        async def capture(event: dict[str, Any]) -> None:
            nonlocal response_start, size
            if event["type"] == "http.response.start":
                response_start = event
            elif event["type"] == "http.response.body":
                part = event.get("body", b"")
                size += len(part)
                if size > MAX_LIST_RESPONSE:
                    raise ValueError("tool list response exceeds limit")
                chunks.append(part)

        try:
            await self.inner(forwarded, replay_receive, capture)
            raw = b"".join(chunks)
            if response_start is None or response_start.get("status") != 200:
                await _send_json(send, 502, {"error": "tools_unavailable"})
                return
            value = json.loads(raw)
            tools = value.get("result", {}).get("tools")
            if not isinstance(tools, list):
                raise ValueError("invalid tool descriptor list")
            filtered = []
            for item in tools:
                if isinstance(item, dict) and item.get("name") in READ_TOOLS:
                    tool = dict(item)
                    tool["securitySchemes"] = [
                        {"type": "oauth2", "scopes": ["motif:read"]}
                    ]
                    filtered.append(tool)
            value["result"]["tools"] = filtered
            await _send_json(send, 200, value)
        except (ValueError, TypeError, KeyError):
            await _send_json(send, 502, {"error": "tools_unavailable"})


def build_app() -> OAuthMCPGateway:
    # This import is intentionally delayed, so the auth boundary's unit tests
    # can test against an inert simulated inner app without unpacking the ZIP.
    from mcp_server.server import app as legacy_app
    settings = Settings.environment()  # Fail closed if config is incomplete.
    return OAuthMCPGateway(legacy_app, settings)


# Uvicorn's --factory avoids constructing the service during import.
