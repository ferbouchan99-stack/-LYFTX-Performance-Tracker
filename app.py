import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="LYFTX", layout="wide")

# 🔐 SUPABASE
SUPABASE_URL = "TU_URL"
SUPABASE_KEY = "TU_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# PWA (APP INSTALABLE)
# =========================
st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#000000">
""", unsafe_allow_html=True)

# =========================
# ESTILO APPLE MINIMAL
# =========================
st.markdown("""
<style>
.stApp { background-color: #ffffff; }
h1 { font-weight: 900; text-align:center; }
button { border-radius: 12px !important; height: 50px; font-weight:600; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN / REGISTER
# =========================
if st.session_state.user is None:

    st.title("LYFTX")

    tab1, tab2 = st.tabs(["Login", "Registro"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Entrar"):
            try:
                user = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = user.user
                st.rerun()
            except:
                st.error("Error de login")

    with tab2:
        email_r = st.text_input("Email registro")
        pass_r = st.text_input("Password registro", type="password")

        if st.button("Crear cuenta"):
            try:
                supabase.auth.sign_up({
                    "email": email_r,
                    "password": pass_r
                })
                st.success("Cuenta creada 🔥")
            except:
                st.error("Error al registrar")

    st.stop()

# =========================
# APP PRINCIPAL
# =========================
st.title("LYFTX PERFORMANCE")

user_id = st.session_state.user.id

musculos = [
    "Pecho","Espalda","Cuádriceps","Isquios","Tríceps",
    "Bíceps","Glúteos","Gemelos","Core",
    "Deltoide frontal","Deltoide lateral","Deltoide posterior"
]

dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

# =========================
# INPUT APP STYLE
# =========================
st.subheader("Registrar entrenamiento")

col1, col2, col3 = st.columns(3)

with col1:
    dia = st.selectbox("Día", dias)

with col2:
    musculo = st.selectbox("Músculo", musculos)

with col3:
    series = st.number_input("Series", min_value=0, step=1)

if st.button("Guardar"):
    supabase.table("entrenamientos").insert({
        "user_id": user_id,
        "dia": dia,
        "musculo": musculo,
        "series": series
    }).execute()

    st.success("Guardado 🔥")
    st.rerun()

# =========================
# CARGAR DATA
# =========================
data = supabase.table("entrenamientos").select("*").eq("user_id", user_id).execute()

df = pd.DataFrame(data.data)

# =========================
# HISTORIAL
# =========================
st.subheader("Historial")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Sin datos aún")

# =========================
# CALCULO VOLUMEN
# =========================
conteo = {m: 0 for m in musculos}

if not df.empty:
    for _, row in df.iterrows():
        m = row["musculo"]
        s = row["series"]

        conteo[m] += s

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

# =========================
# GRAFICA
# =========================
st.divider()
st.subheader("Volumen semanal")

def get_color(v):
    if v == 0: return "#E0E0E0"
    if v <= 6: return "#00FF00"
    if v <= 12: return "#FFEA00"
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

# =========================
# IA RECOMENDACIONES
# =========================
st.divider()
st.subheader("Recomendación inteligente")

for m, v in conteo.items():
    if v < 8:
        st.warning(f"{m}: sube volumen")
    elif v > 20:
        st.error(f"{m}: sobreentrenamiento")
    else:
        st.success(f"{m}: óptimo")

# =========================
# LOGOUT
# =========================
if st.button("Cerrar sesión"):
    st.session_state.user = None
    st.rerun()



