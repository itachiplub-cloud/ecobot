#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[x]${NC} $1"; exit 1; }

REPO_DIR="/opt/ecobot"

[[ ! -d "$REPO_DIR" ]] && err "Repository not found at $REPO_DIR. Run deploy.sh first."
cd "$REPO_DIR"

echo ""
echo "================================================"
echo "  ECOSYSTEM BOT — STATUS DASHBOARD"
echo "================================================"
echo ""

log "Container status:"
docker compose ps

echo ""
log "Recent logs (last 20 lines):"
docker compose logs --tail=20 bot

echo ""
log "Disk usage:"
docker system df

echo ""
log "MongoDB collections:"
docker compose exec mongo mongosh --quiet --eval '
    db = db.getSiblingDB("economy_rpg_bot");
    print("Collections:");
    db.getCollectionNames().forEach(c => {
        count = db[c].countDocuments();
        print("  " + c + ": " + count + " docs");
    });
' 2>/dev/null || warn "Could not connect to MongoDB"

echo ""
log "Memory usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}" 2>/dev/null || true
