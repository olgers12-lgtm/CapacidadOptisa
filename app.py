import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.title("Simulación WIP Variable - Escenario tipo Excel")

# --- Fechas y entradas ---
dias = [
    "1-dic","2-dic","3-dic","4-dic","5-dic","6-dic","7-dic","8-dic","9-dic","10-dic","11-dic","12-dic","13-dic","14-dic"
]
mes_map = {
    'ene':'Jan', 'feb':'Feb', 'mar':'Mar', 'abr':'Apr', 'may':'May', 'jun':'Jun',
    'jul':'Jul', 'ago':'Aug', 'sep':'Sep', 'oct':'Oct', 'nov':'Nov', 'dic':'Dec'
}
def traduce_fecha(fecha_str, year=2025):
    dia, mes = fecha_str.split('-')
    mes_en = mes_map[mes.lower()]
    return f"{dia}-{mes_en}-{year}"
dias_en = [traduce_fecha(d) for d in dias]
dias_fecha = pd.to_datetime(dias_en, format="%d-%b-%Y")

entradas = np.array([889,1332,1358,1340,1488,2070,309,732,789,685,637,668,681,204])

# --- Parámetros variables ---
st.sidebar.header("🔧 Parámetros de Simulación WIP")
wip_inicial = st.sidebar.number_input("WIP inicial (1-dic)", min_value=0, value=1200)
turnos = st.sidebar.number_input("Turnos", min_value=1, max_value=4, value=2)
cap_ar_por_turno = st.sidebar.number_input("Capacidad AR (cuello botella) por turno de 7h", min_value=1, value=290)
lt_pct = st.sidebar.slider("Porcentaje de LT (%)", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
surf_capa_pct = st.sidebar.slider("Porcentaje de SURF+CAPA (%)", min_value=0.0, max_value=1.0, value=0.08, step=0.01)

# CORRECTO: Capacidad AR diaria = turnos * 290 (no multiplica por horas)
cap_ar_dia = turnos * cap_ar_por_turno

outputs_objetivo = []
wip = []
salidas = []
wip_actual = wip_inicial

for i in range(len(dias)):
    entrada = entradas[i]
    output_obj = cap_ar_dia + (entrada * lt_pct) + (entrada * surf_capa_pct)
    outputs_objetivo.append(output_obj)
    salida = min(wip_actual + entrada, output_obj)
    salidas.append(salida)
    wip_actual = wip_actual + entrada - salida
    wip.append(wip_actual)

df_sim = pd.DataFrame({
    "Fecha": dias_fecha,
    "Entradas": entradas,
    "Output Objetivo": np.round(outputs_objetivo, 2),
    "Salidas": np.round(salidas, 2),
    "WIP": np.round(wip, 2)
})

st.markdown("### KPIs de la Simulación")
col1, col2, col3 = st.columns(3)
col1.metric("WIP final", f"{wip[-1]:.0f}")
col2.metric("WIP máximo", f"{np.max(wip):.0f}")
col3.metric("WIP mínimo", f"{np.min(wip):.0f}")

st.subheader("Evolución diaria de Entradas, Salidas y WIP (Simulación)")
fig = go.Figure()
fig.add_trace(go.Bar(x=df_sim["Fecha"], y=df_sim["Entradas"], name="Entradas", marker=dict(color="#2ca02c"), opacity=0.6))
fig.add_trace(go.Bar(x=df_sim["Fecha"], y=df_sim["Salidas"], name="Salidas (Output Real)", marker=dict(color="#d62728"), opacity=0.6))
fig.add_trace(go.Scatter(x=df_sim["Fecha"], y=df_sim["WIP"], name="WIP", mode="lines+markers", line=dict(width=3, color="#1f77b4")))
fig.add_trace(go.Scatter(x=df_sim["Fecha"], y=df_sim["Output Objetivo"], name="Output Objetivo diario", mode="lines", line=dict(dash="dash", color="#555")))
fig.update_layout(barmode='overlay', xaxis_title="Fecha", yaxis_title="Cantidad", legend_title="Variable", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Tabla de Simulación")
st.dataframe(df_sim, use_container_width=True)
st.download_button("Descargar simulación (CSV)", data=df_sim.to_csv(index=False).encode("utf-8"), file_name="simulacion_wip_variable.csv", mime="text/csv")

with st.expander("¿Cómo se calcula el output objetivo?"):
    st.markdown(f"""
    - **Capacidad AR diaria:** turnos × 290 (cuello botella por turno de 7h)
    - **Output objetivo diario:** capacidad AR + (entrada del día × %LT) + (entrada del día × %SURF+CAPA)
    - **WIP:** WIP[i] = WIP[i-1] + Entradas[i] - Salidas[i]
    - **Salidas:** mínimo entre output objetivo y WIP disponible + entradas
    - **Puedes mover los parámetros para ver el efecto en el WIP y las salidas!
    """)
