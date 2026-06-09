"""OpenAI TTS voice-over generation."""

from openai import OpenAI


def generate_audio(client: OpenAI, text: str, path: str) -> None:
    """Call OpenAI TTS and save mp3 to *path*."""
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    with open(path, "wb") as f:
        f.write(response.content)
