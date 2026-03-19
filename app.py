import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración visual de LYFTX
st.set_page_config(page_title="LYFTX: Tracker", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stDataEditor { border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: TRACKER SEMANAL")

# Definición de Músculos y Días
lista_musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Inicialización de la base de datos en sesión
if 'db_lyftx' not in st.session_state:
    st.session_state.db_lyftx = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Ser", "Reps Objetivo", "Kg", "Reps Sacadas"]) for dia in dias}

# Renderizado de tablas por día (Vertical)
for dia in dias:
    st.subheader(f"📅 {dia}")
    
    # Versión simplificada para evitar el TypeError del celular
    df_editado = st.data_editor(
        st.session_state.db_lyftx[dia],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"editor_{dia}",
        column_config={
            "Músculo": st.column_config.SelectboxColumn("Músculo", options=lista_musculos, required=True),
            "Ser": st.column_config.NumberColumn("Ser", min_value=0, step=1)
        }
    )
    st.session_state.db_lyftx[dia] = df_editado
    st.divider()

# Sección de Gráfica de Volumen
df_total = pd.concat(st.session_state.db_lyftx.values())
conteo = {m: 0.0 for m in lista_musculos}

if not df_total.empty:
    for _, fila in df_total.iterrows():
        m = str(fila["Músculo"])
        # Convertimos 'Ser' a número para la gráfica
        s = pd.to_numeric(fila["Ser"], errors='coerce') or 0
        if s > 0 and m in conteo:
            conteo[m] += s
            # Lógica biomecánica para secundarios
            if m == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Deltoide frontal"] += (s * 0.5)
            elif m == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide posterior"] += (s * 0.5)
            elif m == "Cuádriceps":
                conteo["Glúteos"] += (s * 0.3)
            elif m == "Isquios":
                conteo["Glúteos"] += (s * 0.5)

    st.header("📊 Volumen Semanal Acumulado")
    fig = go.Figure(go.Bar(
        x=list(conteo.keys()), 
        y=list(conteo.values()), 
        marker_color='black',
        text=list(conteo.values()),
        textposition='auto'
    ))
    fig.update_layout(template="plotly_white", height=500, xaxis={'tickangle': -45}, margin=dict(b=100))
    st.plotly_chart(fig, use_container_width=True)

# Botón para descargar reporte
csv = df_total.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Reporte Semanal", csv, "lyftx_progreso.csv", "text/csv")


