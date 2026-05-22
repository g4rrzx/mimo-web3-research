"""Telegram bot interface for research agent."""
import asyncio
import json
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.utils.formatters import (
    format_whale_tx, format_social_post, format_news,
    format_alert, format_briefing_header,
)
from src.orchestrator import ResearchOrchestrator


class ResearchBot:
    """Telegram bot for MiMo Web3 Research Agent."""

    def __init__(self):
        self.cfg = get_config()
        self.log = get_logger()
        self.token = self.cfg.require_env("TELEGRAM_BOT_TOKEN")
        self.allowed_chat = self.cfg.env("TELEGRAM_CHAT_ID", "")

        self.orchestrator = ResearchOrchestrator()
        self.app: Optional[Application] = None

    def _is_authorized(self, update: Update) -> bool:
        """Check if user is authorized."""
        if not self.allowed_chat:
            return True
        chat_id = str(update.effective_chat.id)
        return chat_id == str(self.allowed_chat)

    async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not self._is_authorized(update):
            return

        msg = (
            "🤖 *MiMo Web3 Research Agent*\n\n"
            "Commands:\n"
            "/brief - Generate daily briefing\n"
            "/whales - Recent whale txs (24h)\n"
            "/social - Top social posts (24h)\n"
            "/news - Recent news (24h)\n"
            "/collect - Run collection cycle now\n"
            "/sentiment - Current market sentiment\n"
            "/status - Agent status & metrics\n"
            "/help - Show this menu"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def cmd_brief(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Generate daily briefing."""
        if not self._is_authorized(update):
            return

        await update.message.reply_text("⏳ Generating briefing...")

        try:
            briefing = await asyncio.to_thread(
                self.orchestrator.generate_briefing
            )

            header = format_briefing_header()
            full_msg = header + "\n" + briefing

            # Telegram has 4096 char limit — split if needed
            for i in range(0, len(full_msg), 4000):
                chunk = full_msg[i:i + 4000]
                await update.message.reply_text(
                    chunk, parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            self.log.error(f"Brief command failed: {e}")
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_whales(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Show recent whale transactions."""
        if not self._is_authorized(update):
            return

        whales = self.orchestrator.db.get_recent_whales(hours=24, limit=10)

        if not whales:
            await update.message.reply_text(
                "🐋 No whale txs in last 24h\n"
                "_Make sure wallets are configured in config.yaml_",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        lines = ["🐋 *Recent Whale Activity (24h)*\n"]
        for w in whales[:10]:
            lines.append(format_whale_tx(w))

        await update.message.reply_text(
            "\n".join(lines), parse_mode=ParseMode.MARKDOWN
        )

    async def cmd_social(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Show top social posts."""
        if not self._is_authorized(update):
            return

        posts = self.orchestrator.db.get_recent_social(hours=24, limit=10)

        if not posts:
            await update.message.reply_text("📱 No social posts collected yet")
            return

        lines = ["📱 *Top Social Posts (24h)*\n"]
        for p in posts[:8]:
            lines.append(format_social_post(p, max_len=120))
            lines.append("")

        msg = "\n".join(lines)[:4000]
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def cmd_news(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Show recent news."""
        if not self._is_authorized(update):
            return

        articles = self.orchestrator.db.get_recent_news(hours=24, limit=10)

        if not articles:
            await update.message.reply_text("📰 No news collected yet")
            return

        lines = ["📰 *Recent News (24h)*\n"]
        for a in articles[:10]:
            lines.append(format_news(a))
            if a.get("url"):
                lines.append(f"   {a['url']}")
            lines.append("")

        msg = "\n".join(lines)[:4000]
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def cmd_collect(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Trigger collection cycle."""
        if not self._is_authorized(update):
            return

        await update.message.reply_text("⏳ Running collection cycle...")

        try:
            results = await asyncio.to_thread(self.orchestrator.run_collection)

            msg = (
                f"✅ *Collection Complete*\n\n"
                f"🐋 Whales: {len(results['whales'])} new\n"
                f"📱 Farcaster: {len(results['social']['farcaster'])} new\n"
                f"📱 X: {len(results['social']['x'])} new\n"
                f"📰 News: {len(results['news'])} new"
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

            # Send alerts if any
            alerts = self.orchestrator.check_alerts(results)
            for alert in alerts[:5]:
                alert_msg = format_alert(alert["type"], alert["data"])
                await update.message.reply_text(
                    alert_msg, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.log.error(f"Collect command failed: {e}")
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_sentiment(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Show current sentiment."""
        if not self._is_authorized(update):
            return

        posts = self.orchestrator.db.get_recent_social(hours=12, limit=30)
        if not posts:
            await update.message.reply_text("📊 No data for sentiment analysis")
            return

        sentiment = await asyncio.to_thread(
            self.orchestrator.sentiment.analyze_batch, posts
        )

        score = sentiment.get("overall_sentiment", 0)
        emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "🟡"

        msg = (
            f"{emoji} *Market Sentiment (12h)*\n\n"
            f"Score: *{score:+.3f}*\n"
            f"Posts analyzed: {sentiment.get('post_count', 0)}\n\n"
        )

        themes = sentiment.get("key_themes", [])
        if themes:
            msg += "*Key Themes:*\n"
            for t in themes[:5]:
                msg += f"• {t}\n"

        bullish = sentiment.get("bullish_signals", [])
        if bullish:
            msg += "\n*Bullish:*\n"
            for b in bullish[:3]:
                msg += f"🟢 {b}\n"

        bearish = sentiment.get("bearish_signals", [])
        if bearish:
            msg += "\n*Bearish:*\n"
            for b in bearish[:3]:
                msg += f"🔴 {b}\n"

        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def cmd_status(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Show agent status."""
        if not self._is_authorized(update):
            return

        whales_24h = len(self.orchestrator.db.get_recent_whales(24, 999))
        social_24h = len(self.orchestrator.db.get_recent_social(24, 999))
        news_24h = len(self.orchestrator.db.get_recent_news(24, 999))

        mimo_status = "✅" if self.orchestrator.mimo else "❌"

        msg = (
            f"📊 *Agent Status*\n\n"
            f"MiMo API: {mimo_status}\n"
            f"DB: ✅ {self.orchestrator.db.db_path}\n\n"
            f"*Last 24h:*\n"
            f"🐋 Whales: {whales_24h}\n"
            f"📱 Social: {social_24h}\n"
            f"📰 News: {news_24h}\n\n"
            f"_Updated: {datetime.now().strftime('%H:%M:%S')}_"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def send_alert(self, message: str):
        """Send alert to configured chat."""
        if not self.allowed_chat or not self.app:
            return
        try:
            await self.app.bot.send_message(
                chat_id=self.allowed_chat,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            self.log.error(f"Send alert failed: {e}")

    def build_app(self) -> Application:
        """Build telegram application with handlers."""
        self.app = Application.builder().token(self.token).build()

        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_start))
        self.app.add_handler(CommandHandler("brief", self.cmd_brief))
        self.app.add_handler(CommandHandler("whales", self.cmd_whales))
        self.app.add_handler(CommandHandler("social", self.cmd_social))
        self.app.add_handler(CommandHandler("news", self.cmd_news))
        self.app.add_handler(CommandHandler("collect", self.cmd_collect))
        self.app.add_handler(CommandHandler("sentiment", self.cmd_sentiment))
        self.app.add_handler(CommandHandler("status", self.cmd_status))

        return self.app

    def run(self):
        """Start the bot."""
        app = self.build_app()
        self.log.info("🤖 Bot starting...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Entry point."""
    bot = ResearchBot()
    bot.run()


if __name__ == "__main__":
    main()
