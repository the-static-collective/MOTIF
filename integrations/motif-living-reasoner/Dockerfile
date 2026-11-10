# MOTIF v0.3 fixed-source HTTP server + fail-closed OAuth 2.1 resource gateway.
# Use one replica and durable /data; do not attach a Docker socket.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MOTIF_MCP_DB=/data/sessions.sqlite3
WORKDIR /app
COPY release-v0.3.zip /tmp/release-v0.3.zip
RUN python -c 'import hashlib,pathlib; p=pathlib.Path("/tmp/release-v0.3.zip"); expected="7f442cefc995115b5383faf87e0f922a594d7f0a480039c2e5aecc85c122c993"; actual=hashlib.sha256(p.read_bytes()).hexdigest(); assert actual==expected, f"Release artifact checksum mismatch: {actual}"' \
  && python -m zipfile -e /tmp/release-v0.3.zip /opt/motif-release \
  && cp -a /opt/motif-release/motif-living-reasoner/. /app/ \
  && rm -rf /opt/motif-release /tmp/release-v0.3.zip \
  && test -f /app/mcp_server/server.py \
  && test -f /app/requirements.txt
COPY oauth_gateway.py /app/oauth_gateway.py
RUN apt-get update \
  && apt-get install -y --no-install-recommends gosu ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir -r /app/requirements.txt \
  && pip install --no-cache-dir 'PyJWT[crypto]==2.13.0' \
  && useradd -r -u 10001 -s /usr/sbin/nologin motif \
  && mkdir -p /data \
  && chmod 0700 /data
COPY ./start-railway.sh /usr/local/bin/start-motif
RUN chmod 0755 /usr/local/bin/start-motif
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/start-motif"]
