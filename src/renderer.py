"""Renders content sections to NumPy image frames (1080×1920 portrait)."""

import numpy as np
from PIL import Image, ImageDraw

from fonts import load_font
from syntax import draw_code_body


WIDTH, HEIGHT = 1080, 1920
FPS = 24

BG          = (13,  17,  23)
ACCENT      = (88,  166, 255)
WHITE       = (255, 255, 255)
LIGHT_GRAY  = (201, 209, 217)
CODE_BG     = (22,  27,  34)
SUBTITLE_BG = (20,  30,  50)


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def draw_centered(draw, text, y, font, color):
    for line in text.split("\n"):
        w = text_width(draw, line, font)
        draw.text(((WIDTH - w) // 2, y), line, font=font, fill=color)
        y += font.size + 10
    return y


def draw_left(draw, text, x, y, font, color):
    for line in text.split("\n"):
        draw.text((x, y), line, font=font, fill=color)
        y += font.size + 8
    return y


def render_frame(section: dict) -> np.ndarray:
    img  = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    f_title    = load_font(100)
    f_heading  = load_font(72)
    f_body     = load_font(50)
    f_code     = load_font(38, mono=True)
    f_subtitle = load_font(44)

    stype = section["type"]

    if stype == "title":
        y = HEIGHT // 2 - 130
        y = draw_centered(draw, section["heading"], y, f_title, WHITE)
        draw.line([(WIDTH // 2 - 160, y + 20), (WIDTH // 2 + 160, y + 20)], fill=ACCENT, width=5)

    else:
        y = 130
        y = draw_centered(draw, section["heading"], y, f_heading, ACCENT)
        draw.line([(80, y + 10), (WIDTH - 80, y + 10)], fill=ACCENT, width=2)
        y += 40

        body = section.get("body", "")
        if stype == "code":
            # size the box from the complete code so it never jumps during typing
            full_body = section.get("_full_body", body)
            line_h    = f_code.size + 8
            box_h     = len(full_body.split("\n")) * line_h + 60
            pad_x     = 60
            draw.rectangle(
                [(pad_x, y), (WIDTH - pad_x, y + box_h)],
                fill=CODE_BG, outline=ACCENT, width=2,
            )
            draw_code_body(draw, body, pad_x + 28, y + 28, f_code)
        else:
            draw_centered(draw, body, y, f_body, LIGHT_GRAY)

    on_screen_text = section.get("on_screen_text", "")
    if on_screen_text:
        bar_h = 110
        bar_y = HEIGHT - bar_h - 50
        draw.rectangle([(0, bar_y), (WIDTH, bar_y + bar_h)], fill=SUBTITLE_BG)
        sub_y = bar_y + (bar_h - f_subtitle.size) // 2
        draw_centered(draw, on_screen_text, sub_y, f_subtitle, WHITE)

    return np.array(img)
