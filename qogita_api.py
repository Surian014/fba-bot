import os

import requests
import streamlit as st


def _get_qogita_api_key() -> str:
    """Fetch the Qogita API key from Streamlit secrets or the environment."""

    try:
        api_key = st.secrets["QOGITA_API_KEY"]
        if not api_key:
            raise KeyError("QOGITA_API_KEY is empty")
    except KeyError:
        api_key = None
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


def _extract_price_and_currency(offer):
    """Return the first price-like value and currency from a raw offer."""

    currency = None
    amount = None

    def from_container(container):
        nonlocal amount, currency
        if isinstance(container, dict):
            # Typical Qogita responses expose amount/value + currency fields
            for key in ("amount", "value", "price", "gross", "net", "total"):
                if container.get(key) is not None and amount is None:
                    amount = container[key]
                    break
            currency = container.get("currency") or container.get("currency_code") or currency
        elif isinstance(container, (int, float, str)) and amount is None:
            amount = container

    price_like_fields = [
        offer.get("price"),
        offer.get("unit_price"),
        offer.get("purchase_price"),
        offer.get("net_price"),
    ]

    for field in price_like_fields:
        if field is not None:
            from_container(field)
        if amount is not None:
            break

    if amount is None:
        prices = offer.get("prices") or offer.get("pricing")
        if isinstance(prices, dict):
            for value in prices.values():
                from_container(value)
                if amount is not None:
                    break
        elif isinstance(prices, list):
            for value in prices:
                from_container(value)
                if amount is not None:
                    break

    return amount, currency


def _normalize_offer(offer):
    variant = offer.get("variant") or {}
    ean = variant.get("ean") or offer.get("ean")
    name = variant.get("name") or offer.get("name")
    amount, currency = _extract_price_and_currency(offer)

    if ean is None or amount is None:
        return None

    normalized = {
        "ean": ean,
        "name": name,
        "price": str(amount),
    }

    sku = variant.get("sku") or offer.get("sku")
    if sku:
        normalized["sku"] = sku

    brand = variant.get("brand") or offer.get("brand")
    if brand:
        normalized["brand"] = brand

    stock = (
        offer.get("stock")
        or offer.get("quantity_available")
        or offer.get("available_quantity")
    )
    if stock is not None:
        normalized["stock"] = stock

    if currency:
        normalized["currency"] = currency

    return normalized


def get_qogita_products(limit=50):
    try:
        api_key = _get_qogita_api_key()
    except RuntimeError:
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    url = "https://api.qogita.com/api/v1/buyer/variants/offers/search/"
    params = {"page_size": limit}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    offers = data.get("results") or data.get("data") or []
    normalized_offers = []
    for offer in offers:
        normalized = _normalize_offer(offer)
        if normalized:
            normalized_offers.append(normalized)

    return normalized_offers[:limit]
