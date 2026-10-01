import shutil
import subprocess
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
GIT = shutil.which("git") or "git"
MAKE = shutil.which("make") or "make"


@pytest.mark.parametrize(
    "path",
    [
        "apps/theme/static/css/dist/styles.css",
        "apps/theme/static_src/node_modules/tailwindcss/package.json",
        "node_modules/anything.js",
    ],
)
def test_build_artifacts_are_gitignored(path):
    # Fixed argv, path values come from the parametrize list above.
    result = subprocess.run(  # noqa: S603
        [GIT, "check-ignore", "--quiet", "--no-index", path],
        cwd=BASE_DIR,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, f"{path} is not gitignored"


@pytest.mark.parametrize(
    ("target", "command"),
    [
        ("css", "manage.py tailwind install"),
        ("css-watch", "manage.py tailwind start"),
    ],
)
def test_make_targets_build_tailwind_css(target, command):
    # Dry run only (-n): prints the recipe without executing it.
    result = subprocess.run(  # noqa: S603
        [MAKE, "-n", target],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert command in result.stdout
