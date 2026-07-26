# Telegram Economy RPG Bot

A production-ready, full-featured Telegram Economy RPG Bot built with Python 3.12+, Pyrogram v2, Motor/MongoDB, and AsyncIO. Includes virtual stock market, RPG combat, pet system, clans, quests, battle pass, and a complete owner admin panel.

---

## Features

| Category | What's Included |
|----------|----------------|
| **Economy** | Wallet, bank, deposits, withdrawals, transfers, tax system |
| **Work** | 9 careers with salary ranges and cooldowns |
| **Crime** | Beg, steal, rob, heist, hack with risk/reward |
| **Games** | Coinflip, slots, blackjack, roulette, dice, mines, crash |
| **Telegram Games** | Dart, bowling, basketball, football, dice roll (animated emoji) |
| **Betting Games** | Bet roll, high/low, wheel, treasure, lucky card, number guess, crash |
| **RPG** | Stats, equipment, 5 dungeons, 5 bosses, PvP, fishing, mining |
| **Stock Market** | 60 companies, buy/sell, stop loss, take profit, price engine |
| **Quests** | Daily, weekly, monthly quest assignment and completion |
| **Pets** | Collect, equip, feed, play, evolve |
| **Clans** | Create, join, deposit, leaderboard |
| **Shop** | Permanent, daily, weekly, premium items |
| **Banking** | Loans, repay, interest, transactions |
| **Battle Pass** | Seasonal tiers, missions, premium upgrade |
| **Achievements** | 27 achievements with progress tracking |
| **Leaderboards** | Richest, highest level, most XP, group rankings |
| **Admin Panel** | Full inline admin UI with 20+ owner commands |
| **Soft Delete** | Recycle bin with recovery for deleted users |
| **Audit Logs** | Every admin action tracked with old/new values |
| **Group Rankings** | Per-group and cross-group leaderboards |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| Telegram | Pyrogram v2 |
| Database | MongoDB 7 (Motor async driver) |
| Scheduling | APScheduler |
| Config | python-dotenv |
| Logging | loguru |
| Validation | Pydantic v2 |
| YAML | PyYAML |
| Deployment | Docker, Heroku, Railway, VPS |

---

## Project Structure

```
ecobot/
├── bot/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── core/                      # Localization
│   ├── database/
│   │   ├── models/                # 37 Pydantic models
│   │   ├── repositories/          # 38 data access repos
│   │   └── indexes/               # Auto index creation
│   ├── services/                  # 26 business logic services
│   ├── middlewares/                # DB, stats, user, cooldown
│   ├── filters/                   # Owner, sudo, admin, group
│   ├── keyboards/                 # All inline keyboards
│   ├── plugins/                   # 76 command handler files
│   │   ├── economy/               # balance, deposit, withdraw, transfer
│   │   ├── work/                  # 9 careers
│   │   ├── crime/                 # beg, steal, rob, heist, hack
│   │   ├── games/                 # 13 game files (coinflip through crash)
│   │   ├── rpg/                   # stats, equip, dungeon, boss, pvp, fish, mine
│   │   ├── quests/                # quest system
│   │   ├── pets/                  # pet system
│   │   ├── shop/                  # shop system
│   │   ├── market/                # player marketplace
│   │   ├── clans/                 # clan system
│   │   ├── banking/               # bank, loans, investments
│   │   ├── daily/                 # daily/weekly/monthly/yearly rewards
│   │   ├── leaderboard/           # leaderboards + group rankings
│   │   ├── stocks/                # virtual stock market + admin + seed data
│   │   ├── battlepass/            # battle pass + game pass
│   │   ├── achievements/          # achievement system
│   │   ├── mail/                  # system mail
│   │   ├── events/                # event system
│   │   └── admin/                 # admin panel, owner cmds, enhanced owner
│   └── utils/                     # helpers, formatting
├── config/                        # settings.py, __init__.py
├── locales/                       # en.yml (46 sections)
├── scripts/                       # deploy.sh, status.sh, backup.sh
├── tests/                         # unit tests
├── Dockerfile                     # production multi-stage build
├── Dockerfile.heroku              # Heroku-specific build
├── docker-compose.yml             # bot + mongo + mongo-express
├── Procfile                       # Heroku worker
├── runtime.txt                    # Heroku Python version
├── app.json                       # Heroku app manifest
├── railway.json                   # Railway config
├── nixpacks.toml                  # Railway nixpacks build
├── nginx.conf                     # reverse proxy config
├── run.bat                        # Windows batch runner
├── run.ps1                        # Windows PowerShell runner
├── requirements.txt               # 15 dependencies
├── .env.example                   # environment template
├── .gitignore                     # git ignore rules
└── .dockerignore                  # docker ignore rules
```

