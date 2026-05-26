#!/usr/bin/env bash
# Deploy UnifiedSciERE webapp to HuggingFace Spaces.
#
# Reads HF_TOKEN, HF_SPACE_USERNAME, HF_SPACE_NAME from .env.
# Builds the Vite frontend in docker mode, assembles a deployment
# directory, and force-pushes it to the HF Space git remote.
#
# Usage:
#   bash scripts/deploy_hf.sh              # full build + push
#   bash scripts/deploy_hf.sh --skip-build # reuse existing dist/ + data JSON
#   bash scripts/deploy_hf.sh --dry-run    # build but don't push

set -euo pipefail

# ── Parse args ────────────────────────────────────────────────────────────────
SKIP_DATA=0
SKIP_BUILD=0
DRY_RUN=0
for arg in "$@"; do
  case $arg in
    --skip-data)  SKIP_DATA=1 ;;
    --skip-build) SKIP_BUILD=1; SKIP_DATA=1 ;;
    --dry-run)    DRY_RUN=1 ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

# ── Load .env ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: .env not found at $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

for var in HF_TOKEN HF_SPACE_USERNAME HF_SPACE_NAME; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: $var is not set in .env"
    exit 1
  fi
done

HF_REMOTE="https://${HF_SPACE_USERNAME}:${HF_TOKEN}@huggingface.co/spaces/${HF_SPACE_USERNAME}/${HF_SPACE_NAME}"
echo "Target: https://huggingface.co/spaces/${HF_SPACE_USERNAME}/${HF_SPACE_NAME}"

# ── Step 1: Regenerate data files ─────────────────────────────────────────────
if [[ $SKIP_DATA -eq 0 ]]; then
  echo ""
  echo "==> Regenerating data files..."
  cd "$PROJECT_ROOT"
  uv run python scripts/ere_performance/label_statistics.py
  uv run python scripts/ere_performance/cross_dataset_performance.py
  uv run python scripts/ere_performance/reproduce_results_report.py
  uv run python scripts/ere_performance/multi_sciere_results_report.py
  echo "    Data files up to date."
fi

# ── Step 2: Build Vite frontend in docker mode ────────────────────────────────
if [[ $SKIP_BUILD -eq 0 ]]; then
  echo ""
  echo "==> Building frontend (VITE_DOCKER_MODE=true)..."
  cd "$PROJECT_ROOT/webapp"
  VITE_DOCKER_MODE=true npm run build
  echo "    Build complete."
fi

# ── Step 3: Assemble deployment directory ────────────────────────────────────
DEPLOY_DIR="$(mktemp -d)"
trap 'rm -rf "$DEPLOY_DIR"' EXIT
echo ""
echo "==> Assembling deployment in $DEPLOY_DIR..."

# Webapp (built frontend + production server)
mkdir -p "$DEPLOY_DIR/webapp"
cp -r "$PROJECT_ROOT/webapp/dist"      "$DEPLOY_DIR/webapp/dist"
cp -r "$PROJECT_ROOT/webapp/server"    "$DEPLOY_DIR/webapp/server"
cp    "$PROJECT_ROOT/webapp/server.js" "$DEPLOY_DIR/webapp/server.js"
cp    "$PROJECT_ROOT/webapp/package.json"      "$DEPLOY_DIR/webapp/package.json"
cp    "$PROJECT_ROOT/webapp/package-lock.json" "$DEPLOY_DIR/webapp/package-lock.json"

# Data files — flat JSON/YAML in data/webapp/
mkdir -p "$DEPLOY_DIR/data/webapp"
for f in \
  cross_dataset_performance.json \
  label_statistics.json \
  relation_signatures.json \
  reproduce_results.json \
  multi_sciere_results.json \
  example_papers.json \
  domain_shift_results.json \
  semantic_groups.json \
  allowed_signatures.yaml
do
  src="$PROJECT_ROOT/data/webapp/$f"
  if [[ -f "$src" ]]; then
    cp "$src" "$DEPLOY_DIR/data/webapp/$f"
  else
    echo "  WARNING: data/webapp/$f not found, skipping"
  fi
done

# Data subdirectories in data/webapp/
for dir in static confusion_matrices publication_map; do
  src="$PROJECT_ROOT/data/webapp/$dir"
  if [[ -d "$src" ]]; then
    cp -r "$src" "$DEPLOY_DIR/data/webapp/$dir"
  else
    echo "  WARNING: data/webapp/$dir/ not found, skipping"
  fi
done

# Gold + annotation_lookup for Samples/Lookup tabs (raw predictions not needed at runtime)
for dir in gold annotation_lookup; do
  if [[ -d "$PROJECT_ROOT/data/$dir" ]]; then
    cp -r "$PROJECT_ROOT/data/$dir" "$DEPLOY_DIR/data/$dir"
  fi
done

# Reports (sidebar markdown) and configs
cp -r "$PROJECT_ROOT/reports" "$DEPLOY_DIR/reports"
cp -r "$PROJECT_ROOT/configs" "$DEPLOY_DIR/configs"

# Dockerfile
cp "$PROJECT_ROOT/Dockerfile" "$DEPLOY_DIR/Dockerfile"

# HF Space README (creates it with sdk: docker metadata if absent)
README="$PROJECT_ROOT/hf_README.md"
if [[ -f "$README" ]]; then
  cp "$README" "$DEPLOY_DIR/README.md"
else
  cat > "$DEPLOY_DIR/README.md" <<'EOF'
---
title: UnifiedSciERE
emoji: 📊
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# UnifiedSciERE

Interactive demo for the UnifiedSciERE paper.
EOF
fi

echo "    Assembly complete."

# ── Step 4: Git init + LFS + push ─────────────────────────────────────────────
echo ""
echo "==> Initialising git repo..."
cd "$DEPLOY_DIR"
git init -q
git lfs install

# Track binary and large file types via LFS
git lfs track "*.jsonl"
git lfs track "*.npz"
git lfs track "data/annotation_lookup/*.json"
git lfs track "*.ttf"
git lfs track "*.eot"
git lfs track "*.woff"
git lfs track "*.woff2"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.parquet"
git add .gitattributes

git config user.email "deploy@unifiedsciere"
git config user.name  "UnifiedSciERE Deploy"

git add -A
git commit -q -m "deploy $(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ $DRY_RUN -eq 1 ]]; then
  echo ""
  echo "==> DRY RUN — skipping push."
  echo "    Deployment directory: $DEPLOY_DIR (will be cleaned up)"
  echo "    Would push to: https://huggingface.co/spaces/${HF_SPACE_USERNAME}/${HF_SPACE_NAME}"
  # Keep the dir alive briefly so the user can inspect it
  trap - EXIT
  echo "    Run 'rm -rf $DEPLOY_DIR' when done inspecting."
else
  echo ""
  echo "==> Pushing to HuggingFace Spaces..."
  git push --force "$HF_REMOTE" HEAD:main
  echo ""
  echo "Done! Space will build at:"
  echo "  https://huggingface.co/spaces/${HF_SPACE_USERNAME}/${HF_SPACE_NAME}"
fi
