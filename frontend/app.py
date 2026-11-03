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
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    h1 { animation: fadeUp 0.8s ease-out backwards; }
    div[data-testid="stMetric"] {
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background-size: 250% 250% !important;
        animation: fadeUp 0.8s ease-out backwards, gradientShift 6s ease infinite;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 12px 24px rgba(0,0,0,0.25);
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

        [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #cfe8ff 0%, #eaf4ff 40%, #ffffff 100%) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    @keyframes drift {
        from { transform: translateX(-25vw); }
        to { transform: translateX(125vw); }
    }
    .cloud {
        position: fixed;
        z-index: 0;
        pointer-events: none;
        opacity: 0.75;
        animation: drift linear infinite;
    }

    </style>
    """,
    unsafe_allow_html=True,
)
LAT, LON, CITY = 20.30, 85.82, "Bhubaneswar"  # change to your city


@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon,
                    "current": "temperature_2m,weather_code,is_day"},
            timeout=5,
        )
        r.raise_for_status()
        cur = r.json()["current"]
        return int(cur["weather_code"]), float(cur["temperature_2m"]), bool(cur["is_day"])
    except Exception:
        return None


def pick_theme(code, is_day):
    if not is_day:
        return dict(label="Clear night", bg="#0b1d3a, #1d3b6b", icon="✨", kind="drift", dark=True)
    if code == 0:
        return dict(label="Sunny", bg="#8ed1ff, #fff6cc", icon="☀️", kind="drift", dark=False)
    if code in (1, 2, 3):
        return dict(label="Cloudy", bg="#cfe8ff, #ffffff", icon="☁️", kind="drift", dark=False)
    if code in (45, 48):
        return dict(label="Foggy", bg="#d9dee3, #f4f6f8", icon="🌫️", kind="drift", dark=False)
    if code in (71, 73, 75, 77, 85, 86):
        return dict(label="Snow", bg="#dfe9f5, #ffffff", icon="❄️", kind="fall", dark=False)
    if code in (95, 96, 99):
        return dict(label="Thunderstorm", bg="#3b4560, #6b7894", icon="💧", kind="fall", dark=True)
    return dict(label="Rainy", bg="#9fb4c7, #dfe7ee", icon="💧", kind="fall", dark=False)


def particles(icon, kind, n):
    items = []
    for i in range(n):
        if kind == "fall":
            style = (f"left:{(i * 97) % 100}%; font-size:{16 + (i % 3) * 6}px; "
                     f"animation-duration:{2 + (i % 4) * 0.6}s; animation-delay:-{(i % 7) * 0.5}s;")
        else:
            style = (f"top:{8 + (i * 17) % 70}%; font-size:{40 + (i % 4) * 18}px; "
                     f"animation-duration:{60 + (i % 4) * 20}s; animation-delay:-{(i * 13) % 60}s;")
        items.append(f'<div class="particle {kind}" style="{style}">{icon}</div>')
    return "".join(items)


weather = get_weather(LAT, LON)
if weather:
    w_code, w_temp, w_day = weather
    theme = pick_theme(w_code, w_day)
    st.caption(f"{theme['icon']} {CITY}: {w_temp:.0f}°C, {theme['label']}")
else:
    theme = pick_theme(2, True)
    st.caption("Weather unavailable, showing the default sky")

css = (
    "@keyframes drift {from {transform: translateX(-25vw);} to {transform: translateX(125vw);}}"
    "@keyframes fall {from {transform: translateY(-10vh);} to {transform: translateY(110vh);}}"
    ".particle {position: fixed; z-index: 0; pointer-events: none; opacity: 0.75;}"
    ".particle.drift {left: 0; animation: drift linear infinite;}"
    ".particle.fall {top: -10vh; animation: fall linear infinite;}"
)
css += (f'[data-testid="stAppViewContainer"] {{background: linear-gradient(180deg, {theme["bg"]}) '
        f'!important;}}')
if theme["dark"]:
    css += ('[data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, '
            '[data-testid="stAppViewContainer"] h3, [data-testid="stCaptionContainer"], '
            '[data-testid="stMarkdownContainer"] p, button[data-baseweb="tab"] p, '
            '[data-testid="stWidgetLabel"] p {color: #f0f4ff !important;}')

st.markdown(f"<style>{css}</style>" + particles(theme["icon"], theme["kind"], 14),
            unsafe_allow_html=True)
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

tab1, tab2, tab3 = st.tabs(["📈 Overview", "🗓️ Forecast", "🤖 Models"])

# ---------- Tab 1: Overview ----------
with tab1:
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

# ---------- Tab 2: Forecast ----------
with tab2:
    st.subheader("Forecast table")

    col = f"Forecast ({CURRENCY} crore)"
    table = pd.DataFrame({
        "Date": forecast["Date"].dt.date,
        col: forecast["Forecast_Cr"].round(2),
    })

    low_cut = history["Sales_Cr"].quantile(0.33)
    high_cut = history["Sales_Cr"].quantile(0.66)

    def level(value):
        if value >= high_cut:
            return "High"
        if value <= low_cut:
            return "Low"
        return "Medium"

    table["Level"] = table[col].apply(level)

    def colour_row(row):
        colours = {"High": "#c8f7c5", "Medium": "#fff3b0", "Low": "#ffc9c9"}
        return [f"background-color: {colours[row['Level']]}; color: #1a1a2e"] * len(row)

    st.caption("🟩 High   🟨 Medium   🟥 Low (compared with past weekly sales)")
    st.dataframe(
        table.style.apply(colour_row, axis=1).format({col: "{:,.2f}"}),
        use_container_width=True,
    )

    st.download_button(
        label="Download forecast as CSV",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="sales_forecast.csv",
        mime="text/csv",
    )

# ---------- Tab 3: Models ----------
with tab3:
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