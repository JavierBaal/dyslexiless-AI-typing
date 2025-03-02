@echo off
echo Instalando DyslexiLess...
echo Por favor espera, esto puede tardar unos minutos.
echo.

:: Comprobar si Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado. Descargando e instalando Python...
    :: Descargar Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe' -OutFile 'python-installer.exe'"
    
    :: Instalar Python silenciosamente con pip
    echo Instalando Python (esto puede tardar unos minutos)...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    
    :: Eliminar el instalador
    del python-installer.exe
) else (
    echo Python ya está instalado.
)

:: Actualizar pip e instalar dependencias
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install PyQt6 pynput anthropic openai requests

:: Ejecutar la aplicación
echo Iniciando DyslexiLess...
python improved_gui.py

echo.
echo ¡Instalación completada! DyslexiLess está ahora en ejecución.
echo Si la aplicación no se inicia, por favor reinicia tu ordenador e intenta de nuevo.
pause