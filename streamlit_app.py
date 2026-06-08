import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Simulador EBITDA - Autlán",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Simulador de EBITDA - Autlán")
st.markdown("Modelo simplificado para analizar sensibilidad de EBITDA ante ingresos y tipo de cambio.")

# =====================================
# INPUTS
# =====================================

st.sidebar.header("Supuestos")

ingresos = st.sidebar.number_input(
    "Ingresos (USD)",
    min_value=0.0,
    value=500_000_000.0,
    step=1_000_000.0,
    format="%.2f"
)

tipo_cambio = st.sidebar.number_input(
    "Tipo de Cambio Spot (MXN/USD)",
    min_value=1.0,
    value=18.50,
    step=0.10
)

st.sidebar.markdown("---")

gastos_venta = st.sidebar.number_input(
    "Gastos de Venta (USD)",
    value=15_000_000.0,
    step=100_000.0
)

gastos_admin = st.sidebar.number_input(
    "Gastos de Administración (USD)",
    value=20_000_000.0,
    step=100_000.0
)

otros_ingresos = st.sidebar.number_input(
    "Otros Ingresos (USD)",
    value=0.0,
    step=100_000.0
)

otros_gastos = st.sidebar.number_input(
    "Otros Gastos (USD)",
    value=0.0,
    step=100_000.0
)

ingresos_financieros = st.sidebar.number_input(
    "Ingresos Financieros (USD)",
    value=2_000_000.0,
    step=100_000.0
)

gastos_financieros = st.sidebar.number_input(
    "Gastos Financieros (USD)",
    value=25_000_000.0,
    step=100_000.0
)

depreciacion_amortizacion = st.sidebar.number_input(
    "Depreciación y Amortización (USD)",
    value=30_000_000.0,
    step=100_000.0
)

# =====================================
# COGS MODEL
# =====================================

cogs_total = ingresos * 0.85

cogs_usd_fijo = cogs_total * 0.15
cogs_mxn = cogs_total * 0.85

# Convertimos la parte en MXN a dólares usando TC spot
cogs_mxn_en_usd = (cogs_mxn * tipo_cambio) / tipo_cambio

# costo total en USD
cogs_total_ajustado = cogs_usd_fijo + cogs_mxn_en_usd

# =====================================
# ESTADO DE RESULTADOS
# =====================================

utilidad_bruta = ingresos - cogs_total_ajustado

utilidad_operacion = (
    utilidad_bruta
    - gastos_venta
    - gastos_admin
    + otros_ingresos
    - otros_gastos
)

utilidad_antes_impuestos = (
    utilidad_operacion
    + ingresos_financieros
    - gastos_financieros
)

ebitda = utilidad_operacion + depreciacion_amortizacion

margen_bruto = utilidad_bruta / ingresos if ingresos > 0 else 0
margen_operacion = utilidad_operacion / ingresos if ingresos > 0 else 0
margen_ebitda = ebitda / ingresos if ingresos > 0 else 0

# =====================================
# KPIs
# =====================================

st.subheader("📊 Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ingresos",
    f"${ingresos:,.0f}"
)

col2.metric(
    "Utilidad Bruta",
    f"${utilidad_bruta:,.0f}"
)

col3.metric(
    "EBITDA",
    f"${ebitda:,.0f}"
)

col4.metric(
    "Margen EBITDA",
    f"{margen_ebitda:.1%}"
)

# =====================================
# DETALLE COGS
# =====================================

st.subheader("⚙️ Desglose de Costo de Ventas")

detalle_cogs = pd.DataFrame({
    "Concepto": [
        "COGS Total (85% ventas)",
        "Parte USD (15%)",
        "Parte MXN (85%)",
        "Tipo de Cambio",
        "COGS Total Ajustado"
    ],
    "Valor": [
        cogs_total,
        cogs_usd_fijo,
        cogs_mxn,
        tipo_cambio,
        cogs_total_ajustado
    ]
})

st.dataframe(
    detalle_cogs,
    use_container_width=True,
    hide_index=True
)

