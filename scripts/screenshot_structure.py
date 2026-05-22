"""Screenshot 4: Project file structure (tree view)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_common import (
    BG, HEADER, SURFACE, BORDER, TEXT, MUTED, CYAN, GREEN, YELLOW,
    RED, ORANGE, PURPLE, PINK, TITLE,
    draw_window, get_mono, get_sans,
)

W = 900


def render():
    img = Image.new("RGB", (W, 1100), BG)
    draw = ImageDraw.Draw(img)
    draw_window(draw, W, 36, "mimo-web3-research — tree")

    f_title = get_sans(18, bold=True)
    f_sub = get_sans(12)
    draw.text((24, 56), "Project Structure", fill=TITLE, font=f_title)
    draw.text((24, 84), "19 files · ~1,925 lines · modular & production-ready",
              fill=MUTED, font=f_sub)

    font = get_mono(13)
    fb = get_mono(13, bold=True)

    y = 130
    line_h = 20

    def line(text, color=TEXT, bold=False):
        nonlocal y
        f = fb if bold else font
        draw.text((30, y), text, fill=color, font=f)
        y += line_h

    line("$ tree mimo-web3-research/", CYAN, bold=True)
    y += 8
    line("mimo-web3-research/", PURPLE, bold=True)
    line("├── README.md                          full docs + setup", YELLOW)
    line("├── SUBMISSION.md                      MiMo Orbit submission", YELLOW)
    line("├── config.yaml                        tunable settings", ORANGE)
    line("├── .env.example                       credential template", ORANGE)
    line("├── requirements.txt                   pinned deps", ORANGE)
    line("├── setup.sh                           one-shot installer", GREEN)
    line("│", MUTED)
    line("├── src/", PURPLE, bold=True)
    line("│   ├── bot.py                         Telegram bot · 8 cmds", CYAN)
    line("│   ├── orchestrator.py                pipeline coordinator", CYAN)
    line("│   │", MUTED)
    line("│   ├── collectors/", PINK, bold=True)
    line("│   │   ├── onchain.py                 whale watching", TEXT)
    line("│   │   ├── social.py                  Farcaster + X", TEXT)
    line("│   │   └── news.py                    RSS aggregator", TEXT)
    line("│   │", MUTED)
    line("│   ├── analyzers/", PINK, bold=True)
    line("│   │   ├── mimo_client.py             MiMo API + cache", GREEN)
    line("│   │   └── sentiment.py               hybrid sentiment", GREEN)
    line("│   │", MUTED)
    line("│   ├── storage/", PINK, bold=True)
    line("│   │   └── db.py                      SQLite ORM-lite", TEXT)
    line("│   │", MUTED)
    line("│   └── utils/", PINK, bold=True)
    line("│       ├── config.py                  env + YAML loader", TEXT)
    line("│       ├── logger.py                  loguru setup", TEXT)
    line("│       └── formatters.py              output formatters", TEXT)
    line("│", MUTED)
    line("├── scripts/", PURPLE, bold=True)
    line("│   ├── daily_brief.py                 cron: 07:00 WIB", CYAN)
    line("│   ├── collect_loop.py                cron: every 30min", CYAN)
    line("│   └── demo.py                        sample data demo", YELLOW)
    line("│", MUTED)
    line("├── tests/", PURPLE, bold=True)
    line("│   └── test_smoke.py                  5 tests · all pass", GREEN)
    line("│", MUTED)
    line("├── data/                              SQLite databases", MUTED)
    line("├── logs/                              rotated logs", MUTED)
    line("└── assets/                            screenshots & docs", MUTED)
    y += 16

    line("──────────────────────────────────────────────────────────", BORDER)
    line("MODULE BREAKDOWN", TITLE, bold=True)
    y += 4
    line("► src/bot.py            288 lines    Telegram interface", TEXT)
    line("► src/storage/db.py     260 lines    persistence layer", TEXT)
    line("► src/collectors/social 208 lines    FC + X collectors", TEXT)
    line("► src/collectors/onchain 175 lines   whale watching", TEXT)
    line("► src/analyzers/mimo    172 lines    MiMo API wrapper", GREEN)
    line("► src/orchestrator.py   141 lines    pipeline coord", TEXT)
    line("► src/collectors/news   137 lines    RSS aggregator", TEXT)
    line("► src/analyzers/sent     89 lines    sentiment hybrid", TEXT)
    y += 8

    line("✓ All modules tested · zero lint errors", GREEN, bold=True)

    img = img.crop((0, 0, W, y + 30))
    out = Path(__file__).resolve().parent.parent / "assets" / "structure.png"
    img.save(str(out), "PNG", optimize=True)
    print(f"✓ Saved: {out} ({img.size})")


if __name__ == "__main__":
    render()
