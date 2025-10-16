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
         "machines": [{"type": "Encintadora Automática", "count": 1, "capacity": 952},
                      {"type": "Encintado Manual", "count": 1, "capacity": 0}]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60",
         "machines": [{"type": "PRA", "count": 3, "capacity": 952}]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748",
         "machines": [{"type": "Orbit", "count": 3, "capacity": 952}]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017",
         "machines": [{"type": "Automático", "count": 1, "capacity": 952},
                      {"type": "Manual", "count": 1, "capacity": 952}]},
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7",
         "machines": [{"type": "Duo Flex", "count": 2, "capacity": 952},
                      {"type": "DLP", "count": 6, "capacity": 952}]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222",
         "machines": [{"type": "Manual", "count": 1, "capacity": 952},
                      {"type": "Desblocker", "count": 1, "capacity": 952}]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea",
         "machines": [{"type": "Foco Vision", "count": 1, "capacity": 952},
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
                marker={"color": bar_colors},
                textfont=dict(
                    size=28,
                    family="Arial Black, Arial, sans-serif",
                    color="white"
                )
            )
        )
        fig2.update_layout(
            title="Flujo y Bottleneck (lentes/día)",
            funnelmode="stack"
        )
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
                marker={"color": bar_colors},
                textfont=dict(
                    size=28,
                    family="Arial Black, Arial, sans-serif",
                    color="white"
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
    st.title("🔝 Temporada Alta - Simulación por jobs/lentes y WIP dinámico por área (2025)")
    st.sidebar.header("Visualización")
    ver_en = st.sidebar.radio("¿Visualizar en?", ["Jobs (pares de lentes)", "Lentes"])
    
    # Datos de forecast en JOBS (pares) para 2025
    fechas = [
        "24-nov-2025","25-nov-2025","26-nov-2025","27-nov-2025","28-nov-2025","29-nov-2025","30-nov-2025","01-dic-2025","02-dic-2025","03-dic-2025","04-dic-2025","05-dic-2025","06-dic-2025","07-dic-2025",
        "08-dic-2025","09-dic-2025","10-dic-2025","11-dic-2025","12-dic-2025","13-dic-2025","14-dic-2025","15-dic-2025","16-dic-2025","17-dic-2025","18-dic-2025","19-dic-2025","20-dic-2025",
        "21-dic-2025","22-dic-2025","23-dic-2025","24-dic-2025","25-dic-2025","26-dic-2025","27-dic-2025","28-dic-2025"
    ]
    entradas_jobs = [
        677, 642, 600, 572, 602, 738, 246, 1459, 1383, 1293, 1233, 1297, 1592, 530, 730, 692, 647, 617, 649, 796, 265, 686,
        650, 607, 579, 609, 748, 249, 498, 471, 441, 421, 442, 543, 181
    ]
    entradas_lentes = [x*2 for x in entradas_jobs]
    if ver_en == "Jobs (pares de lentes)":
        entradas = entradas_jobs
        unidades = "Jobs (pares)"
    else:
        entradas = entradas_lentes
        unidades = "Lentes"
    
    st.sidebar.header("Split de flujos después de SURF (total debe sumar 100%)")
    pct_surf_ar_no_montaje = st.sidebar.slider("% de SURF → AR (NO pasa a Montaje)", 0, 100, 2, key="ta_pct_ar_no_montaje")
    pct_surf_ar_montaje = st.sidebar.slider("% de SURF → AR y luego a Montaje", 0, 100, 90, key="ta_pct_ar_montaje")
    pct_surf_montaje_no_ar = 100 - pct_surf_ar_no_montaje - pct_surf_ar_montaje
    st.sidebar.markdown(f"**% de SURF → Montaje (sin AR):** {pct_surf_montaje_no_ar}%")
    pct_surf_ar_no_montaje /= 100
    pct_surf_ar_montaje /= 100
    pct_surf_montaje_no_ar /= 100

    st.sidebar.header("Capacidad y turnos por área (por turno)")
    st.sidebar.subheader("SURF")
    capacidad_surf = st.sidebar.number_input(f"Capacidad base SURF ({unidades}/turno)", min_value=1, value=952 if unidades=="Lentes" else 476, key="ta_csurf")
    turnos_surf = st.sidebar.number_input("Turnos SURF (L-V, Sáb)", 1, 4, 3, key="ta_turnos_surf")
    turnos_surf_dom = st.sidebar.number_input("Turnos SURF (Domingo)", 0, 4, 1, key="ta_turnos_surf_dom")
    wip_inicial_surf = st.sidebar.number_input(f"WIP inicial SURF ({unidades})", min_value=0, value=0, key="wip_ini_surf")

    st.sidebar.subheader("AR")
    capacidad_ar = st.sidebar.number_input(f"Capacidad base AR ({unidades}/turno)", min_value=1, value=560 if unidades=="Lentes" else 280, key="ta_car")
    turnos_ar = st.sidebar.number_input("Turnos AR (L-V, Sáb)", 1, 4, 3, key="ta_turnos_ar")
    turnos_ar_dom = st.sidebar.number_input("Turnos AR (Domingo)", 0, 4, 1, key="ta_turnos_ar_dom")
    wip_inicial_ar = st.sidebar.number_input(f"WIP inicial AR ({unidades})", min_value=0, value=0, key="wip_ini_ar")

    st.sidebar.subheader("Montaje (E&M)")
    capacidad_em = st.sidebar.number_input(f"Capacidad base Montaje ({unidades}/turno)", min_value=1, value=1071 if unidades=="Lentes" else 536, key="ta_cem")
    turnos_em = st.sidebar.number_input("Turnos Montaje (L-V, Sáb)", 1, 4, 3, key="ta_turnos_em")
    turnos_em_dom = st.sidebar.number_input("Turnos Montaje (Domingo)", 0, 4, 1, key="ta_turnos_em_dom")
    wip_inicial_em = st.sidebar.number_input(f"WIP inicial Montaje ({unidades})", min_value=0, value=1100 if unidades=="Jobs (pares de lentes)" else 2200, key="ta_wip_inicial_em")

    # Mes en español a inglés para parsear fechas
    MES_MAP = {
        "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr", "may": "May", "jun": "Jun",
        "jul": "Jul", "ago": "Aug", "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec"
    }
    def fecha_a_dt(fecha):
        dia, mes, año = fecha.split('-')
        mes_en = MES_MAP[mes.lower()]
        return datetime.datetime.strptime(f"{dia}-{mes_en}-{año}", "%d-%b-%Y")

    df = pd.DataFrame({
        "Fecha": fechas,
        "Entrada_total": entradas
    })
    df["Es_domingo"] = [fecha_a_dt(f).weekday()==6 for f in fechas]
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
    df["Lente_surf_ar_no_montaje"] = df["Lente_surf"] * pct_surf_ar_no_montaje
    df["Lente_surf_ar_montaje"] = df["Lente_surf"] * pct_surf_ar_montaje
    df["Lente_surf_montaje_no_ar"] = df["Lente_surf"] * pct_surf_montaje_no_ar

    # WIP dinámico por área

    # SURF
    wip_surf = []
    wip_actual_surf = wip_inicial_surf
    salidas_surf = []
    for i in range(len(df)):
        entrada_surf = df.loc[i, "Lente_surf"]
        salida_surf = min(wip_actual_surf + entrada_surf, df.loc[i, "Capacidad_SURF"])
        salidas_surf.append(salida_surf)
        wip_actual_surf = wip_actual_surf + entrada_surf - salida_surf
        if wip_actual_surf < 0:
            wip_actual_surf = 0
        wip_surf.append(wip_actual_surf)
    df["Salida_SURF"] = salidas_surf
    df["WIP_SURF"] = wip_surf

    # AR (suma los dos flujos que pasan por AR)
    entradas_ar = df["Lente_surf_ar_no_montaje"] + df["Lente_surf_ar_montaje"]
    wip_ar = []
    wip_actual_ar = wip_inicial_ar
    salidas_ar = []
    for i in range(len(df)):
        entrada_ar = entradas_ar[i]
        salida_ar = min(wip_actual_ar + entrada_ar, df.loc[i, "Capacidad_AR"])
        salidas_ar.append(salida_ar)
        wip_actual_ar = wip_actual_ar + entrada_ar - salida_ar
        if wip_actual_ar < 0:
            wip_actual_ar = 0
        wip_ar.append(wip_actual_ar)
    df["Entrada_AR"] = entradas_ar
    df["Salida_AR"] = salidas_ar
    df["WIP_AR"] = wip_ar

    # Montaje (suma los 3 flujos que llegan a Montaje)
    ratio_ar_montaje = df["Lente_surf_ar_montaje"] / (df["Lente_surf_ar_montaje"] + df["Lente_surf_ar_no_montaje"])
    ratio_ar_montaje = ratio_ar_montaje.fillna(0)
    df["Entradas_montaje"] = df["Lente_terminado"] + df["Salida_AR"] * ratio_ar_montaje + df["Lente_surf_montaje_no_ar"]

    wip_em = []
    wip_actual_em = wip_inicial_em
    salidas_em = []
    for i in range(len(df)):
        entrada_em = df.loc[i, "Entradas_montaje"]
        salida_em = min(wip_actual_em + entrada_em, df.loc[i, "Capacidad_EM"])
        salidas_em.append(salida_em)
        wip_actual_em = wip_actual_em + entrada_em - salida_em
        if wip_actual_em < 0:
            wip_actual_em = 0
        wip_em.append(wip_actual_em)
    df["Salida_EM"] = salidas_em
    df["WIP_EM"] = wip_em

    st.markdown(f"""
    **Supuestos**:  
    - Forecast de entradas está en {unidades}, fechas para 2025.
    - Puedes ajustar la capacidad diaria y el WIP inicial de cada área.
    - Split parametrizable.
    - WIP de cada área se simula dinámicamente:  
      WIP_día = WIP_día-1 + entradas_día - salidas_día (limitadas por capacidad y turnos)
    """)

    st.subheader(f"Simulación y acumulación de WIP por área ({unidades})")
    st.dataframe(df, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_SURF"], name="WIP SURF", mode="lines+markers", line=dict(color="red", width=3)))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_AR"], name="WIP AR", mode="lines+markers", line=dict(color="blue", width=3)))
    fig.add_trace(go.Scatter(x=df["Fecha"], y=df["WIP_EM"], name="WIP Montaje", mode="lines+markers", line=dict(color="purple", width=3)))
    fig.update_layout(
        title=f"WIP dinámico día a día por área ({unidades})",
        xaxis_title="Fecha",
        yaxis_title=unidades,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"🔴 WIP inicial SURF: {wip_inicial_surf} {unidades}")
    st.info(f"🔵 WIP inicial AR: {wip_inicial_ar} {unidades}")
    st.info(f"🟣 WIP inicial Montaje: {wip_inicial_em} {unidades}")
    st.info(f"🔴 WIP final SURF: {int(df['WIP_SURF'].iloc[-1])} {unidades}")
    st.info(f"🔵 WIP final AR: {int(df['WIP_AR'].iloc[-1])} {unidades}")
    st.info(f"🟣 WIP final Montaje: {int(df['WIP_EM'].iloc[-1])} {unidades}")

    st.markdown(f"""
    **Revisa cómo el WIP baja y se estabiliza en base a forecast, splits y capacidad/turnos por área.**  
    Puedes ajustar todos los parámetros para simular distintos escenarios.
    """)
