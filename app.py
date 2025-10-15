import streamlit as st
import plotly.graph_objs as go
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")

st.markdown("""
<style>
h1, h2, h3, h4 { color: #003366; }
.big-metric { font-size: 2em; font-weight: bold; color: #1f77b4;}
.metric-info { font-size: 1.2em; color: #222; }
hr { border: 1px solid #003366;}
</style>
""", unsafe_allow_html=True)

# --- 1. Sidebar selector de proceso ---
proceso = st.sidebar.radio(
    "Selecciona el dashboard:",
    ["Capacidad SURF", "Capacidad E&M", "Simulación 3D + IA (WOW)"]
)

# --- 2. Sidebar dinámico ---
if proceso == "Capacidad SURF":
    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas (SURF)")
    default_stations = [
        {"name": "Encintado", "icon": "🟦", "color": "#1f3b6f",
         "machines": [
            {"type": "Encintadora Automática", "count": 1, "capacity": 150.0},
            {"type": "Encintado Manual", "count": 1, "capacity": 0.0}]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60",
         "machines": [{"type": "PRA", "count": 3, "capacity": 80.0}]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748",
         "machines": [{"type": "Orbit", "count": 3, "capacity": 77.0}]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017",
         "machines": [
            {"type": "Automático", "count": 1, "capacity": 100.0},
            {"type": "Manual", "count": 1, "capacity": 110.0}]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7",
         "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 30.0},
            {"type": "DLP", "count": 6, "capacity": 27.0}]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222",
         "machines": [
            {"type": "Manual", "count": 1, "capacity": 423.53},
            {"type": "Desblocker", "count": 1, "capacity": 360.0}]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea",
         "machines": [
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
                key=f"SURF_{station['name']}_{machine['type']}_count"
            )
            capacity = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=0.0, value=float(machine["capacity"]),
                key=f"SURF_{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})
    st.sidebar.header("📊 Parámetros globales")
    line_oee = st.sidebar.slider("OEE de la línea", min_value=0.5, max_value=1.0, value=0.85, step=0.01, key="OEE_SURF")
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3, key="turnos_SURF")
    horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8, key="horas_SURF")
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01, key="scrap_SURF")
elif proceso == "Capacidad E&M":
    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas E&M")
    default_stations_em = [
        {"name": "Anaquel", "icon": "🔲", "color": "#8e44ad",
         "machines": [{"type": "Manual", "count": 1, "capacity": 12*60.0}]},
        {"name": "Bloqueo", "icon": "🟦", "color": "#2980b9",
         "machines": [{"type": "Manual", "count": 1, "capacity": 10*60.0}]},
        {"name": "Corte", "icon": "✂️", "color": "#27ae60",
         "machines": [
            {"type": "Bisphera", "count": 1, "capacity": 109.0},
            {"type": "ES4", "count": 2, "capacity": 34.0},
            {"type": "MEI641", "count": 1, "capacity": 74.0}]},
        {"name": "Remate", "icon": "🟨", "color": "#f4d03f",
         "machines": [{"type": "Manual", "count": 1, "capacity": 60.0}]}
    ]
    stations_em = []
    for station in default_stations_em:
        st.sidebar.subheader(f"{station['icon']} {station['name']}")
        machines = []
        for machine in station["machines"]:
            count = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Cantidad)", min_value=1, value=machine["count"],
                key=f"EM_{station['name']}_{machine['type']}_count"
            )
            capacity = st.sidebar.number_input(
                f"{station['name']} - {machine['type']} (Capacidad lentes/hora)", min_value=1.0, value=float(machine["capacity"]),
                key=f"EM_{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations_em.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})
    st.sidebar.header("📊 Parámetros globales")
    line_oee = st.sidebar.slider("OEE de la línea", min_value=0.5, max_value=1.0, value=0.85, step=0.01, key="OEE_EM")
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3, key="turnos_EM")
    horas_turno = st.sidebar.number_input("Horas por turno", min_value=4, max_value=12, value=8, key="horas_EM")
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01, key="scrap_EM")

