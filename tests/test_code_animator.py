"""Tests for code_animator.py — typing animation clip generation."""

import pytest
import numpy as np


def _null_render(section: dict) -> np.ndarray:
    return np.zeros((1920, 1080, 3), dtype=np.uint8)


@pytest.fixture()
def code_section():
    return {
        "type": "code",
        "heading": "Test Code",
        "body": "def foo():\n    return 1",
        "on_screen_text": "",
    }


class TestMakeTypingClip:
    def test_clip_duration_matches_requested(self, code_section):
        from code_animator import make_typing_clip
        clip = make_typing_clip(code_section, duration=5.0, render_fn=_null_render, fps=24)
        assert abs(clip.duration - 5.0) < 0.01

    def test_clip_fps_matches_requested(self, code_section):
        from code_animator import make_typing_clip
        clip = make_typing_clip(code_section, duration=3.0, render_fn=_null_render, fps=12)
        assert clip.fps == 12

    def test_frame_shape_matches_render_fn(self, code_section):
        from code_animator import make_typing_clip
        clip = make_typing_clip(code_section, duration=3.0, render_fn=_null_render, fps=24)
        frame = clip.get_frame(1.0)
        assert frame.shape == (1920, 1080, 3)

    def test_full_body_key_passed_to_render_fn(self, code_section):
        from code_animator import make_typing_clip
        captured = []
        def render_fn(sec):
            captured.append(sec)
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(code_section, duration=5.0, render_fn=render_fn, fps=1)
        clip.get_frame(0.5)
        assert "_full_body" in captured[-1]
        assert captured[-1]["_full_body"] == code_section["body"]

    def test_partial_code_at_start(self, code_section):
        from code_animator import make_typing_clip
        captured = []
        def render_fn(sec):
            captured.append(sec["body"])
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(code_section, duration=10.0, render_fn=render_fn, fps=24)
        clip.get_frame(0.1)
        body = captured[-1]
        full = code_section["body"]
        # At t=0.1 out of 10.0s × 0.88, only a small portion should be visible
        # body ends with cursor char, so strip it before comparing length
        assert len(body.rstrip("| ")) < len(full)

    def test_full_code_at_end(self, code_section):
        from code_animator import make_typing_clip
        captured = []
        def render_fn(sec):
            captured.append(sec["body"])
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(code_section, duration=5.0, render_fn=render_fn, fps=24)
        clip.get_frame(5.0)
        assert captured[-1] == code_section["body"]

    def test_cursor_present_during_typing_phase(self, code_section):
        from code_animator import make_typing_clip
        captured = []
        def render_fn(sec):
            captured.append(sec["body"])
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(code_section, duration=10.0, render_fn=render_fn, fps=24)
        clip.get_frame(1.0)  # well within 0.88 * 10 = 8.8s typing phase
        body = captured[-1]
        assert body[-1] in ("|", " ")

    def test_no_cursor_after_typing_phase(self, code_section):
        from code_animator import make_typing_clip
        captured = []
        def render_fn(sec):
            captured.append(sec["body"])
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(code_section, duration=5.0, render_fn=render_fn, fps=24)
        clip.get_frame(5.0)
        # At exactly duration, body should equal full_code — no cursor appended
        assert captured[-1] == code_section["body"]

    def test_original_section_not_mutated(self, code_section):
        from code_animator import make_typing_clip
        original_body = code_section["body"]
        clip = make_typing_clip(code_section, duration=3.0, render_fn=_null_render, fps=24)
        clip.get_frame(0.5)
        assert code_section["body"] == original_body

    def test_single_char_body(self):
        from code_animator import make_typing_clip
        section = {"type": "code", "heading": "H", "body": "x", "on_screen_text": ""}
        clip = make_typing_clip(section, duration=2.0, render_fn=_null_render, fps=24)
        assert abs(clip.duration - 2.0) < 0.01

    def test_empty_body_does_not_crash(self):
        from code_animator import make_typing_clip
        section = {"type": "code", "heading": "H", "body": "", "on_screen_text": ""}
        captured = []
        def render_fn(sec):
            captured.append(sec)
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        clip = make_typing_clip(section, duration=3.0, render_fn=render_fn, fps=24)
        clip.get_frame(1.0)
        assert len(captured) > 0
