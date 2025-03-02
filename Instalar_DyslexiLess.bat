@echo off
echo Instalando DyslexiLess...
echo Por favor espera, esto puede tardar unos minutos.
echo.

:: Comprobar si Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado. Descargando e instalando Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe' -OutFile 'python-installer.exe'"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    del python-installer.exe
)

:: Instalar dependencias
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Ejecutar la aplicación
python main.py

echo Instalación completada!
pause