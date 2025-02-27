#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad del corrector de texto.
Este script prueba la integración con diferentes servicios de IA.
"""

import sys
import time
import os
from text_corrector import TextCorrector
from logger_manager import logger

# Asegurarse de que la salida se muestre inmediatamente (sin buffering)
sys.stdout.reconfigure(line_buffering=True)

print("Iniciando script de prueba para DyslexiLess...")
print(f"Directorio actual: {os.getcwd()}")
print("Importando módulos necesarios...")

def test_service(service_name, api_key):
    """Prueba un servicio específico de corrección."""
    print(f"\n=== Probando servicio: {service_name} ===")
    
    # Configuración temporal para la prueba
    import json
    import os
    from config_manager import CONFIG_FILE, ensure_config_dir
    
    # Guardar configuración para la prueba
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            "service": service_name,
            "api_key": api_key
        }, f)
    
    try:
        # Inicializar el corrector
        corrector = TextCorrector()
        
        # Palabras de prueba con errores comunes de dislexia
        test_cases = [
            ("qe", "Creo qe esto funciona"),
            ("enpesar", "Vamos a enpesar el proyecto"),
            ("tanbien", "Yo tanbien quiero ir"),
            ("aser", "Voy a aser la tarea"),
            ("dise", "El dise que vendrá mañana")
        ]
        
        # Probar cada caso
        for word, context in test_cases:
            print(f"\nProbando corrección para: '{word}' en contexto: '{context}'")
            try:
                start_time = time.time()
                correction, was_corrected = corrector.correct_text(word, context)
                elapsed = time.time() - start_time
                
                if was_corrected:
                    print(f"✅ Corregido: '{word}' → '{correction}' ({elapsed:.2f}s)")
                else:
                    print(f"❌ No corregido: '{word}' ({elapsed:.2f}s)")
            except Exception as e:
                print(f"❌ Error en corrección: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error al inicializar el servicio {service_name}: {e}")
        return False

def main():
    """Función principal que ejecuta las pruebas."""
    print("=== Prueba de Corrector de Texto DyslexiLess ===")
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("No se proporcionaron argumentos. Ejecutando prueba con el corrector fallback...")
        print("Para probar otros servicios: python test_corrector.py <servicio> <api_key>")
        print("Servicios disponibles: OpenAI, Anthropic, Mixtral, Fallback")
        
        # Ejecutar prueba con el corrector fallback por defecto
        test_service("InvalidService", "invalid_key")
        print("\n=== Prueba completada ===")
        return
    
    # Si se proporcionaron argumentos, usarlos
    service = sys.argv[1]
    
    if service.lower() == "fallback":
        # Para el servicio fallback, usamos una clave API inválida para forzar el uso del fallback
        test_service("InvalidService", "invalid_key")
    else:
        # Verificar que se proporcionó una clave API
        if len(sys.argv) < 3:
            print(f"Error: Se requiere una clave API para el servicio {service}")
            print(f"Uso: python test_corrector.py {service} <api_key>")
            return
            
        api_key = sys.argv[2]
        test_service(service, api_key)
    
    print("\n=== Prueba completada ===")

if __name__ == "__main__":
    try:
        print("Ejecutando prueba de corrector de texto...")
        main()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución de la prueba: {e}")
        import traceback
        print("\nDetalles del error:")
        traceback.print_exc()
        print("\nSugerencia: Verifique que todas las dependencias estén instaladas correctamente.")
        print("Ejecute: pip install -r requirements.txt")
    finally:
        print("\nFin del script de prueba.")