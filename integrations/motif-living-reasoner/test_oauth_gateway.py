"""Offline gateway security tests. No external provider or database required."""
import json
import time
import unittest
from types import SimpleNamespace

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from oauth_gateway import (
    JWTVerifier, OAuthMCPGateway, Settings, TokenRejected, READ_TOOLS,
)

SETTINGS = Settings(
    resource="https://motif.example.org",
    issuer="https://identity.example.org",
    jwks_url="https://identity.example.org/keys",
    allowed_sub="owner-01",
    internal_secret="not-for-public-use-key-00000000000000",
)


class SignedJWTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.verifier = JWTVerifier(SETTINGS)
        cls.verifier.keys = SimpleNamespace(
            get_signing_key_from_jwt=lambda token: SimpleNamespace(
                key=cls.key.public_key())
        )

    def make_token(self, **changes):
        now = int(time.time())
        claims = dict(iss=SETTINGS.issuer, aud=SETTINGS.resource,
                      sub=SETTINGS.allowed_sub, iat=now, exp=now+300,
                      scope="motif:read")
        claims.update(changes)
        return jwt.encode(claims, self.key, algorithm="RS256", headers={"kid": "test"})

    def test_accepts_only_scope_and_one_owner_signed_token(self):
        self.assertEqual(self.verifier.verify(self.make_token())["sub"], "owner-01")
        for changes in (
            {"iss": "https://other.example.org"},
            {"aud": "https://other-resource.example.org"},
            {"sub": "someone-else"},
            {"exp": int(time.time())-60},
            {"scope": "user:read"},
        ):
            with self.assertRaises(TokenRejected):
                self.verifier.verify(self.make_token(**changes))
        with self.assertRaises(TokenRejected):
            self.verifier.verify("garbage")
        self.assertIn("motif:read", self.verifier.verify(self.make_token(scope="motif:read extra"))["scope"])


class FakeVerifier:
    def verify(self, token):
        if token != "valid.jwt":
            raise TokenRejected()
        return {"sub": SETTINGS.allowed_sub, "scope": "motif:read"}


class Inner:
    def __init__(self):
        self.calls = []
        self.headers = []

    async def __call__(self, scope, receive, send):
        self.headers = list(scope.get("headers", []))
        if scope.get("type") != "http":
            return
        msg = await receive()
        request = json.loads(msg.get("body", b"{}"))
        self.calls.append(request.get("method"))
        value = {"jsonrpc": "2.0", "id": request.get("id")}
        if request.get("method") == "tools/list":
            names = sorted(READ_TOOLS | {"record_feedback", "forest_execute_reviewed"})
            value["result"] = {"tools": [
                {"name": name, "inputSchema": {"type": "object"}} for name in names
            ]}
        else:
            value["result"] = {"ok": True}
        payload = json.dumps(value).encode("utf-8")
        await send({"type": "http.response.start", "status": 200,
                    "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": payload})


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.inner = Inner()
        self.gateway = OAuthMCPGateway(self.inner, SETTINGS, FakeVerifier())
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.gateway),
            base_url=SETTINGS.resource,
            timeout=2.0,
        )
        self.auth = {"Authorization": "Bearer valid.jwt"}

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_metadata_and_health_do_not_expose_secrets(self):
        meta = await self.client.get("/.well-known/oauth-protected-resource")
        self.assertEqual(meta.status_code, 200)
        self.assertEqual(meta.json()["resource"], SETTINGS.resource)
        self.assertEqual(meta.json()["authorization_servers"], [SETTINGS.issuer])
        self.assertNotIn(SETTINGS.internal_secret, meta.text)
        health = await self.client.get("/healthz")
        self.assertEqual(health.json()["gateway"], "oauth")
        self.assertEqual((await self.client.get("/docs")).status_code, 404)

    async def test_oauth_challenge_and_reject_old_internal_secret(self):
        for headers in ({}, {"Authorization": "Bearer " + SETTINGS.internal_secret}):
            resp = await self.client.post("/mcp", json={"jsonrpc": "2.0", "id": 1,
                                                          "method": "initialize"},
                                          headers=headers)
            self.assertEqual(resp.status_code, 401)
            self.assertIn("resource_metadata", resp.headers["www-authenticate"])
        self.assertEqual(self.inner.calls, [])

    async def test_lists_only_safe_read_tools_with_oauth_schemes(self):
        resp = await self.client.post("/mcp", headers=self.auth,
                                      json={"jsonrpc": "2.0", "id": 1,
                                            "method": "tools/list", "params": {}})
        self.assertEqual(resp.status_code, 200, resp.text)
        tools = resp.json()["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, READ_TOOLS)
        self.assertTrue(all(t["securitySchemes"][0]["scopes"] == ["motif:read"]
                            for t in tools))
        self.assertNotIn(SETTINGS.internal_secret, resp.text)
        self.assertIn((b"authorization",
                       b"Bearer " + SETTINGS.internal_secret.encode()), self.inner.headers)

    async def test_executable_or_write_tools_never_reach_legacy_server(self):
        for name in ("record_feedback", "forest_execute_reviewed",
                     "execute_reviewed", "new_branch_arbitrary_exec"):
            resp = await self.client.post(
                "/mcp", headers=self.auth,
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                      "params": {"name": name, "arguments": {"approved": True}}})
            self.assertEqual(resp.status_code, 403, (name, resp.text))
        self.assertEqual(self.inner.calls, [])

    async def test_allowed_tool_and_protocol_methods_reach_inner(self):
        for method, params in (
            ("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}}),
            ("tools/call", {"name": "forest_goals", "arguments": {}}),
            ("notifications/initialized", {}),
            ("ping", {}),
        ):
            resp = await self.client.post("/mcp", headers=self.auth,
                    json={"jsonrpc": "2.0", "id": 3, "method": method, "params": params})
            self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(len(self.inner.calls), 4)

    async def test_json_batch_body_size_and_unknown_protocol_rejected(self):
        for kwargs, status in (
            ({"json": [{"method": "initialize"}]}, 400),
            ({"content": b"not json"}, 400),
            ({"json": {"method": "unreviewed/private"}}, 403),
            ({"content": b"x"*65537}, 413),
        ):
            resp = await self.client.post("/mcp", headers=self.auth, **kwargs)
            self.assertEqual(resp.status_code, status, resp.text)
        self.assertEqual(self.inner.calls, [])


if __name__ == "__main__":
    unittest.main()
