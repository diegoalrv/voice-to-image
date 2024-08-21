@echo off
echo Iniciando el despliegue de la aplicación web con Docker...

:: Verificar si Docker está corriendo
docker info >nul 2>&1
if ERRORLEVEL 1 (
    echo Docker no está en ejecución. Por favor, asegúrate de que Docker esté iniciado e inténtalo de nuevo.
    exit /b 1
)

:: Ejecutar docker-compose para construir y levantar el contenedor
echo Ejecutando docker-compose...
docker-compose up -d --build

:: Verificar si el contenedor se ha iniciado correctamente
if ERRORLEVEL 1 (
    echo Ocurrió un error al iniciar los servicios de Docker.
    exit /b 1
)

echo La aplicación web ha sido desplegada exitosamente.
echo Accede a la aplicación en http://localhost
pause
