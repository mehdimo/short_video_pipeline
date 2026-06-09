"""Tests for pipeline.py — narration builder and video orchestrator."""

import os
import pytest
from unittest.mock import MagicMock, patch
import numpy as np


class TestBuildFullNarration:
    def test_excludes_sections_with_empty_narration(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "Title", "narration": ""},
            {"heading": "Sec 1", "narration": "First section content"},
            {"heading": "Sec 2", "narration": "Second section content"},
        ]
        result = build_full_narration(sections)
        assert "Title" not in result
        assert "First section content" in result
        assert "Second section content" in result

    def test_excludes_sections_without_narration_key(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "No Key"},
            {"heading": "Has Key", "narration": "Some narration"},
        ]
        result = build_full_narration(sections)
        assert "No Key" not in result
        assert "Has Key" in result

    def test_numbering_starts_at_1(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "Title", "narration": ""},
            {"heading": "Sec 1", "narration": "Content here"},
        ]
        result = build_full_narration(sections)
        assert result.startswith("1.")

    def test_numbering_is_sequential_ignoring_skipped(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "Title", "narration": ""},
            {"heading": "A", "narration": "First"},
            {"heading": "B", "narration": "Second"},
            {"heading": "C", "narration": "Third"},
        ]
        result = build_full_narration(sections)
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_all_narrations_included(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "X", "narration": "Alpha"},
            {"heading": "Y", "narration": "Beta"},
        ]
        result = build_full_narration(sections)
        assert "Alpha" in result
        assert "Beta" in result

    def test_headings_included(self):
        from pipeline import build_full_narration
        sections = [{"heading": "My Heading", "narration": "My narration"}]
        result = build_full_narration(sections)
        assert "My Heading" in result

    def test_empty_sections_returns_empty_string(self):
        from pipeline import build_full_narration
        assert build_full_narration([]) == ""

    def test_all_empty_narrations_returns_empty_string(self):
        from pipeline import build_full_narration
        sections = [
            {"heading": "A", "narration": ""},
            {"heading": "B", "narration": ""},
        ]
        assert build_full_narration(sections) == ""

    def test_returns_string(self):
        from pipeline import build_full_narration
        result = build_full_narration([{"heading": "H", "narration": "N"}])
        assert isinstance(result, str)


class TestCreateVideoOutputDir:
    def test_creates_output_directory(self, tmp_path):
        from pipeline import create_video

        output_path = str(tmp_path / "subdir" / "output.mp4")

        dummy_clip = MagicMock()
        dummy_clip.duration = 3.0
        dummy_clip.set_duration.return_value = dummy_clip
        dummy_clip.set_audio.return_value = dummy_clip
        dummy_clip.subclip.return_value = dummy_clip

        dummy_audio = MagicMock()
        dummy_audio.duration = 3.0
        dummy_audio.subclip.return_value = dummy_audio
        dummy_audio.set_start.return_value = dummy_audio

        with patch("pipeline.OpenAI"), \
             patch("pipeline.generate_audio"), \
             patch("pipeline.get_animation_clip", return_value=None), \
             patch("pipeline.make_typing_clip", return_value=dummy_clip), \
             patch("pipeline.render_frame", return_value=np.zeros((1920, 1080, 3), dtype=np.uint8)), \
             patch("pipeline.ImageClip", return_value=dummy_clip), \
             patch("pipeline.AudioFileClip", return_value=dummy_audio), \
             patch("pipeline.CompositeAudioClip", return_value=dummy_clip), \
             patch("pipeline.concatenate_videoclips", return_value=dummy_clip), \
             patch("os.path.exists", return_value=True):

            try:
                create_video(output_path)
            except Exception:
                pass

        # The parent directory should have been created
        assert os.path.exists(str(tmp_path / "subdir"))

    def test_creates_audio_subdirectory(self, tmp_path):
        from pipeline import create_video

        output_path = str(tmp_path / "out" / "video.mp4")

        dummy_clip = MagicMock()
        dummy_clip.duration = 3.0
        dummy_clip.set_duration.return_value = dummy_clip
        dummy_clip.set_audio.return_value = dummy_clip

        dummy_audio = MagicMock()
        dummy_audio.duration = 3.0
        dummy_audio.subclip.return_value = dummy_audio
        dummy_audio.set_start.return_value = dummy_audio

        with patch("pipeline.OpenAI"), \
             patch("pipeline.generate_audio"), \
             patch("pipeline.get_animation_clip", return_value=None), \
             patch("pipeline.make_typing_clip", return_value=dummy_clip), \
             patch("pipeline.render_frame", return_value=np.zeros((1920, 1080, 3), dtype=np.uint8)), \
             patch("pipeline.ImageClip", return_value=dummy_clip), \
             patch("pipeline.AudioFileClip", return_value=dummy_audio), \
             patch("pipeline.CompositeAudioClip", return_value=dummy_clip), \
             patch("pipeline.concatenate_videoclips", return_value=dummy_clip), \
             patch("os.path.exists", return_value=True):

            try:
                create_video(output_path)
            except Exception:
                pass

        assert os.path.exists(str(tmp_path / "out" / "audio"))