---

## Deployment Guides

### Option 1: Windows (Local Development)

**Prerequisites:** Python 3.12+, pip

```powershell
# 1. Clone the repo
git clone https://github.com/itachiplub-cloud/ecobot.git
cd ecobot

# 2. Double-click run.bat — OR run in PowerShell:
.\run.ps1

# The script will:
#   - Check Python is installed
#   - Copy .env.example → .env (opens notepad)
#   - Install all dependencies
#   - Start the bot
```

**Manual setup:**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env                          # fill in your credentials
python -m bot.main
```

---

### Option 2: VPS (Ubuntu/Debian — Recommended)

**Prerequisites:** A VPS with Ubuntu 20.04+ (DigitalOcean, Vultr, Hetzner, AWS EC2, etc.)

**One-command deploy:**
```bash
# SSH into your VPS, then:
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/itachiplub-cloud/ecobot/main/scripts/deploy.sh)"
```

**Or manual deploy:**
```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 2. Clone repo
git clone https://github.com/itachiplub-cloud/ecobot.git /opt/ecobot
cd /opt/ecobot

# 3. Configure
cp .env.example .env
nano .env                            # fill in your credentials

# 4. Start
docker compose up -d --build

# 5. Check status
docker compose ps
docker compose logs -f bot
```

**VPS management commands:**
```bash
# Status dashboard
bash /opt/ecobot/scripts/status.sh

# Backup MongoDB
bash /opt/ecobot/scripts/backup.sh

# Restart bot
cd /opt/ecobot && docker compose restart bot

# View logs
docker compose -f /opt/ecobot/docker-compose.yml logs -f bot

# Stop everything
cd /opt/ecobot && docker compose down

# Update to latest code
cd /opt/ecobot && git pull && docker compose up -d --build

# Access Mongo Express (database GUI)
docker compose --profile tools up -d mongo-express
# Then visit http://localhost:8081 (admin/changeme)
```

**Systemd auto-restart** (set up by deploy.sh):
```bash
systemctl status ecobot        # check status
systemctl restart ecobot       # restart
systemctl stop ecobot          # stop
journalctl -u ecobot -f        # view systemd logs
```

---

### Option 3: Heroku

**Prerequisites:** [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), Heroku account

```bash
# 1. Login
heroku login

# 2. Create app
heroku create your-bot-name

# 3. Add MongoDB addon (free tier available)
heroku addons:create mongodb:sandbox

# 4. Set config vars
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set OWNER_ID=your_user_id
heroku config:set MONGO_DB_NAME=economy_rpg_bot
heroku config:set LOG_LEVEL=INFO
heroku config:set PYTHONUNBUFFERED=1

# 5. Deploy
git push heroku main

# 6. Scale worker (NOT web — this is a bot, not a website)
heroku ps:scale worker=1

# 7. View logs
heroku logs --tail

