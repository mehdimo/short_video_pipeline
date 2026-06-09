"""Python syntax highlighting utilities for code frame rendering."""

import re
import keyword as _kwmod
from PIL import ImageDraw


PYTHON_KEYWORDS = frozenset(_kwmod.kwlist)

KEYWORD_COLOR = (255, 123, 114)   # GitHub dark keyword red
STRING_COLOR  = (255, 212, 120)   # warm yellow for string literals
NUMBER_COLOR  = (121, 192, 255)   # light blue for numeric literals
COMMENT_COLOR = (139, 148, 158)   # GitHub dark comment gray
CODE_GREEN    = (163, 230, 136)   # default identifier/function color

# Tokenizer: strings first so 'None' stays a string, not a keyword.
# [^'"\w]+ excludes quote chars so it can't swallow a string opener.
_TOKEN_RE = re.compile(
    r"'[^']*'"
    r'|"[^"]*"'
    r"|\b\d+\.?\d*\b"
    r"|\b\w+\b"
    r"|[^'\"\w]+"
)


def _token_style(token: str) -> tuple[tuple, bool]:
    """Return (color, bold) for a single code token."""
    if token[0] in ("'", '"'):
        return STRING_COLOR, False
    if re.fullmatch(r"\d+\.?\d*", token):
        return NUMBER_COLOR, False
    if token in PYTHON_KEYWORDS:
        return KEYWORD_COLOR, True
    return CODE_GREEN, False


def _split_comment(line: str) -> tuple[str, str]:
    """Split a code line into (code_part, comment_part).

    Tracks open string literals so a '#' inside a string is not treated as a
    comment marker. comment_part includes the leading '#'.
    """
    in_str: str | None = None
    for i, ch in enumerate(line):
        if in_str:
            if ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'"):
                in_str = ch
            elif ch == "#":
                return line[:i], line[i:]
    return line, ""


def draw_code_body(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font) -> None:
    """Draw syntax-highlighted code text onto *draw*.

    Token colors: keywords (bold red), strings (yellow), numbers (blue),
    comments (flat gray — no inner highlighting).
    """
    char_w = draw.textbbox((0, 0), "W", font=font)[2]
    line_h = font.size + 8

    for line in text.split("\n"):
        code_part, comment_part = _split_comment(line)
        cx = x

        for token in _TOKEN_RE.findall(code_part):
            color, bold = _token_style(token)
            if bold:
                draw.text((cx, y), token, font=font, fill=color,
                          stroke_width=1, stroke_fill=color)
            else:
                draw.text((cx, y), token, font=font, fill=color)
            cx += len(token) * char_w

        if comment_part:
            draw.text((cx, y), comment_part, font=font, fill=COMMENT_COLOR)

        y += line_h
