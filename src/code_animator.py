"""
Typing animation for code sections.

make_typing_clip reveals the code body character-by-character over the slide
duration, with a blinking cursor, then holds the completed code to the end.
"""

from typing import Callable
import numpy as np
from moviepy.editor import VideoClip


def make_typing_clip(
    section: dict,
    duration: float,
    render_fn: Callable[[dict], np.ndarray],
    fps: int = 24,
) -> VideoClip:
    """Return a VideoClip that types out section['body'] over *duration* seconds.

    Args:
        section:   Content section dict (must have 'body').
        duration:  Total clip length in seconds.
        render_fn: Frame renderer — takes a section dict, returns an RGB numpy array.
        fps:       Output frame rate.
    """
    full_code  = section["body"]
    n_chars    = len(full_code)
    type_until = duration * 0.88   # finish typing at 88 % of the slide duration

    def make_frame(t: float) -> np.ndarray:
        if t < type_until:
            visible = max(1, int((t / type_until) * n_chars))
            cursor  = "|" if int(t * 4) % 2 == 0 else " "   # blink at 2 Hz
            body    = full_code[:visible] + cursor
        else:
            body = full_code   # typing done, cursor gone

        return render_fn({**section, "body": body, "_full_body": full_code})

    return VideoClip(make_frame, duration=duration).set_fps(fps)