# 8. Restart if needed
heroku restart
```

**Using the Deploy button (app.json):**

Click the button below to deploy directly to Heroku:

[![Deploy](https://raw.githubusercontent.com/heroku/buttons/master/deploy-to-heroku.svg)](https://heroku.com/deploy)

> **Important:** Heroku free tier removed. Use at least Eco ($5/mo) or Basic ($7/mo) dyno type. The worker dyno runs the bot (not web).

---

### Option 4: Railway

**Prerequisites:** [Railway account](https://railway.app)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Add MongoDB plugin
railway add --plugin mongo

# 5. Set environment variables
railway variables set API_ID=your_api_id
railway variables set API_HASH=your_api_hash
railway variables set BOT_TOKEN=your_bot_token
railway variables set OWNER_ID=your_user_id
railway variables set MONGO_DB_NAME=economy_rpg_bot

# 6. Deploy
railway up

# 7. View logs
railway logs

# 8. Check status
railway status
```

**Or deploy via GitHub:**
1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click **New Project → Deploy from GitHub repo**
4. Select your repo
5. Railway auto-detects the Dockerfile
6. Add MongoDB plugin → Set env vars → Done

---

### Option 5: Docker (Any Platform)

```bash
# 1. Clone and configure
git clone https://github.com/itachiplub-cloud/ecobot.git
cd ecobot
cp .env.example .env
nano .env                            # fill in your credentials

# 2. Start with Docker Compose
docker compose up -d --build

# 3. Check
docker compose ps
docker compose logs -f bot

# 4. Stop
docker compose down
```

**With Mongo Express (database GUI):**
```bash
docker compose --profile tools up -d
# Visit http://localhost:8081 (admin/changeme)
```

**Docker without Compose:**
```bash
# Build image
docker build -t ecobot .

# Run with external MongoDB
docker run -d --name ecobot \
    --restart unless-stopped \
    --env-file .env \
    -e MONGO_URI=mongodb://your-mongo-host:27017 \
    ecobot
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_ID` | Yes | — | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Yes | — | Telegram API Hash |
| `BOT_TOKEN` | Yes | — | Bot token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Yes | — | Your Telegram user ID (only you are owner) |
| `MONGO_URI` | Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | No | `economy_rpg_bot` | Database name |
| `DEFAULT_BALANCE` | No | `500` | Starting coins for new users |
| `TAX_RATE` | No | `0.05` | Transaction tax (5%) |
| `BANK_INTEREST_RATE` | No | `0.02` | Bank interest rate (2%) |
| `DAILY_REWARD` | No | `100` | Daily login reward amount |
| `LOG_LEVEL` | No | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |
| `LOG_FILE` | No | `logs/bot.log` | Log file path |
| `SPAM_LIMIT` | No | `3` | Max commands before rate limit |
| `FLOOD_LIMIT` | No | `5` | Max messages in flood window |
| `COOLDOWN_SECONDS` | No | `5` | Default command cooldown |

**Heroku note:** MongoDB URI is auto-set by the MongoDB addon. Don't manually set `MONGO_URI`.

---

## Getting Telegram Credentials

### API ID & Hash
1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click **API development tools**
4. Fill in the form (app title, short name, platform)
5. Copy **App api_id** and **App api_hash**

### Bot Token
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name (e.g., "My RPG Bot")
4. Choose a username (must end in `bot`)
5. Copy the token (looks like `123456:ABC-DEF...`)

### Your User ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID

---

## All Bot Commands

### Main Menu
| Command | Description |
|---------|-------------|
| `/start` | Open main menu |
| `/help` | Paginated help (15 pages) |
| `/profile` | View your profile |
| `/settings` | Bot settings |

### Economy
| Command | Description |
|---------|-------------|
| `/balance` | Wallet & bank balance |
| `/deposit <amount>` | Deposit to bank |
| `/withdraw <amount>` | Withdraw from bank |
| `/transfer @user <amount>` | Send coins to another user |
| `/daily` | Claim daily reward |
| `/weekly` | Claim weekly reward |
| `/monthly` | Claim monthly reward |
| `/yearly` | Claim yearly reward |

### Work & Crime
| Command | Description |
|---------|-------------|
| `/work` | Work at your job (9 careers) |
| `/beg` | Beg for coins |
| `/steal @user` | Steal from a user |
| `/rob @user` | Rob a user (higher risk) |
| `/heist` | Plan a heist |
| `/hack` | Hack for coins |

