# Imagen base: Python 3.12, version "slim" (mas liviana, sin cosas de mas que no usamos)
FROM python:3.12-slim

# Carpeta de trabajo DENTRO del contenedor
WORKDIR /app

# Copiamos primero requirements.txt (aprovecha el cache de Docker: si no
# cambian las librerias, no las vuelve a instalar en cada build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiamos el resto del codigo
COPY . .

# Documenta que el contenedor va a escuchar en el puerto 5000
EXPOSE 5000

# Comando que se ejecuta cuando el contenedor arranca
CMD ["python", "app.py"]