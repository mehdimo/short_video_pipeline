"""Font loading with per-size caching for frame rendering."""

import os
from pathlib import Path
from PIL import ImageFont


_FONTS_DIR = Path(__file__).parent / "fonts"

_REGULAR_CANDIDATES = [
    str(_FONTS_DIR / "HelveticaNeue.ttc"),
    str(_FONTS_DIR / "Geneva.ttf"),
]
_MONO_CANDIDATES = [
    str(_FONTS_DIR / "SFNSMono.ttf"),
    str(_FONTS_DIR / "Menlo.ttc"),
]


def _load(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


_font_cache: dict = {}


def load_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, mono)
    if key not in _font_cache:
        _font_cache[key] = _load(_MONO_CANDIDATES if mono else _REGULAR_CANDIDATES, size)
    return _font_cache[key]
