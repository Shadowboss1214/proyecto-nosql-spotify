import redis
import dateutil.parser

#db = redis.Redis(host='localhost', port=6379, decode_responses=True)
db = redis.Redis(
    host='redis-15209.c11.us-east-1-2.ec2.cloud.redislabs.com',
    port=15209,
    password='pgop5DYncOMRfxKuxkvTwC8DqS8UgdNY',
    decode_responses=True
)

print("Iniciando indexación... esto puede tardar unos segundos.")


pipe = db.pipeline()
count = 0

# 2. Recorremos TODAS las llaves repro:*
for key in db.scan_iter(match='repro:*'):
    # Obtenemos solo el campo 'ts' (timestamp)
    ts_string = db.hget(key, 'ts')
    
    if ts_string:
        try:
            #"2023-11-15T10:00:00Z" -> 1700042400.0
            dt_object = dateutil.parser.parse(ts_string)
            score = dt_object.timestamp()
            
            pipe.zadd('timeline_repros', {key: score})
            
            count += 1
            if count % 5000 == 0:
                print(f"Procesados {count} registros...")
                pipe.execute()
                pipe = db.pipeline()
        except:
            pass

pipe.execute()
print(f"¡Listo! Se ordenaron {count} canciones en el índice 'timeline_repros'.")