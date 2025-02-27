#!/usr/bin/env python3
"""
Script de instalación para DyslexiLess.
Este script instala todas las dependencias necesarias y configura la aplicación.
"""

import os
import sys
import subprocess
import platform
import shutil

def print_header():
    """Imprime el encabezado de la instalación."""
    print("\n" + "=" * 60)
    print("               Instalación de DyslexiLess")
    print("=" * 60)
    print("Este script instalará todas las dependencias necesarias")
    print("y configurará la aplicación DyslexiLess en tu sistema.")
    print("-" * 60)

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    print("\nVerificando versión de Python...")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"❌ Versión de Python incompatible: {major}.{minor}")
        print("DyslexiLess requiere Python 3.8 o superior.")
        return False
    
    print(f"✅ Versión de Python compatible: {major}.{minor}")
    return True

def install_dependencies():
    """Instala las dependencias necesarias."""
    print("\nInstalando dependencias...")
    
    dependencies = [
        "PyQt6",
        "pynput",
        "requests",
        "anthropic>=0.18.0",
        "openai>=1.10.0",
        "Pillow"  # Para crear el icono
    ]
    
    for dep in dependencies:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} instalado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al instalar {dep}: {e}")
            return False
    
    print("\n✅ Todas las dependencias instaladas correctamente.")
    return True

def create_desktop_shortcut():
    """Crea un acceso directo en el escritorio."""
    print("\nCreando acceso directo en el escritorio...")
    
    system = platform.system()
    
    if system == "Windows":
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al escritorio
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Crear un archivo .bat
            shortcut_path = os.path.join(desktop_path, "DyslexiLess.bat")
            with open(shortcut_path, "w") as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}"\n')
            
            print(f"✅ Acceso directo creado en: {shortcut_path}")
            return True
        except Exception as e:
            print(f"❌ Error al crear acceso directo: {e}")
            return False
    
    elif system == "Darwin":  # macOS
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al escritorio
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Crear un archivo .command
            shortcut_path = os.path.join(desktop_path, "DyslexiLess.command")
            with open(shortcut_path, "w") as f:
                f.write(f'#!/bin/bash\ncd "{os.path.dirname(script_path)}"\n"{sys.executable}" "{script_path}"\n')
            
            # Hacer el archivo ejecutable
            os.chmod(shortcut_path, 0o755)
            
            print(f"✅ Acceso directo creado en: {shortcut_path}")
            return True
        except Exception as e:
            print(f"❌ Error al crear acceso directo: {e}")
            return False
    
    elif system == "Linux":
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al escritorio
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.join(os.path.expanduser("~"), "Escritorio")
            
            # Crear un archivo .desktop
            shortcut_path = os.path.join(desktop_path, "DyslexiLess.desktop")
            with open(shortcut_path, "w") as f:
                f.write(f"""[Desktop Entry]
Type=Application
Name=DyslexiLess
Comment=Asistente de escritura para personas con dislexia
Exec={sys.executable} {script_path}
Terminal=false
Categories=Utility;
""")
            
            # Hacer el archivo ejecutable
            os.chmod(shortcut_path, 0o755)
            
            print(f"✅ Acceso directo creado en: {shortcut_path}")
            return True
        except Exception as e:
            print(f"❌ Error al crear acceso directo: {e}")
            return False
    
    else:
        print(f"❌ Sistema operativo no soportado: {system}")
        return False

