import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")

# --- PESTAÑAS PRINCIPALES ---
tabs = st.tabs(["Capacidad SURF", "Capacidad E&M", "Temporada Alta"])

# --------- TAB 1: Capacidad SURF ---------
with tabs[0]:
    st.title("🚀 Dashboard - Capacidad Línea de Superficies")

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

# --------- TAB 2: Capacidad E&M ---------
with tabs[1]:
    st.title("🏭 Dashboard - Capacidad Ensamble y Montaje (E&M)")

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

# --------- TAB 3: Temporada Alta ---------
with tabs[2]:
    st.title("🔝 Temporada Alta - Capacidad y Acumulación de WIP")

    # === ENTRADAS ===
    fechas = [
        "24-nov","25-nov","26-nov","27-nov","28-nov","29-nov","30-nov","1-dic","2-dic","3-dic","4-dic","5-dic","6-dic","7-dic",
        "8-dic","9-dic","10-dic","11-dic","12-dic","13-dic","14-dic","15-dic","16-dic","17-dic","18-dic","19-dic","20-dic",
        "21-dic","22-dic","23-dic","24-dic","25-dic","26-dic","27-dic","28-dic"
    ]
    entradas = [
        677, 642, 600, 572, 602, 738, 246, 1459, 1383, 1293, 1233, 1297, 1592, 530, 730, 692, 647, 617, 649, 796, 265, 686,
        650, 607, 579, 609, 748, 249, 498, 471, 441, 421, 442, 543, 181
    ]

    st.markdown("""
    **Supuestos**:  
    - 25% de lo que entra es Lente Terminado y va directo a Montaje.  
    - 75% pasa primero por SURF y luego a Montaje.  
    - Puedes ajustar la capacidad diaria de SURF y Montaje en el panel lateral.
    """)

    st.sidebar.header("Parámetros de Capacidad (Temporada Alta)")
    capacidad_surf = st.sidebar.number_input("Capacidad diaria SURF (lentes/día)", min_value=100, value=1200, key="capacidad_surf_ta")
    capacidad_em = st.sidebar.number_input("Capacidad diaria Montaje (E&M) (lentes/día)", min_value=100, value=1500, key="capacidad_em_ta")

    df = pd.DataFrame({
        "Fecha": fechas,
        "Entrada_total": entradas
    })
    df["Lente_terminado"] = df["Entrada_total"] * 0.25
    df["Lente_surf"] = df["Entrada_total"] * 0.75

    df["Salida_SURF"] = np.minimum(df["Lente_surf"], capacidad_surf)
    df["WIP_SURF"] = (df["Lente_surf"] - df["Salida_SURF"]).cumsum()

    df["Lentes_montaje"] = df["Salida_SURF"] + df["Lente_terminado"]
    df["Salida_EM"] = np.minimum(df["Lentes_montaje"], capacidad_em)
    df["WIP_EM"] = (df["Lentes_montaje"] - df["Salida_EM"]).cumsum()

    st.subheader("Entradas diarias y acumulación de WIP en temporada alta")
    st.dataframe(df, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Entrada_total"], name="Entradas totales/día", marker_color="#1f77b4"))
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Lente_terminado"], name="Lente Terminado (directo a Montaje)", marker_color="#2ca02c"))
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Lente_surf"], name="Lente pasa por SURF", marker_color="#ff7f0e"))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_SURF"], name="WIP acumulado en SURF", mode="lines+markers", line=dict(color="red", width=3)))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_EM"], name="WIP acumulado en Montaje", mode="lines+markers", line=dict(color="purple", width=3)))
    fig.update_layout(
        barmode='stack',
        title="Carga diaria y acumulación de WIP en temporada alta",
        xaxis_title="Fecha",
        yaxis_title="Lentes",
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)

    max_wip_surf = int(df["WIP_SURF"].max())
    max_wip_em = int(df["WIP_EM"].max())
    st.info(f"🔴 Máximo WIP acumulado en SURF: **{max_wip_surf} lentes**")
    st.info(f"🟣 Máximo WIP acumulado en Montaje: **{max_wip_em} lentes**")
    if max_wip_surf > 0 or max_wip_em > 0:
        st.warning(f"Para evitar acumulación de WIP, considera aumentar capacidad diaria, turnos, horas, o recursos en las estaciones cuello de botella durante la temporada alta.")
    else:
        st.success("✔️ La capacidad actual es suficiente para cubrir la demanda de temporada alta sin acumulación significativa de WIP.")

    demanda_max_surf = df["Lente_surf"].max()
    demanda_max_em = df["Lentes_montaje"].max()
    st.markdown(f"""
    **Demanda máxima diaria a SURF:** {int(demanda_max_surf)} lentes  
    **Demanda máxima diaria a Montaje:** {int(demanda_max_em)} lentes  
    """)
    st.markdown("**Simula capacidad necesaria para NO acumular WIP:**")
    st.write(f"🔸 Para cubrir el pico en SURF necesitas al menos **{int(np.ceil(demanda_max_surf/capacidad_surf))} veces la capacidad diaria actual**")
    st.write(f"🔸 Para cubrir el pico en Montaje necesitas al menos **{int(np.ceil(demanda_max_em/capacidad_em))} veces la capacidad diaria actual**")
