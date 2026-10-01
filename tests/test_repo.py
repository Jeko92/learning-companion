import shutil
import subprocess
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
GIT = shutil.which("git") or "git"


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
    )

    assert result.returncode == 0, f"{path} is not gitignored"
