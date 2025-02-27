#!/usr/bin/env python3
"""
Script de prueba simplificado para el corrector fallback de DyslexiLess.
Este script no requiere argumentos y prueba directamente el corrector fallback.
"""

import os
import sys
import time
from text_corrector import TextCorrector
from logger_manager import logger
from config_manager import CONFIG_FILE, ensure_config_dir
import json

# Configurar salida sin buffer para ver los mensajes inmediatamente
sys.stdout.reconfigure(line_buffering=True)

def setup_fallback_config():
    """Configura el sistema para usar el corrector fallback."""
    print("Configurando para usar el corrector fallback...")
    
    # Crear directorio de configuración si no existe
    ensure_config_dir()
    
    # Guardar configuración con un servicio inválido para forzar el uso del fallback
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            "service": "InvalidService",
            "api_key": "invalid_key"
        }, f)
    
    print(f"Configuración guardada en: {CONFIG_FILE}")

def test_fallback_corrector():
    """Prueba el corrector fallback con palabras comunes con errores de dislexia."""
    print("\n=== Probando Corrector Fallback ===")
    
    try:
        # Inicializar el corrector
        print("Inicializando TextCorrector...")
        corrector = TextCorrector()
        print("TextCorrector inicializado correctamente.")
        
        # Palabras de prueba con errores comunes de dislexia
        test_cases = [
            ("qe", "Creo qe esto funciona"),
            ("enpesar", "Vamos a enpesar el proyecto"),
            ("tanbien", "Yo tanbien quiero ir"),
            ("aser", "Voy a aser la tarea"),
            ("dise", "El dise que vendrá mañana"),
            ("kiero", "Yo kiero un helado"),
            ("ablar", "Vamos a ablar con él"),
            ("oi", "Oi es un buen día"),
            ("mui", "Está mui lejos"),
            ("jente", "Hay mucha jente aquí")
        ]
        
        # Probar cada caso
        success_count = 0
        for word, context in test_cases:
            print(f"\nProbando corrección para: '{word}' en contexto: '{context}'")
            try:
                start_time = time.time()
                correction, was_corrected = corrector.fallback_correct(word, context)
                elapsed = time.time() - start_time
                
                if was_corrected:
                    print(f"✅ Corregido: '{word}' → '{correction}' ({elapsed:.2f}s)")
                    success_count += 1
                else:
                    print(f"❌ No corregido: '{word}' ({elapsed:.2f}s)")
            except Exception as e:
                print(f"❌ Error en corrección: {e}")
        
        # Mostrar resumen
        print(f"\nResumen: {success_count}/{len(test_cases)} correcciones exitosas")
        
        return True
    except Exception as e:
        print(f"❌ Error al inicializar el corrector: {e}")
        return False

def main():
    """Función principal que ejecuta la prueba."""
    print("=== Prueba Simplificada del Corrector Fallback de DyslexiLess ===")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Configurar para usar el corrector fallback
    setup_fallback_config()
    
    # Probar el corrector fallback
    test_fallback_corrector()
    
    print("\n=== Prueba completada ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución de la prueba: {e}")
        import traceback
        print("\nDetalles del error:")
        traceback.print_exc()
    finally:
        print("\nFin del script de prueba.")