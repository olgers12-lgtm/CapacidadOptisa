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
        "color": "#1f3b6f",
        "machines": [
            {"type": "Encintadora Automática", "count": 1, "capacity": 150},
            {"type": "Encintado Manual", "count": 1, "capacity": 0}
        ]
    },
    {
        "name": "Bloqueo Digital",
        "icon": "🟩",
        "color": "#27ae60",
        "machines": [
            {"type": "PRA", "count": 3, "capacity": 80}
        ]
    },
    {
        "name": "Generado Digital",
        "icon": "🟫",
        "color": "#8d6748",
        "machines": [
            {"type": "Orbit", "count": 3, "capacity": 77}
        ]
    },
    {
        "name": "Laser",
        "icon": "🟨",
        "color": "#f7e017",
        "machines": [
            {"type": "Automático", "count": 1, "capacity": 100},
            {"type": "Manual", "count": 1, "capacity": 110}
        ]
    },
    {
        "name": "Pulido",
        "icon": "🟪",
        "color": "#7d3fc7",
        "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 30},
            {"type": "DLP", "count": 6, "capacity": 27}
        ]
    },
    {
        "name": "Desbloqueo",
        "icon": "⬛",
        "color": "#222222",
        "machines": [
            {"type": "Manual", "count": 1, "capacity": 50},
            {"type": "Desblocker", "count": 1, "capacity": 0}
        ]
    },
    {
        "name": "Calidad",
        "icon": "⬜",
        "color": "#eaeaea",
        "machines": [
            {"type": "Foco Vision", "count": 1, "capacity": 0},
            {"type": "Promapper", "count": 1, "capacity": 0}
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
        machines.append({"type": machine["type"], "count": count, "capacity": capacity})
    stations.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})

# --- Parámetro de mix de trabajos ---
st.sidebar.header("🧮 Mix de trabajos")
pct_standard = st.sidebar.slider("Porcentaje de trabajos Standard (%)", min_value=0, max_value=100, value=27, step=1)
pct_free = 100 - pct_standard

# --- OEE de la línea ---
st.sidebar.header("📊 Parámetros globales")
line_oee = st.sidebar.slider("OEE de la línea", min_value=0.5, max_value=1.0, value=0.85, step=0.01)

# --- 2. Parámetros de Turnos y Scrap ---
st.sidebar.header("🕒 Turnos y Scrap")
num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3)
horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8)
scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)

# --- 3. Importación de datos (opcional) ---
st.sidebar.header("📂 Importar datos reales")
uploaded_file = st.sidebar.file_uploader("Cargar archivo Excel/CSV (opcional)", type=["xlsx", "csv"])
if uploaded_file:
    df_input = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)
    st.write("📊 Datos importados:")
    st.dataframe(df_input)

# --- 4. Cálculo de capacidad por estación para cada tipo de trabajo ---
station_capacity_standard = []
station_capacity_free = []

for station in stations:
    # Standard: Laser se omite (capacidad = 0)
    if station["name"] == "Laser":
        total_capacity_standard = 0
    else:
        total_capacity_standard = sum([m["count"] * m["capacity"] for m in station["machines"]]) * line_oee
    capacidad_diaria_standard = total_capacity_standard * num_turnos * horas_turno * (1 - scrap_rate)
    station_capacity_standard.append({
        "Estación": f"{station['icon']} {station['name']}",
        "Color": station["color"],
        "Capacidad hora (teórica)": total_capacity_standard,
        "Capacidad diaria (real)": capacidad_diaria_standard
    })

    # Free: Laser incluido
    total_capacity_free = sum([m["count"] * m["capacity"] for m in station["machines"]]) * line_oee
    capacidad_diaria_free = total_capacity_free * num_turnos * horas_turno * (1 - scrap_rate)
    station_capacity_free.append({
        "Estación": f"{station['icon']} {station['name']}",
        "Color": station["color"],
        "Capacidad hora (teórica)": total_capacity_free,
        "Capacidad diaria (real)": capacidad_diaria_free
    })

df_standard = pd.DataFrame(station_capacity_standard)
df_free = pd.DataFrame(station_capacity_free)

