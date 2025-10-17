import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")
st.markdown("""
<style>
h1, h2, h3, h4 { color: #003366; }
.big-metric { font-size: 2em; font-weight: bold; color: #1f77b4;}
.metric-info { font-size: 1.2em; color: #222; }
hr { border: 1px solid #003366;}
</style>
""", unsafe_allow_html=True)

# --------- TABS/TOP BUTTONS ---------
colA, colB = st.columns(2)
with colA:
    st.image("https://cdn-icons-png.flaticon.com/512/3103/3103474.png", width=70)
with colB:
    st.markdown("<h1 style='margin-top:10px;'>Dashboard de Capacidad Integral</h1>", unsafe_allow_html=True)

tab = st.radio(
    "Selecciona el proceso:", 
    options=["SURF (Superficies)", "E&M (Ensamble y Montaje)", "WIP Temporada Alta"], 
    horizontal=True
)

if tab == "SURF (Superficies)":
    st.markdown("---")
    st.markdown("## 🚀 Superficies - Capacidad, Bottleneck y Simulación Industrial")

    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas (SURF)")
    default_stations = [
        {
            "name": "Encintado",
            "icon": "🟦",
            "color": "#1f3b6f",
            "machines": [
                {"type": "Encintadora Automática", "count": 1, "capacity": 150.0},
                {"type": "Encintado Manual", "count": 1, "capacity": 0.0}
            ]
        },
        {
            "name": "Bloqueo Digital",
            "icon": "🟩",
            "color": "#27ae60",
            "machines": [
                {"type": "PRA", "count": 3, "capacity": 80.0}
            ]
        },
        {
            "name": "Generado Digital",
            "icon": "🟫",
            "color": "#8d6748",
            "machines": [
                {"type": "Orbit", "count": 3, "capacity": 77.0}
            ]
        },
        {
            "name": "Laser",
            "icon": "🟨",
            "color": "#f7e017",
            "machines": [
                {"type": "Automático", "count": 1, "capacity": 100.0},
                {"type": "Manual", "count": 1, "capacity": 110.0}
            ]
        },
        {
            "name": "Pulido",
            "icon": "🟪",
            "color": "#7d3fc7",
            "machines": [
                {"type": "Duo Flex", "count": 2, "capacity": 30.0},
                {"type": "DLP", "count": 6, "capacity": 27.0}
            ]
        },
        {
            "name": "Desbloqueo",
            "icon": "⬛",
            "color": "#222222",
            "machines": [
                {"type": "Manual", "count": 1, "capacity": 423.53},
                {"type": "Desblocker", "count": 1, "capacity": 360.0}
            ]
        },
        {
            "name": "Calidad",
            "icon": "⬜",
            "color": "#eaeaea",
            "machines": [
                {"type": "Foco Vision", "count": 1, "capacity": 60.0},
                {"type": "Promapper", "count": 1, "capacity": 110.0}
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

elif tab == "E&M (Ensamble y Montaje)":
    st.markdown("---")
    st.markdown("## 🏭 Ensamble y Montaje - Capacidad, Bottleneck y Simulación Industrial")

    st.sidebar.header("🔧 Configuración de Estaciones y Máquinas E&M")
    default_stations_em = [
        {
            "name": "Anaquel",
            "icon": "🔲",
            "color": "#8e44ad",
            "machines": [
                {"type": "Manual", "count": 1, "capacity": 12*60.0}
            ]
        },
        {
            "name": "Bloqueo",
            "icon": "🟦",
            "color": "#2980b9",
            "machines": [
                {"type": "Manual", "count": 1, "capacity": 10*60.0}
            ]
        },
        {
            "name": "Corte",
            "icon": "✂️",
            "color": "#27ae60",
            "machines": [
                {"type": "Bisphera", "count": 1, "capacity": 109.0},
                {"type": "ES4", "count": 2, "capacity": 34.0},
                {"type": "MEI641", "count": 1, "capacity": 74.0}
            ]
        },
        {
            "name": "Remate",
            "icon": "🟨",
            "color": "#f4d03f",
            "machines": [
                {"type": "Manual", "count": 1, "capacity": 60.0}
            ]
        }
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

elif tab == "WIP Temporada Alta":
    st.markdown("---")
    st.markdown("## 📈 Análisis WIP, Entradas y Salidas - Temporada Alta")

    # 1. Lee el Excel de Google Sheets transpuesto
    sheet_url = "https://docs.google.com/spreadsheets/d/1kMt2eSweVawnCURnRki0na99uLxQn-yLg_zI2IZwpwY/export?format=xlsx"
    df_raw = pd.read_excel(sheet_url, header=None)
    st.write("Vista previa de datos (10 filas):", df_raw.head(10))

    # 2. Permite elegir la fila de encabezados
    fila_encabezados = st.number_input(
        "¿En qué fila están los nombres de las columnas? (0-index)", min_value=0,
        max_value=len(df_raw)-1, value=10
    )
    df = df_raw.copy()
    df.columns = df.iloc[fila_encabezados]
    df = df.drop(index=range(fila_encabezados + 1)).reset_index(drop=True)
    st.write("Nombres de columnas detectados:", df.columns.tolist())
    st.write("Vista previa de datos limpios:", df.head(10))

    # 3. Permite elegir la columna de tipo de dato (Entradas/Salidas/WIP)
    columna_tipo = st.selectbox("Selecciona la columna que contiene el tipo de dato (Ej: Entradas, Salidas, WIP)", df.columns)
    columnas_fechas = [c for c in df.columns if c != columna_tipo and pd.notna(c)]

    # 4. Derrite el DataFrame (convierte columnas de fechas en filas)
    df_melted = df.melt(id_vars=[columna_tipo], value_vars=columnas_fechas,
                        var_name="Fecha", value_name="Valor")
    df_melted = df_melted.rename(columns={columna_tipo: "Tipo"})
    # Limpia fechas y valores
    def parse_fecha(f):
        try:
            return pd.to_datetime(f + "-2024", format="%d-%b-%Y")
        except:
            try:
                return pd.to_datetime(f, dayfirst=True)
            except:
                return pd.NaT
    df_melted["Fecha"] = df_melted["Fecha"].apply(parse_fecha)
    df_melted["Valor"] = pd.to_numeric(df_melted["Valor"], errors="coerce")
    df_melted = df_melted.dropna(subset=["Fecha", "Valor", "Tipo"])

    st.write("Vista previa tabla normalizada:", df_melted.head(10))

    # 5. Filtros
    tipos_disponibles = df_melted["Tipo"].unique().tolist()
    tipos_seleccionados = st.multiselect("Selecciona los tipos a analizar", tipos_disponibles, default=tipos_disponibles)
    df_melted = df_melted[df_melted["Tipo"].isin(tipos_seleccionados)]

    fecha_min = df_melted["Fecha"].min().date()
    fecha_max = df_melted["Fecha"].max().date()
    rango_fechas = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max], min_value=fecha_min, max_value=fecha_max)
    df_melted = df_melted[(df_melted["Fecha"].dt.date >= rango_fechas[0]) & (df_melted["Fecha"].dt.date <= rango_fechas[1])]

    # 6. Pivot para gráfico
    df_pivot = df_melted.pivot(index="Fecha", columns="Tipo", values="Valor").sort_index()

    # 7. KPIs
    st.title("📈 Dashboard WIP - Temporada Alta")
    col1, col2, col3, col4 = st.columns(4)
    if "WIP" in df_pivot:
        col1.metric("WIP Máximo", int(df_pivot["WIP"].max()))
        col2.metric("WIP Mínimo", int(df_pivot["WIP"].min()))
    if "Entradas" in df_pivot:
        col3.metric("Entradas totales", int(df_pivot["Entradas"].sum()))
    if "Salidas" in df_pivot:
        col4.metric("Salidas totales", int(df_pivot["Salidas"].sum()))

    # 8. Gráfico
    st.subheader("Evolución de Entradas, Salidas y WIP")
    fig = go.Figure()
    if "WIP" in df_pivot:
        fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["WIP"], name="WIP", mode="lines+markers", line=dict(width=3, color="#1f77b4")))
    if "Entradas" in df_pivot:
        fig.add_trace(go.Bar(x=df_pivot.index, y=df_pivot["Entradas"], name="Entradas", marker=dict(color="#2ca02c"), opacity=0.6))
    if "Salidas" in df_pivot:
        fig.add_trace(go.Bar(x=df_pivot.index, y=df_pivot["Salidas"], name="Salidas", marker=dict(color="#d62728"), opacity=0.6))
    fig.update_layout(barmode='overlay', xaxis_title="Fecha", yaxis_title="Cantidad", legend_title="Variable", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 9. Tabla y KPIs avanzados
    with st.expander("🔎 Ver datos filtrados"):
        st.dataframe(df_pivot, use_container_width=True)

    st.subheader("KPIs Avanzados")
    if "WIP" in df_pivot:
        st.write(f"Promedio diario de WIP: **{df_pivot['WIP'].mean():.1f}**")
        st.write(f"Día con mayor WIP: **{df_pivot['WIP'].idxmax().date()}**")
    if "Entradas" in df_pivot:
        st.write(f"Día con mayor entradas: **{df_pivot['Entradas'].idxmax().date()}**")
    if "Salidas" in df_pivot:
        st.write(f"Día con mayor salidas: **{df_pivot['Salidas'].idxmax().date()}**")

    st.download_button("Descargar datos filtrados (CSV)", data=df_pivot.reset_index().to_csv(index=False).encode("utf-8"), file_name="WIP_analisis_temporada_alta.csv", mime="text/csv")
