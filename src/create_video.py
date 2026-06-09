"""
Entry point for the YouTube Shorts video pipeline.

Run:
    python src/create_video.py
Output:
    output/linked_list.mp4
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "config" / ".env")
sys.path.insert(0, os.path.dirname(__file__))

from pipeline import create_video  # noqa: E402

if __name__ == "__main__":
    create_video()
