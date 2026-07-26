#!/usr/bin/env bash
set -euo pipefail

# Telegram Economy RPG Bot — Ubuntu/Debian VPS Installer
# Tested on: Ubuntu 20.04+, Debian 11+

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[x]${NC} $1"; exit 1; }

[[ $EUID -ne 0 ]] && err "Run as root: sudo bash deploy.sh"

log "Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

log "Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
fi
log "Docker $(docker --version)"

log "Installing Docker Compose..."
if ! docker compose version &>/dev/null; then
    apt-get install -y docker-compose-plugin
fi
log "Docker Compose $(docker compose version)"

log "Installing Git..."
apt-get install -y git htop tmux curl wget jq

log "Cloning repository..."
REPO_DIR="/opt/ecobot"
if [[ -d "$REPO_DIR" ]]; then
    warn "Repository exists at $REPO_DIR, pulling latest..."
    cd "$REPO_DIR" && git pull
else
    git clone https://github.com/itachiplub-cloud/ecobot.git "$REPO_DIR"
fi
cd "$REPO_DIR"

log "Creating .env file..."
if [[ ! -f .env ]]; then
    cp .env.example .env
    echo ""
    echo "================================================"
    echo "  EDIT .env WITH YOUR CREDENTIALS:"
    echo "  nano /opt/ecobot/.env"
    echo "================================================"
    echo ""
    echo "Required values:"
    echo "  API_ID      = Your Telegram API ID"
    echo "  API_HASH    = Your Telegram API Hash"
    echo "  BOT_TOKEN   = Your Bot Token from @BotFather"
    echo "  OWNER_ID    = Your Telegram User ID"
    echo "  MONGO_URI   = mongodb://mongo:27017"
    echo ""
else
    log ".env already exists, skipping..."
fi

log "Creating MongoDB data directory..."
mkdir -p /opt/ecobot/data/mongo

log "Creating log directory..."
mkdir -p /opt/ecobot/logs

log "Building and starting services..."
docker compose up -d --build

log "Checking container status..."
sleep 5
docker compose ps

log "Setting up systemd service for auto-restart..."
cat > /etc/systemd/system/ecobot.service <<'EOF'
[Unit]
Description=Telegram Economy RPG Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ecobot
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ecobot.service

log "Setting up log rotation..."
cat > /etc/logrotate.d/ecobot <<'EOF'
/opt/ecobot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

echo ""
echo "================================================"
echo -e "${GREEN}  DEPLOYMENT COMPLETE!${NC}"
echo "================================================"
echo ""
echo "  Bot container:  docker compose -f /opt/ecobot/docker-compose.yml logs -f bot"
echo "  Mongo shell:    docker compose -f /opt/ecobot/docker-compose.yml exec mongo mongosh"
echo "  Mongo Express:  docker compose --profile tools up -d mongo-express"
echo "  Edit config:    nano /opt/ecobot/.env"
echo "  Restart bot:    systemctl restart ecobot"
echo "  Stop bot:       systemctl stop ecobot"
echo "  Status:         systemctl status ecobot"
echo ""
