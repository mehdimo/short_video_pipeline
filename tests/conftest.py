import sys
import os

# Add src/ to sys.path so test modules can import project modules directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
