"""
Generates Manim animation scenes from section narration via OpenAI and
renders them to mp4. Used by create_video.py for type="text" sections.

Caches both the generated Python script and the rendered mp4 under
output/animations/<md5-of-narration>/ so re-runs skip the API/render step.
"""

import sys
import hashlib
import subprocess
import textwrap
from pathlib import Path

from openai import OpenAI
from moviepy.editor import VideoFileClip


SCENE_CLASS = "AnimationScene"

# Only the import — resolution/fps are passed via CLI flags.
_PREAMBLE = "from manim import *\n\n"

_SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert Manim Community Edition (v0.20) animator for CS/AI/ML education shorts.
    Generate a Python class `AnimationScene(Scene)` with a `construct` method that
    visually explains the given concept for a YouTube Shorts video.

    HARD RULES — any violation causes a rendering crash:
    • Do NOT include any import statements or config.* lines — already handled.
    • Class name must be exactly: AnimationScene(Scene)
    • Use ONLY Text(), NEVER Tex() or MathTex() — LaTeX is not installed.
    • Allowed Mobjects: Text, VGroup, Rectangle, Square, Circle, RoundedRectangle,
      Arrow, CurvedArrow, Line, Dot, Brace, SurroundingRectangle, Underline
    • Allowed animations: FadeIn, FadeOut, Write, Create, GrowFromCenter,
      Transform, ReplacementTransform, Indicate, Flash, DrawBorderThenFill
    • GrowArrow(arrow) works ONLY on a single Arrow object — NEVER on a VGroup.
      To animate multiple arrows use: AnimationGroup(*[GrowArrow(a) for a in [a1, a2]])
      When in doubt, use Create() — it works safely on both single objects and VGroups.
    • Do NOT use Polygon with fewer than 3 points or any OpenGL-only features.

    PORTRAIT FRAME — critical for correct positioning:
    • The canvas is 4.5 units wide × 8 units tall (X ∈ [-2.25, 2.25], Y ∈ [-4, 4]).
    • Use .to_edge(UP/DOWN/LEFT/RIGHT), .next_to(), .shift() — avoid hardcoded large X values.
    • Use font_size ≤ 36 for body text; ≤ 48 for headings (default 48 overflows horizontally).
    • Stack elements vertically — you have plenty of vertical room.

    STYLE:
    • First line of construct: self.camera.background_color = "#0D1117"
    • Colors: accent="#58A6FF", text="#C9D1D9", positive="#3FB950", negative="#F85149",
      code_green="#A3E688", dark_box="#161B22"
    • Animation should visualize the concept with shapes/arrows, not just display text.

    TIMING:
    • self.play() + self.wait() calls must sum to ≈ the target duration in seconds.

    Return ONLY the class definition — nothing before or after it.
""")


# ── helpers ───────────────────────────────────────────────────────────────────

def _cache_dir(base: str, narration: str, full_narration: str) -> Path:
    key = hashlib.md5((narration + full_narration).encode()).hexdigest()[:12]
    path = Path(base) / key
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ask(client: OpenAI, messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def _clean(class_code: str) -> str:
    """Strip stray import/config lines the LLM might have included."""
    out = []
    for line in class_code.splitlines():
        s = line.strip()
        if s.startswith("from manim") or s.startswith("import manim"):
            continue
        if s.startswith("config."):
            continue
        # Strip markdown code fences if the LLM wrapped the output
        if s.startswith("```"):
            continue
        out.append(line)
    return "\n".join(out)


def _render(script_path: Path, media_dir: Path) -> tuple[bool, str, Path | None]:
    """Invoke `python -m manim render …`; return (success, stderr, mp4_path)."""
    cmd = [
        sys.executable, "-m", "manim", "render",
        "--media_dir", str(media_dir),
        "--resolution", "1080,1920",
        "--fps", "24",
        "--disable_caching",
        "--verbosity", "error",
        "--progress_bar", "none",
        str(script_path),
        SCENE_CLASS,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        matches = list(media_dir.glob(f"**/{SCENE_CLASS}.mp4"))
        if matches:
            return True, "", matches[0]

    return False, (result.stderr + result.stdout)[-1000:], None


# ── public API ────────────────────────────────────────────────────────────────

def get_animation_clip(
    client: OpenAI,
    section: dict,
    duration: float,
    full_narration: str = "",
    cache_base: str = "output/animations",
) -> VideoFileClip | None:
    """
    Return a VideoFileClip containing a Manim animation for *section*.

    Args:
        full_narration: All sections' narrations joined together, sent as
                        broader context so the LLM understands the video's
                        overall arc while generating this section's animation.

    Caches the script and rendered mp4; re-uses them on subsequent runs.
    The cache key includes both the section narration and the full context,
    so changing either invalidates the cache for this section.
    Returns None if both render attempts fail (caller falls back to static frame).
    """
    narration = section.get("narration", "")
    heading   = section.get("heading",   "")
    if not narration:
        return None

    cache       = _cache_dir(cache_base, narration, full_narration)
    mp4_path    = cache / "animation.mp4"
    script_path = cache / "scene.py"
    media_dir   = cache / "media"

    # ── serve from cache ─────────────────────────────────────────────────────
    if mp4_path.exists():
        print(f"    reusing cached animation: '{heading}'")
        return VideoFileClip(str(mp4_path))

    # ── 1. generate scene code ───────────────────────────────────────────────
    print(f"    generating Manim scene for '{heading}'…")

    context_block = (
        f"=== Full video narration (broader context) ===\n{full_narration}\n\n"
        if full_narration else ""
    )
    user_msg = (
        f"{context_block}"
        f"=== Focus section ===\n"
        f"Heading: {heading}\n"
        f"Narration: {narration}\n"
        f"Target duration: {duration:.1f} s\n\n"
        "Generate the AnimationScene class for the focus section. "
        "Use the full narration above only to understand the video's theme and "
        "what comes before/after — the animation must illustrate the focus section."
    )
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user",   "content": user_msg},
    ]
    class_code = _ask(client, messages)
    script_path.write_text(_PREAMBLE + _clean(class_code))

    # ── 2. render (one retry with error feedback) ────────────────────────────
    print(f"    rendering '{heading}'…")
    ok, err, rendered = _render(script_path, media_dir)

    if not ok:
        print(f"    render failed — sending error back to OpenAI for a fix…")
        messages += [
            {"role": "assistant", "content": class_code},
            {
                "role": "user",
                "content": (
                    "The scene failed to render. Fix the error below and return "
                    "the corrected AnimationScene class only.\n\nError:\n" + err
                ),
            },
        ]
        class_code = _ask(client, messages)
        script_path.write_text(_PREAMBLE + _clean(class_code))
        print(f"    re-rendering after fix…")
        ok, err, rendered = _render(script_path, media_dir)

    if not ok or rendered is None:
        print(f"    WARNING: Manim failed for '{heading}' — will use static frame")
        return None

    rendered.rename(mp4_path)
    print(f"    animation rendered: {mp4_path.name} ({mp4_path.stat().st_size // 1024} KB)")
    return VideoFileClip(str(mp4_path))