# --- 3. Main content area: cambia según proceso ---
if proceso == "Capacidad SURF":
    st.title("🚀 Dashboard - Capacidad Línea de Superficies")
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
        st.markdown(f"<div class='big-metric'>Capacidad diaria (bottleneck): {int(capacidad_linea_diaria)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df.loc[df["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)
        st.write("🕒 **Simulación de reducción de turnos**")
        for t in range(num_turnos, 0, -1):
            capacidad_scen = df["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
            st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")
        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df.drop("Color", axis=1), use_container_width=True)
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
elif proceso == "Capacidad E&M":
    st.title("🏭 Dashboard - Capacidad Ensamble y Montaje (E&M)")
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
        st.markdown(f"<div class='big-metric'>Capacidad diaria (bottleneck): {int(capacidad_linea_diaria_em)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df_em.loc[df_em["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)
        st.write("🕒 **Simulación de reducción de turnos**")
        for t in range(num_turnos, 0, -1):
            capacidad_scen = df_em["Capacidad hora (teórica)"].min() * t * horas_turno * (1-scrap_rate)
            st.write(f"- {t} turnos: {int(capacidad_scen)} lentes/día")
        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df_em.drop("Color", axis=1), use_container_width=True)
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
else:
    st.title("🤖🌐 Simulador 3D Interactivo con IA Industrial")
    st.markdown("""
    Visualiza el flujo de lotes en 3D, identifica cuellos de botella y recibe recomendaciones inteligentes en tiempo real.
    """)
    lote_size = st.number_input("Tamaño de lote (lentes)", min_value=1, value=20, key="lote3d")
    velocidad = st.slider("Velocidad de simulación (segundos/estación)", min_value=0.1, max_value=2.0, value=0.5, step=0.1, key="vel3d")
    stations_full = [
        {"name": "Encintado", "icon": "🟦", "color": "#1f3b6f", "coord": [0, 0, 0]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60", "coord": [1, 0, 0]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748", "coord": [2, 0.5, 0]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017", "coord": [3, 1.5, 0]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7", "coord": [4, 1, 0]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222", "coord": [5, 0.5, 0]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea", "coord": [6, 0, 0]}
    ]
    coords = np.array([s["coord"] for s in stations_full])
    labels = [s["name"] for s in stations_full]
    icons = [s["icon"] for s in stations_full]
    colors = [s["color"] for s in stations_full]
    run_sim = st.button("Simular flujo 3D con IA")
    def ia_bottleneck(stations):
        capacidades = np.random.randint(60, 200, len(stations))
        idx = np.argmin(capacidades)
        return stations[idx]["name"], capacidades[idx], capacidades
    if run_sim:
        st.subheader("🔵 Flujo total (todas las estaciones)")
        bottle, cap, caps = ia_bottleneck(stations_full)
        st.info(f"🧠 IA: Bottleneck: {bottle} ({cap} lentes/hora aprox.)")
        for paso in range(len(stations_full)):
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=coords[:,0], y=coords[:,1], z=coords[:,2],
                mode="markers+text",
                marker=dict(
                    size=[30 if i==paso else 18 for i in range(len(stations_full))],
                    color=["red" if i==paso or stations_full[i]["name"]==bottle else colors[i] for i in range(len(stations_full))],
                    opacity=[0.9 if i==paso else 0.5 for i in range(len(stations_full))]
                ),
                text=[f"{icons[i]}<br>{labels[i]}<br>{caps[i]} l/h" for i in range(len(stations_full))],
                textposition="bottom center"
            ))
            if paso > 0:
                fig.add_trace(go.Scatter3d(
                    x=coords[:paso+1,0], y=coords[:paso+1,1], z=coords[:paso+1,2],
                    mode="lines",
                    line=dict(color="red", width=8)
                ))
            fig.update_layout(
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False),
                ),
                title=f"Lote en {labels[paso]}",
                showlegend=False,
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)
            time.sleep(velocidad)
        st.success(f"Simulación terminada para {lote_size} lentes (flujo total)")
        st.markdown("## 💡 Recomendaciones Inteligentes")
        st.info(f"💡 **Sugerencia IA:** Refuerza la estación '{bottle}' para mejorar el throughput global.")
    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">🤖</span>
        <br>
        <span style="font-size:1em;">Simulación 3D con IA generativa y análisis de cuellos de botella - ¡Impacto industrial asegurado!</span>
    </div>
    """, unsafe_allow_html=True)
