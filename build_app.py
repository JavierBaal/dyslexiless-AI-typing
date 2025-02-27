#!/usr/bin/env python3
"""
Script para generar un ejecutable de DyslexiLess.
Este script utiliza PyInstaller para crear un ejecutable independiente.
"""

import os
import sys
import subprocess
import shutil
import platform

def check_pyinstaller():
    """Verifica si PyInstaller está instalado y lo instala si es necesario."""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado.")
        return True
    except ImportError:
        print("PyInstaller no está instalado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado correctamente.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al instalar PyInstaller: {e}")
            return False

def create_resources():
    """Crea los recursos necesarios para la aplicación."""
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
            except ImportError:
                print("PIL no está instalado. No se pudo crear un icono personalizado.")
                # Usar un archivo de texto como alternativa
                with open(icon_path, 'w') as f:
                    f.write("DyslexiLess Icon")
                print(f"✅ Archivo de icono de texto creado en {icon_path}")
        except Exception as e:
            print(f"❌ Error al crear el icono: {e}")

def build_executable():
    """Construye el ejecutable usando PyInstaller."""
    print("\n=== Construyendo Ejecutable de DyslexiLess ===")
    
    # Determinar el sistema operativo
    system = platform.system()
    print(f"Sistema operativo detectado: {system}")
    
    # Crear directorio de salida
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    os.makedirs(output_dir, exist_ok=True)
    
    # Configurar opciones de PyInstaller
    icon_option = []
    if system == "Windows":
        # En Windows, necesitamos un archivo .ico
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
        if os.path.exists(icon_path):
            icon_option = ["--icon", icon_path]
    elif system == "Darwin":  # macOS
        # En macOS, podemos usar un archivo .icns o .png
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            icon_option = ["--icon", icon_path]
    
    # Archivos a incluir
    files_to_include = [
        "improved_gui.py",
        "text_corrector.py",
        "keyboardlistener.py",
        "config_manager.py",
        "correction_cache.py",
        "logger_manager.py"
    ]
    
    # Verificar que todos los archivos existen
    missing_files = [f for f in files_to_include if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Faltan los siguientes archivos: {', '.join(missing_files)}")
        return False
    
    # Construir el comando de PyInstaller
    cmd = [
        "pyinstaller",
        "--name=DyslexiLess",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data", f"resources{os.pathsep}resources",
    ]
    
    # Añadir opción de icono si está disponible
    cmd.extend(icon_option)
    
    # Añadir el script principal
    cmd.append("improved_gui.py")
    
    print(f"Ejecutando comando: {' '.join(cmd)}")
    
    try:
        # Ejecutar PyInstaller
        subprocess.check_call(cmd)
        
        # Verificar que el ejecutable se creó correctamente
        if system == "Windows":
            exe_path = os.path.join("dist", "DyslexiLess.exe")
        elif system == "Darwin":  # macOS
            exe_path = os.path.join("dist", "DyslexiLess.app")
        else:  # Linux
            exe_path = os.path.join("dist", "DyslexiLess")
        
        if os.path.exists(exe_path):
            print(f"\n✅ Ejecutable creado correctamente en: {os.path.abspath(exe_path)}")
            return True
        else:
            print(f"❌ No se pudo encontrar el ejecutable en: {os.path.abspath(exe_path)}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar PyInstaller: {e}")
        return False

def main():
    """Función principal."""
    print("=== Generador de Ejecutable de DyslexiLess ===")
    
    # Verificar PyInstaller
    if not check_pyinstaller():
        print("❌ No se pudo continuar sin PyInstaller.")
        return
    
    # Crear recursos
    create_resources()
    
    # Construir ejecutable
    if build_executable():
        print("\n=== Proceso Completado ===")
        print("El ejecutable de DyslexiLess ha sido creado correctamente.")
        print("Puedes encontrarlo en la carpeta 'dist'.")
        print("\nPara ejecutar la aplicación:")
        if platform.system() == "Windows":
            print("  - Haz doble clic en 'dist/DyslexiLess.exe'")
        elif platform.system() == "Darwin":  # macOS
            print("  - Haz doble clic en 'dist/DyslexiLess.app'")
        else:  # Linux
            print("  - Ejecuta 'dist/DyslexiLess'")
    else:
        print("\n❌ No se pudo crear el ejecutable.")
        print("Revisa los errores anteriores para más información.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()