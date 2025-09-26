import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

# --- Configuración inicial
st.set_page_config(page_title="🚀 Capacidad AR Dashboard Épico", layout="wide")
st.title("🦾 Epic Dashboard de Ingeniería - Capacidad Línea de Superficies")

# --- Función para configuración de estaciones y máquinas (sidebar)
def get_estaciones_config(sidebar):
    estaciones = [
        {
            "name": "Encintado",
            "icon": "🟦",
            "machines": [
                {"type": "Encintadora Automática", "count": 1, "capacity": 150, "oee": 0.85}
            ]
        },
        {
            "name": "Bloqueo Digital",
            "icon": "🟩",
            "machines": [
                {"type": "PRA", "count": 3, "capacity": 80, "oee": 0.85}
            ]
        },
        {
            "name": "Generado Digital",
            "icon": "🟫",
            "machines": [
                {"type": "Orbit", "count": 3, "capacity": 77, "oee": 0.85}
            ]
        },
        {
            "name": "Laser",
            "icon": "🟨",
            "machines": [
                {"type": "Automático", "count": 1, "capacity": 100, "oee": 0.90},
                {"type": "Manual", "count": 1, "capacity": 110, "oee": 0.80}
            ]
        },
        {
            "name": "Pulido",
            "icon": "🟪",
            "machines": [
                {"type": "Duo Flex", "count": 2, "capacity": 30, "oee": 0.80},
                {"type": "DLP", "count": 6, "capacity": 27, "oee": 0.80}
            ]
        },
        {
            "name": "Desbloqueo",
            "icon": "⬛",
            "machines": [
                {"type": "Manual", "count": 1, "capacity": 50, "oee": 0.75},
                {"type": "Desblocker", "count": 1, "capacity": 0, "oee": 0.75}
            ]
        },
        {
            "name": "Calidad",
            "icon": "⬜",
            "machines": [
                {"type": "Foco Vision", "count": 1, "capacity": 0, "oee": 0.90},
                {"type": "Promapper", "count": 1, "capacity": 0, "oee": 0.90}
            ]
        }
    ]
    estaciones_update = []
    for station in estaciones:
        sidebar.subheader(f"{station['icon']} {station['name']}")
        machines = []
        for machine in station["machines"]:
            count = sidebar.number_input(
                f"{station['name']} - {machine['type']} (Cantidad)", min_value=1, value=machine["count"],
                key=f"{station['name']}_{machine['type']}_count"
            )
            capacity = sidebar.number_input(
                f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=0, value=machine["capacity"],
                key=f"{station['name']}_{machine['type']}_capacity"
            )
            oee = sidebar.slider(
                f"{station['name']} - {machine['type']} (OEE)", min_value=0.5, max_value=1.0, value=machine["oee"],
                step=0.01, key=f"{station['name']}_{machine['type']}_oee"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity, "oee": oee})
        estaciones_update.append({"name": station["name"], "icon": station["icon"], "machines": machines})
    return estaciones_update

# --- Sidebar: parámetros editables
st.sidebar.header("🔧 Configuración de Estaciones y Máquinas")
stations = get_estaciones_config(st.sidebar)

st.sidebar.header("🕒 Turnos y Scrap")
num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3)
horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8)
scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)

# --- Importación de datos (opcional)
st.sidebar.header("📂 Importa datos reales")
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel/CSV (opcional)", type=["xlsx", "csv"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
    st.write("📊 Datos importados:")
    st.dataframe(df_input)

# --- Cálculo de capacidad por estación
station_capacity = []
for station in stations:
    total_capacity = sum([m["count"] * m["capacity"] * m["oee"] for m in station["machines"]])
    capacidad_diaria = total_capacity * num_turnos * horas_turno * (1 - scrap_rate)
    station_capacity.append({
        "Estación": f"{station['icon']} {station['name']}",
        "Capacidad hora (teórica)": total_capacity,
        "Capacidad diaria (real)": capacidad_diaria
    })
df = pd.DataFrame(station_capacity)
capacidad_linea_diaria = df["Capacidad diaria (real)"].min()
bottleneck = df.loc[df["Capacidad diaria (real)"].idxmin()]

