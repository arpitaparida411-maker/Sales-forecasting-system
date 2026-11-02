import altair as alt
import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:5000"
CURRENCY = "₹"
USD_TO_INR = 88.0  # replace with today's rate
CRORE = 1e7

st.set_page_config(page_title="Sales Forecasting", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"], [data-testid="stAppViewContainer"], h1, h2, h3, p, div, span, label {
        font-family: 'Poppins', sans-serif;
    }
    div[data-testid="stMetric"] {
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="stMetric"] * { color: white !important; }
    div[data-testid="stColumn"]:nth-of-type(1) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1f77b4, #4fa3e0);
    }
    div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #2ca02c, #6cc76c);
    }
    div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ff7f0e, #ffb066);
    }
    div[data-testid="stColumn"]:nth-of-type(4) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #9467bd, #c0a0e0);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Intelligent Sales Forecasting")
st.write("Walmart weekly sales: history, model comparison and future forecast.")


def get_data(path):
    response = requests.get(f"{API}{path}", timeout=10)
    response.raise_for_status()
    return pd.DataFrame(response.json())


weeks = st.slider("Weeks to forecast", 1, 26, 12)

try:
    history = get_data("/history")
    forecast = get_data(f"/forecast?weeks={weeks}")
    models = get_data("/models")
except requests.exceptions.RequestException:
    st.error("Cannot reach the backend. Start it first with: python backend\\app.py")
    st.stop()

history["Date"] = pd.to_datetime(history["Date"])
forecast["Date"] = pd.to_datetime(forecast["Date"])

# Convert US dollars to rupees crore
history["Sales_Cr"] = history["Weekly_Sales"] * USD_TO_INR / CRORE
forecast["Forecast_Cr"] = forecast["Forecast_Sales"] * USD_TO_INR / CRORE

best = models.sort_values("MAPE").iloc[0]
peak = forecast.loc[forecast["Forecast_Cr"].idxmax()]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total forecast sales", f"{CURRENCY}{forecast['Forecast_Cr'].sum():,.1f} Cr")
c2.metric("Average per week", f"{CURRENCY}{forecast['Forecast_Cr'].mean():,.1f} Cr")
c3.metric("Peak week", peak["Date"].strftime("%d %b %Y"), f"{CURRENCY}{peak['Forecast_Cr']:,.1f} Cr", delta_color="off")
c4.metric("Best model", best["Model"], f"MAPE {best['MAPE']}%", delta_color="off")

st.subheader("Sales history and forecast")

chart_df = pd.concat([
    history.rename(columns={"Sales_Cr": "Sales"}).assign(Series="History")[["Date", "Sales", "Series"]],
    forecast.rename(columns={"Forecast_Cr": "Sales"}).assign(Series="Forecast")[["Date", "Sales", "Series"]],
])

chart = (
    alt.Chart(chart_df)
    .mark_line(strokeWidth=2)
    .encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Sales:Q", title=f"Weekly Sales ({CURRENCY} crore)", scale=alt.Scale(zero=False)),
        color=alt.Color(
            "Series:N",
            scale=alt.Scale(domain=["History", "Forecast"], range=["#1f77b4", "#ff7f0e"]),
            legend=alt.Legend(title=None),
        ),
        tooltip=["Date:T", "Sales:Q", "Series:N"],
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)

st.subheader("Forecast table")
table = pd.DataFrame({
    "Date": forecast["Date"].dt.date,
    f"Forecast ({CURRENCY} crore)": forecast["Forecast_Cr"].round(2),
})
st.dataframe(table, use_container_width=True)

st.download_button(
    label="Download forecast as CSV",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name="sales_forecast.csv",
    mime="text/csv",
)

st.subheader("Model comparison (lower is better)")
st.caption("MAE and RMSE are in US dollars, as in the original data. MAPE is a percentage.")
st.dataframe(models, use_container_width=True)

st.subheader("Model accuracy comparison")
bar = (
    alt.Chart(models)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("Model:N", sort="y", title=None, axis=alt.Axis(labelAngle=-20)),
        y=alt.Y("MAPE:Q", title="MAPE (%) - lower is better"),
        color=alt.Color("Model:N", legend=None),
        tooltip=["Model:N", "MAPE:Q", "MAE:Q", "RMSE:Q"],
    )
    .properties(height=350)
)
st.altair_chart(bar, use_container_width=True)