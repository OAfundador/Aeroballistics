"""The examples in examples/ run from start to end, from a clone without installation."""
import subprocess
import sys

import pytest

import paths

EXAMPLES = sorted(paths.EXAMPLES.glob("[0-9][0-9]_*.py"))


def test_there_are_examples():
    assert len(EXAMPLES) >= 5


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_example_runs(example):
    r = subprocess.run([sys.executable, str(example)], capture_output=True, text=True,
                       encoding="utf-8", timeout=300, cwd=paths.ROOT)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()
