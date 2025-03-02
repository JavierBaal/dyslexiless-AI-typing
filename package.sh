#!/bin/bash

# Crear directorio temporal para el empaquetado
mkdir -p temp_package

# Copiar solo los archivos necesarios
cp main.py temp_package/
cp text_corrector.py temp_package/
cp config_manager.py temp_package/
cp keyboardlistener.py temp_package/
cp requirements.txt temp_package/
cp -r resources temp_package/

# Copiar los scripts de instalación para Windows
cp Instalar_DyslexiLess.bat temp_package/
cp Crear_Acceso_Directo.bat temp_package/

# Crear un README simple
cat > temp_package/README.txt << EOL
DyslexiLess - Asistente de escritura para personas con dislexia

Instrucciones de instalación:
1. Descomprime este archivo ZIP
2. Haz doble clic en "Instalar_DyslexiLess.bat"
3. Espera a que se complete la instalación
4. La aplicación se iniciará automáticamente

Para iniciar la aplicación en el futuro:
- Usa el acceso directo creado en tu escritorio

Si tienes problemas:
- Asegúrate de tener conexión a internet durante la instalación
- Si la aplicación no se inicia, reinicia tu ordenador e intenta de nuevo
EOL

# Crear el archivo ZIP
cd temp_package
zip -r ../DyslexiLess_Installer.zip *
cd ..

# Limpiar
rm -rf temp_package

echo "Paquete creado: DyslexiLess_Installer.zip"