capacidad_linea_diaria_standard = df_standard["Capacidad diaria (real)"].min()
capacidad_linea_diaria_free = df_free["Capacidad diaria (real)"].min()

# --- 5. Dashboard visual ---
bar_colors_std = df_standard["Color"].tolist()
bar_names_std = df_standard["Estación"].tolist()
bar_colors_free = df_free["Color"].tolist()
bar_names_free = df_free["Estación"].tolist()

st.subheader("⚙️ Capacidad por Estación - Standard")
fig_std = go.Figure(
    go.Bar(
        x=bar_names_std,
        y=df_standard["Capacidad hora (teórica)"],
        marker_color=bar_colors_std,
        text=np.round(df_standard["Capacidad hora (teórica)"], 1),
        textposition='outside'
    )
)
fig_std.update_layout(title="Capacidad por Estación STANDARD (lentes/hora)", yaxis_title="Lentes/hora", xaxis_title="Estación")
st.plotly_chart(fig_std, use_container_width=True)

st.subheader("⚙️ Capacidad por Estación - Free (Digital)")
fig_free = go.Figure(
    go.Bar(
        x=bar_names_free,
        y=df_free["Capacidad hora (teórica)"],
        marker_color=bar_colors_free,
        text=np.round(df_free["Capacidad hora (teórica)"], 1),
        textposition='outside'
    )
)
fig_free.update_layout(title="Capacidad por Estación FREE/DIGITAL (lentes/hora)", yaxis_title="Lentes/hora", xaxis_title="Estación")
st.plotly_chart(fig_free, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 KPIs Standard")
    st.metric("Capacidad diaria Standard", f"{int(capacidad_linea_diaria_standard * pct_standard / 100)} lentes/día")
    bottleneck_std = df_standard.loc[df_standard["Capacidad diaria (real)"].idxmin()]
    st.write(f"🔴 **Cuello de botella (Standard):** {bottleneck_std['Estación']} ({int(bottleneck_std['Capacidad diaria (real)'])} lentes/día)")
    st.write("📝 **Resumen de parámetros Standard**")
    st.dataframe(df_standard.drop("Color", axis=1), use_container_width=True)

with col2:
    st.subheader("📈 KPIs Free (Digital)")
    st.metric("Capacidad diaria Free (Digital)", f"{int(capacidad_linea_diaria_free * pct_free / 100)} lentes/día")
    bottleneck_free = df_free.loc[df_free["Capacidad diaria (real)"].idxmin()]
    st.write(f"🔴 **Cuello de botella (Free):** {bottleneck_free['Estación']} ({int(bottleneck_free['Capacidad diaria (real)'])} lentes/día)")
    st.write("📝 **Resumen de parámetros Free (Digital)**")
    st.dataframe(df_free.drop("Color", axis=1), use_container_width=True)

# --- 6. Exportación de resultados ---
st.header("💾 Exportar análisis")
st.download_button("Descargar tabla Standard en CSV", data=df_standard.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_standard.csv', mime='text/csv')
st.download_button("Descargar tabla Free (Digital) en CSV", data=df_free.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_free.csv', mime='text/csv')

# --- 7. Tooltips, Expander y UI Moderna ---
with st.expander("¿Cómo se calculan los KPIs?"):
    st.markdown(f"""
    - Separamos los flujos de trabajos STANDARD y FREE (Digital).
    - STANDARD: NO pasa por estación Laser.
    - FREE: pasa por Laser.
    - **Capacidad hora (teórica):** ∑ (máquinas × capacidad) por estación × OEE de la línea ({line_oee:.2f}).
    - **Capacidad diaria (real):** Capacidad hora × número de turnos × horas por turno × (1 - scrap).
    - **Cuello de botella:** Estación con menor capacidad diaria por tipo de trabajo.
    - Puedes importar datos reales y ajustar todos los parámetros para simular escenarios de mejora industrial.
    """)

st.markdown("""
<div style="text-align:center;">
    <span style="font-size:2em;"></span>
    <br>
    <span style="font-size:1em;">Hecho por Ing. Sebastian Guerrero!</span>
</div>
""", unsafe_allow_html=True)
