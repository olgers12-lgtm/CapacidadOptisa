import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import datetime

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")

# --- 1. Sidebar selector de proceso ---
proceso = st.sidebar.radio(
    "Selecciona el dashboard:",
    ["Capacidad SURF", "Capacidad E&M", "Temporada Alta"]
)

# --- 2. Sidebar dinámico ---
stations = []
stations_em = []
line_oee = num_turnos = horas_turno = scrap_rate = None

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

elif proceso == "Temporada Alta":
    prefix = "TA_"
    st.sidebar.header("Capacidad base y OEE")
    # SURF
    capacidad_surf_h = st.sidebar.number_input("Capacidad base SURF (lentes/hora)", min_value=10, value=150, key=prefix+"surf_h")
    oee_surf = st.sidebar.slider("OEE SURF", min_value=0.5, max_value=1.0, value=0.85, step=0.01, key=prefix+"oee_surf")
    # AR
    capacidad_ar_h = st.sidebar.number_input("Capacidad base AR (lentes/hora)", min_value=10, value=140, key=prefix+"ar_h")
    oee_ar = st.sidebar.slider("OEE AR", min_value=0.5, max_value=1.0, value=0.85, step=0.01, key=prefix+"oee_ar")
    # E&M
    capacidad_em_h = st.sidebar.number_input("Capacidad base Montaje (lentes/hora)", min_value=10, value=180, key=prefix+"em_h")
    oee_em = st.sidebar.slider("OEE Montaje", min_value=0.5, max_value=1.0, value=0.85, step=0.01, key=prefix+"oee_em")

    st.sidebar.markdown("---")
    st.sidebar.header("Turnos y horas por día (no domingo)")
    turnos_surf = st.sidebar.number_input("Turnos SURF", 1, 4, 3, key=prefix+"turnos_surf") 
    horas_surf = st.sidebar.number_input("Horas por turno SURF", 4, 12, 8, key=prefix+"horas_surf")
    turnos_ar = st.sidebar.number_input("Turnos AR", 1, 4, 3, key=prefix+"turnos_ar")
    horas_ar = st.sidebar.number_input("Horas por turno AR", 4, 12, 8, key=prefix+"horas_ar")
    turnos_em = st.sidebar.number_input("Turnos Montaje", 1, 4, 3, key=prefix+"turnos_em")
    horas_em = st.sidebar.number_input("Horas por turno Montaje", 4, 12, 8, key=prefix+"horas_em")

    st.sidebar.markdown("---")
    st.sidebar.header("Turnos y horas para DOMINGO")
    turnos_dom_surf = st.sidebar.number_input("Turnos SURF (domingo)", 0, 4, 1, key=prefix+"turnos_dom_surf")
    horas_dom_surf = st.sidebar.number_input("Horas por turno SURF (domingo)", 0, 12, 6, key=prefix+"horas_dom_surf")
    turnos_dom_ar = st.sidebar.number_input("Turnos AR (domingo)", 0, 4, 1, key=prefix+"turnos_dom_ar")
    horas_dom_ar = st.sidebar.number_input("Horas por turno AR (domingo)", 0, 12, 6, key=prefix+"horas_dom_ar")
    turnos_dom_em = st.sidebar.number_input("Turnos Montaje (domingo)", 0, 4, 1, key=prefix+"turnos_dom_em")
    horas_dom_em = st.sidebar.number_input("Horas por turno Montaje (domingo)", 0, 12, 6, key=prefix+"horas_dom_em")

    st.sidebar.markdown("---")
    st.sidebar.header("Split de flujos después de SURF")
    pct_ar = st.sidebar.slider("% de trabajos de SURF que van a AR", min_value=0, max_value=100, value=80, step=1, key=prefix+"pct_ar")
    pct_sin_ar = 100 - pct_ar

if proceso == "Temporada Alta":
    st.title("🔝 Temporada Alta - Capacidad, AR y WIP con Turnos/Horas variables")
    fechas = [
        "24-nov","25-nov","26-nov","27-nov","28-nov","29-nov","30-nov","1-dic","2-dic","3-dic","4-dic","5-dic","6-dic","7-dic",
        "8-dic","9-dic","10-dic","11-dic","12-dic","13-dic","14-dic","15-dic","16-dic","17-dic","18-dic","19-dic","20-dic",
        "21-dic","22-dic","23-dic","24-dic","25-dic","26-dic","27-dic","28-dic"
    ]
    entradas = [
        677, 642, 600, 572, 602, 738, 246, 1459, 1383, 1293, 1233, 1297, 1592, 530, 730, 692, 647, 617, 649, 796, 265, 686,
        650, 607, 579, 609, 748, 249, 498, 471, 441, 421, 442, 543, 181
    ]
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

    def capacidad_diaria(is_dom, base_h, oee, turnos, horas, turnos_dom, horas_dom):
        if is_dom:
            return base_h * oee * turnos_dom * horas_dom
        else:
            return base_h * oee * turnos * horas

    df["Capacidad_SURF"] = [
        capacidad_diaria(row["Es_domingo"], capacidad_surf_h, oee_surf, turnos_surf, horas_surf, turnos_dom_surf, horas_dom_surf)
        for idx, row in df.iterrows()
    ]
    df["Capacidad_AR"] = [
        capacidad_diaria(row["Es_domingo"], capacidad_ar_h, oee_ar, turnos_ar, horas_ar, turnos_dom_ar, horas_dom_ar)
        for idx, row in df.iterrows()
    ]
    df["Capacidad_EM"] = [
        capacidad_diaria(row["Es_domingo"], capacidad_em_h, oee_em, turnos_em, horas_em, turnos_dom_em, horas_dom_em)
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
    - Puedes ajustar los turnos, horas, OEE y split, y la simulación se actualiza.  
    - Los domingos puedes poner menos turnos/horas o incluso cero para simular paros.
    """)

    st.subheader("Entradas y acumulación de WIP en Temporada Alta (con AR y turnos/horas variables)")
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
        st.warning("⚠️ Para evitar acumulación de WIP, considera aumentar capacidad diaria, turnos, horas o recursos en los procesos cuello de botella durante la temporada alta.")
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
    st.write(f"🔸 Para cubrir el pico en SURF necesitas al menos **{int(np.ceil(demanda_max_surf/df['Capacidad_SURF'].max()))} veces la capacidad diaria máxima configurada**")
    st.write(f"🔸 Para cubrir el pico en AR necesitas al menos **{int(np.ceil(demanda_max_ar/df['Capacidad_AR'].max()))} veces la capacidad diaria máxima configurada**")
    st.write(f"🔸 Para cubrir el pico en Montaje necesitas al menos **{int(np.ceil(demanda_max_em/df['Capacidad_EM'].max()))} veces la capacidad diaria máxima configurada**")