# --- Dashboard visual principal
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("⚙️ Capacidad por Estación")
    fig = go.Figure(
        go.Bar(
            x=df["Estación"],
            y=df["Capacidad hora (teórica)"],
            marker_color='deepskyblue',
            text=np.round(df["Capacidad hora (teórica)"], 1),
            textposition='outside'
        )
    )
    fig.update_layout(title="Capacidad por Estación (lentes/hora)", yaxis_title="Lentes/hora", xaxis_title="Estación")
    st.plotly_chart(fig, use_container_width=True)
    # --- Animación de flujo/lote (Sankey)
    st.subheader("💡 Simulación de flujo/lote (Sankey)")
    node_labels = [station["icon"] + " " + station["name"] for station in stations]
    capacities = df["Capacidad diaria (real)"].tolist()
    source = list(range(len(node_labels)-1))
    target = list(range(1, len(node_labels)))
    value = [min(capacities[i], capacities[i+1]) for i in range(len(capacities)-1)]
    sankey_fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=["red" if v==min(value) else "lightblue" for v in value]
        ))])
    sankey_fig.update_layout(title_text="Flujo de producción (Sankey)", font_size=10)
    st.plotly_chart(sankey_fig, use_container_width=True)
    st.info(f"Capacidad limitada por cuello de botella: {int(capacidad_linea_diaria)} lentes/día")

with col2:
    st.subheader("📈 KPIs y Simulación")
    st.metric("Capacidad diaria de la línea (bottleneck)", f"{int(capacidad_linea_diaria)} lentes/día")
    st.write(f"🔴 **Cuello de botella:** {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)")
    # --- Alertas inteligentes
    if bottleneck["Capacidad diaria (real)"] < 1000:
        st.error("¡Bottleneck crítico! Se recomienda intervención del equipo.")
    st.write("🕒 **Simulación de reducción de turnos**")
    for t in range(num_turnos, 0, -1):
        capacidad_scen = df["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
        st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")
    st.write("📝 **Resumen de parámetros**")
    st.dataframe(df, use_container_width=True)

# --- Exportación de resultados
st.header("💾 Exporta tu análisis")
st.download_button("Descargar tabla de capacidad en CSV", data=df.to_csv(index=False).encode('utf-8'), file_name='capacidad_linea.csv', mime='text/csv')

# --- Historial y tendencias (simulado)
st.header("📅 Historial y Tendencias")
fechas = pd.date_range("2024-01-01", periods=12, freq="M")
capacidad_mes = [1500+100*i for i in range(12)]
scrap_mes = [0.05+0.01*(i%3) for i in range(12)]
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=fechas, y=capacidad_mes, mode='lines+markers', name='Capacidad (lentes/día)'))
fig_hist.add_trace(go.Scatter(x=fechas, y=[s*100 for s in scrap_mes], mode='lines+markers', name='Scrap (%)', yaxis='y2'))
fig_hist.update_layout(
    title="Tendencia de Capacidad y Scrap",
    yaxis=dict(title='Capacidad (lentes/día)'),
    yaxis2=dict(title='Scrap (%)', overlaying='y', side='right')
)
st.plotly_chart(fig_hist, use_container_width=True)
st.write("Carga tus datos históricos para análisis real.")

# --- Gamificación ingenieril
st.header("🏆 Gamificación Ingenieril")
if capacidad_linea_diaria > 2500:
    st.success("¡Ganaste la medalla 'Lean Master'! 🚀")
elif capacidad_linea_diaria > 2000:
    st.info("¡Ganaste la medalla 'Mejora Continua'! 🔧")
else:
    st.warning("¡Desbloquea la medalla subiendo tu capacidad! 💪")
st.write(f"Logro actual: **{bottleneck['Estación']}** como cuello de botella. ¿Podrás romper el récord el próximo mes?")

# --- Tooltips, Expander y UI Moderna
with st.expander("🧐 ¿Cómo se calculan los KPIs?"):
    st.markdown("""
    - **Capacidad hora (teórica):** ∑ (máquinas × capacidad × OEE) por estación.
    - **Capacidad diaria (real):** Capacidad hora × número de turnos × horas por turno × (1 - scrap).
    - **Cuello de botella:** Estación con menor capacidad diaria.
    - **OEE:** Eficiencia operacional (Disponibilidad × Rendimiento × Calidad).
    - **Scrap:** Tasa de rechazo en la línea.
    - **Simulación de turnos:** Capacidad de la línea si se reduce el número de turnos.
    - Puedes importar datos reales y ajustar todos los parámetros para simular escenarios de mejora industrial.
    """)

st.success("🚀 ¡Dashboard épico listo! Modifica parámetros, simula escenarios, genera reportes, alerta al equipo y gana medallas ingenieriles.")

st.markdown("""
<div style="text-align:center;">
    <span style="font-size:2em;">🤘</span><br>
    <span style="font-size:1em;">Hecho por ingenieros, para ingenieros. ¡Haz que tu línea sea legendaria!</span>
</div>
""", unsafe_allow_html=True)
