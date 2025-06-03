from supabase import create_client
import os
from datetime import datetime
import uuid

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Supabase URL o KEY no está definida en los secrets")
    
supabase = create_client(url, key)

def guardar_datos(data):
    row = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "ip": data.get("ip"),
        "browser": data.get("browser"),
        "os": data.get("os"),
        "hostname": data.get("hostname"),
    }
    print("Datos a guardar:", row)
    try:
        response = supabase.table("visitas").insert(row).execute()
        print("✅ Datos insertados:", response)
    except Exception as e:
        print("❌ Error al guardar en Supabase:", e)

def obtener_visitas():
    response = supabase.table("visitas").select("*").order("timestamp", desc=True).execute()
    return response.data

def check_credentials(username, password, db):
    return db.get(username) == password
