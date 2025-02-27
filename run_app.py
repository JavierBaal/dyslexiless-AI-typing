#!/usr/bin/env python3
"""
Script para ejecutar la aplicación DyslexiLess.
Este script proporciona una forma fácil de iniciar la aplicación y muestra instrucciones claras.
"""

import os
import sys
import subprocess
import time

def print_header():
    """Imprime el encabezado de la aplicación."""
    print("\n" + "=" * 60)
    print("               DyslexiLess - Asistente de Escritura")
    print("=" * 60)
    print("Una herramienta de corrección en tiempo real para personas con dislexia")
    print("-" * 60)

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("Verificando dependencias...")
    
    try:
        # Importar dependencias clave para verificar que estén instaladas
        import PyQt6
        import pynput
        import requests
        
        print("✅ Dependencias básicas verificadas.")
        return True
    except ImportError as e:
        print(f"❌ Error: Falta dependencia - {e}")
        print("\nPor favor, instale las dependencias requeridas:")
        print("pip install -r requirements.txt")
        return False

def run_application():
    """Ejecuta la aplicación principal."""
    print("\nIniciando DyslexiLess...")
    
    try:
        # Ejecutar la aplicación principal
        result = subprocess.run(["python", "main.py"], capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ La aplicación se cerró correctamente.")
        else:
            print(f"\n❌ La aplicación se cerró con código de error: {result.returncode}")
    except Exception as e:
        print(f"\n❌ Error al ejecutar la aplicación: {e}")

def show_instructions():
    """Muestra instrucciones para el usuario."""
    print("\n" + "-" * 60)
    print("INSTRUCCIONES DE USO:")
    print("-" * 60)
    print("1. Configure su servicio de IA preferido y API key en la ventana de configuración")
    print("2. Haga clic en 'Guardar y Comenzar' para iniciar el servicio de corrección")
    print("3. La aplicación se ejecutará en segundo plano, monitoreando su escritura")
    print("4. Las correcciones se aplicarán automáticamente mientras escribe")
    print("\nPara probar el corrector sin configurar una API:")
    print("- Ejecute: python test_fallback.py")
    print("-" * 60)

def main():
    """Función principal."""
    print_header()
    
    # Verificar el directorio actual
    print(f"Directorio actual: {os.getcwd()}")
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    # Mostrar instrucciones
    show_instructions()
    
    # Preguntar al usuario si desea continuar
    response = input("\n¿Desea iniciar la aplicación? (s/n): ").strip().lower()
    
    if response == 's' or response == 'si' or response == 'sí' or response == 'y' or response == 'yes':
        run_application()
    else:
        print("\nAplicación no iniciada. Puede ejecutarla más tarde con:")
        print("python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nFin del script.")