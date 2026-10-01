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
