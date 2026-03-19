import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX: Tracker", layout="wide")

# Estilo Minimalista LYFTX
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stDataEditor { border: 1px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: CONTROL DE VOLUMEN")

# 1. CREAR EL "CAJÓN" DE MEMORIA (Si no existe)
if 'db' not in st.session_state:
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    # Creamos una tabla vacía para cada día
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kilos", "Reps Logradas"]) for dia in dias}

# 2. SELECCIÓN DE DÍA
dia_actual = st.select_slider("Día de la semana:", options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])

# 3. TABLA DE REGISTRO
st.subheader(f"🏋️ Registro: {dia_actual}")

# Cargamos los datos guardados de ese día específico
df_dia = st.session_state.db[dia_actual]

lista_musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]

# Editor de datos que GUARDA AUTOMÁTICAMENTE al escribir
df_editado = st.data_editor(
    df_dia,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key=f"editor_{dia_actual}", # Llave única para que no se mezcle
    column_config={
        "Músculo": st.column_config.SelectboxColumn("Músculo", options=lista_musculos, required=True),
        "Reps Logradas": st.column_config.TextColumn("Reps (Bitácora)", width="large"),
        "Kilos": st.column_config.NumberColumn("Kilos", format="%.1f"),
        "Series": st.column_config.NumberColumn("Series", min_value=0, step=1)
    }
)

# GUARDAR CAMBIOS: Aquí es donde evitamos que se borren
st.session_state.db[dia_actual] = df_editado

# 4. CÁLCULO DE VOLUMEN TOTAL (Biomecánica)
# Unimos todos los días para la gráfica
df_todo = pd.concat(st.session_state.db.values())
conteo = {m: 0.0 for m in lista_musculos}

if not df_todo.empty:
    for _, fila in df_todo.iterrows():
        m = str(fila["Músculo"])
        s = pd.to_numeric(fila["Series"], errors='coerce') or 0
        if s > 0:
            if m in conteo: conteo[m] += s
            # Biomecánica automática (Suma a secundarios)
            if m == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Deltoide frontal"] += (s * 0.5)
            elif m == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide posterior"] += (s * 0.5)
            elif m == "Cuádriceps":
                conteo["Glúteos"] += (s * 0.3)
            elif m == "Isquios":
                conteo["Glúteos"] += (s * 0.5)

    # 5. GRÁFICA DE LYFTX
    st.divider()
    colores = ['#000000' if v <= 20 else '#FF4B4B' for v in conteo.values()]
    fig = go.Figure(go.Bar(x=list(conteo.keys()), y=list(conteo.values()), marker_color=colores))
    fig.update_layout(template="plotly_white", height=450, title="Volumen Semanal Acumulado (Series)")
    st.plotly_chart(fig, use_container_width=True)

# Botón para descargar el reporte final
if st.button("📥 Generar Reporte Semanal"):
    csv = df_todo.to_csv(index=False).encode('utf-8')
    st.download_button("Click para descargar CSV", csv, "reporte_lyftx.csv", "text/csv")




