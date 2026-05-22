"""Sentiment analysis using MiMo + simple heuristics."""
import re
from typing import Optional

from src.analyzers.mimo_client import MiMoClient
from src.utils.logger import get_logger


# Simple keyword-based fallback
BULLISH_WORDS = {
    "moon", "pump", "bullish", "buy", "long", "ath", "breakout",
    "rally", "surge", "gem", "alpha", "lfg", "wagmi", "based",
}
BEARISH_WORDS = {
    "dump", "bearish", "sell", "short", "rekt", "bleed", "crash",
    "rug", "scam", "exploit", "hack", "fud", "ngmi",
}


class SentimentAnalyzer:
    """Hybrid sentiment: MiMo for deep analysis + heuristics for quick pass."""

    def __init__(self, mimo_client: Optional[MiMoClient] = None):
        self.mimo = mimo_client
        self.log = get_logger()

    def quick_score(self, text: str) -> float:
        """Fast keyword-based sentiment (-1 to 1)."""
        if not text:
            return 0.0

        words = set(re.findall(r"\b\w+\b", text.lower()))
        bull = len(words & BULLISH_WORDS)
        bear = len(words & BEARISH_WORDS)

        if bull == 0 and bear == 0:
            return 0.0

        return (bull - bear) / (bull + bear)

    def analyze_batch(self, posts: list) -> dict:
        """Analyze sentiment across batch of posts."""
        if not posts:
            return {
                "overall_sentiment": 0,
                "post_count": 0,
                "key_themes": [],
                "bullish_signals": [],
                "bearish_signals": [],
            }

        # Quick scores for all posts
        quick_scores = []
        for p in posts:
            content = p.get("content", "")
            score = self.quick_score(content)
            p["sentiment"] = score
            quick_scores.append(score)

        avg_quick = sum(quick_scores) / len(quick_scores) if quick_scores else 0

        # Deep analysis with MiMo (if available)
        if self.mimo and len(posts) >= 5:
            try:
                deep = self.mimo.analyze_sentiment(posts)
                # Combine: weighted avg of quick + deep
                overall = (
                    avg_quick * 0.3 +
                    float(deep.get("overall_sentiment", 0)) * 0.7
                )
                return {
                    "overall_sentiment": round(overall, 3),
                    "post_count": len(posts),
                    "quick_avg": round(avg_quick, 3),
                    "key_themes": deep.get("key_themes", []),
                    "bullish_signals": deep.get("bullish_signals", []),
                    "bearish_signals": deep.get("bearish_signals", []),
                }
            except Exception as e:
                self.log.warning(f"Deep sentiment failed, using quick: {e}")

        return {
            "overall_sentiment": round(avg_quick, 3),
            "post_count": len(posts),
            "quick_avg": round(avg_quick, 3),
            "key_themes": [],
            "bullish_signals": [],
            "bearish_signals": [],
        }
