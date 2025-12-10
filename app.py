import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinOps Dashboard", layout="wide")

# -------------------------------
# LOAD EXPORTED DATA
# -------------------------------
daily_cost = pd.read_csv("daily_cost_output.csv")
spikes = pd.read_csv("spikes_output.csv")
idle_resources = pd.read_csv("idle_resources_output.csv")
optimization = pd.read_csv("optimization_output.csv")

# Convert date for plotting
daily_cost['date'] = pd.to_datetime(daily_cost['date'])
spikes['date'] = pd.to_datetime(spikes['date'])

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("🚀 FinOps Cost Spike Monitoring & Optimization Dashboard")

st.write("This dashboard visualizes cloud cost trends, detects anomalies, forecasts usage, and recommends optimization actions.")

# =========================================================
# SECTION 1 — TOTAL CLOUD COST TREND
# =========================================================
st.header("📊 Total Cloud Cost Trend")
st.line_chart(daily_cost.set_index("date")['total_cost'])

# =========================================================
# SECTION 2 — COST SPIKES
# =========================================================
st.header("⚠️ Cost Spike Alerts")
if spikes.shape[0] == 0:
    st.success("No spikes detected — costs are stable.")
else:
    st.dataframe(spikes)

# =========================================================
# SECTION 3 — FORECASTING GRAPH (Holt-Winters)
# =========================================================
st.header("🔮 30-Day Cloud Cost Forecast")

from statsmodels.tsa.holtwinters import ExponentialSmoothing

df_fc = daily_cost.copy()
df_fc.set_index("date", inplace=True)

model = ExponentialSmoothing(df_fc['total_cost'], trend="add", seasonal=None)
fit = model.fit()
forecast = fit.forecast(30)

fig, ax = plt.subplots(figsize=(10, 4))
df_fc['total_cost'].plot(ax=ax, label="Historical")
forecast.plot(ax=ax, label="Forecast")
plt.legend()
plt.title("Cloud Cost Forecast (Holt-Winters)")

st.pyplot(fig)

# =========================================================
# SECTION 4 — IDLE RESOURCE DETECTION
# =========================================================
st.header("🛑 Idle Resources (Cost Wastage)")
st.write("Resources with low CPU/memory usage or missing tags.")

st.dataframe(idle_resources)

# =========================================================
# SECTION 5 — OPTIMIZATION ADVISOR
# =========================================================
st.header("🧠 Optimization Recommendations")
st.write("Heuristic-based instance rightsizing and cleanup suggestions.")

st.dataframe(optimization[['resource_id','instance_type','cpu_usage','memory_usage','recommendation']])

# =========================================================
# FOOTER
# =========================================================
st.markdown("___")
st.write("Built for FinOps Hackathon — Cost Spike Monitoring + ML Forecasting + Optimization System.")
