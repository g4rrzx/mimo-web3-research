"""Cron script: Generate daily briefing and send to Telegram.

Usage:
    python -m scripts.daily_brief
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.orchestrator import ResearchOrchestrator
from src.utils.logger import get_logger
from src.utils.formatters import format_briefing_header


async def send_to_telegram(message: str):
    """Send briefing to configured Telegram chat."""
    from telegram import Bot
    from telegram.constants import ParseMode
    from src.utils.config import get_config

    cfg = get_config()
    token = cfg.env("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️  No Telegram config — printing only")
        print(message)
        return

    bot = Bot(token=token)

    # Split if too long
    for i in range(0, len(message), 4000):
        chunk = message[i:i + 4000]
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            # Fallback without markdown if formatting breaks
            await bot.send_message(chat_id=chat_id, text=chunk)


def main():
    log = get_logger()
    log.info("=== Daily briefing job started ===")

    orchestrator = ResearchOrchestrator()

    # Run collection first to ensure fresh data
    log.info("Running pre-briefing collection...")
    orchestrator.run_collection()

    # Generate briefing
    briefing = orchestrator.generate_briefing()
    header = format_briefing_header()
    full_msg = header + "\n" + briefing

    # Send to Telegram
    asyncio.run(send_to_telegram(full_msg))

    log.info("=== Daily briefing job completed ===")


if __name__ == "__main__":
    main()
