import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX: Intelligence Tracker", layout="wide")

# Estilo Minimalista LYFTX (Negro y Blanco)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stDataEditor { border: 1px solid #000000 !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: CONTROL DE CARGA BIOMECÁNICA")

# Inicialización de Memoria (Sesión)
if 'datos_semana' not in st.session_state:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    st.session_state.datos_semana = {dia: pd.DataFrame(columns=[
        "Grupo Muscular", "Ejercicio", "SER", "REPS", "RIR", "KILS", "REPS LOGRADAS"
    ]) for dia in dias}
if 'max_weights' not in st.session_state:
    st.session_state.max_weights = {}

# 1. Navegador de Días
dia_actual = st.select_slider("Selecciona el día de entrenamiento:", 
                             options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

# 2. Planilla de Entrenamiento (Interfaz de Usuario)
st.subheader(f"📅 Registro de Hoy: {dia_actual}")
df_editado = st.data_editor(
    st.session_state.datos_semana[dia_actual],
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Grupo Muscular": st.column_config.SelectboxColumn("Grupo Muscular", 
            options=["Pecho", "Espalda", "Cuádriceps", "Isquios", "Hombro Frontal", "Deltoide Lateral", "Deltoide Posterior", "Tríceps", "Bíceps", "Glúteo", "Abdomen"], required=True),
        "Ejercicio": st.column_config.TextColumn("Ejercicio", placeholder="Ej: Sentadilla Hack"),
        "SER": st.column_config.NumberColumn("SER", min_value=0, step=1),
        "KILS": st.column_config.NumberColumn("KILS (Peso)", min_value=0.0),
        "REPS LOGRADAS": st.column_config.TextColumn("REPS LOGRADAS (Control de Marcas)", width="large", placeholder="Ej: 12-10-10-8"),
    }
)
st.session_state.datos_semana[dia_actual] = df_editado

# 3. Procesamiento de Datos (Lógica de Carga y Récords)
df_full = pd.concat(st.session_state.datos_semana.values())
musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Hombro Frontal", "Deltoide Lateral", "Deltoide Posterior", "Tríceps", "Bíceps", "Glúteo", "Abdomen"]
conteo = {m: 0.0 for m in musculos}

if not df_full.empty:
    for _, fila in df_full.iterrows():
        g = str(fila["Grupo Muscular"])
        ejer = str(fila["Ejercicio"]).strip().upper()
        s = pd.to_numeric(fila["SER"], errors='coerce') or 0
        k = pd.to_numeric(fila["KILS"], errors='coerce') or 0
        
        # Lógica de Récords Personales
        if ejer != "NAN" and k > 0:
            if k > st.session_state.max_weights.get(ejer, 0):
                st.session_state.max_weights[ejer] = k
                st.toast(f"🔥 ¡NUEVO RÉCORD en {ejer}: {k}kg!", icon="🏆")

        # Lógica Biomecánica Automática
        if s > 0:
            if g in conteo: conteo[g] += s
            if g == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Hombro Frontal"] += (s * 0.5)
            elif g == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide Posterior"] += (s * 0.5)
            elif g == "Cuádriceps":
                conteo["Glúteo"] += (s * 0.3)
            elif g == "Isquios":
                conteo["Glúteo"] += (s * 0.5)
            elif g == "Hombro Frontal":
                conteo["Tríceps"] += (s * 0.5)

    # 4. Gráfica de Semáforo de Fatiga
    st.divider()
    st.subheader("📊 Análisis de Volumen Semanal Acumulado")
    
    # Rojo si supera 22 series (zona de sobre-esfuerzo para la mayoría)
    colores_barras = ['#000000' if v <= 22 else '#FF4B4B' for v in conteo.values()]
    
    fig = go.Figure(go.Bar(
        x=list(conteo.keys()), 
        y=list(conteo.values()), 
        marker_color=colores_barras,
        text=list(conteo.values()),
        textposition='auto'
    ))
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # 5. Exportación y Resumen
    st.download_button(
        label="📥 DESCARGAR REPORTE PARA ENTRENADOR",
        data=df_full.to_csv(index=False).encode('utf-8'),
        file_name='reporte_entrenamiento_lyftx.csv',
        mime='text/csv'
    )
else:
    st.info("La planilla está vacía. Selecciona un día y añade ejercicios para ver el análisis de carga.")

if st.button("BORRAR DATOS DE LA SEMANA"):
    st.session_state.datos_semana = {d: pd.DataFrame(columns=["Grupo Muscular", "Ejercicio", "SER", "REPS", "RIR", "KILS", "REPS LOGRADAS"]) for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]}
    st.rerun()
