# MiMo Web3 Research Agent

> AI-powered Web3 research agent built on Xiaomi MiMo API. Collects on-chain whale activity, social sentiment, and crypto news — generates daily briefings via Telegram bot.

**Submission for Xiaomi MiMo Orbit 100T Creator Program.**

---

## Features

- 🐋 **Whale Watching** — Track large transactions on Arbitrum, Base, Optimism
- 📱 **Social Listening** — Monitor Farcaster channels & X accounts for crypto sentiment
- 📰 **News Aggregation** — RSS feeds from top crypto outlets (Defiant, Bankless, The Block, CoinDesk)
- 🧠 **MiMo-Powered Analysis** — Sentiment analysis, summarization, daily briefings
- 🤖 **Telegram Bot** — Interactive interface with `/brief`, `/whales`, `/sentiment` commands
- ⏰ **Cron-Ready** — Scheduled collection and briefing scripts

---

## Architecture

```
┌──────────────────────────────────────┐
│      Telegram Bot Interface          │
│  /brief /whales /social /sentiment   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Research Orchestrator           │
└──────────────┬───────────────────────┘
               │
       ┌───────┴────────┬────────────┐
       │                │            │
┌──────▼─────┐  ┌──────▼─────┐  ┌──▼──────┐
│  OnChain   │  │   Social   │  │  News   │
│ Collector  │  │  Collector │  │ Collect.│
│ (Arbiscan) │  │ (FC + X)   │  │ (RSS)   │
└──────┬─────┘  └──────┬─────┘  └──┬──────┘
       │               │           │
       └───────┬───────┴───────────┘
               │
       ┌───────▼────────┐
       │  MiMo API      │
       │  (Analysis)    │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │  SQLite + Logs │
       └────────────────┘
```

---

## Quick Start

### 1. Install

```bash
git clone <your-repo>
cd mimo-web3-research
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
nano .env
```

Required keys:
- `MIMO_API_KEY` — Get from Xiaomi MiMo Orbit
- `TELEGRAM_BOT_TOKEN` — From @BotFather
- `TELEGRAM_CHAT_ID` — Your chat ID for alerts
- `ARBISCAN_API_KEY`, `BASESCAN_API_KEY` — Optional, for whale watching
- `FARCASTER_API_KEY` — Neynar API key for Farcaster

Edit `config.yaml` to set:
- Watched wallets (whale_watching.watched_wallets)
- Farcaster channels (social.farcaster.channels)
- X accounts to monitor (social.twitter.accounts)
- News RSS feeds

### 3. Test

```bash
python tests/test_smoke.py
```

### 4. Run

**Interactive bot:**
```bash
python -m src.bot
```

**One-time collection:**
```bash
python -m scripts.collect_loop
```

**Generate daily briefing:**
```bash
python -m scripts.daily_brief
```

---

## Cron Setup

Add to crontab for automation:

```cron
# Collect every 30 minutes
*/30 * * * * cd /path/to/mimo-web3-research && /path/to/.venv/bin/python -m scripts.collect_loop >> logs/cron.log 2>&1

# Daily briefing at 07:00 WIB (00:00 UTC)
0 0 * * * cd /path/to/mimo-web3-research && /path/to/.venv/bin/python -m scripts.daily_brief >> logs/cron.log 2>&1
```

Or use Hermes Agent cron:

```bash
hermes cron add "Web3 Research Briefing" \
  --schedule "0 7 * * *" \
  --script "/path/to/mimo-web3-research/scripts/daily_brief.py"
```

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show menu |
| `/brief` | Generate daily briefing (uses MiMo) |
| `/whales` | Recent whale txs (24h) |
| `/social` | Top social posts (24h) |
| `/news` | Recent news (24h) |
| `/collect` | Run collection cycle now |
| `/sentiment` | Current market sentiment |
| `/status` | Agent status & metrics |
