
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Configuración de Marca y Estética Minimalista
st.set_page_config(page_title="LYFTX: Performance", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2 { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    /* Eliminamos solo el encabezado del índice, no los datos */
    [data-testid="stTable"] th:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: PERFORMANCE TRACKER")

# 2. Variables de Control
musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

if 'db' not in st.session_state:
    st.session_state.db = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kg"]) for dia in dias}

# 3. Interfaz de Usuario (Registro)
for dia in dias:
    with st.expander(f"💪 {dia}"):
        # Usamos hide_index=True de forma nativa para evitar romper la lógica
        edited_df = st.data_editor(
            st.session_state.db[dia],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True, 
            key=f"editor_{dia}",
            column_config={
                "Músculo": st.column_config.SelectboxColumn(options=musculos, required=True),
                "Series": st.column_config.NumberColumn(min_value=0, step=1, default=0),
                "Kg": st.column_config.TextColumn("Kg")
            }
        )
        st.session_state.db[dia] = edited_df

# 4. MOTOR DE CÁLCULO (Suma Absoluta)
# Aquí es donde estaba el error: ahora forzamos la lectura de cada fila escrita
conteo = {m: 0.0 for m in musculos}

for dia in dias:
    df_dia = st.session_state.db[dia]
    # Limpiamos filas vacías para que no den error de cálculo
    df_clean = df_dia.dropna(subset=["Músculo", "Series"])
    
    for _, row in df_clean.iterrows():
        m = row["Músculo"]
        try:
            s = float(row["Series"])
        except:
            s = 0.0
            
        if m in conteo:
            conteo[m] += s
            # Lógica de apoyo (Biomecánica)
            if m == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Deltoide frontal"] += (s * 0.5)
            elif m == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide posterior"] += (s * 0.5)
            elif m == "Cuádriceps":
                conteo["Glúteos"] += (s * 0.3)
            elif m == "Isquios":
                conteo["Glúteos"] += (s * 0.5)

# 5. GRÁFICA Y COLORES (Amarillo MEV corregido)
st.divider()
st.header("VOLUMEN SEMANAL ACUMULADO")

def get_color(v):
    if v == 0: return "#E0E0E0"  # Gris (Sin datos)
    if v <= 6: return "#00FF00"  # Verde (MV)
    if v <= 12: return "#FFFF00" # Amarillo Puro (MEV)
    if v <= 20: return "#FFA500" # Naranja (MAV)
    return "#FF0000"            # Rojo (MRV)

fig = go.Figure(go.Bar(
    x=musculos,
    y=[conteo[m] for m in musculos],
    marker_color=[get_color(conteo[m]) for m in musculos],
    text=[conteo[m] for m in musculos],
    textposition='outside'
))

fig.update_layout(template="plotly_white", height=500, margin=dict(t=20, b=100))
st.plotly_chart(fig, use_container_width=True)

# Leyenda
st.markdown("""
<div style="border: 1px solid #000; padding: 10px; display: flex; justify-content: space-around;">
    <span style="color: #008000;">● MV (1-6)</span>
    <span style="color: #CCCC00;">● MEV (7-12)</span>
    <span style="color: #FF8C00;">● MAV (13-20)</span>
    <span style="color: #FF0000;">● MRV (20+)</span>
</div>
""", unsafe_allow_html=True)

