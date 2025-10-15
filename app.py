import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import datetime

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")

# ---- TABS PRINCIPALES ----
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
            {"type": "Encintadora Automática", "count": 1, "capacity": 952},
            {"type": "Encintado Manual", "count": 1, "capacity": 0}]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60",
         "machines": [{"type": "PRA", "count": 3, "capacity": 952}]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748",
         "machines": [{"type": "Orbit", "count": 3, "capacity": 952}]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017",
         "machines": [
            {"type": "Automático", "count": 1, "capacity": 952},
            {"type": "Manual", "count": 1, "capacity": 952}]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7",
         "machines": [
            {"type": "Duo Flex", "count": 2, "capacity": 952},
            {"type": "DLP", "count": 6, "capacity": 952}]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222",
         "machines": [
            {"type": "Manual", "count": 1, "capacity": 952},
            {"type": "Desblocker", "count": 1, "capacity": 952}]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea",
         "machines": [
            {"type": "Foco Vision", "count": 1, "capacity": 952},
            {"type": "Promapper", "count": 1, "capacity": 952}]}
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
         "machines": [{"type": "Manual", "count": 1, "capacity": 1071}]},
        {"name": "Bloqueo", "icon": "🟦", "color": "#2980b9",
         "machines": [{"type": "Manual", "count": 1, "capacity": 1071}]},
        {"name": "Corte", "icon": "✂️", "color": "#27ae60",
         "machines": [
            {"type": "Bisphera", "count": 1, "capacity": 1071},
            {"type": "ES4", "count": 2, "capacity": 1071},
            {"type": "MEI641", "count": 1, "capacity": 1071}]},
        {"name": "Remate", "icon": "🟨", "color": "#f4d03f",
         "machines": [{"type": "Manual", "count": 1, "capacity": 1071}]}
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
    st.title("🔝 Temporada Alta - Capacidad, AR y WIP (Capacidad general por área, turnos y domingos)")
    fechas = [
        "24-nov","25-nov","26-nov","27-nov","28-nov","29-nov","30-nov","1-dic","2-dic","3-dic","4-dic","5-dic","6-dic","7-dic",
        "8-dic","9-dic","10-dic","11-dic","12-dic","13-dic","14-dic","15-dic","16-dic","17-dic","18-dic","19-dic","20-dic",
        "21-dic","22-dic","23-dic","24-dic","25-dic","26-dic","27-dic","28-dic"
    ]
    entradas = [
        677, 642, 600, 572, 602, 738, 246, 1459, 1383, 1293, 1233, 1297, 1592, 530, 730, 692, 647, 617, 649, 796, 265, 686,
        650, 607, 579, 609, 748, 249, 498, 471, 441, 421, 442, 543, 181
    ]

    st.sidebar.header("Capacidad, turnos por área (por turno, no por hora)")
    st.sidebar.subheader("SURF")
    capacidad_surf = st.sidebar.number_input("Capacidad base SURF (lentes/turno)", min_value=1, value=952, key="ta_csurf")
    turnos_surf = st.sidebar.number_input("Turnos SURF (L-V, Sáb)", 1, 4, 3, key="ta_turnos_surf")
    turnos_surf_dom = st.sidebar.number_input("Turnos SURF (Domingo)", 0, 4, 1, key="ta_turnos_surf_dom")
    st.sidebar.subheader("AR")
    capacidad_ar = st.sidebar.number_input("Capacidad base AR (lentes/turno)", min_value=1, value=560, key="ta_car")
    turnos_ar = st.sidebar.number_input("Turnos AR (L-V, Sáb)", 1, 4, 3, key="ta_turnos_ar")
    turnos_ar_dom = st.sidebar.number_input("Turnos AR (Domingo)", 0, 4, 1, key="ta_turnos_ar_dom")
    st.sidebar.subheader("Montaje (E&M)")
    capacidad_em = st.sidebar.number_input("Capacidad base Montaje (lentes/turno)", min_value=1, value=1071, key="ta_cem")
    turnos_em = st.sidebar.number_input("Turnos Montaje (L-V, Sáb)", 1, 4, 3, key="ta_turnos_em")
    turnos_em_dom = st.sidebar.number_input("Turnos Montaje (Domingo)", 0, 4, 1, key="ta_turnos_em_dom")
    st.sidebar.markdown("---")
    st.sidebar.header("Split de flujos después de SURF")
    pct_ar = st.sidebar.slider("% de trabajos de SURF que van a AR", min_value=0, max_value=100, value=80, step=1, key="ta_pct_ar")
    pct_sin_ar = 100 - pct_ar

    year_ref = 2024 if "nov" in fechas[0] else datetime.datetime.now().year
    month_map = {"nov":11, "dic":12}
    date_objs = []
    for f in fechas:
        dia, mes = f.split("-")
        date_obj = datetime.date(year_ref, month_map[mes], int(dia))
        date_objs.append(date_obj)
    df = pd.DataFrame({
        "Fecha": fechas,
        "Fecha_real": date_objs,
        "Entrada_total": entradas
    })
    df["Es_domingo"] = [d.weekday()==6 for d in df["Fecha_real"]]
    df["Capacidad_SURF"] = [
        capacidad_surf * (turnos_surf_dom if row["Es_domingo"] else turnos_surf)
        for idx, row in df.iterrows()
    ]
    df["Capacidad_AR"] = [
        capacidad_ar * (turnos_ar_dom if row["Es_domingo"] else turnos_ar)
        for idx, row in df.iterrows()
    ]
    df["Capacidad_EM"] = [
        capacidad_em * (turnos_em_dom if row["Es_domingo"] else turnos_em)
        for idx, row in df.iterrows()
    ]

    df["Lente_terminado"] = df["Entrada_total"] * 0.25
    df["Lente_surf"] = df["Entrada_total"] * 0.75
    df["Lente_AR"] = df["Lente_surf"] * (pct_ar / 100)
    df["Lente_sin_AR"] = df["Lente_surf"] * (pct_sin_ar / 100)

    df["Salida_SURF_AR"] = np.minimum(df["Lente_AR"], df["Capacidad_SURF"] * (pct_ar/100))
    df["Salida_SURF_Sin_AR"] = np.minimum(df["Lente_sin_AR"], df["Capacidad_SURF"] * (pct_sin_ar/100))
    df["Salida_SURF_Total"] = df["Salida_SURF_AR"] + df["Salida_SURF_Sin_AR"]
    df["WIP_SURF"] = (df["Lente_AR"] + df["Lente_sin_AR"] - df["Salida_SURF_Total"]).cumsum()

    df["Entrada_AR"] = df["Salida_SURF_AR"]
    df["Salida_AR"] = np.minimum(df["Entrada_AR"], df["Capacidad_AR"])
    df["WIP_AR"] = (df["Entrada_AR"] - df["Salida_AR"]).cumsum()

    df["Entrada_EM"] = df["Lente_terminado"] + df["Salida_AR"] + df["Salida_SURF_Sin_AR"]
    df["Salida_EM"] = np.minimum(df["Entrada_EM"], df["Capacidad_EM"])
    df["WIP_EM"] = (df["Entrada_EM"] - df["Salida_EM"]).cumsum()

    st.markdown("""
    **Supuestos**:  
    - 25% de lo que entra es Lente Terminado y va directo a Montaje.  
    - 75% pasa primero por SURF y luego a AR o directo a Montaje según el split.  
    - Puedes ajustar la capacidad base, turnos para cada área y para domingos.  
    - El dashboard calcula la capacidad diaria automáticamente.
    """)

    st.subheader("Entradas y acumulación de WIP en Temporada Alta (con AR, turnos y domingos)")
    st.dataframe(df, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Entrada_total"], name="Entradas totales/día", marker_color="#1f77b4"))
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Lente_terminado"], name="Lente Terminado (directo a Montaje)", marker_color="#2ca02c"))
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Lente_AR"], name="Lentes a AR", marker_color="#ff7f0e"))
    fig.add_trace(go.Bar(x=df["Fecha"], y=df["Lente_sin_AR"], name="Lentes directos a Montaje", marker_color="#f7e017"))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_SURF"], name="WIP SURF", mode="lines+markers", line=dict(color="red", width=3)))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_AR"], name="WIP AR", mode="lines+markers", line=dict(color="blue", width=3)))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_EM"], name="WIP Montaje", mode="lines+markers", line=dict(color="purple", width=3)))
    fig.update_layout(
        barmode='stack',
        title="Carga diaria y acumulación de WIP (SURF - AR - Montaje)",
        xaxis_title="Fecha",
        yaxis_title="Lentes",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    max_wip_surf = int(df["WIP_SURF"].max())
    max_wip_ar = int(df["WIP_AR"].max())
    max_wip_em = int(df["WIP_EM"].max())
    st.info(f"🔴 Máximo WIP acumulado en SURF: **{max_wip_surf} lentes**")
    st.info(f"🔵 Máximo WIP acumulado en AR: **{max_wip_ar} lentes**")
    st.info(f"🟣 Máximo WIP acumulado en Montaje: **{max_wip_em} lentes**")
    if max_wip_surf > 0 or max_wip_ar > 0 or max_wip_em > 0:
        st.warning("⚠️ Para evitar acumulación de WIP, considera aumentar capacidad, turnos o recursos en los procesos cuello de botella durante la temporada alta.")
    else:
        st.success("✔️ La capacidad actual es suficiente para cubrir la demanda de temporada alta sin acumulación significativa de WIP.")

    demanda_max_surf = df["Lente_AR"].max() + df["Lente_sin_AR"].max()
    demanda_max_ar = df["Entrada_AR"].max()
    demanda_max_em = df["Entrada_EM"].max()
    st.markdown(f"""
    **Demanda máxima diaria a SURF:** {int(demanda_max_surf)} lentes  
    **Demanda máxima diaria a AR:** {int(demanda_max_ar)} lentes  
    **Demanda máxima diaria a Montaje:** {int(demanda_max_em)} lentes  
    """)
    st.markdown("**Simula capacidad necesaria para NO acumular WIP:**")
    st.write(f"🔸 Para cubrir el pico en SURF necesitas al menos **{int(np.ceil(demanda_max_surf / max(df['Capacidad_SURF'])))} veces la capacidad diaria máxima configurada**")
    st.write(f"🔸 Para cubrir el pico en AR necesitas al menos **{int(np.ceil(demanda_max_ar / max(df['Capacidad_AR'])))} veces la capacidad diaria máxima configurada**")
    st.write(f"🔸 Para cubrir el pico en Montaje necesitas al menos **{int(np.ceil(demanda_max_em / max(df['Capacidad_EM'])))} veces la capacidad diaria máxima configurada**")
