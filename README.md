# BEN AURA - Panel de Finanzas

App de Streamlit + MySQL (XAMPP). Estos son los pasos para correrla en **otra computadora**.

## Requisitos previos
- **Python 3.12 o superior** instalado (descargar de https://www.python.org/downloads/). Al instalarlo marcar **"Add Python to PATH"**.
- **XAMPP** instalado (https://www.apachefriends.org/). Sirve para tener MySQL con phpMyAdmin.

## Paso 1: Copiar los archivos
Copiar a la otra computadora esta carpeta (o al menos estos 3 archivos):
- `app.py`
- `requirements.txt`
- `setup_db.sql`

## Paso 2: Iniciar MySQL (XAMPP)
1. Abrir **XAMPP Control Panel**.
2. Botón **Start** en la fila **MySQL**.
3. Si MySQL usa el **puerto 3306** (XAMPP por defecto), iniciar la app con `BEN_AURA_DB_PORT=3306` (ver Paso 5). En esta PC se usa el puerto 3307.

## Paso 3: Crear la base de datos
En una terminal (CMD) dentro de la carpeta del proyecto:

```
mysql -u root -h localhost -P 3306 < setup_db.sql
```

(Usar `-P 3307` si el MySQL está en el puerto 3307).
Esto crea `benaura_db` con la tabla `ventas` y los datos actuales.

## Paso 4: Instalar dependencias
```
pip install -r requirements.txt
```

## Paso 5: Ejecutar la app
```
streamlit run app.py
```

Si el puerto de MySQL no es 3307, definir la variable de entorno (PowerShell):
```
$env:BEN_AURA_DB_PORT="3306"
$env:BEN_AURA_DB_HOST="localhost"
$env:BEN_AURA_DB_USER="root"
$env:BEN_AURA_DB_PASSWORD=""
streamlit run app.py
```

Otras variables opcionales: `BEN_AURA_DB_HOST`, `BEN_AURA_DB_USER`, `BEN_AURA_DB_PASSWORD`.

## Respaldo de datos
Para exportar la base desde la otra PC:
```
mysqldump -u root -h localhost -P 3306 benaura_db > respaldo.sql
```