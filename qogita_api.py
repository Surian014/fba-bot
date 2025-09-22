import requests
import streamlit as st

def get_qogita_products(limit=50):
    headers = {"Authorization": f"Bearer {st.secrets['QOGITA_API_KEY']}"}
    url = "https://api.qogita.com/v1/products"
    r = requests.get(url, headers=headers)
    data = r.json()
    return data.get("data", [])[:limit]
