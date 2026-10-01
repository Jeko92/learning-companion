import importlib

from django.core.exceptions import ImproperlyConfigured

import pytest

import config.settings

ENV_KEYS = ("SECRET_KEY", "DEBUG", "ALLOWED_HOSTS", "DATABASE_URL")


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

    yield _load
    monkeypatch.undo()
    importlib.reload(config.settings)


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
