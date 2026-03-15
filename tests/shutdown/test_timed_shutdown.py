"""Shutdown test with the same topology as bouncing_ball example.

Pipeline:
  Timer -> Producer1 -> Sink1
        -> Producer2 (slow) -> Sink2

Producer1 requests shutdown after 10 ticks.
Verifies that all nodes complete all steps before exiting.
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = str(Path(__file__).parent / "_timed_shutdown.py")
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.mark.timeout(30)
def test_all_steps_complete():
    """All producers and sinks process every step up to shutdown."""
    result = subprocess.run(
        [sys.executable, _SCRIPT],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
    )
    assert result.returncode == 0, f"Process failed with stderr:\n{result.stderr}"

    # Producer1 (fast) must complete all 10 steps
    for i in range(10):
        assert f"P1 step {i}" in result.stderr, f"P1 step {i} missing"

    # Sink1 must receive all 10 values from Producer1
    for i in range(10):
        assert f"S1 got {i}" in result.stderr, f"S1 got {i} missing"

    # Producer2 (slow) must also complete all 10 steps before shutdown
    for i in range(10):
        assert f"P2 step {i}" in result.stderr, f"P2 step {i} missing"

    # Sink2 must receive all 10 values from Producer2
    for i in range(10):
        assert f"S2 got {i}" in result.stderr, f"S2 got {i} missing"
