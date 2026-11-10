#!/bin/sh
set -eu
case "${PORT:-8000}" in
  *[!0-9]*|"") echo "Invalid PORT" >&2; exit 2 ;;
esac
if [ -z "${MOTIF_MCP_API_KEY:-}" ] || [ "${#MOTIF_MCP_API_KEY}" -lt 32 ]; then
  echo "MOTIF_MCP_API_KEY is missing or too short" >&2
  exit 2
fi
# Startup fails closed when issuer, resource, JWKS or owner subject is absent.
# This never runs a public bearer-only server.
chown motif:motif /data
chmod 0700 /data
exec gosu motif uvicorn oauth_gateway:build_app --factory --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
