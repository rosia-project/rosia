import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = str(Path(__file__).parent / "_e2e_chain.py")
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.mark.timeout(30)
def test_logger_output_in_subprocess():
    """Logger output appears from nodes running in child processes."""
    result = subprocess.run(
        [sys.executable, _SCRIPT],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "[Sink_2] got 0" in result.stderr
    assert "[Sink_2] got 1" in result.stderr
    assert "[Sink_2] got 2" in result.stderr


@pytest.mark.timeout(30)
def test_logger_node_name_prefix():
    """Node logs with its own [name] prefix in subprocess."""
    result = subprocess.run(
        [sys.executable, _SCRIPT],
        capture_output=True,
        text=True,
        cwd=_PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "[Sink_2]" in result.stderr