def setup_autostart():
    """Configura la aplicación para que se inicie automáticamente con el sistema."""
    print("\nConfigurando inicio automático...")
    
    system = platform.system()
    
    if system == "Windows":
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al directorio de inicio automático
            startup_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            
            # Crear un archivo .bat
            autostart_path = os.path.join(startup_path, "DyslexiLess.bat")
            with open(autostart_path, "w") as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}"\n')
            
            print(f"✅ Inicio automático configurado en: {autostart_path}")
            return True
        except Exception as e:
            print(f"❌ Error al configurar inicio automático: {e}")
            return False
    
    elif system == "Darwin":  # macOS
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al directorio de inicio automático
            launch_agents_path = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents")
            os.makedirs(launch_agents_path, exist_ok=True)
            
            # Crear un archivo .plist
            plist_path = os.path.join(launch_agents_path, "com.dyslexiless.app.plist")
            with open(plist_path, "w") as f:
                f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dyslexiless.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""")
            
            # Cargar el agente
            subprocess.call(["launchctl", "load", plist_path])
            
            print(f"✅ Inicio automático configurado en: {plist_path}")
            return True
        except Exception as e:
            print(f"❌ Error al configurar inicio automático: {e}")
            return False
    
    elif system == "Linux":
        try:
            # Ruta al script improved_gui.py
            script_path = os.path.abspath("improved_gui.py")
            
            # Ruta al directorio de inicio automático
            autostart_path = os.path.join(os.path.expanduser("~"), ".config", "autostart")
            os.makedirs(autostart_path, exist_ok=True)
            
            # Crear un archivo .desktop
            desktop_path = os.path.join(autostart_path, "DyslexiLess.desktop")
            with open(desktop_path, "w") as f:
                f.write(f"""[Desktop Entry]
Type=Application
Name=DyslexiLess
Comment=Asistente de escritura para personas con dislexia
Exec={sys.executable} {script_path}
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
""")
            
            # Hacer el archivo ejecutable
            os.chmod(desktop_path, 0o755)
            
            print(f"✅ Inicio automático configurado en: {desktop_path}")
            return True
        except Exception as e:
            print(f"❌ Error al configurar inicio automático: {e}")
            return False
    
    else:
        print(f"❌ Sistema operativo no soportado: {system}")
        return False

def create_resources():
    """Crea los recursos necesarios para la aplicación."""
    print("\nCreando recursos...")
    
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Crear un icono simple si no existe
    icon_path = os.path.join(resources_dir, "icon.png")
    if not os.path.exists(icon_path):
        try:
            # Intentar crear un icono simple usando PIL
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Crear una imagen de 256x256 píxeles
                img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                # Dibujar un círculo
                draw.ellipse((20, 20, 236, 236), fill=(65, 105, 225, 255))
                
                # Añadir texto
                try:
                    font = ImageFont.truetype("Arial", 120)
                except:
                    font = ImageFont.load_default()
                
                draw.text((128, 128), "D", fill=(255, 255, 255, 255), font=font, anchor="mm")
                
                # Guardar la imagen
                img.save(icon_path)
                print(f"✅ Icono creado en {icon_path}")
                return True
            except ImportError:
                print("PIL no está instalado. No se pudo crear un icono personalizado.")
                # Usar un archivo de texto como alternativa
                with open(icon_path, 'w') as f:
                    f.write("DyslexiLess Icon")
                print(f"✅ Archivo de icono de texto creado en {icon_path}")
                return True
        except Exception as e:
            print(f"❌ Error al crear el icono: {e}")
            return False
    else:
        print(f"✅ Icono ya existe en {icon_path}")
        return True

def main():
    """Función principal."""
    print_header()
    
    # Verificar versión de Python
    if not check_python_version():
        print("\n❌ La instalación no puede continuar debido a una versión incompatible de Python.")
        return
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ La instalación no puede continuar debido a errores en la instalación de dependencias.")
        return
    
    # Crear recursos
    create_resources()
    
    # Preguntar si se desea crear un acceso directo
    response = input("\n¿Deseas crear un acceso directo en el escritorio? (s/n): ").strip().lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        create_desktop_shortcut()
    
    # Preguntar si se desea configurar el inicio automático
    response = input("\n¿Deseas que DyslexiLess se inicie automáticamente con el sistema? (s/n): ").strip().lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        setup_autostart()
    
    print("\n" + "=" * 60)
    print("               Instalación Completada")
    print("=" * 60)
    print("DyslexiLess ha sido instalado correctamente en tu sistema.")
    print("\nPara iniciar la aplicación:")
    print("  - Ejecuta: python improved_gui.py")
    print("  - O usa el acceso directo creado en el escritorio (si lo elegiste)")
    print("\n¿Deseas iniciar DyslexiLess ahora? (s/n): ", end="")
    
    response = input().strip().lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        print("\nIniciando DyslexiLess...")
        subprocess.Popen([sys.executable, "improved_gui.py"])
        print("✅ DyslexiLess iniciado correctamente.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstalación interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()