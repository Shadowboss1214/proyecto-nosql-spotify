# Proyecto-nosql-spotify

# Gestor de Historial de Spotify

Este proyecto es una aplicación web diseñada para gestionar un dataset de reproducciones de Spotify (Streaming History). Utiliza **Redis** como base de datos NoSQL principal, aprovechando su velocidad y estructuras de datos para manejar más de 150,000 registros de manera eficiente.

## Demo en Vivo
**[Haz clic aquí para ver la aplicación](https://proyecto-nosql-spotify.onrender.com)**

## Herramientas y Lenguajes

Se utilizaron las siguientes tecnologías para el desarrollo del backend, frontend y la gestión de datos:

* **Lenguaje:** Python 3.9
* **Framework Web:** Flask
* **Base de Datos:** Redis (Redis Cloud)
* **Driver:** `redis-py`
* **Servidor Web:** Render Dashboard

## Funcionalidad de la Aplicación

La aplicación implementa una arquitectura **CRUD** (Create, Read, Update, Delete) adaptada a una base de datos de tipo Clave-Valor.

1.  **Lectura (Read):** Muestra un timeline de las últimas 50 canciones reproducidas. Utiliza un **Índice Secundario (Sorted Set)** para ordenar cronológicamente los registros, ya que Redis no garantiza el orden natural de las llaves.
2.  **Creación (Create):** Permite registrar manualmente una nueva reproducción. El sistema genera automáticamente una **ID única basada en Timestamp** para evitar colisiones y actualiza el índice de ordenamiento en tiempo real.
3.  **Actualización (Update):** Permite modificar el estado de la canción (campo `skipped`) mediante una operación atómica, sin necesidad de reescribir todo el objeto JSON/Hash.
4.  **Eliminación (Delete):** Borra el registro de la base de datos y limpia su referencia en el índice para mantener la consistencia de los datos.

## Sentencias CRUD en Redis

A continuación, se documentan los comandos nativos de Redis utilizados por el backend para realizar las operaciones.

### 1. CREATE (Insertar)
Se utiliza `HSET` para guardar los datos y `ZADD` para indexarlos por fecha.
**Descripción:** Crea un Hash bajo una llave única generada por tiempo (repro:ID), almacenando los atributos de la canción como campos.

### 2. READ (listado ordenado)
Se utiliza `ZREVRANGE` para obtener los IDs más recientes.
`ZREVRANGE timeline_repros 0 49`
**Descripción:** Consulta el Sorted Set timeline_repros y devuelve las 50 llaves con la fecha más reciente (orden descendente).

Se utiliza `HGETALL` para recuperar la información completa de cada id de los 50 obtenidos.
`HGETALL repro:1732985000000`
**Descripción:** Obtiene todos los campos y valores (Artista, Canción, Plataforma) almacenados dentro del Hash de la llave especificada.

### 3. UPDATE (Actualizar)
Se utiliza `HSET` (que funciona como Upsert) para modificar un solo campo.
`HSET repro:1732985000000 skipped "TRUE"`
**Descripción:** Modifica únicamente el campo skipped dentro del Hash existente, preservando el resto de la información intacta.

### 4. DELETE (Eliminar)
Se utilizan `DEL` y `ZREM` para una eliminación limpia.
`DEL repro:1732985000000`
**Descripción:** Elimina físicamente la llave y su contenido de la memoria de Redis. El backend también ejecuta ZREM para quitarla del índice.
