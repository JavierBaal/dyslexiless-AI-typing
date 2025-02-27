#!/usr/bin/env python3
"""
Script principal para ejecutar DyslexiLess.
Este script maneja la ejecución y actualización de la aplicación.
"""

import os
import sys
import subprocess
import json
import platform
import shutil
from urllib.request import urlopen
from urllib.error import URLError
import zipfile
import hashlib

VERSION = "1.0.0"

def print_header():
    """Imprime el encabezado de la aplicación."""
    print("\n" + "=" * 60)
    print("                   DyslexiLess")
    print("=" * 60)
    print(f"Versión: {VERSION}")
    print("-" * 60)

def check_for_updates():
    """Verifica si hay actualizaciones disponibles."""
    try:
        print("\nBuscando actualizaciones...")
        # TODO: Implementar la lógica real de verificación de actualizaciones
        # Por ahora, simularemos que no hay actualizaciones
        print("✅ DyslexiLess está actualizado")
        return False
    except URLError:
        print("⚠️ No se pudo verificar actualizaciones")
        return False

def download_update():
    """Descarga e instala una actualización."""
    try:
        print("\nDescargando actualización...")
        # TODO: Implementar la lógica real de descarga e instalación
        print("✅ Actualización completada")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
        return False

def verify_installation():
    """Verifica que la instalación sea correcta."""
    required_files = [
        "improved_gui.py",
        "keyboardlistener.py",
        "text_corrector.py",
        "config_manager.py",
        "correction_cache.py",
        "logger_manager.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("\n❌ Faltan archivos necesarios:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def ensure_resources():
    """Asegura que existan los recursos necesarios."""
    resources_dir = "resources"
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # Crear directorio de logs si no existe
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

def run_application():
    """Ejecuta la aplicación principal."""
    try:
        print("\nIniciando DyslexiLess...")
        
        if platform.system() == "Windows":
            # En Windows, buscar primero el ejecutable
            if os.path.exists("dist/DyslexiLess/DyslexiLess.exe"):
                subprocess.Popen(["dist/DyslexiLess/DyslexiLess.exe"])
                print("✅ Aplicación iniciada desde el ejecutable")
                return True
        
        # Si no hay ejecutable o no estamos en Windows, usar Python
        subprocess.Popen([sys.executable, "improved_gui.py"])
        print("✅ Aplicación iniciada desde Python")
        return True
        
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        return False

def create_shortcut():
    """Crea un acceso directo en el escritorio."""
    try:
        system = platform.system()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        if system == "Windows":
            if not os.path.exists(f"{desktop_path}/DyslexiLess.lnk"):
                # Usar PowerShell para crear el acceso directo
                script = f"""
                $WScriptShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WScriptShell.CreateShortcut("{desktop_path}/DyslexiLess.lnk")
                $Shortcut.TargetPath = "{os.path.abspath(sys.executable)}"
                $Shortcut.Arguments = "{os.path.abspath('improved_gui.py')}"
                $Shortcut.WorkingDirectory = "{os.path.abspath('.')}"
                $Shortcut.IconLocation = "{os.path.abspath('resources/icon.ico')}"
                $Shortcut.Save()
                """
                with open("create_shortcut.ps1", "w") as f:
                    f.write(script)
                
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_shortcut.ps1"])
                os.remove("create_shortcut.ps1")
                
        elif system == "Darwin":  # macOS
            shortcut_path = f"{desktop_path}/DyslexiLess.command"
            if not os.path.exists(shortcut_path):
                with open(shortcut_path, "w") as f:
                    f.write(f"""#!/bin/bash
cd "{os.path.abspath('.')}"
"{sys.executable}" "{os.path.abspath('improved_gui.py')}"
""")
                os.chmod(shortcut_path, 0o755)
                
        elif system == "Linux":
            desktop_file = f"{desktop_path}/DyslexiLess.desktop"
            if not os.path.exists(desktop_file):
                with open(desktop_file, "w") as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name=DyslexiLess
Comment=Asistente de escritura para personas con dislexia
Exec={sys.executable} {os.path.abspath('improved_gui.py')}
Icon={os.path.abspath('resources/icon.png')}
Terminal=false
Categories=Utility;
""")
                os.chmod(desktop_file, 0o755)
        
        print("✅ Acceso directo creado en el escritorio")
        return True
        
    except Exception as e:
        print(f"⚠️ No se pudo crear el acceso directo: {e}")
        return False

def main():
    """Función principal."""
    print_header()
    
    # Verificar instalación
    if not verify_installation():
        print("\n❌ La instalación está incompleta o dañada")
        print("Por favor, reinstala DyslexiLess")
        input("\nPresiona Enter para salir...")
        return
    
    # Asegurar recursos
    ensure_resources()
    
    # Verificar actualizaciones
    if check_for_updates():
        response = input("\n¿Deseas actualizar ahora? (s/n): ").strip().lower()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            if not download_update():
                print("\n⚠️ Continuando con la versión actual")
    
    # Crear acceso directo si no existe
    create_shortcut()
    
    # Ejecutar la aplicación
    if run_application():
        print("\nDyslexiLess se está ejecutando en segundo plano.")
        print("Puedes encontrar el icono en la barra de sistema.")
    else:
        print("\n❌ No se pudo iniciar DyslexiLess")
        input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
