"""MiMo API client (OpenAI-compatible)."""
import hashlib
import json
from typing import Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.storage.db import Database


class MiMoClient:
    """Wrapper for Xiaomi MiMo API with caching and retry."""

    def __init__(self, db: Optional[Database] = None):
        cfg = get_config()
        self.api_key = cfg.require_env("MIMO_API_KEY")
        self.base_url = cfg.env("MIMO_API_BASE", "https://api.mimo.xiaomi.com/v1")
        self.model = cfg.env("MIMO_MODEL", "mimo-v2.5")
        self.db = db
        self.log = get_logger()

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _cache_key(self, prompt: str, system: str = "") -> str:
        """Generate cache key from prompt + system."""
        combined = f"{system}|{prompt}|{self.model}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_api(self, messages: list, **kwargs) -> dict:
        """Call MiMo API with retry."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens if response.usage else 0,
        }

    def chat(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_cache: bool = True,
    ) -> str:
        """Send chat completion request."""
        cache_key = self._cache_key(prompt, system)

        # Check cache
        if use_cache and self.db:
            cached = self.db.get_mimo_cache(cache_key)
            if cached:
                self.log.debug(f"MiMo cache hit: {cache_key[:8]}")
                return cached

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Call API
        try:
            result = self._call_api(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = result["content"]
            tokens = result["tokens"]

            # Cache result
            if use_cache and self.db:
                prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
                self.db.set_mimo_cache(cache_key, prompt_hash, content, tokens)

            self.log.info(f"MiMo call: {tokens} tokens used")
            return content

        except Exception as e:
            self.log.error(f"MiMo API error: {e}")
            raise

    def summarize(self, text: str, context: str = "") -> str:
        """Summarize text into 3-5 bullet points."""
        system = (
            "You are a Web3 research analyst. Summarize the given content "
            "into 3-5 concise bullet points. Focus on actionable insights, "
            "market implications, and technical details."
        )
        prompt = f"{context}\n\nContent:\n{text}\n\nSummary:"
        return self.chat(prompt, system, temperature=0.3, max_tokens=500)

    def analyze_sentiment(self, posts: list) -> dict:
        """Analyze sentiment from social posts."""
        system = (
            "You are a crypto market sentiment analyst. Analyze the given "
            "social media posts and return a JSON object with: "
            '{"overall_sentiment": -1 to 1, "key_themes": [list], '
            '"bullish_signals": [list], "bearish_signals": [list]}. '
            "Return ONLY valid JSON."
        )
        posts_text = "\n---\n".join([
            f"@{p.get('author', 'unknown')}: {p.get('content', '')}"
            for p in posts[:30]
        ])
        prompt = f"Posts:\n{posts_text}\n\nAnalysis:"
        result = self.chat(prompt, system, temperature=0.4, max_tokens=800)

        try:
            # Strip markdown code blocks if present
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            self.log.warning(f"Failed to parse sentiment JSON: {result[:200]}")
            return {
                "overall_sentiment": 0,
                "key_themes": [],
                "bullish_signals": [],
                "bearish_signals": [],
                "raw": result,
            }

    def generate_briefing(self, data: dict) -> str:
        """Generate daily briefing from collected data."""
        system = (
            "You are a Web3 research analyst writing a daily briefing for a "
            "crypto-native developer. Use direct, data-driven language. "
            "Bahasa Indonesia mixed with technical English. "
            "Format with clear sections and bullet points. "
            "Highlight actionable insights and risks."
        )

        prompt = f"""Generate a daily Web3 research briefing based on this data:

## Whale Activity ({len(data.get('whales', []))} txs)
{json.dumps(data.get('whales', [])[:10], indent=2, default=str)}

## Social Sentiment
{json.dumps(data.get('sentiment', {}), indent=2, default=str)}

## Top News ({len(data.get('news', []))} articles)
{json.dumps(data.get('news', [])[:10], indent=2, default=str)}

Format the briefing with these sections:
1. **TL;DR** (3 bullets)
2. **Market Pulse** (whale activity insights)
3. **Social Signals** (what crypto Twitter/Farcaster is buzzing about)
4. **News Recap** (top 5 stories with implications)
5. **Watch List** (3 things to monitor today)
"""

        return self.chat(prompt, system, temperature=0.5, max_tokens=2500,
                         use_cache=False)
