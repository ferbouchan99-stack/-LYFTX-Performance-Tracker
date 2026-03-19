import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX Tracker", layout="wide")

# CSS para eliminar la primera columna (índice) y limpiar la interfaz
st.markdown("""
    <style>
    [data-testid="stTable"] th:first-child, [data-testid="stTable"] td:first-child { display: none; }
    [data-testid="stVerticalBlock"] div:has(th:first-child) td:first-child { display: none; }
    .stDataEditor [data-testid="stDEIndexColumn"] { display: none; }
    .stApp { background-color: #ffffff; }
    h1, h2 { color: #000000 !important; font-family: 'Helvetica', sans-serif; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg"]) for dia in dias}

# --- ENTRADA DE DATOS ---
for dia in dias:
    with st.expander(dia, expanded=(dia == "Lunes")):
        # hide_index=True es clave aquí para eliminar la fila "0"
        res_edicion = st.data_editor(
            st.session_state.db[dia],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True, 
            key=f"editor_{dia}",
            column_config={
                "Músculo": st.column_config.SelectboxColumn(options=musculos, required=True),
                "Series": st.column_config.NumberColumn("Series", min_value=0, step=1, default=0),
                "Kg": st.column_config.TextColumn("Kg")
            }
        )
        st.session_state.db[dia] = res_edicion

# --- MOTOR DE CÁLCULO (SUMA TOTAL REAL) ---
volumen_total = {m: 0.0 for m in musculos}

for dia in dias:
    df = st.session_state.db[dia]
    if not df.empty:
        # Usamos .values para asegurar que leemos el dato crudo de la celda
        for m, s in zip(df["Músculo"].values, df["Series"].values):
            if m in volumen_total and s is not None:
                val = float(s)
                volumen_total[m] += val
                
                # Biomecánica (Suma indirecta)
                if m == "Pecho":
                    volumen_total["Tríceps"] += (val * 0.5); volumen_total["Deltoide frontal"] += (val * 0.5)
                elif m == "Espalda":
                    volumen_total["Bíceps"] += (val * 0.5); volumen_total["Deltoide posterior"] += (val * 0.5)
                elif m == "Cuádriceps":
                    volumen_total["Glúteos"] += (val * 0.3)
                elif m == "Isquios":
                    volumen_total["Glúteos"] += (val * 0.5)

# --- GRÁFICA CORREGIDA ---
st.divider()
st.header("VOLUMEN SEMANAL ACUMULADO")

def color_logic(v):
    if v == 0: return "#F0F0F0"
    if v <= 6: return "#00FF00"  # Verde
    if v <= 12: return "#FFFF00" # Amarillo Puro
    if v <= 20: return "#FFA500" # Naranja
    return "#FF0000"            # Rojo

colores = [color_logic(volumen_total[m]) for m in musculos]

fig = go.Figure(go.Bar(
    x=musculos,
    y=[volumen_total[m] for m in musculos],
    marker_color=colores,
    text=[volumen_total[m] for m in musculos],
    textposition='auto',
))

fig.update_layout(template="plotly_white", height=500, margin=dict(t=20, b=100))
st.plotly_chart(fig, use_container_width=True)

# LEYENDA TÉCNICA
st.markdown("""
<div style="border: 1px solid #000; padding: 10px; display: flex; justify-content: space-around; font-size: 14px;">
    <span style="color: #008000;">● MV (1-6)</span>
    <span style="color: #CCCC00;">● MEV (7-12)</span>
    <span style="color: #FF8C00;">● MAV (13-20)</span>
    <span style="color: #FF0000;">● MRV (20+)</span>
</div>
""", unsafe_allow_html=True)
