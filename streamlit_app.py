import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Income Statement FX Sensitivity")

col1, col2 = st.columns(2)

with col1:
    revenue = st.number_input("Revenue (USD)", value=10000000)
    costs = st.number_input("Base Costs (USD)", value=7000000)

with col2:
    base_fx = st.number_input("Base FX (MXN/USD)", value=17.0)
    fx = st.slider("Current FX", 10.0, 30.0, 17.0)

mxn_cost = costs * 0.60
usd_cost = costs * 0.40

mxn_local = mxn_cost * base_fx
mxn_usd = mxn_local / fx

adjusted_costs = mxn_usd + usd_cost
profit = revenue - adjusted_costs
margin = profit / revenue

income_statement = pd.DataFrame({
    "Line Item": ["Revenue", "Costs", "Net Revenue"],
    "USD": [revenue, adjusted_costs, profit]
})

st.subheader("Income Statement")
st.dataframe(income_statement)

c1, c2 = st.columns(2)

c1.metric("Net Revenue", f"${profit:,.0f}")
c2.metric("Margin", f"{margin:.1%}")

sens = []

for scenario_fx in range(10, 31):
    mxn_usd_s = mxn_local / scenario_fx
    cost_s = mxn_usd_s + usd_cost

    sens.append({
        "FX": scenario_fx,
        "Net Revenue": revenue - cost_s
    })

sens_df = pd.DataFrame(sens).set_index("FX")

st.subheader("Net Revenue Sensitivity")
st.line_chart(sens_df)