### Games
| Command | Description |
|---------|-------------|
| `/coinflip <amount>` | Coin flip |
| `/slots <amount>` | Slot machine |
| `/blackjack <amount>` | Blackjack |
| `/roulette <bet> <choice>` | Roulette |
| `/dice <amount>` | Dice game |
| `/mines <amount>` | Mines (inline grid) |
| `/crash <amount>` | Crash multiplier game |

### Telegram Animated Emoji Games
| Command | Description |
|---------|-------------|
| `/darts` | Dart throw (1-6 score) |
| `/bowling` | Bowling (0-300) |
| `/basketball` | Basketball (0-5) |
| `/football` | Football (0-5) |
| `/diceroll` | Dice roll (1-6) |

### Betting Games
| Command | Description |
|---------|-------------|
| `/betroll <amount>` | Roll 6 = 10x, 5 = 5x |
| `/highlow <amount>` | Higher or lower card |
| `/wheel <amount>` | Spin the wheel |
| `/treasure <amount>` | Find the treasure |
| `/luckycard <amount>` | Lucky card flip |
| `/numberguess <amount> <num>` | Guess number 1-10 |

### RPG
| Command | Description |
|---------|-------------|
| `/rpg` | RPG main menu |
| `/stats` | View RPG stats |
| `/equip <item>` | Equip an item |
| `/dungeon` | Enter dungeon (5 levels) |
| `/boss` | Fight a boss (5 bosses) |
| `/pvp @user` | PvP battle |
| `/fish` | Fishing (7 item types) |
| `/mine` | Mining (7 ore types) |

### Stock Market
| Command | Description |
|---------|-------------|
| `/stocks` | Browse all companies |
| `/buy <ticker> <shares>` | Buy stock |
| `/sell <ticker> <shares>` | Sell stock |
| `/portfolio` | Your portfolio |
| `/stockinfo <ticker>` | Company details |
| `/watchlist` | Your watchlist |
| `/addwatch <ticker>` | Add to watchlist |
| `/removewatch <ticker>` | Remove from watchlist |
| `/stoploss <ticker> <price>` | Set stop loss |
| `/takeprofit <ticker> <price>` | Set take profit |
| `/topgainers` | Top gaining stocks |
| `/toplosers` | Top losing stocks |
| `/stockhistory <ticker>` | Price history |
| `/stocksearch <name>` | Search companies |
| `/stocklb` | Stock market leaderboards |
| `/stockstats` | Market statistics |

### Social
| Command | Description |
|---------|-------------|
| `/quests` | View daily/weekly/monthly quests |
| `/pets` | Pet menu |
| `/clan` | Clan menu |
| `/market` | Player marketplace |
| `/shop` | Shop |
| `/buy <item> [qty]` | Buy item |
| `/sell <item> [qty]` | Sell item |
| `/leaderboard` | View leaderboards |
| `/grouplb` | Group rankings |
| `/achievements` | View achievements |
| `/battlepass` | View battle pass |
| `/gamepass` | View game pass |
| `/mail` | View system mail |
| `/bank` | Bank info & loans |
| `/invest` | Invest coins |

### Admin (Owner Only)
| Command | Description |
|---------|-------------|
| `/admin` | Full admin panel (inline UI) |
| `/addsudo <user_id>` | Add sudo admin |
| `/delsudo <user_id>` | Remove sudo admin |
| `/listsudo` | List all sudo admins |
| `/broadcast <msg>` | Broadcast to all users |
| `/maintenance on/off` | Toggle maintenance mode |
| `/reload` | Reload configurations |
| `/userinfo <user_id>` | Get user info |
| `/searchuser <query>` | Search users |
| `/addcoins <user_id> <amount>` | Add coins |
| `/removecoins <user_id> <amount>` | Remove coins |
| `/setcoins <user_id> <amount>` | Set exact balance |
| `/adminban <user_id>` | Ban user |
| `/adminunban <user_id>` | Unban user |
| `/resetuser <user_id>` | Reset user data |
| `/deleteuser <user_id>` | Soft delete user |
| `/recoveruser <user_id>` | Recover deleted user |
| `/adminreset` | Reset entire economy |

