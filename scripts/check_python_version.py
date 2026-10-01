"""Fail if the project's virtualenv doesn't run the pinned Python version.

The team-wide development interpreter is pinned in `.python-version`
(major.minor). Running a different one locally causes "works on my machine"
bugs, so the pre-commit hook and `make doctor` call this script.

Usage: python scripts/check_python_version.py [path/to/python]
       (defaults to the project's .venv interpreter)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN_FILE = ROOT / ".python-version"
VENV_PYTHON = (
    ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python"
)


def main() -> int:
    expected = PIN_FILE.read_text(encoding="utf-8").strip()
    interpreter = Path(sys.argv[1]) if len(sys.argv) > 1 else VENV_PYTHON

    if not interpreter.exists():
        sys.stderr.write(
            f"✗ No virtualenv found at {interpreter}. Run `make install`.\n"
        )
        return 1

    actual = subprocess.run(  # noqa: S603 — fixed, trusted arguments
        [str(interpreter), "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if actual != expected:
        sys.stderr.write(
            f"✗ .venv runs Python {actual}, but the project pins {expected} "
            f"(.python-version).\n  Fix: rm -rf .venv && make install\n"
        )
        return 1

    sys.stdout.write(f"✓ Python {actual} matches .python-version\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
