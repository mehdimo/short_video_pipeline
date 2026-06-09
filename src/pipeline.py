"""Video pipeline orchestrator — assembles audio, animations, and frames into mp4."""

import os
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from openai import OpenAI

from content import SECTIONS
from renderer import render_frame, FPS
from tts import generate_audio
from manim_animator import get_animation_clip
from code_animator import make_typing_clip


def build_full_narration(sections: list[dict]) -> str:
    """Return a numbered narration summary for all sections that have narration text."""
    narrated = [s for s in sections if s.get("narration")]
    return "\n".join(
        f"{i + 1}. {s['heading']}\n   {s['narration']}"
        for i, s in enumerate(narrated)
    )


def create_video(output_path: str = "output/linked_list.mp4") -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    audio_dir = os.path.join(os.path.dirname(output_path), "audio")
    os.makedirs(audio_dir, exist_ok=True)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    full_narration = build_full_narration(SECTIONS)

    video_clips = []
    audio_clips = []   # each AudioFileClip with .set_start() already applied
    current_time = 0.0

    for i, section in enumerate(SECTIONS):
        stype     = section["type"]
        narration = section.get("narration", "")
        audio_path = os.path.join(audio_dir, f"section_{i}.mp3")

        # ── audio ────────────────────────────────────────────────────────────
        if narration:
            if not os.path.exists(audio_path):
                print(f"  [{i+1}] generating TTS…")
                generate_audio(client, narration, audio_path)
            raw_audio  = AudioFileClip(audio_path)
            audio_dur  = raw_audio.duration
            print(f"  [{i+1}] {stype}: audio {audio_dur:.1f}s")
        else:
            raw_audio = None
            audio_dur = section["duration"]
            print(f"  [{i+1}] {stype}: no narration, fixed {audio_dur:.1f}s")

        # ── video ────────────────────────────────────────────────────────────
        if stype == "code":
            slide_dur  = audio_dur
            video_clip = make_typing_clip(section, slide_dur, render_frame, FPS)

        elif stype == "text":
            anim = get_animation_clip(client, section, audio_dur, full_narration, "output/animations")
            if anim is not None:
                slide_dur  = min(anim.duration, audio_dur)
                video_clip = anim.subclip(0, slide_dur)
            else:
                slide_dur  = audio_dur
                video_clip = ImageClip(render_frame(section)).set_duration(slide_dur)

        else:  # title
            slide_dur  = audio_dur
            video_clip = ImageClip(render_frame(section)).set_duration(slide_dur)

        # ── commit ───────────────────────────────────────────────────────────
        if raw_audio is not None:
            audio_clips.append(raw_audio.subclip(0, slide_dur).set_start(current_time))
        video_clips.append(video_clip)
        current_time += slide_dur

    video = concatenate_videoclips(video_clips, method="compose")

    if audio_clips:
        video = video.set_audio(CompositeAudioClip(audio_clips))

    video.write_videofile(
        output_path, fps=FPS, codec="libx264", audio_codec="aac", logger=None
    )
    print(f"\nDone — {output_path}  ({current_time:.1f} s)")
