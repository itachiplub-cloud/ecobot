#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $1"; }
err()  { echo -e "${RED}[x]${NC} $1"; exit 1; }

REPO_DIR="/opt/ecobot"
BACKUP_DIR="/opt/ecobot/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

[[ ! -d "$REPO_DIR" ]] && err "Repository not found at $REPO_DIR"
mkdir -p "$BACKUP_DIR"

log "Backing up MongoDB..."
docker compose -f "$REPO_DIR/docker-compose.yml" exec -T mongo mongodump \
    --archive --gzip --db=economy_rpg_bot > "$BACKUP_DIR/mongo_${TIMESTAMP}.gz" 2>/dev/null

log "Backing up .env..."
cp "$REPO_DIR/.env" "$BACKUP_DIR/env_${TIMESTAMP}.bak"

log "Cleaning old backups (keeping last 7)..."
ls -t "$BACKUP_DIR"/mongo_*.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
ls -t "$BACKUP_DIR"/env_*.bak 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true

log "Backup complete: $BACKUP_DIR/mongo_${TIMESTAMP}.gz"
ls -lh "$BACKUP_DIR"/
