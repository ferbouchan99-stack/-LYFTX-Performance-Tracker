import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de Marca y Limpieza de Interfaz
st.set_page_config(page_title="LYFTX: Performance", layout="wide")

st.markdown("""
    <style>
    /* Eliminación radical de la columna de índice y bordes innecesarios */
    [data-testid="stDEIndexColumn"] { display: none !important; }
    .stApp { background-color: #ffffff; }
    h1, h2 { color: #000000 !important; font-family: 'Helvetica', sans-serif; font-weight: 800; }
    .stExpander { border: 1px solid #000 !important; border-radius: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

# 2. Estructura de Datos
musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Inicialización robusta del estado
if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg"]) for dia in dias}

# 3. Interfaz de Registro (Vertical y Limpia)
for dia in dias:
    with st.expander(dia, expanded=(dia == "Lunes")):
        # hide_index=True elimina la columna '0' de raíz
        edited_df = st.data_editor(
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
        st.session_state.db[dia] = edited_df

# 4. Motor de Cálculo de Volumen (Suma Real de Todas las Filas)
conteo = {m: 0.0 for m in musculos}

for dia in dias:
    df_actual = st.session_state.db[dia]
    if not df_actual.empty:
        # Forzamos la lectura de cada fila para que no se salte ninguna
        for _, row in df_actual.iterrows():
            m_nombre = row["Músculo"]
            try:
                s_valor = float(row["Series"]) if row["Series"] else 0.0
            except:
                s_valor = 0.0
            
            if m_nombre in conteo:
                conteo[m_nombre] += s_valor
                
                # Lógica Biomecánica de apoyo
                if m_nombre == "Pecho":
                    conteo["Tríceps"] += (s_valor * 0.5); conteo["Deltoide frontal"] += (s_valor * 0.5)
                elif m_nombre == "Espalda":
                    conteo["Bíceps"] += (s_valor * 0.5); conteo["Deltoide posterior"] += (s_valor * 0.5)
                elif m_nombre == "Cuádriceps":
                    conteo["Glúteos"] += (s_valor * 0.3)
                elif m_nombre == "Isquios":
                    conteo["Glúteos"] += (s_valor * 0.5)

# 5. Visualización de Gráfica con Colores de Intensidad
st.divider()
st.header("VOLUMEN SEMANAL ACUMULADO")

def get_color(v):
    if v == 0: return "#E0E0E0"  # Gris
    if v <= 6: return "#00FF00"  # Verde (MV)
    if v <= 12: return "#FFFF00" # Amarillo Puro (MEV)
    if v <= 20: return "#FFA500" # Naranja (MAV)
    return "#FF0000"            # Rojo (MRV)

fig = go.Figure(go.Bar(
    x=musculos,
    y=[conteo[m] for m in musculos],
    marker_color=[get_color(conteo[m]) for m in musculos],
    text=[conteo[m] for m in musculos],
    textposition='auto'
))

fig.update_layout(template="plotly_white", height=500, margin=dict(t=20, b=100))
st.plotly_chart(fig, use_container_width=True)

# Leyenda Profesional
st.markdown("""
<div style="border: 2px solid #000; padding: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
    <div style="color: #008000;">● <b>MV:</b> Mantenimiento (1-6)</div>
    <div style="color: #CCCC00;">● <b>MEV:</b> Mínimo Efectivo (7-12)</div>
    <div style="color: #FF8C00;">● <b>MAV:</b> Máximo Adaptativo (13-20)</div>
    <div style="color: #FF0000;">● <b>MRV:</b> Sobreentrenamiento (20+)</div>
</div>
""", unsafe_allow_html=True)
