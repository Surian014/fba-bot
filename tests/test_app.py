import importlib
import sys
from types import ModuleType
from unittest.mock import Mock


def test_app_handles_empty_products(monkeypatch):
    sys.modules.pop("app", None)

    fake_streamlit = ModuleType("streamlit")
    fake_streamlit.secrets = {}
    fake_streamlit.set_page_config = Mock()
    fake_streamlit.title = Mock()
    fake_streamlit.slider = Mock(return_value=10)
    fake_streamlit.dataframe = Mock()
    fake_streamlit.subheader = Mock()
    fake_streamlit.write = Mock()
    fake_streamlit.download_button = Mock()
    fake_streamlit.info = Mock()
    fake_streamlit.warning = Mock()

    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)

    fake_qogita_api = ModuleType("qogita_api")
    fake_qogita_api.get_qogita_products = Mock(return_value=[])
    monkeypatch.setitem(sys.modules, "qogita_api", fake_qogita_api)

    fake_profit_engine = ModuleType("profit_engine")
    fake_profit_engine.check_profit = Mock(return_value=None)
    monkeypatch.setitem(sys.modules, "profit_engine", fake_profit_engine)

    fake_auto_listing = ModuleType("auto_listing")
    fake_auto_listing.auto_list = Mock()
    monkeypatch.setitem(sys.modules, "auto_listing", fake_auto_listing)

    try:
        importlib.import_module("app")
    finally:
        monkeypatch.delitem(sys.modules, "app", raising=False)

    fake_qogita_api.get_qogita_products.assert_called_once()
    fake_streamlit.dataframe.assert_called_once()
    fake_streamlit.info.assert_called()
    fake_streamlit.download_button.assert_not_called()
