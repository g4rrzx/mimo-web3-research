"""Screenshot 2: Terminal CLI demo output."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_common import (
    BG, HEADER, SURFACE, BORDER, TEXT, MUTED, CYAN, GREEN, YELLOW,
    RED, ORANGE, PURPLE, PINK, TITLE,
    draw_window, get_mono,
)

W = 980


def render():
    img = Image.new("RGB", (W, 1100), BG)
    draw = ImageDraw.Draw(img)
    draw_window(draw, W, 36, "mimo-web3-research — python scripts/demo.py")

    font = get_mono(13)
    fb = get_mono(13, bold=True)
    y = 56
    line_h = 19

    def line(text, color=TEXT, bold=False, indent=0):
        nonlocal y
        f = fb if bold else font
        draw.text((20 + indent, y), text, fill=color, font=f)
        y += line_h

    # Prompt
    line("$ python scripts/demo.py", CYAN, bold=True)
    y += 4
    line("✓ Seeded 3 whales, 5 posts, 4 news", GREEN)
    y += 8

    # Header banner
    draw.rectangle([(20, y), (W - 20, y + 4)], fill=PURPLE)
    y += 12
    line("[ Web3 Research Briefing ]", TITLE, bold=True)
    line("Friday, 22 May 2026 — 18:51 WIB", MUTED)
    draw.rectangle([(20, y + 2), (W - 20, y + 5)], fill=PURPLE)
    y += 14

    # Whale section
    line("▸ WHALE ACTIVITY (24h)", ORANGE, bold=True)
    line("─" * 60, BORDER)
    line("► [ARBITRUM]  Binance14:    1247.50 ETH  ($4,365,625)", TEXT)
    line("              tx: 0xabffffff...", MUTED, indent=20)
    line("► [BASE]      WhaleAlpha:    523.10 ETH  ($1,830,850)", TEXT)
    line("              tx: 0xcdeeeeee...", MUTED, indent=20)
    line("► [OPTIMISM]  Cobie:         312.70 ETH  ($1,094,450)", TEXT)
    line("              tx: 0xef111111...", MUTED, indent=20)
    y += 6

    # Sentiment
    line("▸ SENTIMENT ANALYSIS", YELLOW, bold=True)
    line("─" * 60, BORDER)
    line("◆ Overall: +0.200 (5 posts) [NEUTRAL]", TEXT)
    line("◆ Hybrid score: heuristic 0.180 + MiMo deep 0.220", MUTED)
    y += 6

    # Social
    line("▸ TOP SOCIAL POSTS", CYAN, bold=True)
    line("─" * 60, BORDER)
    line("[X]  @VitalikButerin  (4521 eng)", PURPLE)
    line('     "Decentralized AI agents need better onchain identity', TEXT)
    line('     primitives. Working on EIP for agent-to-agent..."', TEXT)
    line("[X]  @0xfoobar  (892 eng)", PURPLE)
    line('     "Massive exploit discovered in unaudited protocol.', TEXT)
    line('     $4M drained. Always check audits..."', TEXT)
    line("[FC] @dwr.eth  (245 eng)", PINK)
    line('     "AI agents on Base are about to explode. New protocols', TEXT)
    line('     launching weekly, TVL up 40% MoM..."', TEXT)
    y += 6

    # News
    line("▸ NEWS HIGHLIGHTS", GREEN, bold=True)
    line("─" * 60, BORDER)
    line("[Bankless]    AI Agents on Base: The New Frontier      (rel:0.95)", TEXT)
    line("[The Defiant] Arbitrum Hits $5B TVL Milestone           (rel:0.85)", TEXT)
    line("[CoinDesk]    Vitalik Outlines Decentralized AI Roadmap (rel:0.75)", TEXT)
    line("[The Block]   Optimism Superchain Adds Three Members    (rel:0.65)", TEXT)
    y += 6

    # Alert
    line("▸ WHALE ALERT TRIGGERED", RED, bold=True)
    line("─" * 60, BORDER)
    line("⚠  Chain: ARBITRUM", RED)
    line("   Value: $4,365,625 (1247.50 ETH)", TEXT)
    line("   From:  0x28c6c062...", MUTED)
    line("   To:    0x1f9090aa...", MUTED)
    line("   → Telegram alert sent", GREEN)
    y += 8

    line("✓ Demo complete — Production-ready pipeline", GREEN, bold=True)
    line("─" * 60, BORDER)
    line("$ _", CYAN)

    img = img.crop((0, 0, W, y + 30))
    out = Path(__file__).resolve().parent.parent / "assets" / "demo_cli.png"
    img.save(str(out), "PNG", optimize=True)
    print(f"✓ Saved: {out} ({img.size})")


if __name__ == "__main__":
    render()
