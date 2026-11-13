# ───────────── Image: debian:bookworm-slim ─────────────
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# ────────────── Python 3.11 (Debian bookworm) ───────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# ───────────────────────── uv ───────────────────────────────────────
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# ─── pandas (forzando sobre el Python del sistema) ───
RUN uv pip install --system --break-system-packages pandas openpyxl numpy matplotlib scikit-learn flask fastapi uvicorn redis pymongo

# ────────────────────── Node.js 22 LTS ──────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ────────────────────── MongoDB 7.0 (servidor + shell) ──────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg curl ca-certificates \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
       gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" \
       > /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       mongodb-org-server \
       mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data/db /var/log/mongodb

# ─────────── Script de arranque (mongod + sleep infinity) ───────────
RUN printf '%s\n' \
    '#!/bin/bash' \
    'set -e' \
    'mongod --dbpath /data/db --bind_ip 0.0.0.0 --port 27017 --logpath /var/log/mongodb/mongod.log --fork' \
    'sleep 2' \
    'if mongosh --quiet --eval "db.runCommand({ ping: 1 }).ok" | grep -q 1; then' \
    '  echo "[start.sh] MongoDB corriendo en el puerto 27017"' \
    'else' \
    '  echo "[start.sh] ADVERTENCIA: MongoDB no responde"' \
    'fi' \
    'exec sleep infinity' \
    > /usr/local/bin/start.sh \
    && chmod +x /usr/local/bin/start.sh

CMD ["/usr/local/bin/start.sh"]