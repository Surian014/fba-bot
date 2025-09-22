import os

import requests
import streamlit as st


def _get_qogita_api_key() -> str:
    """Fetch the Qogita API key from Streamlit secrets or the environment."""

    try:
        api_key = st.secrets.get("QOGITA_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("QOGITA_API_KEY")

    if not api_key:
        message = (
            "Qogita API key missing. Please set st.secrets['QOGITA_API_KEY'] or "
            "define the QOGITA_API_KEY environment variable."
        )
        try:
            st.warning(message)
        except Exception:
            pass
        raise RuntimeError(message)

    return api_key


def get_qogita_products(limit=50):
    headers = {"Authorization": f"Bearer {_get_qogita_api_key()}"}
    url = "https://api.qogita.com/v1/products"
    r = requests.get(url, headers=headers)
    data = r.json()
    return data.get("data", [])[:limit]
