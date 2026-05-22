"""Cron script: Run collection cycle and send alerts.

Usage:
    python -m scripts.collect_loop
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.orchestrator import ResearchOrchestrator
from src.utils.logger import get_logger
from src.utils.formatters import format_alert


async def send_alert(message: str):
    """Send alert to Telegram."""
    from telegram import Bot
    from telegram.constants import ParseMode
    from src.utils.config import get_config

    cfg = get_config()
    token = cfg.env("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return

    bot = Bot(token=token)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        await bot.send_message(chat_id=chat_id, text=message)


def main():
    log = get_logger()
    log.info("=== Collection cycle started ===")

    orchestrator = ResearchOrchestrator()
    results = orchestrator.run_collection()

    # Check & send alerts
    alerts = orchestrator.check_alerts(results)
    if alerts:
        log.info(f"Sending {len(alerts)} alerts...")
        for alert in alerts:
            msg = format_alert(alert["type"], alert["data"])
            asyncio.run(send_alert(msg))

    log.info("=== Collection cycle completed ===")


if __name__ == "__main__":
    main()
