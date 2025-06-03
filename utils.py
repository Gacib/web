import sqlite3
from pathlib import Path

def guardar_datos(data):
    db_path = Path("data/visitas.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitas (
            timestamp TEXT,
            lat REAL,
            lon REAL,
            ip TEXT,
            browser TEXT,
            os TEXT,
            hostname TEXT
        )
    """)
    
    c.execute("""
        INSERT INTO visitas (timestamp, lat, lon, ip, browser, os, hostname)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["lat"],
        data["lon"],
        data["ip"],
        data["browser"],
        data["os"],
        data["hostname"]
    ))
    
    conn.commit()
    conn.close()
