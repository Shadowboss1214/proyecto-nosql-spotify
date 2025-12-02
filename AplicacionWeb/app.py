from flask import Flask, render_template, request, redirect, url_for
import redis
import time
from datetime import datetime

app = Flask(__name__)
#db = redis.Redis(host='localhost', port=6379, decode_responses=True)
db = redis.Redis(
    host='redis-15209.c11.us-east-1-2.ec2.cloud.redislabs.com',
    port=15209,
    password='pgop5DYncOMRfxKuxkvTwC8DqS8UgdNY',
    decode_responses=True
)

@app.route('/')
def index():
    top_keys = db.zrevrange('timeline_repros', 0, 49)
    
    lista_canciones = []
    for key in top_keys:
        item = db.hgetall(key)
        item['full_id'] = key
        if 'ts' not in item: item['ts'] = 'Desconocido'
        lista_canciones.append(item)
    
    return render_template('index.html', canciones=lista_canciones)

@app.route('/crear', methods=['POST'])
def crear():
    #Obtenemos la última llave
    ultimo_registro = db.zrevrange('timeline_repros', 0, 0)
    if ultimo_registro:
        la_llave = ultimo_registro[0]
        ultimo_id = int(la_llave.split(':')[1]) + 1
        new_id = int(ultimo_id)
        key = f"repro:{new_id}"
    
    # Obtenemos la fecha actual en formato ISO
    ahora_iso = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    ahora_score = time.time()
    
    datos = {
        "track_name": request.form['track_name'],
        "artist_name": request.form['artist_name'],
        "platform": request.form['platform'],
        "skipped": request.form['skipped'],
        "ts": ahora_iso # Constructor
    }
    
    db.hset(key, mapping=datos)
    
    #Actualizar el INDICE (ZSet) para que aparezca arriba
    db.zadd('timeline_repros', {key: ahora_score})
    
    return redirect(url_for('index'))

# --- DELETE: BORRAR DE AMBOS LADOS ---
@app.route('/borrar/<path:key>')
def borrar(key):
    # Borramos el dato
    db.delete(key)
    # Borramos también del índice
    db.zrem('timeline_repros', key)
    return redirect(url_for('index'))

# --- UPDATE ---
@app.route('/actualizar', methods=['POST'])
def actualizar():
    key = request.form['full_id']
    nuevo_estado = request.form['skipped']
    db.hset(key, key="skipped", value=nuevo_estado)
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(debug=True)
