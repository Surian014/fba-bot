import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import qogita_api


class FakeSecrets:
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]


def test_get_qogita_products_returns_data(monkeypatch):
    secrets = FakeSecrets({"QOGITA_API_KEY": "test-key"})
    st_mock = SimpleNamespace(secrets=secrets, warning=Mock())
    monkeypatch.setattr(qogita_api, "st", st_mock)
    monkeypatch.delenv("QOGITA_API_KEY", raising=False)

    fake_response = Mock()
    fake_response.json.return_value = {
        "results": [
            {
                "variant": {
                    "ean": "1234567890123",
                    "name": "Sample Product",
                    "sku": "SKU-1",
                    "brand": "Brand A",
                },
                "price": {"amount": "10.00", "currency": "EUR"},
                "stock": 5,
            },
            {
                "variant": {"ean": "9876543210987", "name": "Extra Product"},
                "price": {"amount": "20.00", "currency": "EUR"},
            },
        ]
    }
    fake_response.raise_for_status = Mock()
    request_post = Mock(return_value=fake_response)
    monkeypatch.setattr(qogita_api.requests, "post", request_post)

    result = qogita_api.get_qogita_products(limit=1)

    assert result == [
        {
            "ean": "1234567890123",
            "name": "Sample Product",
            "price": "10.00",
            "sku": "SKU-1",
            "brand": "Brand A",
            "stock": 5,
            "currency": "EUR",
        }
    ]

    request_post.assert_called_once()
    args, kwargs = request_post.call_args
    assert args[0] == "https://api.qogita.com/api/v1/buyer/variants/offers/search/"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["headers"]["Accept"] == "application/json"
    assert kwargs.get("json", {}) == {"page_size": 1}


def test_get_qogita_products_missing_key_returns_empty_list(monkeypatch):
    st_mock = SimpleNamespace(secrets=FakeSecrets({}), warning=Mock())
    monkeypatch.setattr(qogita_api, "st", st_mock)
    monkeypatch.delenv("QOGITA_API_KEY", raising=False)
    request_post = Mock()
    monkeypatch.setattr(qogita_api.requests, "post", request_post)

    result = qogita_api.get_qogita_products()

    assert result == []
    st_mock.warning.assert_called_once()
    request_post.assert_not_called()
