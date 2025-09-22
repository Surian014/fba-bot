import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import amazon_api


def test_get_secret_missing_shows_user_friendly_error(monkeypatch):
    amazon_api._get_secret.cache_clear()

    st_mock = Mock()
    st_mock.secrets = {}
    st_mock.error = Mock()

    monkeypatch.setattr(amazon_api, "st", st_mock)

    with pytest.raises(RuntimeError) as excinfo:
        amazon_api._get_secret("AMAZON_ACCESS_TOKEN")

    assert "AMAZON_ACCESS_TOKEN" in str(excinfo.value)
    st_mock.error.assert_called_once()
