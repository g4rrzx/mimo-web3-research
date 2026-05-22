"""Social media collector — Farcaster (Neynar) + X/Twitter."""
import time
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.storage.db import Database


class SocialCollector:
    """Collect posts from Farcaster and X."""

    def __init__(self, db: Database):
        self.cfg = get_config()
        self.db = db
        self.log = get_logger()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    def _neynar_get(self, endpoint: str, params: dict = None) -> dict:
        """Call Neynar Farcaster API."""
        api_key = self.cfg.env("FARCASTER_API_KEY")
        if not api_key:
            return {}

        base = self.cfg.env("NEYNAR_API_BASE", "https://api.neynar.com/v2")
        headers = {"api_key": api_key, "accept": "application/json"}

        r = requests.get(
            f"{base}/{endpoint}",
            headers=headers,
            params=params or {},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def collect_farcaster_channel(
        self,
        channel: str,
        limit: int = 25,
    ) -> list:
        """Collect casts from a Farcaster channel."""
        try:
            channel_id = channel.lstrip("/")
            data = self._neynar_get(
                "farcaster/feed/channels",
                {"channel_ids": channel_id, "limit": limit},
            )

            casts = data.get("casts", [])
            new_posts = []

            for cast in casts:
                author = cast.get("author", {}).get("username", "unknown")
                content = cast.get("text", "")
                hash_id = cast.get("hash", "")
                ts = cast.get("timestamp", "")

                # Convert ISO timestamp to unix
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    unix_ts = int(dt.timestamp())
                except Exception:
                    unix_ts = int(time.time())

                reactions = cast.get("reactions", {})
                engagement = (
                    reactions.get("likes_count", 0) +
                    reactions.get("recasts_count", 0) * 2 +
                    cast.get("replies", {}).get("count", 0)
                )

                post = {
                    "platform": "farcaster",
                    "post_id": hash_id,
                    "author": author,
                    "content": content[:2000],
                    "url": f"https://warpcast.com/{author}/{hash_id[:10]}",
                    "engagement_score": float(engagement),
                    "sentiment": None,
                    "timestamp": unix_ts,
                    "keywords": channel_id,
                }

                row_id = self.db.insert_social_post(**post)
                if row_id:
                    new_posts.append(post)

            self.log.info(
                f"Farcaster /{channel_id}: {len(new_posts)}/{len(casts)} new"
            )
            return new_posts

        except Exception as e:
            self.log.error(f"Farcaster channel {channel} failed: {e}")
            return []

    def collect_x_user(self, username: str, limit: int = 10) -> list:
        """Collect tweets from X user (uses xurl CLI if available)."""
        import subprocess
        import json as json_lib

        try:
            # Try xurl CLI first (skill: social-media/xurl)
            result = subprocess.run(
                ["xurl", "-X", "GET",
                 f"/2/users/by/username/{username}"],
                capture_output=True, text=True, timeout=15,
            )

            if result.returncode != 0:
                self.log.debug(f"xurl not available or auth failed: {result.stderr[:100]}")
                return []

            user_data = json_lib.loads(result.stdout)
            user_id = user_data.get("data", {}).get("id")
            if not user_id:
                return []

            # Get user tweets
            result = subprocess.run(
                ["xurl", "-X", "GET",
                 f"/2/users/{user_id}/tweets?max_results={limit}"
                 "&tweet.fields=public_metrics,created_at"],
                capture_output=True, text=True, timeout=15,
            )

            tweets_data = json_lib.loads(result.stdout)
            tweets = tweets_data.get("data", [])

            new_posts = []
            for tweet in tweets:
                tweet_id = tweet.get("id")
                content = tweet.get("text", "")
                created_at = tweet.get("created_at", "")

                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    unix_ts = int(dt.timestamp())
                except Exception:
                    unix_ts = int(time.time())

                metrics = tweet.get("public_metrics", {})
                engagement = (
                    metrics.get("like_count", 0) +
                    metrics.get("retweet_count", 0) * 2 +
                    metrics.get("reply_count", 0) +
                    metrics.get("quote_count", 0) * 1.5
                )

                post = {
                    "platform": "x",
                    "post_id": tweet_id,
                    "author": username,
                    "content": content[:2000],
                    "url": f"https://x.com/{username}/status/{tweet_id}",
                    "engagement_score": float(engagement),
                    "sentiment": None,
                    "timestamp": unix_ts,
                    "keywords": username,
                }

                row_id = self.db.insert_social_post(**post)
                if row_id:
                    new_posts.append(post)

            return new_posts

        except subprocess.TimeoutExpired:
            self.log.warning(f"X collect timeout for @{username}")
            return []
        except Exception as e:
            self.log.error(f"X collect failed for @{username}: {e}")
            return []

    def collect(self) -> dict:
        """Run full social collection."""
        results = {"farcaster": [], "x": []}

        # Farcaster
        if self.cfg.get("social.farcaster.enabled", False):
            channels = self.cfg.get("social.farcaster.channels", [])
            for ch in channels:
                posts = self.collect_farcaster_channel(ch)
                results["farcaster"].extend(posts)
                time.sleep(0.5)

        # X / Twitter
        if self.cfg.get("social.twitter.enabled", False):
            accounts = self.cfg.get("social.twitter.accounts", [])
            for acc in accounts:
                posts = self.collect_x_user(acc)
                results["x"].extend(posts)
                time.sleep(1)

        self.log.info(
            f"Social collected: {len(results['farcaster'])} FC, "
            f"{len(results['x'])} X"
        )
        return results
