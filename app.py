import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import datetime

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")

tab = st.sidebar.radio(
    "Selecciona el dashboard:",
    ["Capacidad SURF", "Capacidad E&M", "Temporada Alta"]
)

if tab == "Capacidad SURF":
    st.title("🚀 Dashboard - Capacidad Línea de Superficies")
    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas (SURF)")
    default_stations = [
        {"name": "Encintado", "icon": "🟦", "color": "#1f3b6f",
         "machines": [
            {"type": "Encintadora Automática", "count": 1, "capacity": 150},
            {"type": "Encintado Manual", "count": 1, "capacity": 0}
         ]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60",
         "machines": [{"type": "PRA", "count": 3, "capacity": 80}]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748",
         "machines": [{"type": "Orbit", "count": 3, "capacity": 77}]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017",
         "machines": [
            {"type": "Automático", "count": 1, "capacity": 100},
            {"type": "Manual", "count": 1, "capacity": 110}
         ]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7",
         "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 30},
            {"type": "DLP", "count": 6, "capacity": 27}
         ]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222",
         "machines": [
            {"type": "Manual", "count": 1, "capacity": 423.53},
            {"type": "Desblocker", "count": 1, "capacity": 360}
         ]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea",
         "machines": [
            {"type": "Foco Vision", "count": 1, "capacity": 60},
            {"type": "Promapper", "count": 1, "capacity": 110}
         ]}
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
                f"{station['name']} - {machine['type']} (Capacidad lentes/turno)", min_value=0.0, value=float(machine["capacity"]),
                key=f"SURF_{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})
    st.sidebar.header("📊 Parámetros globales")
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3, key="turnos_SURF")
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01, key="scrap_SURF")

    station_capacity = []
    for station in stations:
        total_capacity = sum([m["count"] * m["capacity"] for m in station["machines"]])
        capacidad_diaria = total_capacity * num_turnos * (1 - scrap_rate)
        station_capacity.append({
            "Estación": f"{station['icon']} {station['name']}",
            "Color": station["color"],
            "Capacidad turno (teórica)": total_capacity,
            "Capacidad diaria (real)": capacidad_diaria
        })
    df = pd.DataFrame(station_capacity)
    capacidad_linea_diaria = df["Capacidad diaria (real)"].min()
    bar_colors = df["Color"].tolist()
    bar_names = df["Estación"].tolist()

    def get_text_colors(bar_colors, fallback="black"):
        color_map = []
        for color in bar_colors:
            color = color.lower()
            if color in ["#eaeaea", "#ffffff", "white"]:
                color_map.append("black")
            elif color in ["#f7e017", "#f4d03f", "#ffff00", "yellow"]:
                color_map.append("black")
            else:
                color_map.append("white")
        return color_map
    text_colors = get_text_colors(bar_colors)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("⚙️ Capacidad por Estación")
        fig = go.Figure(
            go.Bar(
                x=bar_names,
                y=df["Capacidad turno (teórica)"],
                marker_color=bar_colors,
                text=np.round(df["Capacidad turno (teórica)"], 1),
                textposition='outside'
            )
        )
        fig.update_layout(title="Capacidad por Estación (lentes/turno)", yaxis_title="Lentes/turno", xaxis_title="Estación")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = go.Figure(
            go.Funnel(
                y=bar_names,
                x=df["Capacidad diaria (real)"],
                textinfo="value+percent initial",
                marker={"color": bar_colors},
                textfont=dict(
                    size=28,
                    family="Arial Black, Arial, sans-serif",
                    color=text_colors
                )
            )
        )
        fig2.update_layout(title="Flujo y Bottleneck (lentes/día)", funnelmode="stack")
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader("📈 KPIs y Simulación")
        st.markdown(f"<div class='big-metric'>Capacidad diaria (bottleneck): {int(capacidad_linea_diaria)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df.loc[df["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)
        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df.drop("Color", axis=1), use_container_width=True)
    st.header("💾 Exportar análisis")
    st.download_button("Descargar tabla de capacidad en CSV", data=df.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_linea.csv', mime='text/csv')
    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">👨‍💼</span>
        <br>
        <span style="font-size:1em;">Hecho por Ing. Sebastian Guerrero!</span>
    </div>
    """, unsafe_allow_html=True)

elif tab == "Capacidad E&M":
    st.title("🏭 Dashboard - Capacidad Ensamble y Montaje (E&M)")
    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas E&M")
    default_stations_em = [
        {"name": "Anaquel", "icon": "🔲", "color": "#8e44ad",
         "machines": [{"type": "Manual", "count": 1, "capacity": 150}]},
        {"name": "Bloqueo", "icon": "🟦", "color": "#2980b9",
         "machines": [{"type": "Manual", "count": 1, "capacity": 120}]},
        {"name": "Corte", "icon": "✂️", "color": "#27ae60",
         "machines": [
            {"type": "Bisphera", "count": 1, "capacity": 80},
            {"type": "ES4", "count": 2, "capacity": 70},
            {"type": "MEI641", "count": 1, "capacity": 65}
         ]},
        {"name": "Remate", "icon": "🟨", "color": "#f4d03f",
         "machines": [{"type": "Manual", "count": 1, "capacity": 110}]}
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
                f"{station['name']} - {machine['type']} (Capacidad lentes/turno)", min_value=1.0, value=float(machine["capacity"]),
                key=f"EM_{station['name']}_{machine['type']}_capacity"
            )
            machines.append({"type": machine["type"], "count": count, "capacity": capacity})
        stations_em.append({"name": station["name"], "icon": station["icon"], "color": station["color"], "machines": machines})
    st.sidebar.header("📊 Parámetros globales")
    num_turnos = st.sidebar.number_input("Número de turnos", min_value=1, max_value=4, value=3, key="turnos_EM")
    scrap_rate = st.sidebar.slider("Tasa de scrap (%)", min_value=0.0, max_value=0.2, value=0.05, step=0.01, key="scrap_EM")

    station_capacity_em = []
    for station in stations_em:
        total_capacity = sum([m["count"] * m["capacity"] for m in station["machines"]])
        capacidad_diaria = total_capacity * num_turnos * (1 - scrap_rate)
        station_capacity_em.append({
            "Estación": f"{station['icon']} {station['name']}",
            "Color": station["color"],
            "Capacidad turno (teórica)": total_capacity,
            "Capacidad diaria (real)": capacidad_diaria
        })
    df_em = pd.DataFrame(station_capacity_em)
    capacidad_linea_diaria_em = df_em["Capacidad diaria (real)"].min()
    bar_colors = df_em["Color"].tolist()
    bar_names = df_em["Estación"].tolist()

    def get_text_colors(bar_colors, fallback="black"):
        color_map = []
        for color in bar_colors:
            color = color.lower()
            if color in ["#eaeaea", "#ffffff", "white"]:
                color_map.append("black")
            elif color in ["#f7e017", "#f4d03f", "#ffff00", "yellow"]:
                color_map.append("black")
            else:
                color_map.append("white")
        return color_map
    text_colors = get_text_colors(bar_colors)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("⚙️ Capacidad por Estación")
        fig = go.Figure(
            go.Bar(
                x=bar_names,
                y=df_em["Capacidad turno (teórica)"],
                marker_color=bar_colors,
                text=np.round(df_em["Capacidad turno (teórica)"], 1),
                textposition='outside'
            )
        )
        fig.update_layout(title="Capacidad por Estación (lentes/turno)", yaxis_title="Lentes/turno", xaxis_title="Estación")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = go.Figure(
            go.Funnel(
                y=bar_names,
                x=df_em["Capacidad diaria (real)"],
                textinfo="value+percent initial",
                marker={"color": bar_colors},
                textfont=dict(
                    size=28,
                    family="Arial Black, Arial, sans-serif",
                    color=text_colors
                )
            )
        )
        fig2.update_layout(title="Flujo y Bottleneck (lentes/día)", funnelmode="stack")
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader("📈 KPIs y Simulación")
        st.markdown(f"<div class='big-metric'>Capacidad diaria (bottleneck): {int(capacidad_linea_diaria_em)} lentes/día</div>", unsafe_allow_html=True)
        bottleneck = df_em.loc[df_em["Capacidad diaria (real)"].idxmin()]
        st.markdown(f"<div class='metric-info'>🔴 <b>Cuello de botella:</b> {bottleneck['Estación']} ({int(bottleneck['Capacidad diaria (real)'])} lentes/día)</div>", unsafe_allow_html=True)
        st.write("📝 **Resumen de parámetros**")
        st.dataframe(df_em.drop("Color", axis=1), use_container_width=True)
    st.header("💾 Exportar análisis")
    st.download_button("Descargar tabla de capacidad en CSV", data=df_em.drop("Color", axis=1).to_csv(index=False).encode('utf-8'), file_name='capacidad_em.csv', mime='text/csv')
    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">👨‍💼</span>
        <br>
        <span style="font-size:1em;">Hecho por Ing. Sebastian Guerrero!</span>
    </div>
    """, unsafe_allow_html=True)

elif tab == "Temporada Alta":
    # (Mantén aquí la lógica de Temporada Alta con los splits, WIP, capacidades, etc. como antes)
    # Puedes integrar el bloque de Temporada Alta que ya tienes, usando la lógica y parámetros de los dashboards anteriores,
    # incluyendo la configuración de capacidades por máquina/estación/área desde los dashboards anteriores.
    st.title("🔝 Temporada Alta - Simulación por jobs/lentes y WIP dinámico por área (2025)")
    st.sidebar.header("Visualización")
    ver_en = st.sidebar.radio("¿Visualizar en?", ["Jobs (pares de lentes)", "Lentes"])
    # ... resto igual ...
