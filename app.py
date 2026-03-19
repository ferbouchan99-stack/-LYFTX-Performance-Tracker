import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de la App de Entrenamiento LYFTX
st.set_page_config(page_title="LYFTX: Entrenamiento", layout="wide")

st.title("LYFTX: CONTROL DE VOLUMEN")

# Memoria de la semana
if 'datos_semana' not in st.session_state:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    st.session_state.datos_semana = {dia: pd.DataFrame(columns=["Grupo Muscular", "Ejercicio", "SER", "KILS", "REPS LOGRADAS"]) for dia in dias}

# Navegación
dia_actual = st.select_slider("Día:", options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

# Tabla de Registro (Igual a tu Excel)
st.subheader(f"🏋️ Registro: {dia_actual}")
df_editado = st.data_editor(
    st.session_state.datos_semana[dia_actual],
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Grupo Muscular": st.column_config.SelectboxColumn("Músculo", options=["Pecho", "Espalda", "Cuádriceps", "Isquios", "Hombro Frontal", "Deltoide Lateral", "Deltoide Posterior", "Tríceps", "Bíceps", "Glúteo", "Abdomen"]),
        "REPS LOGRADAS": st.column_config.TextColumn("Reps (Bitácora)", width="large"),
        "KILS": st.column_config.NumberColumn("Kilos"),
        "SER": st.column_config.NumberColumn("Series")
    }
)
st.session_state.datos_semana[dia_actual] = df_editado

# Lógica de Volumen Automático (Biomecánica)
df_full = pd.concat(st.session_state.datos_semana.values())
conteo = {m: 0.0 for m in ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Hombro Frontal", "Deltoide Lateral", "Deltoide Posterior", "Tríceps", "Bíceps", "Glúteo", "Abdomen"]}

if not df_full.empty:
    for _, fila in df_full.iterrows():
        g = str(fila["Grupo Muscular"])
        s = pd.to_numeric(fila["SER"], errors='coerce') or 0
        if s > 0:
            if g in conteo: conteo[g] += s
            # Cálculo de secundarios automático
            if g == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Hombro Frontal"] += (s * 0.5)
            elif g == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide Posterior"] += (s * 0.5)
            elif g == "Cuádriceps":
                conteo["Glúteo"] += (s * 0.3)
            elif g == "Isquios":
                conteo["Glúteo"] += (s * 0.5)

    # Gráfica de Semáforo
    st.divider()
    colores = ['#000000' if v <= 20 else '#FF4B4B' for v in conteo.values()]
    fig = go.Figure(go.Bar(x=list(conteo.keys()), y=list(conteo.values()), marker_color=colores))
    fig.update_layout(template="plotly_white", height=400, title="Volumen Semanal Acumulado")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Descargar CSV", df_full.to_csv(index=False).encode('utf-8'), "entrenamiento.csv")

