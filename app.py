
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX Performance", layout="wide")

# Estética minimalista LYFTX
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stExpander { border: 1px solid #e6e6e6 !important; margin-bottom: 10px; border-radius: 0px; }
    /* Eliminar borde de la columna de índice vacía */
    [data-testid="stTable"] th:first-child, [data-testid="stTable"] td:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg", "Reps Objetivo", "Reps Logradas"]) for dia in dias}

# --- REGISTRO DIARIO ---
for dia in dias:
    with st.expander(dia, expanded=False): 
        # hide_index=True elimina la columna vacía de la izquierda
        df_editado = st.data_editor(
            st.session_state.db[dia],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True, 
            key=f"editor_{dia}",
            column_config={
                "Músculo": st.column_config.SelectboxColumn(options=musculos, required=True),
                "Series": st.column_config.NumberColumn(min_value=0, step=1, default=0),
                "Kg": st.column_config.TextColumn("Kg"),
                "Reps Objetivo": st.column_config.TextColumn("Reps Objetivo"),
                "Reps Logradas": st.column_config.TextColumn("Reps Logradas")
            }
        )
        st.session_state.db[dia] = df_editado

# --- MOTOR DE CÁLCULO SUMATORIO ---
volumen = {m: 0.0 for m in musculos}

for dia in dias:
    df_dia = st.session_state.db[dia]
    if not df_dia.empty:
        for _, row in df_dia.iterrows():
            m = str(row["Músculo"])
            try:
                # Suma rigurosa de cada serie ingresada
                s = float(row["Series"]) if row["Series"] else 0.0
            except:
                s = 0.0
            
            if m in volumen:
                volumen[m] += s
                # Lógica de fatiga/volumen indirecto
                if m == "Pecho":
                    volumen["Tríceps"] += (s * 0.5); volumen["Deltoide frontal"] += (s * 0.5)
                elif m == "Espalda":
                    volumen["Bíceps"] += (s * 0.5); volumen["Deltoide posterior"] += (s * 0.5)
                elif m == "Cuádriceps":
                    volumen["Glúteos"] += (s * 0.3)
                elif m == "Isquios":
                    volumen["Glúteos"] += (s * 0.5)

# --- GRÁFICA SEMÁFORO ---
st.divider()
st.header("VOLUMEN SEMANAL ACUMULADO")

def get_color(v):
    if v == 0: return "#E0E0E0" 
    if v <= 6: return "#4CAF50"  # MV
    if v <= 12: return "#FFEB3B" # MEV
    if v <= 20: return "#FF9800" # MAV
    return "#F44336"            # MRV

colores_barras = [get_color(volumen[m]) for m in musculos]

fig = go.Figure(go.Bar(
    x=musculos,
    y=[volumen[m] for m in musculos],
    marker_color=colores_barras,
    text=[volumen[m] for m in musculos],
    textposition='auto',
))

fig.update_layout(template="plotly_white", height=500, xaxis={'tickangle': -45}, margin=dict(b=100))
st.plotly_chart(fig, use_container_width=True)

# LEYENDA TÉCNICA
st.markdown("""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; border: 1px solid #000; padding: 15px;">
    <div style="color: #4CAF50;">● <b>MV:</b> Mantenimiento (1-6 series)</div>
    <div style="color: #D4AF37;">● <b>MEV:</b> Mínimo Efectivo (7-12 series)</div>
    <div style="color: #FF9800;">● <b>MAV:</b> Máximo Adaptativo (13-20 series)</div>
    <div style="color: #F44336;">● <b>MRV:</b> Sobreentrenamiento (20+ series)</div>
</div>
""", unsafe_allow_html=True)


