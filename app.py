import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de página minimalista
st.set_page_config(page_title="LYFTX Performance", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stExpander { border: 1px solid #000000 !important; border-radius: 0px !important; margin-bottom: 5px; }
    /* Ocultar columna de índice */
    [data-testid="stTable"] th:first-child, [data-testid="stTable"] td:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Inicialización de estado de sesión
if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg"]) for dia in dias}

# --- SECCIÓN DE ENTRADA ---
for dia in dias:
    with st.expander(dia):
        # hide_index=True para eliminar la columna innecesaria
        edited_df = st.data_editor(
            st.session_state.db[dia],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key=f"editor_{dia}",
            column_config={
                "Músculo": st.column_config.SelectboxColumn(options=musculos, required=True),
                "Series": st.column_config.NumberColumn(min_value=0, step=1, default=0),
                "Kg": st.column_config.TextColumn("Kg")
            }
        )
        st.session_state.db[dia] = edited_df

# --- MOTOR DE CÁLCULO DE ALTA PRECISIÓN ---
# Reiniciamos conteo en cada ejecución para evitar duplicados o errores de caché
conteo_volumen = {m: 0.0 for m in musculos}

for dia in dias:
    df_actual = st.session_state.db[dia]
    if not df_actual.empty:
        # Iteración directa sobre los valores para asegurar que nada se escape
        for m_row, s_row in zip(df_actual["Músculo"], df_actual["Series"]):
            if pd.notna(m_row) and m_row in musculos:
                try:
                    val_series = float(s_row) if s_row else 0.0
                except:
                    val_series = 0.0
                
                conteo_volumen[m_row] += val_series
                
                # Biomecánica de apoyo (Suma indirecta)
                if m_row == "Pecho":
                    conteo_volumen["Tríceps"] += (val_series * 0.5)
                    conteo_volumen["Deltoide frontal"] += (val_series * 0.5)
                elif m_row == "Espalda":
                    conteo_volumen["Bíceps"] += (val_series * 0.5)
                    conteo_volumen["Deltoide posterior"] += (val_series * 0.5)
                elif m_row == "Cuádriceps":
                    conteo_volumen["Glúteos"] += (val_series * 0.3)
                elif m_row == "Isquios":
                    conteo_volumen["Glúteos"] += (val_series * 0.5)

# --- VISUALIZACIÓN ---
st.divider()
st.header("VOLUMEN SEMANAL ACUMULADO")

def definir_color(v):
    if v == 0: return "#E0E0E0"  # Gris (Vacío)
    if v <= 6: return "#00FF00"  # Verde (MV)
    if v <= 12: return "#FFFF00" # Amarillo (MEV) - Corregido de dorado a amarillo puro
    if v <= 20: return "#FFA500" # Naranja (MAV)
    return "#FF0000"            # Rojo (MRV)

colores_dinamicos = [definir_color(conteo_volumen[m]) for m in musculos]

fig = go.Figure(go.Bar(
    x=musculos,
    y=[conteo_volumen[m] for m in musculos],
    marker_color=colores_dinamicos,
    text=[round(conteo_volumen[m], 1) for m in musculos],
    textposition='outside',
))

fig.update_layout(
    template="plotly_white",
    height=500,
    xaxis={'tickangle': -45},
    yaxis=dict(title="Series Totales", rangemode="tozero"),
    margin=dict(l=20, r=20, t=20, b=100)
)

st.plotly_chart(fig, use_container_width=True)

# LEYENDA TÉCNICA
st.markdown("""
<div style="border: 2px solid #000; padding: 15px; background-color: #f9f9f9;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div style="color: #008000;">● <b>MV:</b> Mantenimiento (1-6 series)</div>
        <div style="color: #8B8B00;">● <b>MEV:</b> Mínimo Efectivo (7-12 series)</div>
        <div style="color: #FF8C00;">● <b>MAV:</b> Máximo Adaptativo (13-20 series)</div>
        <div style="color: #FF0000;">● <b>MRV:</b> Sobreentrenamiento (20+ series)</div>
    </div>
</div>
""", unsafe_allow_html=True)




