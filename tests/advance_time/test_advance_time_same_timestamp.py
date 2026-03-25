"""Test: advance_time in a reaction must not affect the logical time of
subsequent reactions triggered by the same event.

When two input ports receive messages at the same logical timestamp, they
are merged into a single InputPortEvent. All triggered reactions should
observe logical_time == event.timestamp. If one reaction calls
advance_time(), the others must still see the original timestamp.

This test is expected to FAIL until the bug is fixed.
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = str(Path(__file__).parent / "_advance_time_same_timestamp.py")
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.mark.timeout(30)
def test_advance_time_same_timestamp_reactions():
    """Reactions at the same timestamp must all see the correct logical time,
    even if one of them calls advance_time()."""
    result = subprocess.run(
        [sys.executable, _SCRIPT],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
        timeout=20,
    )
    assert result.returncode == 0, f"Process failed:\n{result.stderr}"
    # Both reactions must have fired
    assert "REACT_A fired" in result.stderr, "react_a did not fire"
    assert "REACT_B fired" in result.stderr, "react_b did not fire"
    # Both must report the correct logical time (T=0)
    assert "REACT_A_TIME_OK" in result.stderr, (
        "react_a saw wrong logical_time (should be T=0)"
    )
    assert "REACT_B_TIME_OK" in result.stderr, (
        "react_b saw wrong logical_time (should be T=0)"
    )
    # Neither should report the wrong time
    assert "TIME_WRONG" not in result.stderr, (
        f"A reaction fired at the wrong logical time:\n{result.stderr}"
    )