### Stock Admin (Owner Only)
| Command | Description |
|---------|-------------|
| `/createstock` | Create new stock |
| `/deletestock` | Remove stock |
| `/setstockprice` | Set stock price |
| `/setstockvolatility` | Set volatility |
| `/marketcrash` | Trigger market crash |
| `/marketboom` | Trigger market boom |
| `/triggerevent` | Trigger random event |
| `/resetstockmarket` | Reset entire market |
| `/stockstatus` | Market status |
| `/setstockupdateinterval` | Change update interval |

---

## Database Collections

| Collection | Purpose |
|-----------|---------|
| `users` | User profiles, levels, XP |
| `economy` | Wallets, banks, financial data |
| `inventory` | User items |
| `items` | Item definitions |
| `shop` | Shop inventory |
| `pets` | User pets |
| `guilds` | Clans/guilds |
| `guild_members` | Guild membership |
| `quests` | Active quests |
| `daily_rewards` | Streak tracking |
| `battle_pass` | Season data |
| `transactions` | Transaction history |
| `banks` | Banking data |
| `market` | Player listings |
| `auction` | Auction house |
| `events` | Active events |
| `cooldowns` | Rate limiting |
| `achievements` | User achievements |
| `mail` | In-game mail |
| `leaderboards` | Ranking data |
| `admins` | Admin roles |
| `settings` | Bot settings |
| `premium` | Premium users |
| `logs` | Audit logs |
| `statistics` | Daily stats |
| `game_stats` | Game statistics |
| `game_history` | Game history |
| `game_config` | Configurable game parameters |
| `deleted_users` | Soft-deleted user backups |
| `audit_log` | Admin action audit trail |
| `investments` | User investments |
| `game_pass` | Game pass progress |
| `stocks` | Stock market companies |
| `stock_portfolios` | User stock holdings |
| `stock_transactions` | Stock buy/sell history |
| `stock_market_events` | Market events log |
| `stock_watchlists` | User watchlists |
| `stock_price_history` | Historical price data |
| `group_rankings` | Per-group XP/coins/messages |

---

## Permission Hierarchy

1. **OWNER** — Full access. Set via `OWNER_ID` env var. Only ONE owner.
2. **SUDO** — Management commands. Added by owner via `/addsudo`.
3. **ADMIN** — Future extension.
4. **USER** — Standard user commands.

---

## Stock Market

- **60 fictional companies** across 10 sectors (Tech, Energy, Finance, etc.)
- Prices update every **10 minutes** via background engine
- Factors: volatility config, popularity, volume pressure, random events
- **15 random events** can affect prices (earnings reports, lawsuits, etc.)
- User features: buy, sell, watchlist, stop loss, take profit, leaderboards
- Admin features: create/delete stocks, set prices, trigger crashes/booms
- **2% tax** on all stock transactions

---

## Localization

All user-facing text is in `locales/en.yml` (46 sections). To add a language:

1. Copy `locales/en.yml` to `locales/xx.yml`
2. Translate all values
3. Users switch via `/settings` → Language

---

## Testing

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'bot'` | Run from project root: `python -m bot.main` |
| `TgCrypto is missing` | Install: `pip install tgcrypto` (optional, faster) |
| `MongoDB connection refused` | Check MongoDB is running: `docker compose ps` |
| Bot starts but doesn't respond | Check `OWNER_ID` matches your Telegram user ID |
| `pydantic.ValidationError` | Check `.env` values, especially `API_ID` (must be int) |
| Docker build fails | Run: `docker compose build --no-cache` |
| Heroku H10 error | You need a `worker` dyno, not `web`: `heroku ps:scale worker=1` |
| VPS bot won't restart | Check logs: `docker compose logs bot` |

---

## License

MIT License

## Credits

Built with [Pyrogram](https://docs.pyrogram.org/), [Motor](https://motor.readthedocs.io/), [Pydantic](https://docs.pydantic.dev/), and [MongoDB](https://www.mongodb.com/).
