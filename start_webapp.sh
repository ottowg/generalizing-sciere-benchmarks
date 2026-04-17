#!/usr/bin/env bash
set -e

# Resolve latest node version installed via nvm and prepend to PATH
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ ! -d "$NVM_DIR/versions/node" ]; then
  echo "nvm node versions not found at $NVM_DIR" >&2
  exit 1
fi
LATEST_NODE=$(ls "$NVM_DIR/versions/node" | sort -V | tail -1)
export PATH="$NVM_DIR/versions/node/$LATEST_NODE/bin:$PATH"
echo "Using node $LATEST_NODE"

# Raise open file limit for Vite's file watcher
ulimit -n 65536 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBAPP_DIR="$SCRIPT_DIR/webapp"

cd "$WEBAPP_DIR"

if [ ! -d node_modules ]; then
  echo "Installing dependencies..."
  npm install
fi

npm run dev
