import redis
import pandas as pd
import dateutil.parser
import time

# --- 1. CONFIGURACIÓN REDIS CLOUD ---
# Ya puse aquí tus credenciales exactas
REDIS_HOST = 'redis-15209.c11.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT = 15209
REDIS_PASSWORD = 'pgop5DYncOMRfxKuxkvTwC8DqS8UgdNY'

try:
    r = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        password=REDIS_PASSWORD, 
        decode_responses=True
    )
    # Ping simple para probar
    if r.ping():
        print("[OK] Conectado a Redis Cloud exitosamente.")
except Exception as e:
    print(f"[ERROR] No se pudo conectar: {e}")
    exit()

# --- 2. LEER EL CSV ---
print("[INFO] Leyendo CSV...")

# IMPORTANTE: Asegurate de que el archivo se llame asi o cambia el nombre abajo
nombre_archivo = 'spotify_history.csv' 

try:
    df = pd.read_csv(nombre_archivo)
except FileNotFoundError:
    print(f"[ERROR] No encuentro el archivo '{nombre_archivo}'. Revisa que este en la misma carpeta.")
    exit()

# --- 3. SUBIDA MASIVA (PIPELINE) ---
print(f"[INFO] Iniciando carga de {len(df)} registros...")

pipe = r.pipeline()
contador_lote = 0

for index, row in df.iterrows():
    # A. Generamos la llave única
    key = f"repro:{index}"
    
    # B. Convertimos fecha para el indice
    try:
        ts_str = row['ts']
        dt_object = dateutil.parser.parse(ts_str)
        score = dt_object.timestamp()
    except:
        score = 0
        ts_str = "Desconocido"

    # C. Preparamos datos (Todo a String)
    datos_cancion = {
        "track_name": str(row.get('track_name', '')),
        "artist_name": str(row.get('artist_name', '')),
        "platform": str(row.get('platform', '')),
        "skipped": str(row.get('skipped', 'FALSE')),
        "ts": str(ts_str),
        "full_id": key
    }
    
    # D. Agregamos a la tuberia
    pipe.hset(key, mapping=datos_cancion)
    pipe.zadd('timeline_repros', {key: score})
    
    # E. Ejecutar cada 1000
    contador_lote += 1
    if contador_lote >= 1000:
        pipe.execute()
        pipe = r.pipeline()
        contador_lote = 0
        print(f"   -> Procesados {index + 1} registros...")

# Ejecutar los restantes
pipe.execute()
print("[FIN] Carga terminada. Todos los datos estan en la nube.")