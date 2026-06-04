pip install plotly

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="FX Sensitivity Income Statement", layout="wide")

st.title("📈 Income Statement FX Sensitivity")

# Inputs
st.sidebar.header("Assumptions")

revenue_usd = st.sidebar.number_input(
    "Revenue (USD)",
    min_value=0.0,
    value=10_000_000.0,
    step=100_000.0,
    format="%.0f"
)

total_cost_base = st.sidebar.number_input(
    "Total Costs at Base FX (USD)",
    min_value=0.0,
    value=7_000_000.0,
    step=100_000.0,
    format="%.0f"
)

base_fx = st.sidebar.number_input(
    "Base FX Rate (MXN/USD)",
    min_value=1.0,
    value=17.0,
    step=0.1
)

current_fx = st.sidebar.slider(
    "Current FX Rate (MXN/USD)",
    min_value=10.0,
    max_value=30.0,
    value=float(base_fx),
    step=0.1
)

# Cost split
mxn_cost_usd_base = total_cost_base * 0.60
usd_cost = total_cost_base * 0.40

# Convert MXN cost to local currency at base FX
mxn_cost_local = mxn_cost_usd_base * base_fx

# Recalculate MXN cost in USD at new FX
mxn_cost_usd_current = mxn_cost_local / current_fx

# Updated costs
total_cost_current = mxn_cost_usd_current + usd_cost

# Income statement
gross_profit = revenue_usd - total_cost_current

df = pd.DataFrame({
    "Line Item": ["Revenue", "Costs", "Net Revenue"],
    "Amount": [
        revenue_usd,
        -total_cost_current,
        gross_profit
    ]
})

# Waterfall chart
fig = go.Figure(go.Waterfall(
    name="Income Statement",
    orientation="v",
    measure=["absolute", "relative", "total"],
    x=["Revenue", "Costs", "Net Revenue"],
    y=[revenue_usd, -total_cost_current, 0],
    connector={"line": {"color": "gray"}}
))

fig.update_layout(
    title=f"Income Statement at FX = {current_fx:.2f} MXN/USD",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Sensitivity analysis
st.subheader("FX Sensitivity Analysis")

fx_range = [x / 10 for x in range(100, 301)]

profits = []

for fx in fx_range:
    mxn_cost_usd = mxn_cost_local / fx
    total_cost = mxn_cost_usd + usd_cost
    profit = revenue_usd - total_cost
    profits.append(profit)

sens_df = pd.DataFrame({
    "FX Rate": fx_range,
    "Net Revenue": profits
})

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=sens_df["FX Rate"],
        y=sens_df["Net Revenue"],
        mode="lines",
        name="Net Revenue"
    )
)

fig2.add_vline(
    x=current_fx,
    line_dash="dash",
    annotation_text=f"Current FX: {current_fx:.1f}"
)

fig2.update_layout(
    title="Net Revenue vs FX Rate",
    xaxis_title="MXN/USD",
    yaxis_title="Net Revenue (USD)",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Revenue", f"${revenue_usd:,.0f}")
col2.metric("Total Costs", f"${total_cost_current:,.0f}")
col3.metric("Net Revenue", f"${gross_profit:,.0f}")

# Cost breakdown
st.subheader("Cost Breakdown")

breakdown = pd.DataFrame({
    "Cost Type": ["MXN Costs (USD Equivalent)", "USD Costs"],
    "Amount": [mxn_cost_usd_current, usd_cost]
})

st.dataframe(
    breakdown.style.format({"Amount": "${:,.0f}"}),
    use_container_width=True
)
