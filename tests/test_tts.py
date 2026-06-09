"""Tests for tts.py — OpenAI TTS wrapper."""

import os
import pytest
from unittest.mock import MagicMock


class TestGenerateAudio:
    def test_writes_response_content_to_file(self, tmp_path):
        from tts import generate_audio
        client = MagicMock()
        client.audio.speech.create.return_value.content = b"fake_audio_bytes"

        out = str(tmp_path / "audio.mp3")
        generate_audio(client, "Hello world", out)

        assert os.path.exists(out)
        assert open(out, "rb").read() == b"fake_audio_bytes"

    def test_calls_openai_with_correct_model_and_voice(self, tmp_path):
        from tts import generate_audio
        client = MagicMock()
        client.audio.speech.create.return_value.content = b"data"

        out = str(tmp_path / "a.mp3")
        generate_audio(client, "Narration text", out)

        client.audio.speech.create.assert_called_once_with(
            model="tts-1",
            voice="alloy",
            input="Narration text",
        )

    def test_passes_text_as_input_param(self, tmp_path):
        from tts import generate_audio
        client = MagicMock()
        client.audio.speech.create.return_value.content = b""

        out = str(tmp_path / "b.mp3")
        generate_audio(client, "My custom narration", out)

        call_kwargs = client.audio.speech.create.call_args.kwargs
        assert call_kwargs["input"] == "My custom narration"

    def test_empty_text_still_calls_api(self, tmp_path):
        from tts import generate_audio
        client = MagicMock()
        client.audio.speech.create.return_value.content = b""

        out = str(tmp_path / "c.mp3")
        generate_audio(client, "", out)

        client.audio.speech.create.assert_called_once()

    def test_creates_file_with_correct_binary_content(self, tmp_path):
        from tts import generate_audio
        expected = bytes(range(256))
        client = MagicMock()
        client.audio.speech.create.return_value.content = expected

        out = str(tmp_path / "d.mp3")
        generate_audio(client, "text", out)

        with open(out, "rb") as f:
            assert f.read() == expected
