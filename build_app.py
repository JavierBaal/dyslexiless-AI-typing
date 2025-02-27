#!/usr/bin/env python3
"""
Script para construir ejecutables de DyslexiLess para diferentes plataformas.
Este script usa PyInstaller para crear ejecutables autocontenidos.
"""

import os
import sys
import shutil
import subprocess
import platform

def print_header():
    """Imprime el encabezado del script de construcción."""
    print("\n" + "=" * 60)
    print("            Construcción de DyslexiLess")
    print("=" * 60)

def check_dependencies():
    """Verifica e instala las dependencias necesarias."""
    print("\nVerificando dependencias...")
    
    required_packages = [
        "pyinstaller",
        "PyQt6",
        "pynput",
        "requests",
        "anthropic",
        "openai",
        "Pillow"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} ya está instalado")
        except ImportError:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def create_icon():
    """Crea un ícono para la aplicación si no existe."""
    from PIL import Image, ImageDraw, ImageFont
    
    resources_dir = "resources"
    os.makedirs(resources_dir, exist_ok=True)
    
    icon_path = os.path.join(resources_dir, "icon.png")
    if not os.path.exists(icon_path):
        print("\nCreando ícono de la aplicación...")
        
        # Crear una imagen de 256x256 píxeles
        img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar un círculo azul
        draw.ellipse((20, 20, 236, 236), fill=(65, 105, 225, 255))
        
        # Añadir texto "D"
        try:
            font = ImageFont.truetype("Arial", 120)
        except:
            font = ImageFont.load_default()
        
        draw.text((128, 128), "D", fill=(255, 255, 255, 255), font=font, anchor="mm")
        img.save(icon_path)
        print(f"✅ Icono creado en: {icon_path}")

def build_windows():
    """Construye el ejecutable para Windows."""
    print("\nConstructyendo ejecutable para Windows...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['improved_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icon.png', 'resources'),
        ('README.md', '.'),
        ('requirements.txt', '.')
    ],
    hiddenimports=[
        'PyQt6',
        'pynput',
        'requests',
        'anthropic',
        'openai'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DyslexiLess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico'
)
"""
    
    # Crear el archivo .spec
    with open("DyslexiLess.spec", "w") as f:
        f.write(spec_content)
    
    # Convertir icon.png a icon.ico para Windows
    try:
        from PIL import Image
        img = Image.open("resources/icon.png")
        icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        img.save("resources/icon.ico", sizes=icon_sizes)
    except Exception as e:
        print(f"⚠️ No se pudo crear el archivo .ico: {e}")
    
    # Construir el ejecutable
    subprocess.check_call(["pyinstaller", "DyslexiLess.spec", "--clean"])
    
    print("✅ Ejecutable para Windows creado en: dist/DyslexiLess.exe")

def build_macos():
    """Construye la aplicación para macOS."""
    print("\nConstruyendo aplicación para macOS...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['improved_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icon.png', 'resources'),
        ('README.md', '.'),
        ('requirements.txt', '.')
    ],
    hiddenimports=[
        'PyQt6',
        'pynput',
        'requests',
        'anthropic',
        'openai'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DyslexiLess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DyslexiLess'
)

app = BUNDLE(
    coll,
    name='DyslexiLess.app',
    icon='resources/icon.icns',
    bundle_identifier='com.dyslexiless.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        }
    }
)
"""
    
    # Crear el archivo .spec
    with open("DyslexiLess.spec", "w") as f:
        f.write(spec_content)
    
    # Convertir icon.png a icon.icns para macOS
    try:
        subprocess.check_call([
            "sips",
            "-s", "format", "icns",
            "resources/icon.png",
            "--out", "resources/icon.icns"
        ])
    except Exception as e:
        print(f"⚠️ No se pudo crear el archivo .icns: {e}")
    
    # Construir la aplicación
    subprocess.check_call(["pyinstaller", "DyslexiLess.spec", "--clean"])
    
    print("✅ Aplicación para macOS creada en: dist/DyslexiLess.app")

def build_linux():
    """Construye el AppImage para Linux."""
    print("\nConstruyendo AppImage para Linux...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['improved_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icon.png', 'resources'),
        ('README.md', '.'),
        ('requirements.txt', '.')
    ],
    hiddenimports=[
        'PyQt6',
        'pynput',
        'requests',
        'anthropic',
        'openai'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DyslexiLess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DyslexiLess'
)
"""
    
    # Crear el archivo .spec
    with open("DyslexiLess.spec", "w") as f:
        f.write(spec_content)
    
    # Crear archivo .desktop para Linux
    desktop_content = """[Desktop Entry]
Type=Application
Name=DyslexiLess
Comment=Asistente de escritura para personas con dislexia
Exec=DyslexiLess
Icon=dyslexiless
Categories=Utility;TextTools;Accessibility;
"""
    
    with open("DyslexiLess.desktop", "w") as f:
        f.write(desktop_content)
    
    # Construir el ejecutable
    subprocess.check_call(["pyinstaller", "DyslexiLess.spec", "--clean"])
    
    print("✅ Ejecutable para Linux creado en: dist/DyslexiLess")
    
    # Nota: La creación del AppImage requeriría pasos adicionales y herramientas específicas de Linux

def main():
    """Función principal."""
    print_header()
    
    # Verificar dependencias
    check_dependencies()
    
    # Crear ícono
    create_icon()
    
    # Detectar sistema operativo
    system = platform.system()
    
    try:
        if system == "Windows":
            build_windows()
        elif system == "Darwin":
            build_macos()
        elif system == "Linux":
            build_linux()
        else:
            print(f"❌ Sistema operativo no soportado: {system}")
            return
            
        print("\n✅ Construcción completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la construcción: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
