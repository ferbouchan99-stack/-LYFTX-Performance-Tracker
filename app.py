import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LYFTX: Tracker Vertical", layout="wide")

# Estilo Minimalista LYFTX
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p { color: #000000 !important; font-family: 'Helvetica', sans-serif; }
    .stDataEditor { border: 1px solid #000000 !important; }
    /* Ajuste para que las tablas no se vean raras en móvil */
    [data-testid="stVerticalBlock"] { gap: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("LYFTX: TRACKER SEMANAL")

# 1. LISTA DE MÚSCULOS
lista_musculos = ["Pecho", "Espalda", "Cuádriceps", "Isquios", "Tríceps", "Bíceps", "Glúteos", "Gemelos", "Core", "Deltoide frontal", "Deltoide lateral", "Deltoide posterior"]
dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# 2. INICIALIZACIÓN DE DATOS (Para que no se borre nada)
if 'db_total' not in st.session_state:
    st.session_state.db_total = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kilos", "Reps Logradas"]) for dia in dias}

# 3. DISEÑO VERTICAL (Como tu Excel)
for dia in dias:
    st.subheader(f"📅 {dia}")
    
    # Cada tabla tiene su propia 'key' para que Streamlit sepa guardar los datos por separado
    df_editado = st.data_editor(
        st.session_state.db_total[dia],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"editor_{dia}",
        column_config={
            "Músculo": st.column_config.SelectboxColumn("Músculo", options=lista_musculos, required=True),
            "Reps Logradas": st.column_config.TextColumn("Reps (Bitácora)", width="medium"),
            "Kilos": st.column_config.NumberColumn("Kg", format="%.1f"),
            "Series": st.column_config.NumberColumn("Ser", min_value=0, step=1)
        }
    )
    # Guardamos los cambios inmediatamente
    st.session_state.db_total[dia] = df_editado
    st.divider()

# 4. CÁLCULO DE VOLUMEN (Biomecánica)
df_final = pd.concat(st.session_state.db_total.values())
conteo = {m: 0.0 for m in lista_musculos}

if not df_final.empty:
    for _, fila in df_final.iterrows():
        m = str(fila["Músculo"])
        s = pd.to_numeric(fila["Series"], errors='coerce') or 0
        if s > 0:
            if m in conteo: conteo[m] += s
            # Biomecánica automática
            if m == "Pecho":
                conteo["Tríceps"] += (s * 0.5); conteo["Deltoide frontal"] += (s * 0.5)
            elif m == "Espalda":
                conteo["Bíceps"] += (s * 0.5); conteo["Deltoide posterior"] += (s * 0.5)
            elif m == "Cuádriceps":
                conteo["Glúteos"] += (s * 0.3)
            elif m == "Isquios":
                conteo["Glúteos"] += (s * 0.5)

    # 5. GRÁFICA CORREGIDA (Nombres verticales para mejor visibilidad)
    st.header("📊 Volumen Semanal Acumulado")
    colores = ['#000000' if v <= 20 else '#FF4B4B' for v in conteo.values()]
    
    fig = go.Figure(go.Bar(
        x=list(conteo.keys()), 
        y=list(conteo.values()), 
        marker_color=colores,
        text=list(conteo.values()),
        textposition='auto'
    ))
    
    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis={'tickangle': -45}, # Gira los nombres para que se lean bien
        margin=dict(l=20, r=20, t=20, b=100) # Espacio para los nombres
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Botón de Reset por si quieres empezar una semana nueva
if st.sidebar.button("🗑️ Borrar toda la semana"):
    st.session_state.db_total = {dia: pd.DataFrame(columns=["Músculo", "Ejercicio", "Series", "Kilos", "Reps Logradas"]) for dia in dias}
    st.rerun()




