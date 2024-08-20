# Utilizamos una imagen base oficial de Python
FROM python:3.9

# Establecemos un directorio de trabajo
WORKDIR /app

# Copiamos los archivos de requisitos primero para aprovechar la cache de Docker
COPY ./requirements.txt /app/requirements.txt

# Instalamos las dependencias del proyecto
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copiamos el resto del código de la aplicación
COPY . /app

# Exponemos el puerto en el que se ejecutará la aplicación
EXPOSE 8050

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]
