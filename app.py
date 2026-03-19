import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de LYFTX
st.set_page_config(page_title="LYFTX: Tracker", layout="wide")

# Estilo Minimalista Negro y Blanco
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stDataEditor { border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: CONTROL DE VOLUMEN")

# Memoria de la semana
if 'datos_semana' not in st.session_state:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    st.session_state.datos_semana = {dia: pd.DataFrame(columns=["Grupo Muscular", "Ejercicio", "SER", "KILS", "REPS LOGRADAS"]) for dia in dias}

dia_actual = st.select_slider("Día:", options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

# Lista de músculos según tu imagen
lista_musculos = [
    "Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", 
    "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"
]

# Tabla de Registro
st.subheader(f"🏋️ Registro: {dia_actual}")
df_editado = st.data_editor(
    st.session_state.datos_semana[dia_actual],
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Grupo Muscular": st.column_config.SelectboxColumn("Músculo", options=lista_musculos, required=True),
        "REPS LOGRADAS": st.column_config.TextColumn("Reps (Bitácora)", width="large"),
        "KILS": st.column_config.NumberColumn("Kilos", format="%.1f"),
        "SER": st.column_config.NumberColumn("Series", min_value=0)
    }
)
st.session_state.datos_semana[dia_actual] = df_editado

# Cálculo de Volumen
df_total = pd.concat(st.session_state.datos_semana.values())
conteo = {m: 0.0 for m in lista_musculos}

if not df_total.empty:
    for _, row in df_total.iterrows():
        g = str(row["Grupo Muscular"])
        s = pd.to_numeric(row["SER"], errors='coerce') or 0
        if s > 0:
            if g in conteo: conteo[g] += s
            # Biomecánica: Suma automática a secundarios
            if g == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Deltoide frontal"] += (s * 0.5)
            elif g == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide posterior"] += (s * 0.5)
            elif g == "Cuádriceps":
                conteo["Glúteos"] += (s * 0.3)
            elif g == "Isquios":
                conteo["Glúteos"] += (s * 0.5)

    # Gráfica de Barras
    st.divider()
    # Las barras se ponen rojas si pasas de 20 series
    colores = ['#000000' if v <= 20 else '#FF4B4B' for v in conteo.values()]
    fig = go.Figure(go.Bar(x=list(conteo.keys()), y=list(conteo.values()), marker_color=colores))
    fig.update_layout(template="plotly_white", height=450, title="Volumen Semanal Acumulado")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Descargar Reporte CSV", df_total.to_csv(index=False).encode('utf-8'), "entrenamiento_lyftx.csv")



