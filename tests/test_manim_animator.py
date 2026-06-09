"""Tests for manim_animator.py — cache key logic and code cleaner."""

import hashlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCacheDir:
    def test_creates_directory(self, tmp_path):
        from manim_animator import _cache_dir
        cache = _cache_dir(str(tmp_path), "some narration", "full context")
        assert cache.exists()
        assert cache.is_dir()

    def test_same_inputs_produce_same_path(self, tmp_path):
        from manim_animator import _cache_dir
        c1 = _cache_dir(str(tmp_path), "narration", "context")
        c2 = _cache_dir(str(tmp_path), "narration", "context")
        assert c1 == c2

    def test_different_narration_produces_different_path(self, tmp_path):
        from manim_animator import _cache_dir
        c1 = _cache_dir(str(tmp_path), "narration A", "context")
        c2 = _cache_dir(str(tmp_path), "narration B", "context")
        assert c1 != c2

    def test_different_full_narration_produces_different_path(self, tmp_path):
        from manim_animator import _cache_dir
        c1 = _cache_dir(str(tmp_path), "narration", "context A")
        c2 = _cache_dir(str(tmp_path), "narration", "context B")
        assert c1 != c2

    def test_key_is_12_char_hex(self, tmp_path):
        from manim_animator import _cache_dir
        cache = _cache_dir(str(tmp_path), "n", "f")
        assert len(cache.name) == 12
        assert all(c in "0123456789abcdef" for c in cache.name)

    def test_key_matches_expected_md5(self, tmp_path):
        from manim_animator import _cache_dir
        narration, full = "test narration", "full ctx"
        expected = hashlib.md5((narration + full).encode()).hexdigest()[:12]
        cache = _cache_dir(str(tmp_path), narration, full)
        assert cache.name == expected

    def test_empty_strings_still_create_dir(self, tmp_path):
        from manim_animator import _cache_dir
        cache = _cache_dir(str(tmp_path), "", "")
        assert cache.exists()

    def test_returns_path_object(self, tmp_path):
        from manim_animator import _cache_dir
        result = _cache_dir(str(tmp_path), "n", "f")
        assert isinstance(result, Path)


class TestClean:
    def test_removes_from_manim_import(self):
        from manim_animator import _clean
        result = _clean("from manim import *\nclass AnimationScene(Scene): pass")
        assert "from manim" not in result
        assert "AnimationScene" in result

    def test_removes_import_manim(self):
        from manim_animator import _clean
        result = _clean("import manim\nclass AnimationScene(Scene): pass")
        assert "import manim" not in result

    def test_removes_config_dot_lines(self):
        from manim_animator import _clean
        result = _clean("config.frame_width = 4.5\nclass AnimationScene(Scene): pass")
        assert "config." not in result

    def test_removes_markdown_opening_fence(self):
        from manim_animator import _clean
        result = _clean("```python\nclass AnimationScene(Scene): pass")
        assert "```" not in result

    def test_removes_markdown_closing_fence(self):
        from manim_animator import _clean
        result = _clean("class AnimationScene(Scene): pass\n```")
        assert "```" not in result

    def test_preserves_class_definition(self):
        from manim_animator import _clean
        code = "class AnimationScene(Scene):\n    def construct(self):\n        pass"
        result = _clean(code)
        assert "class AnimationScene" in result
        assert "construct" in result

    def test_empty_string_returns_empty(self):
        from manim_animator import _clean
        assert _clean("") == ""

    def test_preserves_regular_import(self):
        from manim_animator import _clean
        # non-manim imports should not be stripped
        code = "import math\nclass AnimationScene(Scene): pass"
        result = _clean(code)
        assert "import math" in result

    def test_multiple_stray_lines_all_removed(self):
        from manim_animator import _clean
        code = (
            "from manim import *\n"
            "import manim\n"
            "config.frame_width = 4.5\n"
            "```\n"
            "class AnimationScene(Scene): pass\n"
            "```"
        )
        result = _clean(code)
        assert "from manim" not in result
        assert "import manim" not in result
        assert "config." not in result
        assert "```" not in result
        assert "AnimationScene" in result


class TestGetAnimationClipNoNarration:
    def test_returns_none_for_empty_narration(self):
        from manim_animator import get_animation_clip
        client = MagicMock()
        section = {"type": "text", "heading": "Test", "narration": ""}
        result = get_animation_clip(client, section, 5.0)
        assert result is None

    def test_returns_none_when_narration_key_missing(self):
        from manim_animator import get_animation_clip
        client = MagicMock()
        section = {"type": "text", "heading": "Test"}
        result = get_animation_clip(client, section, 5.0)
        assert result is None


class TestGetAnimationClipCacheHit:
    def test_returns_cached_clip_without_calling_llm(self, tmp_path):
        from manim_animator import get_animation_clip
        import hashlib

        narration = "cached narration"
        full = ""
        key = hashlib.md5((narration + full).encode()).hexdigest()[:12]
        cache_dir = tmp_path / key
        cache_dir.mkdir()
        mp4 = cache_dir / "animation.mp4"
        mp4.touch()

        client = MagicMock()
        section = {"type": "text", "heading": "Test", "narration": narration}

        with patch("manim_animator.VideoFileClip") as mock_vc:
            mock_clip = MagicMock()
            mock_vc.return_value = mock_clip
            result = get_animation_clip(client, section, 5.0, cache_base=str(tmp_path))

        # LLM should NOT have been called
        client.chat.completions.create.assert_not_called()
        assert result == mock_clip

    def test_cache_hit_uses_correct_mp4_path(self, tmp_path):
        from manim_animator import get_animation_clip
        import hashlib

        narration = "test narr"
        full = "context"
        key = hashlib.md5((narration + full).encode()).hexdigest()[:12]
        cache_dir = tmp_path / key
        cache_dir.mkdir()
        mp4 = cache_dir / "animation.mp4"
        mp4.touch()

        client = MagicMock()
        section = {"type": "text", "heading": "H", "narration": narration}

        with patch("manim_animator.VideoFileClip") as mock_vc:
            mock_vc.return_value = MagicMock()
            get_animation_clip(client, section, 5.0, full_narration=full, cache_base=str(tmp_path))
            mock_vc.assert_called_once_with(str(mp4))
