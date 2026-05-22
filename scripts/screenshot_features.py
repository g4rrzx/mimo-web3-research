"""Screenshot 5: Features overview card."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_common import (
    BG, HEADER, SURFACE, BORDER, TEXT, MUTED, CYAN, GREEN, YELLOW,
    RED, ORANGE, PURPLE, PINK, TITLE,
    draw_window, get_mono, get_sans, draw_box,
)

W, H = 1100, 760


def feature_card(draw, x, y, w, h, icon, title, desc, accent=CYAN):
    """Draw a feature card."""
    draw_box(draw, x, y, w, h, fill=SURFACE, border=accent, radius=10)
    # Icon (text-based)
    f_icon = get_sans(28, bold=True)
    draw.text((x + 18, y + 16), icon, fill=accent, font=f_icon)
    # Title
    f_title = get_sans(15, bold=True)
    draw.text((x + 60, y + 18), title, fill=TEXT, font=f_title)
    # Description (multi-line)
    f_desc = get_sans(11)
    lines = desc.split("\n")
    for i, line in enumerate(lines):
        draw.text((x + 60, y + 42 + i * 16), line, fill=MUTED, font=f_desc)


def render():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_window(draw, W, 36, "mimo-web3-research — features")

    # Title
    f_title = get_sans(22, bold=True)
    f_sub = get_sans(13)
    draw.text((40, 56), "MiMo Web3 Research Agent",
              fill=TITLE, font=f_title)
    draw.text((40, 88), "Production features powering autonomous Web3 research",
              fill=MUTED, font=f_sub)

    # Top accent line
    draw.rectangle([(40, 120), (W - 40, 122)], fill=PURPLE)

    # 6 feature cards in 3x2 grid
    cw, ch = 330, 110
    gap_x, gap_y = 20, 18
    start_x = (W - (3 * cw + 2 * gap_x)) // 2
    start_y = 145

    features = [
        ("◆", "Multi-Chain Whale Watch",
         "Track high-value txs across Arbitrum,\nBase, and Optimism. Block explorer APIs.\nConfigurable USD threshold.", ORANGE),
        ("▸", "Social Listening",
         "Farcaster channels via Neynar API +\nX accounts via xurl CLI. Engagement\nscoring and dedup built-in.", PINK),
        ("■", "News Aggregation",
         "RSS from Defiant, Bankless, Block,\nCoinDesk. Relevance scoring with\nWeb3-specific keyword weights.", YELLOW),
        ("●", "MiMo-Powered Analysis",
         "Hybrid sentiment (heuristic + deep).\nDaily briefing synthesis. SQLite-cached\nresponses to minimize API calls.", GREEN),
        ("▲", "Telegram Bot",
         "8 interactive commands: /brief,\n/whales, /social, /sentiment, /news,\n/collect, /status, /help.", CYAN),
        ("◇", "Cron-Ready Automation",
         "Two scripts for hands-free ops:\ndaily_brief.py + collect_loop.py.\nHermes + standard crontab compatible.", PURPLE),
    ]

    for i, (icon, title, desc, color) in enumerate(features):
        col = i % 3
        row = i // 3
        x = start_x + col * (cw + gap_x)
        y = start_y + row * (ch + gap_y)
        feature_card(draw, x, y, cw, ch, icon, title, desc, color)

    # Footer stats bar
    fy = 410
    draw.rectangle([(40, fy), (W - 40, fy + 2)], fill=BORDER)

    f_stat = get_mono(12, bold=True)
    f_lab = get_sans(11)
    stats = [
        ("19", "FILES", CYAN),
        ("1,925", "LINES", GREEN),
        ("5/5", "TESTS PASS", YELLOW),
        ("0", "LINT ERRORS", PURPLE),
        ("8", "BOT CMDS", ORANGE),
        ("3", "CHAINS", PINK),
    ]
    sw = (W - 80) // len(stats)
    for i, (val, lab, color) in enumerate(stats):
        cx = 40 + i * sw + sw // 2
        bbox = draw.textbbox((0, 0), val, font=get_sans(28, bold=True))
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, fy + 24), val,
                  fill=color, font=get_sans(28, bold=True))
        bbox2 = draw.textbbox((0, 0), lab, font=f_lab)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((cx - tw2 // 2, fy + 60), lab, fill=MUTED, font=f_lab)

    # Tech stack badges
    sy = 520
    draw.rectangle([(40, sy), (W - 40, sy + 2)], fill=BORDER)

    f_st_title = get_sans(13, bold=True)
    draw.text((40, sy + 16), "TECH STACK", fill=TITLE, font=f_st_title)

    badges = [
        ("Python 3.11", CYAN),
        ("Xiaomi MiMo API", GREEN),
        ("python-telegram-bot v21", PURPLE),
        ("Web3.py", ORANGE),
        ("SQLite", YELLOW),
        ("Neynar Farcaster", PINK),
        ("loguru + tenacity", RED),
    ]
    bx, by = 40, sy + 48
    f_b = get_mono(11, bold=True)
    for text, color in badges:
        bbox = draw.textbbox((0, 0), text, font=f_b)
        bw = bbox[2] - bbox[0] + 24
        if bx + bw > W - 40:
            bx = 40
            by += 36
        draw_box(draw, bx, by, bw, 26, fill=SURFACE, border=color, radius=13)
        draw.text((bx + 12, by + 6), text, fill=color, font=f_b)
        bx += bw + 10

    # Bottom tagline
    f_tag = get_sans(13)
    tagline = "Submitted to Xiaomi MiMo Orbit 100T Creator Program · github.com/g4rrzx/mimo-web3-research"
    bbox = draw.textbbox((0, 0), tagline, font=f_tag)
    tw = bbox[2] - bbox[0]
    draw.text((W // 2 - tw // 2, H - 40), tagline, fill=MUTED, font=f_tag)

    out = Path(__file__).resolve().parent.parent / "assets" / "features.png"
    img.save(str(out), "PNG", optimize=True)
    print(f"✓ Saved: {out} ({img.size})")


if __name__ == "__main__":
    render()
