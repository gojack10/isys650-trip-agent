#!/bin/sh
set -eu
mkdir -p "$HOME" "$PI_CODING_AGENT_DIR" "$BH_RUNTIME_DIR" "$BH_TMP_DIR" /tmp/chrome-profile
chromium \
  --headless=new \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-gpu \
  --disable-background-networking \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile \
  about:blank >/tmp/chromium.log 2>&1 &
exec uv run --no-project --python /usr/bin/python3 python app.py
