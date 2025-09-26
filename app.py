import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np

st.set_page_config(page_title="🚀 Dash de Capacidad Línea de Superficies", layout="wide")
st.title("Dashboard - Capacidad Línea de Superficies")

# --- 1. Parámetros editables ---
st.sidebar.header("🔧 Configuración de Estaciones y Máquinas")

default_stations = [
    {
        "name": "Encintado",
        "icon": "🟦",
        "color": "#1f3b6f",         # Azul oscuro
        "machines": [
            {"type": "Encintadora Automática", "count": 1, "capacity": 150, "oee": 0.85}
        ]
    },
    {
        "name": "Bloqueo Digital",
        "icon": "🟩",
        "color": "#27ae60",         # Verde
        "machines": [
            {"type": "PRA", "count": 3, "capacity": 80, "oee": 0.85}
        ]
    },
    {
        "name": "Generado Digital",
        "icon": "🟫",
        "color": "#8d6748",         # Café
        "machines": [
            {"type": "Orbit", "count": 3, "capacity": 77, "oee": 0.85}
        ]
    },
    {
        "name": "Laser",
        "icon": "🟨",
        "color": "#f7e017",         # Amarillo
        "machines": [
            {"type": "Automático", "count": 1, "capacity": 100, "oee": 0.90},
            {"type": "Manual", "count": 1, "capacity": 110, "oee": 0.80}
        ]
    },
    {
        "name": "Pulido",
        "icon": "🟪",
        "color": "#7d3fc7",         # Morado
        "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 30, "oee": 0.80},
            {"type": "DLP", "count": 6, "capacity": 27, "oee": 0.80}
        ]
    },
    {
        "name": "Desbloqueo",
        "icon": "⬛",
        "color": "#222222",         # Gris oscuro
        "machines": [
            {"type": "Manual", "count": 1, "capacity": 50, "oee": 0.75},
            {"type": "Desblocker", "count": 1, "capacity": 0, "oee": 0.75}
        ]
    },
    {
        "name": "Calidad",
        "icon": "⬜",
        "color": "#eaeaea",         # Gris claro/Blanco
        "machines": [
            {"type": "Foco Vision", "count": 1, "capacity": 0, "oee": 0.90},
            {"type": "Promapper", "count": 1, "capacity": 0, "oee": 0.90}
        ]
    }
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
            f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=0, value=machine["capacity"],
            key=f"{station['name']}_{machine['type']}_capacity"
        )
        oee = st.sidebar.slider(
            f"{station['name']} - {machine['type']} (OEE)", min_value=0.5, max_value=1.0, value=machine["oee"],
            step=0.01, key=f"{station['name']}_{machine['type']}_oee"
        )
        machines.append({"type": machine["type"], "count": count, "capacity": capacity, "oee": oee})
    stations.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})

# --- 2. Parámetros de Turnos y Scrap ---
st.sidebar.header("🕒 Turnos y Scrap")
num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3)
horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8)
scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)

# --- 3. Importación de datos (opcional) ---
st.sidebar.header("📂 Importa datos reales")
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel/CSV (opcional)", type=["xlsx", "csv"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
    st.write("📊 Datos importados:")
    st.dataframe(df_input)

# --- 4. Cálculo de capacidad por estación ---
station_capacity = []
for station in stations:
    total_capacity = sum([m["count"] * m["capacity"] * m["oee"] for m in station["machines"]])
    capacidad_diaria = total_capacity * num_turnos * horas_turno * (1 - scrap_rate)
    station_capacity.append({
        "Estación": f"{station['icon']} {station['name']}",
        "Color": station["color"],
        "Capacidad hora (teórica)": total_capacity,
        "Capacidad diaria (real)": capacidad_diaria
    })

df = pd.DataFrame(station_capacity)

# --- 5. Simulación de flujo y acumulación ---
capacidad_linea_diaria = df["Capacidad diaria (real)"].min()

# --- 6. Dashboard visual ---
bar_colors = df["Color"].tolist()
bar_names = df["Estación"].tolist()

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
    st.metric("Capacidad diaria de la línea (bottleneck)", f"{int(capacidad_linea_diaria)} lentes/día")
    bottleneck = df.loc[df["Capacidad diaria (real)"].idxmin()]
    st.write(f"🔴 **Cuello de botella:** {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)")

    st.write("🕒 **Simulación de reducción de turnos**")
    for t in range(num_turnos, 0, -1):
        capacidad_scen = df["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
        st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")

    st.write("📝 **Resumen de parámetros**")
    st.dataframe(df.drop("Color", axis=1), use_container_width=True)  # Quita la columna de color

# --- 7. Exportación de resultados ---
st.header("💾 Exporta tu análisis")
st.download_button("Descargar tabla de capacidad en CSV", data=df.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_linea.csv', mime='text/csv')

# --- 8. Tooltips, Expander y UI Moderna ---
with st.expander("🧐 ¿Cómo se calculan los KPIs?"):
    st.markdown("""
    - **Capacidad hora (teórica):** ∑ (máquinas × capacidad × OEE) por estación.
    - **Capacidad diaria (real):** Capacidad hora × número de turnos × horas por turno × (1 - scrap).
    - **Cuello de botella:** Estación con menor capacidad diaria.
    - **OEE:** Eficiencia operacional (Disponibilidad × Rendimiento × Calidad).
    - **Scrap:** Tasa de rechazo en la línea: Quiebra en el caso de Optisa.
    - **Simulación de turnos:** Capacidad de la línea si se reduce el número de turnos.
    
    """)



st.markdown("""
<div style="text-align:center;">
    <span style="font-size:2em;"></span>
    <br>
    <span style="font-size:1em;">Hecho por Ing.Sebastian Guerrero!</span>
</div>
""", unsafe_allow_html=True)
