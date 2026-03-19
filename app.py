import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# CONFIG
st.set_page_config(page_title="LYFTX Performance", layout="wide")

# ESTILO PRO
st.markdown("""
<style>
.stApp { background-color: #ffffff; }
h1, h2 { color: black; font-weight: 900; }
button { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

# DATA
musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# SESSION STATE
if "db" not in st.session_state:
    st.session_state.db = []

# INPUT UI (APP STYLE)
st.header("REGISTRO DE ENTRENAMIENTO")

col1, col2, col3, col4 = st.columns(4)

with col1:
    dia = st.selectbox("Día", dias)

with col2:
    musculo = st.selectbox("Músculo", musculos)

with col3:
    series = st.number_input("Series", min_value=0, step=1)

with col4:
    if st.button("Agregar"):
        st.session_state.db.append({
            "Día": dia,
            "Músculo": musculo,
            "Series": series
        })

# MOSTRAR DATOS
if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    st.dataframe(df, use_container_width=True)

# CALCULO DE VOLUMEN
conteo = {m: 0 for m in musculos}

for row in st.session_state.db:
    m = row["Músculo"]
    s = row["Series"]

    conteo[m] += s

    # Lógica secundaria
    if m == "Pecho":
        conteo["Tríceps"] += s * 0.5
        conteo["Deltoide frontal"] += s * 0.5

    elif m == "Espalda":
        conteo["Bíceps"] += s * 0.5
        conteo["Deltoide posterior"] += s * 0.5

    elif m == "Cuádriceps":
        conteo["Glúteos"] += s * 0.3

    elif m == "Isquios":
        conteo["Glúteos"] += s * 0.5

# GRAFICA PRO
st.divider()
st.header("VOLUMEN SEMANAL")

def get_color(v):
    if v == 0: return "#E0E0E0"
    if v <= 6: return "#00FF00"
    if v <= 12: return "#FFEA00"  # amarillo fix
    if v <= 20: return "#FFA500"
    return "#FF0000"

fig = go.Figure(go.Bar(
    x=musculos,
    y=[conteo[m] for m in musculos],
    marker_color=[get_color(conteo[m]) for m in musculos],
    text=[conteo[m] for m in musculos],
    textposition='auto'
))

fig.update_layout(template="plotly_white", height=500)
st.plotly_chart(fig, use_container_width=True)

# LEYENDA
st.markdown("""
<div style="border:2px solid black; padding:10px;">
● Verde: Mantenimiento (1-6)<br>
● Amarillo: Efectivo (7-12)<br>
● Naranja: Óptimo (13-20)<br>
● Rojo: Exceso (20+)
</div>
""", unsafe_allow_html=True)
