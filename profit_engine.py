from amazon_api import get_asin_from_ean, get_amazon_price, get_fba_fee
import streamlit as st

def check_profit(product):
    ean = product.get("ean")
    qogita_price = float(product["price"])

    asin = get_asin_from_ean(ean)
    if not asin:
        return None

    amazon_price = get_amazon_price(asin)
    if not amazon_price:
        return None

    fee = get_fba_fee(asin, amazon_price) or 0
    profit = amazon_price - fee - qogita_price

    return {
        "EAN": ean,
        "ASIN": asin,
        "Name": product.get("name"),
        "Qogita Price (€)": qogita_price,
        "Amazon Price (€)": amazon_price,
        "Fee (€)": fee,
        "Profit (€)": profit,
        "Profitable": profit > float(st.secrets["MIN_MARGIN"])
    }
