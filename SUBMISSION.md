# Xiaomi MiMo Orbit 100T — Submission

## Project: MiMo Web3 Research Agent

**Repository:** https://github.com/g4rrzx/mimo-web3-research
**Author:** g4rrzx (Tegar)
**Category:** AI Agents · Web3 · Automation
**Stack:** Python · MiMo API · Telegram · SQLite · Web3.py

---

## One-Liner

> AI-powered Web3 research agent that watches whale wallets, listens to crypto social, aggregates news, and delivers MiMo-generated daily briefings via Telegram bot.

---

## Why This Project

Crypto-native developers and traders need real-time onchain intelligence — but existing tools are either too generic (Telegram alerts) or too expensive (Nansen, Arkham). This agent fills the gap with a self-hosted, MiMo-powered research pipeline that runs 24/7 on minimal infrastructure.

**MiMo plays the central reasoning role:**
- Sentiment analysis across 30+ social posts in one call
- Daily briefing synthesis (whale data + sentiment + news)
- Context-aware summarization with Web3-specific prompts

---

## Key Features

- **Whale watching** — Multi-chain (Arbitrum, Base, Optimism) via block explorer APIs
- **Social listening** — Farcaster (Neynar) + X with engagement scoring
- **News aggregation** — RSS feeds (Defiant, Bankless, The Block, CoinDesk) with relevance ranking
- **MiMo-powered analysis** — Hybrid sentiment (heuristic + deep) and structured briefing generation
- **Telegram bot** — 8 interactive commands (`/brief`, `/whales`, `/social`, `/news`, `/collect`, `/sentiment`, `/status`, `/help`)
- **Cron-ready** — Two automation scripts for periodic collection and briefings
- **Smart caching** — SQLite-backed MiMo response cache to minimize redundant API calls

---

## Architecture Highlights

```
Collectors → Orchestrator → MiMo API → Storage → Telegram
```

- **Modular collectors** — Each data source (onchain, social, news) is independent and pluggable
- **Hybrid sentiment** — Quick keyword scoring (free) blended with MiMo deep analysis (accurate) for cost efficiency
- **Alert dedup** — Cooldown logic prevents spam (configurable per alert type)
- **Production-grade error handling** — Tenacity retry, transactional DB ops, structured logging

---

## Tech Choices

| Concern | Choice | Why |
|---------|--------|-----|
| LLM API | Xiaomi MiMo (OpenAI-compatible) | Native fit for the Orbit program |
| Storage | SQLite | Zero-ops, perfect for single-node agent |
| Bot framework | python-telegram-bot v21 | Async-first, well-maintained |
| Onchain data | Block explorer APIs | No RPC node required, simple to scale |
| Social | Neynar (Farcaster) + xurl (X) | Best-in-class APIs for each platform |

---

## Stats

- **19 source files**
- **~1,925 lines of Python**
- **5/5 smoke tests passing**
- **Zero lint errors**
- **Single-command setup** via `setup.sh`

---

## Future Roadmap

- DeFi position monitoring (Aave, Uniswap LP tracking)
- Multi-agent coordination (research → execution sub-agents)
- On-chain risk scoring with MiMo-powered contract analysis
- Personalized briefings based on portfolio
- Web dashboard for non-technical users
