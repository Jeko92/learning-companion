import importlib
import os
from collections.abc import Iterator
from contextlib import contextmanager

from django.core.exceptions import ImproperlyConfigured

import pytest

import config.settings
from config.settings import _env_file_to_read

ENV_KEYS = ("SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "DATABASE_URL")


@contextmanager
def isolated_environ() -> Iterator[None]:
    """Undo every os.environ change made inside the block.

    monkeypatch alone can't: env.read_env() sets keys monkeypatch never saw.
    """
    saved = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


@pytest.fixture
def load_settings(monkeypatch):
    """Re-import config.settings under a controlled environment, no .env file."""

    def _load(**env):
        for key in ENV_KEYS:
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("DJANGO_ENV_FILE", "")
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(config.settings)

    with isolated_environ():
        yield _load
        monkeypatch.undo()
    importlib.reload(config.settings)


def test_isolated_environ_removes_values_read_from_env_file(monkeypatch):
    before = dict(os.environ)

    with isolated_environ():
        for key in ENV_KEYS:
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("DJANGO_ENV_FILE", ".env.example")
        importlib.reload(config.settings)  # read_env adds DEBUG etc. to os.environ
        monkeypatch.undo()

    after = dict(os.environ)
    importlib.reload(config.settings)
    assert after == before


def test_missing_secret_key_fails_fast(load_settings):
    with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
        load_settings()


def test_settings_come_from_environment(load_settings):
    settings = load_settings(
        SECRET_KEY="from-env",
        DEBUG="true",
        ALLOWED_HOSTS="example.com,www.example.com",
        DATABASE_URL="sqlite:////tmp/other.sqlite3",
    )

    assert settings.SECRET_KEY == "from-env"  # noqa: S105 - test value, not a secret
    assert settings.DEBUG is True
    assert settings.ALLOWED_HOSTS == ["example.com", "www.example.com"]
    assert settings.DATABASES["default"]["NAME"] == "/tmp/other.sqlite3"  # noqa: S108 - path string only, nothing is written


def test_settings_defaults_when_unset(load_settings):
    settings = load_settings(SECRET_KEY="only-this-is-required")

    assert settings.DEBUG is False
    assert settings.ALLOWED_HOSTS == []
    database = settings.DATABASES["default"]
    assert database["ENGINE"] == "django.db.backends.sqlite3"
    assert database["NAME"] == str(settings.BASE_DIR / "db.sqlite3")


def test_tailwind_and_theme_app_installed(settings):
    assert "tailwind" in settings.INSTALLED_APPS
    assert "apps.theme" in settings.INSTALLED_APPS
    assert settings.TAILWIND_APP_NAME == "apps.theme"


def test_explicit_env_file_that_does_not_exist_fails_fast(load_settings):
    with pytest.raises(ImproperlyConfigured, match="DJANGO_ENV_FILE"):
        load_settings(DJANGO_ENV_FILE="does-not-exist.env")


def test_relative_env_file_resolves_against_base_dir(
    load_settings, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)

    settings = load_settings(DJANGO_ENV_FILE=".env.example")

    assert settings.SECRET_KEY == "change-me"  # noqa: S105 - value from .env.example


def test_env_file_unset_uses_default_env_when_present(tmp_path):
    (tmp_path / ".env").write_text("DEBUG=false\n")

    assert _env_file_to_read(tmp_path, None) == tmp_path / ".env"


def test_env_file_unset_skips_missing_default_env(tmp_path):
    assert _env_file_to_read(tmp_path, None) is None


def test_env_file_empty_reads_nothing(tmp_path):
    (tmp_path / ".env").write_text("DEBUG=false\n")

    assert _env_file_to_read(tmp_path, "") is None


def test_env_file_relative_and_absolute_paths(tmp_path):
    (tmp_path / "custom.env").write_text("")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    assert _env_file_to_read(tmp_path, "custom.env") == tmp_path / "custom.env"
    assert _env_file_to_read(elsewhere, str(tmp_path / "custom.env")) == (
        tmp_path / "custom.env"
    )


def test_env_file_expands_home_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "home.env").write_text("")

    assert _env_file_to_read(tmp_path / "project", "~/home.env") == (
        tmp_path / "home.env"
    )


def test_env_file_explicit_missing_fails_fast(tmp_path):
    with pytest.raises(ImproperlyConfigured, match="missing file"):
        _env_file_to_read(tmp_path, "nope.env")
