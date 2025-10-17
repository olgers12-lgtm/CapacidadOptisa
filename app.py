import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral y Simulación WIP", layout="wide")
st.markdown("""
<style>
h1, h2, h3, h4 { color: #003366; }
.big-metric { font-size: 2em; font-weight: bold; color: #1f77b4;}
.metric-info { font-size: 1.2em; color: #222; }
hr { border: 1px solid #003366;}
</style>
""", unsafe_allow_html=True)

colA, colB = st.columns(2)
with colA:
    st.image("https://cdn-icons-png.flaticon.com/512/3103/3103474.png", width=70)
with colB:
    st.markdown("<h1 style='margin-top:10px;'>Dashboard de Capacidad Integral</h1>", unsafe_allow_html=True)

tab = st.radio(
    "Selecciona el proceso:", 
    options=["SURF (Superficies)", "E&M (Ensamble y Montaje)", "Simulación WIP"], 
    horizontal=True
)

# ========== BLOQUE 1: SURF (Superficies) ==========
if tab == "SURF (Superficies)":
    st.markdown("---")
    st.markdown("## 🚀 Superficies - Capacidad, Bottleneck y Simulación Industrial")

    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas (SURF)")
    default_stations = [
        {"name": "Encintado", "icon": "🟦", "color": "#1f3b6f", "machines": [
            {"type": "Encintadora Automática", "count": 1, "capacity": 150.0},
            {"type": "Encintado Manual", "count": 1, "capacity": 0.0}]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60", "machines": [
            {"type": "PRA", "count": 3, "capacity": 80.0}]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748", "machines": [
            {"type": "Orbit", "count": 3, "capacity": 77.0}]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017", "machines": [
            {"type": "Automático", "count": 1, "capacity": 100.0},
            {"type": "Manual", "count": 1, "capacity": 110.0}]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7", "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 30.0},
            {"type": "DLP", "count": 6, "capacity": 27.0}]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222", "machines": [
            {"type": "Manual", "count": 1, "capacity": 423.53},
            {"type": "Desblocker", "count": 1, "capacity": 360.0}]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea", "machines": [
            {"type": "Foco Vision", "count": 1, "capacity": 60.0},
            {"type": "Promapper", "count": 1, "capacity": 110.0}]}
    ]

    stations = []
    for station in default_stations:
        st.sidebar.subheader(f"{station['icon']} {station['name']}")
        machines = []
        for machine in station["machines"]:
            count = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Cantidad)", min_value=1, value=machine["count"],
                key=f"{station['name']}_{machine['type']}_count"
            )
            capacity = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=0.0, value=float(machine["capacity"]),
                key=f"{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})

    st.sidebar.header("📊 Parámetros globales")
    line_oee = st.sidebar.slider("OEE de la línea", min_value=0.5, max_value=1.0, value=0.85, step=0.01)
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3)
    horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8)
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)

    st.sidebar.header("📂 Importar datos reales")
    uploaded_file = st.sidebar.file_uploader("Cargar archivo Excel/CSV (opcional)", type=["xlsx", "csv"])
    if uploaded_file:
        df_input = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
        st.write("📊 Datos importados:")
        st.dataframe(df_input)

    station_capacity = []
    for station in stations:
        total_capacity = sum([m["count"] * m["capacity"] for m in station["machines"]]) * line_oee
        capacidad_diaria = total_capacity * num_turnos * horas_turno * (1 - scrap_rate)
        station_capacity.append({
            "Estación": f"{station['icon']} {station['name']}",
            "Color": station["color"],
            "Capacidad hora (teórica)": total_capacity,
            "Capacidad diaria (real)": capacidad_diaria
        })

    df = pd.DataFrame(station_capacity)
    capacidad_linea_diaria = df["Capacidad diaria (real)"].min()

    bar_colors = df["Color"].tolist()
    bar_names = df["Estación"].tolist()

    st.markdown("### 🔍 Visualización de Capacidad y Bottleneck")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("⚙️ Capacidad por Estación")
        fig = go.Figure(
            go.Bar(
                x=bar_names,
                y=df["Capacidad hora (teórica)"],
                marker_color=bar_colors,
                text=np.round(df["Capacidad hora (teórica)"], 1),
                textposition='outside'
            )
        )
        fig.update_layout(title="Capacidad por Estación (lentes/hora)", yaxis_title="Lentes/hora", xaxis_title="Estación")
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = go.Figure(
            go.Funnel(
                y=bar_names,
                x=df["Capacidad diaria (real)"],
                textinfo="value+percent initial",
                marker={"color": bar_colors}
            )
        )
        fig2.update_layout(title="Flujo y Bottleneck (lentes/día)", funnelmode="stack")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("📈 KPIs y Simulación")
        st.markdown(f"<div class='big-metric'>Cap. diaria (bottleneck): {int(capacidad_linea_diaria)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df.loc[df["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)

        st.write("🕒 **Simulación de reducción de turnos**")
        for t in range(num_turnos, 0, -1):
            capacidad_scen = df["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
            st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")

        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df.drop("Color", axis=1), use_container_width=True)

    st.markdown("---")
    st.header("💾 Exportar análisis")
    st.download_button("Descargar tabla de capacidad en CSV", data=df.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_linea.csv', mime='text/csv')

    with st.expander("¿Cómo se calculan los KPIs?"):
        st.markdown(f"""
        - **Capacidad hora (teórica):** ∑ (máquinas × capacidad) por estación × OEE de la línea ({line_oee:.2f}).
        - **Capacidad diaria (real):** Capacidad hora × número de turnos × horas por turno × (1 - scrap).
        - **Cuello de botella:** Estación con menor capacidad diaria.
        - Puedes importar datos reales y ajustar todos los parámetros para simular escenarios de mejora industrial.
        """)

    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">👨‍💼</span>
        <br>
        <span style="font-size:1em;">Hecho por Ing. Sebastian Guerrero!</span>
    </div>
    """, unsafe_allow_html=True)

# ========== BLOQUE 2: E&M ==========
elif tab == "E&M (Ensamble y Montaje)":
    st.markdown("---")
    st.markdown("## 🏭 Ensamble y Montaje - Capacidad, Bottleneck y Simulación Industrial")

    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas E&M")
    default_stations_em = [
        {"name": "Anaquel", "icon": "🔲", "color": "#8e44ad", "machines": [
            {"type": "Manual", "count": 1, "capacity": 12*60.0}]},
        {"name": "Bloqueo", "icon": "🟦", "color": "#2980b9", "machines": [
            {"type": "Manual", "count": 1, "capacity": 10*60.0}]},
        {"name": "Corte", "icon": "✂️", "color": "#27ae60", "machines": [
            {"type": "Bisphera", "count": 1, "capacity": 109.0},
            {"type": "ES4", "count": 2, "capacity": 34.0},
            {"type": "MEI641", "count": 1, "capacity": 74.0}]},
        {"name": "Remate", "icon": "🟨", "color": "#f4d03f", "machines": [
            {"type": "Manual", "count": 1, "capacity": 60.0}]}
    ]

    stations_em = []
    for station in default_stations_em:
        st.sidebar.subheader(f"{station['icon']} {station['name']}")
        machines = []
        for machine in station["machines"]:
            count = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Cantidad)", min_value=1, value=machine["count"],
                key=f"E&M_{station['name']}_{machine['type']}_count"
            )
            capacity = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=1.0, value=float(machine["capacity"]),
                key=f"E&M_{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations_em.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})

    st.sidebar.header("📊 Parámetros globales")
    line_oee = st.sidebar.slider("OEE de la línea", min_value=0.5, max_value=1.0, value=0.85, step=0.01)
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3)
    horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8)
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)

    station_capacity_em = []
    for station in stations_em:
        total_capacity = sum([m["count"] * m["capacity"] for m in station["machines"]]) * line_oee
        capacidad_diaria = total_capacity * num_turnos * horas_turno * (1 - scrap_rate)
        station_capacity_em.append({
            "Estación": f"{station['icon']} {station['name']}",
            "Color": station["color"],
            "Capacidad hora (teórica)": total_capacity,
            "Capacidad diaria (real)": capacidad_diaria
        })
    df_em = pd.DataFrame(station_capacity_em)
    capacidad_linea_diaria_em = df_em["Capacidad diaria (real)"].min()

    bar_colors = df_em["Color"].tolist()
    bar_names = df_em["Estación"].tolist()

    st.markdown("### 🔍 Visualización de Capacidad y Bottleneck")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("⚙️ Capacidad por Estación")
        fig = go.Figure(
            go.Bar(
                x=bar_names,
                y=df_em["Capacidad hora (teórica)"],
                marker_color=bar_colors,
                text=np.round(df_em["Capacidad hora (teórica)"], 1),
                textposition='outside'
            )
        )
        fig.update_layout(title="Capacidad por Estación (lentes/hora)", yaxis_title="Lentes/hora", xaxis_title="Estación")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure(
            go.Funnel(
                y=bar_names,
                x=df_em["Capacidad diaria (real)"],
                textinfo="value+percent initial",
                marker={"color": bar_colors}
            )
        )
        fig2.update_layout(title="Flujo y Bottleneck (lentes/día)", funnelmode="stack")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("📈 KPIs y Simulación")
        st.markdown(f"<div class='big-metric'>Cap. diaria (bottleneck): {int(capacidad_linea_diaria_em)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df_em.loc[df_em["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)

        st.write("🕒 **Simulación de reducción de turnos**")
        for t in range(num_turnos, 0, -1):
            capacidad_scen = df_em["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
            st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")

        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df_em.drop("Color", axis=1), use_container_width=True)

    st.markdown("---")
    st.header("💾 Exportar análisis")
    st.download_button("Descargar tabla de capacidad en CSV", data=df_em.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_em.csv', mime='text/csv')

    with st.expander("¿Cómo se calculan los KPIs?"):
        st.markdown(f"""
        - **Capacidad hora (teórica):** ∑ (máquinas × capacidad) por estación × OEE de la línea ({line_oee:.2f}).
        - **Capacidad diaria (real):** Capacidad hora × número de turnos × horas por turno × (1 - scrap).
        - **Cuello de botella:** Estación con menor capacidad diaria.
        - Puedes importar datos reales y ajustar todos los parámetros para simular escenarios de mejora industrial.
        """)

    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">👨‍💼</span>
        <br>
        <span style="font-size:1em;">Hecho por Ing. Sebastian Guerrero!</span>
    </div>
    """, unsafe_allow_html=True)

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
