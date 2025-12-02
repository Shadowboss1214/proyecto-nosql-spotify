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

## Descripción de Archivos

A continuación se detalla la función de cada componente del código fuente:

* **`app.py`**: Es el núcleo de la aplicación (Backend). Inicia el servidor web con Flask, gestiona la conexión segura con Redis Cloud y contiene las funciones lógicas para ejecutar las operaciones CRUD (Crear, Leer, Actualizar, Borrar) solicitadas por el usuario desde el navegador.
* **`migrarCloud.py`**: Script de utilidad diseñado para la migración de datos. Se encarga de leer el dataset original (CSV), procesarlo y subirlo masivamente a la nube utilizando *Pipelines* de Redis para optimizar el tiempo de transferencia.
* **`ordenar.py`**: Script auxiliar encargado de la indexación. Su función es recorrer los datos desordenados y generar un "Sorted Set" (Índice ordenado) en Redis, lo que permite recuperar y visualizar las canciones cronológicamente.
* **`requirements.txt`**: Archivo de configuración de dependencias. Lista las librerías necesarias (Flask, Redis, Gunicorn, Pandas) para que la plataforma de despliegue (Render) sepa qué instalar para hacer funcionar la aplicación.
* **`templates/index.html`**: Representa la capa de presentación (Frontend). Es el archivo HTML que estructura la interfaz gráfica, mostrando la tabla de reproducciones y los formularios para ingresar o modificar datos.

## Observaciones

**Limitaciones de Infraestructura (Memoria):**
Es importante notar que el dataset original consta de aproximadamente 150,000 registros. Sin embargo, debido a que el servicio de **Redis Cloud en su capa gratuita (Free Tier)** impone un límite de memoria de trabajo de 30MB, no fue posible cargar la base de datos en su totalidad. El proyecto opera con una muestra significativa de los datos que se ajusta a este límite para garantizar la estabilidad y rendimiento del servidor sin incurrir en costos.

**Lógica de Inserción y Consistencia de IDs:**
Dado que Redis es una base de datos NoSQL de tipo Clave-Valor y no posee contadores autoincrementales nativos (como el `AUTO_INCREMENT` de SQL), se implementó una lógica personalizada para la operación **CREATE**:
1.  Antes de insertar, el sistema consulta el índice para identificar cuál es la llave del **último dato registrado**.
2.  Extrae el ID numérico de esa llave y le suma `1`.
3.  Utiliza este nuevo valor para generar la llave del nuevo registro.

Este mecanismo asegura que cada nueva canción tenga un identificador único y secuencial, evitando colisiones o sobrescritura de datos existentes.
