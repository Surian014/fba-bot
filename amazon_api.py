import requests
import streamlit as st

headers = {"Authorization": f"Bearer {st.secrets['AMAZON_ACCESS_TOKEN']}"}
MARKETPLACE_ID = st.secrets["MARKETPLACE_ID"]
SELLER_ID = st.secrets["SELLER_ID"]

def get_asin_from_ean(ean):
    url = "https://sellingpartnerapi-eu.amazon.com/catalog/v0/items"
    params = {"MarketplaceId": MARKETPLACE_ID, "Query": ean}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        try:
            return r.json()["payload"]["Items"][0]["Identifiers"]["MarketplaceASIN"]["ASIN"]
        except:
            return None
    return None

def get_amazon_price(asin):
    url = f"https://sellingpartnerapi-eu.amazon.com/products/pricing/v0/items/{asin}"
    params = {"MarketplaceId": MARKETPLACE_ID}
    r = requests.get(url, headers=headers, params=params)
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
            "MarketplaceId": MARKETPLACE_ID,
            "IsAmazonFulfilled": True,
            "Identifier": asin,
            "PriceToEstimateFees": {
                "ListingPrice": {"CurrencyCode": currency, "Amount": price},
                "Shipping": {"CurrencyCode": currency, "Amount": 0}
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        try:
            return float(r.json()["payload"]["FeesEstimateResult"]["FeesEstimate"]["TotalFeesEstimate"]["Amount"])
        except:
            return None
    return None

def create_listing(asin, price, quantity):
    url = f"https://sellingpartnerapi-eu.amazon.com/listings/2021-08-01/items/{SELLER_ID}"
    payload = {
        "productType": "PRODUCT",
        "requirements": "LISTING_OFFER_ONLY",
        "attributes": {
            "asin": [{"value": asin}],
            "fulfillmentAvailability": [{"fulfillmentChannelCode": "AMAZON_EU", "quantity": quantity}],
            "price": [{"currency": "EUR", "amount": price}]
        }
    }
    r = requests.put(url, headers=headers, json=payload)
    return r.json()
