import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Income Statement - FX & Interest Rate Sensitivity")

# =========================
# INPUTS
# =========================

col1, col2 = st.columns(2)

with col1:

    revenue = st.number_input(
        "Revenue (USD)",
        value=10000000.0,
        step=100000.0
    )

    operating_expenses = st.number_input(
        "Operating Expenses (USD)",
        value=1000000.0,
        step=50000.0
    )

    interest_usd = st.number_input(
        "Interest Expense USD",
        value=500000.0,
        step=10000.0
    )

with col2:

    base_fx = st.number_input(
        "Base Spot FX (MXN/USD)",
        value=17.0,
        step=0.1
    )

    fx = st.slider(
        "Current FX (MXN/USD)",
        min_value=10.0,
        max_value=30.0,
        value=17.0,
        step=0.1
    )

    tiie = st.slider(
        "TIIE (%)",
        min_value=5.0,
        max_value=15.0,
        value=10.0,
        step=0.25
    )

# =========================
# COGS
# =========================

usd_cogs = revenue * 0.15

mxn_cogs_local = revenue * 0.70 * base_fx
mxn_cogs_usd = mxn_cogs_local / fx

total_cogs = usd_cogs + mxn_cogs_usd

gross_profit = revenue - total_cogs

gross_margin = (
    gross_profit / revenue
    if revenue > 0
    else 0
)

# =========================
# EBIT
# =========================

ebit = gross_profit - operating_expenses

# =========================
# DEBT INTEREST
# =========================

mxn_debt = 260_000_000

total_rate = (tiie + 4.0) / 100

interest_mxn = mxn_debt * total_rate

interest_mxn_usd = interest_mxn / fx

total_interest = interest_usd + interest_mxn_usd

# =========================
# EBT
# =========================

ebt = ebit - total_interest

# =========================
# KPIs
# =========================

st.subheader("Key Metrics")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Gross Profit",
    f"${gross_profit:,.0f}"
)

k2.metric(
    "Gross Margin",
    f"{gross_margin:.1%}"
)

k3.metric(
    "EBIT",
    f"${ebit:,.0f}"
)

k4.metric(
    "EBT",
    f"${ebt:,.0f}"
)

# =========================
# INCOME STATEMENT
# =========================

income_statement = pd.DataFrame({
    "Line Item": [
        "Revenue",
        "COGS USD",
        "COGS MXN (USD Eq.)",
        "Total COGS",
        "Gross Profit",
        "Operating Expenses",
        "EBIT",
        "Interest USD",
        "Interest MXN (USD Eq.)",
        "EBT"
    ],
    "USD": [
        revenue,
        -usd_cogs,
        -mxn_cogs_usd,
        -total_cogs,
        gross_profit,
        -operating_expenses,
        ebit,
        -interest_usd,
        -interest_mxn_usd,
        ebt
    ]
})

st.subheader("Income Statement")

st.dataframe(
    income_statement,
    use_container_width=True
)

# =========================
# DETAILS
# =========================

st.subheader("Debt Details")

debt_df = pd.DataFrame({
    "Metric": [
        "MXN Debt",
        "TIIE",
        "Spread",
        "Total Rate",
        "Interest MXN",
        "Interest MXN (USD Eq.)"
    ],
    "Value": [
        f"{mxn_debt:,.0f}",
        f"{tiie:.2f}%",
        "4.00%",
        f"{(tiie+4):.2f}%",
        f"{interest_mxn:,.0f}",
        f"${interest_mxn_usd:,.0f}"
    ]
})

st.dataframe(
    debt_df,
    use_container_width=True
)

# =========================
# FX SENSITIVITY
# =========================

sens = []

for scenario_fx in range(10, 31):

    scenario_mxn_cogs_usd = mxn_cogs_local / scenario_fx

    scenario_interest_usd = interest_mxn / scenario_fx

    scenario_total_cogs = (
        usd_cogs +
        scenario_mxn_cogs_usd
    )

    scenario_gp = revenue - scenario_total_cogs

    scenario_ebit = (
        scenario_gp -
        operating_expenses
    )

    scenario_ebt = (
        scenario_ebit -
        interest_usd -
        scenario_interest_usd
    )

    sens.append({
        "FX": scenario_fx,
        "EBT": scenario_ebt
    })

sens_df = pd.DataFrame(sens).set_index("FX")

st.subheader("EBT Sensitivity to FX")

st.line_chart(sens_df)

# =========================
# TIIE SENSITIVITY
# =========================

st.subheader("EBT Sensitivity to TIIE")

tiie_sensitivity = []

for scenario_tiie in range(5, 16):

    scenario_rate = (scenario_tiie + 4) / 100

    scenario_interest_mxn = (
        mxn_debt *
        scenario_rate
    )

    scenario_interest_usd = (
        scenario_interest_mxn /
        fx
    )

    scenario_ebt = (
        ebit
        - interest_usd
        - scenario_interest_usd
    )

    tiie_sensitivity.append({
        "TIIE (%)": scenario_tiie,
        "EBT": scenario_ebt
    })

tiie_df = pd.DataFrame(
    tiie_sensitivity
).set_index("TIIE (%)")

st.line_chart(tiie_df)

st.subheader("Financial Drivers")

drivers = pd.DataFrame({
    "Metric": [
        "Current FX",
        "TIIE",
        "Spread",
        "Total Interest Rate",
        "MXN Debt"
    ],
    "Value": [
        f"{fx:.2f}",
        f"{tiie:.2f}%",
        "4.00%",
        f"{tiie+4:.2f}%",
        f"{mxn_debt:,.0f}"
    ]
})

st.dataframe(
    drivers,
    use_container_width=True
)
