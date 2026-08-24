# Usa python:3.10-slim para reducir el tamaño de la imagen y agilizar el despliegue
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del repositorio al contenedor
COPY . .

# Variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expone el puerto 5000
EXPOSE 5000

# Arranca la aplicación Flask
CMD ["flask", "run"]

