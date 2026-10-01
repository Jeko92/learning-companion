import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_EXAMPLE = BASE_DIR / ".env.example"


def _example_keys() -> list[str]:
    lines = ENV_EXAMPLE.read_text().splitlines()
    return [
        line.split("=", 1)[0].strip()
        for line in lines
        if "=" in line and not line.lstrip().startswith("#")
    ]


def test_manage_check_passes_with_env_example():
    env = {k: v for k, v in os.environ.items() if k not in _example_keys()}
    env["DJANGO_ENV_FILE"] = str(ENV_EXAMPLE)

    # Fixed argv (current interpreter + repo's manage.py), no untrusted input.
    result = subprocess.run(
        [sys.executable, "manage.py", "check"],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "System check identified no issues" in result.stdout
