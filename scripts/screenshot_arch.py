"""Screenshot 3: System architecture diagram."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_common import (
    BG, HEADER, SURFACE, BORDER, TEXT, MUTED, CYAN, GREEN, YELLOW,
    RED, ORANGE, PURPLE, PINK, TITLE,
    draw_window, get_mono, get_sans, draw_box,
)

W, H = 1100, 750


def box(draw, x, y, w, h, label, sub="", color=CYAN, fill=SURFACE):
    """Draw a labeled component box."""
    draw_box(draw, x, y, w, h, fill=fill, border=color, radius=8)
    f1 = get_sans(14, bold=True)
    f2 = get_mono(11)
    bbox = draw.textbbox((0, 0), label, font=f1)
    tw = bbox[2] - bbox[0]
    draw.text((x + w // 2 - tw // 2, y + 12), label, fill=color, font=f1)
    if sub:
        bbox2 = draw.textbbox((0, 0), sub, font=f2)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((x + w // 2 - tw2 // 2, y + 34), sub, fill=MUTED, font=f2)


def arrow(draw, x1, y1, x2, y2, color=BORDER, width=2):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # Arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    al = 8
    p1 = (x2 - al * math.cos(angle - math.pi / 6),
          y2 - al * math.sin(angle - math.pi / 6))
    p2 = (x2 - al * math.cos(angle + math.pi / 6),
          y2 - al * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), p1, p2], fill=color)


def render():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_window(draw, W, 36, "mimo-web3-research — architecture")

    # Title
    f_title = get_sans(20, bold=True)
    f_sub = get_sans(13)
    draw.text((40, 56), "MiMo Web3 Research Agent", fill=TITLE, font=f_title)
    draw.text((40, 86), "Production architecture · 4 layers · MiMo at the core",
              fill=MUTED, font=f_sub)

    # Layer labels
    f_layer = get_mono(11, bold=True)
    layers = [
        (130, "INTERFACE"),
        (230, "ORCHESTRATION"),
        (350, "DATA COLLECTION"),
        (510, "STORAGE & ANALYSIS"),
    ]
    for y, label in layers:
        draw.text((20, y), label, fill=MUTED, font=f_layer)

    # Telegram Bot (top)
    box(draw, 380, 130, 340, 60,
        "Telegram Bot Interface",
        "/brief /whales /sentiment /collect ...",
        color=CYAN)

    # Orchestrator
    box(draw, 380, 230, 340, 60,
        "Research Orchestrator",
        "coordinates pipeline · alerts · briefings",
        color=PURPLE)

    # Collectors row
    box(draw, 90, 350, 240, 70,
        "On-Chain Collector",
        "Arbiscan · Basescan · Etherscan",
        color=ORANGE)
    box(draw, 430, 350, 240, 70,
        "Social Collector",
        "Farcaster (Neynar) · X (xurl)",
        color=PINK)
    box(draw, 770, 350, 240, 70,
        "News Collector",
        "Defiant · Bankless · Block · Coindesk",
        color=YELLOW)

    # MiMo center (highlighted)
    box(draw, 360, 510, 380, 80,
        "Xiaomi MiMo API",
        "sentiment · summarize · briefing gen",
        color=GREEN, fill=(40, 60, 50))

    # Storage flanking
    box(draw, 90, 510, 240, 80,
        "SQLite Storage",
        "whales · posts · news · cache",
        color=CYAN)
    box(draw, 770, 510, 240, 80,
        "Sentiment Analyzer",
        "hybrid: heuristic + MiMo deep",
        color=RED)

    # Arrows
    # Bot ↔ Orchestrator
    arrow(draw, 550, 190, 550, 230)
    arrow(draw, 540, 230, 540, 190)
    # Orchestrator → 3 Collectors
    arrow(draw, 480, 290, 210, 350)
    arrow(draw, 550, 290, 550, 350)
    arrow(draw, 620, 290, 890, 350)
    # Collectors → Storage
    arrow(draw, 210, 420, 210, 510)
    arrow(draw, 550, 420, 550, 510)
    arrow(draw, 890, 420, 890, 510)
    # Center connections
    arrow(draw, 550, 510, 890, 510)
    arrow(draw, 360, 550, 330, 550)

    # Footer note
    f_note = get_mono(11)
    notes = [
        "▸ MiMo API powers core reasoning: sentiment scoring, summarization,",
        "  daily briefing generation with Web3-context-aware prompts",
        "▸ All collectors are pluggable & rate-limited (tenacity retry)",
        "▸ Cron-ready: scripts/daily_brief.py + scripts/collect_loop.py",
    ]
    for i, note in enumerate(notes):
        draw.text((40, 620 + i * 18), note, fill=MUTED, font=f_note)

    out = Path(__file__).resolve().parent.parent / "assets" / "architecture.png"
    img.save(str(out), "PNG", optimize=True)
    print(f"✓ Saved: {out} ({img.size})")


if __name__ == "__main__":
    render()
