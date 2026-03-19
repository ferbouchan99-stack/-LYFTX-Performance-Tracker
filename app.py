import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX Performance", layout="wide")

# CSS para evitar movimientos raros y mantener estética LYFTX
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    [data-testid="stMetricValue"] { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

# Configuración de Músculos y Rangos (Basado en tu tabla de Revive Stronger)
# MV: Mantenimiento, MEV: Mínimo Efectivo, MAV: Máximo Adaptativo, MRV: Máximo Recuperable
musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg", "Reps Objetivo", "Reps Logradas"]) for dia in dias}

# --- REGISTRO DIARIO (DISEÑO VERTICAL) ---
for dia in dias:
    with st.expander(f"📅 {dia}", expanded=(dia == "Lunes")):
        df_editado = st.data_editor(
            st.session_state.db[dia],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key=f"editor_{dia}",
            column_config={
                "Músculo": st.column_config.SelectboxColumn(options=musculos, required=True),
                "Series": st.column_config.NumberColumn(min_value=0, step=1, default=0),
                "Kg": st.column_config.TextColumn("Kg (ej: 20-20-15)"),
                "Reps Objetivo": st.column_config.TextColumn("Plan (ej: 10-12)"),
                "Reps Logradas": st.column_config.TextColumn("Logro (ej: 12-11-10)")
            }
        )
        st.session_state.db[dia] = df_editado

# --- PROCESAMIENTO DE VOLUMEN ---
df_total = pd.concat(st.session_state.db.values())
volumen = {m: 0.0 for m in musculos}

if not df_total.empty:
    for _, row in df_total.iterrows():
        m = str(row["Músculo"])
        s = pd.to_numeric(row["Series"], errors='coerce') or 0
        if m in volumen:
            volumen[m] += s
            # Biomecánica básica (Suma indirecta)
            if m == "Pecho": volumen["Tríceps"] += (s * 0.5); volumen["Deltoide frontal"] += (s * 0.5)
            elif m == "Espalda": volumen["Bíceps"] += (s * 0.5); volumen["Deltoide posterior"] += (s * 0.5)

# --- GRÁFICA CON SEMÁFORO DE INTENSIDAD ---
st.divider()
st.header("📊 VOLUMEN SEMANAL ACUMULADO")

def get_color(m, v):
    # Lógica simplificada basada en tu imagen de rangos
    if v == 0: return "#E0E0E0" # Gris (Sin datos)
    if v < 6: return "#4CAF50"  # Verde (MV - Mantenimiento)
    if v <= 12: return "#FFEB3B" # Amarillo (MEV - Mínimo Efectivo)
    if v <= 20: return "#FF9800" # Naranja (MAV - Máximo Adaptativo)
    return "#F44336"            # Rojo (MRV - Riesgo de Sobreentrenamiento)

colores_barras = [get_color(m, volumen[m]) for m in musculos]

fig = go.Figure(go.Bar(
    x=musculos,
    y=[volumen[m] for m in musculos],
    marker_color=colores_barras,
    text=[volumen[m] for m in musculos],
    textposition='auto',
))

fig.update_layout(
    template="plotly_white",
    height=500,
    xaxis={'tickangle': -45},
    yaxis_title="Series Totales",
    margin=dict(b=100)
)

st.plotly_chart(fig, use_container_width=True)

# Leyenda de Colores
st.markdown("""
<div style="display: flex; justify-content: space-around; font-size: 0.8em; border: 1px solid #ddd; padding: 10px;">
    <span>🟢 <b>MV</b> (Mantenimiento)</span>
    <span>🟡 <b>MEV</b> (Mínimo Efectivo)</span>
    <span>🟠 <b>MAV</b> (Máximo Adaptativo)</span>
    <span>🔴 <b>MRV</b> (Sobreentrenamiento)</span>
</div>
""", unsafe_allow_html=True)


