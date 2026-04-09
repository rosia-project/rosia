import sys
from pathlib import Path

# Add the examples directory to sys.path so we can import example modules directly.
examples_dir = str(Path(__file__).resolve().parents[3] / "examples")
if examples_dir not in sys.path:
    sys.path.insert(0, examples_dir)
