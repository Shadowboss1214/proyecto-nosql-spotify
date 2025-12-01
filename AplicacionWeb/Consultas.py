from flask import Flask, render_template, request, redirect, url_for
import redis
import time
from datetime import datetime

app = Flask(__name__)
db = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Obtenemos solo el primer elemento de la lista invertida (el más nuevo)
ultimo_registro = db.zrevrange('timeline_repros', 0, 0)
if ultimo_registro:
    la_llave = ultimo_registro[0]
    ultimo_id = int(la_llave.split(':')[1])
    print(f"La última canción registrada es la llave: {ultimo_id}")