# =====================================
# ESTADO DE RESULTADOS
# =====================================

st.subheader("📄 Estado de Resultados Simplificado")

estado_resultados = pd.DataFrame({
    "Concepto": [
        "Ingresos",
        "Costo de Ventas",
        "Utilidad Bruta",
        "Gastos de Venta",
        "Gastos de Administración",
        "Otros Ingresos",
        "Otros Gastos",
        "Utilidad Operativa",
        "Ingresos Financieros",
        "Gastos Financieros",
        "Utilidad Antes de Impuestos",
        "Depreciación y Amortización",
        "EBITDA"
    ],
    "USD": [
        ingresos,
        -cogs_total_ajustado,
        utilidad_bruta,
        -gastos_venta,
        -gastos_admin,
        otros_ingresos,
        -otros_gastos,
        utilidad_operacion,
        ingresos_financieros,
        -gastos_financieros,
        utilidad_antes_impuestos,
        depreciacion_amortizacion,
        ebitda
    ]
})

st.dataframe(
    estado_resultados.style.format({"USD": "${:,.0f}"}),
    use_container_width=True,
    hide_index=True
)

# =====================================
# MÁRGENES
# =====================================

st.subheader("📈 Márgenes")

margenes = pd.DataFrame({
    "Indicador": [
        "Margen Bruto",
        "Margen Operativo",
        "Margen EBITDA"
    ],
    "Valor": [
        margen_bruto,
        margen_operacion,
        margen_ebitda
    ]
})

st.dataframe(
    margenes.style.format({"Valor": "{:.1%}"}),
    use_container_width=True,
    hide_index=True
)

# =====================================
# SENSIBILIDAD TIPO DE CAMBIO
# =====================================

st.subheader("🌎 Sensibilidad Tipo de Cambio")

escenarios = [15, 16, 17, 18, 19, 20, 21, 22]

sensibilidad = []

for tc in escenarios:

    cogs_tc = cogs_usd_fijo + ((cogs_mxn * tc) / tc)

    utilidad_bruta_tc = ingresos - cogs_tc

    utilidad_operacion_tc = (
        utilidad_bruta_tc
        - gastos_venta
        - gastos_admin
        + otros_ingresos
        - otros_gastos
    )

    ebitda_tc = utilidad_operacion_tc + depreciacion_amortizacion

    margen_tc = ebitda_tc / ingresos

    sensibilidad.append([
        tc,
        ebitda_tc,
        margen_tc
    ])

df_sensibilidad = pd.DataFrame(
    sensibilidad,
    columns=[
        "Tipo Cambio",
        "EBITDA",
        "Margen EBITDA"
    ]
)

st.dataframe(
    df_sensibilidad.style.format({
        "EBITDA": "${:,.0f}",
        "Margen EBITDA": "{:.1%}"
    }),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Modelo simplificado para análisis de sensibilidad de EBITDA de Autlán."
)




import numpy as np
import plotly.express as px

st.subheader("🌎 Sensibilidad EBITDA vs Tipo de Cambio")

fx_range = np.arange(14, 24.5, 0.5)

ebitda_fx = []

for tc in fx_range:

    # Parte MXN fija
    cogs_mxn_fijo = cogs_total * 0.85 * tipo_cambio

    cogs_usd_tc = cogs_usd_fijo + (cogs_mxn_fijo / tc)

    utilidad_bruta_tc = ingresos - cogs_usd_tc

    utilidad_operacion_tc = (
        utilidad_bruta_tc
        - gastos_venta
        - gastos_admin
        + otros_ingresos
        - otros_gastos
    )

    ebitda_tc = utilidad_operacion_tc + depreciacion_amortizacion

    ebitda_fx.append(ebitda_tc)

df_fx = pd.DataFrame({
    "Tipo de Cambio": fx_range,
    "EBITDA": ebitda_fx
})

fig_fx = px.line(
    df_fx,
    x="Tipo de Cambio",
    y="EBITDA",
    title="Impacto del Tipo de Cambio en EBITDA"
)

st.plotly_chart(fig_fx, use_container_width=True)
