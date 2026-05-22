"""Render demo output as PNG image using PIL."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Colors (Telegram dark theme)
BG = (10, 14, 39)
HEADER_BG = (23, 33, 43)
CHAT_BG = (14, 22, 33)
USER_MSG = (43, 82, 120)
BOT_MSG = (24, 37, 51)
TEXT = (232, 232, 232)
ACCENT = (106, 183, 255)
ORANGE = (255, 122, 89)
GREEN = (76, 175, 80)
GRAY = (112, 132, 153)

WIDTH = 540
PADDING = 20


def get_font(size, bold=False):
    """Get system font."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_mono(size):
    """Get monospace font."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_emoji_font(size):
    """Get emoji font."""
    path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
    if Path(path).exists():
        # NotoColorEmoji only supports specific sizes
        return ImageFont.truetype(path, 109, layout_engine=ImageFont.Layout.RAQM if hasattr(ImageFont, 'Layout') else None)
    return None


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit width."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_message(img, draw, text, y, is_user=False, mono=False, font_size=14):
    """Draw a chat bubble."""
    font = get_mono(font_size) if mono else get_font(font_size)
    max_msg_width = int(WIDTH * 0.78)
    inner_pad = 12

    lines = wrap_text(text, font, max_msg_width - 2 * inner_pad, draw)
    line_height = font_size + 6
    msg_height = len(lines) * line_height + 2 * inner_pad

    # Calculate widest line
    max_line_w = max(
        (draw.textbbox((0, 0), line, font=font)[2] for line in lines),
        default=100
    )
    bubble_width = min(max_line_w + 2 * inner_pad, max_msg_width)

    # Position
    if is_user:
        x = WIDTH - PADDING - bubble_width
        bg = USER_MSG
    else:
        x = PADDING
        bg = BOT_MSG

    # Draw rounded rectangle
    draw.rounded_rectangle(
        [(x, y), (x + bubble_width, y + msg_height)],
        radius=14,
        fill=bg,
    )

    # Draw text
    text_y = y + inner_pad
    for line in lines:
        # Highlight bold markers
        if line.startswith("**") and line.endswith("**"):
            line = line[2:-2]
            draw.text((x + inner_pad, text_y), line, fill=ACCENT, font=font)
        elif "🚨" in line or "🐋" in line or "📊" in line:
            draw.text((x + inner_pad, text_y), line, fill=ORANGE, font=font)
        else:
            draw.text((x + inner_pad, text_y), line, fill=TEXT, font=font)
        text_y += line_height

    return y + msg_height + 8


def draw_header(img, draw):
    """Draw bot header."""
    # Header background
    draw.rectangle([(0, 0), (WIDTH, 80)], fill=HEADER_BG)

    # Avatar circle
    draw.ellipse([(20, 16), (68, 64)], fill=ORANGE)
    font_avatar = get_font(28, bold=True)
    bbox = draw.textbbox((0, 0), "M", font=font_avatar)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((44 - text_w // 2, 40 - text_h // 2 - 2),
              "M", fill=(255, 255, 255), font=font_avatar)

    # Bot name
    font_name = get_font(15, bold=True)
    draw.text((84, 22), "MiMo Web3 Research Bot",
              fill=(255, 255, 255), font=font_name)

    # Status
    font_status = get_font(12)
    draw.text((84, 44), "online · powered by Xiaomi MiMo",
              fill=GRAY, font=font_status)
