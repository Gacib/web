import streamlit as st
import jwt
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from utils import check_credentials
from utils import guardar_datos, obtener_visitas

# Config app
st.set_page_config(page_title="Panel Admin", layout="wide")

# Secret key para tokens
SECRET = "supersecretclave"  # ¡Cambia esto!

# Simples credenciales
USUARIOS = {
    "admin": "1234",  # puedes cambiar esto por seguridad
}

# Función para crear token JWT
def crear_token(usuario):
    expiracion = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({"user": usuario, "exp": expiracion}, SECRET, algorithm="HS256")
    return token

# Función para validar token
def validar_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["user"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# --- Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None

# --- Login Form
if not st.session_state.token:
    st.subheader("🔐 Iniciar sesión")
    with st.form("login_form"):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        login_btn = st.form_submit_button("Entrar")

    if login_btn:
        if check_credentials(user, pwd, USUARIOS):
            st.session_state.token = crear_token(user)
            st.success("Login correcto")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# --- Panel principal
else:
    user = validar_token(st.session_state.token)
    if user:
        st.title("📊 Panel de capturas - Web 1")
        st.write(f"Sesión activa para: `{user}`")

        # Mostrar tabla de capturas
        db_path = Path("data/visitas.db")

        visitas = obtener_visitas()
        if visitas:
            df = pd.DataFrame(visitas)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)
        else:
            st.warning("No hay datos aún...")

        if st.button("🔓 Cerrar sesión"):
            st.session_state.token = None
            st.rerun()
    else:
        st.warning("Tu sesión ha expirado. Vuelve a iniciar sesión.")
        st.session_state.token = None
