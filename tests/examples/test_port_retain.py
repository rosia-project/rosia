"""Test that input port values are retained across reactions.

Pipeline:
  Timer -> Producer -> Consumer

Producer sends on every tick. Consumer has two input ports: one from Producer
and one from a second Timer at a slower rate. When the slow timer fires,
Consumer should still see the latest value from Producer (not None).
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = str(Path(__file__).parent / "_port_retain.py")
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.mark.timeout(30)
def test_port_retain():
    """Input ports retain the most recent value, not cleared after reaction."""
    result = subprocess.run(
        [sys.executable, _SCRIPT],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
    )
    assert result.returncode == 0, f"Process failed:\n{result.stderr}"
    # The consumer should see the retained value from the fast producer
    # when the slow timer fires, not None
    assert "RETAINED OK" in result.stderr
    assert "RETAINED FAIL" not in result.stderr
