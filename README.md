# Short Video Pipeline

Automatically generates YouTube Shorts-format educational programming videos from structured content definitions. Given a topic (e.g. Python Linked Lists), the pipeline renders slides, animates code, synthesises voice-over, and produces a portrait MP4 ready for upload.

---

## Features

- **Typing animation** — code sections reveal character-by-character with a blinking cursor, mimicking live coding
- **Manim animations** — concept sections use GPT-4o to generate and render Manim scenes that visually explain the narration
- **Syntax highlighting** — Python keywords, strings, numbers, and comments are each rendered in distinct colours
- **TTS voice-over** — OpenAI TTS (`alloy` voice) reads each section's narration; audio and animations are composed into a single track
- **MD5 caching** — generated TTS audio and Manim mp4s are cached on disk; re-runs skip the API and render steps
- **YouTube Shorts format** — 1080×1920 portrait, 24 fps, under 60 seconds

---

## Requirements

- Python 3.11+
- [FFmpeg](https://ffmpeg.org/download.html) on your `PATH`
- OpenAI API key (TTS + GPT-4o for Manim scene generation)

---

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key
cp config/.env.example config/.env   # then edit config/.env
```

`config/.env`:
```
OPENAI_API_KEY=sk-...
```

---

## Usage

```bash
python src/create_video.py
```

Output is written to `output/linked_list.mp4`.

---

## Project Structure

```
short_video_pipeline/
├── config/
│   └── .env                  # API keys (not committed)
├── src/
│   ├── content.py            # Content definition — all sections for the video
│   ├── syntax.py             # Python tokenizer and syntax highlighting
│   ├── fonts.py              # Font loading with size/mono caching
│   ├── renderer.py           # Frame renderer — produces 1080×1920 NumPy arrays
│   ├── tts.py                # OpenAI TTS wrapper
│   ├── code_animator.py      # Typing animation clip generator
│   ├── manim_animator.py     # LLM-driven Manim scene generation and rendering
│   ├── pipeline.py           # Video pipeline orchestrator
│   └── create_video.py       # Entry point
├── tests/
│   ├── conftest.py           # Adds src/ to sys.path
│   ├── test_syntax.py
│   ├── test_fonts.py
│   ├── test_renderer.py
│   ├── test_code_animator.py
│   ├── test_manim_animator.py
│   ├── test_content.py
│   ├── test_tts.py
│   └── test_pipeline.py
├── output/                   # Rendered video and cached audio (created on first run)
├── requirements.txt
└── pytest.ini
```

### Module responsibilities

| Module | Responsibility                                                                     |
|---|------------------------------------------------------------------------------------|
| `content.py` | A sample source for all video sections (`type`, `heading`, `body`, `narration`, …) |
| `syntax.py` | Regex tokeniser, `_token_style`, `_split_comment`, `draw_code_body`                |
| `fonts.py` | `load_font(size, mono)` with an in-memory cache to avoid re-loading the same font  |
| `renderer.py` | `render_frame(section)` — dispatches on section type to produce a full slide image |
| `tts.py` | `generate_audio(client, text, path)` — calls `tts-1` / `alloy` and writes an mp3   |
| `code_animator.py` | `make_typing_clip` — builds a `VideoClip` that reveals code over time              |
| `manim_animator.py` | `get_animation_clip` — prompts GPT-4o for a Manim class, renders it, caches the mp4 |
| `pipeline.py` | `create_video` — sequences all modules, composes audio, writes the final mp4       |

---

## Adding New Content

Edit `src/content.py`. Each entry in `SECTIONS` is a dict:

```python
{
    "type": "text",                          # "title" | "text" | "code"
    "heading": "What is a Linked List?",
    "body": "A chain of nodes …",            # displayed on slide
    "on_screen_text": "Nodes + pointers",    # bar at the bottom of the frame
    "narration": "A linked list is …",       # read aloud via TTS; drives slide duration
    "duration": 5.0,                         # fallback duration when narration is empty
}
```

- `type: "code"` sections animate the `body` as typing and apply syntax highlighting.
- `type: "text"` sections generate a Manim animation from the narration (falls back to a static slide if rendering fails).
- `type: "title"` sections render a centred title card.

---

## Running Tests

```bash
venv/bin/pytest tests/ -v
```

With coverage:

```bash
venv/bin/pytest tests/ --cov=src --cov-report=term-missing
```
