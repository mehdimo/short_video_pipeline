"""Tests for fonts.py — font loading and caching."""

import pytest
from PIL import ImageFont


class TestLoadHelper:
    def test_nonexistent_path_returns_default(self):
        from fonts import _load
        font = _load(["/nonexistent/font.ttf", "/also/missing.ttf"], 48)
        assert font is not None

    def test_valid_candidate_is_loaded(self):
        import os
        from fonts import _load, _REGULAR_CANDIDATES
        # Find the first available regular font candidate
        available = [p for p in _REGULAR_CANDIDATES if os.path.exists(p)]
        if not available:
            pytest.skip("no system fonts available on this machine")
        font = _load(available, 48)
        assert font is not None

    def test_empty_candidates_returns_default(self):
        from fonts import _load
        font = _load([], 48)
        assert font is not None


class TestLoadFont:
    def setup_method(self):
        from fonts import _font_cache
        _font_cache.clear()

    def test_returns_font_object(self):
        from fonts import load_font
        font = load_font(48)
        assert font is not None

    def test_mono_returns_font(self):
        from fonts import load_font
        font = load_font(38, mono=True)
        assert font is not None

    def test_cache_returns_same_instance(self):
        from fonts import load_font
        font1 = load_font(36)
        font2 = load_font(36)
        assert font1 is font2

    def test_different_size_different_instance(self):
        from fonts import load_font
        font_small = load_font(24)
        font_large = load_font(72)
        # Different sizes should not be the same cached object
        assert font_small is not font_large

    def test_mono_and_regular_are_different_cache_keys(self):
        from fonts import load_font, _font_cache
        load_font(48, mono=False)
        load_font(48, mono=True)
        assert (48, False) in _font_cache
        assert (48, True) in _font_cache

    def test_cache_key_is_size_mono_tuple(self):
        from fonts import load_font, _font_cache
        load_font(50)
        assert (50, False) in _font_cache

    def test_various_sizes_load_without_error(self):
        from fonts import load_font
        for size in [24, 36, 44, 50, 72, 100]:
            font = load_font(size)
            assert font is not None
