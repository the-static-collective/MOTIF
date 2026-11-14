"""Integration smoke through the byte-pinned original v0.3 MCP app.

Run from the unpacked release root after copying oauth_gateway.py here.
Uses a simulated OAuth verifier ONLY in test mode; no network/real tokens.
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path

import httpx

os.environ["MOTIF_MCP_API_KEY"] = "smoke-test-internal-secret-key-must-be-private"
os.environ["MOTIF_MCP_DB"] = str(Path(tempfile.gettempdir()) / "motif-oauth-smoke.sqlite3")

from mcp_server.server import app as packaged_app
from oauth_gateway import OAuthMCPGateway, Settings, READ_TOOLS, TokenRejected


class SmokeVerifier:
    def verify(self, token):
        if token != "synthetic-smoke-token":
            raise TokenRejected()
        return {"sub": "test-owner", "scope": "motif:read"}


async def main():
    settings = Settings("https://example.org", "https://issuer.example.org/",
                        "https://issuer.example.org/.well-known/jwks.json",
                        "test-owner", os.environ["MOTIF_MCP_API_KEY"])
    gateway = OAuthMCPGateway(packaged_app, settings, SmokeVerifier())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway),
                                 base_url=settings.resource, timeout=15.0) as client:
        headers = {"Authorization": "Bearer synthetic-smoke-token",
                   "Accept": "application/json, text/event-stream"}
        init = await client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "oauth-smoke", "version": "0.1"}}
        })
        assert init.status_code == 200, (init.status_code, init.text[:700])
        assert init.json().get("result"), init.text
        listing = await client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
        })
        assert listing.status_code == 200, (listing.status_code, listing.text[:700])
        names = {tool["name"] for tool in listing.json()["result"]["tools"]}
        assert names and names <= READ_TOOLS, names
        assert "forest_goals" in names, names
        assert "forest_execute_reviewed" not in names
        blocked = await client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "forest_execute_reviewed", "arguments": {}}})
        assert blocked.status_code == 403
        unauth = await client.post("/mcp", json={"jsonrpc":"2.0","id":4,
                                                  "method":"tools/list"})
        assert unauth.status_code == 401
        print("PASS pinned MCP initialize, safe tool-list, forbidden execution, and OAuth challenge")


if __name__ == "__main__":
    asyncio.run(main())
