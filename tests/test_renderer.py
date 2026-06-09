"""Tests for renderer.py — draw helpers and frame rendering."""

import pytest
import numpy as np
from PIL import Image, ImageDraw


@pytest.fixture(autouse=True)
def clear_font_cache():
    from fonts import _font_cache
    _font_cache.clear()
    yield
    _font_cache.clear()


@pytest.fixture()
def draw_surface():
    img = Image.new("RGB", (1080, 1920), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    return draw


@pytest.fixture()
def font_48():
    from fonts import load_font
    return load_font(48)


class TestTextWidth:
    def test_positive_for_nonempty_text(self, draw_surface, font_48):
        from renderer import text_width
        w = text_width(draw_surface, "Hello", font_48)
        assert w > 0

    def test_longer_text_is_wider(self, draw_surface, font_48):
        from renderer import text_width
        w_short = text_width(draw_surface, "Hi", font_48)
        w_long  = text_width(draw_surface, "Hello World Extended", font_48)
        assert w_long > w_short

    def test_single_char_width(self, draw_surface, font_48):
        from renderer import text_width
        w = text_width(draw_surface, "A", font_48)
        assert w > 0


class TestDrawCentered:
    def test_returns_incremented_y(self, draw_surface, font_48):
        from renderer import draw_centered
        y_end = draw_centered(draw_surface, "Hello", 100, font_48, (255, 255, 255))
        assert y_end > 100

    def test_multiline_increments_more(self, draw_surface, font_48):
        from renderer import draw_centered
        y_one  = draw_centered(draw_surface, "Line 1", 100, font_48, (255, 255, 255))
        y_two  = draw_centered(draw_surface, "Line 1\nLine 2", 100, font_48, (255, 255, 255))
        assert y_two > y_one

    def test_does_not_raise_for_empty_string(self, draw_surface, font_48):
        from renderer import draw_centered
        draw_centered(draw_surface, "", 100, font_48, (255, 255, 255))


class TestDrawLeft:
    def test_returns_incremented_y(self, draw_surface, font_48):
        from renderer import draw_left
        y_end = draw_left(draw_surface, "Hello", 50, 100, font_48, (255, 255, 255))
        assert y_end > 100

    def test_multiline_increments_more(self, draw_surface, font_48):
        from renderer import draw_left
        y_one = draw_left(draw_surface, "Line 1", 50, 100, font_48, (255, 255, 255))
        y_two = draw_left(draw_surface, "Line 1\nLine 2", 50, 100, font_48, (255, 255, 255))
        assert y_two > y_one


class TestRenderFrame:
    def _title_section(self, on_screen_text=""):
        return {"type": "title", "heading": "Test\nTitle", "on_screen_text": on_screen_text}

    def _text_section(self, on_screen_text="Subtitle"):
        return {"type": "text", "heading": "Heading", "body": "Body text here", "on_screen_text": on_screen_text}

    def _code_section(self, body="def foo():\n    pass", on_screen_text=""):
        return {"type": "code", "heading": "Code", "body": body, "on_screen_text": on_screen_text}

    def test_title_frame_shape(self):
        from renderer import render_frame
        frame = render_frame(self._title_section())
        assert frame.shape == (1920, 1080, 3)

    def test_text_frame_shape(self):
        from renderer import render_frame
        frame = render_frame(self._text_section())
        assert frame.shape == (1920, 1080, 3)

    def test_code_frame_shape(self):
        from renderer import render_frame
        frame = render_frame(self._code_section())
        assert frame.shape == (1920, 1080, 3)

    def test_returns_numpy_array(self):
        from renderer import render_frame
        frame = render_frame(self._title_section())
        assert isinstance(frame, np.ndarray)

    def test_dtype_is_uint8(self):
        from renderer import render_frame
        frame = render_frame(self._title_section())
        assert frame.dtype == np.uint8

    def test_not_all_zero(self):
        from renderer import render_frame
        frame = render_frame(self._title_section())
        assert not np.all(frame == 0)

    def test_on_screen_text_bar_visible(self):
        from renderer import render_frame
        frame_with = render_frame(self._title_section(on_screen_text="subtitle"))
        frame_without = render_frame(self._title_section(on_screen_text=""))
        # Bottom area should differ when on_screen_text is present
        assert not np.array_equal(frame_with[1700:], frame_without[1700:])

    def test_code_with_full_body_uses_stable_box(self):
        from renderer import render_frame
        section = {
            "type": "code",
            "heading": "Code",
            "body": "def",
            "_full_body": "def foo():\n    return 1\n    pass",
            "on_screen_text": "",
        }
        frame = render_frame(section)
        assert frame.shape == (1920, 1080, 3)

    def test_code_without_full_body_key(self):
        from renderer import render_frame
        frame = render_frame(self._code_section())
        assert frame.shape == (1920, 1080, 3)

    def test_missing_body_defaults_to_empty(self):
        from renderer import render_frame
        section = {"type": "text", "heading": "H", "on_screen_text": ""}
        frame = render_frame(section)
        assert frame.shape == (1920, 1080, 3)

    def test_title_heading_with_newline(self):
        from renderer import render_frame
        frame = render_frame({"type": "title", "heading": "Line 1\nLine 2", "on_screen_text": ""})
        assert frame.shape == (1920, 1080, 3)

    def test_dimensions_constant(self):
        from renderer import WIDTH, HEIGHT
        assert WIDTH == 1080
        assert HEIGHT == 1920
