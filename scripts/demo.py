"""Demo script — generate sample data + run pipeline (no API keys needed)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.storage.db import Database
from src.utils.formatters import (
    format_whale_tx, format_social_post, format_news,
    format_alert, format_briefing_header,
)
from src.analyzers.sentiment import SentimentAnalyzer


def seed_demo_data(db: Database):
    """Insert realistic mock data for demo."""
    now = int(time.time())

    # Whale transactions
    whales = [
        {
            "chain": "arbitrum", "tx_hash": "0xab" + "f" * 60,
            "from_address": "0x28c6c06298d514db089934071355e5743bf21d60",
            "to_address": "0x1f9090aae28b8a3dceadf281b0f12828e676c326",
            "value_eth": 1247.5, "value_usd": 4365625, "token_symbol": "ETH",
            "block_number": 195842301, "timestamp": now - 600, "label": "Binance14",
        },
        {
            "chain": "base", "tx_hash": "0xcd" + "e" * 60,
            "from_address": "0x3b3a45f3b32f86b8e44c61e98736b7e8b5a1a7c8",
            "to_address": "0x4a679253410272dd5232b3ff7cf5dbb88f295319",
            "value_eth": 523.1, "value_usd": 1830850, "token_symbol": "ETH",
            "block_number": 12483921, "timestamp": now - 1800, "label": "WhaleAlpha",
        },
        {
            "chain": "optimism", "tx_hash": "0xef" + "1" * 60,
            "from_address": "0x9696f59e4d72e237be84ffd425dcad154bf96976",
            "to_address": "0x6b175474e89094c44da98b954eedeac495271d0f",
            "value_eth": 312.7, "value_usd": 1094450, "token_symbol": "ETH",
            "block_number": 134821234, "timestamp": now - 3600, "label": "Cobie",
        },
    ]
    for w in whales:
        db.insert_whale_tx(**w)

    # Social posts
    posts = [
        {
            "platform": "farcaster", "post_id": "fc_001",
            "author": "dwr.eth", "content": "AI agents on Base are about to explode. New protocols launching weekly, TVL up 40% MoM. Bullish on the entire stack.",
            "url": "https://warpcast.com/dwr.eth/0xabc",
            "engagement_score": 245.0, "timestamp": now - 1200,
            "keywords": "base,ai-agents",
        },
        {
            "platform": "farcaster", "post_id": "fc_002",
            "author": "jacob", "content": "Arbitrum surpassing all L2s in active wallets this week. The migration from mainnet is real and accelerating. LFG.",
            "url": "https://warpcast.com/jacob/0xdef",
            "engagement_score": 187.0, "timestamp": now - 2400,
            "keywords": "arbitrum,l2",
        },
        {
            "platform": "x", "post_id": "x_001",
            "author": "VitalikButerin", "content": "Decentralized AI agents need better onchain identity primitives. Working on EIP for agent-to-agent verification.",
            "url": "https://x.com/VitalikButerin/status/123",
            "engagement_score": 4521.0, "timestamp": now - 5400,
            "keywords": "ai,ethereum",
        },
        {
            "platform": "x", "post_id": "x_002",
            "author": "0xfoobar", "content": "Massive exploit discovered in unaudited protocol. $4M drained. Always check audits before depositing. Be careful out there.",
            "url": "https://x.com/0xfoobar/status/456",
            "engagement_score": 892.0, "timestamp": now - 7200,
            "keywords": "security,exploit",
        },
        {
            "platform": "farcaster", "post_id": "fc_003",
            "author": "ace", "content": "Just shipped a new MiMo-powered research agent. Onchain analytics + sentiment in real-time. The future is autonomous agents.",
            "url": "https://warpcast.com/ace/0x789",
            "engagement_score": 156.0, "timestamp": now - 900,
            "keywords": "ai-agents,mimo",
        },
    ]
    for p in posts:
        db.insert_social_post(**p)

    # News
    news = [
        {
            "source": "The Defiant",
            "title": "Arbitrum Hits $5B TVL Milestone as DeFi Activity Surges",
            "url": "https://thedefiant.io/arbitrum-5b-tvl",
            "summary": "Layer 2 leader Arbitrum crossed $5B in total value locked, driven by new lending and AI-agent protocols.",
            "published_at": now - 7200, "relevance_score": 0.85,
            "tags": "arbitrum,defi,tvl,l2",
        },
        {
            "source": "Bankless",
            "title": "AI Agents on Base: The New Frontier of Onchain Automation",
            "url": "https://newsletter.banklesshq.com/ai-agents-base",
            "summary": "Base ecosystem sees explosion of autonomous AI agents managing portfolios, executing trades, and providing research.",
            "published_at": now - 14400, "relevance_score": 0.95,
            "tags": "base,ai agent,defi",
        },
        {
            "source": "The Block",
            "title": "Optimism Superchain Adds Three New Members in Q2",
            "url": "https://theblock.co/optimism-superchain-q2",
            "summary": "Optimism's Superchain ecosystem grew to 12 chains with three major additions, expanding shared sequencing.",
            "published_at": now - 21600, "relevance_score": 0.65,
            "tags": "optimism,rollup,l2",
        },
        {
            "source": "CoinDesk",
            "title": "Vitalik Outlines Roadmap for Decentralized AI on Ethereum",
            "url": "https://coindesk.com/vitalik-decentralized-ai",
            "summary": "Ethereum founder details vision for AI-native primitives including agent identity and verifiable computation.",
            "published_at": now - 28800, "relevance_score": 0.75,
            "tags": "ethereum,vitalik,ai",
        },
    ]
    for n in news:
        db.insert_news(**n)

    print(f"✅ Seeded {len(whales)} whales, {len(posts)} posts, {len(news)} news")


def run_demo(db: Database):
    """Run demo and print formatted output."""
    print("\n" + "=" * 60)
    print(format_briefing_header())
    print("=" * 60)

    # Whales
    print("\n🐋 WHALE ACTIVITY (24h)\n" + "-" * 40)
    for w in db.get_recent_whales(hours=24, limit=10):
        print(format_whale_tx(w))

    # Sentiment
    print("\n📊 SENTIMENT ANALYSIS\n" + "-" * 40)
    posts = db.get_recent_social(hours=24, limit=20)
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.analyze_batch(posts)
    score = sentiment["overall_sentiment"]
    emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "🟡"
    print(f"{emoji} Overall: {score:+.3f} ({sentiment['post_count']} posts)")

    # Social
    print("\n📱 TOP SOCIAL POSTS\n" + "-" * 40)
    for p in posts[:5]:
        print(format_social_post(p, max_len=100))
        print()

    # News
    print("\n📰 NEWS HIGHLIGHTS\n" + "-" * 40)
    for n in db.get_recent_news(hours=24, limit=5):
        print(format_news(n))

    # Sample alert
    print("\n🚨 SAMPLE WHALE ALERT\n" + "-" * 40)
    whales = db.get_recent_whales(hours=24, limit=1)
    if whales:
        print(format_alert("whale", whales[0]))

    print("\n" + "=" * 60)
    print("✅ Demo complete — Production-ready pipeline")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    db_path = "./data/demo.db"
    Path("./data").mkdir(exist_ok=True)
    Path(db_path).unlink(missing_ok=True)

    db = Database(db_path)
    seed_demo_data(db)
    run_demo(db)
