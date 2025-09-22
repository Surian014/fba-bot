from amazon_api import create_listing

def auto_list(product):
    if product["Profitable"]:
        return create_listing(product["ASIN"], product["Amazon Price (€)"], 10)
    return {"status": "Not listed", "reason": "Not profitable"}
