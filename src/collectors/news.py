"""News collector via RSS feeds."""
import time
from datetime import datetime
from typing import Optional
import feedparser
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.storage.db import Database


class NewsCollector:
    """Collect crypto/web3 news from RSS feeds."""

    # Keywords that boost relevance score
    RELEVANT_KEYWORDS = {
        "high": ["arbitrum", "base", "optimism", "ai agent", "defi",
                 "farcaster", "l2", "rollup", "stablecoin"],
        "medium": ["ethereum", "bitcoin", "vitalik", "coinbase", "binance",
                   "uniswap", "aave", "lido", "tvl"],
        "low": ["nft", "memecoin", "altcoin"],
    }

    def __init__(self, db: Database):
        self.cfg = get_config()
        self.db = db
        self.log = get_logger()

    def _calc_relevance(self, title: str, summary: str = "") -> float:
        """Score article relevance (0-1)."""
        text = f"{title} {summary}".lower()
        score = 0.0

        for kw in self.RELEVANT_KEYWORDS["high"]:
            if kw in text:
                score += 0.3
        for kw in self.RELEVANT_KEYWORDS["medium"]:
            if kw in text:
                score += 0.15
        for kw in self.RELEVANT_KEYWORDS["low"]:
            if kw in text:
                score += 0.05

        return min(score, 1.0)

    def _extract_tags(self, title: str, summary: str = "") -> str:
        """Extract relevant tags from text."""
        text = f"{title} {summary}".lower()
        all_keywords = (
            self.RELEVANT_KEYWORDS["high"] +
            self.RELEVANT_KEYWORDS["medium"]
        )
        found = [kw for kw in all_keywords if kw in text]
        return ",".join(found[:5])

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    def _fetch_feed(self, url: str):
        """Fetch and parse RSS feed."""
        return feedparser.parse(url, request_headers={
            "User-Agent": "Mozilla/5.0 MiMo-Research/0.1"
        })

    def collect_feed(self, name: str, url: str) -> list:
        """Collect articles from one RSS feed."""
        try:
            feed = self._fetch_feed(url)
            new_articles = []

            for entry in feed.entries[:30]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary_raw = entry.get("summary", "")[:1000]

                # Parse published date
                published = entry.get("published_parsed") or \
                            entry.get("updated_parsed")
                if published:
                    pub_ts = int(time.mktime(published))
                else:
                    pub_ts = int(time.time())

                # Filter old articles (>3 days)
                if (time.time() - pub_ts) > (3 * 86400):
                    continue

                relevance = self._calc_relevance(title, summary_raw)

                # Skip irrelevant articles
                if relevance < 0.1:
                    continue

                tags = self._extract_tags(title, summary_raw)

                article = {
                    "source": name,
                    "title": title[:500],
                    "url": link,
                    "summary": summary_raw,
                    "published_at": pub_ts,
                    "relevance_score": relevance,
                    "tags": tags,
                }

                row_id = self.db.insert_news(**article)
                if row_id:
                    new_articles.append(article)

            self.log.info(
                f"News [{name}]: {len(new_articles)} new "
                f"(of {len(feed.entries)})"
            )
            return new_articles

        except Exception as e:
            self.log.error(f"News feed [{name}] failed: {e}")
            return []

    def collect(self) -> list:
        """Run full news collection."""
        if not self.cfg.get("news.enabled", False):
            return []

        feeds = self.cfg.get("news.rss_feeds", [])
        all_new = []

        for feed in feeds:
            articles = self.collect_feed(feed.get("name"), feed.get("url"))
            all_new.extend(articles)
            time.sleep(0.5)

        self.log.info(f"News total new: {len(all_new)}")
        return all_new
