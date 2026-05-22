"""Shared rendering utilities for screenshots."""
from pathlib import Path
from PIL import ImageFont

# Tokyo Night palette
BG = (26, 27, 38)
SURFACE = (32, 35, 53)
HEADER = (16, 17, 28)
BORDER = (60, 65, 95)
TITLE = (122, 162, 247)
TEXT = (192, 202, 245)
MUTED = (86, 95, 137)
DIM = (60, 65, 95)
CYAN = (125, 207, 255)
GREEN = (158, 206, 106)
YELLOW = (224, 175, 104)
RED = (247, 118, 142)
ORANGE = (255, 158, 100)
PURPLE = (187, 154, 247)
PINK = (217, 119, 169)


def get_mono(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_sans(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_window(draw, w, h, title="mimo-web3-research"):
    """Draw macOS-style window chrome at top."""
    draw.rectangle([(0, 0), (w, 36)], fill=HEADER)
    # Traffic lights
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx, cy = 18 + i * 22, 18
        draw.ellipse([(cx - 7, cy - 7), (cx + 7, cy + 7)], fill=color)
    # Title centered
    font = get_mono(12)
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((w // 2 - tw // 2, 11), title, fill=MUTED, font=font)


def draw_box(draw, x, y, w, h, fill=SURFACE, border=BORDER, radius=8):
    """Rounded box."""
    draw.rounded_rectangle([(x, y), (x + w, y + h)],
                            radius=radius, fill=fill, outline=border, width=1)


def draw_line(draw, x, y, parts, font=None):
    """Draw colored text segments inline."""
    if font is None:
        font = get_mono(12)
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        bbox = draw.textbbox((0, 0), text, font=font)
        cx += bbox[2] - bbox[0]
    return cx
