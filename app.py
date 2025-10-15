import streamlit as st
import plotly.graph_objs as go
import numpy as np
import time

st.set_page_config(page_title="🚀 Dashboard de Capacidad Integral", layout="wide")
st.markdown("""
<style>
h1, h2, h3, h4 { color: #003366; }
.big-metric { font-size: 2em; font-weight: bold; color: #1f77b4;}
.metric-info { font-size: 1.2em; color: #222; }
hr { border: 1px solid #003366;}
</style>
""", unsafe_allow_html=True)

# ---- Tabs para toda la experiencia ----
tabs = st.tabs([
    "Capacidad SURF", 
    "Capacidad E&M", 
    "Simulación 3D + IA (WOW)"
])

# --------- TAB 1: Capacidad SURF ---------
with tabs[0]:
    st.title("🚀 Dashboard - Capacidad Línea de Superficies")
    st.info("Aquí va tu dashboard SURF completo (usa tu código profesional previo aquí)")
    # Puedes copiar aquí tu código previo de SURF

# --------- TAB 2: Capacidad E&M ---------
with tabs[1]:
    st.title("🏭 Dashboard - Capacidad Ensamble y Montaje (E&M)")
    st.info("Aquí va tu dashboard E&M completo (usa tu código profesional previo aquí)")
    # Puedes copiar aquí tu código previo de E&M

# --------- TAB 3: Simulador 3D con IA ---------
with tabs[2]:
    st.title("🤖🌐 Simulador 3D Interactivo con IA Industrial")

    st.markdown("""
    Visualiza el flujo de lotes en 3D, identifica cuellos de botella y recibe recomendaciones inteligentes en tiempo real.
    """)
    
    # Parámetros de simulación (puedes conectarlos a los valores actuales del dashboard)
    lote_size = st.number_input("Tamaño de lote (lentes)", min_value=1, value=20)
    velocidad = st.slider("Velocidad de simulación (segundos/estación)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
    pct_standard = st.slider("Porcentaje de trabajos Standard (%)", min_value=0, max_value=100, value=27)
    pct_free = 100 - pct_standard

    stations_full = [
        {"name": "Encintado", "icon": "🟦", "color": "#1f3b6f", "coord": [0, 0, 0]},
        {"name": "Bloqueo Digital", "icon": "🟩", "color": "#27ae60", "coord": [1, 0, 0]},
        {"name": "Generado Digital", "icon": "🟫", "color": "#8d6748", "coord": [2, 0.5, 0]},
        {"name": "Laser", "icon": "🟨", "color": "#f7e017", "coord": [3, 1.5, 0]}, # Solo Free
        {"name": "Pulido", "icon": "🟪", "color": "#7d3fc7", "coord": [4, 1, 0]},
        {"name": "Desbloqueo", "icon": "⬛", "color": "#222222", "coord": [5, 0.5, 0]},
        {"name": "Calidad", "icon": "⬜", "color": "#eaeaea", "coord": [6, 0, 0]}
    ]

    stations_standard = [s for s in stations_full if s["name"] != "Laser"]
    coords_standard = np.array([s["coord"] for s in stations_standard])
    labels_standard = [s["name"] for s in stations_standard]
    icons_standard = [s["icon"] for s in stations_standard]
    colors_standard = [s["color"] for s in stations_standard]

    stations_free = stations_full
    coords_free = np.array([s["coord"] for s in stations_free])
    labels_free = [s["name"] for s in stations_free]
    icons_free = [s["icon"] for s in stations_free]
    colors_free = [s["color"] for s in stations_free]

    run_sim = st.button("Simular flujo 3D con IA")

    def ia_bottleneck(stations, tipo):
        # "IA": usa datos aleatorios como demo, aquí conectas tu modelo real de IA si tienes datos históricos
        capacidades = np.random.randint(60, 200, len(stations))
        idx = np.argmin(capacidades)
        return stations[idx]["name"], capacidades[idx], capacidades

    if run_sim:
        st.subheader("🔵 Flujo STANDARD (no pasa por Laser)")
        bottle_std, cap_std, caps_std = ia_bottleneck(stations_standard, "Standard")
        st.info(f"🧠 IA: Bottleneck Standard: {bottle_std} ({cap_std} lentes/hora aprox.)")

        for paso in range(len(stations_standard)):
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=coords_standard[:,0], y=coords_standard[:,1], z=coords_standard[:,2],
                mode="markers+text",
                marker=dict(
                    size=[30 if i==paso else 18 for i in range(len(stations_standard))],
                    color=["red" if i==paso or stations_standard[i]["name"]==bottle_std else colors_standard[i] for i in range(len(stations_standard))],
                    opacity=[0.9 if i==paso else 0.5 for i in range(len(stations_standard))]
                ),
                text=[f"{icons_standard[i]}<br>{labels_standard[i]}<br>{caps_std[i]} l/h" for i in range(len(stations_standard))],
                textposition="bottom center"
            ))
            if paso > 0:
                fig.add_trace(go.Scatter3d(
                    x=coords_standard[:paso+1,0], y=coords_standard[:paso+1,1], z=coords_standard[:paso+1,2],
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
                title=f"Lote Standard en {labels_standard[paso]}",
                showlegend=False,
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)
            time.sleep(velocidad)

        st.success(f"Simulación terminada para Standard ({pct_standard}% del total)")

        st.subheader("🟡 Flujo FREE/DIGITAL (pasa por Laser)")
        bottle_free, cap_free, caps_free = ia_bottleneck(stations_free, "Free")
        st.info(f"🧠 IA: Bottleneck Free: {bottle_free} ({cap_free} lentes/hora aprox.)")

        for paso in range(len(stations_free)):
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=coords_free[:,0], y=coords_free[:,1], z=coords_free[:,2],
                mode="markers+text",
                marker=dict(
                    size=[30 if i==paso else 18 for i in range(len(stations_free))],
                    color=["blue" if i==paso or stations_free[i]["name"]==bottle_free else colors_free[i] for i in range(len(stations_free))],
                    opacity=[0.9 if i==paso else 0.5 for i in range(len(stations_free))]
                ),
                text=[f"{icons_free[i]}<br>{labels_free[i]}<br>{caps_free[i]} l/h" for i in range(len(stations_free))],
                textposition="bottom center"
            ))
            if paso > 0:
                fig.add_trace(go.Scatter3d(
                    x=coords_free[:paso+1,0], y=coords_free[:paso+1,1], z=coords_free[:paso+1,2],
                    mode="lines",
                    line=dict(color="blue", width=8)
                ))
            fig.update_layout(
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False),
                ),
                title=f"Lote Free en {labels_free[paso]}",
                showlegend=False,
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)
            time.sleep(velocidad)

        st.success(f"Simulación terminada para Free ({pct_free}% del total)")

        # "IA" recomienda acciones (puede ser real ML en producción)
        st.markdown("## 💡 Recomendaciones Inteligentes")
        if cap_std < cap_free:
            st.info(f"💡 **Sugerencia IA:** Refuerza la estación '{bottle_std}' (Standard) para mejorar el throughput global.")
        else:
            st.info(f"💡 **Sugerencia IA:** Refuerza la estación '{bottle_free}' (Free) y revisa el flujo Free para maximizar eficiencia.")

    st.markdown("""
    <div style="text-align:center;">
        <span style="font-size:2em;">🤖</span>
        <br>
        <span style="font-size:1em;">Simulación 3D con IA generativa y análisis de cuellos de botella - ¡Impacto industrial asegurado!</span>
    </div>
    """, unsafe_allow_html=True)
