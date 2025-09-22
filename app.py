import streamlit as st
import pandas as pd
from qogita_api import get_qogita_products
from profit_engine import check_profit
from auto_listing import auto_list

st.set_page_config(page_title="Qogita → Amazon Profit Scanner", layout="wide")
st.title("📦 Qogita → Amazon FBA Auto-Bot")

limit = st.slider("Anzahl Produkte prüfen:", 10, 100, 20)
products = get_qogita_products(limit=limit)

rows = []
for p in products:
    result = check_profit(p)
    if result:
        rows.append(result)

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)

profitable = pd.DataFrame(columns=df.columns)

if df.empty:
    st.info("Keine Produkte gefunden. Bitte passe die Filter an und versuche es erneut.")
elif "Profitable" not in df.columns:
    st.info(
        "Die Ergebnisdaten enthalten keine Spalte 'Profitable'. "
        "Automatisches Listing und Download werden übersprungen."
    )
else:
    profitable = df[df["Profitable"]]
    st.subheader("✅ Automatisch profitable Produkte listen")
    for _, row in profitable.iterrows():
        resp = auto_list(row.to_dict())
        st.write(row["Name"], resp)

    st.download_button(
        "📥 Export CSV",
        data=profitable.to_csv(index=False).encode("utf-8"),
        file_name="profitable_products.csv",
        mime="text/csv"
    )
