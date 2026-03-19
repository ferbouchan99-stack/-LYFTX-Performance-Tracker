import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración básica
st.set_page_config(page_title="LYFTX: Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: TRACKER SEMANAL")

# Músculos y Días
lista_musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Memoria de datos
if 'db_lyftx' not in st.session_state:
    st.session_state.db_lyftx = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Ser", "Reps Objetivo", "Kg", "Reps Sacadas"]) for dia in dias}

# Diseño Vertical (Uno tras otro)
for dia in dias:
    st.subheader(f"📅 {dia}")
    
    # Editor simplificado para evitar el TypeError
    df_editado = st.data_editor(
        st.session_state.db_lyftx[dia],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"editor_{dia}",
        column_config={
            "Músculo": st.column_config.SelectboxColumn(options=lista_musculos, required=True),
            "Ser": st.column_config.NumberColumn(min_value=0, step=1)
        }
    )
    st.session_state.db_lyftx[dia] = df_editado
    st.divider()

# Gráfica de Volumen
df_total = pd.concat(st.session_state.db_lyftx.values())
conteo = {m: 0.0 for m in lista_musculos}

if not df_total.empty:
    for _, fila in df_total.iterrows():
        m = str(fila["Músculo"])
        s = pd.to_numeric(fila["Ser"], errors='coerce') or 0
        if s > 0 and m in conteo:
            conteo[m] += s
            # Biomecánica básica
            if m == "Pecho": conteo["Tríceps"] += (s * 0.5)
            elif m == "Espalda": conteo["Bíceps"] += (s * 0.5)

    st.header("📊 Volumen Semanal")
    fig = go.Figure(go.Bar(x=list(conteo.keys()), y=list(conteo.values()), marker_color='black'))
    fig.update_layout(template="plotly_white", height=400, xaxis={'tickangle': -45})
    st.plotly_chart(fig, use_container_width=True)
