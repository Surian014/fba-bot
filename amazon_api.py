from functools import lru_cache

import requests
import streamlit as st


def _missing_secret(secret_name: str) -> None:
    """Display a user-friendly error and raise when a secret is missing."""

    message = (
        f"Streamlit secret '{secret_name}' is required to connect to the Amazon API. "
        "Please add this value to your Streamlit app's configuration."
    )
    try:
        st.error(message)
    except Exception:
        # In non-Streamlit contexts (e.g., unit tests) we still raise a clear error.
        pass
    raise RuntimeError(message)


@lru_cache(maxsize=None)
def _get_secret(secret_name: str) -> str:
    """Safely fetch a required Streamlit secret and raise a friendly error if missing."""

    try:
        value = st.secrets[secret_name]
    except KeyError:
        value = None
    except Exception:
        value = None

    if value in (None, ""):
        _missing_secret(secret_name)

    return value


def _get_auth_headers() -> dict:
    """Construct the authorization headers for Amazon API requests."""

    access_token = _get_secret("AMAZON_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {access_token}"}


def _get_marketplace_id() -> str:
    return _get_secret("MARKETPLACE_ID")


def _get_seller_id() -> str:
    return _get_secret("SELLER_ID")

def get_asin_from_ean(ean):
    url = "https://sellingpartnerapi-eu.amazon.com/catalog/v0/items"
    params = {"MarketplaceId": _get_marketplace_id(), "Query": ean}
    r = requests.get(url, headers=_get_auth_headers(), params=params)
    if r.status_code == 200:
        try:
            return r.json()["payload"]["Items"][0]["Identifiers"]["MarketplaceASIN"]["ASIN"]
        except:
            return None
    return None

def get_amazon_price(asin):
    url = f"https://sellingpartnerapi-eu.amazon.com/products/pricing/v0/items/{asin}"
    params = {"MarketplaceId": _get_marketplace_id()}
    r = requests.get(url, headers=_get_auth_headers(), params=params)
    if r.status_code == 200:
        try:
            return float(r.json()["payload"][0]["Summary"]["LowestPrices"][0]["LandedPrice"]["Amount"])
        except:
            return None
    return None

def get_fba_fee(asin, price, currency="EUR"):
    url = f"https://sellingpartnerapi-eu.amazon.com/products/fees/v0/items/{asin}/feesEstimate"
    payload = {
        "FeesEstimateRequest": {
            "MarketplaceId": _get_marketplace_id(),
            "IsAmazonFulfilled": True,
            "Identifier": asin,
            "PriceToEstimateFees": {
                "ListingPrice": {"CurrencyCode": currency, "Amount": price},
                "Shipping": {"CurrencyCode": currency, "Amount": 0}
            }
        }
    }
    r = requests.post(url, headers=_get_auth_headers(), json=payload)
    if r.status_code == 200:
        try:
            return float(r.json()["payload"]["FeesEstimateResult"]["FeesEstimate"]["TotalFeesEstimate"]["Amount"])
        except:
            return None
    return None

def create_listing(asin, price, quantity):
    url = (
        "https://sellingpartnerapi-eu.amazon.com/listings/2021-08-01/items/"
        f"{_get_seller_id()}"
    )
    payload = {
        "productType": "PRODUCT",
        "requirements": "LISTING_OFFER_ONLY",
        "attributes": {
            "asin": [{"value": asin}],
            "fulfillmentAvailability": [{"fulfillmentChannelCode": "AMAZON_EU", "quantity": quantity}],
            "price": [{"currency": "EUR", "amount": price}]
        }
    }
    r = requests.put(url, headers=_get_auth_headers(), json=payload)
    return r.json()
