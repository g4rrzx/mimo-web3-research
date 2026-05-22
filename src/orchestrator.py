"""Main orchestrator — coordinates collection, analysis, and reporting."""
import json
from datetime import datetime
from typing import Optional

from src.utils.config import get_config
from src.utils.logger import get_logger, setup_logger
from src.storage.db import Database
from src.collectors.onchain import OnChainCollector
from src.collectors.social import SocialCollector
from src.collectors.news import NewsCollector
from src.analyzers.mimo_client import MiMoClient
from src.analyzers.sentiment import SentimentAnalyzer


class ResearchOrchestrator:
    """Main coordinator for research pipeline."""

    def __init__(self):
        self.cfg = get_config()
        log_path = self.cfg.env("LOG_PATH", "./logs/research.log")
        log_level = self.cfg.env("LOG_LEVEL", "INFO")
        setup_logger(log_path, log_level)
        self.log = get_logger()

        # Init storage
        db_path = self.cfg.env("DB_PATH", "./data/research.db")
        self.db = Database(db_path)

        # Init MiMo client (lazy — only if API key set)
        self.mimo: Optional[MiMoClient] = None
        if self.cfg.env("MIMO_API_KEY"):
            try:
                self.mimo = MiMoClient(self.db)
                self.log.info("MiMo client initialized")
            except Exception as e:
                self.log.warning(f"MiMo init failed: {e}")

        # Init collectors
        self.onchain = OnChainCollector(self.db)
        self.social = SocialCollector(self.db)
        self.news = NewsCollector(self.db)

        # Analyzers
        self.sentiment = SentimentAnalyzer(self.mimo)

    def run_collection(self) -> dict:
        """Run all collectors. Returns summary."""
        self.log.info("=== Starting collection cycle ===")

        results = {
            "whales": [],
            "social": {"farcaster": [], "x": []},
            "news": [],
            "started_at": int(datetime.now().timestamp()),
        }

        # On-chain
        try:
            results["whales"] = self.onchain.collect()
        except Exception as e:
            self.log.error(f"Onchain collection error: {e}")

        # Social
        try:
            results["social"] = self.social.collect()
        except Exception as e:
            self.log.error(f"Social collection error: {e}")

        # News
        try:
            results["news"] = self.news.collect()
        except Exception as e:
            self.log.error(f"News collection error: {e}")

        results["completed_at"] = int(datetime.now().timestamp())

        self.log.info(
            f"=== Collection done: {len(results['whales'])} whales, "
            f"{len(results['social']['farcaster']) + len(results['social']['x'])} social, "
            f"{len(results['news'])} news ==="
        )
        return results

    def generate_briefing(self) -> str:
        """Generate daily briefing from recent data."""
        if not self.mimo:
            return "⚠️ MiMo client not initialized — set MIMO_API_KEY"

        # Fetch recent data
        whales = self.db.get_recent_whales(hours=24, limit=20)
        social_posts = self.db.get_recent_social(hours=24, limit=50)
        news = self.db.get_recent_news(hours=24, limit=20)

        # Sentiment analysis
        sentiment = self.sentiment.analyze_batch(social_posts)

        data = {
            "whales": whales,
            "sentiment": sentiment,
            "news": news,
        }

        try:
            briefing = self.mimo.generate_briefing(data)

            # Save to DB
            today = datetime.now().strftime("%Y-%m-%d")
            metrics = json.dumps({
                "whale_count": len(whales),
                "social_count": len(social_posts),
                "news_count": len(news),
                "sentiment": sentiment.get("overall_sentiment", 0),
            })
            self.db.save_briefing(today, briefing, metrics=metrics)

            self.log.info(f"Briefing generated for {today}")
            return briefing

        except Exception as e:
            self.log.error(f"Briefing generation failed: {e}")
            return f"❌ Briefing failed: {e}"

    def check_alerts(self, results: dict) -> list:
        """Check if any data triggers alerts."""
        alerts = []
        threshold = self.cfg.get("alerts.whale_threshold_usd", 500000)
        cooldown = self.cfg.get("alerts.cooldown_minutes", 15) * 60

        # Whale alerts
        for whale in results.get("whales", []):
            if whale.get("value_usd", 0) >= threshold:
                target = whale.get("tx_hash", "")
                if self.db.can_alert("whale", target, cooldown):
                    alerts.append({
                        "type": "whale",
                        "data": whale,
                    })
                    self.db.log_alert("whale", target, json.dumps(whale, default=str))

        return alerts
