"""Generate Telegram bot demo screenshot."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_screenshot import (
    WIDTH, BG, CHAT_BG, draw_header, draw_message,
)


def render_demo():
    """Render the full demo screenshot."""
    height = 2200
    img = Image.new("RGB", (WIDTH, height), CHAT_BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw_header(img, draw)

    # Chat messages
    y = 100

    # User: /brief
    y = draw_message(img, draw, "/brief", y, is_user=True, mono=True)

    # Bot: generating
    y = draw_message(img, draw, "▸ Generating briefing...", y, font_size=13)

    # Bot: briefing
    briefing = """[ Web3 Research Briefing ]
Friday, 22 May 2026 — 07:00 WIB
══════════════════════════════

▸ TL;DR
  • AI agents on Base hitting parabolic growth (+40% MoM TVL)
  • Whale rotation from CEX to L2s — $7.2M moved in 24h
  • Vitalik signals decentralized AI roadmap = bullish

▸ Market Pulse
  3 whale txs detected (>$1M each):
  ► Binance14 → unknown: $4.36M ETH on Arbitrum
  ► WhaleAlpha → multisig: $1.83M ETH on Base
  ► Cobie → DAI vault: $1.09M ETH on Optimism

▸ Social Signals (Sentiment: +0.20 NEUTRAL)
  Top themes: AI agents, L2 migration, security
  Bullish narrative on Farcaster /base channel

▸ Watch List
  1. Base AI agent protocols launching this week
  2. Arbitrum DEX volume spike correlation
  3. Optimism Superchain new chain announcement"""
    y = draw_message(img, draw, briefing, y, mono=True, font_size=11)

    # User: /whales
    y = draw_message(img, draw, "/whales", y, is_user=True, mono=True)

    # Bot: whales
    whales_text = """[ Recent Whale Activity (24h) ]

► [ARBITRUM] Binance14:
   1247.50 ETH ($4,365,625)
   tx: 0xabffffff...

► [BASE] WhaleAlpha:
   523.10 ETH ($1,830,850)
   tx: 0xcdeeeeee...

► [OPTIMISM] Cobie:
   312.70 ETH ($1,094,450)
   tx: 0xef111111..."""
    y = draw_message(img, draw, whales_text, y, mono=True, font_size=11)

    # Bot: alert
    alert_text = """⚠ WHALE ALERT
Chain: ARBITRUM
Value: $4,365,625 (1247.50 ETH)
From: 0x28c6c062...
To:   0x1f9090aa...
Tx:   0xabffffff..."""
    y = draw_message(img, draw, alert_text, y, mono=True, font_size=11)

    # User: /sentiment
    y = draw_message(img, draw, "/sentiment", y, is_user=True, mono=True)

    # Bot: sentiment
    sent_text = """[ Market Sentiment (12h) ]

Score: +0.200  ◆ NEUTRAL
Posts analyzed: 47

▸ Key Themes:
  • AI agents adoption
  • L2 ecosystem growth
  • Onchain identity primitives

▸ Bullish:
  ▲ Base AI protocol explosion
  ▲ Arbitrum active wallet leadership

▸ Bearish:
  ▼ Recent unaudited protocol exploit"""
    y = draw_message(img, draw, sent_text, y, mono=True, font_size=11)

    # Crop to actual content
    img = img.crop((0, 0, WIDTH, y + 30))

    output = Path(__file__).resolve().parent.parent / "assets" / "demo_telegram.png"
    output.parent.mkdir(exist_ok=True)
    img.save(str(output), "PNG", optimize=True)
    print(f"✅ Saved: {output}")
    print(f"   Size: {img.size}")
    return str(output)


if __name__ == "__main__":
    render_demo()
