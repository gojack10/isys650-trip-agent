FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/usr/local/bin:$PATH \
    HOME=/tmp/home \
    PI_CODING_AGENT_DIR=/tmp/pi-agent \
    UV_TOOL_DIR=/opt/uv-tools \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_NO_CACHE=1 \
    BH_TELEMETRY=0 \
    BU_CDP_URL=http://127.0.0.1:9222 \
    BH_RUNTIME_DIR=/tmp/browser-harness/run \
    BH_TMP_DIR=/tmp/browser-harness/tmp

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates chromium python3 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN npm install -g @mariozechner/pi-coding-agent@0.73.1 \
 && uv tool install browser-harness==0.1.13

WORKDIR /app
COPY app.py start.sh ./
COPY agent agent
COPY docs/trip-calendar.html docs/trip-calendar.html
RUN chmod +x start.sh
USER 1000:1000
CMD ["./start.sh"]
