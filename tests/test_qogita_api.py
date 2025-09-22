import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import qogita_api


def test_get_qogita_products_returns_data(monkeypatch):
    secrets = {"QOGITA_API_KEY": "test-key"}
    st_mock = SimpleNamespace(secrets=secrets, warning=Mock())
    monkeypatch.setattr(qogita_api, "st", st_mock)
    monkeypatch.delenv("QOGITA_API_KEY", raising=False)

    fake_response = Mock()
    fake_response.json.return_value = {"data": [1, 2, 3]}
    request_get = Mock(return_value=fake_response)
    monkeypatch.setattr(qogita_api.requests, "get", request_get)

    result = qogita_api.get_qogita_products(limit=2)

    assert result == [1, 2]
    request_get.assert_called_once()
    headers = request_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-key"


def test_get_qogita_products_missing_key_returns_empty_list(monkeypatch):
    st_mock = SimpleNamespace(secrets={}, warning=Mock())
    monkeypatch.setattr(qogita_api, "st", st_mock)
    monkeypatch.delenv("QOGITA_API_KEY", raising=False)
    request_get = Mock()
    monkeypatch.setattr(qogita_api.requests, "get", request_get)

    result = qogita_api.get_qogita_products()

    assert result == []
    st_mock.warning.assert_called_once()
    request_get.assert_not_called()
